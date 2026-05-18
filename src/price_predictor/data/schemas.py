"""Declarative Pandera contract for the listings frame.

This is the dataframe analogue of :class:`price_predictor.domain.Listing`:
a *contract*, not logic. Bounds are sourced from the same domain
constants so the row model and the frame schema cannot drift apart.
"""

from __future__ import annotations

import pandera.polars as pa
from pandera.typing.polars import Series

from price_predictor.domain import constants
from price_predictor.domain.enums import PropertyType


class ListingFrame(pa.DataFrameModel):
    """Pandera schema mirroring the modelled Otodom fields."""

    listing_id: Series[str] = pa.Field(nullable=False, unique=True)
    price: Series[float] = pa.Field(
        ge=float(constants.PRICE_MIN_PLN), le=float(constants.PRICE_MAX_PLN)
    )
    area: Series[float] = pa.Field(ge=constants.AREA_MIN_SQM, le=constants.AREA_MAX_SQM)
    rooms: Series[int] = pa.Field(ge=constants.ROOMS_MIN, le=constants.ROOMS_MAX)
    city: Series[str] = pa.Field(nullable=False)
    district: Series[str] = pa.Field(nullable=False)
    year_built: Series[int] = pa.Field(ge=constants.YEAR_BUILT_MIN)
    floor: Series[int] = pa.Field(ge=constants.FLOOR_MIN, le=constants.FLOOR_MAX)
    property_type: Series[str] = pa.Field(isin=[member.value for member in PropertyType])

    class Config:
        """Pandera options."""

        strict = True
        coerce = True
