from fastapi import APIRouter, HTTPException
import src.domain.simulation.poisson_model as poisson
import src.domain.models.dixon_coles as dc
import json
from pathlib import Path

router = APIRouter()

NORMALIZED_DIR = Path("src/data/normalized")
CALIBRATION_DIR = Path("outputs/calibration")

def load_teams():
    teams_path = NORMALIZED_DIR / "teams.json"
    if not teams_path.exists():
        raise HTTPException(status_code=404, detail="teams.json missing")
    with teams_path.open("r", encoding="utf-8") as f:
        return {t["id"]: t for t in json.load(f)}

def load_calibration():
    base_goals = 1.35
    scale = 800.0
    try:
        if (CALIBRATION_DIR / "base_goals.json").exists():
            with (CALIBRATION_DIR / "base_goals.json").open("r") as f:
                base_goals = float(json.load(f).get("baseGoals", base_goals))
        if (CALIBRATION_DIR / "scale_search.json").exists():
            with (CALIBRATION_DIR / "scale_search.json").open("r") as f:
                data = json.load(f)
                scale = float(data.get("best", {}).get("scale", data.get("best_scale", scale)))
    except Exception:
        pass
    return base_goals, scale

def get_model_prediction(home_id, away_id, home_elo, away_elo, bg, sc, model_id, model_name, real_results=None):
    if model_id == "V4":
        import src.domain.models.bayesian_v4 as bayesian
        lam_home, lam_away = bayesian.compute_lambdas_v4(home_elo, away_elo, home_id, away_id, real_results, bg, sc)
        probs = bayesian.match_probabilities_v4(lam_home, lam_away)
        matrix = bayesian.score_matrix_v4(lam_home, lam_away)
    elif model_id == "V5":
        import src.domain.models.bivariate_v5 as v5
        hc = {"goal_diff": 0, "rest_days": 5}
        ac = {"goal_diff": 0, "rest_days": 5}
        lam_home, lam_away = v5.compute_lambdas_v5(home_elo, away_elo, hc, ac, bg, sc)
        probs = v5.match_probabilities_v5(lam_home, lam_away)
        matrix = v5.score_matrix_v5(lam_home, lam_away)
    else:
        lam_home, lam_away = poisson.compute_lambdas(home_elo, away_elo, base_goals=bg, scale=sc)
        if model_id == "V3":
            probs = dc.match_probabilities_dc(lam_home, lam_away)
            matrix = dc.score_matrix_dc(lam_home, lam_away)
        else:
            probs = poisson.match_probabilities(lam_home, lam_away)
            matrix = poisson.score_matrix(lam_home, lam_away)
    
    exact_scores = []
    for h in range(len(matrix)):
        for a in range(len(matrix[h])):
            prob = matrix[h][a]
            if prob > 0.001:
                exact_scores.append({"homeGoals": h, "awayGoals": a, "probability": prob})
                
    exact_scores = sorted(exact_scores, key=lambda x: x["probability"], reverse=True)[:5]
    
    return {
        "id": model_id,
        "name": model_name,
        "baseGoals": bg,
        "scale": sc,
        "xgHome": round(lam_home, 2),
        "xgAway": round(lam_away, 2),
        "probabilities": {
            "homeWin": probs["win_a"],
            "draw": probs["draw"],
            "awayWin": probs["win_b"]
        },
        "topExactScores": exact_scores
    }

@router.get("/match")
def predict_match(home: str, away: str):
    teams = load_teams()
    if home not in teams or away not in teams:
        raise HTTPException(status_code=404, detail="Team not found")
        
    # --- Live Elo Tracking Application ---
    # Load real results and compute live elos to reflect current tournament state
    real_results_path = NORMALIZED_DIR.parent / "raw" / "real_results.json"
    if real_results_path.exists():
        with real_results_path.open("r", encoding="utf-8") as f:
            real_results = json.load(f)
        from src.domain.simulation.live_elo import compute_live_elos
        compute_live_elos(teams, real_results)
    # -------------------------------------
        
    home_elo = teams[home].get("elo", 1500)
    away_elo = teams[away].get("elo", 1500)

    
    current_bg, current_scale = load_calibration()
    
    models = [
        get_model_prediction(home, away, home_elo, away_elo, 1.35, 800.0, "V1", "V1 - Poisson Indépendant (Classique)"),
        get_model_prediction(home, away, home_elo, away_elo, current_bg, current_scale, "V2", "V2 - Calibré (Coupe du Monde)"),
        get_model_prediction(home, away, home_elo, away_elo, current_bg, current_scale, "V3", "V3 - Dixon-Coles (Réaliste)"),
        get_model_prediction(home, away, home_elo, away_elo, current_bg, current_scale, "V4", "V4 - Bayésien (Ajusté)", real_results=real_results if 'real_results' in locals() else {}),
        get_model_prediction(home, away, home_elo, away_elo, current_bg, current_scale, "V5", "V5 - Bivarié Covariables", real_results=real_results if 'real_results' in locals() else {})
    ]
    
    return {
        "home": teams[home],
        "away": teams[away],
        "models": models
    }
