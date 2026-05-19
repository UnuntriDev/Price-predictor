"""Model registry layer: port, MLflow adapter, promotion advice."""

from __future__ import annotations

from price_predictor.registry.mlflow_registry import MLflowModelRegistry
from price_predictor.registry.ports import ModelRegistry
from price_predictor.registry.promotion import (
    PromotionRecommendation,
    recommend_promotion,
)

__all__ = [
    "MLflowModelRegistry",
    "ModelRegistry",
    "PromotionRecommendation",
    "recommend_promotion",
]
