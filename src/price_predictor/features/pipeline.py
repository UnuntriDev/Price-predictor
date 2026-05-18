"""Otodom feature pipeline (skeleton)."""

from __future__ import annotations

from collections.abc import Sequence

import polars as pl


class PriceFeaturePipeline:
    """Builds model features from validated listing frames.

    Args:
        categorical: Columns to treat as categoricals (e.g. city, district).
        numeric: Columns passed through / scaled.
    """

    def __init__(self, categorical: Sequence[str], numeric: Sequence[str]) -> None:
        self._categorical = tuple(categorical)
        self._numeric = tuple(numeric)

    def fit(self, frame: pl.DataFrame) -> PriceFeaturePipeline:
        """See :meth:`FeatureTransformer.fit`."""
        raise NotImplementedError("Phase 2: fit encoders/derived features (price_per_sqm, age)")

    def transform(self, frame: pl.DataFrame) -> pl.DataFrame:
        """See :meth:`FeatureTransformer.transform`."""
        raise NotImplementedError("Phase 2: emit the engineered feature frame")
