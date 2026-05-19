# 8. Prediction intervals via conformal prediction

- Status: accepted
- Date: 2026-05-19

## Context

`PredictionResult` exposes `interval_low`/`interval_high`. Options
considered: quantile regression, NGBoost, and conformal prediction.

## Decision

Use **split/inductive conformal prediction** wrapped around the chosen
point regressor (model-agnostic, e.g. MAPIE-style). A calibration split
yields intervals with a finite-sample coverage guarantee.

## Consequences

- Works with any of xgboost/lightgbm/catboost without changing the
  training objective.
- Distribution-free coverage guarantee — a strong story for a portfolio
  and honest uncertainty for users.
- Requires a held-out calibration set in the training pipeline.
- Default symmetric intervals; locally-adaptive (normalized) conformal
  is a possible later refinement.
