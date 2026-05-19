"""Programmatic crawl runner (illustrative skeleton).

Inactive — see :mod:`price_predictor.scraping.spider`. Retained to show
the DI/runner pattern; ``run`` raises rather than crawling.
"""

from __future__ import annotations

from price_predictor.config.settings import ScrapingSettings

_DISABLED = (
    "scraping disabled: Otodom DataDome anti-bot (ADR 0013/0014); "
    "use the Kaggle dataset via `make data`"
)


class ScrapyRunner:
    """Skeleton runner; not wired into any data pipeline.

    Args:
        settings: Polite-crawl parameters (unused while inactive).
    """

    def __init__(self, settings: ScrapingSettings) -> None:
        self._settings = settings

    def run(self) -> int:
        """Inactive: see module docstring."""
        raise NotImplementedError(_DISABLED)
