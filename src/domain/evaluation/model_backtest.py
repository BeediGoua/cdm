import argparse
from typing import Dict, List

import pandas as pd

from src.domain.simulation.poisson_model import match_probabilities, compute_lambdas
from src.domain.evaluation.log_loss import mean_log_loss
from src.domain.evaluation.brier_score import mean_brier_score
from src.domain.evaluation.calibration_curve import calibration_curve
import json
from pathlib import Path


def get_actual_outcome(home_score: int, away_score: int) -> str:
    if home_score > away_score:
        return "home_win"
    if home_score == away_score:
        return "draw"
    return "away_win"


def build_elo_lookup(teams_json_like: List[Dict]) -> Dict[str, float]:
    return {
        row["nameEn"]: float(row["elo"])
        for row in teams_json_like
        if row.get("nameEn") and row.get("elo") is not None
    }


def load_teams(path: str = "src/data/normalized/teams.json") -> List[Dict]:
    import json

    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def backtest_v1(
    matches_csv: str,
    teams_path: str,
    base_goals: float,
    scale: float,
    min_year: int = 2018,
    max_matches: int | None = None,
):
    df = pd.read_csv(matches_csv)

    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df["year"] = df["date"].dt.year
    df = df[df["year"] >= min_year]
    df = df.dropna(subset=["home_score", "away_score", "home_team", "away_team"])

    if max_matches:
        df = df.tail(max_matches)

    teams = load_teams(teams_path)
    elo_by_name = build_elo_lookup(teams)

    evaluated_rows = []
    skipped = 0

    for _, row in df.iterrows():
        home_team = row["home_team"]
        away_team = row["away_team"]

        if home_team not in elo_by_name or away_team not in elo_by_name:
            skipped += 1
            continue

        home_elo = elo_by_name[home_team]
        away_elo = elo_by_name[away_team]

        # compute expected goal rates (lambdas) from Elo and feed poisson model
        lambda_home, lambda_away = compute_lambdas(home_elo, away_elo, base_goals=base_goals, scale=scale)
        probs = match_probabilities(lambda_home, lambda_away)

        # poisson_model returns keys 'win_a', 'draw', 'win_b'
        predicted = {
            "home_win": probs.get("win_a") or probs.get("homeWin"),
            "draw": probs.get("draw"),
            "away_win": probs.get("win_b") or probs.get("awayWin"),
        }

        actual = get_actual_outcome(
            int(row["home_score"]),
            int(row["away_score"]),
        )

        evaluated_rows.append({
            "predicted": predicted,
            "actual_outcome": actual,
            "true_probability": predicted[actual],
        })

    if not evaluated_rows:
        raise ValueError(
            "Aucun match évalué. Vérifie le mapping entre noms martj42 et teams.json."
        )

    return {
        "baseGoals": base_goals,
        "scale": scale,
        "minYear": min_year,
        "nEvaluated": len(evaluated_rows),
        "nSkipped": skipped,
        "logLoss": mean_log_loss(r["true_probability"] for r in evaluated_rows),
        "brierScore": mean_brier_score(evaluated_rows),
        "evaluated_rows": evaluated_rows,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--matches", default="src/data/processed/matches_clean.csv")
    parser.add_argument("--teams", default="src/data/normalized/teams.json")
    parser.add_argument("--base-goals", type=float, default=1.35)
    parser.add_argument("--scale", type=float, default=800.0)
    parser.add_argument("--min-year", type=int, default=2018)
    parser.add_argument("--max-matches", type=int, default=None)

    args = parser.parse_args()

    result = backtest_v1(
        matches_csv=args.matches,
        teams_path=args.teams,
        base_goals=args.base_goals,
        scale=args.scale,
        min_year=args.min_year,
        max_matches=args.max_matches,
    )

    # build a report JSON including calibration curve
    evaluated = result.pop("evaluated_rows", [])

    # build calibration input: one entry per outcome per match
    cal_rows = []
    for r in evaluated:
        for outcome_key, prob in r["predicted"].items():
            cal_rows.append({
                "probability": prob,
                "actual": 1 if r["actual_outcome"] == outcome_key else 0,
            })

    curve = calibration_curve(cal_rows, probability_key="probability", outcome_key="actual", n_bins=10)

    report = {
        "summary": result,
        "calibration_curve": curve,
    }

    out = Path("reports") / "backtests"
    out.mkdir(parents=True, exist_ok=True)
    out_path = out / "V1_backtest.json"
    with out_path.open("w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)

    print("\n=== BACKTEST V1 ===")
    print(f"Rapport sauvegardé : {out_path}")


if __name__ == "__main__":
    main()