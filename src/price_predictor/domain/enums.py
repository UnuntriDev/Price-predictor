"""Closed enumerations used across the domain.

String-valued so they serialise cleanly to JSON, Postgres, and Parquet
without an adapter layer.
"""

from __future__ import annotations

from enum import StrEnum


class PropertyType(StrEnum):
    """Otodom dwelling category.

    Values mirror Otodom's own taxonomy so the scraper can map listing
    pages without a translation table.
    """

    APARTMENT = "apartment"
    HOUSE = "house"
    STUDIO = "studio"
    ROOM = "room"
    PLOT = "plot"
    INVESTMENT = "investment"


class ModelStage(StrEnum):
    """Lifecycle stage of a registered model version.

    Mirrors the MLflow Model Registry stages so the registry adapter is a
    thin pass-through rather than a mapping layer.
    """

    NONE = "none"
    STAGING = "staging"
    PRODUCTION = "production"
    ARCHIVED = "archived"
