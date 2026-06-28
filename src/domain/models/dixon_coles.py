import math
from typing import Dict, Tuple

def poisson_pmf(k: int, lam: float) -> float:
    if k < 0:
        return 0.0
    return (math.exp(-lam) * (lam ** k)) / math.factorial(k)

def tau_function(x: int, y: int, lambda_x: float, lambda_y: float, rho: float) -> float:
    """
    Fonction d'ajustement de Dixon-Coles pour les scores faibles.
    Si rho < 0, cela augmente la probabilité de 0-0 et 1-1, et diminue celle de 1-0 et 0-1.
    """
    if x == 0 and y == 0:
        return max(0.0, 1.0 - lambda_x * lambda_y * rho)
    elif x == 0 and y == 1:
        return max(0.0, 1.0 + lambda_x * rho)
    elif x == 1 and y == 0:
        return max(0.0, 1.0 + lambda_y * rho)
    elif x == 1 and y == 1:
        return max(0.0, 1.0 - rho)
    else:
        return 1.0

def score_matrix_dc(lambda_a: float, lambda_b: float, max_goals: int = 10, rho: float = -0.13) -> list:
    """
    Génère une matrice des probabilités pour tous les scores possibles
    ajustée avec le paramètre de corrélation de Dixon-Coles (rho).
    """
    matrix = []
    
    # Étape 1 : Calcul de la matrice non-normalisée avec ajustement tau
    sum_probs = 0.0
    for i in range(max_goals + 1):
        row = []
        for j in range(max_goals + 1):
            base_prob = poisson_pmf(i, lambda_a) * poisson_pmf(j, lambda_b)
            adjusted_prob = base_prob * tau_function(i, j, lambda_a, lambda_b, rho)
            row.append(adjusted_prob)
            sum_probs += adjusted_prob
        matrix.append(row)
        
    # Étape 2 : Re-normalisation (car la fonction tau peut légèrement déséquilibrer la somme à 1)
    if sum_probs > 0:
        for i in range(max_goals + 1):
            for j in range(max_goals + 1):
                matrix[i][j] /= sum_probs
                
    return matrix

def match_probabilities_dc(lambda_a: float, lambda_b: float, max_goals: int = 10, rho: float = -0.13) -> Dict[str, float]:
    """
    Calcule les probabilités de victoire (A ou B) et de match nul
    en utilisant la matrice de Dixon-Coles.
    """
    matrix = score_matrix_dc(lambda_a, lambda_b, max_goals, rho)
    
    prob_win_a = 0.0
    prob_draw = 0.0
    prob_win_b = 0.0
    
    for i in range(max_goals + 1):
        for j in range(max_goals + 1):
            if i > j:
                prob_win_a += matrix[i][j]
            elif i == j:
                prob_draw += matrix[i][j]
            else:
                prob_win_b += matrix[i][j]
                
    return {
        "win_a": prob_win_a,
        "draw": prob_draw,
        "win_b": prob_win_b
    }
