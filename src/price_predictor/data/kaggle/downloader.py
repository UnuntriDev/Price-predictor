"""Kaggle dataset downloader (ADR 0014).

Wraps the Kaggle CLI. Credentials are resolved the way the CLI itself
does: ``~/.kaggle/kaggle.json`` or the ``KAGGLE_USERNAME`` /
``KAGGLE_KEY`` environment variables. Missing creds or a CLI failure
surface as :class:`DataDownloadError`.
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
    """Return True if Kaggle creds are discoverable."""
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
    """Downloads and unzips the apartment-prices dataset.

    Args:
        slug: Kaggle ``owner/dataset`` identifier.
    """

    def __init__(self, slug: str = DATASET_SLUG) -> None:
        self._slug = slug

    def download(self, dest: Path) -> Path:
        """Download + unzip the dataset into ``dest``.

        Args:
            dest: Target directory (created if absent).

        Returns:
            ``dest``.

        Raises:
            DataDownloadError: If creds are missing or the CLI fails.
        """
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
