import json
from pathlib import Path

import streamlit as st


SNAPSHOT_PATH = Path("outputs/snapshots/snapshot_current.json")


st.set_page_config(
    page_title="World Cup 2026 Simulator",
    layout="wide",
)


st.title("World Cup 2026 — Probabilistic Simulator")

if not SNAPSHOT_PATH.exists():
    st.warning("Aucun snapshot trouvé. Lance d'abord le pipeline.")
    st.code("python -m src.pipeline.run_pipeline --n 1000 --mode pre_tournament")
    st.stop()

with SNAPSHOT_PATH.open("r", encoding="utf-8") as f:
    snapshot = json.load(f)

results = snapshot.get("results", {})

st.subheader("Configuration du snapshot")

col1, col2, col3, col4 = st.columns(4)

col1.metric("Model", snapshot.get("modelVersion"))
col2.metric("State", snapshot.get("state"))
col3.metric("Simulations", snapshot.get("nSimulations"))
col4.metric("Teams", len(results))

st.subheader("Top favoris champion")

rows = []

for team_id, data in results.items():
    rows.append({
        "teamId": team_id,
        "name": data.get("name", team_id),
        "roundOf32": data.get("roundOf32", 0),
        "roundOf16": data.get("roundOf16", 0),
        "quarterFinal": data.get("quarterFinal", 0),
        "semiFinal": data.get("semiFinal", 0),
        "final": data.get("final", 0),
        "champion": data.get("champion", 0),
    })

rows = sorted(rows, key=lambda x: x["champion"], reverse=True)

st.dataframe(rows, use_container_width=True)