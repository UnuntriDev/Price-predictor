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


def _listings(n: int = 90) -> pl.DataFrame:
    rng = np.random.default_rng(7)
    area = rng.uniform(25, 110, n)
    rooms = rng.integers(1, 6, n)
    cities = rng.choice(["Warszawa", "Krakow", "Gdansk"], n)
    districts = rng.choice(["Wola", "Mokotow", "Centrum"], n)
    price = 8_000 * area + 60_000 * rooms + rng.normal(0, 5_000, n) + 50_000
    return pl.DataFrame(
        {
            "listing_id": [f"OT-{i}" for i in range(n)],
            "price": price,
            "area": area,
            "rooms": rooms,
            "city": cities,
            "district": districts,
            "year_built": rng.integers(1960, 2024, n),
            "floor": rng.integers(0, 12, n),
            "property_type": ["apartment"] * n,
        }
    )


def test_end_to_end_run() -> None:
    registry = FakeRegistry()
    result = run_training(
        _listings(90),
        registry,
        model_name="price-predictor",
        reference_year=2026,
        estimator_params={"n_estimators": 60, "max_depth": 3, "verbosity": 0},
        seed=1,
    )

    # round(90*0.2) == 18 held-out test rows
    assert result.report.n_samples == 18
    assert result.report.r2 > 0.5  # strong synthetic signal
    assert result.model_version.version == "1"
    assert result.recommendation.should_promote is True
    assert result.recommendation.incumbent is None

    assert isinstance(registry.logged, ConformalModel)
    assert registry.logged.conformal_q > 0.0
    assert registry.metrics["mae"] == result.report.mae


def test_split_too_small_raises() -> None:
    with pytest.raises(TrainingError, match="cannot split"):
        run_training(
            _listings(2),
            FakeRegistry(),
            model_name="m",
            reference_year=2026,
        )


def test_logged_artifact_predicts_on_raw_request() -> None:
    registry = FakeRegistry()
    run_training(
        _listings(90),
        registry,
        model_name="m",
        reference_year=2026,
        estimator_params={"n_estimators": 40, "max_depth": 3, "verbosity": 0},
        seed=2,
    )
    model = registry.logged
    assert isinstance(model, ConformalModel)

    raw = _listings(5).drop("price", "listing_id").to_pandas()
    preds = model.predict(raw)
    assert len(preds) == 5
    assert (preds > 0).all()
