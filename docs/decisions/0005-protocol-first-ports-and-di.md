# 5. Protocol-first ports and constructor injection

- Status: accepted
- Date: 2026-05-18

## Context

The pipeline crosses many I/O boundaries (Postgres, DuckDB, MLflow,
Scrapy, Evidently). Hard-wiring concrete clients makes the code
untestable and the layers circular.

## Decision

- Every cross-boundary dependency is a `typing.Protocol` ("port").
  Concrete classes ("adapters") implement it; nothing imports a
  vendor SDK to satisfy a type.
- Collaborators are passed via constructors / factory arguments. No
  module-level singletons or global state. `serving.asgi.get_app` is the
  single composition root.
- Domain models (`pydantic`) and dataframe schemas (`pandera`) are the
  stable contracts every layer depends on.

## Consequences

- Units test against fakes; no DB needed for the bulk of the suite.
- Swapping an adapter (e.g. registry backend) is a one-file change.
- Slightly more boilerplate (a port + an adapter) per integration.
