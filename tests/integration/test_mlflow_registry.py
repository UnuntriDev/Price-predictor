"""Integration placeholder: real MLflow registry round-trip (Phase 2)."""

from __future__ import annotations

import pytest

pytestmark = pytest.mark.integration


@pytest.mark.skip(reason="Phase 2: needs an MLflow tracking server / SQLite store")
def test_register_and_promote() -> None:
    raise AssertionError("unreachable until Phase 2")
