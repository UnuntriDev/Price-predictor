"""Data layer: adapters satisfy their ports and stay unimplemented."""

from __future__ import annotations

from pathlib import Path

import pytest

from price_predictor.config.settings import PostgresSettings
from price_predictor.data import (
    DataFrameStore,
    DuckDBDataFrameStore,
    ListingFrame,
    ListingRepository,
    PanderaListingValidator,
    PostgresListingRepository,
    SchemaContract,
)


def test_adapters_satisfy_ports() -> None:
    repo = PostgresListingRepository(PostgresSettings())
    store = DuckDBDataFrameStore(Path("x.duckdb"))
    validator = PanderaListingValidator()
    assert isinstance(repo, ListingRepository)
    assert isinstance(store, DataFrameStore)
    assert isinstance(validator, SchemaContract)


def test_schema_declares_modelled_columns() -> None:
    columns = set(ListingFrame.to_schema().columns)
    assert {"price", "area", "rooms", "city", "property_type"} <= columns


def test_repository_methods_are_phase2_stubs() -> None:
    repo = PostgresListingRepository(PostgresSettings())
    with pytest.raises(NotImplementedError, match="Phase 2"):
        repo.fetch_all()
