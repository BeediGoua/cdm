from typing import List, Dict, Any

def rank_third_placed(group_standings: Dict[str, List[Dict[str, Any]]]) -> List[Dict[str, Any]]:
    """
    Extrait et classe les équipes arrivées 3ème de chaque groupe pour repêcher les 8 meilleures.
    
    :param group_standings: Dictionnaire où la clé est le nom du groupe ("A", "B") et la valeur est le classement (liste de dicts).
    :return: Liste triée des 8 meilleures équipes repêchées (dicts enrichis avec 'group').
    """
    thirds = []
    
    for group_name, standings in group_standings.items():
        if len(standings) >= 3:
            # L'équipe à l'index 2 est la 3ème (puisque la liste est triée 0-indexée)
            third_team = standings[2].copy()
            third_team["group"] = group_name
            thirds.append(third_team)
            
    # Tri selon les règles (Points > Goal Difference > Goals For > Random)
    # Note: L'attribut _random_tiebreaker pourrait être réintroduit si on veut, 
    # mais en pratique le tri stable gardera l'ordre alphabétique des groupes en cas d'égalité stricte, 
    # ce qui est acceptable pour un MVP. On peut aussi relancer un random.
    import random
    for stat in thirds:
        stat["_random_tiebreaker"] = random.random()
        
    thirds.sort(key=lambda x: (
        x["points"],
        x["goalDifference"],
        x["goalsFor"],
        x["_random_tiebreaker"]
    ), reverse=True)
    
    for stat in thirds:
        del stat["_random_tiebreaker"]
        
    # On ne retourne que les 8 meilleurs
    return thirds[:8]
