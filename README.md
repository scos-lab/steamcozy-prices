# steamcozy-prices

Daily Steam price samples for ~5,000 games, collected for
[SteamCozy](https://steamcozy.com) — a game knowledge & discovery site.

## What this is

A [git-scraping](https://simonwillison.net/2020/Oct/9/git-scraping/) price
tracker: a scheduled GitHub Action samples current prices from Steam's public
storefront API twice a day and commits one CSV per run. The git history *is*
the price history.

- **Coverage**: `watchlist.json` — top ~5,000 Steam games by review count,
  plus games featured on SteamCozy.
- **Cadence**: 06:17 and 18:17 UTC daily (tracking began 2026-07-11).
- **Format**: `data/<YYYY-MM>/<YYYY-MM-DD_HHMM>.csv` with
  `appid,cc,currency,initial,final,discount_pct,is_free` — minor units per region currency.
  Regions sampled: us, de, gb, au, ca, jp, br, cn (files before 2026-07-11 12:00 UTC are us-only, 6 columns).

## Honest-data notes

- Price data comes from Steam's public storefront API; this repo simply
  snapshots it. Games delisted at sample time are skipped, not zero-filled.
- History starts at the tracking epoch (2026-07-11). Any "lowest price"
  statement derived from this data means *lowest since tracking began* —
  it is **not** an all-time low claim.

Not affiliated with Valve Corporation. Code is MIT licensed; the sampled
numbers are facts from a public API.

Questions: suggest@steamcozy.com
