# 13. Otodom __NEXT_DATA__ parsed against a documented assumed contract

- Status: accepted (provisional)
- Date: 2026-05-19

## Context

Per ADR 0006 the spider extracts from Otodom's `__NEXT_DATA__` JSON.
The exact key paths in that payload could not be verified from a real
captured page during this work. Hard-coding unverified paths silently is
unacceptable; blocking all scraping work on a capture is also wasteful.

## Decision

- The mapping from payload -> `domain.Listing` lives in one pure
  function, `scraping.parser.parse_listing`, against an **explicitly
  documented assumed schema** (`props.pageProps.ad.{...}`).
- Any structural mismatch raises `ScrapeError` (fail loud, never guess).
- A synthetic fixture (`tests/unit/scraping/fixtures/next_data_sample.json`)
  encodes the assumed schema and drives unit tests. When a real Otodom
  capture is available, replace the fixture and adjust the single
  mapping function; tests then pin the real contract.

## Consequences

- Scraper structure, validation, DI, and tests are complete now.
- The assumed key paths are a known provisional risk, isolated to one
  function and one fixture — cheap to correct.
- This ADR moves to `accepted` once verified against a real capture.
