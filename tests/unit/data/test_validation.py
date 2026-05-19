"""PanderaListingValidator enforces the RawListingSchema contract."""

from __future__ import annotations

from collections.abc import Callable
from pathlib import Path

import polars as pl
import pytest

from price_predictor.data import PanderaListingValidator, load_listings
from price_predictor.domain import SchemaValidationError

_FIXTURES = Path(__file__).parent.parent / "data" / "kaggle" / "fixtures"


def _valid_frame() -> pl.DataFrame:
    return load_listings(_FIXTURES).collect()


def test_valid_frame_passes_through() -> None:
    out = PanderaListingValidator().validate(_valid_frame())
    assert out.height == 100
    assert set(out.columns) == set(_valid_frame().columns)


@pytest.mark.parametrize(
    "mutate",
    [
        pytest.param(lambda f: f.with_columns(price_pln=pl.lit(0)), id="price-too-low"),
        pytest.param(
            lambda f: f.with_columns(square_meters=pl.lit(5.0)),
            id="square-meters-low",
        ),
        pytest.param(lambda f: f.drop("rooms"), id="missing-column"),
        pytest.param(lambda f: f.with_columns(extra=pl.lit(1)), id="extra-column-strict"),
        pytest.param(lambda f: f.with_columns(city=pl.lit("berlin")), id="bad-city-enum"),
        pytest.param(
            lambda f: f.with_columns(latitude=pl.lit(70.0)),
            id="latitude-out-of-poland",
        ),
    ],
)
def test_contract_violations_raise_domain_error(
    mutate: Callable[[pl.DataFrame], pl.DataFrame],
) -> None:
    with pytest.raises(SchemaValidationError):
        PanderaListingValidator().validate(mutate(_valid_frame()))
