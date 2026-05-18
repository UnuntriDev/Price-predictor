"""Feature engineering ports."""

from __future__ import annotations

from typing import Protocol, runtime_checkable

import polars as pl


@runtime_checkable
class FeatureTransformer(Protocol):
    """A fit/transform step over a Polars frame.

    Mirrors the scikit-learn estimator contract closely enough that a
    transformer can be dropped into a sklearn ``Pipeline`` later.
    """

    def fit(self, frame: pl.DataFrame) -> FeatureTransformer:
        """Learn any state from ``frame`` and return ``self``."""
        ...

    def transform(self, frame: pl.DataFrame) -> pl.DataFrame:
        """Return the engineered feature frame."""
        ...
