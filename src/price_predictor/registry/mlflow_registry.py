"""MLflow-backed :class:`ModelRegistry`."""

from __future__ import annotations

from collections.abc import Mapping
from datetime import UTC, datetime
from typing import Any

import mlflow
import mlflow.sklearn
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
_METRIC_TAG_PREFIX = "metric."


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

    def _configure_global_uris(self) -> None:
        """Point MLflow flavor APIs at the configured tracking backend."""
        registry_uri = self._settings.registry_uri or self._settings.tracking_uri
        mlflow.set_tracking_uri(self._settings.tracking_uri)
        mlflow.set_registry_uri(registry_uri)

    @staticmethod
    def _metrics_from_tags(tags: Mapping[str, Any] | None) -> dict[str, float]:
        metrics: dict[str, float] = {}
        for key, value in (tags or {}).items():
            if not key.startswith(_METRIC_TAG_PREFIX):
                continue
            try:
                metrics[key.removeprefix(_METRIC_TAG_PREFIX)] = float(value)
            except (TypeError, ValueError):
                _log.warning("registry.metric_tag_invalid", key=key, value=value)
        return metrics

    @classmethod
    def _to_domain(cls, version: Any, metrics: dict[str, float] | None = None) -> ModelVersion:
        version_metrics = cls._metrics_from_tags(getattr(version, "tags", None))
        if metrics is not None:
            version_metrics.update(metrics)
        return ModelVersion(
            name=version.name,
            version=str(version.version),
            stage=ModelStage(str(version.current_stage).lower()),
            run_id=version.run_id,
            metrics=version_metrics,
            created_at=datetime.fromtimestamp(version.creation_timestamp / 1000, tz=UTC),
        )

    def log_and_register(self, model: Any, name: str, metrics: dict[str, float]) -> ModelVersion:
        """See :meth:`ModelRegistry.log_and_register`."""
        self._configure_global_uris()
        mlflow.set_experiment(self._settings.experiment_name)
        with mlflow.start_run():
            mlflow.log_metrics(metrics)
            model_info = mlflow.sklearn.log_model(model, name="model")
        version = mlflow.register_model(model_uri=model_info.model_uri, name=name)
        for key, value in metrics.items():
            self._client.set_model_version_tag(name, version.version, f"metric.{key}", value)
        return self._to_domain(version, metrics)

    def transition_stage(self, name: str, version: str, stage: ModelStage) -> ModelVersion:
        """See :meth:`ModelRegistry.transition_stage`."""
        updated = self._client.transition_model_version_stage(
            name=name, version=version, stage=_STAGE_TO_MLFLOW[stage]
        )
        fresh = self._client.get_model_version(name, str(updated.version))
        return self._to_domain(fresh)

    def get_version(self, name: str, stage: ModelStage) -> ModelVersion:
        """See :meth:`ModelRegistry.get_version`."""
        matches = self._client.get_latest_versions(name, stages=[_STAGE_TO_MLFLOW[stage]])
        if not matches:
            msg = f"no '{name}' version at stage {stage.value}"
            raise ModelNotFoundError(msg)
        version = matches[0]
        fresh = self._client.get_model_version(name, str(version.version))
        return self._to_domain(fresh)

    def load_model(self, name: str, stage: ModelStage) -> Any:
        """See :meth:`ModelRegistry.load_model`.

        Uses the sklearn flavor so the original :class:`ConformalModel`
        object is returned intact (its ``conformal_q`` attribute and
        ``predict`` survive the round-trip, unlike a pyfunc wrapper).
        """
        self._configure_global_uris()
        uri = f"models:/{name}/{_STAGE_TO_MLFLOW[stage]}"
        loaded: Any = mlflow.sklearn.load_model(uri)
        return loaded
