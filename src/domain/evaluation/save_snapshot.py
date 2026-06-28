# src/domain/evaluation/save_snapshot.py
"""Helpers to build and save Monte Carlo snapshots.

Keep this file small and side-effect free so it can be safely imported
by scripts and test helpers.
"""
from __future__ import annotations

import json
from pathlib import Path
from datetime import datetime, timezone
from typing import Any, Dict, Optional


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def build_snapshot(
    results: Dict[str, Any],
    model_version: str,
    state: str,
    n_simulations: int,
    base_goals: float,
    scale: float,
    metadata: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    created_at = utc_now_iso()

    snapshot_id = (
        f"{model_version.lower()}_"
        f"{state.lower()}_"
        f"{created_at.replace(':', '').replace('-', '').replace('+0000', 'z')}"
    )

    return {
        "snapshotId": snapshot_id,
        "modelVersion": model_version,
        "state": state,
        "nSimulations": n_simulations,
        "baseGoals": base_goals,
        "scale": scale,
        "createdAt": created_at,
        "metadata": metadata or {},
        "results": results,
    }


def save_snapshot(
    snapshot: Dict[str, Any],
    output_dir: str = "outputs/snapshots",
    filename: Optional[str] = None,
) -> str:
    out_dir = Path(output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    if filename is None:
        filename = f"{snapshot['snapshotId']}.json"

    path = out_dir / filename

    with path.open("w", encoding="utf-8") as f:
        json.dump(snapshot, f, ensure_ascii=False, indent=2)

    # Always update the 'current' snapshot so the dashboard and API serve the latest data
    current_path = out_dir / "snapshot_current.json"
    with current_path.open("w", encoding="utf-8") as f:
        json.dump(snapshot, f, ensure_ascii=False, indent=2)

    return str(path)