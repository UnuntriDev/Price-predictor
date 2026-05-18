"""Regression evaluation (skeleton)."""

from __future__ import annotations

import polars as pl

from price_predictor.training.report import RegressionReport


class RegressionEvaluator:
    """Computes hold-out regression metrics into a :class:`RegressionReport`."""

    def evaluate(self, y_true: pl.Series, y_pred: pl.Series) -> RegressionReport:
        """See :meth:`Evaluator.evaluate`."""
        raise NotImplementedError("Phase 2: compute MAE/RMSE/MAPE/R2 -> RegressionReport")
