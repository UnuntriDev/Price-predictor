# 3. MLflow backend: SQLite locally, Postgres in compose

- Status: accepted
- Date: 2026-05-18

## Context

MLflow needs a backend store for runs and the model registry. A local
dev loop wants zero setup; the compose stack wants something closer to
production with concurrent access.

## Decision

- Local default: `sqlite:///mlflow.db` (no service to run).
- docker-compose: an MLflow server backed by the Postgres service,
  artifacts on a mounted volume.

The URI is a single setting (`PP_MLFLOW__TRACKING_URI`) so switching is
one environment variable.

## Consequences

- Frictionless local experimentation.
- The compose stack exercises the realistic Postgres-backed path.
- SQLite's single-writer limit is acceptable for solo local runs only.
