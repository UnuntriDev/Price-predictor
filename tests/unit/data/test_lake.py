"""DuckDBDataFrameStore round-trips frames and guards inputs."""

from __future__ import annotations

from pathlib import Path

import polars as pl
import pytest
from polars.testing import assert_frame_equal

from price_predictor.data import DuckDBDataFrameStore
from price_predictor.domain import StorageError


def _frame() -> pl.DataFrame:
    return pl.DataFrame({"listing_id": ["a", "b"], "price": [1.0, 2.0]})


def test_write_then_read_roundtrip(tmp_path: Path) -> None:
    store = DuckDBDataFrameStore(tmp_path / "lake.duckdb")
    store.write("listings", _frame())
    assert_frame_equal(store.read("listings"), _frame())


def test_write_replaces_existing(tmp_path: Path) -> None:
    store = DuckDBDataFrameStore(tmp_path / "lake.duckdb")
    store.write("listings", _frame())
    store.write("listings", _frame().head(1))
    assert store.read("listings").height == 1


def test_persists_across_instances(tmp_path: Path) -> None:
    path = tmp_path / "lake.duckdb"
    DuckDBDataFrameStore(path).write("listings", _frame())
    assert DuckDBDataFrameStore(path).read("listings").height == 2


def test_missing_table_raises_storage_error(tmp_path: Path) -> None:
    store = DuckDBDataFrameStore(tmp_path / "lake.duckdb")
    store.write("listings", _frame())
    with pytest.raises(StorageError, match="could not read"):
        store.read("absent")


@pytest.mark.parametrize("bad", ["bad name", "drop;table", "1col", ""])
def test_invalid_identifier_rejected(tmp_path: Path, bad: str) -> None:
    store = DuckDBDataFrameStore(tmp_path / "lake.duckdb")
    with pytest.raises(StorageError, match="invalid table name"):
        store.write(bad, _frame())
