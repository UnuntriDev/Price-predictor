"""Scrapy item pipeline (illustrative skeleton).

Inactive — see :mod:`price_predictor.scraping.spider`. Kept to show the
validate-at-the-boundary pattern; not coupled to the data model.
"""

from __future__ import annotations

from typing import Any

_DISABLED = (
    "scraping disabled: Otodom DataDome anti-bot (ADR 0013/0014); "
    "use the Kaggle dataset via `make data`"
)


class ListingValidationPipeline:
    """Skeleton item pipeline; not wired into any data pipeline."""

    def process_item(self, item: Any, spider: Any) -> dict[str, Any]:
        """Inactive: see module docstring."""
        raise NotImplementedError(_DISABLED)
