"""Kaggle CLI wrapper (ADR 0014).

Creds via ``KAGGLE_USERNAME``/``KAGGLE_KEY`` or ``~/.kaggle/kaggle.json``
— same lookup the CLI uses. Any failure → :class:`DataDownloadError`.
"""

from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path

from price_predictor.config import get_logger
from price_predictor.domain import DataDownloadError

_log = get_logger(__name__)

DATASET_SLUG = "krzysztofjamroz/apartment-prices-in-poland"


def credentials_available() -> bool:
    """True if Kaggle creds are reachable."""
    if os.environ.get("KAGGLE_USERNAME") and os.environ.get("KAGGLE_KEY"):
        return True
    cred = Path.home() / ".kaggle" / "kaggle.json"
    if not cred.is_file():
        return False
    try:
        data = json.loads(cred.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return False
    return bool(data.get("username") and data.get("key"))


class KaggleDatasetDownloader:
    """Pulls + unzips the configured dataset."""

    def __init__(self, slug: str = DATASET_SLUG) -> None:
        self._slug = slug

    def download(self, dest: Path) -> Path:
        """Download + unzip into ``dest`` (created if missing)."""
        if not credentials_available():
            msg = (
                "Kaggle credentials not found: set KAGGLE_USERNAME/"
                "KAGGLE_KEY or place ~/.kaggle/kaggle.json"
            )
            raise DataDownloadError(msg)
        dest.mkdir(parents=True, exist_ok=True)
        cmd = [
            "kaggle",
            "datasets",
            "download",
            "-d",
            self._slug,
            "-p",
            str(dest),
            "--unzip",
        ]
        _log.info("kaggle.download.start", slug=self._slug, dest=str(dest))
        try:
            subprocess.run(cmd, check=True, capture_output=True, text=True)
        except FileNotFoundError as exc:
            msg = "kaggle CLI not found on PATH (is the env synced?)"
            raise DataDownloadError(msg) from exc
        except subprocess.CalledProcessError as exc:
            msg = f"kaggle download failed: {exc.stderr.strip() or exc}"
            raise DataDownloadError(msg) from exc
        _log.info("kaggle.download.done", dest=str(dest))
        return dest
