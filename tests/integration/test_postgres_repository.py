"""Postgres repository round-trip (Kaggle schema).

Skipped unless ``PP_TEST_PG_DSN`` points at a disposable database
(e.g. the docker-compose ``postgres`` service). No network/docker is
assumed by default, so local + current CI stay green.
"""

from __future__ import annotations

import os
from datetime import date

import psycopg
import pytest
from psycopg.conninfo import conninfo_to_dict
from pydantic import SecretStr

from price_predictor.config.settings import PostgresSettings
from price_predictor.data import PostgresListingRepository
from price_predictor.domain import CityEnum, Listing, OwnershipType, PropertyType

_DSN = os.environ.get("PP_TEST_PG_DSN")

pytestmark = [
    pytest.mark.integration,
    pytest.mark.skipif(_DSN is None, reason="set PP_TEST_PG_DSN to run"),
]


def _settings() -> PostgresSettings:
    info = conninfo_to_dict(_DSN or "")
    return PostgresSettings(
        host=str(info.get("host", "localhost")),
        port=int(str(info.get("port", 5432))),
        user=str(info.get("user", "price_predictor")),
        password=SecretStr(str(info.get("password", ""))),
        database=str(info.get("dbname", "price_predictor")),
    )


def _listing(listing_id: str) -> Listing:
    return Listing(
        id=listing_id,
        city=CityEnum.WARSZAWA,
        property_type=PropertyType.BLOCK_OF_FLATS,
        square_meters=52.0,
        rooms=3,
        floor=4,
        floor_count=10,
        build_year=2015,
        latitude=52.23,
        longitude=21.01,
        centre_distance_km=3.5,
        poi_count=12,
        ownership=OwnershipType.CONDOMINIUM,
        has_parking=True,
        has_balcony=True,
        has_elevator=True,
        has_security=False,
        has_storage=True,
        price_pln=750_000,
        snapshot_month=date(2024, 6, 1),
    )


def test_create_upsert_fetch_is_idempotent() -> None:
    repo = PostgresListingRepository(_settings())
    repo.create_schema()
    key = "IT-PG-1"

    assert repo.upsert_many([_listing(key)]) == 1
    assert repo.upsert_many([_listing(key)]) == 1  # idempotent

    stored = {row.id: row for row in repo.fetch_all()}
    assert key in stored
    assert stored[key].price_pln == 750_000

    with psycopg.connect(_DSN or "") as conn:
        conn.execute("DELETE FROM listings WHERE id = %s", (key,))
        conn.commit()
