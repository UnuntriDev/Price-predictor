"""Otodom Scrapy spider (illustrative skeleton).

Inactive: Otodom is behind DataDome anti-bot and returns a JS shell
page with no ``__NEXT_DATA__`` (ADR 0013, superseded by ADR 0014). The
project's data source is the Kaggle dataset (``make data``). This class
is retained only to show the scraping architectural pattern; every
method raises to make the inactive status unmistakable.
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
