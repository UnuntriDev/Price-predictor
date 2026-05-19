"""Contract tests for prediction request/response models."""

from __future__ import annotations

from datetime import UTC, datetime

import pytest
from pydantic import ValidationError

from price_predictor.domain import (
    CityEnum,
    OwnershipType,
    PredictionRequest,
    PredictionResult,
)


def _req() -> dict[str, object]:
    return {
        "city": CityEnum.KRAKOW,
        "square_meters": 55.0,
        "rooms": 3,
        "latitude": 50.06,
        "longitude": 19.94,
        "centre_distance_km": 2.0,
        "poi_count": 8,
        "ownership": OwnershipType.COOPERATIVE,
        "has_parking": True,
        "has_balcony": False,
        "has_security": False,
        "has_storage": True,
    }


def test_minimal_request_constructs_with_optional_defaults() -> None:
    req = PredictionRequest(**_req())
    assert req.property_type is None
    assert req.build_year is None
    assert req.school_distance_km is None


def test_request_rejects_price_field() -> None:
    with pytest.raises(ValidationError):
        PredictionRequest(**_req(), price_pln=1)


def test_result_defaults_intervals_to_none() -> None:
    res = PredictionResult(
        predicted_price=612_345,
        model_name="price-predictor",
        model_version="3",
        predicted_at=datetime(2026, 5, 19, tzinfo=UTC),
    )
    assert res.interval_low is None
    assert res.interval_high is None


def test_result_rejects_non_positive_price() -> None:
    with pytest.raises(ValidationError):
        PredictionResult(
            predicted_price=0,
            model_name="m",
            model_version="1",
            predicted_at=datetime(2026, 5, 19, tzinfo=UTC),
        )
