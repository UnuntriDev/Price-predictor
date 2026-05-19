"""Kaggle loader normalisation + downloader credential handling."""

from __future__ import annotations

from pathlib import Path

import polars as pl
import pytest

from price_predictor.data import PanderaListingValidator, load_listings
from price_predictor.data.kaggle import KaggleDatasetDownloader, credentials_available
from price_predictor.data.schemas import RawListingSchema
from price_predictor.domain import DataDownloadError, DataError

_FIXTURES = Path(__file__).parent.parent.parent / "data" / "kaggle" / "fixtures"


def test_loader_merges_sales_and_ignores_rent() -> None:
    frame = load_listings(_FIXTURES).collect()
    assert frame.height == 100  # 60 + 40, rent file excluded
    assert list(frame.columns) == list(RawListingSchema.to_schema().columns)
    assert set(frame["snapshot_month"].unique()) == {"2023-08", "2024-06"}
    assert frame["has_parking"].dtype == pl.Boolean
    assert "RENT-should-be-ignored" not in frame["id"].to_list()


def test_loader_output_satisfies_schema() -> None:
    frame = load_listings(_FIXTURES).collect()
    validated = PanderaListingValidator().validate(frame)
    assert validated.height == 100


def test_loader_raises_without_sale_files(tmp_path: Path) -> None:
    with pytest.raises(DataError, match="no apartments_pl"):
        load_listings(tmp_path).collect()


def test_credentials_absent(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.delenv("KAGGLE_USERNAME", raising=False)
    monkeypatch.delenv("KAGGLE_KEY", raising=False)
    monkeypatch.setattr(Path, "home", lambda: tmp_path)
    assert credentials_available() is False
    with pytest.raises(DataDownloadError, match="credentials not found"):
        KaggleDatasetDownloader().download(tmp_path / "raw")


def test_credentials_from_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("KAGGLE_USERNAME", "u")
    monkeypatch.setenv("KAGGLE_KEY", "k")
    assert credentials_available() is True
