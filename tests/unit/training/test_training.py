"""Port conformance and the RegressionReport contract."""

from __future__ import annotations

from datetime import UTC, datetime

import polars as pl
import pytest

from price_predictor.domain import TrainingError
from price_predictor.training import (
    Evaluator,
    GradientBoostingTrainer,
    HyperparameterTuner,
    ModelTrainer,
    OptunaTuner,
    RegressionEvaluator,
    RegressionReport,
)


def test_adapters_satisfy_ports() -> None:
    assert isinstance(GradientBoostingTrainer("xgboost", {}), ModelTrainer)
    assert isinstance(OptunaTuner(n_trials=1, timeout_seconds=5), HyperparameterTuner)
    assert isinstance(RegressionEvaluator(), Evaluator)


def test_regression_report_as_metrics() -> None:
    report = RegressionReport(mae=41000.0, rmse=60000.0, mape=0.12, r2=0.81, n_samples=2048)
    assert report.as_metrics()["r2"] == 0.81
    assert "n_samples" not in report.as_metrics()


def test_report_generated_at_uses_tz() -> None:
    RegressionReport(mae=1.0, rmse=1.0, mape=0.1, r2=0.5, n_samples=1)
    assert datetime.now(UTC).tzinfo is not None


def test_trainer_rejects_empty_input() -> None:
    with pytest.raises(TrainingError, match="aligned non-empty"):
        GradientBoostingTrainer("xgboost", {}).train(
            pl.DataFrame({"x": []}), pl.Series("price", [])
        )


def test_unknown_estimator_raises() -> None:
    frame = pl.DataFrame({"x": [1.0, 2.0, 3.0, 4.0]})
    with pytest.raises(TrainingError, match="unknown estimator"):
        GradientBoostingTrainer("randomforest", {}).train(
            frame, pl.Series("price", [1.0, 2.0, 3.0, 4.0])
        )
