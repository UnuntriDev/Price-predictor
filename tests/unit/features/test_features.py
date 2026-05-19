"""PriceFeaturePipeline: imputation + feature selection (Kaggle schema)."""

from __future__ import annotations

from pathlib import Path

import polars as pl
import pytest

from price_predictor.data import load_listings
from price_predictor.domain import FeatureError
from price_predictor.features import FEATURE_COLUMNS, FeatureTransformer, PriceFeaturePipeline

_FIXTURES = Path(__file__).parent.parent / "data" / "kaggle" / "fixtures"


def _frame() -> pl.DataFrame:
    return load_listings(_FIXTURES).collect()


def test_satisfies_port() -> None:
    assert isinstance(PriceFeaturePipeline(), FeatureTransformer)


def test_transform_before_fit_raises() -> None:
    with pytest.raises(FeatureError, match="before fit"):
        PriceFeaturePipeline().transform(_frame())


def test_fit_requires_target() -> None:
    with pytest.raises(FeatureError, match="target column"):
        PriceFeaturePipeline().fit(_frame().drop("price_pln"))


def test_transform_emits_features_with_no_nulls() -> None:
    frame = _frame()
    pipe = PriceFeaturePipeline().fit(frame)
    out = pipe.transform(frame)
    assert out.columns == list(FEATURE_COLUMNS)
    assert out.null_count().to_numpy().sum() == 0
    assert "price_pln" not in out.columns


def test_imputes_unseen_nulls_with_learned_median() -> None:
    frame = _frame()
    pipe = PriceFeaturePipeline().fit(frame)
    one = frame.head(1).with_columns(
        floor=pl.lit(None, dtype=pl.Int64),
        condition=pl.lit(None, dtype=pl.Utf8),
        has_elevator=pl.lit(None, dtype=pl.Utf8),
    )
    out = pipe.transform(one)
    assert out["floor"].null_count() == 0
    assert out["condition"].to_list() == ["missing"]
    assert out["has_elevator"].to_list() == [0]
