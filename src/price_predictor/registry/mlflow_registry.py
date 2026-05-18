"""MLflow-backed :class:`ModelRegistry` (skeleton)."""

from __future__ import annotations

from typing import Any

from price_predictor.config.settings import MLflowSettings
from price_predictor.domain import ModelStage, ModelVersion


class MLflowModelRegistry:
    """Wraps the MLflow Model Registry.

    Args:
        settings: Tracking/registry URIs and experiment name. Injected so
            tests can target a temp SQLite tracking store.
    """

    def __init__(self, settings: MLflowSettings) -> None:
        self._settings = settings

    def register(self, run_id: str, name: str, metrics: dict[str, float]) -> ModelVersion:
        """See :meth:`ModelRegistry.register`."""
        raise NotImplementedError("Phase 2: mlflow.register_model + set metrics")

    def transition_stage(self, name: str, version: str, stage: ModelStage) -> ModelVersion:
        """See :meth:`ModelRegistry.transition_stage`."""
        raise NotImplementedError("Phase 2: MlflowClient stage transition")

    def get_version(self, name: str, stage: ModelStage) -> ModelVersion:
        """See :meth:`ModelRegistry.get_version`."""
        raise NotImplementedError("Phase 2: resolve latest version at stage -> ModelVersion")

    def load_model(self, name: str, stage: ModelStage) -> Any:
        """See :meth:`ModelRegistry.load_model`."""
        raise NotImplementedError("Phase 2: mlflow.pyfunc.load_model(stage URI)")
