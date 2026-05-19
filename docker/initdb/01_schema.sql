-- Applied by the postgres image on first init (docker-entrypoint-initdb.d).
-- The three tables from the design: scraped listings, served predictions,
-- and a registry mirror. Kept in sync with the domain models.

CREATE TABLE IF NOT EXISTS listings (
    listing_id    TEXT PRIMARY KEY,
    source_url    TEXT NOT NULL,
    scraped_at    TIMESTAMPTZ NOT NULL,
    price         NUMERIC(12, 2) NOT NULL,
    area          DOUBLE PRECISION NOT NULL,
    rooms         INTEGER NOT NULL,
    city          TEXT NOT NULL,
    district      TEXT NOT NULL,
    year_built    INTEGER NOT NULL,
    floor         INTEGER NOT NULL,
    property_type TEXT NOT NULL
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
CREATE INDEX IF NOT EXISTS idx_listings_city_district
    ON listings (city, district);
