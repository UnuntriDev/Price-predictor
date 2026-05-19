"""ConformalModel pipes raw request columns through to the estimator."""

from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd
import polars as pl

from price_predictor.pipeline import ConformalModel
from price_predictor.pipeline.artifact import REQUEST_COLUMNS


class _FeatureStub:
    def transform(self, frame: pl.DataFrame) -> pl.DataFrame:
        # Proves the raw -> polars -> features hop happened.
        return pl.DataFrame({"n": [float(frame.height)] * frame.height})


class _EstimatorStub:
    def predict(self, frame: Any) -> np.ndarray[Any, Any]:
        return np.arange(len(frame), dtype=np.float64)


def _raw(rows: int) -> pd.DataFrame:
    return pd.DataFrame(
        {
            "area": [50.0] * rows,
            "rooms": [3] * rows,
            "city": ["Warszawa"] * rows,
            "district": ["Wola"] * rows,
            "year_built": [2010] * rows,
            "floor": [2] * rows,
            "property_type": ["apartment"] * rows,
            "extra": ["ignored"] * rows,
        }
    )


def test_predict_and_attribute() -> None:
    model = ConformalModel(_FeatureStub(), _EstimatorStub(), conformal_q=12_345.0)
    out = model.predict(_raw(4))
    assert list(out) == [0.0, 1.0, 2.0, 3.0]
    assert model.conformal_q == 12_345.0


def test_only_request_columns_are_used() -> None:
    model = ConformalModel(_FeatureStub(), _EstimatorStub(), conformal_q=1.0)
    # 'extra' present in raw must not break the request-column selection.
    assert len(model.predict(_raw(2))) == 2
    assert set(REQUEST_COLUMNS).isdisjoint({"extra"})
