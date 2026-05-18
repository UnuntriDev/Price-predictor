"""Hydra composition helper.

Hydra owns *experiment* configuration (which model, which search space,
which data window). This module wraps Hydra's compose API so callers get
a plain, typed-at-the-edge ``DictConfig`` without each entrypoint having
to manage Hydra's global state.
"""

from __future__ import annotations

import os
from collections.abc import Sequence
from pathlib import Path

from hydra import compose, initialize_config_dir
from hydra.core.global_hydra import GlobalHydra
from omegaconf import DictConfig

_ENV_OVERRIDE = "PP_CONFIGS_DIR"


def configs_dir() -> Path:
    """Locate the top-level ``configs/`` directory.

    Resolution order: the ``PP_CONFIGS_DIR`` env var (set in containers),
    then the repo-root ``configs/`` inferred from this file's location.

    Returns:
        Absolute path to the Hydra config root.
    """
    override = os.environ.get(_ENV_OVERRIDE)
    if override:
        return Path(override).resolve()
    return Path(__file__).resolve().parents[3] / "configs"


def compose_config(
    overrides: Sequence[str] | None = None,
    *,
    config_name: str = "config",
) -> DictConfig:
    """Compose a Hydra configuration tree.

    Args:
        overrides: Hydra dotlist overrides, e.g. ``["model=lightgbm"]``.
        config_name: Root config file name (without extension).

    Returns:
        The composed configuration.
    """
    GlobalHydra.instance().clear()
    with initialize_config_dir(version_base=None, config_dir=str(configs_dir())):
        cfg = compose(config_name=config_name, overrides=list(overrides or []))
    assert isinstance(cfg, DictConfig)
    return cfg
