"""MLflow-backed :class:`ModelRegistry`."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

import mlflow
import mlflow.sklearn
from mlflow.exceptions import MlflowException
from mlflow.tracking import MlflowClient

from price_predictor.config import get_logger
from price_predictor.config.settings import MLflowSettings
from price_predictor.domain import ModelNotFoundError, ModelStage, ModelVersion

_log = get_logger(__name__)

_STAGE_TO_MLFLOW: dict[ModelStage, str] = {
    ModelStage.NONE: "None",
    ModelStage.STAGING: "Staging",
    ModelStage.PRODUCTION: "Production",
    ModelStage.ARCHIVED: "Archived",
}


class MLflowModelRegistry:
    """Wraps the MLflow Model Registry.

    Args:
        settings: Tracking/registry URIs and experiment name. Injected so
            tests can target a temp SQLite tracking store.
    """

    def __init__(self, settings: MLflowSettings) -> None:
        self._settings = settings
        self._client = MlflowClient(
            tracking_uri=settings.tracking_uri,
            registry_uri=settings.registry_uri or settings.tracking_uri,
        )

    @staticmethod
    def _to_domain(version: Any, metrics: dict[str, float]) -> ModelVersion:
        return ModelVersion(
            name=version.name,
            version=str(version.version),
            stage=ModelStage(str(version.current_stage).lower()),
            run_id=version.run_id,
            metrics=metrics,
            created_at=datetime.fromtimestamp(version.creation_timestamp / 1000, tz=UTC),
        )

    def register(self, run_id: str, name: str, metrics: dict[str, float]) -> ModelVersion:
        """See :meth:`ModelRegistry.register`."""
        try:
            self._client.create_registered_model(name)
        except MlflowException:
            _log.info("registry.model_exists", name=name)
        version = self._client.create_model_version(
            name=name, source=f"runs:/{run_id}/model", run_id=run_id
        )
        for key, value in metrics.items():
            self._client.set_model_version_tag(name, version.version, f"metric.{key}", value)
        return self._to_domain(version, metrics)

    def log_and_register(self, model: Any, name: str, metrics: dict[str, float]) -> ModelVersion:
        """See :meth:`ModelRegistry.log_and_register`."""
        mlflow.set_tracking_uri(self._settings.tracking_uri)
        mlflow.set_experiment(self._settings.experiment_name)
        with mlflow.start_run() as run:
            mlflow.log_metrics(metrics)
            mlflow.sklearn.log_model(model, name="model")
            run_id = run.info.run_id
        return self.register(run_id, name, metrics)

    def transition_stage(self, name: str, version: str, stage: ModelStage) -> ModelVersion:
        """See :meth:`ModelRegistry.transition_stage`."""
        updated = self._client.transition_model_version_stage(
            name=name, version=version, stage=_STAGE_TO_MLFLOW[stage]
        )
        return self._to_domain(updated, {})

    def get_version(self, name: str, stage: ModelStage) -> ModelVersion:
        """See :meth:`ModelRegistry.get_version`."""
        matches = self._client.get_latest_versions(name, stages=[_STAGE_TO_MLFLOW[stage]])
        if not matches:
            msg = f"no '{name}' version at stage {stage.value}"
            raise ModelNotFoundError(msg)
        return self._to_domain(matches[0], {})

    def load_model(self, name: str, stage: ModelStage) -> Any:
        """See :meth:`ModelRegistry.load_model`.

        Uses the sklearn flavor so the original :class:`ConformalModel`
        object is returned intact (its ``conformal_q`` attribute and
        ``predict`` survive the round-trip, unlike a pyfunc wrapper).
        """
        uri = f"models:/{name}/{_STAGE_TO_MLFLOW[stage]}"
        loaded: Any = mlflow.sklearn.load_model(uri)
        return loaded
