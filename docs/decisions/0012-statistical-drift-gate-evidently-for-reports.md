# 12. Programmatic drift gate is statistical; Evidently is for reports

- Status: accepted
- Date: 2026-05-19

## Context

ADR 0004/stack lists Evidently for monitoring. Evidently's programmatic
result schema changes substantially across minor versions (0.4 -> 0.6 ->
0.7 restructured the public API and the result dict). A CI/serving
*drift gate* must be deterministic, version-stable, and unit-testable.

## Decision

- The programmatic drift gate (`monitoring.StatisticalDriftDetector`)
  uses transparent two-sample tests: **Kolmogorov–Smirnov** for numeric
  features and **Population Stability Index** for categorical features —
  the same tests Evidently's `DataDriftPreset` applies internally.
- **Evidently is retained for human-facing HTML drift reports** in the
  local compose stack (a Phase 2 job), where its UI is the value-add and
  API churn is tolerable.

## Consequences

- The gate is deterministic and fully covered by fast unit tests with no
  dependency on Evidently's evolving result schema.
- Two drift surfaces exist (gate vs. report); they must stay
  conceptually aligned (same tests, same thresholds).
- scipy becomes a direct dependency.
