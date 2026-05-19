"""StatisticalDriftDetector: KS + PSI behaviour and guards."""

from __future__ import annotations

import numpy as np
import polars as pl
import pytest

from price_predictor.domain import MonitoringError
from price_predictor.monitoring import DriftDetector, StatisticalDriftDetector
from price_predictor.monitoring.metrics import PREDICTION_REQUESTS


def _frame(area: np.ndarray, city: list[str]) -> pl.DataFrame:
    return pl.DataFrame({"area": area, "city": city})


def test_detector_satisfies_port() -> None:
    assert isinstance(StatisticalDriftDetector(p_value_threshold=0.05), DriftDetector)


def test_no_drift_on_same_distribution() -> None:
    rng = np.random.default_rng(0)
    ref = _frame(rng.normal(50, 5, 500), ["A"] * 250 + ["B"] * 250)
    cur = _frame(rng.normal(50, 5, 500), ["A"] * 250 + ["B"] * 250)
    rep = StatisticalDriftDetector(p_value_threshold=0.05).detect(ref, cur)
    assert rep.dataset_drift is False
    assert rep.drifted_features == ()
    assert rep.share_drifted == 0.0


def test_numeric_and_categorical_drift_detected() -> None:
    rng = np.random.default_rng(1)
    ref = _frame(rng.normal(50, 5, 500), ["A"] * 400 + ["B"] * 100)
    cur = _frame(rng.normal(80, 5, 500), ["B"] * 400 + ["C"] * 100)
    rep = StatisticalDriftDetector(p_value_threshold=0.05).detect(ref, cur)
    assert set(rep.drifted_features) == {"area", "city"}
    assert rep.share_drifted == 1.0
    assert rep.dataset_drift is True


def test_empty_or_disjoint_frames_raise() -> None:
    det = StatisticalDriftDetector(p_value_threshold=0.05)
    with pytest.raises(MonitoringError):
        det.detect(pl.DataFrame({"a": [1.0]}), pl.DataFrame({"b": [1.0]}))


def test_prometheus_metric_is_registered() -> None:
    PREDICTION_REQUESTS.labels(outcome="ok")
