"""Estimator factory.

Maps the Hydra ``model.name`` key to a concrete scikit-learn-compatible
regressor. Centralised so the trainer, tuner, and tests agree on exactly
one construction path.
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from price_predictor.domain import TrainingError


def _xgboost(params: dict[str, Any]) -> Any:
    from xgboost import XGBRegressor

    return XGBRegressor(**params)


def _lightgbm(params: dict[str, Any]) -> Any:
    from lightgbm import LGBMRegressor

    return LGBMRegressor(**params)


def _catboost(params: dict[str, Any]) -> Any:
    from catboost import CatBoostRegressor

    return CatBoostRegressor(**params)


_FACTORIES: dict[str, Callable[[dict[str, Any]], Any]] = {
    "xgboost": _xgboost,
    "lightgbm": _lightgbm,
    "catboost": _catboost,
}


def build_estimator(name: str, params: dict[str, Any]) -> Any:
    """Construct an unfitted regressor by name.

    Args:
        name: One of ``xgboost`` / ``lightgbm`` / ``catboost``.
        params: Keyword arguments forwarded to the estimator.

    Returns:
        The unfitted estimator instance.

    Raises:
        TrainingError: If ``name`` is not a known estimator.
    """
    try:
        factory = _FACTORIES[name]
    except KeyError as exc:
        known = ", ".join(sorted(_FACTORIES))
        msg = f"unknown estimator {name!r}; known: {known}"
        raise TrainingError(msg) from exc
    return factory(params)
