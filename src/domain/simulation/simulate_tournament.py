import json
import random
from pathlib import Path
from typing import Dict, Any, List, Tuple

from datetime import datetime
from src.domain.simulation.simulate_match import sample_match_score
from src.domain.simulation.live_elo import compute_live_elos
from src.domain.tournament.compute_group_standings import compute_group_standings
from src.domain.tournament.rank_third_placed import rank_third_placed
from src.domain.tournament.build_bracket import build_round_of_32

DATA_DIR = Path("src/data")


def load_json(path: str):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def load_tournament_data():
    """
    Charge les données une seule fois pour accélérer Monte Carlo.
    """
    teams_data = load_json(DATA_DIR / "normalized" / "teams.json")
    teams_dict = {t["id"]: t for t in teams_data}

    groups = load_json(DATA_DIR / "normalized" / "groups.json")
    group_matches = load_json(DATA_DIR / "normalized" / "groupMatches.json")
    bracket_rules = load_json(DATA_DIR / "normalized" / "bracketRules.json")

    real_results_path = DATA_DIR / "raw" / "real_results.json"

    if real_results_path.exists():
        real_results = load_json(real_results_path)
    else:
        real_results = {"groups": {}, "knockouts": {}}

    return teams_dict, groups, group_matches, bracket_rules, real_results


def get_tournament_team_ids(groups: Dict[str, List[str]]) -> List[str]:
    team_ids = []
    for group_teams in groups.values():
        for team_id in group_teams:
            if team_id not in team_ids:
                team_ids.append(team_id)
    return team_ids


def get_real_group_result(match_id: str, real_results: Dict[str, Any], mode: str):
    if mode != "live":
        return None

    return real_results.get("groups", {}).get(match_id)


def get_real_knockout_result(match_id: str, real_results: Dict[str, Any], mode: str):
    if mode != "live":
        return None

    return real_results.get("knockouts", {}).get(match_id)


def _calculate_rest_days(last_date_str: str, current_date_str: str) -> int:
    if not last_date_str or not current_date_str:
        return 5
    try:
        d1 = datetime.strptime(last_date_str, "%Y-%m-%d")
        d2 = datetime.strptime(current_date_str, "%Y-%m-%d")
        return (d2 - d1).days
    except:
        return 5


def simulate_or_use_real_group_match(
    match: Dict[str, Any],
    teams_dict: Dict[str, Any],
    real_results: Dict[str, Any],
    base_goals: float,
    scale: float,
    mode: str,
    model_version: str = "V2",
    home_covars: dict = None,
    away_covars: dict = None,
):
    match_id = match["id"]
    home_team = match["homeTeamId"]
    away_team = match["awayTeamId"]

    real_match = get_real_group_result(match_id, real_results, mode)

    if real_match is not None:
        return {
            "id": match_id,
            "group": match.get("group"),
            "homeTeamId": home_team,
            "awayTeamId": away_team,
            "homeGoals": int(real_match["homeGoals"]),
            "awayGoals": int(real_match["awayGoals"]),
            "status": "played",
        }

    home_goals, away_goals = sample_match_score(
        teams_dict[home_team]["elo"],
        teams_dict[away_team]["elo"],
        base_goals,
        scale,
        model_version=model_version,
        team_a=home_team,
        team_b=away_team,
        real_results=real_results,
        home_covars=home_covars,
        away_covars=away_covars,
    )

    return {
        "id": match_id,
        "group": match.get("group"),
        "homeTeamId": home_team,
        "awayTeamId": away_team,
        "homeGoals": home_goals,
        "awayGoals": away_goals,
        "status": "simulated",
    }


def simulate_group_stage(
    teams_dict: Dict[str, Any],
    groups: Dict[str, List[str]],
    group_matches: List[Dict[str, Any]],
    real_results: Dict[str, Any],
    base_goals: float,
    scale: float,
    mode: str,
    model_version: str = "V2",
    team_covariables: Dict[str, Any] = None,
):
    all_group_standings = {}

    matches_by_group = {group_name: [] for group_name in groups.keys()}

    for match in group_matches:
        group = match.get("group")
        if group not in matches_by_group:
            continue

        match_date = match.get("date")
        home_team = match["homeTeamId"]
        away_team = match["awayTeamId"]
        
        home_covars = None
        away_covars = None
        if team_covariables is not None:
            home_covars = {
                "goal_diff": team_covariables[home_team]["goal_diff"],
                "rest_days": _calculate_rest_days(team_covariables[home_team]["last_match_date"], match_date)
            }
            away_covars = {
                "goal_diff": team_covariables[away_team]["goal_diff"],
                "rest_days": _calculate_rest_days(team_covariables[away_team]["last_match_date"], match_date)
            }

        simulated_match = simulate_or_use_real_group_match(
            match=match,
            teams_dict=teams_dict,
            real_results=real_results,
            base_goals=base_goals,
            scale=scale,
            mode=mode,
            model_version=model_version,
            home_covars=home_covars,
            away_covars=away_covars,
        )

        if team_covariables is not None:
            team_covariables[home_team]["goal_diff"] += (simulated_match["homeGoals"] - simulated_match["awayGoals"])
            team_covariables[away_team]["goal_diff"] += (simulated_match["awayGoals"] - simulated_match["homeGoals"])
            team_covariables[home_team]["last_match_date"] = match_date
            team_covariables[away_team]["last_match_date"] = match_date

        matches_by_group[group].append(simulated_match)

    for group_name, group_teams in groups.items():
        standings = compute_group_standings(
            matches_by_group[group_name],
            group_teams,
        )
        all_group_standings[group_name] = standings

    return all_group_standings


def simulate_knockout_match(
    match_id: str,
    team_a: str,
    team_b: str,
    teams_dict: Dict[str, Any],
    real_results: Dict[str, Any],
    base_goals: float,
    scale: float,
    mode: str,
    model_version: str = "V2",
    home_covars: dict = None,
    away_covars: dict = None,
):
    real_match = get_real_knockout_result(match_id, real_results, mode)

    if real_match is not None:
        goals_a = int(real_match["homeGoals"])
        goals_b = int(real_match["awayGoals"])
    else:
        goals_a, goals_b = sample_match_score(
            teams_dict[team_a]["elo"],
            teams_dict[team_b]["elo"],
            base_goals,
            scale,
            model_version=model_version,
            team_a=team_a,
            team_b=team_b,
            real_results=real_results,
            home_covars=home_covars,
            away_covars=away_covars,
        )

    if goals_a == goals_b:
        winner = team_a if random.random() < 0.5 else team_b
    elif goals_a > goals_b:
        winner = team_a
    else:
        winner = team_b

    return winner, goals_a, goals_b


def winner_slot(match_id: str) -> str:
    """
    Convertit M073 -> W73.
    """
    digits = "".join(ch for ch in match_id if ch.isdigit())
    return f"W{int(digits)}"


def simulate_tournament(
    teams_dict: Dict[str, Any],
    groups: Dict[str, List[str]],
    group_matches: List[Dict[str, Any]],
    bracket_rules: Dict[str, Any],
    real_results: Dict[str, Any],
    base_goals: float = 1.35,
    scale: float = 800.0,
    mode: str = "pre_tournament",
    model_version: str = "V2",
) -> Tuple[Dict[str, str], Dict[str, List[str]]]:
    """
    Simule un tournoi complet.

    Retour :
    (
      {"fra": "champion", "can": "group", ...},
      {"fra": ["arg", "bra", ...], ...}
    )
    """
    tournament_team_ids = get_tournament_team_ids(groups)

    results = {team_id: "group" for team_id in tournament_team_ids}
    opponents = {team_id: [] for team_id in tournament_team_ids}
    
    team_covariables = {team_id: {"goal_diff": 0, "last_match_date": None} for team_id in tournament_team_ids}

    # 1. Group stage
    all_group_standings = simulate_group_stage(
        teams_dict=teams_dict,
        groups=groups,
        group_matches=group_matches,
        real_results=real_results,
        base_goals=base_goals,
        scale=scale,
        mode=mode,
        model_version=model_version,
        team_covariables=team_covariables,
    )

    # 2. Round of 32
    best_thirds = rank_third_placed(all_group_standings)

    round_32 = build_round_of_32(
        bracket_rules["roundOf32"],
        all_group_standings,
        best_thirds,
    )

    # 3. Knockout rounds
    winners_dict = {}

    rounds = [
        ("roundOf32", round_32, "roundOf32", "roundOf16"),
        ("roundOf16", bracket_rules["roundOf16"], "roundOf16", "quarterFinal"),
        ("quarterFinals", bracket_rules["quarterFinals"], "quarterFinal", "semiFinal"),
        ("semiFinals", bracket_rules["semiFinals"], "semiFinal", "final"),
        ("final", bracket_rules["final"], "final", "champion"),
    ]

    for round_name, match_rules, reached_stage, next_stage in rounds:
        next_round_winners = {}

        for match in match_rules:
            match_id = match["id"]

            if round_name == "roundOf32":
                team_a = match["homeTeamId"]
                team_b = match["awayTeamId"]
            else:
                team_a = winners_dict[match["homeSlot"]]
                team_b = winners_dict[match["awaySlot"]]

            results[team_a] = reached_stage
            results[team_b] = reached_stage
            
            opponents[team_a].append(team_b)
            opponents[team_b].append(team_a)

            match_date = match.get("date")
            home_covars = None
            away_covars = None
            if team_covariables is not None:
                home_covars = {
                    "goal_diff": team_covariables[team_a]["goal_diff"],
                    "rest_days": _calculate_rest_days(team_covariables[team_a]["last_match_date"], match_date)
                }
                away_covars = {
                    "goal_diff": team_covariables[team_b]["goal_diff"],
                    "rest_days": _calculate_rest_days(team_covariables[team_b]["last_match_date"], match_date)
                }

            winner, goals_a, goals_b = simulate_knockout_match(
                match_id=match_id,
                team_a=team_a,
                team_b=team_b,
                teams_dict=teams_dict,
                real_results=real_results,
                base_goals=base_goals,
                scale=scale,
                mode=mode,
                model_version=model_version,
                home_covars=home_covars,
                away_covars=away_covars,
            )

            if team_covariables is not None:
                team_covariables[team_a]["goal_diff"] += (goals_a - goals_b)
                team_covariables[team_b]["goal_diff"] += (goals_b - goals_a)
                team_covariables[team_a]["last_match_date"] = match_date
                team_covariables[team_b]["last_match_date"] = match_date

            next_round_winners[winner_slot(match_id)] = winner

            if round_name == "final":
                results[winner] = "champion"

        winners_dict = next_round_winners

    return results, opponents


if __name__ == "__main__":
    teams_dict, groups, group_matches, bracket_rules, real_results = load_tournament_data()

    result = simulate_tournament(
        teams_dict=teams_dict,
        groups=groups,
        group_matches=group_matches,
        bracket_rules=bracket_rules,
        real_results=real_results,
        mode="pre_tournament",
    )

    print(json.dumps(result, indent=2, ensure_ascii=False))
    
# python -m src.domain.simulation.simulate_tournament
# python -m src.domain.simulation.run_monte_carlo --n 1000
# python -m src.domain.simulation.run_monte_carlo --n 1000 --mode live