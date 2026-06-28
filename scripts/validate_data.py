import json
import os

DATA_DIR = os.path.join("src", "data", "normalized")

def load_json(filename):
    with open(os.path.join(DATA_DIR, filename), 'r', encoding='utf-8') as f:
        return json.load(f)

def validate():
    print("Chargement des données...")
    teams = load_json("teams.json")
    groups = load_json("groups.json")
    matches = load_json("groupMatches.json")
    bracket = load_json("bracketRules.json")
    venues = load_json("venues.json")
    
    errors = []

    # 1. Teams: check if all have Elo and are valid
    team_ids = set()
    for t in teams:
        if "id" not in t:
            errors.append("Team manquante d'ID: " + str(t))
            continue
        team_ids.add(t["id"])
        if "elo" not in t or t["elo"] is None:
            errors.append(f"Team {t['id']} n'a pas d'Elo.")

    # 2. Groups: check if all teams exist
    group_team_count = 0
    for g_name, g_teams in groups.items():
        for t_id in g_teams:
            group_team_count += 1
            if t_id not in team_ids:
                errors.append(f"Team {t_id} dans le groupe {g_name} n'existe pas dans teams.json.")
    
    if group_team_count != 48:
        errors.append(f"Nombre total d'équipes dans les groupes : {group_team_count} (attendu: 48)")

    # 3. Matches: check if teams exist and matchday is present
    for m in matches:
        if "homeTeamId" in m and m["homeTeamId"] not in team_ids:
            errors.append(f"Match {m.get('id')} : homeTeamId {m['homeTeamId']} n'existe pas.")
        if "awayTeamId" in m and m["awayTeamId"] not in team_ids:
            errors.append(f"Match {m.get('id')} : awayTeamId {m['awayTeamId']} n'existe pas.")
        if "matchday" not in m:
            errors.append(f"Match {m.get('id')} : n'a pas de champ 'matchday'.")

    # 4. Bracket Rules: check awaySlotOptions
    for b in bracket:
        if "awaySlotOptions" in b:
            # Example check: should be list like ["3A", "3B", "3C"]
            opts = b["awaySlotOptions"]
            if not isinstance(opts, list):
                errors.append(f"Bracket {b.get('id')} : awaySlotOptions n'est pas une liste.")
            else:
                for opt in opts:
                    if not opt.startswith("3") or len(opt) != 2:
                        errors.append(f"Bracket {b.get('id')} : option {opt} dans awaySlotOptions semble invalide (attendu ex: '3A').")

    # 5. Venues: ensure it's not empty and valid (if there are rules)
    if not venues:
        errors.append("venues.json est vide.")

    print(f"Validation terminée. {len(errors)} erreurs trouvées.")
    for e in errors:
        print(" -", e)

if __name__ == "__main__":
    validate()
