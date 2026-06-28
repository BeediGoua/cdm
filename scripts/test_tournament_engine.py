import json
import random
from src.domain.tournament.compute_group_standings import compute_group_standings
from src.domain.tournament.rank_third_placed import rank_third_placed
from src.domain.tournament.build_bracket import build_round_of_32

def test_tournament():
    print("--- Test du Moteur de Tournoi ---")
    
    # 1. Charger les données normalisées
    with open("src/data/normalized/groups.json", "r", encoding="utf-8") as f:
        groups = json.load(f)
        
    with open("src/data/normalized/bracketRules.json", "r", encoding="utf-8") as f:
        bracket_rules = json.load(f)
        round_32_rules = bracket_rules["roundOf32"]

    # 2. Générer des matchs factices pour tous les groupes
    all_group_standings = {}
    for group_name, teams in groups.items():
        # Générer des matchs en round-robin
        matches = []
        for i in range(len(teams)):
            for j in range(i + 1, len(teams)):
                matches.append({
                    "homeTeamId": teams[i],
                    "awayTeamId": teams[j],
                    "homeGoals": random.randint(0, 3),
                    "awayGoals": random.randint(0, 3)
                })
                
        # Calculer le classement
        standings = compute_group_standings(matches, teams)
        all_group_standings[group_name] = standings
        
        print(f"\nGroupe {group_name} :")
        for idx, t in enumerate(standings):
            print(f"  {idx+1}. {t['teamId']} - {t['points']} pts, Diff: {t['goalDifference']}, Buts: {t['goalsFor']}")

    # 3. Classer les 3èmes
    best_thirds = rank_third_placed(all_group_standings)
    print("\n--- Les 8 Meilleurs Troisièmes ---")
    for idx, t in enumerate(best_thirds):
        print(f"  {idx+1}. {t['teamId']} (Gr. {t['group']}) - {t['points']} pts, Diff: {t['goalDifference']}")

    # 4. Construire le bracket des 16e de finale (Round of 32)
    print("\n--- Tableau des 16e de finale (Round of 32) ---")
    round_32_matches = build_round_of_32(round_32_rules, all_group_standings, best_thirds)
    for m in round_32_matches:
        home = m.get("homeTeamId", "???")
        away = m.get("awayTeamId", "???")
        print(f"  {m['id']} : {home} vs {away} (Options away : {m.get('awaySlotOptions')})")
        
    print("\nTest complété avec succès !")

if __name__ == "__main__":
    test_tournament()
