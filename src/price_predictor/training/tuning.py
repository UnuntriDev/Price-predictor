"""Optuna hyper-parameter search (skeleton)."""

from __future__ import annotations

import polars as pl


class OptunaTuner:
    """Bayesian hyper-parameter search over the estimator space.

    Args:
        n_trials: Number of Optuna trials.
        timeout_seconds: Wall-clock budget for the study.
    """

    def __init__(self, n_trials: int, timeout_seconds: int) -> None:
        self._n_trials = n_trials
        self._timeout_seconds = timeout_seconds

    def search(self, features: pl.DataFrame, target: pl.Series) -> dict[str, object]:
        """See :meth:`HyperparameterTuner.search`."""
        raise NotImplementedError("Phase 2: Optuna study minimising CV MAE -> best params")
