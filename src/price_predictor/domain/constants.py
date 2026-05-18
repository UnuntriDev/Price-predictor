"""Domain sanity bounds.

These are **anti-noise filters**, not business rules. Otodom is a
free-text marketplace; scrapers will occasionally capture mis-parsed
values (e.g. a phone number where the price should be). Rejecting values
outside a generous physical range keeps obviously corrupt records out of
the training set without encoding pricing assumptions.

All monetary values are Polish zloty (PLN).
"""

from __future__ import annotations

from decimal import Decimal
from typing import Final

PRICE_MIN_PLN: Final = Decimal("10000")
PRICE_MAX_PLN: Final = Decimal("50000000")

AREA_MIN_SQM: Final = 5.0
AREA_MAX_SQM: Final = 2000.0

ROOMS_MIN: Final = 1
ROOMS_MAX: Final = 30

# Oldest standing tenements in PL stock are ~mid 19th century; the upper
# bound allows off-plan ("primary market") listings sold before completion.
YEAR_BUILT_MIN: Final = 1850
YEAR_BUILT_FUTURE_TOLERANCE: Final = 5

# Souterrain / basement units exist; high-rises in PL top out well under 100.
FLOOR_MIN: Final = -2
FLOOR_MAX: Final = 100
