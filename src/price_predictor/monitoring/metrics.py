"""Prometheus metric definitions.

The metric objects are declared here (a contract the dashboards depend
on); the call sites that observe them are wired in Phase 2.
"""

from __future__ import annotations

from prometheus_client import Counter, Histogram

PREDICTION_REQUESTS = Counter(
    "price_predictor_prediction_requests_total",
    "Total prediction requests received.",
    labelnames=("outcome",),
)

PREDICTION_LATENCY = Histogram(
    "price_predictor_prediction_latency_seconds",
    "Wall-clock latency of a single prediction.",
)

DRIFT_SHARE = Histogram(
    "price_predictor_drift_share",
    "Share of features flagged as drifted in the latest report.",
    buckets=(0.0, 0.1, 0.25, 0.5, 0.75, 1.0),
)
