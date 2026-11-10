"""
    python download_bsp.py                        # last 30 days
    python download_bsp.py --start 2026-01-01     # from a date up to yesterday
"""

import argparse
import time
import urllib.error
import urllib.request
from datetime import date, timedelta
from pathlib import Path

BASE_URL = "https://promo.betfair.com/betfairsp/prices/"
OUT_DIR = Path(__file__).parent / "data" / "raw"
MISSING_LOG = OUT_DIR / "_missing.txt"
DELAY_SECONDS = 1.0  # adding pausing between reqs to not batter betfair
RECENT_DAYS = 3 


def filename(market: str, day: date) -> str:
    return f"dwbfgreyhound{market}{day:%d%m%Y}.csv"


def fetch(name: str) -> bytes | None:
    """Return the file's bytes, or None if Betfair has no file for that day."""
    request = urllib.request.Request(
        BASE_URL + name, headers={"User-Agent": "bsp-downloader/1.0"}
    )
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            body = response.read()
    except urllib.error.HTTPError as error:
        if error.code == 404:
            return None
        raise
    if not body[:8].lower().startswith(b"event_id"):
        raise ValueError(f"{name}: response is not a BSP csv")
    return body


def main() -> None:
    yesterday = date.today() - timedelta(days=1)
    parser = argparse.ArgumentParser(description=__doc__.strip().splitlines()[0])
    parser.add_argument("--start", type=date.fromisoformat,
                        default=yesterday - timedelta(days=29), help="YYYY-MM-DD")
    parser.add_argument("--end", type=date.fromisoformat,
                        default=yesterday, help="YYYY-MM-DD")
    parser.add_argument("--markets", nargs="+", choices=["win", "place"],
                        default=["win", "place"])
    args = parser.parse_args()

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    missing = set(MISSING_LOG.read_text().split()) if MISSING_LOG.exists() else set()

    downloaded = skipped = unavailable = 0
    day = args.start
    while day <= args.end:
        for market in args.markets:
            name = filename(market, day)
            target = OUT_DIR / name
            if target.exists() or name in missing:
                skipped += 1
                continue

            try:
                body = fetch(name)
            except Exception as error:  # report and stop
                print(f"stopped at {name}: {error}")
                print(f"downloaded {downloaded}, skipped {skipped}, unavailable {unavailable}")
                raise SystemExit(1)

            if body is None:
                unavailable += 1
                print(f"no file   {name}")
                if (date.today() - day).days > RECENT_DAYS:
                    with MISSING_LOG.open("a") as log:
                        log.write(name + "\n")
            else:
                partial = target.with_suffix(".part")
                partial.write_bytes(body)
                partial.rename(target)
                downloaded += 1
                print(f"saved     {name}  ({len(body) / 1024:.0f} KB)")
            time.sleep(DELAY_SECONDS)
        day += timedelta(days=1)

    print(f"downloaded {downloaded}, skipped {skipped}, unavailable {unavailable}")


if __name__ == "__main__":
    main()
