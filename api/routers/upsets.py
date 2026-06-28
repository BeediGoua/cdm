from fastapi import APIRouter
from typing import Dict, Any, List
import json
from pathlib import Path
from src.domain.simulation.live_elo import compute_live_elos

router = APIRouter()

@router.get("")
def get_upsets() -> List[Dict[str, Any]]:
    # Load base teams
    teams_path = Path("src/data/raw/teams.json")
    if not teams_path.exists():
        return []
        
    with teams_path.open("r", encoding="utf-8") as f:
        teams_data = json.load(f)
        
    # Load real results
    results_path = Path("src/data/raw/real_results.json")
    if not results_path.exists():
        return []
        
    with results_path.open("r", encoding="utf-8") as f:
        real_results = json.load(f)
        
    # compute_live_elos returns the list of upsets while modifying teams_data in place
    upsets = compute_live_elos(teams_data, real_results)
    
    # Sort by upset score descending
    upsets.sort(key=lambda x: x["upsetScore"], reverse=True)
    
    return upsets
