"""EvidentlyReportGenerator writes a non-empty standalone HTML report."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import polars as pl
import pytest

from price_predictor.domain import MonitoringError
from price_predictor.monitoring import EvidentlyReportGenerator


def _frame(loc: float, seed: int) -> pl.DataFrame:
    rng = np.random.default_rng(seed)
    return pl.DataFrame(
        {
            "area": rng.normal(loc, 5, 120),
            "city": rng.choice(["Warszawa", "Krakow"], 120),
        }
    )


def test_generates_html_artifact(tmp_path: Path) -> None:
    out = tmp_path / "drift" / "report.html"
    result = EvidentlyReportGenerator().generate(_frame(50.0, 0), _frame(70.0, 1), out)
    assert result == out
    assert out.exists()
    content = out.read_text(encoding="utf-8", errors="ignore")
    assert len(content) > 1000
    assert "html" in content.lower()


def test_empty_frame_raises(tmp_path: Path) -> None:
    gen = EvidentlyReportGenerator()
    with pytest.raises(MonitoringError, match="non-empty"):
        gen.generate(pl.DataFrame(), _frame(1.0, 2), tmp_path / "r.html")
