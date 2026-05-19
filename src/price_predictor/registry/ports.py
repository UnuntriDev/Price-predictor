"""Model registry port."""

from __future__ import annotations

from typing import Any, Protocol, runtime_checkable

from price_predictor.domain import ModelStage, ModelVersion


@runtime_checkable
class ModelRegistry(Protocol):
    """Registers, promotes, and loads trained model artifacts."""

    def register(self, run_id: str, name: str, metrics: dict[str, float]) -> ModelVersion:
        """Register the artifact from ``run_id`` and return its version."""
        ...

    def log_and_register(self, model: Any, name: str, metrics: dict[str, float]) -> ModelVersion:
        """Log ``model`` in a fresh run and register it in one step."""
        ...

    def transition_stage(self, name: str, version: str, stage: ModelStage) -> ModelVersion:
        """Move a version to ``stage`` and return the updated record."""
        ...

    def get_version(self, name: str, stage: ModelStage) -> ModelVersion:
        """Return the version currently at ``stage``.

        Raises:
            ModelNotFoundError: If no version occupies ``stage``.
        """
        ...

    def load_model(self, name: str, stage: ModelStage) -> Any:
        """Load and return the runnable model object at ``stage``."""
        ...
