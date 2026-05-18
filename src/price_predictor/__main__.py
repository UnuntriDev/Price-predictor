"""Command-line entrypoint for the PricePredictor package.

Phase 1 exposes only a version probe so the console script resolves on a
clean install. Real subcommands (scrape/train/serve) arrive in Phase 2.
"""

from __future__ import annotations

import sys

from price_predictor import __version__


def main(argv: list[str] | None = None) -> int:
    """Run the PricePredictor CLI.

    Args:
        argv: Optional argument vector. Defaults to ``sys.argv[1:]``.

    Returns:
        Process exit code.
    """
    args = sys.argv[1:] if argv is None else argv
    if args and args[0] in {"-V", "--version"}:
        sys.stdout.write(f"price-predictor {__version__}\n")
        return 0
    sys.stdout.write(
        "price-predictor (Phase 1 skeleton). "
        "Subcommands land in Phase 2; see the Makefile for entrypoints.\n"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
