"""Registry-backed predictor (skeleton)."""

from __future__ import annotations

from price_predictor.domain import ModelStage, PredictionRequest, PredictionResult
from price_predictor.registry.ports import ModelRegistry


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

    def predict(self, request: PredictionRequest) -> PredictionResult:
        """See :meth:`PredictorService.predict`."""
        raise NotImplementedError(
            "Phase 2: load model from registry, run inference -> PredictionResult"
        )
