"""Spider identity, runner wiring, and the validation pipeline."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

from price_predictor.config.settings import ScrapingSettings
from price_predictor.domain import ScrapeError
from price_predictor.scraping import (
    ListingValidationPipeline,
    OtodomSpider,
    ScrapeRunner,
    ScrapyRunner,
)

_FIXTURE = Path(__file__).parent / "fixtures" / "next_data_sample.json"


def test_spider_identity() -> None:
    assert OtodomSpider.name == "otodom"
    assert "otodom.pl" in OtodomSpider.allowed_domains


def test_runner_satisfies_port_and_builds_seed_urls() -> None:
    runner = ScrapyRunner(ScrapingSettings(max_pages=3))
    assert isinstance(runner, ScrapeRunner)
    urls = runner._seed_urls()
    assert len(urls) == 3
    assert all(u.startswith("https://www.otodom.pl/") for u in urls)


def test_pipeline_maps_valid_item() -> None:
    payload: dict[str, Any] = json.loads(_FIXTURE.read_text(encoding="utf-8"))
    item = {"__next_data__": payload, "scraped_at": "2026-05-19T00:00:00+00:00"}
    out = ListingValidationPipeline().process_item(item, spider=None)
    assert out["listing_id"] == "123456"
    assert out["city"] == "Warszawa"


def test_pipeline_rejects_malformed_item() -> None:
    with pytest.raises(ScrapeError, match="missing required keys"):
        ListingValidationPipeline().process_item({"oops": 1}, spider=None)
