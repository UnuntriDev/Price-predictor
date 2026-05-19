"""Data layer: adapters satisfy their ports and handle errors."""

from __future__ import annotations

from pathlib import Path

import pytest
from pydantic import SecretStr

from price_predictor.config.settings import PostgresSettings
from price_predictor.data import (
    DataFrameStore,
    DuckDBDataFrameStore,
    ListingRepository,
    PanderaListingValidator,
    PostgresListingRepository,
    RawListingSchema,
    SchemaContract,
)
from price_predictor.domain import StorageError


def test_adapters_satisfy_ports() -> None:
    repo = PostgresListingRepository(PostgresSettings())
    store = DuckDBDataFrameStore(Path("x.duckdb"))
    validator = PanderaListingValidator()
    assert isinstance(repo, ListingRepository)
    assert isinstance(store, DataFrameStore)
    assert isinstance(validator, SchemaContract)


def test_schema_declares_modelled_columns() -> None:
    columns = set(RawListingSchema.to_schema().columns)
    assert {"price_pln", "square_meters", "city", "snapshot_month"} <= columns


def test_repository_wraps_connection_errors() -> None:
    # Unreachable port -> psycopg.Error must surface as StorageError.
    repo = PostgresListingRepository(
        PostgresSettings(host="127.0.0.1", port=1, password=SecretStr("x"))
    )
    with pytest.raises(StorageError, match="fetch_all failed"):
        repo.fetch_all()
