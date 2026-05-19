"""Otodom ``__NEXT_DATA__`` -> :class:`Listing` mapping.

ASSUMED CONTRACT (ADR 0013) - not yet verified against a real capture.
The offer is expected at ``props.pageProps.ad`` with::

    ad.id                              -> listing_id
    ad.url                             -> source_url
    ad.category.name                   -> property_type (mapped)
    ad.location.{city,district}        -> city, district
    ad.characteristics.{price,area,rooms_num,year_built,floor_no}

All access is funnelled through one function so correcting the paths
after a real capture is a single, well-tested edit. Any deviation
raises :class:`ScrapeError` rather than guessing.
"""

from __future__ import annotations

import json
from datetime import datetime
from decimal import Decimal, InvalidOperation
from typing import Any

from parsel import Selector

from price_predictor.domain import (
    DomainValidationError,
    Listing,
    PropertyType,
    ScrapeError,
)


def extract_next_data(html: str) -> dict[str, Any]:
    """Pull and decode the ``__NEXT_DATA__`` script from rendered HTML.

    Args:
        html: Fully rendered offer-page HTML.

    Returns:
        The decoded JSON object.

    Raises:
        ScrapeError: If the script tag is absent or not valid JSON.
    """
    raw = Selector(text=html).css("script#__NEXT_DATA__::text").get()
    if not raw:
        msg = "no <script id=__NEXT_DATA__> in page"
        raise ScrapeError(msg)
    try:
        payload = json.loads(raw)
    except json.JSONDecodeError as exc:
        msg = f"__NEXT_DATA__ is not valid JSON: {exc}"
        raise ScrapeError(msg) from exc
    if not isinstance(payload, dict):
        msg = "__NEXT_DATA__ did not decode to an object"
        raise ScrapeError(msg)
    return payload


_CATEGORY_TO_TYPE: dict[str, PropertyType] = {
    "mieszkanie": PropertyType.APARTMENT,
    "apartment": PropertyType.APARTMENT,
    "dom": PropertyType.HOUSE,
    "house": PropertyType.HOUSE,
    "kawalerka": PropertyType.STUDIO,
    "studio": PropertyType.STUDIO,
    "pokoj": PropertyType.ROOM,
    "room": PropertyType.ROOM,
    "dzialka": PropertyType.PLOT,
    "plot": PropertyType.PLOT,
    "inwestycja": PropertyType.INVESTMENT,
    "investment": PropertyType.INVESTMENT,
}


def _require(node: Any, *path: str) -> Any:
    """Walk ``path`` through nested mappings or raise ScrapeError."""
    cursor = node
    for key in path:
        if not isinstance(cursor, dict) or key not in cursor:
            joined = ".".join(path)
            msg = f"__NEXT_DATA__ missing expected path: {joined}"
            raise ScrapeError(msg)
        cursor = cursor[key]
    return cursor


def parse_listing(payload: dict[str, Any], scraped_at: datetime) -> Listing:
    """Map one rendered offer payload to a validated :class:`Listing`.

    Args:
        payload: The decoded ``__NEXT_DATA__`` object.
        scraped_at: Capture timestamp (injected for reproducibility).

    Returns:
        A validated listing.

    Raises:
        ScrapeError: If the structure deviates from the assumed contract
            or values cannot be coerced/validated.
    """
    ad = _require(payload, "props", "pageProps", "ad")
    chars = _require(ad, "characteristics")
    location = _require(ad, "location")
    category = str(_require(ad, "category", "name")).strip().casefold()

    property_type = _CATEGORY_TO_TYPE.get(category)
    if property_type is None:
        msg = f"unmapped Otodom category: {category!r}"
        raise ScrapeError(msg)

    try:
        listing = Listing(
            listing_id=str(_require(ad, "id")),
            source_url=str(_require(ad, "url")),
            scraped_at=scraped_at,
            price=Decimal(str(_require(chars, "price"))),
            area=float(_require(chars, "area")),
            rooms=int(_require(chars, "rooms_num")),
            city=str(_require(location, "city")),
            district=str(_require(location, "district")),
            year_built=int(_require(chars, "year_built")),
            floor=int(_require(chars, "floor_no")),
            property_type=property_type,
        )
    except (DomainValidationError, ValueError, TypeError, InvalidOperation) as exc:
        msg = f"offer failed domain validation: {exc}"
        raise ScrapeError(msg) from exc
    return listing
