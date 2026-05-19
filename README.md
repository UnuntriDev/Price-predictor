# PricePredictor

**End-to-end MLOps pipeline that predicts Polish apartment prices from
the public Kaggle dataset** — versioned data, validated contracts,
training with conformal intervals and experiment tracking, a
registry-backed inference API, a Streamlit demo, and drift monitoring.
Built to portfolio quality: strict typing, Protocol-first interfaces,
dependency injection, and a reproducible toolchain.

> **Status: Phase 2 — implemented.** The loop runs end to end:
> `make data → train (+ conformal) → MLflow register → serve /predict
> → drift gate + Evidently report`. Strict typing, tests, and CI are
> green. Scraping is retained only as an inactive illustrative skeleton
> (see Data Source & Ethics).

## Data Source & Ethics

Direct scraping of Polish real estate portals (Otodom, OLX) was
initially planned but proved infeasible due to aggressive anti-bot
protection (DataDome). The project pivoted to using a public Kaggle
dataset (Apartment Prices in Poland, krzysztofjamroz) which actually
provides richer features (POI distances, building condition) than basic
scraping would yield. The scraping module remains in the codebase as an
illustrative skeleton showing the architectural pattern, but is not
active in the data pipeline. This is a deliberate trade-off prioritizing
reproducibility and focus on MLOps over scraping engineering.

Fetch the data on demand (Kaggle token required; CSVs are never
committed, they are DVC-tracked):

```bash
make data        # kaggle download -> data/raw + dvc add
make data-push   # upload to the MinIO/S3 DVC remote
```

---

## Architecture

```mermaid
flowchart LR
    subgraph Acquire
        KG[Kaggle dataset] -->|kaggle CLI + DVC| LD[data.kaggle loader]
        LD --> VAL[data: Pandera RawListingSchema]
    end
    subgraph Learn
        VAL --> FE[features]
        FE --> TR[training: xgb/lgbm/catboost + optuna + conformal]
        TR --> ML[(MLflow tracking)]
        TR --> REG[registry: MLflow Model Registry]
    end
    subgraph Serve
        REG --> API[serving: FastAPI /predict]
        API --> UI[ui: Streamlit]
    end
    subgraph Observe
        API --> PROM[monitoring: Prometheus]
        VAL --> EV[monitoring: KS+PSI gate / Evidently HTML]
        PROM --> GRAF[Grafana]
    end

    CFG[[config: pydantic-settings + Hydra]] -.-> SP & FE & TR & API
    DOM[[domain: Pydantic contracts]] -.-> VAL & TR & API
```

Layers depend on **ports** (`typing.Protocol`) and **contracts**
(`domain` Pydantic models, `data.schemas` Pandera schema), never on each
other's concrete adapters. `serving.asgi.get_app` is the only
composition root. See [`docs/decisions/`](docs/decisions/) for the ADRs.

## Quickstart

```bash
uv sync                 # locked environment (Python 3.12)
make check              # ruff + mypy --strict + pytest + pre-commit
make serve              # FastAPI at :8000  (GET /health, /metrics)
make ui                 # Streamlit at :7860
make up                 # full local stack (pg/mlflow/prometheus/grafana)
```

`make help` lists every target.

## Definition of done (Phase 1)

All green on a clean clone:

```bash
uv sync
uv run ruff check . && uv run ruff format --check .
uv run mypy src/
uv run pytest
docker compose config
pre-commit run --all-files
```

Plus a green GitHub Actions run (`.github/workflows/ci.yml`).

## Deployment trade-offs

The public demo is a **single Hugging Face Space** (Docker SDK): one
image, supervisord running Streamlit on `:7860` (public) and FastAPI on
`:8000` (internal, called over localhost). It serves a
**model-from-registry** only — no scraping, training, or persistence.

Postgres, MLflow, Prometheus, and Grafana run **only** in the local
`docker-compose.yml`. A Space is one container with one public port;
shipping a database and an observability stack there would be wrong, so
the heavy stack stays local by design. `docker-compose.spaces.yml`
reproduces the exact Space image locally. Rationale:
[ADR 0004](docs/decisions/0004-single-hf-spaces-image.md).

## Layout

```
src/price_predictor/   domain · config · scraping · data · features
                       training · registry · serving · monitoring · ui
configs/               Hydra groups (paths/data/model/training)
docker/                multi-stage Dockerfiles, supervisord, prometheus
docs/decisions/        ADRs
tests/unit + tests/integration   mirror src/
```

## Modelled fields

Target `price_pln`. Numeric: `square_meters`, `rooms`, `floor`,
`floor_count`, `build_year`, `centre_distance_km`, `poi_count` + 7 POI
distances. Categorical: `city`, `property_type`, `ownership`,
`building_material`, `condition`. Boolean: `has_*`. Bounds live in
`domain.constants`, shared by the Pydantic `Listing` and the Pandera
`RawListingSchema` so they cannot drift (ADR 0014).

## Phase 2 — implemented

Design decisions are recorded in [ADRs 0006–0014](docs/decisions/).
Run the loop:

```bash
make up                # pg / mlflow / prometheus / grafana / api / ui / minio
make data              # Kaggle download -> data/raw + dvc add
make train             # data -> features -> fit -> conformal -> MLflow
make serve             # /predict: price + conformal interval
make drift             # KS+PSI gate + Evidently HTML report
```

- **Data** — Kaggle "Apartment Prices in Poland" via the Kaggle CLI;
  loader merges monthly sale snapshots, normalises, Pandera-validated;
  DVC-tracked on an S3-compatible MinIO remote (ADR 0009/0014).
- **Features** — median/sentinel imputation + feature selection;
  leakage-aware (target/ids never emitted).
- **Training** — `run_training` orchestrates validate→split→features→
  fit→**conformal**→evaluate→MLflow `log_and_register`; Optuna tuner.
- **Registry** — manual promotion gate with an automated
  `recommend_promotion` (promote/hold + metric delta).
- **Serving** — real `/predict` returns price + conformal interval;
  the artifact is loaded from the registry at startup.
- **Monitoring** — KS+PSI drift gate (deterministic) plus the Evidently
  HTML report job (ADR 0012).
- **Scraping** — inactive illustrative skeleton only (ADR 0013/0014;
  Otodom DataDome anti-bot).

**Not wired:** the HF-Space-pulls-from-remote-registry deploy (ADR
0011) remains an infra follow-up.

## License

MIT — see [LICENSE](LICENSE).
