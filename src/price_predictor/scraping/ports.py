"""Scraping port."""

from __future__ import annotations

from typing import Protocol, runtime_checkable


@runtime_checkable
class ScrapeRunner(Protocol):
    """Drives a crawl and reports how many listings were captured."""

    def run(self) -> int:
        """Execute the crawl.

        Returns:
            The number of listings scraped and handed to the pipeline.
        """
        ...
