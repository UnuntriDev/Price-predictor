# 14. Use a Kaggle dataset as the primary data source

- Status: accepted
- Date: 2026-05-19
- Supersedes: [ADR 0006](0006-otodom-next-data-extraction.md),
  [ADR 0013](0013-assumed-next-data-contract.md)

## Context

Direct scraping of Polish real-estate portals (Otodom, OLX) was the
original plan (ADR 0006/0013). In practice Otodom is behind **DataDome**
anti-bot, which serves a JS shell page with no `__NEXT_DATA__` payload
to non-browser / automated clients. Defeating commercial anti-bot is a
scraping-engineering rabbit hole that adds no MLOps value and would make
the pipeline non-reproducible for reviewers.

## Decision

The primary data source is the public Kaggle dataset **"Apartment
Prices in Poland"** (`krzysztofjamroz/apartment-prices-in-poland`):
195k+ listings, 15 cities, 28 columns, monthly snapshots
2023-08 → 2024-06 (11 sale files).

- Data is fetched on demand via the Kaggle CLI (`make data`) and tracked
  with DVC; CSVs are never committed.
- The scraping module stays as an illustrative architectural skeleton,
  decoupled from the data model and inactive in the pipeline.

### Modelled features / target (this ADR is the source of truth)

- **Target:** `price_pln` (int, PLN).
- **Numeric:** `square_meters`, `rooms`, `floor`, `floor_count`,
  `build_year`, `centre_distance_km`, `poi_count`, and the seven POI
  distances (school/clinic/post_office/kindergarten/restaurant/college/
  pharmacy). Missing values are median-imputed in the feature pipeline.
- **Categorical:** `city`, `property_type`, `ownership`,
  `building_material`, `condition` (one-hot, unknowns ignored).
- **Boolean:** `has_parking`, `has_balcony`, `has_elevator`,
  `has_security`, `has_storage` (missing → False).
- Conformal intervals and the promotion gate are unchanged.

## Consequences

- **Reproducible**: anyone with a Kaggle token gets identical data;
  DVC pins the exact snapshot used by a model.
- **Richer features** than raw scraping would yield: geocoordinates,
  centre distance, POI proximity, building condition.
- Focus stays on MLOps, not anti-bot engineering.
- High missingness in some columns (`condition` 74.8%,
  `buildingMaterial` 39.6%, `type` 21.6%, `floor` 17.7%, `buildYear`
  16.5%, `hasElevator` 5%) is handled by nullable schema fields +
  imputation, not row drops.
- Trade-off accepted deliberately: reproducibility and MLOps focus over
  live-data realism.
