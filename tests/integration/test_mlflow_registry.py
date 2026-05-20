"""MLflowModelRegistry round-trip against a temp SQLite store.

No network/docker: SQLite backend + local file artifacts in tmp_path.
Uses the same ``log_and_register`` entrypoint that scripts/train.py
calls in production, so the test exercises the real MLflow 3 path.
"""

from __future__ import annotations

import sys
from pathlib import Path

import mlflow
import numpy as np
import pytest
from mlflow.tracking import MlflowClient
from sklearn.linear_model import LinearRegression

from price_predictor.config.settings import MLflowSettings
from price_predictor.domain import ModelNotFoundError, ModelStage
from price_predictor.registry import MLflowModelRegistry

pytestmark = [
    pytest.mark.integration,
    pytest.mark.skipif(
        sys.platform == "win32",
        reason=(
            "mlflow resolves local artifact URIs via the Windows drive "
            "letter as a scheme ('c:'); Linux CI exercises this path"
        ),
    ),
]


def test_log_and_register_round_trip(tmp_path: Path) -> None:
    tracking_uri = f"sqlite:///{tmp_path.as_posix()}/mlflow.db"
    mlflow.set_tracking_uri(tracking_uri)
    mlflow.set_registry_uri(tracking_uri)

    # Pre-create the experiment with a local artifact location so the
    # default "./mlruns" doesn't leak into the working tree.
    MlflowClient(tracking_uri=tracking_uri).create_experiment(
        "price-predictor", artifact_location=(tmp_path / "artifacts").as_uri()
    )

    model = LinearRegression().fit(
        np.array([[0.0], [1.0], [2.0]]), np.array([0.0, 1.0, 2.0])
    )

    registry = MLflowModelRegistry(MLflowSettings(tracking_uri=tracking_uri))

    mv = registry.log_and_register(model, "price-test", {"mae": 1.23})
    assert mv.name == "price-test"
    assert mv.version == "1"
    assert mv.stage is ModelStage.NONE
    assert mv.metrics["mae"] == 1.23

    promoted = registry.transition_stage("price-test", mv.version, ModelStage.STAGING)
    assert promoted.stage is ModelStage.STAGING

    got = registry.get_version("price-test", ModelStage.STAGING)
    assert got.version == mv.version

    with pytest.raises(ModelNotFoundError):
        registry.get_version("price-test", ModelStage.PRODUCTION)

    loaded = registry.load_model("price-test", ModelStage.STAGING)
    preds = loaded.predict(np.array([[3.0]]))
    assert len(preds) == 1
