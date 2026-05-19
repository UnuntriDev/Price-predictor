"""Split-conformal intervals: ordering, coverage, and guards."""

from __future__ import annotations

import numpy as np
import pytest
from sklearn.linear_model import LinearRegression

from price_predictor.domain import TrainingError
from price_predictor.training import ConformalRegressor


def _split() -> tuple[np.ndarray, ...]:
    rng = np.random.default_rng(7)
    x = rng.normal(size=(300, 1))
    y = 2.0 * x[:, 0] + rng.normal(scale=0.3, size=300)
    return x[:150], y[:150], x[150:225], y[150:225], x[225:], y[225:]


def test_ordering_and_marginal_coverage() -> None:
    x_tr, y_tr, x_cal, y_cal, x_te, y_te = _split()
    est = LinearRegression().fit(x_tr, y_tr)
    conf = ConformalRegressor(est, alpha=0.1).calibrate(x_cal, y_cal)

    out = conf.predict(x_te)
    assert np.all(out.lower <= out.point)
    assert np.all(out.point <= out.upper)

    covered = np.mean((y_te >= out.lower) & (y_te <= out.upper))
    assert covered >= 0.85  # target 0.90, tolerance for finite sample


def test_predict_before_calibrate_raises() -> None:
    est = LinearRegression().fit(np.array([[0.0], [1.0]]), np.array([0.0, 1.0]))
    with pytest.raises(TrainingError, match="before calibrate"):
        ConformalRegressor(est).predict(np.array([[0.5]]))


@pytest.mark.parametrize("alpha", [0.0, 1.0, -0.1, 1.5])
def test_invalid_alpha_rejected(alpha: float) -> None:
    with pytest.raises(TrainingError, match="alpha"):
        ConformalRegressor(LinearRegression(), alpha=alpha)
