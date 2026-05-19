"""__NEXT_DATA__ extraction and the assumed-contract mapping (ADR 0013)."""

from __future__ import annotations

import copy
import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import pytest

from price_predictor.domain import Listing, PropertyType, ScrapeError
from price_predictor.scraping import extract_next_data, parse_listing

_SCRAPED_AT = datetime(2026, 5, 19, tzinfo=UTC)
_FIXTURE = Path(__file__).parent / "fixtures" / "next_data_sample.json"


def _payload() -> dict[str, Any]:
    return json.loads(_FIXTURE.read_text(encoding="utf-8"))


def test_parse_listing_maps_assumed_contract() -> None:
    listing = parse_listing(_payload(), _SCRAPED_AT)
    assert isinstance(listing, Listing)
    assert listing.listing_id == "123456"
    assert listing.city == "Warszawa"
    assert listing.district == "Mokotów"
    assert listing.rooms == 3
    assert listing.property_type is PropertyType.APARTMENT
    assert str(listing.price) == "750000"


def test_missing_path_raises_scrape_error() -> None:
    payload = _payload()
    del payload["props"]["pageProps"]["ad"]["characteristics"]
    with pytest.raises(ScrapeError, match="missing expected path"):
        parse_listing(payload, _SCRAPED_AT)


def test_out_of_bounds_value_raises_scrape_error() -> None:
    payload = copy.deepcopy(_payload())
    payload["props"]["pageProps"]["ad"]["characteristics"]["price"] = 100
    with pytest.raises(ScrapeError, match="failed domain validation"):
        parse_listing(payload, _SCRAPED_AT)


def test_unmapped_category_raises_scrape_error() -> None:
    payload = copy.deepcopy(_payload())
    payload["props"]["pageProps"]["ad"]["category"]["name"] = "Garaż"
    with pytest.raises(ScrapeError, match="unmapped Otodom category"):
        parse_listing(payload, _SCRAPED_AT)


def test_extract_next_data_roundtrip() -> None:
    html = (
        '<html><body><script id="__NEXT_DATA__" type="application/json">'
        '{"a": 1}</script></body></html>'
    )
    assert extract_next_data(html) == {"a": 1}


@pytest.mark.parametrize(
    ("html", "match"),
    [
        ("<html><body>no script</body></html>", "no <script"),
        (
            '<script id="__NEXT_DATA__">not json</script>',
            "not valid JSON",
        ),
    ],
)
def test_extract_next_data_failures(html: str, match: str) -> None:
    with pytest.raises(ScrapeError, match=match):
        extract_next_data(html)
