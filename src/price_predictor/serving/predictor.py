"""Registry-backed predictor.

Loads a model once from the registry (lazy, then cached) and serves
predictions. The loaded model accepts the raw request feature columns,
so serving stays decoupled from feature engineering. If the model
carries a ``conformal_q`` attribute it becomes a prediction interval.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from enum import Enum
from typing import Any

import polars as pl

from price_predictor.config import get_logger
from price_predictor.domain import (
    ModelNotLoadedError,
    ModelStage,
    PredictionRequest,
    PredictionResult,
)
from price_predictor.features import FEATURE_COLUMNS
from price_predictor.registry.ports import ModelRegistry
from price_predictor.serving.schemas import ModelInfo

_log = get_logger(__name__)


@dataclass(frozen=True, slots=True)
class _Loaded:
    model: Any
    version: str


class ModelBackedPredictor:
    """Serves predictions from the model at a registry stage.

    Args:
        registry: Source of the runnable model. Injected so the service
            never imports MLflow directly.
        model_name: Registered model name to serve.
        stage: Which lifecycle stage to load.
    """

    def __init__(
        self,
        registry: ModelRegistry,
        model_name: str,
        stage: ModelStage = ModelStage.PRODUCTION,
    ) -> None:
        self._registry = registry
        self._model_name = model_name
        self._stage = stage
        # Single source of truth for load state: None until warmup/first
        # request succeeds. Avoids drift between a `_model` field and a
        # parallel `_version` cache.
        self._loaded: _Loaded | None = None

    def _ensure_loaded(self) -> Any:
        if self._loaded is None:
            try:
                model = self._registry.load_model(self._model_name, self._stage)
                version = self._registry.get_version(self._model_name, self._stage).version
            except Exception as exc:
                # Boundary: any registry/MLflow failure (incl. unreachable
                # server) becomes the one domain error serving handles.
                msg = f"could not load '{self._model_name}'@{self._stage}"
                raise ModelNotLoadedError(msg) from exc
            self._loaded = _Loaded(model=model, version=version)
            _log.info("model.loaded", name=self._model_name, version=version)
        return self._loaded.model

    def describe_model(self) -> ModelInfo:
        """Snapshot of what is loaded (no I/O, never raises).

        ``/health`` calls this to expose the live artefact's identity
        without coupling to MLflow.
        """
        return ModelInfo(
            name=self._model_name,
            version=self._loaded.version if self._loaded is not None else "",
            stage=self._stage,
            loaded=self._loaded is not None,
        )

    def warmup(self) -> None:
        """Eagerly load the model at startup (ADR 0011), tolerantly.

        A failure (registry/network down) is logged, not raised, so the
        container still becomes healthy; ``/predict`` then returns 503
        and retries the load on each request until it succeeds.
        """
        try:
            self._ensure_loaded()
        except ModelNotLoadedError as exc:
            _log.warning("model.warmup_failed", error=str(exc))

    def predict(self, request: PredictionRequest) -> PredictionResult:
        """See :meth:`PredictorService.predict`."""
        model = self._ensure_loaded()
        # ``_ensure_loaded`` succeeded, so ``_loaded`` is set here.
        assert self._loaded is not None
        row: dict[str, list[Any]] = {}
        for col in FEATURE_COLUMNS:
            value = getattr(request, col)
            row[col] = [value.value if isinstance(value, Enum) else value]
        frame = pl.DataFrame(row)

        point = round(float(model.predict(frame.to_pandas())[0]))
        half = getattr(model, "conformal_q", None)
        low = round(point - float(half)) if half is not None else None
        high = round(point + float(half)) if half is not None else None

        return PredictionResult(
            predicted_price=point,
            interval_low=max(low, 0) if low is not None else None,
            interval_high=high,
            model_name=self._model_name,
            model_version=self._loaded.version,
            predicted_at=datetime.now(UTC),
        )
