"""run_training wires the full flow against a fake registry."""

from __future__ import annotations

from datetime import UTC, datetime

import numpy as np
import polars as pl
import pytest

from price_predictor.domain import (
    ModelNotFoundError,
    ModelStage,
    ModelVersion,
    TrainingError,
)
from price_predictor.pipeline import ConformalModel, run_training


class FakeRegistry:
    """Captures the artifact; behaves as if no production model exists."""

    def __init__(self) -> None:
        self.logged: object | None = None
        self.metrics: dict[str, float] = {}

    def log_and_register(self, model: object, name: str, metrics: dict[str, float]) -> ModelVersion:
        self.logged = model
        self.metrics = metrics
        return ModelVersion(
            name=name,
            version="1",
            stage=ModelStage.NONE,
            run_id="run-1",
            metrics=metrics,
            created_at=datetime.now(UTC),
        )

    def get_version(self, name: str, stage: ModelStage) -> ModelVersion:
        raise ModelNotFoundError("no production model")


def _listings(n: int = 120) -> pl.DataFrame:
    rng = np.random.default_rng(7)
    sqm = rng.uniform(25, 150, n)
    rooms = rng.integers(1, 6, n)
    centre = rng.uniform(0.5, 12.0, n)
    price = 9_000 * sqm + 40_000 * rooms - 8_000 * centre + rng.normal(0, 4_000, n)
    return pl.DataFrame(
        {
            "id": [f"id-{i}" for i in range(n)],
            "city": rng.choice(["warszawa", "krakow", "gdansk"], n),
            "property_type": rng.choice(["blockOfFlats", "tenement"], n),
            "square_meters": sqm,
            "rooms": rooms,
            "floor": rng.integers(0, 12, n),
            "floor_count": rng.integers(1, 15, n),
            "build_year": rng.integers(1950, 2024, n),
            "latitude": rng.uniform(50.0, 54.0, n),
            "longitude": rng.uniform(15.0, 23.0, n),
            "centre_distance_km": centre,
            "poi_count": rng.integers(0, 60, n),
            "school_distance_km": rng.uniform(0.1, 3.0, n),
            "clinic_distance_km": rng.uniform(0.1, 3.0, n),
            "post_office_distance_km": rng.uniform(0.1, 3.0, n),
            "kindergarten_distance_km": rng.uniform(0.1, 3.0, n),
            "restaurant_distance_km": rng.uniform(0.1, 3.0, n),
            "college_distance_km": rng.uniform(0.1, 5.0, n),
            "pharmacy_distance_km": rng.uniform(0.1, 3.0, n),
            "ownership": rng.choice(["condominium", "cooperative", "udział"], n),
            "building_material": rng.choice(["brick", "concreteSlab"], n),
            "condition": rng.choice(["low", "premium"], n),
            "has_parking": rng.choice([True, False], n),
            "has_balcony": rng.choice([True, False], n),
            "has_elevator": rng.choice([True, False], n),
            "has_security": rng.choice([True, False], n),
            "has_storage": rng.choice([True, False], n),
            "price_pln": np.clip(price, 50_000, 5_000_000).astype(np.int64),
            "snapshot_month": ["2024-06"] * n,
        }
    )


def test_end_to_end_run() -> None:
    registry = FakeRegistry()
    result = run_training(
        _listings(120),
        registry,
        model_name="price-predictor",
        estimator_params={"n_estimators": 80, "max_depth": 3, "verbosity": 0},
        seed=1,
    )

    assert result.report.n_samples == round(120 * 0.2)
    assert result.report.r2 > 0.5
    assert result.model_version.version == "1"
    assert result.recommendation.should_promote is True
    assert result.recommendation.incumbent is None

    assert isinstance(registry.logged, ConformalModel)
    assert registry.logged.conformal_q > 0.0
    assert registry.metrics["mae"] == result.report.mae


def test_split_too_small_raises() -> None:
    with pytest.raises(TrainingError, match="cannot split"):
        run_training(_listings(2), FakeRegistry(), model_name="m")


def test_logged_artifact_predicts_on_raw_request() -> None:
    registry = FakeRegistry()
    run_training(
        _listings(120),
        registry,
        model_name="m",
        estimator_params={"n_estimators": 40, "max_depth": 3, "verbosity": 0},
        seed=2,
    )
    model = registry.logged
    assert isinstance(model, ConformalModel)

    raw = _listings(5).to_pandas()
    preds = model.predict(raw)
    assert len(preds) == 5
    assert (preds > 0).all()
