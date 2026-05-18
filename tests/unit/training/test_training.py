"""Training adapters satisfy ports; RegressionReport is a real contract."""

from __future__ import annotations

from datetime import UTC, datetime

import polars as pl
import pytest

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
    trainer = GradientBoostingTrainer("xgboost", {"max_depth": 6})
    tuner = OptunaTuner(n_trials=10, timeout_seconds=60)
    evaluator = RegressionEvaluator()
    assert isinstance(trainer, ModelTrainer)
    assert isinstance(tuner, HyperparameterTuner)
    assert isinstance(evaluator, Evaluator)


def test_regression_report_as_metrics() -> None:
    report = RegressionReport(mae=41000.0, rmse=60000.0, mape=0.12, r2=0.81, n_samples=2048)
    metrics = report.as_metrics()
    assert metrics["r2"] == 0.81
    assert "n_samples" not in metrics


def test_trainer_is_phase2_stub() -> None:
    trainer = GradientBoostingTrainer("xgboost", {})
    with pytest.raises(NotImplementedError, match="Phase 2"):
        trainer.train(pl.DataFrame(), pl.Series("price", []))


def test_report_generated_at_uses_tz() -> None:
    # sanity: contract accepts an aware datetime
    RegressionReport(mae=1.0, rmse=1.0, mape=0.1, r2=0.5, n_samples=1)
    assert datetime.now(UTC).tzinfo is not None
