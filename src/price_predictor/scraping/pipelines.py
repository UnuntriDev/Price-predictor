"""Scrapy item pipeline.

Maps the spider's raw ``__NEXT_DATA__`` payload to a validated domain
``Listing`` so malformed offers never reach storage.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any

from price_predictor.domain import ScrapeError
from price_predictor.scraping.parser import parse_listing


class ListingValidationPipeline:
    """Coerces scraped items into validated domain ``Listing`` records."""

    def process_item(self, item: Any, spider: Any) -> dict[str, Any]:
        """Validate one scraped item.

        Args:
            item: ``{"__next_data__": <payload>, "scraped_at": <iso>}``.
            spider: The originating spider (unused; Scrapy contract).

        Returns:
            The JSON-serialisable validated listing.

        Raises:
            ScrapeError: If the item is shaped wrong or fails validation.
        """
        try:
            payload = item["__next_data__"]
            scraped_at = datetime.fromisoformat(item["scraped_at"])
        except (KeyError, TypeError, ValueError) as exc:
            msg = f"scraped item missing required keys: {exc}"
            raise ScrapeError(msg) from exc
        return parse_listing(payload, scraped_at).model_dump(mode="json")
