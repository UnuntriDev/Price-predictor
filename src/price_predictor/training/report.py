"""Evaluation report contract.

A frozen Pydantic model so a training run's scores serialise verbatim
into MLflow and the ``registry_model_versions.metrics`` column.
"""

from __future__ import annotations

from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field


class RegressionReport(BaseModel):
    """Hold-out metrics for a price regressor."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    mae: Annotated[float, Field(ge=0.0, description="Mean absolute error, PLN")]
    rmse: Annotated[float, Field(ge=0.0, description="Root mean squared error, PLN")]
    mape: Annotated[float, Field(ge=0.0, description="Mean absolute percentage error")]
    r2: Annotated[float, Field(le=1.0, description="Coefficient of determination")]
    n_samples: Annotated[int, Field(gt=0)]

    def as_metrics(self) -> dict[str, float]:
        """Return a flat ``name -> value`` mapping for the registry/MLflow."""
        return {
            "mae": self.mae,
            "rmse": self.rmse,
            "mape": self.mape,
            "r2": self.r2,
        }
