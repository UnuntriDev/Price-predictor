"""``make train`` entrypoint.

Wires the Hydra config to the training skeleton. The trainer raises a
Phase 2 ``NotImplementedError``; this wrapper turns that into a clean,
non-crashing message so the command is self-documenting.
"""

from __future__ import annotations

import sys

import polars as pl

from price_predictor.config import compose_config
from price_predictor.training import GradientBoostingTrainer


def main() -> int:
    """Compose config and hand off to the trainer skeleton."""
    cfg = compose_config()
    trainer = GradientBoostingTrainer(
        estimator_name=str(cfg.model.name),
        params=dict(cfg.model.params),
    )
    try:
        trainer.train(pl.DataFrame(), pl.Series("price", []))
    except NotImplementedError as exc:
        sys.stdout.write(f"[train] not implemented yet: {exc}\n")
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
