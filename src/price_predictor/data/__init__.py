"""Data acquisition and preparation layer (ports + skeleton adapters)."""

from __future__ import annotations

from price_predictor.data.lake import DuckDBDataFrameStore
from price_predictor.data.ports import (
    DataFrameStore,
    ListingRepository,
    SchemaContract,
)
from price_predictor.data.repository import PostgresListingRepository
from price_predictor.data.schemas import ListingFrame
from price_predictor.data.validation import PanderaListingValidator

__all__ = [
    "DataFrameStore",
    "DuckDBDataFrameStore",
    "ListingFrame",
    "ListingRepository",
    "PanderaListingValidator",
    "PostgresListingRepository",
    "SchemaContract",
]
