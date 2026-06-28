import json
import random
from typing import Dict, Any

from src.domain.simulation.simulate_match import sample_match_score
from src.domain.tournament.compute_group_standings import compute_group_standings
from src.domain.tournament.rank_third_placed import rank_third_placed
from src.domain.tournament.build_bracket import build_round_of_32

def load_tournament_data():
    """Charge les données une seule fois pour accélérer les simulations en boucle."""
    with open("src/data/normalized/teams.json", "r", encoding="utf-8") as f:
        teams_data = json.load(f)
        teams_dict = {t["id"]: t for t in teams_data}
        
    with open("src/data/normalized/groups.json", "r", encoding="utf-8") as f:
        groups = json.load(f)
        
    with open("src/data/normalized/bracketRules.json", "r", encoding="utf-8") as f:
        bracket_rules = json.load(f)
        
    with open("src/data/raw/real_results.json", "r", encoding="utf-8") as f:
        real_results = json.load(f)
        
    return teams_dict, groups, bracket_rules, real_results

def simulate_tournament(teams_dict, groups, bracket_rules, real_results, base_goals=1.35, scale=800.0) -> Dict[str, str]:
    """
    Simule un tournoi complet et retourne le stade final atteint par chaque équipe.
    Exemple de retour : {"fra": "champion", "can": "group", "esp": "quarterFinal"}
    """
    results = {team_id: "group" for team_id in teams_dict.keys()}
    
    # 1. Phase de poules
    all_group_standings = {}
    for group_name, group_teams in groups.items():
        matches = []
        for i in range(len(group_teams)):
            for j in range(i + 1, len(group_teams)):
                t1 = group_teams[i]
                t2 = group_teams[j]
                
                # Créer la clé (ordre alphabétique)
                match_key = f"{min(t1, t2)}_{max(t1, t2)}"
                
                if match_key in real_results.get("groups", {}):
                    real_match = real_results["groups"][match_key]
                    # Respecter qui est home et away dans le json réel
                    if real_match["homeTeamId"] == t1:
                        s1, s2 = real_match["homeGoals"], real_match["awayGoals"]
                    else:
                        s2, s1 = real_match["homeGoals"], real_match["awayGoals"]
                else:
                    s1, s2 = sample_match_score(teams_dict[t1]["elo"], teams_dict[t2]["elo"], base_goals, scale)
                    
                matches.append({
                    "homeTeamId": t1,
                    "awayTeamId": t2,
                    "homeGoals": s1,
                    "awayGoals": s2
                })
        standings = compute_group_standings(matches, group_teams)
        all_group_standings[group_name] = standings
        
    # 2. Meilleurs troisièmes et génération de l'arbre
    best_thirds = rank_third_placed(all_group_standings)
    round_32 = build_round_of_32(bracket_rules["roundOf32"], all_group_standings, best_thirds)
    
    # 3. Phase Finale
    winners_dict = {}
    rounds = [
        ("roundOf32", round_32, "roundOf32", "roundOf16"),
        ("roundOf16", bracket_rules["roundOf16"], "roundOf16", "quarterFinal"),
        ("quarterFinals", bracket_rules["quarterFinals"], "quarterFinal", "semiFinal"),
        ("semiFinals", bracket_rules["semiFinals"], "semiFinal", "final"),
        ("final", bracket_rules["final"], "final", "champion")
    ]
    
    for round_name, match_rules, reached_stage, next_stage in rounds:
        next_round_winners = {}
        for match in match_rules:
            # Récupérer les identifiants des opposants
            if round_name == "roundOf32":
                t1 = match["homeTeamId"]
                t2 = match["awayTeamId"]
            else:
                t1 = winners_dict[match["homeSlot"]]
                t2 = winners_dict[match["awaySlot"]]
                
            # Mettre à jour le statut de l'équipe (si elle joue ce tour, elle l'a atteint)
            results[t1] = reached_stage
            results[t2] = reached_stage
            
            # Vérifier si ce match a déjà été joué
            if match["id"] in real_results.get("knockouts", {}):
                real_match = real_results["knockouts"][match["id"]]
                s1, s2 = real_match["homeGoals"], real_match["awayGoals"]
            else:
                # Simuler le match
                s1, s2 = sample_match_score(teams_dict[t1]["elo"], teams_dict[t2]["elo"], base_goals, scale)
            
            # Gestion du nul (prolongations / tirs au but simulés par 50/50)
            if s1 == s2:
                winner = t1 if random.random() < 0.5 else t2
            elif s1 > s2:
                winner = t1
            else:
                winner = t2
                
            # Enregistrer le vainqueur pour le tour suivant
            # ex: Si id = "M073", le slot du tour suivant est "W73"
            match_num = str(int(match["id"][1:]))
            next_round_winners["W" + match_num] = winner
            
            # Si c'est la finale, désigner le champion
            if round_name == "final":
                results[winner] = "champion"
                
        winners_dict = next_round_winners
        
    return results
