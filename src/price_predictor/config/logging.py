"""Structured logging setup built on structlog.

A single :func:`configure_logging` call wires structlog and the stdlib
``logging`` module together so third-party libraries (uvicorn, scrapy,
mlflow) emit through the same pipeline. Output is human-readable in
development and line-delimited JSON in production.
"""

from __future__ import annotations

import logging
import sys

import structlog
from structlog.typing import Processor

from price_predictor.config.settings import LoggingSettings


def configure_logging(settings: LoggingSettings) -> None:
    """Configure structlog and the stdlib root logger.

    Idempotent: calling it again reconfigures cleanly, which keeps test
    isolation simple.

    Args:
        settings: Logging level and output-format selection.
    """
    # Force UTF-8 on stdio so third-party libs that print emoji (e.g.
    # MLflow 3's run-link "View run ... at ..." line) don't crash on
    # Windows non-UTF8 system locales such as cp1250.
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
    """Return a bound structlog logger for ``name``.

    Args:
        name: Usually ``__name__`` of the calling module.

    Returns:
        A logger that inherits the global structlog configuration.
    """
    logger: structlog.stdlib.BoundLogger = structlog.get_logger(name)
    return logger
