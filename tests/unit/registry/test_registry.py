"""Registry adapter: port conformance and pure mapping logic.

The end-to-end round-trip lives in tests/integration; here we only
cover what needs no MLflow backend.
"""

from __future__ import annotations

from types import SimpleNamespace

from price_predictor.config.settings import MLflowSettings
from price_predictor.domain import ModelStage, ModelVersion
from price_predictor.registry import MLflowModelRegistry, ModelRegistry
from price_predictor.registry.mlflow_registry import _STAGE_TO_MLFLOW


def test_adapter_satisfies_port() -> None:
    registry = MLflowModelRegistry(MLflowSettings())
    assert isinstance(registry, ModelRegistry)


def test_stage_mapping_is_total() -> None:
    assert set(_STAGE_TO_MLFLOW) == set(ModelStage)
    assert _STAGE_TO_MLFLOW[ModelStage.PRODUCTION] == "Production"


def test_to_domain_maps_mlflow_version() -> None:
    fake = SimpleNamespace(
        name="price-predictor",
        version=7,
        current_stage="Staging",
        run_id="abc123",
        creation_timestamp=1_700_000_000_000,
    )
    mv = MLflowModelRegistry._to_domain(fake, {"mae": 1.0})
    assert isinstance(mv, ModelVersion)
    assert mv.version == "7"
    assert mv.stage is ModelStage.STAGING
    assert mv.metrics == {"mae": 1.0}
