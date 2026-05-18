"""Runtime configuration via pydantic-settings.

Responsibility split (see ADR 0002): **pydantic-settings owns the
deployment environment and secrets** (DB credentials, ports, URIs);
**Hydra owns experiment/pipeline composition** (model choice, search
spaces, data paths). They never read each other's sources.

All variables use the ``PP_`` prefix and ``__`` to descend into nested
groups, e.g. ``PP_POSTGRES__PASSWORD``.
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
    """Deployment environment the process is running in."""

    LOCAL = "local"
    CI = "ci"
    PROD = "prod"


class PostgresSettings(BaseModel):
    """Connection parameters for the application Postgres instance."""

    host: str = "localhost"
    port: int = Field(default=_POSTGRES_DEFAULT_PORT, ge=1, le=65535)
    user: str = "price_predictor"
    password: SecretStr = SecretStr("change-me")
    database: str = "price_predictor"

    @property
    def dsn(self) -> str:
        """Return a psycopg v3 connection string with the secret revealed."""
        pwd = self.password.get_secret_value()
        return f"postgresql://{self.user}:{pwd}@{self.host}:{self.port}/{self.database}"


class MLflowSettings(BaseModel):
    """MLflow tracking/registry configuration.

    Defaults to a local SQLite store; docker-compose overrides the URI to
    point at the Postgres service (see ADR 0003).
    """

    tracking_uri: str = "sqlite:///mlflow.db"
    registry_uri: str | None = None
    experiment_name: str = "price-predictor"


class ScrapingSettings(BaseModel):
    """Polite-crawl parameters for the Otodom spider."""

    base_url: str = "https://www.otodom.pl"
    max_pages: int = Field(default=50, ge=1)
    download_delay_seconds: float = Field(default=2.0, ge=0.0)
    concurrent_requests: int = Field(default=4, ge=1, le=32)
    user_agent: str = "price-predictor-bot/0.1 (+research; contact in repo)"


class APISettings(BaseModel):
    """FastAPI inference service binding and model selection."""

    host: str = "0.0.0.0"
    port: int = Field(default=_API_DEFAULT_PORT, ge=1, le=65535)
    streamlit_port: int = Field(default=_STREAMLIT_DEFAULT_PORT, ge=1, le=65535)
    model_name: str = "price-predictor"
    model_stage: ModelStage = ModelStage.PRODUCTION
    workers: int = Field(default=2, ge=1, le=32)


class MonitoringSettings(BaseModel):
    """Drift detection and metrics exposure."""

    prometheus_port: int = Field(default=_PROMETHEUS_DEFAULT_PORT, ge=1, le=65535)
    drift_p_value_threshold: float = Field(default=0.05, gt=0.0, lt=1.0)


class LoggingSettings(BaseModel):
    """Structured logging behaviour."""

    level: str = "INFO"
    json_output: bool = False


class Settings(BaseSettings):
    """Top-level application settings, composed from the environment."""

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
    """Build a fresh :class:`Settings` from the current environment.

    Returns:
        A populated settings instance. Not cached: tests and the eventual
        DI container should own lifetime, not a module-level singleton.
    """
    return Settings()
