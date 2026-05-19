# 4. One Hugging Face Spaces image; heavy infra stays local

- Status: accepted
- Date: 2026-05-18

## Context

A Hugging Face Space is a single container with one public port. The
full stack (Postgres, MLflow, Prometheus, Grafana) cannot — and should
not — run there for a demo.

## Decision

- The Space ships **one image** running Streamlit (`:7860`, public) and
  FastAPI (`:8000`, internal) via **supervisord**. Streamlit calls the
  API over localhost.
- Postgres / MLflow / Prometheus / Grafana exist **only** in
  `docker-compose.yml` for local runs.
- The demo serves a model loaded from the registry; it does not scrape,
  train, or persist.

## Consequences

- The public demo is cheap, single-container, and reproducible
  (`docker-compose.spaces.yml`).
- Full observability/persistence requires the local stack — an explicit,
  documented trade-off rather than an accident.
