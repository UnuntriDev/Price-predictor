"""FastAPI application factory.

The factory takes its collaborators as arguments (no module-level app,
no global predictor) so tests construct an app with a fake service and
production wiring lives in one composition root.
"""

from __future__ import annotations

import time

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, Response
from prometheus_client import CONTENT_TYPE_LATEST, generate_latest

from price_predictor import __version__
from price_predictor.config import get_logger
from price_predictor.domain import (
    DomainValidationError,
    PredictionRequest,
    PredictionResult,
    PricePredictorError,
    ServingError,
)
from price_predictor.monitoring.metrics import (
    PREDICTION_LATENCY,
    PREDICTION_REQUESTS,
)
from price_predictor.serving.ports import PredictorService
from price_predictor.serving.schemas import HealthResponse

_log = get_logger(__name__)

_HTTP_NOT_IMPLEMENTED = 501
_HTTP_UNPROCESSABLE = 422
_HTTP_SERVICE_UNAVAILABLE = 503
_HTTP_INTERNAL = 500

_OUTCOMES = ("ok", "error")


def create_app(predictor: PredictorService) -> FastAPI:
    """Build the inference API around an injected predictor.

    Args:
        predictor: The service that fulfils prediction requests.

    Returns:
        A configured :class:`fastapi.FastAPI` instance.
    """
    app = FastAPI(title="PricePredictor API", version=__version__)
    # Initialise label series so /metrics exposes them before any request.
    for outcome in _OUTCOMES:
        PREDICTION_REQUESTS.labels(outcome=outcome)

    @app.get("/health", response_model=HealthResponse, tags=["ops"])
    async def health() -> HealthResponse:
        return HealthResponse(status="ok", version=__version__)

    @app.get("/metrics", tags=["ops"])
    async def metrics() -> Response:
        return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)

    @app.post("/predict", response_model=PredictionResult, tags=["inference"])
    async def predict(payload: PredictionRequest) -> PredictionResult:
        start = time.perf_counter()
        try:
            result = predictor.predict(payload)
        except Exception:
            PREDICTION_REQUESTS.labels(outcome="error").inc()
            raise
        PREDICTION_REQUESTS.labels(outcome="ok").inc()
        PREDICTION_LATENCY.observe(time.perf_counter() - start)
        return result

    _register_error_handlers(app)
    return app


def _json_error(status_code: int, detail: str) -> JSONResponse:
    return JSONResponse(status_code=status_code, content={"detail": detail})


def _register_error_handlers(app: FastAPI) -> None:
    """Map the domain exception hierarchy onto HTTP status codes."""

    @app.exception_handler(NotImplementedError)
    async def _not_implemented(_request: Request, exc: NotImplementedError) -> JSONResponse:
        return _json_error(_HTTP_NOT_IMPLEMENTED, str(exc) or "Not implemented")

    @app.exception_handler(DomainValidationError)
    async def _validation(_request: Request, exc: DomainValidationError) -> JSONResponse:
        return _json_error(_HTTP_UNPROCESSABLE, str(exc))

    @app.exception_handler(ServingError)
    async def _serving(_request: Request, exc: ServingError) -> JSONResponse:
        return _json_error(_HTTP_SERVICE_UNAVAILABLE, str(exc))

    @app.exception_handler(PricePredictorError)
    async def _fallback(_request: Request, exc: PricePredictorError) -> JSONResponse:
        _log.error("unhandled.domain_error", error=str(exc))
        return _json_error(_HTTP_INTERNAL, "Internal error")
