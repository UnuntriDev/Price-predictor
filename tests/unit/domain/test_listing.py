"""Contract tests for the Listing aggregate."""

from __future__ import annotations

from datetime import UTC, datetime
from decimal import Decimal

import pytest
from pydantic import ValidationError

from price_predictor.domain import Listing, PropertyType


def _valid_kwargs() -> dict[str, object]:
    return {
        "listing_id": "OT-12345",
        "source_url": "https://www.otodom.pl/pl/oferta/OT-12345",
        "scraped_at": datetime(2026, 5, 1, tzinfo=UTC),
        "price": Decimal("750000.00"),
        "area": 52.0,
        "rooms": 3,
        "city": "Warszawa",
        "district": "Mokotow",
        "year_built": 2015,
        "floor": 4,
        "property_type": PropertyType.APARTMENT,
    }


def test_valid_listing_constructs() -> None:
    listing = Listing(**_valid_kwargs())
    assert listing.city == "Warszawa"
    assert listing.property_type is PropertyType.APARTMENT


def test_listing_is_frozen() -> None:
    listing = Listing(**_valid_kwargs())
    with pytest.raises(ValidationError):
        listing.price = Decimal("1.00")  # type: ignore[misc]


def test_unknown_field_is_rejected() -> None:
    with pytest.raises(ValidationError):
        Listing(**_valid_kwargs(), broker="ACME Realty")


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("price", Decimal("100.00")),
        ("area", 1.0),
        ("rooms", 0),
        ("floor", -9),
        ("year_built", 1700),
    ],
)
def test_out_of_range_values_rejected(field: str, value: object) -> None:
    with pytest.raises(ValidationError):
        Listing(**{**_valid_kwargs(), field: value})


def test_year_built_future_tolerance() -> None:
    kwargs = _valid_kwargs()
    Listing(**{**kwargs, "year_built": 2030})  # within +5 tolerance
    with pytest.raises(ValidationError, match="plausible ceiling"):
        Listing(**{**kwargs, "year_built": 2099})


def test_price_per_sqm_is_quantized() -> None:
    listing = Listing(**{**_valid_kwargs(), "price": Decimal("750000.00"), "area": 52.0})
    assert listing.price_per_sqm == Decimal("14423.08")
