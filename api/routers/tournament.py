import json
from pathlib import Path
from fastapi import APIRouter, HTTPException

router = APIRouter()

NORMALIZED_DIR = Path("src/data/normalized")

@router.get("/groups")
def get_groups():
    groups_path = NORMALIZED_DIR / "groups.json"
    teams_path = NORMALIZED_DIR / "teams.json"
    
    if not groups_path.exists() or not teams_path.exists():
         raise HTTPException(status_code=404, detail="Tournament data missing")
         
    with groups_path.open("r", encoding="utf-8") as f:
         groups = json.load(f)
    with teams_path.open("r", encoding="utf-8") as f:
         teams = json.load(f)
         
    real_results_path = Path("src/data/raw/real_results.json")
    real_results = {}
    if real_results_path.exists():
        with real_results_path.open("r", encoding="utf-8") as f:
            data = json.load(f)
            real_results = data.get("groups", {})
            
    team_stats = {
        t["id"]: {
            "id": t["id"], 
            "name": t.get("nameFr") or t.get("nameEn") or t.get("name") or t["id"], 
            "p": 0, "w": 0, "d": 0, "l": 0, "gf": 0, "ga": 0, "gd": 0, "pts": 0
        } for t in teams
    }

    for m_id, res in real_results.items():
        if res.get("status") != "played": continue
        home = res["homeTeamId"]
        away = res["awayTeamId"]
        hg = res["homeGoals"]
        ag = res["awayGoals"]

        if home in team_stats:
            team_stats[home]["p"] += 1
            team_stats[home]["gf"] += hg
            team_stats[home]["ga"] += ag
            team_stats[home]["gd"] = team_stats[home]["gf"] - team_stats[home]["ga"]
            if hg > ag:
                team_stats[home]["w"] += 1
                team_stats[home]["pts"] += 3
            elif hg == ag:
                team_stats[home]["d"] += 1
                team_stats[home]["pts"] += 1
            else:
                team_stats[home]["l"] += 1
        
        if away in team_stats:
            team_stats[away]["p"] += 1
            team_stats[away]["gf"] += ag
            team_stats[away]["ga"] += hg
            team_stats[away]["gd"] = team_stats[away]["gf"] - team_stats[away]["ga"]
            if ag > hg:
                team_stats[away]["w"] += 1
                team_stats[away]["pts"] += 3
            elif ag == hg:
                team_stats[away]["d"] += 1
                team_stats[away]["pts"] += 1
            else:
                team_stats[away]["l"] += 1

    enriched_groups = {}
    for group_name, team_ids in groups.items():
        group_teams = [team_stats[tid] for tid in team_ids if tid in team_stats]
        group_teams.sort(key=lambda x: (x["pts"], x["gd"], x["gf"]), reverse=True)
        enriched_groups[group_name] = group_teams
        
    return enriched_groups

@router.get("/bracket")
def get_bracket():
    bracket_path = NORMALIZED_DIR / "bracketRules.json"
    if not bracket_path.exists():
         raise HTTPException(status_code=404, detail="Bracket data missing")
    with bracket_path.open("r", encoding="utf-8") as f:
         bracket = json.load(f)
    return bracket

@router.get("/matches")
def get_matches():
    matches_path = NORMALIZED_DIR / "groupMatches.json"
    teams_path = NORMALIZED_DIR / "teams.json"
    bracket_path = NORMALIZED_DIR / "bracketRules.json"
    real_results_path = Path("src/data/raw/real_results.json")
    
    if not matches_path.exists() or not teams_path.exists():
         raise HTTPException(status_code=404, detail="Match data missing")
         
    with matches_path.open("r", encoding="utf-8") as f:
         matches = json.load(f)
    with teams_path.open("r", encoding="utf-8") as f:
         teams = json.load(f)
         
    real_results = {}
    if real_results_path.exists():
        with real_results_path.open("r", encoding="utf-8") as f:
             real_results = json.load(f)
         
    teams_by_id = {t["id"]: t["name"] for t in teams if "name" in t}
    
    enriched_matches = []
    for m in matches:
        match_id = m["id"]
        res = real_results.get("groups", {}).get(match_id) or real_results.get("knockouts", {}).get(match_id)
        enriched_matches.append({
            "id": match_id,
            "homeTeamId": m["homeTeamId"],
            "awayTeamId": m["awayTeamId"],
            "homeTeamName": teams_by_id.get(m["homeTeamId"], m["homeTeamId"]),
            "awayTeamName": teams_by_id.get(m["awayTeamId"], m["awayTeamId"]),
            "group": m.get("group", ""),
            "date": m.get("date", ""),
            "matchday": m.get("matchday"),
            "type": "group",
            "played": bool(res),
            "homeScore": res["homeGoals"] if res else None,
            "awayScore": res["awayGoals"] if res else None
        })
        
    if bracket_path.exists():
        with bracket_path.open("r", encoding="utf-8") as f:
            bracket = json.load(f)
            
        for round_key, round_matches in bracket.items():
            for m in round_matches:
                match_id = m["id"]
                res = real_results.get("groups", {}).get(match_id) or real_results.get("knockouts", {}).get(match_id)
                enriched_matches.append({
                    "id": match_id,
                    "homeTeamId": m["homeSlot"],
                    "awayTeamId": m["awaySlot"],
                    "homeTeamName": f"[{m['homeSlot']}]",
                    "awayTeamName": f"[{m['awaySlot']}]",
                    "group": m["round"], # We use the round name (e.g. "Round of 32") as "group"
                    "date": m.get("date", ""),
                    "type": "knockout",
                    "played": bool(res),
                    "homeScore": res["homeGoals"] if res else None,
                    "awayScore": res["awayGoals"] if res else None
                })
        
    return enriched_matches
