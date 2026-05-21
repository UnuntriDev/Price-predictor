"""Merge Kaggle sale CSVs into one Polars LazyFrame.

Renames camelCase→snake, casts yes/no→bool, stamps ``snapshot_month``
from the filename. Rent files are skipped. Output matches
:class:`RawListingSchema`.
"""

from __future__ import annotations

import re
from pathlib import Path

import polars as pl

from price_predictor.domain import DataError

_SALE_FILE = re.compile(r"^apartments_pl_(\d{4})_(\d{2})\.csv$")

_RENAME = {
    "id": "id",
    "city": "city",
    "type": "property_type",
    "squareMeters": "square_meters",
    "rooms": "rooms",
    "floor": "floor",
    "floorCount": "floor_count",
    "buildYear": "build_year",
    "latitude": "latitude",
    "longitude": "longitude",
    "centreDistance": "centre_distance_km",
    "poiCount": "poi_count",
    "schoolDistance": "school_distance_km",
    "clinicDistance": "clinic_distance_km",
    "postOfficeDistance": "post_office_distance_km",
    "kindergartenDistance": "kindergarten_distance_km",
    "restaurantDistance": "restaurant_distance_km",
    "collegeDistance": "college_distance_km",
    "pharmacyDistance": "pharmacy_distance_km",
    "ownership": "ownership",
    "buildingMaterial": "building_material",
    "condition": "condition",
    "hasParkingSpace": "has_parking",
    "hasBalcony": "has_balcony",
    "hasElevator": "has_elevator",
    "hasSecurity": "has_security",
    "hasStorageRoom": "has_storage",
    "price": "price_pln",
}

_BOOL_COLUMNS = (
    "has_parking",
    "has_balcony",
    "has_elevator",
    "has_security",
    "has_storage",
)

_OUTPUT_ORDER = (
    "id",
    "city",
    "property_type",
    "square_meters",
    "rooms",
    "floor",
    "floor_count",
    "build_year",
    "latitude",
    "longitude",
    "centre_distance_km",
    "poi_count",
    "school_distance_km",
    "clinic_distance_km",
    "post_office_distance_km",
    "kindergarten_distance_km",
    "restaurant_distance_km",
    "college_distance_km",
    "pharmacy_distance_km",
    "ownership",
    "building_material",
    "condition",
    *_BOOL_COLUMNS,
    "price_pln",
    "snapshot_month",
)


def _yes_no_to_bool(column: str) -> pl.Expr:
    return (
        pl.when(pl.col(column).str.to_lowercase() == "yes")
        .then(pl.lit(value=True))
        .when(pl.col(column).str.to_lowercase() == "no")
        .then(pl.lit(value=False))
        .otherwise(None)
        .alias(column)
    )


def load_listings(raw_dir: Path) -> pl.LazyFrame:
    """Stack every ``apartments_pl_YYYY_MM.csv`` under ``raw_dir``."""
    frames: list[pl.LazyFrame] = []
    for path in sorted(raw_dir.glob("apartments_pl_*.csv")):
        match = _SALE_FILE.match(path.name)
        if match is None:
            continue
        year, month = match.groups()
        lf = (
            pl.scan_csv(path, infer_schema_length=10_000, null_values=[""])
            .rename(_RENAME)
            .with_columns(
                *[_yes_no_to_bool(col) for col in _BOOL_COLUMNS],
                pl.lit(f"{year}-{month}").alias("snapshot_month"),
            )
            .select(_OUTPUT_ORDER)
        )
        frames.append(lf)

    if not frames:
        msg = f"no apartments_pl_*.csv sale files found in {raw_dir}"
        raise DataError(msg)
    return pl.concat(frames, how="vertical")
