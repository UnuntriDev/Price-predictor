"""Regression evaluation."""

from __future__ import annotations

import numpy as np
import polars as pl

from price_predictor.domain import TrainingError
from price_predictor.training.report import RegressionReport


class RegressionEvaluator:
    """MAE / RMSE / MAPE / R² in one pass."""

    def evaluate(self, y_true: pl.Series, y_pred: pl.Series) -> RegressionReport:
        """See :meth:`Evaluator.evaluate`."""
        # MAPE drops y==0 rows (undefined); R² → 0 when target has zero variance.
        yt = y_true.to_numpy().astype(np.float64)
        yp = y_pred.to_numpy().astype(np.float64)
        if yt.size == 0 or yt.size != yp.size:
            msg = f"evaluate needs equal non-empty arrays, got {yt.size} vs {yp.size}"
            raise TrainingError(msg)

        err = yt - yp
        mae = float(np.abs(err).mean())
        rmse = float(np.sqrt(np.square(err).mean()))

        nonzero = yt != 0.0
        mape = float(np.abs(err[nonzero] / yt[nonzero]).mean()) if bool(nonzero.any()) else 0.0

        ss_res = float(np.square(err).sum())
        ss_tot = float(np.square(yt - yt.mean()).sum())
        r2 = 1.0 - ss_res / ss_tot if ss_tot != 0.0 else 0.0

        return RegressionReport(
            mae=mae,
            rmse=rmse,
            mape=mape,
            r2=r2,
            n_samples=int(yt.size),
        )
