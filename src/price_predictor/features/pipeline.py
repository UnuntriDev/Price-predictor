"""Otodom feature pipeline.

Turns a validated listings frame into model features. Two deliberate
choices:

- **No price-derived features.** ``price_per_sqm`` would leak the target,
  so it is never emitted as an input.
- **Smoothed district target encoding** (ADR 0007): raw districts are
  normalized (diacritics/case folded), mapped through a canonical
  dictionary, then encoded by a smoothed mean of the target. The
  smoothing prior is the leakage guard at this layer; out-of-fold
  wrapping is the training layer's job.
"""

from __future__ import annotations

import unicodedata
from collections.abc import Mapping
from typing import Self

import polars as pl

from price_predictor.domain import FeatureError

_OUTPUT_COLUMNS = (
    "area",
    "rooms",
    "floor",
    "building_age",
    "district_te",
    "city",
    "property_type",
)


def _normalize(value: str) -> str:
    """Casefold and strip diacritics so 'Mokotów' == 'mokotow'."""
    decomposed = unicodedata.normalize("NFKD", value)
    ascii_only = decomposed.encode("ascii", "ignore").decode("ascii")
    return ascii_only.strip().casefold()


class PriceFeaturePipeline:
    """Stateful fit/transform feature builder.

    Args:
        reference_year: Year used to derive ``building_age``; injected
            (typically the data snapshot year) so transforms are
            reproducible and never depend on wall-clock time.
        district_dictionary: Raw-or-normalized district -> canonical
            district. Lookups fall back to the normalized raw value.
        target_col: Target column present at fit time.
        smoothing: Target-encoding smoothing strength (rows-equivalent of
            the global prior). Higher = more shrinkage to the global mean.
    """

    def __init__(
        self,
        reference_year: int,
        district_dictionary: Mapping[str, str] | None = None,
        target_col: str = "price",
        smoothing: float = 10.0,
    ) -> None:
        self._reference_year = reference_year
        self._dictionary = dict(district_dictionary or {})
        self._target_col = target_col
        self._smoothing = smoothing
        self._global_mean: float | None = None
        self._district_te: dict[str, float] = {}

    def _canonical(self, district: str) -> str:
        normalized = _normalize(district)
        mapped = self._dictionary.get(district) or self._dictionary.get(normalized)
        return _normalize(mapped) if mapped else normalized

    @property
    def is_fitted(self) -> bool:
        """Whether :meth:`fit` has run."""
        return self._global_mean is not None

    def fit(self, frame: pl.DataFrame) -> Self:
        """Learn the global mean and smoothed per-district target means.

        Args:
            frame: Validated listings frame; must contain ``target_col``.

        Returns:
            ``self``.

        Raises:
            FeatureError: If the target column is absent.
        """
        if self._target_col not in frame.columns:
            msg = f"fit requires target column {self._target_col!r}"
            raise FeatureError(msg)

        global_mean = float(frame.select(pl.col(self._target_col).cast(pl.Float64).mean()).item())
        canon = frame["district"].map_elements(self._canonical, return_dtype=pl.Utf8)
        grouped = (
            frame.select(self._target_col)
            .with_columns(canon.alias("_canon"))
            .group_by("_canon")
            .agg(
                pl.len().alias("_n"),
                pl.col(self._target_col).mean().alias("_mean"),
            )
        )
        self._district_te = {
            row["_canon"]: (
                (row["_n"] * row["_mean"] + self._smoothing * global_mean)
                / (row["_n"] + self._smoothing)
            )
            for row in grouped.iter_rows(named=True)
        }
        self._global_mean = global_mean
        return self

    def transform(self, frame: pl.DataFrame) -> pl.DataFrame:
        """Emit the engineered feature frame.

        Args:
            frame: Listings frame (price not required at inference).

        Returns:
            A frame with exactly :data:`_OUTPUT_COLUMNS`.

        Raises:
            FeatureError: If called before :meth:`fit`.
        """
        if self._global_mean is None:
            msg = "transform called before fit"
            raise FeatureError(msg)

        canon = frame["district"].map_elements(self._canonical, return_dtype=pl.Utf8)
        district_te = canon.replace_strict(
            self._district_te, default=self._global_mean, return_dtype=pl.Float64
        )
        building_age = ((self._reference_year - pl.col("year_built")).clip(lower_bound=0)).alias(
            "building_age"
        )

        return frame.with_columns(
            building_age,
            district_te.alias("district_te"),
        ).select(*_OUTPUT_COLUMNS)
