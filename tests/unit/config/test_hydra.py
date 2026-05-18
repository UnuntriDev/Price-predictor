"""Hydra composition resolves the tree and honours overrides."""

from __future__ import annotations

from price_predictor.config import compose_config


def test_default_composition() -> None:
    cfg = compose_config()
    assert cfg.seed == 42
    assert cfg.model.name == "xgboost"
    assert cfg.data.target == "price"
    assert "area" in cfg.data.features


def test_model_override() -> None:
    cfg = compose_config(["model=lightgbm"])
    assert cfg.model.name == "lightgbm"
    assert cfg.model.estimator == "lightgbm.LGBMRegressor"
