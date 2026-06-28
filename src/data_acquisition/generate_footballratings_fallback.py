# src/data_acquisition/generate_footballratings_fallback.py
import csv
import json
from pathlib import Path

try:
    from .data_sources import RAW_DIR
except ImportError:
    from data_sources import RAW_DIR


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else None


def normalize_text(value: str) -> str:
    if not value:
        return ""
    import unicodedata, re

    normalized = unicodedata.normalize("NFKD", value)
    normalized = "".join(ch for ch in normalized if not unicodedata.combining(ch))
    normalized = normalized.lower().strip()
    normalized = re.sub(r"[^a-z0-9]+", " ", normalized)
    return normalized.strip()


def generate_from_fifa(output_path: Path = None):
    output = output_path or (RAW_DIR / "footballratings_elo_fallback.csv")
    data = load_json(RAW_DIR / "fifa_rankings_current.json")
    if not data:
        print("Missing fifa_rankings_current.json; cannot generate fallback.")
        return False

    teams = data.get("Results", [])
    # collect points
    points = []
    for t in teams:
        p = t.get("DecimalTotalPoints") or t.get("TotalPoints") or 0
        try:
            points.append(float(p))
        except Exception:
            points.append(0.0)
    if not points:
        print("No points found in FIFA data; aborting.")
        return False

    max_p = max(points)
    min_p = min(points)
    spread = max_p - min_p if max_p != min_p else 1.0

    rows = []
    for t in teams:
        name = ""
        for item in t.get("TeamName", []):
            if item.get("Locale", "").lower().startswith("en"):
                name = item.get("Description", "")
                break
        if not name and t.get("TeamName"):
            name = t.get("TeamName")[0].get("Description", "")
        points_val = t.get("DecimalTotalPoints") or t.get("TotalPoints") or 0
        try:
            pv = float(points_val)
        except Exception:
            pv = 0.0
        # scale to Elo-like 1200..2200
        elo = int(1200 + ((pv - min_p) / spread) * 1000)
        rank = t.get("Rank") or ""
        rows.append({"team": name, "rank": rank, "elo": elo})

    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", encoding="utf-8", newline="") as fp:
        writer = csv.DictWriter(fp, fieldnames=["team", "rank", "elo"])
        writer.writeheader()
        for r in rows:
            writer.writerow(r)

    print(f"Wrote {len(rows)} fallback rows to {output}")
    return True


if __name__ == "__main__":
    generate_from_fifa()
