"""PanderaListingValidator enforces the ListingFrame contract."""

from __future__ import annotations

from collections.abc import Callable

import polars as pl
import pytest

from price_predictor.data import PanderaListingValidator
from price_predictor.domain import SchemaValidationError


def _valid_frame() -> pl.DataFrame:
    return pl.DataFrame(
        {
            "listing_id": ["OT-1", "OT-2"],
            "price": [500_000.0, 750_000.0],
            "area": [50.0, 70.0],
            "rooms": [2, 3],
            "city": ["Warszawa", "Krakow"],
            "district": ["Wola", "Stare Miasto"],
            "year_built": [2000, 2010],
            "floor": [2, 5],
            "property_type": ["apartment", "house"],
        }
    )


def test_valid_frame_passes_through() -> None:
    out = PanderaListingValidator().validate(_valid_frame())
    assert out.height == 2
    assert set(out.columns) == set(_valid_frame().columns)


@pytest.mark.parametrize(
    "mutate",
    [
        pytest.param(lambda f: f.with_columns(price=pl.lit(100.0)), id="price-too-low"),
        pytest.param(lambda f: f.with_columns(listing_id=pl.lit("DUP")), id="duplicate-id"),
        pytest.param(lambda f: f.drop("rooms"), id="missing-column"),
        pytest.param(lambda f: f.with_columns(extra=pl.lit(1)), id="extra-column-strict"),
        pytest.param(
            lambda f: f.with_columns(property_type=pl.lit("villa")),
            id="bad-property-type",
        ),
    ],
)
def test_contract_violations_raise_domain_error(
    mutate: Callable[[pl.DataFrame], pl.DataFrame],
) -> None:
    with pytest.raises(SchemaValidationError):
        PanderaListingValidator().validate(mutate(_valid_frame()))
