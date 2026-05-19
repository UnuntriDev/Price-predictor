"""Inference request/response contracts.

The request carries the modelled features (ADR 0014); it is decoupled
from :class:`Listing` because the caller supplies no id, price, or
snapshot month.
"""

from __future__ import annotations

from datetime import datetime
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field

from price_predictor.domain import constants
from price_predictor.domain.enums import (
    BuildingMaterial,
    CityEnum,
    ConditionType,
    OwnershipType,
    PropertyType,
)
from price_predictor.domain.listing import NonEmptyStr

_OptDist = Annotated[float | None, Field(default=None, ge=0.0)]


class PredictionRequest(BaseModel):
    """Features a caller supplies to value an apartment."""

    model_config = ConfigDict(frozen=True, extra="forbid", str_strip_whitespace=True)

    city: CityEnum
    property_type: PropertyType | None = None
    square_meters: Annotated[
        float,
        Field(ge=constants.SQUARE_METERS_MIN, le=constants.SQUARE_METERS_MAX),
    ]
    rooms: Annotated[int, Field(ge=constants.ROOMS_MIN, le=constants.ROOMS_MAX)]
    floor: Annotated[
        int | None, Field(default=None, ge=constants.FLOOR_MIN, le=constants.FLOOR_MAX)
    ]
    floor_count: Annotated[int | None, Field(default=None, ge=0, le=constants.FLOOR_MAX)]
    build_year: Annotated[
        int | None, Field(default=None, ge=constants.BUILD_YEAR_MIN)
    ]
    latitude: Annotated[
        float, Field(ge=constants.LATITUDE_MIN, le=constants.LATITUDE_MAX)
    ]
    longitude: Annotated[
        float, Field(ge=constants.LONGITUDE_MIN, le=constants.LONGITUDE_MAX)
    ]
    centre_distance_km: Annotated[float, Field(ge=0.0)]
    poi_count: Annotated[int, Field(ge=0)]
    school_distance_km: _OptDist
    clinic_distance_km: _OptDist
    post_office_distance_km: _OptDist
    kindergarten_distance_km: _OptDist
    restaurant_distance_km: _OptDist
    college_distance_km: _OptDist
    pharmacy_distance_km: _OptDist
    ownership: OwnershipType
    building_material: BuildingMaterial | None = None
    condition: ConditionType | None = None
    has_parking: bool
    has_balcony: bool
    has_elevator: bool | None = None
    has_security: bool
    has_storage: bool


class PredictionResult(BaseModel):
    """A model's valuation of a :class:`PredictionRequest`.

    Attributes:
        predicted_price: Point estimate in PLN.
        interval_low: Lower bound of the prediction interval, if any.
        interval_high: Upper bound of the prediction interval, if any.
        model_name: Registered model name that produced the estimate.
        model_version: Registered model version string.
        predicted_at: UTC timestamp the inference was served.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    predicted_price: Annotated[int, Field(gt=0)]
    interval_low: Annotated[int | None, Field(default=None, ge=0)]
    interval_high: Annotated[int | None, Field(default=None, ge=0)]
    model_name: NonEmptyStr
    model_version: NonEmptyStr
    predicted_at: datetime
