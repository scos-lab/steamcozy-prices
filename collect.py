#!/usr/bin/env python3
"""Sample current Steam prices for the watchlist and write one CSV per run.

Runs on GitHub Actions (stdlib only, no pip installs). Data source is Steam's
public storefront API (appdetails, price_overview filter, batched). Output:
data/<YYYY-MM>/<YYYY-MM-DD_HHMM>.csv with header
appid,currency,initial,final,discount_pct,is_free

Prices are in minor units (cents) for US region (cc=us). A row per watchlist
game that returned successfully; delisted games are skipped. 429s retry with
backoff (GitHub runner IPs are shared, Steam may throttle).
"""
import csv
import json
import time
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent
BATCH = 80
PAUSE = 1.0
# 8 representative Steam pricing regions (Steam prices vary per region).
# us kept first = column-compat with pre-2026-07-11 single-region files.
REGIONS = ["us", "de", "gb", "au", "ca", "jp", "br", "cn"]


def fetch(appids, cc):
    url = ("https://store.steampowered.com/api/appdetails?appids="
           + ",".join(map(str, appids)) + f"&filters=price_overview&cc={cc}")
    req = urllib.request.Request(url, headers={"User-Agent": "steamcozy-prices/1.0"})
    for attempt in range(4):
        try:
            with urllib.request.urlopen(req, timeout=30) as r:
                return json.load(r)
        except Exception as e:
            code = getattr(e, "code", None)
            if attempt == 3:
                raise
            time.sleep(10 * (attempt + 1) if code == 429 else 5)
    return {}


def main():
    watchlist = json.loads((ROOT / "watchlist.json").read_text())
    now = datetime.now(timezone.utc)
    out = ROOT / "data" / f"{now:%Y-%m}" / f"{now:%Y-%m-%d_%H%M}.csv"
    out.parent.mkdir(parents=True, exist_ok=True)
    n = 0
    with out.open("w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["appid", "cc", "currency", "initial", "final", "discount_pct", "is_free"])
        for cc in REGIONS:
            for i in range(0, len(watchlist), BATCH):
                chunk = watchlist[i:i + BATCH]
                for appid_s, entry in sorted(fetch(chunk, cc).items(), key=lambda kv: int(kv[0])):
                    if not entry.get("success"):
                        continue
                    data = entry.get("data")
                    if isinstance(data, list) and not data:  # free games return []
                        w.writerow([appid_s, cc, "", 0, 0, 0, 1])
                        n += 1
                        continue
                    po = (data or {}).get("price_overview")
                    if not po:
                        continue
                    w.writerow([appid_s, cc, po.get("currency"), po.get("initial"),
                                po.get("final"), po.get("discount_percent"), 0])
                    n += 1
                time.sleep(PAUSE)
    print(f"{out.relative_to(ROOT)}: {n} rows across {len(REGIONS)} regions")


if __name__ == "__main__":
    main()
