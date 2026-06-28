import csv
import json
import re
import unicodedata
from pathlib import Path

try:
    from .data_sources import NORMALIZED_DIR, PROCESSED_DIR, RAW_DIR, NORMALIZED_FILES
    from .team_resolution import resolve_with_overrides, load_manual_overrides
except ImportError:
    from data_sources import NORMALIZED_DIR, PROCESSED_DIR, RAW_DIR, NORMALIZED_FILES
    from data_acquisition.team_resolution import resolve_with_overrides, load_manual_overrides
from .team_name_aliases import TEAM_NAME_ALIASES


def ensure_directories():
    NORMALIZED_DIR.mkdir(parents=True, exist_ok=True)
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)


def write_json(path: Path, value):
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False), encoding="utf-8")


def write_csv(path: Path, fieldnames, rows):
    with path.open("w", encoding="utf-8", newline="") as fp:
        writer = csv.DictWriter(fp, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else None


def load_csv(path: Path):
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8", errors="ignore") as file:
        lines = [line for line in file if line.strip() and not line.strip().startswith("#")]
        reader = csv.DictReader(lines, skipinitialspace=True)
        return [row for row in reader if any(row.values())]


def normalize_text(value: str) -> str:
    if not value:
        return ""
    normalized = unicodedata.normalize("NFKD", value)
    normalized = "".join(ch for ch in normalized if not unicodedata.combining(ch))
    normalized = normalized.lower().strip()
    normalized = re.sub(r"[^a-z0-9]+", " ", normalized)
    return normalized.strip()


def parse_date_line(line: str):
    month_lookup = {
        "jan": "01",
        "january": "01",
        "feb": "02",
        "february": "02",
        "mar": "03",
        "march": "03",
        "apr": "04",
        "april": "04",
        "may": "05",
        "jun": "06",
        "june": "06",
        "jul": "07",
        "july": "07",
        "aug": "08",
        "august": "08",
        "sep": "09",
        "september": "09",
        "oct": "10",
        "october": "10",
        "nov": "11",
        "november": "11",
        "dec": "12",
        "december": "12",
    }
    parts = line.strip().split()
    if len(parts) >= 2:
        month_text = parts[-2].lower().strip().rstrip(".")
        day_text = parts[-1].strip().rstrip(",")
        if day_text.isdigit() and month_text in month_lookup:
            return f"2026-{month_lookup[month_text]}-{int(day_text):02d}"
    return line


def extend_team_name_aliases():
    # Dynamically add aliases from FIFA rankings so all teams are covered.
    try:
        data = load_json(RAW_DIR / "fifa_rankings_current.json")
        if not data:
            return
        for team in data.get("Results", []):
            team_id = (team.get("IdCountry") or team.get("IdTeam") or "").lower()
            name_en = ""
            for item in team.get("TeamName", []):
                if item.get("Locale", "").lower().startswith("en"):
                    name_en = item.get("Description", "")
                    break
            if not name_en and team.get("TeamName"):
                name_en = team.get("TeamName")[0].get("Description", "")
            norm_name = normalize_text(name_en) if name_en else ""
            if norm_name:
                # map normalized team name to itself (no-op) and map FIFA code to normalized name
                if norm_name not in TEAM_NAME_ALIASES:
                    TEAM_NAME_ALIASES[norm_name] = norm_name
                if team_id and team_id not in TEAM_NAME_ALIASES:
                    TEAM_NAME_ALIASES[team_id] = norm_name
    except Exception:
        # fail silently — aliases will remain as the statics
        return


# attempt to extend aliases at import time
extend_team_name_aliases()


def build_team_name_map(ranking_entries):
    name_to_id = {}
    for team in ranking_entries:
        team_id = team.get("IdCountry") or team.get("IdTeam")
        if not team_id:
            continue
        name_en = ""
        name_fr = ""
        for item in team.get("TeamName", []):
            locale = item.get("Locale", "").lower()
            if locale.startswith("en") and not name_en:
                name_en = item.get("Description", "")
            if locale.startswith("fr") and not name_fr:
                name_fr = item.get("Description", "")
        if not name_en and team.get("TeamName"):
            name_en = team.get("TeamName")[0].get("Description", "")
        if name_en:
            name_to_id[normalize_text(name_en)] = team_id.lower()
        if name_fr:
            name_to_id[normalize_text(name_fr)] = team_id.lower()
    return name_to_id


def resolve_team_id(raw_name: str, name_map: dict):
    if not raw_name:
        return ""
    normalized = normalize_text(raw_name)
    # first check manual overrides
    override = resolve_with_overrides(normalized)
    if override:
        return override.lower()

    # then check built-in aliases
    normalized = TEAM_NAME_ALIASES.get(normalized, normalized)
    if normalized in name_map:
        return name_map[normalized]

    # next check manual elo/team override file for mapping by name
    manual = load_manual_overrides()
    if normalized in manual:
        return manual[normalized].lower()

    # fallback: create an id-like string
    return normalized.replace(" ", "_").replace("&", "and")


def load_footballratings():
    # Prefer authoritative world Elo CSV, then FootballRatings if available, then FIFA approximation fallback
    primary = RAW_DIR / "world_football_elo.csv"
    secondary = RAW_DIR / "footballratings_elo.csv"
    fallback = RAW_DIR / "footballratings_elo_fallback.csv"
    csv_path = primary if primary.exists() else (secondary if secondary.exists() else (fallback if fallback.exists() else None))
    ratings = {}
    if csv_path is None:
        return ratings
    rows = load_csv(csv_path)
    if not rows:
        return ratings
    ranking_data = load_json(RAW_DIR / "fifa_rankings_current.json") or {}
    name_map = build_team_name_map(ranking_data.get("Results", []))
    for row in rows:
        team_name = (row.get("team") or row.get("country") or "").strip()
        rank = (row.get("rank") or "").strip()
        elo = (row.get("elo") or "").strip()
        if not team_name or not elo:
            continue
        try:
            elo_value = int(float(elo))
        except ValueError:
            continue
        team_id = resolve_team_id(team_name, name_map)
        if not team_id:
            continue
        if csv_path == primary:
            source = "world_football_elo"
            confidence = "primary"
        elif csv_path == secondary:
            source = "footballratings_elo"
            confidence = "secondary"
        else:
            source = "fifa_fallback"
            confidence = "fallback"
        ratings[team_id] = {
            "elo": elo_value,
            "eloRank": int(rank) if str(rank).isdigit() else None,
            "eloSource": row.get("elo_source") or source,
            "eloDate": None,
            "sourceConfidence": confidence,
        }
    return ratings


def normalize_teams():
    raw_rankings = load_json(RAW_DIR / "fifa_rankings_current.json")
    manual_elo = load_json(RAW_DIR / "elo_ratings_manual.json") or []
    elo_by_team = {e["teamId"].lower(): e for e in manual_elo}
    footballratings = load_footballratings()
    teams = []

    if raw_rankings is None:
        print("Missing fifa_rankings_current.json; skipping team normalization.")
        return []

    for team in raw_rankings.get("Results", []):
        fifa_code = team.get("IdCountry") or team.get("IdTeam") or "?"
        team_id = fifa_code.lower()
        name_en = ""
        name_fr = ""
        for item in team.get("TeamName", []):
            locale = item.get("Locale", "").lower()
            if locale.startswith("en") and not name_en:
                name_en = item.get("Description", "")
            if locale.startswith("fr") and not name_fr:
                name_fr = item.get("Description", "")
        if not name_en and team.get("TeamName"):
            name_en = team.get("TeamName")[0].get("Description", "")

        entries = {
            "id": team_id,
            "fifaCode": fifa_code,
            "fifaTeamId": fifa_code,
            "nameEn": name_en,
            "nameFr": name_fr,
            "confederation": team.get("ConfederationName", ""),
            "fifaRank": team.get("Rank"),
            "fifaPoints": team.get("DecimalTotalPoints") or team.get("TotalPoints"),
            "previousFifaRank": team.get("PrevRank"),
            "previousFifaPoints": team.get("DecimalPrevPoints") or team.get("PrevPoints"),
            "flagUrl": None,
            "sourceConfidence": None,
        }
        if team.get("IdCountry"):
            entries["flagUrl"] = f"https://api.fifa.com/api/v3/picture/flags-sq-2/{team.get('IdCountry')}"
        manual = elo_by_team.get(team_id)
        if manual:
            entries["elo"] = manual.get("elo")
            entries["eloRank"] = manual.get("rank")
            entries["eloSource"] = manual.get("source")
            entries["eloDate"] = manual.get("date")
            entries["sourceConfidence"] = "manual"
        elif team_id in footballratings:
            entries.update(footballratings[team_id])
        teams.append(entries)

    write_json(NORMALIZED_FILES["teams.json"], teams)
    print(f"Normalized {len(teams)} teams into {NORMALIZED_FILES['teams.json']}")
    return teams


def normalize_groups():
    result = {}
    openfootball_cup = RAW_DIR / "openfootball_cup.txt"
    if not openfootball_cup.exists():
        print("Missing openfootball_cup.txt; skipping group normalization.")
        write_json(NORMALIZED_FILES["groups.json"], result)
        return result

    ranking_data = load_json(RAW_DIR / "fifa_rankings_current.json") or {}
    name_map = build_team_name_map(ranking_data.get("Results", []))

    for line in openfootball_cup.read_text(encoding="utf-8", errors="ignore").splitlines():
        line = line.strip()
        if line.startswith("Group ") and "|" in line:
            group_label = line.split("|", 1)[0].replace("Group ", "").strip()
            teams_text = line.split("|", 1)[1].strip()
            team_names = [t.strip() for t in re.split(r"\s{2,}", teams_text) if t.strip()]
            team_ids = [resolve_team_id(name, name_map) for name in team_names]
            result[group_label] = team_ids

    write_json(NORMALIZED_FILES["groups.json"], result)
    print(f"Normalized {len(result)} groups into {NORMALIZED_FILES['groups.json']}")
    return result


def normalize_group_matches():
    result = []
    openfootball_cup = RAW_DIR / "openfootball_cup.txt"
    if not openfootball_cup.exists():
        print("Missing openfootball_cup.txt; skipping group matches normalization.")
        write_json(NORMALIZED_FILES["groupMatches.json"], result)
        return result

    ranking_data = load_json(RAW_DIR / "fifa_rankings_current.json") or {}
    name_map = build_team_name_map(ranking_data.get("Results", []))

    current_group = None
    current_date = None
    match_id = 1
    group_match_counts = {}
    for line in openfootball_cup.read_text(encoding="utf-8", errors="ignore").splitlines():
        stripped = line.strip()
        if stripped.startswith("▪ Group "):
            current_group = stripped.replace("▪ Group ", "").strip()
            continue
        if re.match(r"^[A-Za-z]{3} [A-Za-z]+ \d{1,2}$", stripped):
            current_date = parse_date_line(stripped)
            continue
        if " @ " in stripped:
            match = re.match(
                r"^(?P<time>\d{1,2}:\d{2})\s+UTC(?P<tz>[-+0-9]+)\s+(?P<teams_and_score>.*?)\s+@\s+(?P<venue>.+)$",
                stripped,
            )
            if not match or not current_group:
                continue
            
            teams_and_score = match.group("teams_and_score").strip()
            if " v " in teams_and_score:
                home_name, away_name = teams_and_score.split(" v ", 1)
            else:
                # Match scores like " 2-0 " or " 2-0 (1-0) "
                score_match = re.search(r"\s+\d+-\d+(?:\s+\(\d+-\d+\))?\s+", teams_and_score)
                if score_match:
                    home_name = teams_and_score[:score_match.start()].strip()
                    away_name = teams_and_score[score_match.end():].strip()
                else:
                    # In case of other formats like "a.e.t", let's try a generic split on digits if possible, or fallback
                    # For group stage, standard score format is enough
                    continue

            venue_name = match.group("venue").strip()
            current_count = group_match_counts.get(current_group, 0)
            matchday = current_count // 2 + 1
            group_match_counts[current_group] = current_count + 1
            entry = {
                "id": f"G{match_id:03}",
                "group": current_group,
                "homeTeamId": resolve_team_id(home_name, name_map),
                "awayTeamId": resolve_team_id(away_name, name_map),
                "matchday": matchday,
                "date": current_date,
                "timeLocal": match.group("time"),
                "timezone": match.group("tz"),
                "venueId": normalize_text(venue_name).replace(" ", "_").replace("'", ""),
            }
            result.append(entry)
            match_id += 1

    write_json(NORMALIZED_FILES["groupMatches.json"], result)
    print(f"Normalized {len(result)} group matches into {NORMALIZED_FILES['groupMatches.json']}")
    return result


def normalize_venues():
    result = []
    openfootball_stadiums = RAW_DIR / "openfootball_stadiums.csv"
    if not openfootball_stadiums.exists():
        print("Missing openfootball_stadiums.csv; skipping venue normalization.")
        write_json(NORMALIZED_FILES["venues.json"], result)
        return result

    for row in load_csv(openfootball_stadiums):
        name = row.get("name", "").strip()
        if not name:
            continue
        venue_id = normalize_text(name).replace(" ", "_").replace("'", "")
        result.append({
            "id": venue_id,
            "name": name,
            "city": row.get("city", "").strip(),
            "capacity": row.get("capacity", "").strip(),
            "country": row.get("cc", "").strip(),
            "timezone": row.get("timezone", "").strip(),
            "coords": row.get("coords", "").strip(),
            "wikipedia": row.get("wikipedia", "").strip(),
        })

    write_json(NORMALIZED_FILES["venues.json"], result)
    print(f"Normalized {len(result)} venues into {NORMALIZED_FILES['venues.json']}")
    return result


def normalize_bracket_rules():
    openfootball_finals = RAW_DIR / "openfootball_cup_finals.txt"
    rules = {
        "roundOf32": [],
        "roundOf16": [],
        "quarterFinals": [],
        "semiFinals": [],
        "thirdPlace": [],
        "final": [],
    }
    if not openfootball_finals.exists():
        print("Missing openfootball_cup_finals.txt; skipping bracket rules normalization.")
        write_json(NORMALIZED_FILES["bracketRules.json"], rules)
        return rules

    current_round = None
    current_date = None
    round_map = {
        "Round of 32": "roundOf32",
        "Round of 16": "roundOf16",
        "Quarter-final": "quarterFinals",
        "Semi-final": "semiFinals",
        "Match for third place": "thirdPlace",
        "Final": "final",
    }

    for line in openfootball_finals.read_text(encoding="utf-8", errors="ignore").splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or stripped.startswith("=") or stripped.startswith("##"):
            continue
        if stripped.startswith("▪ "):
            current_round = stripped.replace("▪ ", "").strip()
            continue
        if re.match(r"^[A-Za-z]{3} [A-Za-z]+ \d{1,2}$", stripped):
            current_date = parse_date_line(stripped)
            continue
        match = re.match(
            r"^\((?P<match_num>\d+)\)\s+(?P<time>\d{1,2}:\d{2})\s+(?P<timezone>UTC[-+0-9]+)\s+(?P<home>.*?)\s+v\s+(?P<away>.*?)\s+@\s+(?P<venue>.+)$",
            stripped,
        )
        if not match or not current_round:
            continue
        home = match.group("home").strip()
        away = match.group("away").strip()
        away_slot_options = [slot.strip() for slot in away.split("/") if slot.strip()]
        entry = {
            "id": f"M{int(match.group('match_num')):03}",
            "round": current_round,
            "homeSlot": home,
            "awaySlot": away,
            "awaySlotOptions": away_slot_options if len(away_slot_options) > 1 else None,
            "venue": match.group("venue").strip(),
            "time": match.group("time"),
            "timezone": match.group("timezone"),
            "date": current_date,
        }
        key = round_map.get(current_round, "rounds")
        if key not in rules:
            rules[key] = []
        rules[key].append(entry)

    write_json(NORMALIZED_FILES["bracketRules.json"], rules)
    print(f"Normalized bracket rules into {NORMALIZED_FILES['bracketRules.json']}")
    return rules


def normalize_playoffs():
    openfootball_playoffs = RAW_DIR / "openfootball_quali_playoffs.txt"
    playoffs = {
        "uefa": [],
        "interConfederation": [],
    }
    if not openfootball_playoffs.exists():
        print("Missing openfootball_quali_playoffs.txt; skipping playoffs normalization.")
        write_json(NORMALIZED_FILES["playoffs.json"], playoffs)
        return playoffs

    section = "uefa"
    path_label = None
    stage = None

    for line in openfootball_playoffs.read_text(encoding="utf-8", errors="ignore").splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or stripped.startswith("="):
            continue
        if stripped.startswith("▪▪ Path"):
            path_label = stripped.replace("▪▪ Path", "").strip()
            continue
        if stripped.startswith("▪▪▪"):
            stage = stripped.replace("▪▪▪", "").strip()
            continue
        if stripped.startswith("▪ Inter-confederation"):
            section = "interConfederation"
            continue
        match = re.match(
            r"^(?P<date>\w{2} \d{1,2}/\d{1,2}/\d{2})\s+(?P<time>\d{1,2}:\d{2})\s+(?P<timezone>\S+)\s+(?P<rest>.+)$",
            stripped,
        )
        if not match:
            continue
        date = match.group("date")
        time = match.group("time")
        timezone = match.group("timezone")
        rest = match.group("rest").strip()
        parts = rest.rsplit("@", 1)
        venue = parts[1].strip() if len(parts) > 1 else ""
        score_section = parts[0].strip()
        score_match = re.search(r"(?P<home>.*?)\s+(?P<score>\d+-\d+(?:[^\s]*))\s+(?P<away>.+)$", score_section)
        if not score_match:
            continue
        home = score_match.group("home").strip()
        score_text = score_match.group("score").strip()
        away = score_match.group("away").strip()
        score_numeric = score_text.split()[0]
        home_score, away_score = score_numeric.split("-") if "-" in score_numeric else (None, None)
        winner = None
        try:
            if home_score is not None and away_score is not None:
                home_score_int = int(home_score)
                away_score_int = int(away_score)
                winner = home if home_score_int > away_score_int else away if away_score_int > home_score_int else None
        except ValueError:
            winner = None
        record = {
            "path": path_label,
            "stage": stage,
            "date": date,
            "time": time,
            "timezone": timezone,
            "homeTeam": home,
            "awayTeam": away,
            "scoreText": score_text,
            "homeScore": int(home_score) if home_score and home_score.isdigit() else None,
            "awayScore": int(away_score) if away_score and away_score.isdigit() else None,
            "winner": winner,
            "venue": venue,
        }
        playoffs[section].append(record)

    write_json(NORMALIZED_FILES["playoffs.json"], playoffs)
    print(f"Normalized {sum(len(v) for v in playoffs.values())} playoff matches into {NORMALIZED_FILES['playoffs.json']}")
    return playoffs


def process_historical_results():
    source = RAW_DIR / "historical_results.csv"
    target = PROCESSED_DIR / "matches_clean.csv"
    rows = load_csv(source)
    header = [
        "date",
        "home_team",
        "away_team",
        "home_score",
        "away_score",
        "competition",
        "venue",
        "neutral",
        "home_win",
        "draw",
        "away_win",
        "total_goals",
        "goal_diff",
    ]

    if not rows:
        write_csv(target, header, [])
        print(f"Created historical results placeholder at {target}")
        return target

    cleaned = []
    for row in rows:
        date_value = row.get("date", "").strip()
        home_team = row.get("home_team", "").strip()
        away_team = row.get("away_team", "").strip()
        home_score = row.get("home_score", "").strip()
        away_score = row.get("away_score", "").strip()
        if not date_value or not home_team or not away_team or home_score == "" or away_score == "":
            continue
        try:
            home_value = int(home_score)
            away_value = int(away_score)
        except ValueError:
            continue
        home_win = int(home_value > away_value)
        draw = int(home_value == away_value)
        away_win = int(away_value > home_value)
        cleaned.append({
            "date": date_value,
            "home_team": home_team,
            "away_team": away_team,
            "home_score": home_value,
            "away_score": away_value,
            "competition": row.get("competition", "").strip(),
            "venue": row.get("venue", "").strip(),
            "neutral": row.get("neutral", "").strip(),
            "home_win": home_win,
            "draw": draw,
            "away_win": away_win,
            "total_goals": home_value + away_value,
            "goal_diff": home_value - away_value,
        })

    write_csv(target, header, cleaned)
    print(f"Processed {len(cleaned)} historical matches into {target}")
    return target


def run_normalization():
    ensure_directories()
    normalize_teams()
    normalize_groups()
    normalize_group_matches()
    normalize_venues()
    normalize_bracket_rules()
    normalize_playoffs()
    process_historical_results()
    print("Data normalization pipeline finished. Review normalized files in src/data/normalized/ and processed files in src/data/processed/")


if __name__ == "__main__":
    run_normalization()
