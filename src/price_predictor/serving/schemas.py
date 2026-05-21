"""HTTP-only response models.

Request/response payloads reuse the domain contracts directly
(``PredictionRequest`` / ``PredictionResult``); only transport-specific
shapes live here.
"""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict

from price_predictor.domain import ModelStage


class ModelInfo(BaseModel):
    """Metadata about the model currently backing ``/predict``.

    Surfaced on ``/health`` so operators (and the UI footer) can see
    which registry artefact is live without poking MLflow directly.
    """

    name: str
    version: str
    stage: ModelStage
    loaded: bool


class HealthResponse(BaseModel):
    """Liveness/readiness probe payload."""

    # Avoid Pydantic v2's protected ``model_`` namespace warning on the
    # ``model_info`` field name.
    model_config = ConfigDict(protected_namespaces=())

    status: str
    version: str
    model_info: ModelInfo | None = None
