"""MLflow registry adapter satisfies the port and is unimplemented."""

from __future__ import annotations

import pytest

from price_predictor.config.settings import MLflowSettings
from price_predictor.domain import ModelStage
from price_predictor.registry import MLflowModelRegistry, ModelRegistry


def test_adapter_satisfies_port() -> None:
    registry = MLflowModelRegistry(MLflowSettings())
    assert isinstance(registry, ModelRegistry)


def test_get_version_is_phase2_stub() -> None:
    registry = MLflowModelRegistry(MLflowSettings())
    with pytest.raises(NotImplementedError, match="Phase 2"):
        registry.get_version("price-predictor", ModelStage.PRODUCTION)
