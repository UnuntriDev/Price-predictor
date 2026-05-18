"""Training, tuning, and evaluation ports."""

from __future__ import annotations

from typing import Any, Protocol, runtime_checkable

import polars as pl

from price_predictor.training.report import RegressionReport


@runtime_checkable
class ModelTrainer(Protocol):
    """Fits a regressor on a feature frame and returns the fitted estimator."""

    def train(self, features: pl.DataFrame, target: pl.Series) -> Any:
        """Fit and return the underlying estimator object."""
        ...


@runtime_checkable
class HyperparameterTuner(Protocol):
    """Searches a hyper-parameter space and returns the best params."""

    def search(self, features: pl.DataFrame, target: pl.Series) -> dict[str, object]:
        """Return the best hyper-parameters found."""
        ...


@runtime_checkable
class Evaluator(Protocol):
    """Scores predictions against ground truth."""

    def evaluate(self, y_true: pl.Series, y_pred: pl.Series) -> RegressionReport:
        """Return a populated :class:`RegressionReport`."""
        ...
