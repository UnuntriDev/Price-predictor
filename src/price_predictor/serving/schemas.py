"""Transport-only response shapes. Domain contracts are reused as-is."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict

from price_predictor.domain import ModelStage


class ModelInfo(BaseModel):
    """Identity of the artefact backing ``/predict``."""

    name: str
    version: str
    stage: ModelStage
    loaded: bool


class HealthResponse(BaseModel):
    """Liveness/readiness payload."""

    # ``model_info`` collides with Pydantic v2's protected namespace.
    model_config = ConfigDict(protected_namespaces=())

    status: str
    version: str
    model_info: ModelInfo | None = None
