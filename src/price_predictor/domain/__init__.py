"""Pure domain layer: Pydantic contracts, enums, and the error hierarchy.

This package has no I/O and no third-party dependencies beyond Pydantic.
Everything that crosses a module boundary is defined here so the rest of
the codebase depends on stable contracts rather than each other.
"""

from __future__ import annotations

from price_predictor.domain.enums import ModelStage, PropertyType
from price_predictor.domain.exceptions import (
    ConfigurationError,
    DataError,
    DomainValidationError,
    FeatureError,
    ModelNotFoundError,
    ModelNotLoadedError,
    MonitoringError,
    PricePredictorError,
    RegistryError,
    SchemaValidationError,
    ScrapeError,
    ServingError,
    StorageError,
    TrainingError,
)
from price_predictor.domain.listing import Listing
from price_predictor.domain.model_version import ModelVersion
from price_predictor.domain.prediction import PredictionRequest, PredictionResult

__all__ = [
    "ConfigurationError",
    "DataError",
    "DomainValidationError",
    "FeatureError",
    "Listing",
    "ModelNotFoundError",
    "ModelNotLoadedError",
    "ModelStage",
    "ModelVersion",
    "MonitoringError",
    "PredictionRequest",
    "PredictionResult",
    "PricePredictorError",
    "PropertyType",
    "RegistryError",
    "SchemaValidationError",
    "ScrapeError",
    "ServingError",
    "StorageError",
    "TrainingError",
]
