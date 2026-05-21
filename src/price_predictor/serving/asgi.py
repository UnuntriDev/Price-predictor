"""Composition root for prod. Everything else depends on ports.

uvicorn entry: ``uvicorn --factory price_predictor.serving.asgi:get_app``.
"""

from __future__ import annotations

from fastapi import FastAPI

from price_predictor.config import configure_logging, get_settings
from price_predictor.registry import MLflowModelRegistry
from price_predictor.serving.app import create_app
from price_predictor.serving.predictor import ModelBackedPredictor


def get_app() -> FastAPI:
    """Build the wired FastAPI app from settings."""
    settings = get_settings()
    configure_logging(settings.logging)
    registry = MLflowModelRegistry(settings.mlflow)
    predictor = ModelBackedPredictor(
        registry,
        model_name=settings.api.model_name,
        stage=settings.api.model_stage,
    )
    return create_app(predictor)
