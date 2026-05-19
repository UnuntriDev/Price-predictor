"""The deployable model artifact.

``ConformalModel`` bundles everything serving needs behind a single
``predict`` plus a ``conformal_q`` attribute: the fitted feature
pipeline, the fitted sklearn estimator pipeline, and the conformal
half-width. It is cloudpickle-friendly so MLflow can log/load it whole,
and it accepts the *raw request columns* so the serving layer never has
to know about feature engineering.
"""

from __future__ import annotations

from typing import Any

import numpy.typing as npt
import polars as pl

from price_predictor.features import PriceFeaturePipeline

REQUEST_COLUMNS = (
    "area",
    "rooms",
    "city",
    "district",
    "year_built",
    "floor",
    "property_type",
)


class ConformalModel:
    """Serving-ready model: raw request in, price out, plus interval.

    Args:
        feature_pipeline: A *fitted* :class:`PriceFeaturePipeline`.
        estimator: A *fitted* sklearn pipeline (encoder + regressor)
            trained on the feature-pipeline output.
        conformal_q: Calibrated conformal half-width (PLN).
    """

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
        """Predict prices for a pandas frame of raw request columns.

        Args:
            raw: pandas DataFrame containing :data:`REQUEST_COLUMNS`.

        Returns:
            1-D array of point price predictions (PLN).
        """
        predictions: npt.NDArray[Any] = self._estimator.predict(self._features(raw))
        return predictions
