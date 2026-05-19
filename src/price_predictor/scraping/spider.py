"""Otodom Scrapy spider.

Responsibility split: the spider only navigates and lifts the
``__NEXT_DATA__`` JSON out of Playwright-rendered pages. Mapping and
validation happen in :class:`ListingValidationPipeline` so both halves
are independently testable. Playwright is enabled via the download
handler configured by :class:`ScrapyRunner` (Phase 2 infra).
"""

from __future__ import annotations

from collections.abc import Iterator
from datetime import UTC, datetime
from typing import Any

import scrapy

from price_predictor.scraping.parser import extract_next_data

_PLAYWRIGHT_META = {"playwright": True}


class OtodomSpider(scrapy.Spider):
    """Crawls Otodom search result and offer pages."""

    name = "otodom"
    allowed_domains = ("otodom.pl",)
    #: Seed search URLs; set by the runner from settings.
    search_urls: tuple[str, ...] = ()

    def start_requests(self) -> Iterator[Any]:
        """Yield the seed search requests (Playwright-rendered)."""
        if not self.search_urls:
            self.logger.warning("OtodomSpider.search_urls is empty")
        for url in self.search_urls:
            yield scrapy.Request(url, callback=self.parse, meta=_PLAYWRIGHT_META)

    def parse(self, response: Any, **_kwargs: Any) -> Iterator[Any]:
        """Follow offer links, then paginate."""
        for href in response.css("a[data-cy=listing-item-link]::attr(href)").getall():
            yield response.follow(href, callback=self.parse_offer, meta=_PLAYWRIGHT_META)
        next_page = response.css("a[data-cy=pagination.next-page]::attr(href)").get()
        if next_page:
            yield response.follow(next_page, callback=self.parse, meta=_PLAYWRIGHT_META)

    def parse_offer(self, response: Any) -> Iterator[Any]:
        """Lift the offer's ``__NEXT_DATA__`` for the pipeline to map."""
        payload = extract_next_data(response.text)
        yield {
            "__next_data__": payload,
            "scraped_at": datetime.now(UTC).isoformat(),
        }
