from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
RAW_DIR = ROOT_DIR / "data" / "raw"
NORMALIZED_DIR = ROOT_DIR / "data" / "normalized"
PROCESSED_DIR = ROOT_DIR / "data" / "processed"

FIFA_RANKINGS_URL = (
    "https://api.fifa.com/api/v3/rankings/?gender=1&count=211"
)

OPENFOOTBALL_URLS = {
    "openfootball_cup.txt": "https://raw.githubusercontent.com/openfootball/worldcup/master/2026--usa/cup.txt",
    "openfootball_cup_finals.txt": "https://raw.githubusercontent.com/openfootball/worldcup/master/2026--usa/cup_finals.txt",
    "openfootball_stadiums.csv": "https://raw.githubusercontent.com/openfootball/worldcup/master/2026--usa/cup_stadiums.csv",
    "openfootball_quali_playoffs.txt": "https://raw.githubusercontent.com/openfootball/worldcup/master/2026--usa/quali_playoffs.txt",
}

FOOTBALLRATINGS_URL = (
    "https://www.football-rankings.info/footballratings.html"
)

RAW_FILES = {
    "fifa_rankings_current.json": FIFA_RANKINGS_URL,
    "footballratings_elo.html": FOOTBALLRATINGS_URL,
    "openfootball_cup.txt": OPENFOOTBALL_URLS["openfootball_cup.txt"],
    "openfootball_cup_finals.txt": OPENFOOTBALL_URLS["openfootball_cup_finals.txt"],
    "openfootball_stadiums.csv": OPENFOOTBALL_URLS["openfootball_stadiums.csv"],
    "openfootball_quali_playoffs.txt": OPENFOOTBALL_URLS["openfootball_quali_playoffs.txt"],
    "elo_ratings_manual.json": None,
    "historical_results.csv": None,
    "team_name_overrides.json": None,
}

NORMALIZED_FILES = {
    "teams.json": NORMALIZED_DIR / "teams.json",
    "groups.json": NORMALIZED_DIR / "groups.json",
    "groupMatches.json": NORMALIZED_DIR / "groupMatches.json",
    "venues.json": NORMALIZED_DIR / "venues.json",
    "bracketRules.json": NORMALIZED_DIR / "bracketRules.json",
    "playoffs.json": NORMALIZED_DIR / "playoffs.json",
}
