"""Serving port."""

from __future__ import annotations

from typing import Protocol, runtime_checkable

from price_predictor.domain import PredictionRequest, PredictionResult


@runtime_checkable
class PredictorService(Protocol):
    """Turns a validated request into a price estimate."""

    def predict(self, request: PredictionRequest) -> PredictionResult:
        """Return a :class:`PredictionResult` for ``request``.

        Raises:
            ModelNotLoadedError: If no model is loaded yet.
        """
        ...
