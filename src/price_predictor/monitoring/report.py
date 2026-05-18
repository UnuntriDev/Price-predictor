"""Drift report contract."""

from __future__ import annotations

from datetime import datetime
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field


class DriftReport(BaseModel):
    """Outcome of a drift check over one feature window."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    dataset_drift: bool
    drifted_features: Annotated[tuple[str, ...], Field(default_factory=tuple)]
    share_drifted: Annotated[float, Field(ge=0.0, le=1.0)]
    generated_at: datetime
