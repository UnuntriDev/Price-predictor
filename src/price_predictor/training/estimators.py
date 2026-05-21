"""Single construction path for the regressor — used by trainer + tuner."""

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
    """Return an unfitted estimator (``xgboost`` / ``lightgbm`` / ``catboost``)."""
    try:
        factory = _FACTORIES[name]
    except KeyError as exc:
        known = ", ".join(sorted(_FACTORIES))
        msg = f"unknown estimator {name!r}; known: {known}"
        raise TrainingError(msg) from exc
    return factory(params)
