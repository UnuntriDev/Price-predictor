"""Drift job: gate (KS+PSI) + human Evidently HTML report.

Packaged (not a loose script) so it is importable in the container and
locally. Reference/current are a deterministic 50/50 split of the
current listings table — a documented stand-in until a temporal column
is persisted (the split point is the only thing to change then).
"""

from __future__ import annotations

import sys
from pathlib import Path

import polars as pl

from price_predictor.config import configure_logging, get_logger, get_settings
from price_predictor.data import PostgresListingRepository
from price_predictor.domain import PricePredictorError
from price_predictor.monitoring.drift import StatisticalDriftDetector
from price_predictor.monitoring.evidently_report import EvidentlyReportGenerator

_log = get_logger(__name__)

_FRAME_COLUMNS = (
    "listing_id",
    "price",
    "area",
    "rooms",
    "city",
    "district",
    "year_built",
    "floor",
    "property_type",
)


def _frame(repo: PostgresListingRepository) -> pl.DataFrame:
    rows = [
        {
            "listing_id": x.listing_id,
            "price": float(x.price),
            "area": x.area,
            "rooms": x.rooms,
            "city": x.city,
            "district": x.district,
            "year_built": x.year_built,
            "floor": x.floor,
            "property_type": x.property_type.value,
        }
        for x in repo.fetch_all()
    ]
    return pl.DataFrame(rows, schema=list(_FRAME_COLUMNS))


def main() -> int:
    """Run the drift gate and write the Evidently HTML report."""
    settings = get_settings()
    configure_logging(settings.logging)
    repo = PostgresListingRepository(settings.postgres)

    try:
        frame = _frame(repo)
        if frame.height < 2:
            sys.stdout.write("[drift] need >=2 listings; run scrape first\n")
            return 2
        midpoint = frame.height // 2
        reference, current = frame[:midpoint], frame[midpoint:]

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
