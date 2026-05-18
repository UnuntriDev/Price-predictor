"""Postgres-backed :class:`ListingRepository` (skeleton)."""

from __future__ import annotations

from collections.abc import Iterable, Sequence

from price_predictor.config.settings import PostgresSettings
from price_predictor.domain import Listing


class PostgresListingRepository:
    """Persists listings in Postgres via psycopg v3.

    Args:
        settings: Connection parameters. Injected, never read from a
            module-level global, so tests can point at a throwaway DB.
    """

    def __init__(self, settings: PostgresSettings) -> None:
        self._settings = settings

    def upsert_many(self, listings: Iterable[Listing]) -> int:
        """See :meth:`ListingRepository.upsert_many`."""
        raise NotImplementedError("Phase 2: bulk upsert into the `listings` table via psycopg")

    def fetch_all(self) -> Sequence[Listing]:
        """See :meth:`ListingRepository.fetch_all`."""
        raise NotImplementedError("Phase 2: SELECT * FROM listings -> Listing")
