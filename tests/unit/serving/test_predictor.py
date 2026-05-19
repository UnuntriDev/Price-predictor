"""ModelBackedPredictor: registry loading, intervals, error mapping."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

import pytest

from price_predictor.domain import (
    CityEnum,
    ModelNotLoadedError,
    ModelStage,
    ModelVersion,
    OwnershipType,
    PredictionRequest,
    RegistryError,
)
from price_predictor.serving.predictor import ModelBackedPredictor

_REQUEST = PredictionRequest(
    city=CityEnum.WARSZAWA,
    square_meters=55.0,
    rooms=3,
    latitude=52.23,
    longitude=21.01,
    centre_distance_km=2.0,
    poi_count=8,
    ownership=OwnershipType.CONDOMINIUM,
    has_parking=True,
    has_balcony=False,
    has_security=False,
    has_storage=True,
)


class _Model:
    def __init__(self, value: float, conformal_q: float | None = None) -> None:
        self._value = value
        if conformal_q is not None:
            self.conformal_q = conformal_q

    def predict(self, frame: Any) -> list[float]:
        assert frame.shape[0] == 1
        return [self._value]


class _Registry:
    def __init__(self, model: Any | None, fail: bool = False) -> None:
        self._model = model
        self._fail = fail

    def register(self, run_id: str, name: str, metrics: dict[str, float]) -> ModelVersion:
        raise NotImplementedError

    def log_and_register(self, model: Any, name: str, metrics: dict[str, float]) -> ModelVersion:
        raise NotImplementedError

    def transition_stage(self, name: str, version: str, stage: ModelStage) -> ModelVersion:
        raise NotImplementedError

    def get_version(self, name: str, stage: ModelStage) -> ModelVersion:
        return ModelVersion(
            name=name,
            version="5",
            stage=stage,
            run_id="run-1",
            created_at=datetime(2026, 5, 19, tzinfo=UTC),
        )

    def load_model(self, name: str, stage: ModelStage) -> Any:
        if self._fail:
            raise RegistryError("boom")
        return self._model


def test_predict_rounds_to_int_without_interval() -> None:
    pred = ModelBackedPredictor(_Registry(_Model(612_345.6789)), "price-predictor")
    out = pred.predict(_REQUEST)
    assert out.predicted_price == 612_346
    assert out.model_version == "5"
    assert out.interval_low is None


def test_predict_uses_conformal_band_when_present() -> None:
    pred = ModelBackedPredictor(
        _Registry(_Model(500_000.0, conformal_q=25_000.0)), "price-predictor"
    )
    out = pred.predict(_REQUEST)
    assert out.interval_low == 475_000
    assert out.interval_high == 525_000


def test_model_caches_after_first_load() -> None:
    registry = _Registry(_Model(1.0))
    pred = ModelBackedPredictor(registry, "price-predictor")
    pred.predict(_REQUEST)
    registry._model = None  # would break a second load if not cached
    pred.predict(_REQUEST)  # must not raise


def test_registry_failure_maps_to_model_not_loaded() -> None:
    pred = ModelBackedPredictor(_Registry(None, fail=True), "price-predictor")
    with pytest.raises(ModelNotLoadedError, match="could not load"):
        pred.predict(_REQUEST)
