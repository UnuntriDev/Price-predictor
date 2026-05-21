"""The :class:`Listing` aggregate: one apartment record (Kaggle schema)."""

from __future__ import annotations

from datetime import date
from typing import Annotated, Self

from pydantic import BaseModel, ConfigDict, Field, StringConstraints, model_validator

from price_predictor.domain import constants
from price_predictor.domain.enums import (
    BuildingMaterial,
    CityEnum,
    ConditionType,
    OwnershipType,
    PropertyType,
)
from price_predictor.domain.validation import validate_build_year_not_future

NonEmptyStr = Annotated[str, StringConstraints(min_length=1, max_length=120, strip_whitespace=True)]

_Distance = Annotated[float, Field(ge=0.0)]
_OptDistance = Annotated[float | None, Field(default=None, ge=0.0)]


class Listing(BaseModel):
    """One Kaggle apartment row.

    Frozen + ``extra='forbid'`` so dataset drift fails loud. Nullable
    fields follow the dataset's own missingness — never imputed here.
    """

    model_config = ConfigDict(frozen=True, extra="forbid", str_strip_whitespace=True)

    id: NonEmptyStr
    city: CityEnum
    property_type: PropertyType | None = None

    square_meters: Annotated[
        float,
        Field(
            ge=constants.SQUARE_METERS_MIN,
            le=constants.SQUARE_METERS_MAX,
        ),
    ]
    rooms: Annotated[int, Field(ge=constants.ROOMS_MIN, le=constants.ROOMS_MAX)]
    floor: Annotated[
        int | None, Field(default=None, ge=constants.FLOOR_MIN, le=constants.FLOOR_MAX)
    ]
    floor_count: Annotated[int | None, Field(default=None, ge=0, le=constants.FLOOR_MAX)]
    build_year: Annotated[int | None, Field(default=None, ge=constants.BUILD_YEAR_MIN)]

    latitude: Annotated[float, Field(ge=constants.LATITUDE_MIN, le=constants.LATITUDE_MAX)]
    longitude: Annotated[float, Field(ge=constants.LONGITUDE_MIN, le=constants.LONGITUDE_MAX)]
    centre_distance_km: _Distance

    poi_count: Annotated[int, Field(ge=0)]
    school_distance_km: _OptDistance
    clinic_distance_km: _OptDistance
    post_office_distance_km: _OptDistance
    kindergarten_distance_km: _OptDistance
    restaurant_distance_km: _OptDistance
    college_distance_km: _OptDistance
    pharmacy_distance_km: _OptDistance

    ownership: OwnershipType
    building_material: BuildingMaterial | None = None
    condition: ConditionType | None = None

    has_parking: bool
    has_balcony: bool
    has_elevator: bool | None = None
    has_security: bool
    has_storage: bool

    price_pln: Annotated[int, Field(ge=constants.PRICE_MIN_PLN, le=constants.PRICE_MAX_PLN)]
    snapshot_month: date

    @model_validator(mode="after")
    def _build_year_not_future(self) -> Self:
        """No build years past today."""
        validate_build_year_not_future(self.build_year)
        return self

    @property
    def price_per_sqm(self) -> float:
        """PLN per m²."""
        return round(self.price_pln / self.square_meters, 2)
