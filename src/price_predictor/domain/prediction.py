"""Inference request/response contracts.

These are the public API and persistence shapes for the ``predictions``
table; they are deliberately decoupled from :class:`Listing` because the
caller never supplies a price and may not have an offer id.
"""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field

from price_predictor.domain import constants
from price_predictor.domain.enums import PropertyType
from price_predictor.domain.listing import NonEmptyStr


class PredictionRequest(BaseModel):
    """Features a caller supplies to value a property."""

    model_config = ConfigDict(frozen=True, extra="forbid", str_strip_whitespace=True)

    area: Annotated[float, Field(ge=constants.AREA_MIN_SQM, le=constants.AREA_MAX_SQM)]
    rooms: Annotated[int, Field(ge=constants.ROOMS_MIN, le=constants.ROOMS_MAX)]
    city: NonEmptyStr
    district: NonEmptyStr
    year_built: Annotated[int, Field(ge=constants.YEAR_BUILT_MIN)]
    floor: Annotated[int, Field(ge=constants.FLOOR_MIN, le=constants.FLOOR_MAX)]
    property_type: PropertyType


class PredictionResult(BaseModel):
    """A model's valuation of a :class:`PredictionRequest`.

    Attributes:
        predicted_price: Point estimate in PLN.
        interval_low: Lower bound of the prediction interval, if the model
            exposes one.
        interval_high: Upper bound of the prediction interval, if any.
        model_name: Registered model name that produced the estimate.
        model_version: Registered model version string.
        predicted_at: UTC timestamp the inference was served.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    predicted_price: Annotated[Decimal, Field(gt=Decimal("0"), decimal_places=2)]
    interval_low: Annotated[Decimal | None, Field(default=None, ge=Decimal("0"))]
    interval_high: Annotated[Decimal | None, Field(default=None, ge=Decimal("0"))]
    model_name: NonEmptyStr
    model_version: NonEmptyStr
    predicted_at: datetime
