"""Registry metadata contract: mirrors a row of the ``model_versions`` table."""

from __future__ import annotations

from datetime import datetime
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field

from price_predictor.domain.enums import ModelStage
from price_predictor.domain.listing import NonEmptyStr


class ModelVersion(BaseModel):
    """An immutable pointer to one trained-model artifact.

    Attributes:
        name: Registered model name.
        version: Monotonic version string assigned by the registry.
        stage: Lifecycle stage.
        run_id: Tracking run that produced the artifact.
        metrics: Validation metrics captured at registration time.
        created_at: UTC registration timestamp.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    name: NonEmptyStr
    version: NonEmptyStr
    stage: ModelStage = ModelStage.NONE
    run_id: NonEmptyStr
    metrics: Annotated[dict[str, float], Field(default_factory=dict)]
    created_at: datetime
