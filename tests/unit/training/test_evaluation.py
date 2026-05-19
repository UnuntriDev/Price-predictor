"""RegressionEvaluator produces correct, deterministic metrics."""

from __future__ import annotations

import polars as pl
import pytest

from price_predictor.domain import TrainingError
from price_predictor.training import RegressionEvaluator


def test_known_metrics() -> None:
    yt = pl.Series([100.0, 200.0, 300.0, 400.0])
    yp = pl.Series([110.0, 190.0, 310.0, 390.0])
    rep = RegressionEvaluator().evaluate(yt, yp)
    assert rep.mae == pytest.approx(10.0)
    assert rep.rmse == pytest.approx(10.0)
    assert rep.mape == pytest.approx((0.1 + 0.05 + 10 / 300 + 0.025) / 4)
    assert rep.r2 == pytest.approx(1.0 - 400.0 / 50_000.0)
    assert rep.n_samples == 4


def test_perfect_prediction() -> None:
    s = pl.Series([1.0, 2.0, 3.0])
    rep = RegressionEvaluator().evaluate(s, s)
    assert (rep.mae, rep.rmse, rep.mape, rep.r2) == (0.0, 0.0, 0.0, 1.0)


def test_zero_variance_target_gives_r2_zero() -> None:
    yt = pl.Series([5.0, 5.0, 5.0])
    yp = pl.Series([5.0, 6.0, 4.0])
    assert RegressionEvaluator().evaluate(yt, yp).r2 == 0.0


@pytest.mark.parametrize(
    ("yt", "yp"),
    [
        (pl.Series([], dtype=pl.Float64), pl.Series([], dtype=pl.Float64)),
        (pl.Series([1.0, 2.0]), pl.Series([1.0])),
    ],
)
def test_bad_inputs_raise(yt: pl.Series, yp: pl.Series) -> None:
    with pytest.raises(TrainingError):
        RegressionEvaluator().evaluate(yt, yp)
