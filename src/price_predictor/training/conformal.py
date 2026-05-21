"""Split-conformal regression (ADR 0008).

Calibrate on a held-out split, then every prediction gets ± q where q is
the conformal-adjusted quantile of |residuals|. Marginal coverage is
≥ 1 - alpha by construction (finite-sample, no distributional assumption).
"""

from __future__ import annotations

import math
from typing import Any, NamedTuple, Self

import numpy as np
import numpy.typing as npt

from price_predictor.domain import TrainingError


class IntervalPrediction(NamedTuple):
    """Point estimate with a lower/upper conformal band."""

    point: npt.NDArray[np.float64]
    lower: npt.NDArray[np.float64]
    upper: npt.NDArray[np.float64]


class ConformalRegressor:
    """Wraps a fitted regressor with a calibrated ± interval."""

    def __init__(self, estimator: Any, alpha: float = 0.1) -> None:
        if not 0.0 < alpha < 1.0:
            msg = f"alpha must be in (0, 1), got {alpha}"
            raise TrainingError(msg)
        self._estimator = estimator
        self._alpha = alpha
        self._q: float | None = None

    def calibrate(
        self,
        x_cal: Any,
        y_cal: npt.NDArray[np.float64],
    ) -> Self:
        """Set ``q`` from absolute residuals on the calibration split."""
        n = int(y_cal.shape[0])
        if n == 0:
            msg = "conformal calibration set is empty"
            raise TrainingError(msg)
        residuals = np.abs(y_cal - np.asarray(self._estimator.predict(x_cal)))
        # Conformal level: ceil((n+1)(1-alpha)) / n, clipped to 1.
        level = min(math.ceil((n + 1) * (1.0 - self._alpha)) / n, 1.0)
        self._q = float(np.quantile(residuals, level, method="higher"))
        return self

    @property
    def q(self) -> float:
        """Calibrated half-width."""
        if self._q is None:
            msg = "q accessed before calibrate"
            raise TrainingError(msg)
        return self._q

    def predict(self, x: Any) -> IntervalPrediction:
        """Point estimate + ±q band."""
        if self._q is None:
            msg = "predict called before calibrate"
            raise TrainingError(msg)
        point = np.asarray(self._estimator.predict(x), dtype=np.float64)
        return IntervalPrediction(point, point - self._q, point + self._q)
