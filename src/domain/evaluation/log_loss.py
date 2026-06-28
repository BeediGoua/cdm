import math
from typing import Iterable


EPSILON = 1e-15


def clip_probability(p: float) -> float:
    return max(EPSILON, min(1.0 - EPSILON, float(p)))


def log_loss_one(probability_assigned_to_true_class: float) -> float:
    p = clip_probability(probability_assigned_to_true_class)
    return -math.log(p)


def mean_log_loss(probabilities_assigned_to_true_class: Iterable[float]) -> float:
    values = list(probabilities_assigned_to_true_class)

    if not values:
        raise ValueError("La liste des probabilités est vide.")

    return sum(log_loss_one(p) for p in values) / len(values)

