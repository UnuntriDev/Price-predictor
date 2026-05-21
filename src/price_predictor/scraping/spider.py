"""Otodom spider — inert skeleton.

DataDome blocks the site (ADR 0013 → 0014); we use Kaggle data instead.
Kept only to show the shape. Every method raises.
"""

from __future__ import annotations

from collections.abc import Iterator
from typing import Any

import scrapy

_DISABLED = (
    "scraping disabled: Otodom DataDome anti-bot (ADR 0013/0014); "
    "use the Kaggle dataset via `make data`"
)


class OtodomSpider(scrapy.Spider):
    """Skeleton spider; not wired into any data pipeline."""

    name = "otodom"
    allowed_domains = ("otodom.pl",)

    def start_requests(self) -> Iterator[Any]:
        """Inactive: see module docstring."""
        raise NotImplementedError(_DISABLED)

    def parse(self, response: Any, **_kwargs: Any) -> Iterator[Any]:
        """Inactive: see module docstring."""
        raise NotImplementedError(_DISABLED)
