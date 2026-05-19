-- Applied by the postgres image on first init (docker-entrypoint-initdb.d).
-- The three tables from the design: scraped listings, served predictions,
-- and a registry mirror. Kept in sync with the domain models.

-- Kaggle "Apartment Prices in Poland" schema (ADR 0014). Monthly panel:
-- the natural key is (id, snapshot_month).
CREATE TABLE IF NOT EXISTS listings (
    id                       TEXT NOT NULL,
    city                     TEXT NOT NULL,
    property_type            TEXT,
    square_meters            DOUBLE PRECISION NOT NULL,
    rooms                    INTEGER NOT NULL,
    floor                    INTEGER,
    floor_count              INTEGER,
    build_year               INTEGER,
    latitude                 DOUBLE PRECISION NOT NULL,
    longitude                DOUBLE PRECISION NOT NULL,
    centre_distance_km       DOUBLE PRECISION NOT NULL,
    poi_count                INTEGER NOT NULL,
    school_distance_km       DOUBLE PRECISION,
    clinic_distance_km       DOUBLE PRECISION,
    post_office_distance_km  DOUBLE PRECISION,
    kindergarten_distance_km DOUBLE PRECISION,
    restaurant_distance_km   DOUBLE PRECISION,
    college_distance_km      DOUBLE PRECISION,
    pharmacy_distance_km     DOUBLE PRECISION,
    ownership                TEXT NOT NULL,
    building_material        TEXT,
    condition                TEXT,
    has_parking              BOOLEAN NOT NULL,
    has_balcony              BOOLEAN NOT NULL,
    has_elevator             BOOLEAN,
    has_security             BOOLEAN NOT NULL,
    has_storage              BOOLEAN NOT NULL,
    price_pln                BIGINT NOT NULL,
    snapshot_month           DATE NOT NULL,
    PRIMARY KEY (id, snapshot_month)
);

CREATE TABLE IF NOT EXISTS predictions (
    id              BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    predicted_price NUMERIC(12, 2) NOT NULL,
    interval_low    NUMERIC(12, 2),
    interval_high   NUMERIC(12, 2),
    model_name      TEXT NOT NULL,
    model_version   TEXT NOT NULL,
    predicted_at    TIMESTAMPTZ NOT NULL,
    request         JSONB NOT NULL
);

CREATE TABLE IF NOT EXISTS model_versions (
    name       TEXT NOT NULL,
    version    TEXT NOT NULL,
    stage      TEXT NOT NULL,
    run_id     TEXT NOT NULL,
    metrics    JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL,
    PRIMARY KEY (name, version)
);

CREATE INDEX IF NOT EXISTS idx_predictions_predicted_at
    ON predictions (predicted_at);
CREATE INDEX IF NOT EXISTS idx_listings_city_snapshot
    ON listings (city, snapshot_month);
