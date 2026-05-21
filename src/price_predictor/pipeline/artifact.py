"""Deployable model bundle: feature pipeline + estimator + conformal q.

Cloudpickle-friendly so MLflow logs/loads it as one object. Accepts the
raw request columns so serving stays oblivious to feature engineering.
"""

from __future__ import annotations

from typing import Any

import numpy.typing as npt
import polars as pl

from price_predictor.features import FEATURE_COLUMNS, PriceFeaturePipeline

# Raw columns the caller supplies — same as the modelled features.
REQUEST_COLUMNS = FEATURE_COLUMNS


class ConformalModel:
    """Raw request in, price + interval out."""

    def __init__(
        self,
        feature_pipeline: PriceFeaturePipeline,
        estimator: Any,
        conformal_q: float,
    ) -> None:
        self._feature_pipeline = feature_pipeline
        self._estimator = estimator
        self.conformal_q = conformal_q

    def _features(self, raw: Any) -> Any:
        frame = pl.from_pandas(raw[list(REQUEST_COLUMNS)])
        return self._feature_pipeline.transform(frame).to_pandas()

    def predict(self, raw: Any) -> npt.NDArray[Any]:
        """Point predictions (PLN) for a pandas frame of REQUEST_COLUMNS."""
        predictions: npt.NDArray[Any] = self._estimator.predict(self._features(raw))
        return predictions
