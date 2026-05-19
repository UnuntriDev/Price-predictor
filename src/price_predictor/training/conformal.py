"""Split (inductive) conformal regression (ADR 0008).

Model-agnostic prediction intervals: calibrate on a held-out split,
then every prediction gets a symmetric band of width ``q`` where ``q``
is the conformal-adjusted quantile of absolute calibration residuals.
The band has finite-sample marginal coverage >= ``1 - alpha``.
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
    """Wraps a fitted estimator with split-conformal intervals.

    Args:
        estimator: An already-fitted regressor exposing ``predict``.
        alpha: Miscoverage rate; ``1 - alpha`` is the target coverage.
    """

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
        """Compute the conformal quantile from calibration residuals.

        Args:
            x_cal: Calibration features.
            y_cal: Calibration targets.

        Returns:
            ``self``.

        Raises:
            TrainingError: If the calibration set is empty.
        """
        n = int(y_cal.shape[0])
        if n == 0:
            msg = "conformal calibration set is empty"
            raise TrainingError(msg)
        residuals = np.abs(y_cal - np.asarray(self._estimator.predict(x_cal)))
        # Conformal level: ceil((n + 1)(1 - alpha)) / n, clipped to 1.0.
        level = min(math.ceil((n + 1) * (1.0 - self._alpha)) / n, 1.0)
        self._q = float(np.quantile(residuals, level, method="higher"))
        return self

    @property
    def q(self) -> float:
        """The calibrated conformal half-width.

        Raises:
            TrainingError: If accessed before :meth:`calibrate`.
        """
        if self._q is None:
            msg = "q accessed before calibrate"
            raise TrainingError(msg)
        return self._q

    def predict(self, x: Any) -> IntervalPrediction:
        """Return point predictions with the calibrated band.

        Raises:
            TrainingError: If called before :meth:`calibrate`.
        """
        if self._q is None:
            msg = "predict called before calibrate"
            raise TrainingError(msg)
        point = np.asarray(self._estimator.predict(x), dtype=np.float64)
        return IntervalPrediction(point, point - self._q, point + self._q)
