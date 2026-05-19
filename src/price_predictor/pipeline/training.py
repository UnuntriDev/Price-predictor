"""End-to-end training orchestration.

Wires the verified building blocks into one flow:

    validate -> split -> fit features -> fit estimator -> conformal
    calibrate -> evaluate -> log+register -> promotion recommendation

Everything is injected (the listings frame and the registry), so this
runs as a fast unit test with a fake registry and as a real run against
MLflow with no code change.
"""

from __future__ import annotations

from typing import Any

import numpy as np
import polars as pl
from pydantic import BaseModel, ConfigDict
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder

from price_predictor.data import PanderaListingValidator
from price_predictor.domain import ModelNotFoundError, ModelStage, TrainingError
from price_predictor.domain.model_version import ModelVersion
from price_predictor.features import PriceFeaturePipeline
from price_predictor.pipeline.artifact import ConformalModel
from price_predictor.registry.ports import ModelRegistry
from price_predictor.registry.promotion import (
    PromotionRecommendation,
    recommend_promotion,
)
from price_predictor.training import (
    ConformalRegressor,
    RegressionEvaluator,
    RegressionReport,
    build_estimator,
)

_CATEGORICAL = ["city", "property_type", "ownership", "building_material", "condition"]


class TrainingRunResult(BaseModel):
    """Outcome of one orchestrated training run."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    report: RegressionReport
    model_version: ModelVersion
    recommendation: PromotionRecommendation


def _split(
    n: int, test_size: float, calibration_size: float, seed: int
) -> tuple[list[int], list[int], list[int]]:
    order = np.random.default_rng(seed).permutation(n)
    n_test = round(n * test_size)
    n_cal = round(n * calibration_size)
    if min(n - n_test - n_cal, n_cal, n_test) <= 0:
        msg = f"cannot split {n} rows into train/cal/test with given sizes"
        raise TrainingError(msg)
    test_idx = order[:n_test].tolist()
    cal_idx = order[n_test : n_test + n_cal].tolist()
    train_idx = order[n_test + n_cal :].tolist()
    return train_idx, cal_idx, test_idx


def run_training(
    listings: pl.DataFrame,
    registry: ModelRegistry,
    *,
    model_name: str,
    estimator_name: str = "xgboost",
    estimator_params: dict[str, Any] | None = None,
    alpha: float = 0.1,
    test_size: float = 0.2,
    calibration_size: float = 0.2,
    seed: int = 42,
    primary_metric: str = "mae",
) -> TrainingRunResult:
    """Train, calibrate, register, and recommend in one call.

    Args:
        listings: Raw listings frame (must satisfy ``RawListingSchema``).
        registry: Where the artifact is logged + registered.
        model_name: Registered model name.
        estimator_name: xgboost / lightgbm / catboost.
        estimator_params: Estimator hyper-parameters.
        alpha: Conformal miscoverage rate.
        test_size: Hold-out test fraction.
        calibration_size: Conformal calibration fraction.
        seed: Split seed.
        primary_metric: Metric the promotion gate hinges on.

    Returns:
        The run result (metrics, registered version, recommendation).

    Raises:
        TrainingError: If the data cannot be split.
        SchemaValidationError: If the frame violates the contract.
    """
    valid = PanderaListingValidator().validate(listings)
    train_idx, cal_idx, test_idx = _split(valid.height, test_size, calibration_size, seed)
    train_df, cal_df, test_df = valid[train_idx], valid[cal_idx], valid[test_idx]

    features = PriceFeaturePipeline().fit(train_df)

    def _xy(frame: pl.DataFrame) -> tuple[Any, Any]:
        x = features.transform(frame).to_pandas()
        y = frame["price_pln"].to_numpy().astype(np.float64)
        return x, y

    x_train, y_train = _xy(train_df)
    x_cal, y_cal = _xy(cal_df)
    x_test, y_test = _xy(test_df)

    estimator = Pipeline(
        [
            (
                "prep",
                ColumnTransformer(
                    [
                        (
                            "cat",
                            OneHotEncoder(handle_unknown="ignore", sparse_output=False),
                            _CATEGORICAL,
                        )
                    ],
                    remainder="passthrough",
                ),
            ),
            ("model", build_estimator(estimator_name, estimator_params or {})),
        ]
    )
    estimator.fit(x_train, y_train)

    conformal = ConformalRegressor(estimator, alpha=alpha).calibrate(x_cal, y_cal)
    report = RegressionEvaluator().evaluate(
        pl.Series("y", y_test),
        pl.Series("p", np.asarray(estimator.predict(x_test), dtype=np.float64)),
    )

    artifact = ConformalModel(features, estimator, conformal.q)
    version = registry.log_and_register(artifact, model_name, report.as_metrics())

    try:
        incumbent = registry.get_version(model_name, ModelStage.PRODUCTION)
        incumbent_metrics: dict[str, float] | None = (
            incumbent.metrics if primary_metric in incumbent.metrics else None
        )
    except ModelNotFoundError:
        incumbent_metrics = None

    recommendation = recommend_promotion(
        report.as_metrics(), incumbent_metrics, primary=primary_metric
    )
    return TrainingRunResult(report=report, model_version=version, recommendation=recommendation)
