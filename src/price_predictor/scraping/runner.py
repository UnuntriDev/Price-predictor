"""Programmatic crawl runner.

Wires :class:`OtodomSpider` + :class:`ListingValidationPipeline` into a
Scrapy ``CrawlerProcess`` configured for polite crawling and Playwright
rendering. Running a real crawl needs ``scrapy-playwright`` and a
browser (``playwright install chromium``) - Phase 2 infra, not unit
tested. The seed-URL pattern is assumed (see ADR 0013).
"""

from __future__ import annotations

from typing import Any

from price_predictor.config import get_logger
from price_predictor.config.settings import ScrapingSettings

_log = get_logger(__name__)

_PIPELINE = "price_predictor.scraping.pipelines.ListingValidationPipeline"
_PW_HANDLER = "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler"


class ScrapyRunner:
    """Runs :class:`OtodomSpider` from Python.

    Args:
        settings: Polite-crawl parameters injected from app settings.
    """

    def __init__(self, settings: ScrapingSettings) -> None:
        self._settings = settings

    def _seed_urls(self) -> list[str]:
        base = self._settings.base_url.rstrip("/")
        return [
            f"{base}/pl/wyniki/sprzedaz/mieszkanie/cala-polska?page={page}"
            for page in range(1, self._settings.max_pages + 1)
        ]

    def _scrapy_settings(self) -> dict[str, Any]:
        return {
            "USER_AGENT": self._settings.user_agent,
            "DOWNLOAD_DELAY": self._settings.download_delay_seconds,
            "CONCURRENT_REQUESTS": self._settings.concurrent_requests,
            "ROBOTSTXT_OBEY": True,
            "ITEM_PIPELINES": {_PIPELINE: 300},
            "DOWNLOAD_HANDLERS": {
                "http": _PW_HANDLER,
                "https": _PW_HANDLER,
            },
            "TWISTED_REACTOR": ("twisted.internet.asyncioreactor.AsyncioSelectorReactor"),
            "LOG_LEVEL": "INFO",
        }

    def run(self) -> int:
        """See :meth:`ScrapeRunner.run`.

        Returns:
            The number of validated listings scraped.
        """
        from scrapy import signals
        from scrapy.crawler import CrawlerProcess

        from price_predictor.scraping.spider import OtodomSpider

        scraped = 0

        def _count(item: object, response: object, spider: object) -> None:
            nonlocal scraped
            scraped += 1

        process = CrawlerProcess(settings=self._scrapy_settings())
        crawler = process.create_crawler(OtodomSpider)
        crawler.signals.connect(_count, signal=signals.item_scraped)
        process.crawl(crawler, search_urls=tuple(self._seed_urls()))
        process.start()
        _log.info("scrape.done", listings=scraped)
        return scraped
