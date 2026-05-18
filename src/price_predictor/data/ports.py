"""I/O ports for the data layer.

Everything the data layer needs from the outside world is expressed as a
``Protocol`` so adapters (Postgres, DuckDB, Pandera) are swappable and
unit tests can substitute fakes without a database.
"""

from __future__ import annotations

from collections.abc import Iterable, Sequence
from typing import Protocol, runtime_checkable

import polars as pl

from price_predictor.domain import Listing


@runtime_checkable
class ListingRepository(Protocol):
    """Durable store of canonical :class:`Listing` records (Postgres)."""

    def upsert_many(self, listings: Iterable[Listing]) -> int:
        """Insert or update listings keyed by ``listing_id``.

        Returns:
            The number of rows written.
        """
        ...

    def fetch_all(self) -> Sequence[Listing]:
        """Return every stored listing."""
        ...


@runtime_checkable
class DataFrameStore(Protocol):
    """Columnar analytics store for feature/training frames (DuckDB)."""

    def write(self, name: str, frame: pl.DataFrame) -> None:
        """Persist ``frame`` under a logical ``name``."""
        ...

    def read(self, name: str) -> pl.DataFrame:
        """Load a previously written frame by ``name``."""
        ...


@runtime_checkable
class SchemaContract(Protocol):
    """Validates a dataframe against a declared schema."""

    def validate(self, frame: pl.DataFrame) -> pl.DataFrame:
        """Return ``frame`` unchanged if valid, else raise.

        Raises:
            SchemaValidationError: If the frame violates the contract.
        """
        ...
