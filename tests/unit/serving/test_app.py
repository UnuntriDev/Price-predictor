"""FastAPI surface: ops live, /predict delegates to the injected service."""

from __future__ import annotations

from datetime import UTC, datetime

from fastapi.testclient import TestClient

from price_predictor.config.settings import APISettings, MLflowSettings
from price_predictor.domain import (
    ModelNotLoadedError,
    PredictionRequest,
    PredictionResult,
)
from price_predictor.registry import MLflowModelRegistry
from price_predictor.serving import create_app, get_app
from price_predictor.serving.predictor import ModelBackedPredictor
from price_predictor.serving.schemas import ModelInfo

_PAYLOAD = {
    "city": "warszawa",
    "square_meters": 55.0,
    "rooms": 3,
    "latitude": 52.23,
    "longitude": 21.01,
    "centre_distance_km": 2.0,
    "poi_count": 8,
    "ownership": "condominium",
    "has_parking": True,
    "has_balcony": False,
    "has_security": False,
    "has_storage": True,
}


class _OkPredictor:
    def predict(self, request: PredictionRequest) -> PredictionResult:
        assert isinstance(request, PredictionRequest)
        return PredictionResult(
            predicted_price=612_345,
            model_name="price-predictor",
            model_version="3",
            predicted_at=datetime(2026, 5, 19, tzinfo=UTC),
        )


class _UnavailablePredictor:
    def predict(self, request: PredictionRequest) -> PredictionResult:
        raise ModelNotLoadedError("no production model")


class _DescribingPredictor(_OkPredictor):
    def describe_model(self) -> ModelInfo:
        return ModelInfo(
            name="price-predictor",
            version="3",
            stage="production",
            loaded=True,
        )


def test_health_ok() -> None:
    resp = TestClient(create_app(_OkPredictor())).get("/health")
    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] == "ok"
    # Plain PredictorService without describe_model -> no model_info.
    assert body["model_info"] is None


def test_health_exposes_model_info_when_predictor_supports_it() -> None:
    resp = TestClient(create_app(_DescribingPredictor())).get("/health")
    assert resp.status_code == 200
    info = resp.json()["model_info"]
    assert info == {
        "name": "price-predictor",
        "version": "3",
        "stage": "production",
        "loaded": True,
    }


def test_describe_model_reflects_load_state() -> None:
    predictor = ModelBackedPredictor(
        MLflowModelRegistry(MLflowSettings(tracking_uri="http://127.0.0.1:1")),
        model_name="price-predictor",
    )
    # Before warmup: ``loaded`` is the contract; ``version`` is an
    # internal placeholder when nothing has been resolved yet.
    info = predictor.describe_model()
    assert info.loaded is False
    assert info.name == "price-predictor"
    assert info.stage == "production"


def test_metrics_exposed() -> None:
    resp = TestClient(create_app(_OkPredictor())).get("/metrics")
    assert resp.status_code == 200
    assert "price_predictor_prediction_requests_total" in resp.text


def test_predict_ok() -> None:
    resp = TestClient(create_app(_OkPredictor())).post("/predict", json=_PAYLOAD)
    assert resp.status_code == 200
    assert resp.json()["predicted_price"] == 612_345


def test_predict_model_unavailable_returns_503() -> None:
    resp = TestClient(create_app(_UnavailablePredictor())).post("/predict", json=_PAYLOAD)
    assert resp.status_code == 503


def test_predict_rejects_invalid_payload() -> None:
    resp = TestClient(create_app(_OkPredictor())).post("/predict", json={"city": "warszawa"})
    assert resp.status_code == 422


def test_settings_default_ports() -> None:
    api = APISettings()
    assert (api.port, api.streamlit_port) == (8000, 7860)


def test_asgi_composition_root_builds_a_live_app() -> None:
    resp = TestClient(get_app()).get("/health")
    assert resp.status_code == 200


def test_startup_warmup_is_tolerant_of_registry_outage() -> None:
    # ADR 0011: registry down at startup -> app still healthy; /predict 503.
    predictor = ModelBackedPredictor(
        MLflowModelRegistry(MLflowSettings(tracking_uri="http://127.0.0.1:1")),
        model_name="price-predictor",
    )
    with TestClient(create_app(predictor)) as client:  # runs lifespan/warmup
        assert client.get("/health").status_code == 200
        assert client.post("/predict", json=_PAYLOAD).status_code == 503
