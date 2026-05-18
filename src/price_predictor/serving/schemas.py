"""HTTP-only response models.

Request/response payloads reuse the domain contracts directly
(``PredictionRequest`` / ``PredictionResult``); only transport-specific
shapes live here.
"""

from __future__ import annotations

from pydantic import BaseModel


class HealthResponse(BaseModel):
    """Liveness/readiness probe payload."""

    status: str
    version: str
