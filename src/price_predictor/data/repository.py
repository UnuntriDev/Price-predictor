"""Postgres-backed :class:`ListingRepository` (psycopg v3)."""

from __future__ import annotations

from collections.abc import Iterable, Sequence

import psycopg
from psycopg.rows import dict_row

from price_predictor.config.settings import PostgresSettings
from price_predictor.domain import Listing, StorageError

_COLUMNS = (
    "listing_id",
    "source_url",
    "scraped_at",
    "price",
    "area",
    "rooms",
    "city",
    "district",
    "year_built",
    "floor",
    "property_type",
)

_CREATE_SCHEMA = """
CREATE TABLE IF NOT EXISTS listings (
    listing_id    TEXT PRIMARY KEY,
    source_url    TEXT NOT NULL,
    scraped_at    TIMESTAMPTZ NOT NULL,
    price         NUMERIC(12, 2) NOT NULL,
    area          DOUBLE PRECISION NOT NULL,
    rooms         INTEGER NOT NULL,
    city          TEXT NOT NULL,
    district      TEXT NOT NULL,
    year_built    INTEGER NOT NULL,
    floor         INTEGER NOT NULL,
    property_type TEXT NOT NULL
);
"""

_UPSERT = """
INSERT INTO listings (
    listing_id, source_url, scraped_at, price, area, rooms,
    city, district, year_built, floor, property_type
) VALUES (
    %(listing_id)s, %(source_url)s, %(scraped_at)s, %(price)s, %(area)s,
    %(rooms)s, %(city)s, %(district)s, %(year_built)s, %(floor)s,
    %(property_type)s
)
ON CONFLICT (listing_id) DO UPDATE SET
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at,
    price = EXCLUDED.price,
    area = EXCLUDED.area,
    rooms = EXCLUDED.rooms,
    city = EXCLUDED.city,
    district = EXCLUDED.district,
    year_built = EXCLUDED.year_built,
    floor = EXCLUDED.floor,
    property_type = EXCLUDED.property_type;
"""

_SELECT_ALL = f"SELECT {', '.join(_COLUMNS)} FROM listings ORDER BY listing_id;"


class PostgresListingRepository:
    """Persists listings in Postgres via psycopg v3.

    Args:
        settings: Connection parameters. Injected, never read from a
            module-level global, so tests can point at a throwaway DB.
    """

    def __init__(self, settings: PostgresSettings) -> None:
        self._settings = settings

    def create_schema(self) -> None:
        """Create the ``listings`` table if it does not exist.

        Raises:
            StorageError: On any connection/DDL failure.
        """
        try:
            with psycopg.connect(self._settings.dsn) as conn:
                conn.execute(_CREATE_SCHEMA)
        except psycopg.Error as exc:
            msg = f"could not create schema: {exc}"
            raise StorageError(msg) from exc

    def upsert_many(self, listings: Iterable[Listing]) -> int:
        """See :meth:`ListingRepository.upsert_many`."""
        rows = [
            {
                "listing_id": listing.listing_id,
                "source_url": listing.source_url,
                "scraped_at": listing.scraped_at,
                "price": listing.price,
                "area": listing.area,
                "rooms": listing.rooms,
                "city": listing.city,
                "district": listing.district,
                "year_built": listing.year_built,
                "floor": listing.floor,
                "property_type": listing.property_type.value,
            }
            for listing in listings
        ]
        if not rows:
            return 0
        try:
            with psycopg.connect(self._settings.dsn) as conn, conn.cursor() as cur:
                cur.executemany(_UPSERT, rows)
        except psycopg.Error as exc:
            msg = f"upsert failed: {exc}"
            raise StorageError(msg) from exc
        return len(rows)

    def fetch_all(self) -> Sequence[Listing]:
        """See :meth:`ListingRepository.fetch_all`."""
        try:
            with (
                psycopg.connect(self._settings.dsn, row_factory=dict_row) as conn,
                conn.cursor() as cur,
            ):
                cur.execute(_SELECT_ALL)
                return [Listing(**row) for row in cur]
        except psycopg.Error as exc:
            msg = f"fetch_all failed: {exc}"
            raise StorageError(msg) from exc
