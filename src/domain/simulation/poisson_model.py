import math
from typing import Dict, Tuple

def compute_lambdas(elo_a: float, elo_b: float, base_goals: float = 1.35, scale: float = 800.0) -> Tuple[float, float]:
    """
    Calcule les moyennes de buts attendus (lambda) pour les deux équipes
    basées sur leur différence de points Elo.
    
    :param elo_a: Rating Elo de l'équipe A
    :param elo_b: Rating Elo de l'équipe B
    :param base_goals: Moyenne globale de buts marqués par une équipe par match
    :param scale: Facteur d'échelle contrôlant l'impact de la différence Elo
    :return: (lambda_a, lambda_b)
    """
    diff = elo_a - elo_b
    lambda_a = base_goals * math.exp(diff / scale)
    lambda_b = base_goals * math.exp(-diff / scale)
    
    return lambda_a, lambda_b

def poisson_pmf(k: int, lam: float) -> float:
    """
    Fonction de masse de probabilité (PMF) pour la loi de Poisson.
    Calcule la probabilité de marquer k buts sachant une moyenne de lam.
    
    :param k: Nombre de buts
    :param lam: Moyenne attendue de buts (lambda)
    :return: Probabilité P(X = k)
    """
    if k < 0:
        return 0.0
    return (math.exp(-lam) * (lam ** k)) / math.factorial(k)

def score_matrix(lambda_a: float, lambda_b: float, max_goals: int = 10) -> list:
    """
    Génère une matrice des probabilités pour tous les scores possibles
    jusqu'à max_goals.
    
    :param lambda_a: Moyenne de buts attendue pour l'équipe A
    :param lambda_b: Moyenne de buts attendue pour l'équipe B
    :param max_goals: Nombre maximum de buts simulés pour chaque équipe
    :return: Matrice 2D (liste de listes) où matrix[i][j] = P(A=i, B=j)
    """
    matrix = []
    for i in range(max_goals + 1):
        row = []
        for j in range(max_goals + 1):
            prob = poisson_pmf(i, lambda_a) * poisson_pmf(j, lambda_b)
            row.append(prob)
        matrix.append(row)
        
    return matrix

def match_probabilities(lambda_a: float, lambda_b: float, max_goals: int = 10) -> Dict[str, float]:
    """
    Calcule les probabilités de victoire (A ou B) et de match nul
    en sommant les probabilités de la matrice de scores.
    
    :param lambda_a: Moyenne de buts attendue pour l'équipe A
    :param lambda_b: Moyenne de buts attendue pour l'équipe B
    :param max_goals: Nombre maximum de buts pris en compte pour la somme
    :return: Dictionnaire avec les clés 'win_a', 'draw', 'win_b'
    """
    matrix = score_matrix(lambda_a, lambda_b, max_goals)
    
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

if __name__ == "__main__":
    # Test avec l'exemple de STEPS.md
    # France (2062) vs Canada (1780)
    elo_fra = 2062
    elo_can = 1780
    bg = 1.35
    sc = 800.0
    
    lam_fra, lam_can = compute_lambdas(elo_fra, elo_can, base_goals=bg, scale=sc)
    print(f"France Elo: {elo_fra}, Canada Elo: {elo_can}")
    print(f"Lambda France : {lam_fra:.2f}")
    print(f"Lambda Canada : {lam_can:.2f}")
    
    probs = match_probabilities(lam_fra, lam_can)
    print("\nProbabilités du match :")
    print(f"Victoire France : {probs['win_a'] * 100:.1f}%")
    print(f"Match Nul :       {probs['draw'] * 100:.1f}%")
    print(f"Victoire Canada : {probs['win_b'] * 100:.1f}%")
