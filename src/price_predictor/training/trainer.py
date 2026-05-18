"""Gradient-boosting trainer (skeleton)."""

from __future__ import annotations

from typing import Any

import polars as pl

from price_predictor.config import get_logger

_log = get_logger(__name__)


class GradientBoostingTrainer:
    """Trains the configured boosting estimator (xgb / lgbm / catboost).

    Args:
        estimator_name: Hydra-selected estimator key.
        params: Estimator hyper-parameters from the Hydra ``model`` group.
    """

    def __init__(self, estimator_name: str, params: dict[str, object]) -> None:
        self._estimator_name = estimator_name
        self._params = params

    def train(self, features: pl.DataFrame, target: pl.Series) -> Any:
        """See :meth:`ModelTrainer.train`."""
        _log.info("train.requested", estimator=self._estimator_name)
        raise NotImplementedError("Phase 2: fit the boosting estimator and return it")
