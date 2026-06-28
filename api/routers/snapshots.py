import json
import time
from pathlib import Path
from fastapi import APIRouter, HTTPException

router = APIRouter()

SNAPSHOT_DIR = Path("outputs/snapshots")
CURRENT_SNAPSHOT_PATH = SNAPSHOT_DIR / "snapshot_current.json"

# Global in-memory cache
_snapshot_cache = {
    "data": None,
    "last_modified": 0
}

def invalidate_cache():
    _snapshot_cache["data"] = None
    _snapshot_cache["last_modified"] = 0

@router.get("/current")
def get_current_snapshot():
    if not CURRENT_SNAPSHOT_PATH.exists():
        raise HTTPException(status_code=404, detail="No current snapshot found. Run Monte Carlo pipeline first.")
    
    mtime = CURRENT_SNAPSHOT_PATH.stat().st_mtime
    
    # Return cached data if file hasn't changed
    if _snapshot_cache["data"] is not None and _snapshot_cache["last_modified"] == mtime:
        return _snapshot_cache["data"]
        
    # Read and cache
    with CURRENT_SNAPSHOT_PATH.open("r", encoding="utf-8") as f:
        data = json.load(f)
        
    _snapshot_cache["data"] = data
    _snapshot_cache["last_modified"] = mtime
        
    return data

@router.get("/list")
def list_snapshots():
    if not SNAPSHOT_DIR.exists():
        return []
    
    files = []
    for f in SNAPSHOT_DIR.glob("*.json"):
        if f.name != "snapshot_current.json":
            files.append({
                "filename": f.name,
                "created_at": f.stat().st_mtime
            })
    return sorted(files, key=lambda x: x["created_at"], reverse=True)

@router.get("/deltas")
def get_deltas(metric: str = "champion", model: str = "V3", team: str = None):
    if not SNAPSHOT_DIR.exists():
        return {"message": "Aucun snapshot trouvé"}
        
    files = []
    # Load all snapshots except current
    for f in SNAPSHOT_DIR.glob("*.json"):
        if f.name == "snapshot_current.json":
            continue
        files.append({
            "path": f,
            "created_at": f.stat().st_mtime
        })
        
    if not files:
        return {"message": "Pas assez de snapshots pour calculer un delta"}
        
    files.sort(key=lambda x: x["created_at"])
    
    def load_snap_standard(p):
        with p.open("r", encoding="utf-8") as f:
            return json.load(f)
            
    latest_full = load_snap_standard(files[-1]["path"])
    latest_results = latest_full.get("results", {})
    all_team_names = sorted([tdata.get("name", tid) for tid, tdata in latest_results.items()])
    all_team_ids = sorted([tid for tid in latest_results.keys()])
    
    valid_metrics = ["roundOf32", "roundOf16", "quarterFinal", "semiFinal", "final", "champion"]
    if metric not in valid_metrics:
        metric = "champion"
        
    if model == "COMPARE" and team:
        history_data = []
        for snapshot_meta in files:
            with snapshot_meta["path"].open("r", encoding="utf-8") as f:
                full_data = json.load(f)
                
            time_label = full_data.get("createdAt", "").split("T")[-1][:5]
            fname = snapshot_meta["path"].name.lower()
            if "_j1_" in fname:
                time_label = "J1 " + time_label
            elif "_j2_" in fname:
                time_label = "J2 " + time_label
            elif "_j3_" in fname:
                time_label = "J3 " + time_label
            elif "live" in full_data.get("state", "live"):
                time_label = "Live " + time_label
            else:
                time_label = "Pre " + time_label
                
            entry = {"time": time_label}
            comps = full_data.get("comparisons", {})
            if comps:
                entry["V1"] = round(comps.get("V1", {}).get(team, {}).get(metric, 0) * 100, 1)
                entry["V2"] = round(comps.get("V2", {}).get(team, {}).get(metric, 0) * 100, 1)
                entry["V3"] = round(comps.get("V3", {}).get(team, {}).get(metric, 0) * 100, 1)
                entry["V4"] = round(comps.get("V4", {}).get(team, {}).get(metric, 0) * 100, 1)
                entry["V5"] = round(comps.get("V5", {}).get(team, {}).get(metric, 0) * 100, 1)
            else:
                # Fallback to single result for older snapshots
                res = full_data.get("results", {}).get(team, {}).get(metric, 0)
                entry["V1"] = round(res * 100, 1)
                entry["V2"] = round(res * 100, 1)
                entry["V3"] = round(res * 100, 1)
                entry["V4"] = round(res * 100, 1)
                entry["V5"] = round(res * 100, 1)
                
            history_data.append(entry)
            
        return {
            "status": "ok",
            "metric": metric,
            "mode": "COMPARE",
            "history": history_data,
            "topTeams": ["V1", "V2", "V3", "V4", "V5"],
            "allTeams": ["V1", "V2", "V3", "V4", "V5"],
            "availableTeams": [{"id": tid, "name": latest_results[tid].get("name", tid)} for tid in all_team_ids],
            "global": None,
            "recent": None
        }

    # STANDARD MODE (V1, V2 or V3)
    def load_snap(p, m=model):
        with p.open("r", encoding="utf-8") as f:
            data = json.load(f)
            if m and m != "V3" and "comparisons" in data and m in data["comparisons"]:
                return data["comparisons"][m]
            return data.get("results", {})
            
    latest = load_snap(files[-1]["path"])
    previous = load_snap(files[-2]["path"]) if len(files) > 1 else latest
    earliest = load_snap(files[0]["path"])
    
    def calc_delta(old_snap, new_snap):
        deltas = []
        for tid, tdata in new_snap.items():
            new_val = tdata.get(metric, 0)
            old_val = old_snap.get(tid, {}).get(metric, 0)
            diff = new_val - old_val
            deltas.append({
                "teamId": tid,
                "name": tdata.get("name", tid),
                "old": old_val,
                "new": new_val,
                "delta": diff
            })
        deltas.sort(key=lambda x: x["delta"], reverse=True)
        return {
            "topWinner": deltas[0] if deltas and deltas[0]["delta"] > 0 else None,
            "topLoser": deltas[-1] if deltas and deltas[-1]["delta"] < 0 else None,
            "all": deltas
        }
        
    top_teams_now = sorted(latest.items(), key=lambda x: x[1].get(metric, 0), reverse=True)[:6]
    top_ids = [t[0] for t in top_teams_now]
    top_names = [latest[tid]["name"] for tid in top_ids]
    
    history_data = []
    for snapshot_meta in files:
        snap_data = load_snap(snapshot_meta["path"])
        with snapshot_meta["path"].open("r", encoding="utf-8") as f:
            full_data = json.load(f)
            time_label = full_data.get("createdAt", "").split("T")[-1][:5]
            fname = snapshot_meta["path"].name.lower()
            if "_j1_" in fname:
                time_label = "J1 " + time_label
            elif "_j2_" in fname:
                time_label = "J2 " + time_label
            elif "_j3_" in fname:
                time_label = "J3 " + time_label
            elif "live" in full_data.get("state", "live"):
                time_label = "Live " + time_label
            else:
                time_label = "Pre " + time_label
                
            entry = {"time": time_label}
            for tid, tdata in latest.items():
                team_name = tdata.get("name", tid)
                entry[team_name] = round(snap_data.get(tid, {}).get(metric, 0) * 100, 1)
            history_data.append(entry)

    return {
        "status": "ok",
        "metric": metric,
        "mode": "STANDARD",
        "global": calc_delta(earliest, latest),
        "recent": calc_delta(previous, latest),
        "history": history_data,
        "topTeams": top_names,
        "allTeams": all_team_names,
        "availableTeams": [{"id": tid, "name": latest_results[tid].get("name", tid)} for tid in all_team_ids]
    }
