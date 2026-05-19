"""Scraping layer: illustrative skeleton only (ADR 0013/0014).

Inactive in the data pipeline. The data source is the Kaggle dataset
(see :mod:`price_predictor.data.kaggle`).
"""

from __future__ import annotations

from price_predictor.scraping.pipelines import ListingValidationPipeline
from price_predictor.scraping.ports import ScrapeRunner
from price_predictor.scraping.runner import ScrapyRunner
from price_predictor.scraping.spider import OtodomSpider

__all__ = [
    "ListingValidationPipeline",
    "OtodomSpider",
    "ScrapeRunner",
    "ScrapyRunner",
]
