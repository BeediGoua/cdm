import time
from collections import defaultdict
from src.domain.simulation.simulate_tournament import simulate_tournament, load_tournament_data

def run_monte_carlo(n_simulations: int = 1000):
    """
    Répète le tournoi N fois et calcule les probabilités d'atteindre chaque stade
    pour chaque équipe engagée.
    """
    teams_dict, groups, bracket_rules, real_results = load_tournament_data()
    
    # stats[team_id][stage] = nombre de fois que le stade a été atteint
    stats = defaultdict(lambda: defaultdict(int))
    hierarchy = ["group", "roundOf32", "roundOf16", "quarterFinal", "semiFinal", "final", "champion"]
    
    start_time = time.time()
    print(f"Lancement de {n_simulations} simulations Monte Carlo...")
    
    for i in range(n_simulations):
        results = simulate_tournament(teams_dict, groups, bracket_rules, real_results)
        
        for team, max_stage in results.items():
            # Si l'équipe a atteint la finale, elle a de facto atteint les 16e, 8e, quarts...
            # On incrémente tous les compteurs jusqu'au stade maximal atteint
            idx = hierarchy.index(max_stage)
            for j in range(1, idx + 1):
                stats[team][hierarchy[j]] += 1
                
        if (i + 1) % 1000 == 0:
            print(f"  {i+1} simulations terminées...")
            
    end_time = time.time()
    print(f"Terminé en {end_time - start_time:.2f} secondes.")
    
    # Transformation des compteurs en pourcentages
    probabilities = {}
    for team, st in stats.items():
        team_name = teams_dict[team].get("nameFr")
        if not team_name:
            team_name = teams_dict[team].get("nameEn", team)
        probabilities[team] = {
            "name": team_name,
            "roundOf32": st["roundOf32"] / n_simulations,
            "roundOf16": st["roundOf16"] / n_simulations,
            "quarterFinal": st["quarterFinal"] / n_simulations,
            "semiFinal": st["semiFinal"] / n_simulations,
            "final": st["final"] / n_simulations,
            "champion": st["champion"] / n_simulations
        }
        
    import json
    import os
    os.makedirs("snapshots", exist_ok=True)
    with open("snapshots/snapshot_current.json", "w", encoding="utf-8") as f:
        json.dump(probabilities, f, indent=2)
    print("Résultats sauvegardés dans snapshots/snapshot_current.json")
        
    return probabilities

if __name__ == "__main__":
    # Test avec 1000 simulations par défaut
    probs = run_monte_carlo(1000)
    
    # Affichage du Top 15 des favoris (trié par chances de titre)
    sorted_teams = sorted(probs.items(), key=lambda x: x[1]["champion"], reverse=True)
    
    print("\n=== TOP 15 FAVORIS ===")
    print(f"{'Equipe':<20} | {'Champion':<9} | {'Finale':<9} | {'Demies':<9} | {'Quarts':<9} | {'8es':<9}")
    print("-" * 75)
    for team_id, prob in sorted_teams[:15]:
        print(f"{prob['name']:<20} | {prob['champion']*100:>7.1f}% | {prob['final']*100:>7.1f}% | {prob['semiFinal']*100:>7.1f}% | {prob['quarterFinal']*100:>7.1f}% | {prob['roundOf16']*100:>7.1f}%")
