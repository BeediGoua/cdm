import csv
import re
import requests
from bs4 import BeautifulSoup
from pathlib import Path

try:
    from .data_sources import RAW_DIR
except ImportError:
    from data_sources import RAW_DIR

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/125.0 Safari/537.36"
    )
}


def clean_text(x):
    return re.sub(r"\s+", " ", x or "").strip()


def fetch_url(url):
    r = requests.get(url, headers=HEADERS, timeout=30)
    r.raise_for_status()
    return r.text


def parse_eloratings(html):
    text = BeautifulSoup(html, "html.parser").get_text("\n")
    rows = []

    # Format observed: "1. Spain. 2155" or similar
    pattern = re.compile(r"^\s*(\d+)\.\s+(.+?)\.\s+(\d{3,4})\s*$")

    for line in text.splitlines():
        line = clean_text(line)
        m = pattern.match(line)
        if not m:
            continue

        rank, team, elo = m.groups()
        rows.append({
            "team": team,
            "rank": int(rank),
            "elo": int(elo),
            "elo_source": "eloratings.net",
            "source_confidence": "high",
        })

    return rows


def parse_international_football(html):
    text = BeautifulSoup(html, "html.parser").get_text("\n")
    rows = []

    pattern = re.compile(r"^\s*(\d+)\.\s+(.+?)\s+(\d{3,4})\s*$")

    for line in text.splitlines():
        line = clean_text(line)
        m = pattern.match(line)
        if not m:
            continue

        rank, team, elo = m.groups()
        if len(team) > 40:
            continue

        rows.append({
            "team": team,
            "rank": int(rank),
            "elo": int(elo),
            "elo_source": "international-football.net",
            "source_confidence": "medium",
        })

    return rows


def write_rows(rows, output: Path):
    output.parent.mkdir(parents=True, exist_ok=True)

    with output.open("w", encoding="utf-8", newline="") as fp:
        writer = csv.DictWriter(
            fp,
            fieldnames=["team", "rank", "elo", "elo_source", "source_confidence"],
        )
        writer.writeheader()
        for r in rows:
            writer.writerow(r)

    print(f"Wrote {len(rows)} rows to {output}")


def fetch_world_elo(output_path: Path = None):
    output = output_path or RAW_DIR / "world_football_elo.csv"

    sources = [
        {
            "name": "eloratings.net",
            "url": "https://www.eloratings.net/",
            "parser": parse_eloratings,
            "min_rows": 40,
        },
        {
            "name": "international-football.net",
            "url": "https://www.international-football.net/elo-ratings-table",
            "parser": parse_international_football,
            "min_rows": 40,
        },
    ]

    errors = []

    for src in sources:
        try:
            html = fetch_url(src["url"]) 
            rows = src["parser"](html)

            if len(rows) >= src["min_rows"]:
                write_rows(rows, output)
                print(f"Success with {src['name']}")
                return True

            errors.append(f"{src['name']}: only {len(rows)} rows parsed")

        except Exception as e:
            errors.append(f"{src['name']}: {e}")

    print("Failed to fetch real Elo.")
    for err in errors:
        print("-", err)

    return False


if __name__ == "__main__":
    fetch_world_elo()
