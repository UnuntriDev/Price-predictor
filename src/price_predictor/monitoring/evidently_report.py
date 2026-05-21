"""Evidently HTML drift report (ADR 0012).

Programmatic gate lives in :mod:`drift`. Evidently's API churn is
quarantined to this one file.
"""

from __future__ import annotations

from pathlib import Path

import polars as pl
from evidently import Report
from evidently.presets import DataDriftPreset

from price_predictor.domain import MonitoringError


class EvidentlyReportGenerator:
    """Writes the ``DataDriftPreset`` as standalone HTML."""

    def generate(
        self,
        reference: pl.DataFrame,
        current: pl.DataFrame,
        output_path: Path,
    ) -> Path:
        """Render to ``output_path``."""
        if reference.is_empty() or current.is_empty():
            msg = "drift report needs non-empty reference and current frames"
            raise MonitoringError(msg)
        try:
            report = Report([DataDriftPreset()])
            snapshot = report.run(
                current_data=current.to_pandas(),
                reference_data=reference.to_pandas(),
            )
            output_path.parent.mkdir(parents=True, exist_ok=True)
            snapshot.save_html(str(output_path))
        except MonitoringError:
            raise
        except Exception as exc:  # Evidently throws a wide net
            msg = f"Evidently report generation failed: {exc}"
            raise MonitoringError(msg) from exc
        return output_path
