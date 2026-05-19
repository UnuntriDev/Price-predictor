"""Human-facing Evidently HTML drift report (ADR 0012).

The programmatic gate is :class:`StatisticalDriftDetector`; this module
is the *report* side — a rich HTML artifact for humans. It is isolated
here so Evidently's evolving API touches exactly one file.
"""

from __future__ import annotations

from pathlib import Path

import polars as pl
from evidently import Report
from evidently.presets import DataDriftPreset

from price_predictor.domain import MonitoringError


class EvidentlyReportGenerator:
    """Writes an Evidently ``DataDriftPreset`` report as standalone HTML."""

    def generate(
        self,
        reference: pl.DataFrame,
        current: pl.DataFrame,
        output_path: Path,
    ) -> Path:
        """Render the drift report to ``output_path``.

        Args:
            reference: Baseline window.
            current: Window under inspection.
            output_path: Destination ``.html`` file.

        Returns:
            ``output_path``.

        Raises:
            MonitoringError: If the frames are empty or Evidently fails.
        """
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
        except Exception as exc:  # Evidently raises broadly
            msg = f"Evidently report generation failed: {exc}"
            raise MonitoringError(msg) from exc
        return output_path
