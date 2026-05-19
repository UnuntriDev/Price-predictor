"""Scraping is an inactive illustrative skeleton (ADR 0013/0014)."""

from __future__ import annotations

import pytest

from price_predictor.config.settings import ScrapingSettings
from price_predictor.scraping import (
    ListingValidationPipeline,
    OtodomSpider,
    ScrapeRunner,
    ScrapyRunner,
)


def test_spider_identity() -> None:
    assert OtodomSpider.name == "otodom"
    assert "otodom.pl" in OtodomSpider.allowed_domains


def test_runner_satisfies_port_but_is_disabled() -> None:
    runner = ScrapyRunner(ScrapingSettings())
    assert isinstance(runner, ScrapeRunner)
    with pytest.raises(NotImplementedError, match="scraping disabled"):
        runner.run()


def test_pipeline_is_disabled() -> None:
    with pytest.raises(NotImplementedError, match="scraping disabled"):
        ListingValidationPipeline().process_item({"x": 1}, spider=None)
