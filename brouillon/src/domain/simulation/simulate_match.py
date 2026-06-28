import random
from typing import Dict, Tuple

# On importe les fonctions du modèle de Poisson que nous venons de créer
from src.domain.simulation.poisson_model import compute_lambdas, match_probabilities, score_matrix

def predict_match(elo_a: float, elo_b: float, base_goals: float = 1.35, scale: float = 800.0) -> Dict[str, float]:
    """
    Retourne les probabilités de victoire, nul et défaite pour un match entre deux équipes.
    C'est le mode "distribution".
    
    :param elo_a: Rating Elo de l'équipe A
    :param elo_b: Rating Elo de l'équipe B
    :param base_goals: Paramètre de moyenne de buts
    :param scale: Facteur d'échelle Elo
    :return: Dictionnaire avec les clés 'win_a', 'draw', 'win_b'
    """
    lambda_a, lambda_b = compute_lambdas(elo_a, elo_b, base_goals, scale)
    return match_probabilities(lambda_a, lambda_b)

def sample_match_score(elo_a: float, elo_b: float, base_goals: float = 1.35, scale: float = 800.0, max_goals: int = 10) -> Tuple[int, int]:
    """
    Tire aléatoirement un score (buts A, buts B) basé sur la distribution de probabilités du modèle Poisson.
    C'est le mode "random".
    
    :param elo_a: Rating Elo de l'équipe A
    :param elo_b: Rating Elo de l'équipe B
    :param base_goals: Paramètre de moyenne de buts
    :param scale: Facteur d'échelle Elo
    :param max_goals: Limite supérieure du nombre de buts pour limiter la taille de la matrice
    :return: Tuple (score_équipe_A, score_équipe_B)
    """
    lambda_a, lambda_b = compute_lambdas(elo_a, elo_b, base_goals, scale)
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
