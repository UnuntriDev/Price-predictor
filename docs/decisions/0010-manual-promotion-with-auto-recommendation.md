# 10. Model promotion: manual gate with automated recommendation

- Status: accepted
- Date: 2026-05-19

## Context

A new training run produces a candidate model version. Promotion to
`production` can be fully automated (on metric improvement) or fully
manual. Fully automated risks shipping a regression that metrics didn't
catch; fully manual loses the signal of *which* run is worth shipping.

## Decision

**Manual promotion gate with an automated recommendation.** The pipeline
evaluates the candidate against the current production model and emits a
recommendation (promote / hold) with the metric delta and drift context;
a human performs the actual stage transition via the registry.

## Consequences

- A human owns the production-impacting action (`registry.transition_stage`).
- The recommendation makes the decision fast and evidence-based.
- Requires a comparison step (candidate vs. production) and somewhere to
  surface the recommendation (CI summary / Streamlit ops view).
