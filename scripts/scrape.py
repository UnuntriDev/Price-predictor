"""``make scrape`` entrypoint.

Builds the Scrapy runner from settings and starts it. The runner raises
a Phase 2 ``NotImplementedError``; this wrapper reports it cleanly.
"""

from __future__ import annotations

import sys

from price_predictor.config import get_settings
from price_predictor.scraping import ScrapyRunner


def main() -> int:
    """Construct the crawl runner and attempt a run."""
    settings = get_settings()
    runner = ScrapyRunner(settings.scraping)
    try:
        count = runner.run()
    except NotImplementedError as exc:
        sys.stdout.write(f"[scrape] not implemented yet: {exc}\n")
        return 2
    sys.stdout.write(f"[scrape] captured {count} listings\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
