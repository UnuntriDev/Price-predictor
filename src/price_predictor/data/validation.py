"""Pandera-backed :class:`SchemaContract`."""

from __future__ import annotations

import pandera.errors as pa_errors
import polars as pl
import polars.exceptions as pl_errors

from price_predictor.data.schemas import RawListingSchema
from price_predictor.domain import SchemaValidationError


class PanderaListingValidator:
    """``RawListingSchema`` enforcement; all failures funnel into one domain error."""

    schema: type[RawListingSchema] = RawListingSchema

    def validate(self, frame: pl.DataFrame) -> pl.DataFrame:
        """See :meth:`SchemaContract.validate`."""
        try:
            validated: pl.DataFrame = RawListingSchema.validate(frame, lazy=True)
        except (
            pa_errors.SchemaError,
            pa_errors.SchemaErrors,
            pl_errors.PolarsError,
        ) as exc:
            raise SchemaValidationError(str(exc)) from exc
        return validated
