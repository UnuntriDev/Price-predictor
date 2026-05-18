"""The exception hierarchy must let callers catch broadly or narrowly."""

from __future__ import annotations

import pytest

from price_predictor.domain import (
    DataError,
    ModelNotFoundError,
    PricePredictorError,
    RegistryError,
    ScrapeError,
)


@pytest.mark.parametrize(
    ("specific", "broader"),
    [
        (ScrapeError, DataError),
        (DataError, PricePredictorError),
        (ModelNotFoundError, RegistryError),
        (RegistryError, PricePredictorError),
    ],
)
def test_subclass_relationships(specific: type[Exception], broader: type[Exception]) -> None:
    assert issubclass(specific, broader)


def test_every_error_is_catchable_as_base() -> None:
    with pytest.raises(PricePredictorError):
        raise ModelNotFoundError("no production model for 'price-xgb'")
