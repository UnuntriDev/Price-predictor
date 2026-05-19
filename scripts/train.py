"""``make train`` entrypoint.

Real end-to-end run: pull listings from Postgres, run the orchestrated
training pipeline (validate -> features -> fit -> conformal -> evaluate
-> log+register), and print the promotion recommendation. Hydra selects
the estimator/params; pydantic-settings supplies the DB + MLflow config.
"""

from __future__ import annotations

import sys
from datetime import UTC, datetime

import polars as pl

from price_predictor.config import compose_config, configure_logging, get_settings
from price_predictor.data import PostgresListingRepository
from price_predictor.domain import PricePredictorError
from price_predictor.pipeline import run_training
from price_predictor.registry import MLflowModelRegistry

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


def _listings_frame(repo: PostgresListingRepository) -> pl.DataFrame:
    rows = [
        {
            "listing_id": listing.listing_id,
            "price": float(listing.price),
            "area": listing.area,
            "rooms": listing.rooms,
            "city": listing.city,
            "district": listing.district,
            "year_built": listing.year_built,
            "floor": listing.floor,
            "property_type": listing.property_type.value,
        }
        for listing in repo.fetch_all()
    ]
    return pl.DataFrame(rows, schema=list(_FRAME_COLUMNS))


def main() -> int:
    """Run the end-to-end training pipeline."""
    settings = get_settings()
    configure_logging(settings.logging)
    cfg = compose_config()

    repo = PostgresListingRepository(settings.postgres)
    registry = MLflowModelRegistry(settings.mlflow)

    try:
        frame = _listings_frame(repo)
        if frame.is_empty():
            sys.stdout.write("[train] no listings in Postgres yet; run scrape first\n")
            return 2
        result = run_training(
            frame,
            registry,
            model_name=settings.api.model_name,
            reference_year=datetime.now(UTC).year,
            estimator_name=str(cfg.model.name),
            estimator_params=dict(cfg.model.params),
        )
    except PricePredictorError as exc:
        sys.stdout.write(f"[train] failed: {exc}\n")
        return 2

    sys.stdout.write(
        f"[train] {result.model_version.name} v{result.model_version.version} | "
        f"MAE={result.report.mae:.0f} R2={result.report.r2:.3f} | "
        f"{result.recommendation.reason}\n"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
