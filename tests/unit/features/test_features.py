"""Feature pipeline conforms to the transformer port and is a stub."""

from __future__ import annotations

import polars as pl
import pytest

from price_predictor.features import FeatureTransformer, PriceFeaturePipeline


def test_pipeline_satisfies_port() -> None:
    pipeline = PriceFeaturePipeline(categorical=["city"], numeric=["area"])
    assert isinstance(pipeline, FeatureTransformer)


def test_fit_is_phase2_stub() -> None:
    pipeline = PriceFeaturePipeline(categorical=[], numeric=[])
    with pytest.raises(NotImplementedError, match="Phase 2"):
        pipeline.fit(pl.DataFrame())
