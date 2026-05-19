"""Pandera-backed :class:`SchemaContract`."""

from __future__ import annotations

import pandera.errors as pa_errors
import polars as pl
import polars.exceptions as pl_errors

from price_predictor.data.schemas import ListingFrame
from price_predictor.domain import SchemaValidationError


class PanderaListingValidator:
    """Validates listing frames against :class:`ListingFrame`.

    Pandera's failure modes (wrong dtype, out-of-bound value, missing or
    extra column, duplicate id) are aggregated with ``lazy=True`` and
    re-raised as the single domain error the rest of the codebase knows
    how to catch.
    """

    schema: type[ListingFrame] = ListingFrame

    def validate(self, frame: pl.DataFrame) -> pl.DataFrame:
        """See :meth:`SchemaContract.validate`.

        Args:
            frame: The candidate listings frame.

        Returns:
            The validated (and coerced) frame.

        Raises:
            SchemaValidationError: If ``frame`` violates the contract.
        """
        try:
            validated: pl.DataFrame = ListingFrame.validate(frame, lazy=True)
        except (
            pa_errors.SchemaError,
            pa_errors.SchemaErrors,
            pl_errors.PolarsError,
        ) as exc:
            raise SchemaValidationError(str(exc)) from exc
        return validated
