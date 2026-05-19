"""FastAPI surface: ops live, /predict delegates to the injected service."""

from __future__ import annotations

from datetime import UTC, datetime

from fastapi.testclient import TestClient

from price_predictor.config.settings import APISettings
from price_predictor.domain import (
    ModelNotLoadedError,
    PredictionRequest,
    PredictionResult,
)
from price_predictor.serving import create_app, get_app

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


def test_health_ok() -> None:
    resp = TestClient(create_app(_OkPredictor())).get("/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"


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
