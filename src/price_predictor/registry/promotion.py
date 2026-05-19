"""Automated promotion recommendation (ADR 0010).

A human owns the actual stage transition; this module only computes an
evidence-based *recommendation* by comparing a candidate's primary
metric against the incumbent production model.
"""

from __future__ import annotations

from collections.abc import Mapping

from pydantic import BaseModel, ConfigDict

from price_predictor.domain import RegistryError


class PromotionRecommendation(BaseModel):
    """Advice for a human promotion gate."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    should_promote: bool
    reason: str
    primary_metric: str
    candidate: float
    incumbent: float | None
    relative_improvement: float | None


def recommend_promotion(
    candidate_metrics: Mapping[str, float],
    incumbent_metrics: Mapping[str, float] | None,
    *,
    primary: str = "mae",
    lower_is_better: bool = True,
    min_relative_improvement: float = 0.0,
) -> PromotionRecommendation:
    """Recommend whether to promote the candidate model.

    Args:
        candidate_metrics: The new run's metrics.
        incumbent_metrics: The current production model's metrics, or
            ``None`` if there is no production model yet.
        primary: Metric key the decision hinges on.
        lower_is_better: True for error metrics (MAE/RMSE), False for
            score metrics (R^2).
        min_relative_improvement: Required fractional improvement over
            the incumbent (e.g. ``0.02`` for 2%).

    Returns:
        The recommendation.

    Raises:
        RegistryError: If ``primary`` is missing from a provided metrics
            mapping.
    """
    if primary not in candidate_metrics:
        msg = f"candidate metrics missing primary metric {primary!r}"
        raise RegistryError(msg)

    cand = candidate_metrics[primary]
    if incumbent_metrics is None:
        return PromotionRecommendation(
            should_promote=True,
            reason="no incumbent production model; promote the first candidate",
            primary_metric=primary,
            candidate=cand,
            incumbent=None,
            relative_improvement=None,
        )
    if primary not in incumbent_metrics:
        msg = f"incumbent metrics missing primary metric {primary!r}"
        raise RegistryError(msg)

    inc = incumbent_metrics[primary]
    gain = (inc - cand) if lower_is_better else (cand - inc)
    denom = abs(inc) if inc != 0 else 1.0
    rel = gain / denom
    promote = rel > min_relative_improvement
    direction = "lower" if lower_is_better else "higher"
    reason = (
        f"{primary} {cand:.6g} vs incumbent {inc:.6g} "
        f"({rel:+.2%}; {direction} is better; "
        f"threshold {min_relative_improvement:+.2%}) -> "
        f"{'promote' if promote else 'hold'}"
    )
    return PromotionRecommendation(
        should_promote=promote,
        reason=reason,
        primary_metric=primary,
        candidate=cand,
        incumbent=inc,
        relative_improvement=rel,
    )
