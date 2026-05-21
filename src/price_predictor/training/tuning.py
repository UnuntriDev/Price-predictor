"""Optuna hyper-parameter search."""

from __future__ import annotations

from typing import Any

import optuna
import polars as pl
from sklearn.model_selection import KFold, cross_val_score

from price_predictor.domain import TrainingError
from price_predictor.training.estimators import build_estimator


class OptunaTuner:
    """TPE search minimising cross-validated MAE."""

    def __init__(
        self,
        n_trials: int,
        timeout_seconds: int,
        estimator_name: str = "xgboost",
        cv_folds: int = 5,
        seed: int = 42,
    ) -> None:
        self._n_trials = n_trials
        self._timeout_seconds = timeout_seconds
        self._estimator_name = estimator_name
        self._cv_folds = cv_folds
        self._seed = seed

    def _suggest(self, trial: optuna.Trial) -> dict[str, Any]:
        return {
            "n_estimators": trial.suggest_int("n_estimators", 50, 400, step=50),
            "max_depth": trial.suggest_int("max_depth", 2, 8),
            "learning_rate": trial.suggest_float("learning_rate", 1e-3, 3e-1, log=True),
        }

    def search(self, features: pl.DataFrame, target: pl.Series) -> dict[str, object]:
        """See :meth:`HyperparameterTuner.search`."""
        if features.height == 0 or features.height != target.len():
            msg = "search needs aligned non-empty data"
            raise TrainingError(msg)

        x = features.to_numpy()
        y = target.to_numpy()
        folds = KFold(
            n_splits=min(self._cv_folds, features.height),
            shuffle=True,
            random_state=self._seed,
        )

        def objective(trial: optuna.Trial) -> float:
            params = self._suggest(trial)
            estimator = build_estimator(self._estimator_name, params)
            scores = cross_val_score(estimator, x, y, cv=folds, scoring="neg_mean_absolute_error")
            return -float(scores.mean())

        optuna.logging.set_verbosity(optuna.logging.WARNING)
        study = optuna.create_study(
            direction="minimize",
            sampler=optuna.samplers.TPESampler(seed=self._seed),
        )
        study.optimize(
            objective,
            n_trials=self._n_trials,
            timeout=self._timeout_seconds,
            show_progress_bar=False,
        )
        return dict(study.best_params)
