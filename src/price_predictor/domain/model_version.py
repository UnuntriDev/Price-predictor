"""Registry metadata contract: mirrors a row of ``registry_model_versions``."""

from __future__ import annotations

from datetime import datetime
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field

from price_predictor.domain.enums import ModelStage
from price_predictor.domain.listing import NonEmptyStr


class ModelVersion(BaseModel):
    """Pointer to one registered model artefact."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    name: NonEmptyStr
    version: NonEmptyStr
    stage: ModelStage = ModelStage.NONE
    run_id: NonEmptyStr
    metrics: Annotated[dict[str, float], Field(default_factory=dict)]
    created_at: datetime
