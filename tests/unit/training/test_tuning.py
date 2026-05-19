"""OptunaTuner returns a reproducible best-params dict."""

from __future__ import annotations

import numpy as np
import polars as pl
import pytest

from price_predictor.domain import TrainingError
from price_predictor.training import OptunaTuner

_SPACE = {"n_estimators", "max_depth", "learning_rate"}


def _dataset() -> tuple[pl.DataFrame, pl.Series]:
    rng = np.random.default_rng(3)
    x = rng.normal(size=(90, 2))
    y = 1.5 * x[:, 0] + 0.5 * x[:, 1]
    return pl.DataFrame(x, schema=["f0", "f1"]), pl.Series("price", y)


def _tuner() -> OptunaTuner:
    return OptunaTuner(n_trials=4, timeout_seconds=60, estimator_name="xgboost", cv_folds=3, seed=1)


def test_search_returns_space_and_is_reproducible() -> None:
    frame, target = _dataset()
    best_a = _tuner().search(frame, target)
    best_b = _tuner().search(frame, target)
    assert set(best_a) <= _SPACE
    assert best_a == best_b  # seeded TPE -> deterministic


def test_search_rejects_empty() -> None:
    with pytest.raises(TrainingError):
        _tuner().search(pl.DataFrame({"x": []}), pl.Series("price", []))
