"""Closed enumerations used across the domain.

String-valued so they serialise cleanly to JSON, Postgres, and Parquet
without an adapter layer. Values mirror the Kaggle "Apartment Prices in
Poland" dataset verbatim so the loader maps without a translation table.
"""

from __future__ import annotations

from enum import StrEnum


class CityEnum(StrEnum):
    """The 15 cities present in the dataset."""

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
    """Dataset ``type`` column (often missing -> Optional in the model)."""

    APARTMENT_BUILDING = "apartmentBuilding"
    APARTMENT_BLOCK = "apartmentBlock"
    BLOCK_OF_FLATS = "blockOfFlats"
    TENEMENT = "tenement"


class OwnershipType(StrEnum):
    """Dataset ``ownership`` column. Note the Polish 'udział'."""

    CONDOMINIUM = "condominium"
    COOPERATIVE = "cooperative"
    SHARE = "udział"


class BuildingMaterial(StrEnum):
    """Dataset ``buildingMaterial`` column (frequently missing)."""

    BRICK = "brick"
    CONCRETE_SLAB = "concreteSlab"


class ConditionType(StrEnum):
    """Dataset ``condition`` column (mostly missing)."""

    LOW = "low"
    PREMIUM = "premium"


class ModelStage(StrEnum):
    """Lifecycle stage of a registered model version.

    Mirrors the MLflow Model Registry stages so the registry adapter is a
    thin pass-through rather than a mapping layer.
    """

    NONE = "none"
    STAGING = "staging"
    PRODUCTION = "production"
    ARCHIVED = "archived"
