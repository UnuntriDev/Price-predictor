"""Scraping layer: spider, item pipeline, and runner skeletons."""

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
