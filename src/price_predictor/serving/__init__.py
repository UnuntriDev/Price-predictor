"""Serving layer: predictor port, skeleton, FastAPI factory, ASGI root."""

from __future__ import annotations

from price_predictor.serving.app import create_app
from price_predictor.serving.asgi import get_app
from price_predictor.serving.ports import PredictorService

__all__ = ["PredictorService", "create_app", "get_app"]
