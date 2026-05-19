"""``make scrape`` entrypoint (inactive).

Otodom scraping is disabled (DataDome anti-bot; ADR 0013 superseded by
ADR 0014). The data source is the Kaggle dataset — use ``make data``.
This wrapper reports that clearly instead of attempting a crawl.
"""

from __future__ import annotations

import sys


def main() -> int:
    """Explain that scraping is inactive and point to `make data`."""
    sys.stdout.write(
        "[scrape] disabled: Otodom DataDome anti-bot (ADR 0013/0014).\n"
        "[scrape] the data source is the Kaggle dataset - run `make data`.\n"
    )
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
