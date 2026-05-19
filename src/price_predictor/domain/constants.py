"""Domain sanity bounds for the Kaggle "Apartment Prices in Poland" data.

Anti-noise filters, not business rules: reject physically impossible
values without encoding pricing assumptions. Monetary values are PLN.
"""

from __future__ import annotations

from typing import Final

PRICE_MIN_PLN: Final = 1
PRICE_MAX_PLN: Final = 50_000_000

# Dataset is apartments only; the published range is ~25-150 m^2.
SQUARE_METERS_MIN: Final = 25.0
SQUARE_METERS_MAX: Final = 150.0

ROOMS_MIN: Final = 1
ROOMS_MAX: Final = 30

# Oldest standing tenements in PL stock are ~mid 19th century.
BUILD_YEAR_MIN: Final = 1850

# Floors are non-negative in this dataset's encoding.
FLOOR_MIN: Final = 0
FLOOR_MAX: Final = 100

# Bounding box of Poland (degrees).
LATITUDE_MIN: Final = 49.0
LATITUDE_MAX: Final = 55.0
LONGITUDE_MIN: Final = 14.0
LONGITUDE_MAX: Final = 24.0
