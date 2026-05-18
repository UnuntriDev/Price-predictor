"""Production ASGI composition root.

This is the one place that wires concrete adapters together. Everything
downstream depends on ports, so swapping the registry or predictor is a
change here only. ``uvicorn --factory price_predictor.serving.asgi:get_app``
calls :func:`get_app`.
"""

from __future__ import annotations

from fastapi import FastAPI

from price_predictor.config import configure_logging, get_settings
from price_predictor.registry import MLflowModelRegistry
from price_predictor.serving.app import create_app
from price_predictor.serving.predictor import ModelBackedPredictor


def get_app() -> FastAPI:
    """Build the fully wired FastAPI application from settings.

    Returns:
        The ASGI app with a registry-backed predictor injected.
    """
    settings = get_settings()
    configure_logging(settings.logging)
    registry = MLflowModelRegistry(settings.mlflow)
    predictor = ModelBackedPredictor(
        registry,
        model_name=settings.api.model_name,
        stage=settings.api.model_stage,
    )
    return create_app(predictor)
