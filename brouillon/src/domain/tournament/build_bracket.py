from typing import Dict, List, Any

def get_slot_team(slot_str: str, group_standings: Dict[str, List[Dict[str, Any]]]) -> str:
    """
    Récupère l'ID de l'équipe pour un slot simple (ex: '1A', '2B').
    """
    pos = int(slot_str[0]) - 1  # 0 pour 1er, 1 pour 2ème
    group = slot_str[1:]
    return group_standings[group][pos]["teamId"]

def assign_thirds(bracket_matches: List[Dict[str, Any]], best_thirds: List[Dict[str, Any]]) -> Dict[str, str]:
    """
    Assigne les 8 meilleurs troisièmes aux 8 matchs qui les attendent 
    en trouvant une combinaison parfaite via backtracking.
    Retourne un dictionnaire {match_id: team_id}.
    """
    matches_needing_third = [m for m in bracket_matches if m.get("awaySlotOptions")]
    available_groups = [t["group"] for t in best_thirds]
    group_to_team_id = {t["group"]: t["teamId"] for t in best_thirds}
    
    def solve(match_idx: int, used_groups: set) -> Dict[str, str]:
        if match_idx == len(matches_needing_third):
            return {}
            
        match = matches_needing_third[match_idx]
        match_id = match["id"]
        
        for option in match["awaySlotOptions"]:
            group = option[1:]  # "3A" -> "A"
            if group in available_groups and group not in used_groups:
                used_groups.add(group)
                res = solve(match_idx + 1, used_groups)
                if res is not None:
                    res[match_id] = group_to_team_id[group]
                    return res
                used_groups.remove(group)
        return None
        
    assignment = solve(0, set())
    
    if assignment is None:
        print("ATTENTION : Aucune assignation parfaite trouvée pour les 3èmes.")
        # Fallback naïf (théoriquement impossible si bracketRules.json est conforme aux règles FIFA)
        assignment = {}
        used = set()
        for match in matches_needing_third:
            for option in match["awaySlotOptions"]:
                grp = option[1:]
                if grp in available_groups and grp not in used:
                    assignment[match["id"]] = group_to_team_id[grp]
                    used.add(grp)
                    break
                    
    return assignment

def build_round_of_32(bracket_rules: List[Dict[str, Any]], group_standings: Dict[str, List[Dict[str, Any]]], best_thirds: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Construit la liste des matchs des 16e de finale (Round of 32)
    en remplaçant les slots (ex: 1A, 2B, 3C/D/F) par les vrais IDs d'équipes.
    """
    third_assignments = assign_thirds(bracket_rules, best_thirds)
    
    round_32 = []
    for match in bracket_rules:
        new_match = match.copy()
        # Assigner le homeTeam
        new_match["homeTeamId"] = get_slot_team(match["homeSlot"], group_standings)
        
        # Assigner le awayTeam
        if match.get("awaySlotOptions"):
            new_match["awayTeamId"] = third_assignments.get(match["id"])
        else:
            new_match["awayTeamId"] = get_slot_team(match["awaySlot"], group_standings)
            
        new_match["status"] = "scheduled"
        round_32.append(new_match)
        
    return round_32
