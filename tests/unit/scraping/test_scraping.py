"""Spider/runner are declared but parsing is deferred to Phase 2."""

from __future__ import annotations

import pytest

from price_predictor.config.settings import ScrapingSettings
from price_predictor.scraping import OtodomSpider, ScrapeRunner, ScrapyRunner


def test_spider_identity() -> None:
    assert OtodomSpider.name == "otodom"
    assert "otodom.pl" in OtodomSpider.allowed_domains


def test_runner_satisfies_port_and_is_stub() -> None:
    runner = ScrapyRunner(ScrapingSettings())
    assert isinstance(runner, ScrapeRunner)
    with pytest.raises(NotImplementedError, match="Phase 2"):
        runner.run()
