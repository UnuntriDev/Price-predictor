"""DuckDB-backed :class:`DataFrameStore`."""

from __future__ import annotations

import re
from pathlib import Path

import duckdb
import polars as pl

from price_predictor.domain import StorageError

_IDENTIFIER = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")


def _safe_identifier(name: str) -> str:
    """Validate a table name (DuckDB has no parameterised identifiers).

    Raises:
        StorageError: If ``name`` is not a plain SQL identifier.
    """
    if not _IDENTIFIER.fullmatch(name):
        msg = f"invalid table name: {name!r}"
        raise StorageError(msg)
    return name


class DuckDBDataFrameStore:
    """Reads/writes analytics frames in a local DuckDB file.

    Args:
        database_path: Path to the DuckDB file (created on first write).
    """

    def __init__(self, database_path: Path) -> None:
        self._database_path = database_path

    def write(self, name: str, frame: pl.DataFrame) -> None:
        """See :meth:`DataFrameStore.write`."""
        table = _safe_identifier(name)
        self._database_path.parent.mkdir(parents=True, exist_ok=True)
        with duckdb.connect(str(self._database_path)) as con:
            con.register("_incoming", frame)
            con.execute(f'CREATE OR REPLACE TABLE "{table}" AS SELECT * FROM _incoming')
            con.unregister("_incoming")

    def read(self, name: str) -> pl.DataFrame:
        """See :meth:`DataFrameStore.read`.

        Raises:
            StorageError: If the table does not exist.
        """
        table = _safe_identifier(name)
        try:
            with duckdb.connect(str(self._database_path), read_only=True) as con:
                result: pl.DataFrame = con.execute(f'SELECT * FROM "{table}"').pl()
        except duckdb.Error as exc:
            msg = f"could not read table {table!r}: {exc}"
            raise StorageError(msg) from exc
        return result
