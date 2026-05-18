"""Serving layer: predictor port, skeleton, and FastAPI app factory."""

from __future__ import annotations

from price_predictor.serving.app import create_app
from price_predictor.serving.ports import PredictorService

__all__ = ["PredictorService", "create_app"]
