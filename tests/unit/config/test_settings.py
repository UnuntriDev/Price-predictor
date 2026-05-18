"""Settings load from defaults and the environment without leaking secrets."""

from __future__ import annotations

import pytest

from price_predictor.config import AppEnv, get_settings


def test_defaults(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("PP_ENV", raising=False)
    settings = get_settings()
    assert settings.env is AppEnv.LOCAL
    assert settings.postgres.port == 5432
    assert settings.api.streamlit_port == 7860
    assert settings.mlflow.tracking_uri.startswith("sqlite:///")


def test_nested_env_override(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("PP_ENV", "prod")
    monkeypatch.setenv("PP_POSTGRES__PASSWORD", "s3cret")
    monkeypatch.setenv("PP_API__PORT", "9001")
    settings = get_settings()
    assert settings.env is AppEnv.PROD
    assert settings.api.port == 9001
    assert settings.postgres.password.get_secret_value() == "s3cret"


def test_secret_not_in_repr(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("PP_POSTGRES__PASSWORD", "topsecret")
    settings = get_settings()
    assert "topsecret" not in repr(settings)
    assert "topsecret" in settings.postgres.dsn  # explicit reveal only
