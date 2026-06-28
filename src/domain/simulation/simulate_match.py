import random
from typing import Dict, Tuple

from src.domain.simulation.poisson_model import compute_lambdas, match_probabilities, score_matrix
from src.domain.models.dixon_coles import match_probabilities_dc, score_matrix_dc
from src.domain.models.bayesian_v4 import compute_lambdas_v4, match_probabilities_v4, score_matrix_v4
from src.domain.models.bivariate_v5 import compute_lambdas_v5, match_probabilities_v5, score_matrix_v5

def predict_match(elo_a: float, elo_b: float, base_goals: float = 1.35, scale: float = 800.0, model_version: str = "V2", team_a: str = None, team_b: str = None, real_results: dict = None, home_covars: dict = None, away_covars: dict = None) -> Dict[str, float]:
    """
    Retourne les probabilités de victoire, nul et défaite pour un match entre deux équipes.
    C'est le mode "distribution".
    """
    if model_version == "V4" and team_a and team_b:
        lambda_a, lambda_b = compute_lambdas_v4(elo_a, elo_b, team_a, team_b, real_results, base_goals, scale)
        return match_probabilities_v4(lambda_a, lambda_b)
        
    if model_version == "V5":
        hc = home_covars if home_covars is not None else {"goal_diff": 0, "rest_days": 5}
        ac = away_covars if away_covars is not None else {"goal_diff": 0, "rest_days": 5}
        lambda_a, lambda_b = compute_lambdas_v5(elo_a, elo_b, hc, ac, base_goals, scale)
        return match_probabilities_v5(lambda_a, lambda_b)
        
    lambda_a, lambda_b = compute_lambdas(elo_a, elo_b, base_goals, scale)
    if model_version == "V3":
        return match_probabilities_dc(lambda_a, lambda_b)
    return match_probabilities(lambda_a, lambda_b)

def sample_match_score(elo_a: float, elo_b: float, base_goals: float = 1.35, scale: float = 800.0, max_goals: int = 10, model_version: str = "V2", team_a: str = None, team_b: str = None, real_results: dict = None, home_covars: dict = None, away_covars: dict = None) -> Tuple[int, int]:
    """
    Tire aléatoirement un score (buts A, buts B) basé sur la distribution de probabilités du modèle Poisson ou Dixon-Coles.
    C'est le mode "random".
    """
    if model_version == "V4" and team_a and team_b:
        lambda_a, lambda_b = compute_lambdas_v4(elo_a, elo_b, team_a, team_b, real_results, base_goals, scale)
        matrix = score_matrix_v4(lambda_a, lambda_b, max_goals)
    elif model_version == "V5":
        hc = home_covars if home_covars is not None else {"goal_diff": 0, "rest_days": 5}
        ac = away_covars if away_covars is not None else {"goal_diff": 0, "rest_days": 5}
        lambda_a, lambda_b = compute_lambdas_v5(elo_a, elo_b, hc, ac, base_goals, scale)
        matrix = score_matrix_v5(lambda_a, lambda_b, max_goals)
    else:
        lambda_a, lambda_b = compute_lambdas(elo_a, elo_b, base_goals, scale)
        if model_version == "V3":
            matrix = score_matrix_dc(lambda_a, lambda_b, max_goals)
        else:
            matrix = score_matrix(lambda_a, lambda_b, max_goals)
    
    # Pour utiliser random.choices, on doit aplatir la matrice en une liste 1D
    # de scores possibles (i, j) et une liste 1D de probabilités (weights).
    scores = []
    weights = []
    
    for i in range(max_goals + 1):
        for j in range(max_goals + 1):
            scores.append((i, j))
            weights.append(matrix[i][j])
            
    # random.choices retourne une liste d'éléments tirés, on prend le premier [0]
    sampled_score = random.choices(scores, weights=weights, k=1)[0]
    
    return sampled_score

if __name__ == "__main__":
    # Test de vérification avec l'exemple de STEPS.md
    elo_fra = 2062
    elo_can = 1780
    
    print("Mode Distribution (Prédiction pure) :")
    probs = predict_match(elo_fra, elo_can)
    print(f"FRA gagne: {probs['win_a']:.2%}, Nul: {probs['draw']:.2%}, CAN gagne: {probs['win_b']:.2%}")
    
    print("\nMode Random (Tirage de 5 scores simulés) :")
    for i in range(5):
        score_fra, score_can = sample_match_score(elo_fra, elo_can)
        print(f"Simulation {i+1} -> FRA {score_fra} - {score_can} CAN")
