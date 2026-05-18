"""Contract tests for prediction request/response models."""

from __future__ import annotations

from datetime import UTC, datetime
from decimal import Decimal

import pytest
from pydantic import ValidationError

from price_predictor.domain import PredictionRequest, PredictionResult, PropertyType


def test_prediction_request_rejects_price_field() -> None:
    with pytest.raises(ValidationError):
        PredictionRequest(
            area=50.0,
            rooms=2,
            city="Krakow",
            district="Stare Miasto",
            year_built=2000,
            floor=1,
            property_type=PropertyType.APARTMENT,
            price=Decimal("1"),
        )


def test_prediction_result_defaults_intervals_to_none() -> None:
    result = PredictionResult(
        predicted_price=Decimal("612345.00"),
        model_name="price-xgb",
        model_version="3",
        predicted_at=datetime(2026, 5, 18, tzinfo=UTC),
    )
    assert result.interval_low is None
    assert result.interval_high is None


def test_prediction_result_rejects_non_positive_price() -> None:
    with pytest.raises(ValidationError):
        PredictionResult(
            predicted_price=Decimal("0.00"),
            model_name="price-xgb",
            model_version="3",
            predicted_at=datetime(2026, 5, 18, tzinfo=UTC),
        )
