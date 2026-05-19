"""``make scrape`` entrypoint.

Builds the Scrapy runner from settings (with Postgres persistence wired)
and runs the crawl. Requires Chromium (`make browsers`) and a reachable
Postgres; failures are reported cleanly instead of crashing.
"""

from __future__ import annotations

import sys

from price_predictor.config import configure_logging, get_settings
from price_predictor.domain import PricePredictorError
from price_predictor.scraping import ScrapyRunner


def main() -> int:
    """Construct the crawl runner and run it, persisting to Postgres."""
    settings = get_settings()
    configure_logging(settings.logging)
    runner = ScrapyRunner(settings.scraping, postgres=settings.postgres)
    try:
        count = runner.run()
    except PricePredictorError as exc:
        sys.stdout.write(f"[scrape] failed: {exc}\n")
        return 2
    sys.stdout.write(f"[scrape] captured {count} listings\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
