"""Smoke tests asserting the package is importable and well-formed."""

from __future__ import annotations

import price_predictor


def test_version_is_pep440() -> None:
    """The package exposes a non-empty semantic version string."""
    parts = price_predictor.__version__.split(".")
    assert len(parts) == 3
    assert all(part.isdigit() for part in parts)
