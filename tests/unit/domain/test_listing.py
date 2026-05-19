"""Contract tests for the Kaggle-schema Listing aggregate."""

from __future__ import annotations

from datetime import UTC, date, datetime

import pytest
from pydantic import ValidationError

from price_predictor.domain import (
    BuildingMaterial,
    CityEnum,
    ConditionType,
    Listing,
    OwnershipType,
    PropertyType,
)


def _valid() -> dict[str, object]:
    return {
        "id": "abc-1",
        "city": CityEnum.WARSZAWA,
        "property_type": PropertyType.BLOCK_OF_FLATS,
        "square_meters": 52.0,
        "rooms": 3,
        "floor": 4,
        "floor_count": 10,
        "build_year": 2015,
        "latitude": 52.23,
        "longitude": 21.01,
        "centre_distance_km": 3.5,
        "poi_count": 12,
        "school_distance_km": 0.4,
        "clinic_distance_km": 0.8,
        "post_office_distance_km": 0.5,
        "kindergarten_distance_km": 0.3,
        "restaurant_distance_km": 0.1,
        "college_distance_km": 2.0,
        "pharmacy_distance_km": 0.2,
        "ownership": OwnershipType.CONDOMINIUM,
        "building_material": BuildingMaterial.BRICK,
        "condition": ConditionType.PREMIUM,
        "has_parking": True,
        "has_balcony": True,
        "has_elevator": True,
        "has_security": False,
        "has_storage": True,
        "price_pln": 750_000,
        "snapshot_month": date(2024, 1, 1),
    }


def test_valid_listing_constructs() -> None:
    listing = Listing(**_valid())
    assert listing.city is CityEnum.WARSZAWA
    assert listing.price_per_sqm == round(750_000 / 52.0, 2)


def test_optional_fields_default_to_none() -> None:
    kwargs = _valid()
    for opt in (
        "property_type",
        "floor",
        "build_year",
        "building_material",
        "condition",
        "has_elevator",
    ):
        del kwargs[opt]
    listing = Listing(**kwargs)
    assert listing.property_type is None
    assert listing.has_elevator is None


def test_is_frozen_and_forbids_extra() -> None:
    listing = Listing(**_valid())
    with pytest.raises(ValidationError):
        listing.price_pln = 1  # type: ignore[misc]
    with pytest.raises(ValidationError):
        Listing(**_valid(), district="Wola")


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("price_pln", 0),
        ("square_meters", 10.0),
        ("square_meters", 200.0),
        ("rooms", 0),
        ("latitude", 60.0),
        ("longitude", 30.0),
        ("ownership", "freehold"),
        ("city", "berlin"),
    ],
)
def test_out_of_range_or_bad_enum_rejected(field: str, value: object) -> None:
    with pytest.raises(ValidationError):
        Listing(**{**_valid(), field: value})


def test_build_year_not_future() -> None:
    future = datetime.now(UTC).year + 1
    with pytest.raises(ValidationError, match="exceeds current year"):
        Listing(**{**_valid(), "build_year": future})


def test_ownership_accepts_polish_share_value() -> None:
    listing = Listing(**{**_valid(), "ownership": "udział"})
    assert listing.ownership is OwnershipType.SHARE
