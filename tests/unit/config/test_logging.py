"""Logging configuration is idempotent and yields a usable logger."""

from __future__ import annotations

from price_predictor.config import configure_logging, get_logger
from price_predictor.config.settings import LoggingSettings


def test_configure_is_idempotent_and_logger_works() -> None:
    configure_logging(LoggingSettings(json_output=True, level="DEBUG"))
    configure_logging(LoggingSettings(json_output=False, level="INFO"))
    log = get_logger(__name__)
    # Should not raise with the global config in place.
    log.info("configured", component="test")
