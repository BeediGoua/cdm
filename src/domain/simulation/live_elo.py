import math
import json
import hashlib
from pathlib import Path
from typing import Dict, Any

def compute_live_elos(teams_dict: Dict[str, Any], real_results: Dict[str, Any]):
    """
    Modifie le dictionnaire teams_dict EN PLACE pour mettre à jour les Elos
    en fonction des matchs joués contenus dans real_results.
    Retourne une liste des plus grands "miracles" (upsets) détectés chronologiquement.
    """
    cache_dir = Path("outputs/cache")
    cache_dir.mkdir(parents=True, exist_ok=True)
    cache_file = cache_dir / "live_elo_cache.json"
    
    results_str = json.dumps(real_results, sort_keys=True)
    results_hash = hashlib.md5(results_str.encode('utf-8')).hexdigest()
    
    if cache_file.exists():
        try:
            with cache_file.open("r", encoding="utf-8") as f:
                cache_data = json.load(f)
                if cache_data.get("hash") == results_hash:
                    for team_id, cached_elo in cache_data.get("elos", {}).items():
                        if team_id in teams_dict:
                            teams_dict[team_id]["elo"] = cached_elo
                    return cache_data.get("upsets", [])
        except Exception:
            pass

    played_matches = []
    upsets = []
    
    # Extraire les matchs de poule
    groups = real_results.get("groups", {})
    for match_id, match_data in groups.items():
        if match_data.get("homeGoals") is not None and match_data.get("awayGoals") is not None:
            played_matches.append({
                "id": str(match_id),
                "type": "group",
                "home": match_data["homeTeamId"],
                "away": match_data["awayTeamId"],
                "hg": int(match_data["homeGoals"]),
                "ag": int(match_data["awayGoals"])
            })
            
    # Extraire les matchs à élimination directe
    knockouts = real_results.get("knockouts", {})
    for match_id, match_data in knockouts.items():
        if match_data.get("homeGoals") is not None and match_data.get("awayGoals") is not None:
            played_matches.append({
                "id": str(match_id),
                "type": "knockout",
                "home": match_data["homeTeamId"],
                "away": match_data["awayTeamId"],
                "hg": int(match_data["homeGoals"]),
                "ag": int(match_data["awayGoals"])
            })
            
    # Trier chronologiquement selon le numéro du match pour une évolution Elo mathématiquement juste
    def extract_number(match_id_str):
        digits = "".join(c for c in match_id_str if c.isdigit())
        return int(digits) if digits else 0
        
    played_matches.sort(key=lambda x: extract_number(x["id"]))
    
    # Mise à jour incrémentale de l'Elo
    for match in played_matches:
        home_id = match["home"]
        away_id = match["away"]
        
        if home_id not in teams_dict or away_id not in teams_dict:
            continue
            
        elo_home = float(teams_dict[home_id]["elo"])
        elo_away = float(teams_dict[away_id]["elo"])
        
        # 1. DYNAMIC K-FACTOR : Plus d'enjeu = Plus d'impact psychologique
        base_k = 40 if match["type"] == "group" else 60
        
        # Probabilité attendue (E)
        e_home = 1.0 / (1.0 + 10.0 ** ((elo_away - elo_home) / 400.0))
        e_away = 1.0 - e_home
        
        # Résultat réel (W)
        hg = match["hg"]
        ag = match["ag"]
        
        if hg > ag:
            w_home, w_away = 1.0, 0.0
        elif hg < ag:
            w_home, w_away = 0.0, 1.0
        else:
            w_home, w_away = 0.5, 0.5
            
        # 2. MARGIN OF VICTORY (G-Factor)
        # Formule dérivée des standards statistiques : ln(abs(diff) + 1.5) ou similaire.
        # Attention aux matchs nuls (diff = 0) où G doit valoir un peu moins ou équivalent à 1.
        goal_diff = abs(hg - ag)
        
        if goal_diff == 0:
            g_factor = 1.0
        elif goal_diff == 1:
            g_factor = 1.0
        elif goal_diff == 2:
            g_factor = 1.5
        elif goal_diff == 3:
            g_factor = 1.75
        else:
            g_factor = 1.75 + (goal_diff - 3) / 8.0  # Croissance lente (diminishing returns)
            
        # Nouveaux Elos pondérés par K et G
        teams_dict[home_id]["elo"] = elo_home + base_k * g_factor * (w_home - e_home)
        teams_dict[away_id]["elo"] = elo_away + base_k * g_factor * (w_away - e_away)
        
        # 3. DÉTECTION DE MIRACLES (Upsets)
        if w_home == 1.0 and e_home < 0.40:
            upsets.append({
                "matchId": match["id"],
                "winnerId": home_id,
                "loserId": away_id,
                "winnerName": teams_dict[home_id].get("nameFr", home_id),
                "loserName": teams_dict[away_id].get("nameFr", away_id),
                "score": f"{hg} - {ag}",
                "expectedProb": e_home,
                "upsetScore": (1.0 - e_home) * 100,
                "stage": match["type"]
            })
        elif w_away == 1.0 and e_away < 0.40:
            upsets.append({
                "matchId": match["id"],
                "winnerId": away_id,
                "loserId": home_id,
                "winnerName": teams_dict[away_id].get("nameFr", away_id),
                "loserName": teams_dict[home_id].get("nameFr", home_id),
                "score": f"{hg} - {ag}",
                "expectedProb": e_away,
                "upsetScore": (1.0 - e_away) * 100,
                "stage": match["type"]
            })
            
    try:
        cache_data = {
            "hash": results_hash,
            "elos": {team_id: data["elo"] for team_id, data in teams_dict.items()},
            "upsets": upsets
        }
        with cache_file.open("w", encoding="utf-8") as f:
            json.dump(cache_data, f, indent=2)
    except Exception as e:
        print(f"[WARN] Impossible d'écrire le cache Live Elo: {e}")

    return upsets
