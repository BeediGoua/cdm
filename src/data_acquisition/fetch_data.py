import csv
import json
import re
import warnings
from pathlib import Path

import requests
from requests.exceptions import RequestException, SSLError

try:
    from .data_sources import RAW_DIR, RAW_FILES, FIFA_RANKINGS_URL
except ImportError:
    from data_sources import RAW_DIR, RAW_FILES, FIFA_RANKINGS_URL


def ensure_directories():
    RAW_DIR.mkdir(parents=True, exist_ok=True)


def download_url(url: str, dest: Path) -> bool:
    print(f"Downloading {url} -> {dest}")
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        dest.write_bytes(response.content)
        return True
    except SSLError as exc:
        print(f"SSL error downloading {url}: {exc}. Retrying without certificate verification.")
        warnings.filterwarnings("ignore", message="Unverified HTTPS request")
        try:
            response = requests.get(url, headers=headers, timeout=30, verify=False)
            response.raise_for_status()
            dest.write_bytes(response.content)
            return True
        except RequestException as exc2:
            print(f"Request error downloading {url}: {exc2}")
    except RequestException as exc:
        print(f"Request error downloading {url}: {exc}")
    return False


def fetch_fifa_rankings():
    destination = RAW_DIR / "fifa_rankings_current.json"
    return download_url(FIFA_RANKINGS_URL, destination)


def fetch_openfootball_files():
    success = True
    for filename, url in RAW_FILES.items():
        if filename.startswith("openfootball_"):
            dest = RAW_DIR / filename
            success = download_url(url, dest) and success
    return success


def fetch_footballratings():
    html_path = RAW_DIR / "footballratings_elo.html"
    success = download_url(RAW_FILES["footballratings_elo.html"], html_path)
    if not success:
        return False

    text = html_path.read_text(encoding="utf-8", errors="ignore")
    parsed_rows = []
    rating_pattern = re.compile(r"<tr>\s*<td>\s*(\d+)\s*</td>\s*<td>\s*([^<]+?)\s*</td>\s*<td>\s*(\d+)\s*</td>", re.I)
    for match in rating_pattern.finditer(text):
        rank = int(match.group(1))
        team = match.group(2).strip()
        elo = int(match.group(3))
        parsed_rows.append({"rank": rank, "team": team, "elo": elo})

    if parsed_rows:
        csv_path = RAW_DIR / "footballratings_elo.csv"
        with csv_path.open("w", encoding="utf-8") as output:
            output.write("rank,team,elo\n")
            for row in parsed_rows:
                output.write(f"{row['rank']},{row['team']},{row['elo']}\n")
        print(f"Extracted {len(parsed_rows)} FootballRatings rows into {csv_path}")
        return True

    print("Warning: FootballRatings parsing did not extract any rows. Inspect footballratings_elo.html manually.")
    return False


def create_manual_elo_template():
    manual_path = RAW_DIR / "elo_ratings_manual.json"
    if manual_path.exists():
        print(f"Manual ELO fallback already exists at {manual_path}")
        return True

    sample = [
        {
            "teamId": "fra",
            "teamName": "France",
            "elo": 2062,
            "rank": 3,
            "source": "manual",
            "date": "2026-06-09",
        }
    ]
    manual_path.write_text(json.dumps(sample, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Created manual ELO fallback template at {manual_path}")
    return True


def create_historical_placeholder():
    placeholder = RAW_DIR / "historical_results.csv"
    if placeholder.exists():
        print(f"Historical results placeholder already exists at {placeholder}")
        return True

    placeholder.write_text(
        "date,home_team,away_team,home_score,away_score,competition,venue\n",
        encoding="utf-8",
    )
    print(f"Created historical results placeholder at {placeholder}")
    return True


def create_team_name_overrides_template():
    override_path = RAW_DIR / "team_name_overrides.json"
    if override_path.exists():
        print(f"Team name overrides file already exists at {override_path}")
        return True

    override_path.write_text("{}\n", encoding="utf-8")
    print(f"Created team name overrides placeholder at {override_path}")
    return True


def fetch_martj42_historical():
    """Download historical_results.csv from the martj42 repository.
    Falls back to creating a placeholder if download fails.
    """
    candidates = [
        "https://raw.githubusercontent.com/martj42/international_results/master/historical_results.csv",
        "https://raw.githubusercontent.com/martj42/international_results/master/results/historical_results.csv",
        "https://raw.githubusercontent.com/martj42/international_results/master/data/historical_results.csv",
        "https://raw.githubusercontent.com/martj42/international_results/master/csv/historical_results.csv",
        "https://raw.githubusercontent.com/martj42/international_results/master/results.csv",
        "https://raw.githubusercontent.com/martj42/international_results/master/data/results.csv",
    ]
    dest = RAW_DIR / "historical_results.csv"
    print(f"Fetching martj42 historical results -> {dest}")
    for url in candidates:
        print(f"Trying {url}")
        success = download_url(url, dest)
        if success:
            print(f"Downloaded historical results into {dest} from {url}")
            return True
    print("Failed to download martj42 historical results from known paths; creating placeholder instead.")
    return create_historical_placeholder()


def run_all():
    ensure_directories()
    fetch_fifa_rankings()
    fetch_openfootball_files()
    fetch_footballratings()
    fetch_martj42_historical()
    create_manual_elo_template()
    create_team_name_overrides_template()
    # historical_results.csv is created by fetch_martj42_historical() or as a placeholder
    print("Data acquisition pipeline finished. Review raw files in src/data/raw/")


if __name__ == "__main__":
    run_all()
