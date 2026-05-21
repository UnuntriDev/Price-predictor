"""Thin wrapper over Hydra's compose API — owns its global state for callers."""

from __future__ import annotations

import os
from collections.abc import Sequence
from pathlib import Path

from hydra import compose, initialize_config_dir
from hydra.core.global_hydra import GlobalHydra
from omegaconf import DictConfig

_ENV_OVERRIDE = "PP_CONFIGS_DIR"


def configs_dir() -> Path:
    """``configs/`` root: ``PP_CONFIGS_DIR`` env var, else repo-relative."""
    override = os.environ.get(_ENV_OVERRIDE)
    if override:
        return Path(override).resolve()
    return Path(__file__).resolve().parents[3] / "configs"


def compose_config(
    overrides: Sequence[str] | None = None,
    *,
    config_name: str = "config",
) -> DictConfig:
    """Compose with dotlist overrides like ``model=lightgbm``."""
    GlobalHydra.instance().clear()
    with initialize_config_dir(version_base=None, config_dir=str(configs_dir())):
        cfg = compose(config_name=config_name, overrides=list(overrides or []))
    assert isinstance(cfg, DictConfig)
    return cfg
