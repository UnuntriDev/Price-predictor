"""Postgres repository round-trip.

Skipped unless ``PP_TEST_PG_DSN`` points at a disposable database
(e.g. the docker-compose ``postgres`` service). No network/docker is
assumed by default, so local + current CI stay green.
"""

from __future__ import annotations

import os
from datetime import UTC, datetime
from decimal import Decimal

import psycopg
import pytest
from psycopg.conninfo import conninfo_to_dict
from pydantic import SecretStr

from price_predictor.config.settings import PostgresSettings
from price_predictor.data import PostgresListingRepository
from price_predictor.domain import Listing, PropertyType

_DSN = os.environ.get("PP_TEST_PG_DSN")

pytestmark = [
    pytest.mark.integration,
    pytest.mark.skipif(_DSN is None, reason="set PP_TEST_PG_DSN to run"),
]


def _settings() -> PostgresSettings:
    info = conninfo_to_dict(_DSN or "")
    return PostgresSettings(
        host=str(info.get("host", "localhost")),
        port=int(info.get("port", 5432)),
        user=str(info.get("user", "price_predictor")),
        password=SecretStr(str(info.get("password", ""))),
        database=str(info.get("dbname", "price_predictor")),
    )


def _listing(listing_id: str) -> Listing:
    return Listing(
        listing_id=listing_id,
        source_url=f"https://www.otodom.pl/pl/oferta/{listing_id}",
        scraped_at=datetime(2026, 5, 19, tzinfo=UTC),
        price=Decimal("750000.00"),
        area=52.0,
        rooms=3,
        city="Warszawa",
        district="Mokotow",
        year_built=2015,
        floor=4,
        property_type=PropertyType.APARTMENT,
    )


def test_create_upsert_fetch_is_idempotent() -> None:
    repo = PostgresListingRepository(_settings())
    repo.create_schema()
    key = "IT-PG-1"

    assert repo.upsert_many([_listing(key)]) == 1
    assert repo.upsert_many([_listing(key)]) == 1  # idempotent

    stored = {row.listing_id: row for row in repo.fetch_all()}
    assert key in stored
    assert stored[key].price == Decimal("750000.00")

    with psycopg.connect(_DSN or "") as conn:
        conn.execute("DELETE FROM listings WHERE listing_id = %s", (key,))
