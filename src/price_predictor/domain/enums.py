"""Closed enums shared across the domain.

StrEnum so JSON/Postgres/Parquet need no adapter. Values match the
Kaggle dataset verbatim — no translation table in the loader.
"""

from __future__ import annotations

from enum import StrEnum


class CityEnum(StrEnum):
    """15 cities in the Kaggle dataset."""

    SZCZECIN = "szczecin"
    GDYNIA = "gdynia"
    KRAKOW = "krakow"
    POZNAN = "poznan"
    BIALYSTOK = "bialystok"
    GDANSK = "gdansk"
    WROCLAW = "wroclaw"
    RADOM = "radom"
    RZESZOW = "rzeszow"
    LODZ = "lodz"
    KATOWICE = "katowice"
    LUBLIN = "lublin"
    CZESTOCHOWA = "czestochowa"
    WARSZAWA = "warszawa"
    BYDGOSZCZ = "bydgoszcz"


class PropertyType(StrEnum):
    """``type`` column — often missing."""

    APARTMENT_BUILDING = "apartmentBuilding"
    APARTMENT_BLOCK = "apartmentBlock"
    BLOCK_OF_FLATS = "blockOfFlats"
    TENEMENT = "tenement"


class OwnershipType(StrEnum):
    """``ownership`` column — yes, one value is in Polish ('udział')."""

    CONDOMINIUM = "condominium"
    COOPERATIVE = "cooperative"
    SHARE = "udział"


class BuildingMaterial(StrEnum):
    """``buildingMaterial`` column — frequently missing."""

    BRICK = "brick"
    CONCRETE_SLAB = "concreteSlab"


class ConditionType(StrEnum):
    """``condition`` column — mostly missing."""

    LOW = "low"
    PREMIUM = "premium"


class ModelStage(StrEnum):
    """Mirrors MLflow Model Registry stages (no mapping layer)."""

    NONE = "none"
    STAGING = "staging"
    PRODUCTION = "production"
    ARCHIVED = "archived"
