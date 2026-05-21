"""KS + PSI drift gate (ADR 0012).

KS on numeric columns, PSI on categorical, two-sample reference vs
current. Deterministic — Evidently is kept for HTML reports only.
"""

from __future__ import annotations

from datetime import UTC, datetime

import numpy as np
import polars as pl
from scipy.stats import ks_2samp

from price_predictor.domain import MonitoringError
from price_predictor.monitoring.report import DriftReport

_PSI_EPS = 1e-6


def _psi(reference: pl.Series, current: pl.Series) -> float:
    """Population Stability Index over the union of observed categories."""
    ref_share = reference.value_counts(normalize=True)
    cur_share = current.value_counts(normalize=True)
    col = reference.name
    ref_map = dict(zip(ref_share[col], ref_share["proportion"], strict=True))
    cur_map = dict(zip(cur_share[col], cur_share["proportion"], strict=True))
    psi = 0.0
    for category in set(ref_map) | set(cur_map):
        r = ref_map.get(category, 0.0) + _PSI_EPS
        c = cur_map.get(category, 0.0) + _PSI_EPS
        psi += (c - r) * np.log(c / r)
    return float(psi)


class StatisticalDriftDetector:
    """Per-feature drift, then a dataset-level verdict (PSI 0.2 = moderate)."""

    def __init__(
        self,
        p_value_threshold: float,
        psi_threshold: float = 0.2,
        dataset_drift_share: float = 0.5,
    ) -> None:
        self._p = p_value_threshold
        self._psi_threshold = psi_threshold
        self._dataset_share = dataset_drift_share

    def detect(self, reference: pl.DataFrame, current: pl.DataFrame) -> DriftReport:
        """See :meth:`DriftDetector.detect`."""
        shared = [c for c in reference.columns if c in current.columns]
        if not shared or reference.height == 0 or current.height == 0:
            msg = "drift detection needs non-empty frames with shared columns"
            raise MonitoringError(msg)

        drifted: list[str] = []
        for col in shared:
            if reference[col].dtype.is_numeric():
                stat = ks_2samp(
                    reference[col].drop_nulls().to_numpy(),
                    current[col].drop_nulls().to_numpy(),
                )
                if float(stat.pvalue) < self._p:
                    drifted.append(col)
            elif _psi(reference[col], current[col]) > self._psi_threshold:
                drifted.append(col)

        share = len(drifted) / len(shared)
        return DriftReport(
            dataset_drift=share >= self._dataset_share,
            drifted_features=tuple(drifted),
            share_drifted=share,
            generated_at=datetime.now(UTC),
        )
