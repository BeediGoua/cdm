
# src/domain/evaluation/calibrate_base_goals.py

"""
Calcul de la calibration `baseGoals` à partir d'un CSV de matches.

Usage :

    .venv\Scripts\python.exe -u -m src.domain.evaluation.calibrate_base_goals --min-year 2000

Sorties :

    outputs/calibration/base_goals.json

Exemple :

{
  "csvPath": "src/data/processed/matches_clean.csv",
  "minYear": 2000,
  "nMatches": 25316,
  "totalGoalsPerMatch": 2.75557,
  "baseGoals": 1.37778,
  "baseGoalsRounded": 1.378
}
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Optional

import pandas as pd


DEFAULT_OUTPUT = "outputs/calibration/base_goals.json"


def compute_base_goals(
    csv_path: str,
    min_year: Optional[int] = None,
) -> dict:

    print(f"[INFO] Lecture du fichier CSV : {csv_path}...")

    if not os.path.exists(csv_path):
        print(
            f"[ERREUR] Le fichier '{csv_path}' est introuvable.",
            file=sys.stderr,
        )
        print(
            "[ASTUCE] Vérifie que tu es dans le dossier racine du projet.",
            file=sys.stderr,
        )
        return {}

    df = pd.read_csv(csv_path)

    print(f"[INFO] Nombre de lignes chargées : {len(df)}")

    if "date" in df.columns:
        df["date"] = pd.to_datetime(df["date"], errors="coerce")
        df["year"] = df["date"].dt.year

    if min_year is not None and "year" in df.columns:
        df = df[df["year"] >= min_year]
        print(f"[INFO] Filtrage appliqué : année >= {min_year}")

    df = df.dropna(subset=["home_score", "away_score"])

    if len(df) == 0:
        print(
            "[ERREUR] Aucune donnée restante après filtrage.",
            file=sys.stderr,
        )
        return {}

    total_goals_per_match = (
        df["home_score"] + df["away_score"]
    ).mean()

    base_goals = total_goals_per_match / 2

    return {
        "csvPath": csv_path,
        "minYear": min_year,
        "nMatches": int(len(df)),
        "totalGoalsPerMatch": round(
            float(total_goals_per_match),
            6,
        ),
        "baseGoals": round(
            float(base_goals),
            6,
        ),
        "baseGoalsRounded": round(
            float(base_goals),
            3,
        ),
    }


def save_report(
    report: dict,
    output_path: str,
) -> str:

    output_file = Path(output_path)

    output_file.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with open(
        output_file,
        "w",
        encoding="utf-8",
    ) as f:
        json.dump(
            report,
            f,
            ensure_ascii=False,
            indent=2,
        )

    return str(output_file)


def main() -> None:

    try:
        sys.stdout.reconfigure(line_buffering=True)
    except Exception:
        pass

    print("\n--- [DÉBUT DU SCRIPT] ---")

    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--csv",
        default="src/data/processed/matches_clean.csv",
    )

    parser.add_argument(
        "--min-year",
        type=int,
        default=2000,
    )

    parser.add_argument(
        "--output",
        default=DEFAULT_OUTPUT,
    )

    # use parse_known_args to be resilient to extra args when run via -m or tooling
    args, _ = parser.parse_known_args()

    print(
        f"[INFO] Arguments reçus -> min-year={args.min_year}"
    )

    result = compute_base_goals(csv_path=args.csv, min_year=args.min_year)

    if not result:
        print(
            "\n[ÉCHEC] Impossible de calculer baseGoals."
        )
        sys.exit(1)

    output_file = save_report(result, args.output)

    print("\n=== CALIBRATION baseGoals ===")

    for k, v in result.items():
        print(f"{k}: {v}")

    print(f"\n[OK] Rapport sauvegardé :")
    print(output_file)

    print("\n--- [FIN DU SCRIPT] ---")


if __name__ == "__main__":
    main()