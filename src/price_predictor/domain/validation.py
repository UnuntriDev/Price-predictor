"""Shared domain validation helpers."""

from __future__ import annotations

from datetime import UTC, datetime


def validate_build_year_not_future(build_year: int | None) -> None:
    """Reject construction years after the current UTC year."""
    if build_year is None:
        return
    ceiling = datetime.now(UTC).year
    if build_year > ceiling:
        msg = f"build_year {build_year} exceeds current year {ceiling}"
        raise ValueError(msg)
