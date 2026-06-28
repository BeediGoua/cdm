import src.domain.simulation.poisson_model as poisson
import src.domain.models.dixon_coles as dc

def compute_lambdas_v4(home_elo: float, away_elo: float, home_id: str, away_id: str, real_results: dict, base_goals: float = 1.35, scale: float = 800.0) -> tuple[float, float]:
    """
    Calcule les lambdas ajustés via inférence Bayésienne (Gamma-Poisson).
    """
    # 1. Prior: Expected lambdas based on Elo alone (from poisson_model)
    prior_lam_home, prior_lam_away = poisson.compute_lambdas(home_elo, away_elo, base_goals, scale)
    
    # Extract goals scored and matches played in the tournament from real_results
    def get_team_stats(team_id: str):
        goals_scored = 0
        matches_played = 0
        if not real_results:
            return goals_scored, matches_played
            
        groups = real_results.get("groups", {})
        knockouts = real_results.get("knockouts", {})
        
        all_matches = list(groups.values()) + list(knockouts.values())
        for m in all_matches:
            if m.get("status") == "played":
                if m.get("homeTeamId") == team_id:
                    goals_scored += m.get("homeGoals", 0)
                    matches_played += 1
                elif m.get("awayTeamId") == team_id:
                    goals_scored += m.get("awayGoals", 0)
                    matches_played += 1
        return goals_scored, matches_played

    h_goals, h_matches = get_team_stats(home_id)
    a_goals, a_matches = get_team_stats(away_id)
    
    # 2. Bayesian Update (Gamma-Poisson conjugate)
    # We assign a weight to our prior to decide how quickly it adapts to tournament performance
    # prior_weight represents the confidence in the Prior equivalent to a number of matches.
    # We use 3.0 so the prior is roughly equal to a full group stage worth of evidence.
    prior_weight = 3.0
    
    # Home team update
    alpha_prior_h = prior_lam_home * prior_weight
    beta_prior_h = prior_weight
    alpha_post_h = alpha_prior_h + h_goals
    beta_post_h = beta_prior_h + h_matches
    post_lam_home = alpha_post_h / beta_post_h
    
    # Away team update
    alpha_prior_a = prior_lam_away * prior_weight
    beta_prior_a = prior_weight
    alpha_post_a = alpha_prior_a + a_goals
    beta_post_a = beta_prior_a + a_matches
    post_lam_away = alpha_post_a / beta_post_a
    
    return post_lam_home, post_lam_away

def score_matrix_v4(lam_home: float, lam_away: float, max_goals: int = 10) -> list:
    """Utilise la matrice Dixon-Coles avec les lambdas Bayésiens."""
    return dc.score_matrix_dc(lam_home, lam_away, max_goals)

def match_probabilities_v4(lam_home: float, lam_away: float, max_goals: int = 10) -> dict:
    """Utilise les probabilités Dixon-Coles avec les lambdas Bayésiens."""
    return dc.match_probabilities_dc(lam_home, lam_away, max_goals)
