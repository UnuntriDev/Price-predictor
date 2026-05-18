"""Monitoring ports."""

from __future__ import annotations

from typing import Protocol, runtime_checkable

import polars as pl

from price_predictor.monitoring.report import DriftReport


@runtime_checkable
class DriftDetector(Protocol):
    """Compares a current feature window against a reference window."""

    def detect(self, reference: pl.DataFrame, current: pl.DataFrame) -> DriftReport:
        """Return a populated :class:`DriftReport`."""
        ...
