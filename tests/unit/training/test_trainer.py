"""GradientBoostingTrainer fits a usable estimator on numeric data."""

from __future__ import annotations

import numpy as np
import polars as pl

from price_predictor.training import GradientBoostingTrainer, RegressionEvaluator


def _dataset() -> tuple[pl.DataFrame, pl.Series]:
    rng = np.random.default_rng(0)
    x = rng.normal(size=(120, 2))
    y = 3.0 * x[:, 0] - 2.0 * x[:, 1] + rng.normal(scale=0.05, size=120)
    return pl.DataFrame(x, schema=["f0", "f1"]), pl.Series("price", y)


def test_trained_model_fits_signal() -> None:
    frame, target = _dataset()
    model = GradientBoostingTrainer(
        "xgboost", {"n_estimators": 60, "max_depth": 3, "verbosity": 0}
    ).train(frame, target)

    preds = pl.Series("p", model.predict(frame.to_numpy()))
    report = RegressionEvaluator().evaluate(target, preds)
    assert report.n_samples == 120
    assert report.r2 > 0.9
