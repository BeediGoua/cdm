import math
import src.domain.simulation.poisson_model as poisson
import src.domain.models.dixon_coles as dc

def compute_lambdas_v5(home_elo: float, away_elo: float, home_covars: dict, away_covars: dict, base_goals: float = 1.35, scale: float = 800.0, gamma_1: float = 0.05, gamma_2: float = 0.02) -> tuple[float, float]:
    """
    Régression de Poisson Bivariée avec Covariables (Modèle V5).
    log(lambda_home) = log(base_goals) + log(10) * ((elo_home - elo_away) / scale) + gamma_1 * goal_diff_home + gamma_2 * rest_days_home
    """
    # Calcul initial via Elo (comme V1/V3)
    base_lam_home, base_lam_away = poisson.compute_lambdas(home_elo, away_elo, base_goals, scale)
    
    # Extraction covariables
    # goal_diff = buts marqués - buts encaissés jusqu'à présent dans le tournoi
    # rest_days = jours écoulés depuis le dernier match
    gd_h = home_covars.get('goal_diff', 0)
    rd_h = home_covars.get('rest_days', 5) # 5 jours par défaut si pas de dernier match
    
    gd_a = away_covars.get('goal_diff', 0)
    rd_a = away_covars.get('rest_days', 5)
    
    # Application de l'ajustement exponentiel (car on fait l'addition dans le domaine log)
    # log(lam) = log(base_lam) + gamma_1 * relative_gd + gamma_2 * relative_rd
    # Il est préférable d'utiliser des différences relatives pour ne pas surgonfler systématiquement 
    # le nombre de buts total d'un match (les équipes se neutralisent).
    relative_gd_h = gd_h - gd_a
    relative_rd_h = rd_h - rd_a
    
    relative_gd_a = gd_a - gd_h
    relative_rd_a = rd_a - rd_h
    
    adj_lam_home = base_lam_home * math.exp(gamma_1 * relative_gd_h + gamma_2 * relative_rd_h)
    adj_lam_away = base_lam_away * math.exp(gamma_1 * relative_gd_a + gamma_2 * relative_rd_a)
    
    return adj_lam_home, adj_lam_away

def score_matrix_v5(lam_home: float, lam_away: float, max_goals: int = 10) -> list:
    """Utilise la matrice Dixon-Coles avec les lambdas ajustés par covariables."""
    return dc.score_matrix_dc(lam_home, lam_away, max_goals)

def match_probabilities_v5(lam_home: float, lam_away: float, max_goals: int = 10) -> dict:
    """Utilise les probabilités Dixon-Coles avec les lambdas ajustés par covariables."""
    return dc.match_probabilities_dc(lam_home, lam_away, max_goals)
