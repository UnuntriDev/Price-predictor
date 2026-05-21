"""Runtime config (ADR 0002).

pydantic-settings owns env + secrets; Hydra owns experiment composition.
Env vars use ``PP_`` prefix and ``__`` for nesting (e.g. ``PP_POSTGRES__PASSWORD``).
"""

from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel, Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

from price_predictor.domain.enums import ModelStage

_POSTGRES_DEFAULT_PORT = 5432
_API_DEFAULT_PORT = 8000
_STREAMLIT_DEFAULT_PORT = 7860
_PROMETHEUS_DEFAULT_PORT = 9090


class AppEnv(StrEnum):
    """Where the process runs."""

    LOCAL = "local"
    CI = "ci"
    PROD = "prod"


class PostgresSettings(BaseModel):
    """libpq connection params."""

    host: str = "localhost"
    port: int = Field(default=_POSTGRES_DEFAULT_PORT, ge=1, le=65535)
    user: str = "price_predictor"
    password: SecretStr = SecretStr("change-me")
    database: str = "price_predictor"

    @property
    def dsn(self) -> str:
        """Psycopg v3 conn string (secret revealed)."""
        pwd = self.password.get_secret_value()
        return f"postgresql://{self.user}:{pwd}@{self.host}:{self.port}/{self.database}"


class MLflowSettings(BaseModel):
    """Tracking/registry URIs (ADR 0003 — defaults to local SQLite)."""

    tracking_uri: str = "sqlite:///mlflow.db"
    registry_uri: str | None = None
    experiment_name: str = "price-predictor"


class ScrapingSettings(BaseModel):
    """Polite-crawl knobs for the Otodom spider."""

    base_url: str = "https://www.otodom.pl"
    max_pages: int = Field(default=50, ge=1)
    download_delay_seconds: float = Field(default=2.0, ge=0.0)
    concurrent_requests: int = Field(default=4, ge=1, le=32)
    user_agent: str = "price-predictor-bot/0.1 (+research; contact in repo)"


class APISettings(BaseModel):
    """Inference service bind + model selection."""

    host: str = "0.0.0.0"
    port: int = Field(default=_API_DEFAULT_PORT, ge=1, le=65535)
    streamlit_port: int = Field(default=_STREAMLIT_DEFAULT_PORT, ge=1, le=65535)
    model_name: str = "price-predictor"
    model_stage: ModelStage = ModelStage.PRODUCTION
    workers: int = Field(default=2, ge=1, le=32)


class MonitoringSettings(BaseModel):
    """Drift thresholds + Prometheus port."""

    prometheus_port: int = Field(default=_PROMETHEUS_DEFAULT_PORT, ge=1, le=65535)
    drift_p_value_threshold: float = Field(default=0.05, gt=0.0, lt=1.0)


class LoggingSettings(BaseModel):
    """structlog options."""

    level: str = "INFO"
    json_output: bool = False


class Settings(BaseSettings):
    """Root settings, composed from env + .env."""

    model_config = SettingsConfigDict(
        env_prefix="PP_",
        env_nested_delimiter="__",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    env: AppEnv = AppEnv.LOCAL
    data_dir: str = "data"
    artifacts_dir: str = "artifacts"

    postgres: PostgresSettings = Field(default_factory=PostgresSettings)
    mlflow: MLflowSettings = Field(default_factory=MLflowSettings)
    scraping: ScrapingSettings = Field(default_factory=ScrapingSettings)
    api: APISettings = Field(default_factory=APISettings)
    monitoring: MonitoringSettings = Field(default_factory=MonitoringSettings)
    logging: LoggingSettings = Field(default_factory=LoggingSettings)


def get_settings() -> Settings:
    """Build fresh from env. Not cached — callers own lifetime."""
    return Settings()
