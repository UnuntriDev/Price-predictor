"""Automated promotion advice (ADR 0010). The transition itself is manual."""

from __future__ import annotations

from collections.abc import Mapping

from pydantic import BaseModel, ConfigDict

from price_predictor.domain import RegistryError


class PromotionRecommendation(BaseModel):
    """Promote/hold + the numbers behind the decision."""

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
    """Compare candidate vs incumbent on ``primary`` and recommend."""
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
