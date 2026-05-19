"""Drift job: gate (KS+PSI) + human Evidently HTML report.

Packaged (not a loose script) so it is importable in the container and
locally. The Kaggle data is a monthly panel, so reference = all earlier
snapshots and current = the latest ``snapshot_month`` (falling back to a
50/50 split when only one snapshot is present).
"""

from __future__ import annotations

import sys
from pathlib import Path

import polars as pl

from price_predictor.config import configure_logging, get_logger, get_settings
from price_predictor.data import load_listings
from price_predictor.domain import PricePredictorError
from price_predictor.monitoring.drift import StatisticalDriftDetector
from price_predictor.monitoring.evidently_report import EvidentlyReportGenerator

_log = get_logger(__name__)


def _split(frame: pl.DataFrame) -> tuple[pl.DataFrame, pl.DataFrame]:
    months = sorted(frame["snapshot_month"].unique().to_list())
    if len(months) > 1:
        latest = months[-1]
        return (
            frame.filter(pl.col("snapshot_month") != latest),
            frame.filter(pl.col("snapshot_month") == latest),
        )
    mid = frame.height // 2
    return frame[:mid], frame[mid:]


def main() -> int:
    """Run the drift gate and write the Evidently HTML report."""
    settings = get_settings()
    configure_logging(settings.logging)
    raw_dir = Path(settings.data_dir) / "raw"

    try:
        frame = load_listings(raw_dir).collect()
        if frame.height < 2:
            sys.stdout.write(f"[drift] need >=2 listings under {raw_dir}; run `make data`\n")
            return 2
        reference, current = _split(frame)

        report = StatisticalDriftDetector(
            p_value_threshold=settings.monitoring.drift_p_value_threshold
        ).detect(reference, current)

        out = Path(settings.artifacts_dir) / "drift_report.html"
        EvidentlyReportGenerator().generate(reference, current, out)
    except PricePredictorError as exc:
        sys.stdout.write(f"[drift] failed: {exc}\n")
        return 2

    sys.stdout.write(
        f"[drift] dataset_drift={report.dataset_drift} "
        f"share={report.share_drifted:.2f} "
        f"features={list(report.drifted_features)} -> {out}\n"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
