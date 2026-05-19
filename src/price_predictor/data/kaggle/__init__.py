"""Kaggle data source: downloader + normalising loader (ADR 0014)."""

from __future__ import annotations

from price_predictor.data.kaggle.downloader import (
    DATASET_SLUG,
    KaggleDatasetDownloader,
    credentials_available,
)
from price_predictor.data.kaggle.loader import load_listings

__all__ = [
    "DATASET_SLUG",
    "KaggleDatasetDownloader",
    "credentials_available",
    "load_listings",
]
