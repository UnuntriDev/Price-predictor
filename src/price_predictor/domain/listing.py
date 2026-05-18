"""The :class:`Listing` aggregate: one scraped Otodom offer."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Annotated, Self

from pydantic import BaseModel, ConfigDict, Field, StringConstraints, model_validator

from price_predictor.domain import constants
from price_predictor.domain.enums import PropertyType

NonEmptyStr = Annotated[str, StringConstraints(min_length=1, max_length=120, strip_whitespace=True)]


class Listing(BaseModel):
    """A single real-estate offer scraped from Otodom.

    This is the *raw* contract that crosses the scraping -> storage
    boundary. It is immutable and rejects unknown fields so that schema
    drift on the source site fails loudly instead of silently widening
    the model.

    Attributes:
        listing_id: Stable Otodom offer identifier (primary key).
        source_url: Canonical URL the record was scraped from.
        scraped_at: UTC timestamp of capture.
        price: Asking price in PLN.
        area: Usable floor area in square metres.
        rooms: Number of rooms.
        city: City the property is located in.
        district: District / neighbourhood within the city.
        year_built: Year of construction (or planned completion).
        floor: Floor index; ``0`` is ground, negatives are souterrain.
        property_type: Dwelling category.
    """

    model_config = ConfigDict(frozen=True, extra="forbid", str_strip_whitespace=True)

    listing_id: NonEmptyStr
    source_url: Annotated[str, Field(min_length=1, max_length=2048)]
    scraped_at: datetime

    price: Annotated[
        Decimal,
        Field(ge=constants.PRICE_MIN_PLN, le=constants.PRICE_MAX_PLN, decimal_places=2),
    ]
    area: Annotated[float, Field(ge=constants.AREA_MIN_SQM, le=constants.AREA_MAX_SQM)]
    rooms: Annotated[int, Field(ge=constants.ROOMS_MIN, le=constants.ROOMS_MAX)]
    city: NonEmptyStr
    district: NonEmptyStr
    year_built: Annotated[int, Field(ge=constants.YEAR_BUILT_MIN)]
    floor: Annotated[int, Field(ge=constants.FLOOR_MIN, le=constants.FLOOR_MAX)]
    property_type: PropertyType

    @model_validator(mode="after")
    def _year_not_implausibly_future(self) -> Self:
        """Reject construction years far past the capture date.

        Primary-market offers are sold before completion, so a small
        forward tolerance is allowed; anything beyond it is scrape noise.
        """
        ceiling = self.scraped_at.year + constants.YEAR_BUILT_FUTURE_TOLERANCE
        if self.year_built > ceiling:
            msg = f"year_built {self.year_built} exceeds plausible ceiling {ceiling}"
            raise ValueError(msg)
        return self

    @property
    def price_per_sqm(self) -> Decimal:
        """Asking price per square metre in PLN."""
        return (self.price / Decimal(str(self.area))).quantize(Decimal("0.01"))
