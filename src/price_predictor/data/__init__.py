"""Data acquisition and preparation layer."""

from __future__ import annotations

from price_predictor.data.kaggle import KaggleDatasetDownloader, load_listings
from price_predictor.data.lake import DuckDBDataFrameStore
from price_predictor.data.ports import (
    DataFrameStore,
    ListingRepository,
    SchemaContract,
)
from price_predictor.data.repository import PostgresListingRepository
from price_predictor.data.schemas import RawListingSchema
from price_predictor.data.validation import PanderaListingValidator

__all__ = [
    "DataFrameStore",
    "DuckDBDataFrameStore",
    "KaggleDatasetDownloader",
    "ListingRepository",
    "PanderaListingValidator",
    "PostgresListingRepository",
    "RawListingSchema",
    "SchemaContract",
    "load_listings",
]
