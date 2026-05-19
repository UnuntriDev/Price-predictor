"""The :class:`Listing` aggregate: one apartment record (Kaggle schema)."""

from __future__ import annotations

from datetime import UTC, date, datetime
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

NonEmptyStr = Annotated[
    str, StringConstraints(min_length=1, max_length=120, strip_whitespace=True)
]

_Distance = Annotated[float, Field(ge=0.0)]
_OptDistance = Annotated[float | None, Field(default=None, ge=0.0)]


class Listing(BaseModel):
    """One apartment listing from the Kaggle dataset.

    Immutable and ``extra='forbid'`` so dataset drift fails loudly.
    Nullable fields mirror the dataset's documented missingness; values
    are not invented.
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
    build_year: Annotated[
        int | None, Field(default=None, ge=constants.BUILD_YEAR_MIN)
    ]

    latitude: Annotated[
        float, Field(ge=constants.LATITUDE_MIN, le=constants.LATITUDE_MAX)
    ]
    longitude: Annotated[
        float, Field(ge=constants.LONGITUDE_MIN, le=constants.LONGITUDE_MAX)
    ]
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

    price_pln: Annotated[
        int, Field(ge=constants.PRICE_MIN_PLN, le=constants.PRICE_MAX_PLN)
    ]
    snapshot_month: date

    @model_validator(mode="after")
    def _build_year_not_future(self) -> Self:
        """Reject construction years after the current year."""
        if self.build_year is not None:
            ceiling = datetime.now(UTC).year
            if self.build_year > ceiling:
                msg = f"build_year {self.build_year} exceeds current year {ceiling}"
                raise ValueError(msg)
        return self

    @property
    def price_per_sqm(self) -> float:
        """Price per square metre in PLN."""
        return round(self.price_pln / self.square_meters, 2)
