"""Otodom Scrapy spider (skeleton).

Parsing selectors are deliberately absent: Otodom's markup changes and
hard-coding stale selectors now would be misleading. Phase 2 implements
``parse``/``parse_listing`` with Playwright-rendered pages.
"""

from __future__ import annotations

from collections.abc import Iterator
from typing import Any

import scrapy


class OtodomSpider(scrapy.Spider):
    """Crawls Otodom search result and offer pages."""

    name = "otodom"
    allowed_domains = ("otodom.pl",)

    def start_requests(self) -> Iterator[Any]:
        """Yield the seed search requests."""
        raise NotImplementedError("Phase 2: build seeded search requests from ScrapingSettings")

    def parse(self, response: Any, **kwargs: Any) -> Iterator[Any]:
        """Follow result pages and dispatch to :meth:`parse_listing`."""
        raise NotImplementedError("Phase 2: paginate search results")

    def parse_listing(self, response: Any) -> Iterator[Any]:
        """Extract one offer into a scrapy item / domain Listing."""
        raise NotImplementedError("Phase 2: extract the eight modelled fields")
