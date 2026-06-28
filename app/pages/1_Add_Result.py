# Copyright 2026 gouab
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     https://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import json
from pathlib import Path
from datetime import datetime, timezone

import streamlit as st


REAL_RESULTS_PATH = Path("src/data/raw/real_results.json")
GROUP_MATCHES_PATH = Path("src/data/normalized/groupMatches.json")


def load_json(path: Path):
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def save_json(path: Path, data):
    path.parent.mkdir(parents=True, exist_ok=True)

    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def utc_now():
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


st.title("Ajouter un résultat réel")

group_matches = load_json(GROUP_MATCHES_PATH)

if REAL_RESULTS_PATH.exists():
    real_results = load_json(REAL_RESULTS_PATH)
else:
    real_results = {"groups": {}, "knockouts": {}}

match_options = {
    f"{m['id']} — {m['homeTeamId']} vs {m['awayTeamId']}": m
    for m in group_matches
}

selected_label = st.selectbox("Match", list(match_options.keys()))
selected_match = match_options[selected_label]

home_goals = st.number_input("Buts équipe domicile", min_value=0, step=1)
away_goals = st.number_input("Buts équipe extérieur", min_value=0, step=1)

if st.button("Ajouter / mettre à jour le résultat"):
    match_id = selected_match["id"]

    real_results.setdefault("groups", {})
    real_results.setdefault("knockouts", {})

    real_results["groups"][match_id] = {
        "matchId": match_id,
        "homeTeamId": selected_match["homeTeamId"],
        "awayTeamId": selected_match["awayTeamId"],
        "homeGoals": int(home_goals),
        "awayGoals": int(away_goals),
        "status": "played",
        "source": "streamlit_app",
        "updatedAt": utc_now(),
    }

    save_json(REAL_RESULTS_PATH, real_results)

    st.success(f"Résultat sauvegardé pour {match_id}")
    st.json(real_results["groups"][match_id])

st.info("Après ajout, lance le pipeline live dans le terminal.")
st.code("python -m src.pipeline.run_pipeline --n 1000 --mode live --model-version V1")