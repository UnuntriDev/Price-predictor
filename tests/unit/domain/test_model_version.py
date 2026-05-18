"""Contract tests for the ModelVersion registry record."""

from __future__ import annotations

from datetime import UTC, datetime

from price_predictor.domain import ModelStage, ModelVersion


def test_defaults_to_none_stage_and_empty_metrics() -> None:
    mv = ModelVersion(
        name="price-xgb",
        version="7",
        run_id="abc123",
        created_at=datetime(2026, 5, 18, tzinfo=UTC),
    )
    assert mv.stage is ModelStage.NONE
    assert mv.metrics == {}


def test_metrics_are_captured() -> None:
    mv = ModelVersion(
        name="price-xgb",
        version="7",
        stage=ModelStage.PRODUCTION,
        run_id="abc123",
        metrics={"mae": 41250.5, "r2": 0.83},
        created_at=datetime(2026, 5, 18, tzinfo=UTC),
    )
    assert mv.metrics["r2"] == 0.83
    assert mv.stage is ModelStage.PRODUCTION
