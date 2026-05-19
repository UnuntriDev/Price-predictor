"""``make train`` entrypoint.

End-to-end run: load the Kaggle sale snapshots (ADR 0014), run the
orchestrated training pipeline (validate -> features -> fit -> conformal
-> evaluate -> log+register), and print the promotion recommendation.
Hydra selects the estimator/params; settings supply paths + MLflow.
"""

from __future__ import annotations

import sys
from pathlib import Path

from price_predictor.config import compose_config, configure_logging, get_settings
from price_predictor.data import load_listings
from price_predictor.domain import PricePredictorError
from price_predictor.pipeline import run_training
from price_predictor.registry import MLflowModelRegistry


def main() -> int:
    """Run the end-to-end training pipeline."""
    settings = get_settings()
    configure_logging(settings.logging)
    cfg = compose_config()

    raw_dir = Path(settings.data_dir) / "raw"
    registry = MLflowModelRegistry(settings.mlflow)

    try:
        frame = load_listings(raw_dir).collect()
        if frame.is_empty():
            sys.stdout.write(f"[train] no listings under {raw_dir}; run `make data` first\n")
            return 2
        result = run_training(
            frame,
            registry,
            model_name=settings.api.model_name,
            estimator_name=str(cfg.model.name),
            estimator_params=dict(cfg.model.params),
        )
    except PricePredictorError as exc:
        sys.stdout.write(f"[train] failed: {exc}\n")
        return 2

    sys.stdout.write(
        f"[train] {result.model_version.name} v{result.model_version.version} | "
        f"MAE={result.report.mae:.0f} R2={result.report.r2:.3f} | "
        f"{result.recommendation.reason}\n"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
