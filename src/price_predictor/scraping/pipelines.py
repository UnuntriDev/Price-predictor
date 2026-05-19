"""Scrapy item pipelines.

Two stages, run in order:

1. :class:`ListingValidationPipeline` maps the raw ``__NEXT_DATA__``
   payload to a validated domain ``Listing`` (as a JSON dict) so
   malformed offers never reach storage.
2. :class:`PostgresPersistPipeline` buffers those validated rows and
   bulk-upserts them through the injected repository.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any

from price_predictor.data.ports import ListingRepository
from price_predictor.data.repository import PostgresListingRepository
from price_predictor.domain import Listing, ScrapeError
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


class PostgresPersistPipeline:
    """Batched upsert of validated listings into Postgres.

    Args:
        repository: Destination store (injected; a fake is used in tests).
        batch_size: Rows buffered before a flush.
    """

    def __init__(self, repository: ListingRepository, batch_size: int = 100) -> None:
        self._repository = repository
        self._batch_size = batch_size
        self._buffer: list[Listing] = []
        self.written = 0

    @classmethod
    def from_crawler(cls, crawler: Any) -> PostgresPersistPipeline:
        """Build from Scrapy settings (the runner sets ``PP_POSTGRES_DSN``)."""
        dsn = crawler.settings.get("PP_POSTGRES_DSN")
        if not dsn:
            msg = "PP_POSTGRES_DSN is not configured for the crawl"
            raise ScrapeError(msg)
        return cls(PostgresListingRepository.from_dsn(str(dsn)))

    def _flush(self) -> None:
        if self._buffer:
            self.written += self._repository.upsert_many(self._buffer)
            self._buffer.clear()

    def process_item(self, item: dict[str, Any], spider: Any) -> dict[str, Any]:
        """Buffer a validated row, flushing on a full batch.

        Args:
            item: The dict emitted by :class:`ListingValidationPipeline`.
            spider: The originating spider (unused; Scrapy contract).

        Returns:
            The item, unchanged, for any downstream consumer.

        Raises:
            ScrapeError: If the row cannot be revalidated as a Listing.
        """
        try:
            listing = Listing.model_validate(item)
        except ValueError as exc:
            msg = f"row is not a valid Listing: {exc}"
            raise ScrapeError(msg) from exc
        self._buffer.append(listing)
        if len(self._buffer) >= self._batch_size:
            self._flush()
        return item

    def close_spider(self, spider: Any) -> None:
        """Flush any buffered rows when the crawl ends."""
        self._flush()
