# 11. HF Space pulls the model from the remote registry at startup

- Status: accepted
- Date: 2026-05-19

## Context

The Hugging Face Space needs a model to serve. Either bake the artifact
into the image at build time, or fetch it from the remote MLflow
registry when the container starts.

## Decision

The Space **pulls the production model from the remote MLflow registry
at startup** (the `serving.asgi` composition root already resolves the
model by name + stage). The image stays model-free.

## Consequences

- Promoting a new model updates the demo on next restart — no image
  rebuild, no redeploy.
- Requires a reachable, authenticated remote MLflow tracking/registry
  server (a Phase 2 infra task) and startup-time network access.
- Cold start is slower (model download) and depends on registry
  availability — acceptable for a demo; a cached/bundled fallback can be
  revisited if it bites.
