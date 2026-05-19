"""MLflowModelRegistry round-trip against a temp SQLite store.

No network/docker: SQLite backend + local file artifacts in tmp_path.
"""

from __future__ import annotations

import sys
from pathlib import Path

import mlflow
import mlflow.sklearn
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


def test_register_transition_get_and_load(tmp_path: Path) -> None:
    tracking_uri = f"sqlite:///{tmp_path.as_posix()}/mlflow.db"
    mlflow.set_tracking_uri(tracking_uri)
    client = MlflowClient(tracking_uri=tracking_uri)
    exp_id = client.create_experiment(
        "reg-test", artifact_location=(tmp_path / "artifacts").as_uri()
    )

    model = LinearRegression().fit(np.array([[0.0], [1.0], [2.0]]), np.array([0.0, 1.0, 2.0]))
    with mlflow.start_run(experiment_id=exp_id) as run:
        mlflow.sklearn.log_model(model, artifact_path="model")
        run_id = run.info.run_id

    registry = MLflowModelRegistry(MLflowSettings(tracking_uri=tracking_uri))

    mv = registry.register(run_id, "price-test", {"mae": 1.23})
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
