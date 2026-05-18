"""Pandera-backed :class:`SchemaContract` (skeleton)."""

from __future__ import annotations

import polars as pl

from price_predictor.data.schemas import ListingFrame


class PanderaListingValidator:
    """Validates listing frames against :class:`ListingFrame`.

    The schema (the contract) is declared now; wiring Pandera's
    ``validate`` call and error translation to ``SchemaValidationError``
    is Phase 2.
    """

    schema: type[ListingFrame] = ListingFrame

    def validate(self, frame: pl.DataFrame) -> pl.DataFrame:
        """See :meth:`SchemaContract.validate`."""
        raise NotImplementedError("Phase 2: ListingFrame.validate(frame) -> SchemaValidationError")
