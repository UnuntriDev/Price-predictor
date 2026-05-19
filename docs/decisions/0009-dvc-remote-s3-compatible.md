# 9. DVC remote: S3-compatible (MinIO local, AWS S3 prod)

- Status: accepted
- Date: 2026-05-19

## Context

The dataset and the district dictionary need a versioned remote. The
local dev loop should not depend on a cloud account; production wants a
durable managed store.

## Decision

Use an **S3-compatible** DVC remote:

- **Local / CI**: a MinIO service (added to `docker-compose.yml` in
  Phase 2) — same S3 API, zero cloud dependency.
- **Production**: AWS S3.

The remote URL/endpoint is configuration, so switching is an env change,
not a code change. **Google Drive remains a documented fallback** for
contributors without S3/MinIO; it is not the primary path.

## Consequences

- One DVC code path; MinIO and AWS differ only by endpoint/credentials.
- CI can pull data deterministically from MinIO.
- Open sub-decision: exact prod bucket/region and whether the GDrive
  fallback is actually wired or just documented.
