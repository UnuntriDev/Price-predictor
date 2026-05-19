"""PriceFeaturePipeline: engineered features + smoothed district TE."""

from __future__ import annotations

import polars as pl
import pytest

from price_predictor.domain import FeatureError
from price_predictor.features import FeatureTransformer, PriceFeaturePipeline

_OUTPUT = ["area", "rooms", "floor", "building_age", "district_te", "city", "property_type"]


def _train_frame() -> pl.DataFrame:
    return pl.DataFrame(
        {
            "listing_id": ["a", "b", "c"],
            "price": [600_000.0, 800_000.0, 400_000.0],
            "area": [60.0, 80.0, 40.0],
            "rooms": [3, 4, 2],
            "city": ["Warszawa", "Warszawa", "Warszawa"],
            "district": ["Mokotów", "mokotow", "Wola"],
            "year_built": [2005, 2015, 1995],
            "floor": [2, 5, 1],
            "property_type": ["apartment", "apartment", "house"],
        }
    )


def test_satisfies_port() -> None:
    assert isinstance(PriceFeaturePipeline(reference_year=2025), FeatureTransformer)


def test_transform_before_fit_raises() -> None:
    with pytest.raises(FeatureError, match="before fit"):
        PriceFeaturePipeline(reference_year=2025).transform(_train_frame())


def test_fit_requires_target() -> None:
    pipe = PriceFeaturePipeline(reference_year=2025)
    with pytest.raises(FeatureError, match="target column"):
        pipe.fit(_train_frame().drop("price"))


def test_engineered_columns_and_no_target_leak() -> None:
    pipe = PriceFeaturePipeline(reference_year=2025).fit(_train_frame())
    out = pipe.transform(_train_frame())
    assert out.columns == _OUTPUT
    assert "price" not in out.columns
    assert out["building_age"].to_list() == [20, 10, 30]


def test_smoothed_district_target_encoding() -> None:
    # global mean = 600000; smoothing = 10
    # mokotow: n=2 mean=700000 -> (2*700000 + 10*600000)/12
    # wola:    n=1 mean=400000 -> (1*400000 + 10*600000)/11
    pipe = PriceFeaturePipeline(reference_year=2025, smoothing=10.0).fit(_train_frame())
    te = pipe.transform(_train_frame())["district_te"].to_list()
    assert te[0] == pytest.approx(7_400_000 / 12)
    assert te[1] == pytest.approx(7_400_000 / 12)
    assert te[2] == pytest.approx(6_400_000 / 11)


def test_unseen_district_falls_back_to_global_mean() -> None:
    pipe = PriceFeaturePipeline(reference_year=2025).fit(_train_frame())
    unseen = _train_frame().with_columns(district=pl.lit("Ursynów"))
    assert pipe.transform(unseen)["district_te"].to_list() == pytest.approx(
        [600_000.0, 600_000.0, 600_000.0]
    )


def test_canonical_dictionary_collapses_aliases() -> None:
    pipe = PriceFeaturePipeline(
        reference_year=2025,
        district_dictionary={"srodmiescie": "centrum", "Wola": "centrum"},
    ).fit(_train_frame())
    # Mokotow stays itself; Wola -> centrum. Distinct canonical means.
    frame = _train_frame().with_columns(district=pl.Series(["Wola", "Wola", "Mokotów"]))
    out = pipe.transform(frame)["district_te"].to_list()
    assert out[0] == out[1]  # both canonical 'centrum'
