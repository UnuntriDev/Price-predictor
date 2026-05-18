"""Drift detector satisfies its port; metric objects are declared."""

from __future__ import annotations

import polars as pl
import pytest

from price_predictor.monitoring import DriftDetector, EvidentlyDriftDetector
from price_predictor.monitoring.metrics import PREDICTION_REQUESTS


def test_detector_satisfies_port() -> None:
    detector = EvidentlyDriftDetector(p_value_threshold=0.05)
    assert isinstance(detector, DriftDetector)


def test_detect_is_phase2_stub() -> None:
    detector = EvidentlyDriftDetector(p_value_threshold=0.05)
    with pytest.raises(NotImplementedError, match="Phase 2"):
        detector.detect(pl.DataFrame(), pl.DataFrame())


def test_prometheus_metric_is_registered() -> None:
    # Counter exposes a labelled child without raising.
    PREDICTION_REQUESTS.labels(outcome="ok")
