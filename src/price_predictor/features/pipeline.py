"""Feature pipeline for the Kaggle dataset (ADR 0014).

fit learns medians; transform imputes (numeric→median, bool→False,
categorical→"missing") and emits exactly the modelled columns —
target/ids stripped to keep leakage out.
"""

from __future__ import annotations

from typing import Self

import polars as pl

from price_predictor.domain import FeatureError

_NUMERIC = (
    "square_meters",
    "rooms",
    "floor",
    "floor_count",
    "build_year",
    "centre_distance_km",
    "poi_count",
    "school_distance_km",
    "clinic_distance_km",
    "post_office_distance_km",
    "kindergarten_distance_km",
    "restaurant_distance_km",
    "college_distance_km",
    "pharmacy_distance_km",
)
_CATEGORICAL = ("city", "property_type", "ownership", "building_material", "condition")
_BOOL = ("has_parking", "has_balcony", "has_elevator", "has_security", "has_storage")

FEATURE_COLUMNS = (*_NUMERIC, *_CATEGORICAL, *_BOOL)
_MISSING = "missing"


class PriceFeaturePipeline:
    """Median/sentinel imputer + column projector."""

    def __init__(self, target_col: str = "price_pln") -> None:
        self._target_col = target_col
        self._medians: dict[str, float] = {}

    @property
    def is_fitted(self) -> bool:
        """True once :meth:`fit` has run."""
        return bool(self._medians)

    def fit(self, frame: pl.DataFrame) -> Self:
        """Learn per-column medians."""
        if self._target_col not in frame.columns:
            msg = f"fit requires target column {self._target_col!r}"
            raise FeatureError(msg)
        self._medians = {
            col: float(frame.select(pl.col(col).cast(pl.Float64).median()).item() or 0.0)
            for col in _NUMERIC
        }
        return self

    def transform(self, frame: pl.DataFrame) -> pl.DataFrame:
        """Impute + project to :data:`FEATURE_COLUMNS`."""
        if not self._medians:
            msg = "transform called before fit"
            raise FeatureError(msg)
        return frame.with_columns(
            *[pl.col(col).cast(pl.Float64).fill_null(self._medians[col]) for col in _NUMERIC],
            *[pl.col(col).cast(pl.Utf8).fill_null(_MISSING) for col in _CATEGORICAL],
            *[
                pl.col(col).cast(pl.Boolean, strict=False).fill_null(value=False).cast(pl.Int8)
                for col in _BOOL
            ],
        ).select(*FEATURE_COLUMNS)
