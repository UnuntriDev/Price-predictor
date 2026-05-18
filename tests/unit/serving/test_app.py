"""The FastAPI surface is live for ops; /predict 501s until Phase 2."""

from __future__ import annotations

from fastapi.testclient import TestClient

from price_predictor.config.settings import APISettings, MLflowSettings
from price_predictor.domain import ModelStage
from price_predictor.registry import MLflowModelRegistry
from price_predictor.serving import create_app
from price_predictor.serving.predictor import ModelBackedPredictor


def _client() -> TestClient:
    predictor = ModelBackedPredictor(
        MLflowModelRegistry(MLflowSettings()),
        model_name="price-predictor",
        stage=ModelStage.PRODUCTION,
    )
    return TestClient(create_app(predictor))


def test_health_ok() -> None:
    resp = _client().get("/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"


def test_metrics_exposed() -> None:
    resp = _client().get("/metrics")
    assert resp.status_code == 200
    assert "price_predictor_prediction_requests_total" in resp.text


def test_predict_returns_501_until_phase2() -> None:
    payload = {
        "area": 55.0,
        "rooms": 3,
        "city": "Warszawa",
        "district": "Wola",
        "year_built": 2018,
        "floor": 5,
        "property_type": "apartment",
    }
    resp = _client().post("/predict", json=payload)
    assert resp.status_code == 501
    assert "Phase 2" in resp.json()["detail"]


def test_predict_rejects_invalid_payload() -> None:
    resp = _client().post("/predict", json={"area": -1})
    assert resp.status_code == 422


def test_settings_default_ports() -> None:
    api = APISettings()
    assert (api.port, api.streamlit_port) == (8000, 7860)
