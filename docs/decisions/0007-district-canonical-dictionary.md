# 7. District normalization: canonical dictionary + target-encoding fallback

- Status: accepted
- Date: 2026-05-19

## Context

`district` from Otodom is free text and inconsistent ("Mokotów",
"mokotow", "Mokotow (Górny Mokotów)"). Left raw it explodes
cardinality and fragments signal.

## Decision

A maintained **canonical district dictionary** (per city) maps raw
strings to a normalized district. Unmapped/rare values fall back to
**target encoding** (out-of-fold, fit on train only) rather than being
dropped.

## Consequences

- Common districts get stable, interpretable categories.
- Long-tail / new districts still carry price signal via the fallback.
- The dictionary is a data asset that needs curation and review; it
  lives under version control / DVC alongside the data.
- Target encoding must be fit inside CV folds to avoid leakage.
