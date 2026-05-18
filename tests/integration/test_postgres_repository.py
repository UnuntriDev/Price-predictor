"""Integration placeholder: real Postgres round-trip (Phase 2).

Marked ``integration`` and skipped so the suite mirrors src/ now while
the implementation and a docker-compose Postgres fixture land later.
"""

from __future__ import annotations

import pytest

pytestmark = pytest.mark.integration


@pytest.mark.skip(reason="Phase 2: needs the docker-compose Postgres service")
def test_upsert_then_fetch_roundtrip() -> None:
    raise AssertionError("unreachable until Phase 2")
