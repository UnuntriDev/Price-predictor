# 6. Extract Otodom data from __NEXT_DATA__, not the DOM

- Status: accepted
- Date: 2026-05-19

## Context

Otodom is a Next.js app. Listing facts can be scraped either by parsing
rendered HTML (CSS/XPath selectors) or by reading the server-state JSON
that Next.js embeds in the `__NEXT_DATA__` script tag and hydrates the
page from.

## Decision

The spider extracts from the `__NEXT_DATA__` JSON payload. Playwright is
used only to obtain the fully rendered page (anti-bot, lazy chunks); the
data itself comes from the embedded JSON, not DOM selectors.

## Consequences

- Far more robust to cosmetic markup changes; selectors don't rot.
- Parsing is a typed JSON traversal that maps cleanly onto
  `domain.Listing`.
- Risk shifts to Next.js data-shape changes — handled by validating the
  parsed payload through `data.schemas.ListingFrame` so breakage fails
  loudly, not silently.
