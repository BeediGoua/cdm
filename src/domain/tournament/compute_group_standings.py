import random
from typing import List, Dict, Any

def compute_group_standings(matches: List[Dict[str, Any]], group_teams: List[str]) -> List[Dict[str, Any]]:
    """
    Calcule le classement d'un groupe à partir des matchs joués ou simulés.
    
    :param matches: Liste des matchs avec 'homeTeamId', 'awayTeamId', 'homeGoals', 'awayGoals'
    :param group_teams: Liste des identifiants des équipes du groupe
    :return: Liste de dictionnaires représentant le classement, triée selon les règles FIFA
    """
    # Initialisation des statistiques pour chaque équipe
    standings = {
        team_id: {
            "teamId": team_id,
            "played": 0,
            "wins": 0,
            "draws": 0,
            "losses": 0,
            "goalsFor": 0,
            "goalsAgainst": 0,
            "goalDifference": 0,
            "points": 0
        }
        for team_id in group_teams
    }
    
    # Remplissage des statistiques à partir des matchs
    for match in matches:
        home_id = match.get("homeTeamId")
        away_id = match.get("awayTeamId")
        
        # S'assurer que le match concerne bien les équipes de ce groupe et qu'il a un score
        if home_id in standings and away_id in standings and "homeGoals" in match and "awayGoals" in match:
            home_goals = match["homeGoals"]
            away_goals = match["awayGoals"]
            
            standings[home_id]["played"] += 1
            standings[away_id]["played"] += 1
            
            standings[home_id]["goalsFor"] += home_goals
            standings[away_id]["goalsFor"] += away_goals
            
            standings[home_id]["goalsAgainst"] += away_goals
            standings[away_id]["goalsAgainst"] += home_goals
            
            if home_goals > away_goals:
                standings[home_id]["wins"] += 1
                standings[home_id]["points"] += 3
                standings[away_id]["losses"] += 1
            elif home_goals == away_goals:
                standings[home_id]["draws"] += 1
                standings[away_id]["draws"] += 1
                standings[home_id]["points"] += 1
                standings[away_id]["points"] += 1
            else:
                standings[away_id]["wins"] += 1
                standings[away_id]["points"] += 3
                standings[home_id]["losses"] += 1
    
    # Mise à jour des différences de buts
    for team_id in group_teams:
        standings[team_id]["goalDifference"] = standings[team_id]["goalsFor"] - standings[team_id]["goalsAgainst"]
        
    # Transformation en liste
    standings_list = list(standings.values())
    
    # Tri selon les règles (Départage MVP)
    # Python trie de manière stable, donc on peut ajouter du hasard d'abord, puis trier par les critères principaux.
    # On ajoute une valeur aléatoire pour le départage "fair-play/manuel" en dernier recours.
    for stat in standings_list:
        stat["_random_tiebreaker"] = random.random()
        
    standings_list.sort(key=lambda x: (
        x["points"],
        x["goalDifference"],
        x["goalsFor"],
        x["_random_tiebreaker"]
    ), reverse=True)
    
    # Nettoyage de la clé temporaire
    for stat in standings_list:
        del stat["_random_tiebreaker"]
        
    return standings_list
