"""structlog + stdlib logging wiring (JSON in prod, console in dev)."""

from __future__ import annotations

import logging
import sys

import structlog
from structlog.typing import Processor

from price_predictor.config.settings import LoggingSettings


def configure_logging(settings: LoggingSettings) -> None:
    """Configure structlog + stdlib root. Idempotent."""
    # Pin stdio to UTF-8 so MLflow 3's emoji run-link doesn't crash on
    # Windows cp1250.
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8", errors="backslashreplace")

    shared: list[Processor] = [
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso", utc=True),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
    ]
    renderer: Processor = (
        structlog.processors.JSONRenderer()
        if settings.json_output
        else structlog.dev.ConsoleRenderer(colors=sys.stderr.isatty())
    )

    level = logging.getLevelNamesMapping().get(settings.level.upper(), logging.INFO)

    logging.basicConfig(format="%(message)s", stream=sys.stderr, level=level)
    structlog.configure(
        processors=[*shared, renderer],
        wrapper_class=structlog.make_filtering_bound_logger(level),
        logger_factory=structlog.PrintLoggerFactory(file=sys.stderr),
        cache_logger_on_first_use=True,
    )


def get_logger(name: str) -> structlog.stdlib.BoundLogger:
    """Bound logger for ``name`` (usually ``__name__``)."""
    logger: structlog.stdlib.BoundLogger = structlog.get_logger(name)
    return logger
