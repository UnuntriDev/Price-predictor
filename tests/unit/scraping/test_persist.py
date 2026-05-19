"""PostgresPersistPipeline batches and flushes via the injected repo."""

from __future__ import annotations

import json
from collections.abc import Iterable
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import pytest

from price_predictor.config.settings import PostgresSettings, ScrapingSettings
from price_predictor.data import PostgresListingRepository
from price_predictor.domain import Listing, ScrapeError
from price_predictor.scraping import ScrapyRunner
from price_predictor.scraping.parser import parse_listing
from price_predictor.scraping.pipelines import PostgresPersistPipeline

_FIXTURE = Path(__file__).parent / "fixtures" / "next_data_sample.json"


class _FakeRepo:
    def __init__(self) -> None:
        self.batches: list[int] = []

    def upsert_many(self, listings: Iterable[Listing]) -> int:
        rows = list(listings)
        self.batches.append(len(rows))
        return len(rows)

    def fetch_all(self) -> list[Listing]:
        return []


def _item(listing_id: str) -> dict[str, Any]:
    payload = json.loads(_FIXTURE.read_text(encoding="utf-8"))
    payload["props"]["pageProps"]["ad"]["id"] = listing_id
    return parse_listing(payload, datetime(2026, 5, 19, tzinfo=UTC)).model_dump(mode="json")


def test_batches_and_flushes_remainder() -> None:
    repo = _FakeRepo()
    pipe = PostgresPersistPipeline(repo, batch_size=2)
    for i in range(5):
        pipe.process_item(_item(f"OT-{i}"), spider=None)
    assert repo.batches == [2, 2]  # two full batches flushed
    pipe.close_spider(spider=None)
    assert repo.batches == [2, 2, 1]  # remainder on close
    assert pipe.written == 5


def test_invalid_row_raises_scrape_error() -> None:
    pipe = PostgresPersistPipeline(_FakeRepo())
    with pytest.raises(ScrapeError, match="not a valid Listing"):
        pipe.process_item({"listing_id": "x"}, spider=None)


def test_repository_from_dsn_parses_components() -> None:
    repo = PostgresListingRepository.from_dsn("postgresql://u:p@db.example:6543/mydb")
    assert isinstance(repo, PostgresListingRepository)


def test_runner_registers_persist_pipeline_when_postgres_given() -> None:
    runner = ScrapyRunner(ScrapingSettings(), postgres=PostgresSettings())
    cfg = runner._scrapy_settings()
    pipelines = cfg["ITEM_PIPELINES"]
    assert any("PostgresPersistPipeline" in key for key in pipelines)
    assert "PP_POSTGRES_DSN" in cfg

    no_pg = ScrapyRunner(ScrapingSettings())._scrapy_settings()
    assert not any("PostgresPersistPipeline" in key for key in no_pg["ITEM_PIPELINES"])
