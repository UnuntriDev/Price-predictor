"""Custom exception hierarchy.

Every error raised by first-party code derives from
:class:`PricePredictorError`, so callers can catch the whole subsystem
with one ``except`` while still discriminating on the specific subclass.
The tree mirrors the package's module boundaries.
"""

from __future__ import annotations


class PricePredictorError(Exception):
    """Base class for every error raised by PricePredictor code."""


class ConfigurationError(PricePredictorError):
    """Settings are missing, malformed, or mutually inconsistent."""


class DomainValidationError(PricePredictorError):
    """A value violates a domain invariant.

    Raised by hand-written checks; Pydantic's own ``ValidationError`` is
    wrapped into this at adapter boundaries so the rest of the codebase
    never imports pydantic just to catch validation failures.
    """


class DataError(PricePredictorError):
    """Base for the data acquisition and preparation layer."""


class ScrapeError(DataError):
    """A listing page could not be fetched or parsed."""


class SchemaValidationError(DataError):
    """A dataframe failed its Pandera schema contract."""


class StorageError(DataError):
    """A read/write against DuckDB or Postgres failed."""


class DataDownloadError(DataError):
    """The Kaggle dataset could not be downloaded (creds/CLI/network)."""


class FeatureError(PricePredictorError):
    """Feature construction failed or produced an invalid frame."""


class TrainingError(PricePredictorError):
    """Model training or hyper-parameter search failed."""


class RegistryError(PricePredictorError):
    """Base for model registry interactions."""


class ModelNotFoundError(RegistryError):
    """No model version matched the requested name/stage."""


class ServingError(PricePredictorError):
    """Base for the inference service."""


class ModelNotLoadedError(ServingError):
    """A prediction was requested before a model was loaded."""


class MonitoringError(PricePredictorError):
    """Drift detection or metrics emission failed."""
