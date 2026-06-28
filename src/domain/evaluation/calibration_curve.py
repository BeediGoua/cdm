from typing import Dict, Iterable, List
import math


def assign_bin(probability: float, n_bins: int) -> int:
    if probability >= 1:
        return n_bins - 1
    if probability <= 0:
        return 0
    return int(math.floor(probability * n_bins))


def calibration_curve(
    rows: Iterable[Dict],
    probability_key: str = "probability",
    outcome_key: str = "actual",
    n_bins: int = 10,
):
    """
    rows attendus :
    [
      {"probability": 0.72, "actual": 1},
      {"probability": 0.31, "actual": 0}
    ]
    """
    bins = {
        i: {
            "bin": i,
            "count": 0,
            "mean_predicted": 0.0,
            "mean_observed": 0.0,
            "min_prob": i / n_bins,
            "max_prob": (i + 1) / n_bins,
        }
        for i in range(n_bins)
    }

    for row in rows:
        p = float(row[probability_key])
        y = int(row[outcome_key])

        b = assign_bin(p, n_bins)

        bins[b]["count"] += 1
        bins[b]["mean_predicted"] += p
        bins[b]["mean_observed"] += y

    output = []

    for b in bins.values():
        if b["count"] > 0:
            b["mean_predicted"] /= b["count"]
            b["mean_observed"] /= b["count"]

        output.append(b)

    return output