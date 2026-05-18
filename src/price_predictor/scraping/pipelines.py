"""Scrapy item pipeline (skeleton)."""

from __future__ import annotations

from typing import Any


class ListingValidationPipeline:
    """Coerces scraped items into validated domain ``Listing`` records.

    Sits between the spider and storage so malformed offers never reach
    the database.
    """

    def process_item(self, item: Any, spider: Any) -> Any:
        """Validate one scraped item.

        Raises:
            ScrapeError: If the item cannot be coerced to a Listing.
        """
        raise NotImplementedError("Phase 2: map scrapy item -> domain.Listing with validation")
