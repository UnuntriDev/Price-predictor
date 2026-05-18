"""DuckDB-backed :class:`DataFrameStore` (skeleton)."""

from __future__ import annotations

from pathlib import Path

import polars as pl


class DuckDBDataFrameStore:
    """Reads/writes analytics frames in a local DuckDB file.

    Args:
        database_path: Path to the DuckDB file (created on first write).
    """

    def __init__(self, database_path: Path) -> None:
        self._database_path = database_path

    def write(self, name: str, frame: pl.DataFrame) -> None:
        """See :meth:`DataFrameStore.write`."""
        raise NotImplementedError("Phase 2: register Polars frame as a DuckDB table")

    def read(self, name: str) -> pl.DataFrame:
        """See :meth:`DataFrameStore.read`."""
        raise NotImplementedError("Phase 2: query DuckDB table back into Polars")
