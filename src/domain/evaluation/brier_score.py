from typing import Dict, Iterable, List


OUTCOMES = ["home_win", "draw", "away_win"]


def brier_score_one(predicted: Dict[str, float], actual_outcome: str) -> float:
    if actual_outcome not in OUTCOMES:
        raise ValueError(f"Outcome invalide: {actual_outcome}")

    score = 0.0

    for outcome in OUTCOMES:
        y = 1.0 if outcome == actual_outcome else 0.0
        p = float(predicted.get(outcome, 0.0))
        score += (p - y) ** 2

    return score


def mean_brier_score(rows: Iterable[Dict]) -> float:
    values: List[float] = []

    for row in rows:
        values.append(
            brier_score_one(
                predicted=row["predicted"],
                actual_outcome=row["actual_outcome"],
            )
        )

    if not values:
        raise ValueError("Aucune observation pour calculer le Brier Score.")

    return sum(values) / len(values)