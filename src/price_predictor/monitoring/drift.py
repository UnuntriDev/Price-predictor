"""Evidently-backed drift detector (skeleton)."""

from __future__ import annotations

import polars as pl

from price_predictor.monitoring.report import DriftReport


class EvidentlyDriftDetector:
    """Detects data drift with Evidently presets.

    Args:
        p_value_threshold: Significance level below which a feature is
            flagged as drifted.
    """

    def __init__(self, p_value_threshold: float) -> None:
        self._p_value_threshold = p_value_threshold

    def detect(self, reference: pl.DataFrame, current: pl.DataFrame) -> DriftReport:
        """See :meth:`DriftDetector.detect`."""
        raise NotImplementedError("Phase 2: run Evidently DataDriftPreset -> DriftReport")
