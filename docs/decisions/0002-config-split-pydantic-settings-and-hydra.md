# 2. Split config: pydantic-settings for env, Hydra for experiments

- Status: accepted
- Date: 2026-05-18

## Context

The project has two very different kinds of configuration: deployment
environment + secrets (DB DSN, ports, tracking URI) and experiment
composition (which model, search space, data window). Forcing both into
one tool makes each awkward.

## Decision

- **pydantic-settings** owns the runtime environment and secrets:
  validated, typed, `PP_`-prefixed, `SecretStr` for credentials.
- **Hydra** owns experiment composition: `configs/` group tree, CLI
  overrides, multirun.

They never read each other's sources. `compose_config()` is the only
Hydra seam; `get_settings()` is the only environment seam.

## Consequences

- Secrets never live in YAML; experiments never live in env vars.
- Two config entrypoints to learn — documented in the README and code.
