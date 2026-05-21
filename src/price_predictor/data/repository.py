"""Postgres :class:`ListingRepository` (psycopg v3).

Natural key is ``(id, snapshot_month)`` — the dataset is a monthly
panel, the same listing id reappears across snapshots.
"""

from __future__ import annotations

from collections.abc import Iterable, Sequence

import psycopg
from psycopg.conninfo import conninfo_to_dict
from psycopg.rows import dict_row
from pydantic import SecretStr

from price_predictor.config.settings import PostgresSettings
from price_predictor.domain import Listing, StorageError

_COLUMNS = (
    "id",
    "city",
    "property_type",
    "square_meters",
    "rooms",
    "floor",
    "floor_count",
    "build_year",
    "latitude",
    "longitude",
    "centre_distance_km",
    "poi_count",
    "school_distance_km",
    "clinic_distance_km",
    "post_office_distance_km",
    "kindergarten_distance_km",
    "restaurant_distance_km",
    "college_distance_km",
    "pharmacy_distance_km",
    "ownership",
    "building_material",
    "condition",
    "has_parking",
    "has_balcony",
    "has_elevator",
    "has_security",
    "has_storage",
    "price_pln",
    "snapshot_month",
)

_CREATE_SCHEMA = """
CREATE TABLE IF NOT EXISTS listings (
    id                       TEXT NOT NULL,
    city                     TEXT NOT NULL,
    property_type            TEXT,
    square_meters            DOUBLE PRECISION NOT NULL,
    rooms                    INTEGER NOT NULL,
    floor                    INTEGER,
    floor_count              INTEGER,
    build_year               INTEGER,
    latitude                 DOUBLE PRECISION NOT NULL,
    longitude                DOUBLE PRECISION NOT NULL,
    centre_distance_km       DOUBLE PRECISION NOT NULL,
    poi_count                INTEGER NOT NULL,
    school_distance_km       DOUBLE PRECISION,
    clinic_distance_km       DOUBLE PRECISION,
    post_office_distance_km  DOUBLE PRECISION,
    kindergarten_distance_km DOUBLE PRECISION,
    restaurant_distance_km   DOUBLE PRECISION,
    college_distance_km      DOUBLE PRECISION,
    pharmacy_distance_km     DOUBLE PRECISION,
    ownership                TEXT NOT NULL,
    building_material        TEXT,
    condition                TEXT,
    has_parking              BOOLEAN NOT NULL,
    has_balcony              BOOLEAN NOT NULL,
    has_elevator             BOOLEAN,
    has_security             BOOLEAN NOT NULL,
    has_storage              BOOLEAN NOT NULL,
    price_pln                BIGINT NOT NULL,
    snapshot_month           DATE NOT NULL,
    PRIMARY KEY (id, snapshot_month)
);
"""

_PLACEHOLDERS = ", ".join(f"%({c})s" for c in _COLUMNS)
_UPDATE_SET = ", ".join(
    f"{c} = EXCLUDED.{c}" for c in _COLUMNS if c not in {"id", "snapshot_month"}
)
_UPSERT = (
    f"INSERT INTO listings ({', '.join(_COLUMNS)}) VALUES ({_PLACEHOLDERS}) "
    f"ON CONFLICT (id, snapshot_month) DO UPDATE SET {_UPDATE_SET};"
)
_SELECT_ALL = f"SELECT {', '.join(_COLUMNS)} FROM listings ORDER BY id, snapshot_month;"


def _row(listing: Listing) -> dict[str, object]:
    data = listing.model_dump()
    for enum_col in ("city", "property_type", "ownership", "building_material", "condition"):
        value = data[enum_col]
        if value is not None:
            data[enum_col] = value.value if hasattr(value, "value") else value
    return data


class PostgresListingRepository:
    """psycopg v3 adapter for the listings table."""

    def __init__(self, settings: PostgresSettings) -> None:
        self._settings = settings

    @classmethod
    def from_dsn(cls, dsn: str) -> PostgresListingRepository:
        """Build from a libpq connection string."""
        info = conninfo_to_dict(dsn)
        return cls(
            PostgresSettings(
                host=str(info.get("host", "localhost")),
                port=int(str(info.get("port", 5432))),
                user=str(info.get("user", "price_predictor")),
                password=SecretStr(str(info.get("password", ""))),
                database=str(info.get("dbname", "price_predictor")),
            )
        )

    def create_schema(self) -> None:
        """Create the ``listings`` table if absent."""
        try:
            with psycopg.connect(self._settings.dsn) as conn:
                conn.execute(_CREATE_SCHEMA)
        except psycopg.Error as exc:
            msg = f"could not create schema: {exc}"
            raise StorageError(msg) from exc

    def upsert_many(self, listings: Iterable[Listing]) -> int:
        """See :meth:`ListingRepository.upsert_many`."""
        rows = [_row(listing) for listing in listings]
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
