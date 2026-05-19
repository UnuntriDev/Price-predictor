"""Declarative Pandera contract for the normalised listings frame.

The dataframe analogue of :class:`price_predictor.domain.Listing` for
the Kaggle "Apartment Prices in Poland" data, *after* the loader has
renamed columns to snake_case, mapped yes/no booleans, and added
``snapshot_month``. Nullable fields mirror the dataset's documented
missingness (ADR 0014) — rows are validated, not dropped.
"""

from __future__ import annotations

from enum import StrEnum

import pandera.polars as pa
from pandera.typing.polars import Series

from price_predictor.domain import constants
from price_predictor.domain.enums import (
    BuildingMaterial,
    CityEnum,
    ConditionType,
    OwnershipType,
    PropertyType,
)


def _values(enum: type[StrEnum]) -> list[str]:
    return [member.value for member in enum]


class RawListingSchema(pa.DataFrameModel):
    """Schema for the normalised Kaggle listings frame (29 columns)."""

    # Not unique: monthly snapshots re-observe the same listing id.
    id: Series[str] = pa.Field(nullable=False)
    city: Series[str] = pa.Field(isin=_values(CityEnum), nullable=False)
    property_type: Series[str] = pa.Field(isin=_values(PropertyType), nullable=True)
    square_meters: Series[float] = pa.Field(
        ge=constants.SQUARE_METERS_MIN, le=constants.SQUARE_METERS_MAX
    )
    rooms: Series[int] = pa.Field(ge=constants.ROOMS_MIN, le=constants.ROOMS_MAX)
    floor: Series[int] = pa.Field(ge=constants.FLOOR_MIN, le=constants.FLOOR_MAX, nullable=True)
    floor_count: Series[int] = pa.Field(ge=0, le=constants.FLOOR_MAX, nullable=True)
    build_year: Series[int] = pa.Field(ge=constants.BUILD_YEAR_MIN, nullable=True)
    latitude: Series[float] = pa.Field(ge=constants.LATITUDE_MIN, le=constants.LATITUDE_MAX)
    longitude: Series[float] = pa.Field(ge=constants.LONGITUDE_MIN, le=constants.LONGITUDE_MAX)
    centre_distance_km: Series[float] = pa.Field(ge=0.0)
    poi_count: Series[int] = pa.Field(ge=0)
    school_distance_km: Series[float] = pa.Field(ge=0.0, nullable=True)
    clinic_distance_km: Series[float] = pa.Field(ge=0.0, nullable=True)
    post_office_distance_km: Series[float] = pa.Field(ge=0.0, nullable=True)
    kindergarten_distance_km: Series[float] = pa.Field(ge=0.0, nullable=True)
    restaurant_distance_km: Series[float] = pa.Field(ge=0.0, nullable=True)
    college_distance_km: Series[float] = pa.Field(ge=0.0, nullable=True)
    pharmacy_distance_km: Series[float] = pa.Field(ge=0.0, nullable=True)
    ownership: Series[str] = pa.Field(isin=_values(OwnershipType), nullable=False)
    building_material: Series[str] = pa.Field(isin=_values(BuildingMaterial), nullable=True)
    condition: Series[str] = pa.Field(isin=_values(ConditionType), nullable=True)
    has_parking: Series[bool] = pa.Field(nullable=False)
    has_balcony: Series[bool] = pa.Field(nullable=False)
    has_elevator: Series[bool] = pa.Field(nullable=True)
    has_security: Series[bool] = pa.Field(nullable=False)
    has_storage: Series[bool] = pa.Field(nullable=False)
    price_pln: Series[int] = pa.Field(ge=constants.PRICE_MIN_PLN, le=constants.PRICE_MAX_PLN)
    snapshot_month: Series[str] = pa.Field(nullable=False)

    class Config:
        """Pandera options."""

        strict = True
        coerce = True
