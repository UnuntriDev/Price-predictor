"""recommend_promotion: first model, improvement, regression, guards."""

from __future__ import annotations

import pytest

from price_predictor.domain import RegistryError
from price_predictor.registry import recommend_promotion


def test_first_model_is_promoted() -> None:
    rec = recommend_promotion({"mae": 50_000.0}, None)
    assert rec.should_promote is True
    assert rec.incumbent is None


def test_improvement_promotes_with_threshold() -> None:
    rec = recommend_promotion({"mae": 40_000.0}, {"mae": 50_000.0}, min_relative_improvement=0.05)
    assert rec.should_promote is True
    assert rec.relative_improvement == pytest.approx(0.2)


def test_marginal_gain_below_threshold_holds() -> None:
    rec = recommend_promotion({"mae": 49_900.0}, {"mae": 50_000.0}, min_relative_improvement=0.05)
    assert rec.should_promote is False


def test_regression_holds() -> None:
    rec = recommend_promotion({"mae": 60_000.0}, {"mae": 50_000.0})
    assert rec.should_promote is False


def test_higher_is_better_metric() -> None:
    rec = recommend_promotion({"r2": 0.85}, {"r2": 0.80}, primary="r2", lower_is_better=False)
    assert rec.should_promote is True


def test_missing_primary_metric_raises() -> None:
    with pytest.raises(RegistryError, match="missing primary"):
        recommend_promotion({"rmse": 1.0}, None, primary="mae")
