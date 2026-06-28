import json
import sqlite3
from pathlib import Path

try:
    from .data_sources import NORMALIZED_DIR, PROCESSED_DIR
except ImportError:
    from data_sources import NORMALIZED_DIR, PROCESSED_DIR

DB_PATH = PROCESSED_DIR / "worldcup2026.db"

CREATE_TABLES_SQL = [
    """
    CREATE TABLE IF NOT EXISTS teams (
        id TEXT PRIMARY KEY,
        fifaCode TEXT,
        nameEn TEXT,
        nameFr TEXT,
        confederation TEXT,
        fifaRank INTEGER,
        fifaPoints REAL,
        previousFifaRank INTEGER,
        previousFifaPoints REAL,
        flagUrl TEXT,
        elo INTEGER,
        eloSource TEXT,
        eloDate TEXT,
        sourceConfidence TEXT
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS groups (
        groupId TEXT,
        teamId TEXT,
        PRIMARY KEY (groupId, teamId),
        FOREIGN KEY(teamId) REFERENCES teams(id)
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS group_matches (
        id TEXT PRIMARY KEY,
        groupId TEXT,
        homeTeamId TEXT,
        awayTeamId TEXT,
        matchday INTEGER,
        date TEXT,
        timeLocal TEXT,
        venueId TEXT,
        FOREIGN KEY(homeTeamId) REFERENCES teams(id),
        FOREIGN KEY(awayTeamId) REFERENCES teams(id)
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS venues (
        id TEXT PRIMARY KEY,
        name TEXT,
        city TEXT,
        capacity TEXT,
        country TEXT
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS bracket_rules (
        id TEXT PRIMARY KEY,
        roundName TEXT,
        homeSlot TEXT,
        awaySlot TEXT,
        payload TEXT
    )
    """,
]


def load_json_file(filename: str):
    path = NORMALIZED_DIR / filename
    if not path.exists():
        raise FileNotFoundError(f"Missing normalized file: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def import_teams(cursor, teams):
    cursor.execute("DELETE FROM teams")
    for team in teams:
        cursor.execute(
            """
            INSERT OR REPLACE INTO teams (
                id, fifaCode, nameEn, nameFr, confederation,
                fifaRank, fifaPoints, previousFifaRank, previousFifaPoints,
                flagUrl, elo, eloSource, eloDate, sourceConfidence
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                team.get("id"),
                team.get("fifaCode"),
                team.get("nameEn"),
                team.get("nameFr"),
                team.get("confederation"),
                team.get("fifaRank"),
                team.get("fifaPoints"),
                team.get("previousFifaRank"),
                team.get("previousFifaPoints"),
                team.get("flagUrl"),
                team.get("elo"),
                team.get("eloSource"),
                team.get("eloDate"),
                team.get("sourceConfidence"),
            ),
        )


def import_groups(cursor, groups):
    cursor.execute("DELETE FROM groups")
    for group_id, team_ids in groups.items():
        for team_id in team_ids:
            cursor.execute(
                "INSERT OR REPLACE INTO groups (groupId, teamId) VALUES (?, ?)"
                ,
                (group_id, team_id.lower()),
            )


def import_group_matches(cursor, matches):
    cursor.execute("DELETE FROM group_matches")
    for match in matches:
        cursor.execute(
            """
            INSERT OR REPLACE INTO group_matches (
                id, groupId, homeTeamId, awayTeamId, matchday,
                date, timeLocal, timezone, venueId
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                match.get("id"),
                match.get("group"),
                match.get("homeTeamId"),
                match.get("awayTeamId"),
                match.get("matchday"),
                match.get("date"),
                match.get("timeLocal"),
                match.get("timezone"),
                match.get("venueId"),
            ),
        )


def import_venues(cursor, venues):
    cursor.execute("DELETE FROM venues")
    for venue in venues:
        cursor.execute(
            """
            INSERT OR REPLACE INTO venues (id, name, city, capacity, country)
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                venue.get("id"),
                venue.get("name"),
                venue.get("city"),
                venue.get("capacity"),
                venue.get("country"),
            ),
        )


def import_bracket_rules(cursor, rules):
    cursor.execute("DELETE FROM bracket_rules")
    if isinstance(rules, dict):
        for round_name, entries in rules.items():
            if isinstance(entries, list):
                for entry in entries:
                    cursor.execute(
                        """
                        INSERT OR REPLACE INTO bracket_rules (
                            id, roundName, homeSlot, awaySlot, payload
                        ) VALUES (?, ?, ?, ?, ?)
                        """,
                        (
                            entry.get("id") or f"{round_name}_{entry.get('homeSlot')}_{entry.get('awaySlot')}",
                            round_name,
                            entry.get("homeSlot"),
                            entry.get("awaySlot"),
                            json.dumps(entry, ensure_ascii=False),
                        ),
                    )
            elif isinstance(entries, dict):
                cursor.execute(
                    """
                    INSERT OR REPLACE INTO bracket_rules (
                        id, roundName, homeSlot, awaySlot, payload
                    ) VALUES (?, ?, ?, ?, ?)
                    """,
                    (
                        entries.get("id") or round_name,
                        round_name,
                        entries.get("homeSlot"),
                        entries.get("awaySlot"),
                        json.dumps(entries, ensure_ascii=False),
                    ),
                )


def initialize_database(conn):
    for sql in CREATE_TABLES_SQL:
        conn.execute(sql)
    add_column_if_missing(conn, "teams", "sourceConfidence TEXT")
    add_column_if_missing(conn, "group_matches", "timezone TEXT")

def add_column_if_missing(conn, table_name: str, column_definition: str):
    column_name = column_definition.split()[0]
    cursor = conn.execute(f"PRAGMA table_info({table_name})")
    existing = [row[1] for row in cursor.fetchall()]
    if column_name not in existing:
        conn.execute(f"ALTER TABLE {table_name} ADD COLUMN {column_definition}")


def run_import():
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    teams = load_json_file("teams.json")
    groups = load_json_file("groups.json")
    group_matches = load_json_file("groupMatches.json")
    venues = load_json_file("venues.json")
    bracket_rules = load_json_file("bracketRules.json")

    with sqlite3.connect(DB_PATH) as conn:
        initialize_database(conn)
        import_teams(conn.cursor(), teams)
        import_groups(conn.cursor(), groups)
        import_group_matches(conn.cursor(), group_matches)
        import_venues(conn.cursor(), venues)
        import_bracket_rules(conn.cursor(), bracket_rules)
        conn.commit()

    print(f"Imported normalized data into SQLite database: {DB_PATH}")


if __name__ == "__main__":
    run_import()
