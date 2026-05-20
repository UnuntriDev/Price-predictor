"""Registry-backed predictor.

Loads a model once from the registry (lazy, then cached) and serves
predictions. The loaded model accepts the raw request feature columns,
so serving stays decoupled from feature engineering. If the model
carries a ``conformal_q`` attribute it becomes a prediction interval.
"""

from __future__ import annotations

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

_log = get_logger(__name__)


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
        self._model: Any | None = None
        self._version: str = "unknown"

    def _ensure_loaded(self) -> Any:
        if self._model is None:
            try:
                model = self._registry.load_model(self._model_name, self._stage)
                version = self._registry.get_version(self._model_name, self._stage).version
            except Exception as exc:
                # Boundary: any registry/MLflow failure (incl. unreachable
                # server) becomes the one domain error serving handles.
                msg = f"could not load '{self._model_name}'@{self._stage.value}"
                raise ModelNotLoadedError(msg) from exc
            self._model = model
            self._version = version
            _log.info("model.loaded", name=self._model_name, version=self._version)
        return self._model

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
            model_version=self._version,
            predicted_at=datetime.now(UTC),
        )
