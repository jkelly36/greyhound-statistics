import json
from pathlib import Path

import polars as pl

ROOT = Path(__file__).parent
RAW_DIR = ROOT / "data" / "raw"
OUT_DIR = ROOT / "site" / "data"


def load_winners() -> pl.DataFrame:
    files = sorted(RAW_DIR.glob("dwbfgreyhoundwin*.csv"))
    if not files:
        raise SystemExit(f"no win files in {RAW_DIR} - run download_bsp.py first")

    runners = (
        pl.concat(
            [pl.read_csv(f, infer_schema_length=None) for f in files],
            how="vertical_relaxed",
        )
        .unique(subset=["event_id", "selection_id"])
        .with_columns(
            pl.col("event_dt").str.to_datetime("%d-%m-%Y %H:%M").alias("off"),
            # Hove 7th Nov -> Hove, 
            # Bendigo (AUS) 7th Nov -> "Bendigo (AUS)"
            pl.col("menu_hint")
            .str.replace(r"\s+\d{1,2}(st|nd|rd|th)\s+\w{3}$", "")
            .alias("track"),
        )
    )

    return (
        runners.filter(pl.col("win_lose") == 1)
        .sort("selection_name")
        .group_by("event_id")
        .agg(
            pl.col("off").first(),
            pl.col("track").first(),
            pl.col("event_name").first().alias("race"),
            pl.col("selection_name").str.join(" / ").alias("winner"),
            pl.col("bsp")
            .map_elements(lambda price: f"{price:.2f}", return_dtype=pl.String)
            .str.join(" / ")
            .alias("bsp"),
        )
        .sort("off", "track")
    )


def main() -> None:
    winners = load_winners().with_columns(
        pl.col("off").dt.strftime("%Y-%m-%d").alias("day"),
        pl.col("off").dt.strftime("%H:%M").alias("time"),
    )

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for old in OUT_DIR.glob("*.json"):
        old.unlink()

    days = []
    for (day,), races in winners.group_by("day", maintain_order=True):
        rows = races.select("time", "track", "race", "winner", "bsp").rows()
        (OUT_DIR / f"{day}.json").write_text(json.dumps(rows, separators=(",", ":")))
        days.append(day)

    (OUT_DIR / "days.json").write_text(json.dumps(sorted(days, reverse=True)))
    print(f"wrote {len(winners)} races across {len(days)} days to {OUT_DIR}")


if __name__ == "__main__":
    main()
