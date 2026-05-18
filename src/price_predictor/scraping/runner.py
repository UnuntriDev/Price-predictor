"""Programmatic crawl runner (skeleton)."""

from __future__ import annotations

from price_predictor.config.settings import ScrapingSettings


class ScrapyRunner:
    """Runs :class:`OtodomSpider` from Python (CrawlerProcess).

    Args:
        settings: Polite-crawl parameters injected from app settings.
    """

    def __init__(self, settings: ScrapingSettings) -> None:
        self._settings = settings

    def run(self) -> int:
        """See :meth:`ScrapeRunner.run`."""
        raise NotImplementedError("Phase 2: configure CrawlerProcess with Playwright + run spider")
