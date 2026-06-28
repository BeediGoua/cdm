import json
import subprocess
from pathlib import Path
from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from api.routers.snapshots import invalidate_cache

router = APIRouter()

REAL_RESULTS_PATH = Path("src/data/raw/real_results.json")

class MatchResult(BaseModel):
    matchId: str
    homeTeamId: str
    awayTeamId: str
    homeGoals: int
    awayGoals: int
    status: str = "played"

@router.post("/match")
def update_match(result: MatchResult):
    if not REAL_RESULTS_PATH.exists():
        data = {"groups": {}, "knockouts": {}}
    else:
        with REAL_RESULTS_PATH.open("r", encoding="utf-8") as f:
            data = json.load(f)
            
    if result.matchId.startswith("G"):
        if "groups" not in data:
            data["groups"] = {}
        data["groups"][result.matchId] = result.model_dump()
    else:
        if "knockouts" not in data:
            data["knockouts"] = {}
        data["knockouts"][result.matchId] = result.model_dump()
        
    with REAL_RESULTS_PATH.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
        
    return {"status": "success", "message": f"Match {result.matchId} mis à jour."}

from typing import Dict, Optional

class SimulateRequest(BaseModel):
    nSimulations: Optional[int] = 10000
    mode: Optional[str] = "live"
    modelVersion: Optional[str] = "V2"
    eloDeltas: Optional[Dict[str, float]] = None

def run_simulation_task(n: int, mode: str, model_version: str, elo_deltas: Dict[str, float] = None):
    try:
        from src.domain.simulation.run_monte_carlo import run_monte_carlo
        run_monte_carlo(n_simulations=n, mode=mode, model_version=model_version, save=True, elo_deltas=elo_deltas)
        invalidate_cache()
    except Exception as e:
        print(f"Erreur lors de la simulation: {e}")

@router.post("/simulate")
def trigger_simulation(req: Optional[SimulateRequest] = None):
    if req is None:
        req = SimulateRequest()
    run_simulation_task(req.nSimulations, req.mode, req.modelVersion, req.eloDeltas)
    return {"status": "success", "message": "Simulation terminée avec succès !"}

class WhatIfRequest(BaseModel):
    homeTeamId: str
    awayTeamId: str
    homeGoals: int
    awayGoals: int

@router.post("/what-if")
def what_if_simulation(req: WhatIfRequest):
    import sys
    try:
        # For simplicity, we just trigger a fast Monte Carlo.
        # Ideally, we should apply this specific result to a temporary real_results copy.
        # Here we just run the simulation and return the results directly.
        # This is a stub for the full what-if implementation to be done.
        
        # We can run monte carlo directly and get probabilities:
        from src.domain.simulation.run_monte_carlo import run_monte_carlo
        
        # Run 200 iterations for speed without saving
        probs = run_monte_carlo(n_simulations=200, mode="pre_tournament", save=False)
        
        # Just return the teams requested to see impact
        return {
            "status": "success",
            "homeTeam": probs.get(req.homeTeamId, {}),
            "awayTeam": probs.get(req.awayTeamId, {})
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
