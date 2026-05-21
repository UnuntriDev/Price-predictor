"""Pulls the model from the registry on first use.

If the loaded artefact has ``conformal_q`` the response carries an
interval (ADR 0008).
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
    """Lazy-load + cache, then predict."""

    def __init__(
        self,
        registry: ModelRegistry,
        model_name: str,
        stage: ModelStage = ModelStage.PRODUCTION,
    ) -> None:
        self._registry = registry
        self._model_name = model_name
        self._stage = stage
        self._loaded: _Loaded | None = None

    def _ensure_loaded(self) -> Any:
        if self._loaded is None:
            try:
                model = self._registry.load_model(self._model_name, self._stage)
                version = self._registry.get_version(self._model_name, self._stage).version
            except Exception as exc:
                # Any MLflow blow-up → one domain error.
                msg = f"could not load '{self._model_name}'@{self._stage}"
                raise ModelNotLoadedError(msg) from exc
            self._loaded = _Loaded(model=model, version=version)
            _log.info("model.loaded", name=self._model_name, version=version)
        return self._loaded.model

    def describe_model(self) -> ModelInfo:
        """Read state for ``/health`` (never raises)."""
        return ModelInfo(
            name=self._model_name,
            version=self._loaded.version if self._loaded is not None else "",
            stage=self._stage,
            loaded=self._loaded is not None,
        )

    def warmup(self) -> None:
        """Try to load at startup, swallow if it fails (ADR 0011)."""
        # Registry can be down; container still becomes healthy and
        # /predict retries the load per request.
        try:
            self._ensure_loaded()
        except ModelNotLoadedError as exc:
            _log.warning("model.warmup_failed", error=str(exc))

    def predict(self, request: PredictionRequest) -> PredictionResult:
        """See :meth:`PredictorService.predict`."""
        model = self._ensure_loaded()
        assert self._loaded is not None  # _ensure_loaded set it
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
