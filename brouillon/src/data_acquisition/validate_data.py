import csv
import json
import re
import sys
from pathlib import Path

try:
    from .data_sources import RAW_DIR, RAW_FILES
except ImportError:
    from data_sources import RAW_DIR, RAW_FILES


def check_exists(path: Path) -> bool:
    if not path.exists():
        print(f"ERROR: missing file {path}")
        return False
    return True


def validate_json(path: Path) -> bool:
    try:
        with path.open("r", encoding="utf-8") as fp:
            data = json.load(fp)
    except json.JSONDecodeError as exc:
        print(f"ERROR: invalid JSON in {path}: {exc}")
        return False
    if path.name == "fifa_rankings_current.json":
        if not isinstance(data, dict) or "Results" not in data:
            print(f"ERROR: {path.name} must contain a top-level 'Results' array")
            return False
        if not isinstance(data["Results"], list):
            print(f"ERROR: 'Results' in {path.name} must be a list")
            return False
    if path.name == "elo_ratings_manual.json":
        if not isinstance(data, list):
            print(f"ERROR: {path.name} must be a JSON array")
            return False
        for idx, item in enumerate(data, start=1):
            if not isinstance(item, dict):
                print(f"ERROR: item {idx} in {path.name} must be an object")
                return False
            for key in ["teamId", "elo", "source"]:
                if key not in item:
                    print(f"ERROR: item {idx} in {path.name} is missing required key '{key}'")
                    return False
            if not isinstance(item["teamId"], str) or not item["teamId"].strip():
                print(f"ERROR: item {idx} in {path.name} has invalid 'teamId'")
                return False
            if not isinstance(item["source"], str) or not item["source"].strip():
                print(f"ERROR: item {idx} in {path.name} has invalid 'source'")
                return False
            try:
                int(float(item["elo"]))
            except (TypeError, ValueError):
                print(f"ERROR: item {idx} in {path.name} has invalid 'elo' value: {item.get('elo')}")
                return False
            if "rank" in item and item["rank"] is not None:
                try:
                    int(float(item["rank"]))
                except (TypeError, ValueError):
                    print(f"ERROR: item {idx} in {path.name} has invalid 'rank' value: {item.get('rank')}")
                    return False
    if path.name == "team_name_overrides.json":
        if not isinstance(data, dict):
            print(f"ERROR: {path.name} must be a JSON object mapping normalized names to team IDs")
            return False
        for key, value in data.items():
            if not isinstance(key, str) or not isinstance(value, str):
                print(f"ERROR: entries in {path.name} must be string-to-string mappings")
                return False
    return True


def validate_csv(path: Path) -> bool:
    try:
        with path.open("r", encoding="utf-8", errors="ignore") as fp:
            headers = None
            row_count = 0
            for line in fp:
                stripped = line.strip()
                if not stripped or stripped.startswith("#"):
                    continue
                if headers is None:
                    headers = next(csv.reader([line]), None)
                    continue
                row_count += 1
    except Exception as exc:
        print(f"ERROR: failed reading CSV {path}: {exc}")
        return False
    if not headers:
        print(f"ERROR: empty CSV file {path}")
        return False
    normalized_headers = set(h.strip().lower() for h in headers if h)
    if path.name == "openfootball_stadiums.csv":
        expected = {"city", "name", "capacity", "cc", "timezone", "wikipedia", "coords"}
        if not expected <= normalized_headers:
            print(f"ERROR: {path.name} is missing stadium headers: {sorted(expected - normalized_headers)}")
            return False
    if path.name == "footballratings_elo.csv":
        expected = {"rank", "team", "elo"}
        if not expected <= normalized_headers:
            print(f"ERROR: {path.name} is missing FootballRatings headers: {sorted(expected - normalized_headers)}")
            return False
    if path.name == "historical_results.csv":
        expected = {"date", "home_team", "away_team", "home_score", "away_score", "competition", "venue"}
        missing = expected - set(h.strip().lower() for h in headers)
        if missing:
            print(f"WARNING: {path.name} does not contain standard historical result headers: {sorted(missing)}")
        if row_count == 0:
            print(f"WARNING: {path.name} contains no match data; it is only a placeholder.")
    return True


def validate_footballratings_csv(path: Path) -> bool:
    try:
        with path.open("r", encoding="utf-8", errors="ignore") as fp:
            reader = csv.DictReader([line for line in fp if line.strip() and not line.strip().startswith("#")], skipinitialspace=True)
            for idx, row in enumerate(reader, start=1):
                if not row.get("team") or not row.get("elo"):
                    print(f"ERROR: invalid FootballRatings row {idx} in {path}")
                    return False
                try:
                    int(row.get("elo", ""))
                except ValueError:
                    print(f"ERROR: invalid ELO value on row {idx} in {path}: {row.get('elo')}")
                    return False
    except Exception as exc:
        print(f"ERROR: failed reading FootballRatings CSV {path}: {exc}")
        return False
    return True


def validate_txt(path: Path) -> bool:
    text = path.read_text(encoding="utf-8", errors="ignore").strip()
    if not text:
        print(f"ERROR: empty text file {path}")
        return False
    if path.name == "openfootball_cup.txt":
        if "Group " not in text:
            print(f"ERROR: {path.name} does not contain any 'Group ' markers")
            return False
        if " v " not in text or " @ " not in text:
            print(f"WARNING: {path.name} does not appear to contain match schedule lines")
    if path.name == "openfootball_quali_playoffs.txt":
        if not re.search(r"play[- ]?off", text, flags=re.I):
            print(f"WARNING: {path.name} does not contain obvious playoff keywords")
    return True


def validate_html(path: Path) -> bool:
    text = path.read_text(encoding="utf-8", errors="ignore")
    if "<html" not in text.lower() and "<!doctype html" not in text.lower():
        print(f"WARNING: {path.name} does not appear to be an HTML document")
    if "footballratings" not in text.lower() and "elo" not in text.lower():
        print(f"WARNING: {path.name} may not contain FootballRatings content")
    return True


def run_validation() -> bool:
    all_ok = True
    print("Validating raw data files...")

    for filename in RAW_FILES.keys():
        path = RAW_DIR / filename
        if filename == "footballratings_elo.html" and not path.exists():
            if (RAW_DIR / "elo_ratings_manual.json").exists():
                print(f"WARNING: {filename} missing, but manual ELO fallback exists.")
                continue
            if (RAW_DIR / "footballratings_elo.csv").exists():
                print(f"WARNING: {filename} missing, but footballratings_elo.csv exists.")
                continue
        exists = check_exists(path)
        if not exists:
            all_ok = False
            continue

        if filename.endswith(".json"):
            valid = validate_json(path)
        elif filename.endswith(".txt"):
            valid = validate_txt(path)
        elif filename.endswith(".html"):
            valid = validate_html(path)
        elif filename.endswith(".csv"):
            if path.name == "footballratings_elo.csv":
                valid = validate_footballratings_csv(path)
            else:
                valid = validate_csv(path)
        else:
            print(f"Skipping unknown raw file type for {filename}")
            valid = True

        if not valid:
            all_ok = False

    if all_ok:
        print("All raw data files are present and valid.")
    else:
        print("Raw data validation failed. Please fix the reported issues.")
    return all_ok


if __name__ == "__main__":
    success = run_validation()
    sys.exit(0 if success else 1)
