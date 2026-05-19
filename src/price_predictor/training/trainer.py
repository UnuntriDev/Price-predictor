"""Gradient-boosting trainer."""

from __future__ import annotations

from typing import Any

import polars as pl

from price_predictor.config import get_logger
from price_predictor.domain import TrainingError
from price_predictor.training.estimators import build_estimator

_log = get_logger(__name__)


class GradientBoostingTrainer:
    """Trains the configured boosting estimator (xgb / lgbm / catboost).

    The input feature frame must be fully numeric (the caller runs
    :class:`~price_predictor.features.PriceFeaturePipeline` and any
    categorical encoding first); this keeps the trainer estimator-only.

    Args:
        estimator_name: Hydra-selected estimator key.
        params: Estimator hyper-parameters from the Hydra ``model`` group.
    """

    def __init__(self, estimator_name: str, params: dict[str, object]) -> None:
        self._estimator_name = estimator_name
        self._params = params

    def train(self, features: pl.DataFrame, target: pl.Series) -> Any:
        """Fit and return the underlying estimator.

        Args:
            features: Numeric feature frame.
            target: Target series aligned with ``features``.

        Returns:
            The fitted estimator.

        Raises:
            TrainingError: If inputs are empty or misaligned.
        """
        if features.height == 0 or features.height != target.len():
            msg = (
                f"train needs aligned non-empty data, got "
                f"{features.height} rows vs {target.len()} targets"
            )
            raise TrainingError(msg)

        _log.info(
            "train.start",
            estimator=self._estimator_name,
            rows=features.height,
            features=features.width,
        )
        estimator = build_estimator(self._estimator_name, dict(self._params))
        estimator.fit(features.to_numpy(), target.to_numpy())
        _log.info("train.done", estimator=self._estimator_name)
        return estimator
