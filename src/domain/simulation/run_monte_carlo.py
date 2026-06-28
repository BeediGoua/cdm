import argparse
import time
import math
import os
import concurrent.futures
from typing import Dict, Any

import src.domain.simulation.simulate_tournament as sim_tournament_module
import src.domain.evaluation.save_snapshot as snap_module


STAGES = [
    "group",
    "roundOf32",
    "roundOf16",
    "quarterFinal",
    "semiFinal",
    "final",
    "champion",
]


def init_stats(team_ids):
    return {
        team_id: {
            "roundOf32": 0,
            "roundOf16": 0,
            "quarterFinal": 0,
            "semiFinal": 0,
            "final": 0,
            "champion": 0,
        }
        for team_id in team_ids
    }


def stage_index(stage: str) -> int:
    if stage not in STAGES:
        raise ValueError(f"Stage inconnu: {stage}")
    return STAGES.index(stage)


def increment_reached_stages(stats: Dict[str, Dict[str, int]], team_id: str, max_stage: str):
    """
    Si une équipe atteint les demies, elle a aussi atteint :
    roundOf32, roundOf16, quarterFinal, semiFinal.
    """
    max_idx = stage_index(max_stage)

    for stage in STAGES[1:max_idx + 1]:
        stats[team_id][stage] += 1

def worker_simulate(args):
    n_sims, teams_dict, groups, group_matches, bracket_rules, real_results, base_goals, scale, mode, model_version = args
    tournament_team_ids = sim_tournament_module.get_tournament_team_ids(groups)
    local_stats = init_stats(tournament_team_ids)
    local_opp_stats = {team_id: {} for team_id in tournament_team_ids}
    
    for _ in range(n_sims):
        tournament_result, tournament_opponents = sim_tournament_module.simulate_tournament(
            teams_dict=teams_dict,
            groups=groups,
            group_matches=group_matches,
            bracket_rules=bracket_rules,
            real_results=real_results,
            base_goals=base_goals,
            scale=scale,
            mode=mode,
            model_version=model_version,
        )
        for team_id, max_stage in tournament_result.items():
            if team_id in local_stats:
                increment_reached_stages(local_stats, team_id, max_stage)
        for team_id, opps in tournament_opponents.items():
            for opp_id in opps:
                if opp_id not in local_opp_stats[team_id]:
                    local_opp_stats[team_id][opp_id] = 0
                local_opp_stats[team_id][opp_id] += 1
    
    return local_stats, local_opp_stats


def convert_counts_to_probabilities(
    stats: Dict[str, Dict[str, int]],
    opp_stats: Dict[str, Dict[str, int]],
    teams_dict: Dict[str, Any],
    n_simulations: int,
    base_elos_dict: Dict[str, float] = None
):
    probabilities = {}

    def get_metrics(prefix: str, count: int):
        p = count / n_simulations
        se = math.sqrt(p * (1 - p) / n_simulations) if p > 0 else 0
        ci_low = max(0.0, p - 1.96 * se) if p > 0 else 0
        ci_high = min(1.0, p + 1.96 * se) if p > 0 else 3.0 / n_simulations
        
        if p == 0:
            display = f"< {(3.0 / n_simulations) * 100:.2f}%"
        elif p >= 0.999:
            display = f"> 99.9%"
        else:
            display = f"{p * 100:.1f}%"
            
        return {
            prefix: p,
            f"{prefix}_se": se,
            f"{prefix}_ci95_low": ci_low,
            f"{prefix}_ci95_high": ci_high,
            f"{prefix}_display": display,
        }

    for team_id, counts in stats.items():
        team = teams_dict.get(team_id, {})
        team_name = team.get("nameFr") or team.get("nameEn") or team_id

        team_data = {
            "name": team_name,
            "liveElo": team.get("elo", 1500),
            "baseElo": base_elos_dict.get(team_id, 1500) if base_elos_dict else team.get("elo", 1500),
            "fifaPoints": team.get("fifaPoints", 0),
        }
        
        for stage in ["roundOf32", "roundOf16", "quarterFinal", "semiFinal", "final", "champion"]:
            team_data.update(get_metrics(stage, counts[stage]))
            
        potential_opponents = {}
        for opp_id, opp_count in opp_stats.get(team_id, {}).items():
            prob = opp_count / n_simulations
            if prob > 0.01:
                potential_opponents[opp_id] = round(prob, 4)
                
        team_data["potentialOpponents"] = potential_opponents
            
        probabilities[team_id] = team_data

    return probabilities


def run_monte_carlo(
    n_simulations: int = 1000,
    base_goals: float = 1.35,
    scale: float = 800.0,
    mode: str = "pre_tournament",
    model_version: str = "V1",
    save: bool = True,
    elo_deltas: Dict[str, float] = None,
):
    """
    Répète le tournoi N fois et calcule les probabilités d'atteindre chaque stade.

    mode:
    - pre_tournament : ignore real_results.json
    - live : applique real_results.json
    """
    if mode not in {"pre_tournament", "live"}:
        raise ValueError("mode doit être 'pre_tournament' ou 'live'")

    teams_dict, groups, group_matches, bracket_rules, real_results = sim_tournament_module.load_tournament_data()

    if elo_deltas:
        for team_id, delta in elo_deltas.items():
            if team_id in teams_dict:
                teams_dict[team_id]["elo"] = float(teams_dict[team_id]["elo"]) + delta

    # Sauvegarder les Elos initiaux (avant le tournoi) pour calculer le Delta
    base_elos_dict = {team_id: float(data.get("elo", 1500)) for team_id, data in teams_dict.items()}

    # -- APPRENTISSAGE ACTIF (Live Elo) --
    # On l'applique UNE SEULE FOIS ici, pour mettre à jour teams_dict en place.
    if mode == "live":
        from src.domain.simulation.live_elo import compute_live_elos
        compute_live_elos(teams_dict, real_results)

    tournament_team_ids = sim_tournament_module.get_tournament_team_ids(groups)

    def _run_single_model(m_version):
        stats = init_stats(tournament_team_ids)
        opp_stats = {team_id: {} for team_id in tournament_team_ids}
        n_workers = min(os.cpu_count() or 4, 8)
        chunk_size = n_simulations // n_workers
        chunks = [chunk_size] * n_workers
        chunks[0] += n_simulations % n_workers

        args_list = [
            (c, teams_dict, groups, group_matches, bracket_rules, real_results, base_goals, scale, mode, m_version)
            for c in chunks if c > 0
        ]

        with concurrent.futures.ProcessPoolExecutor(max_workers=n_workers) as executor:
            results = list(executor.map(worker_simulate, args_list))

        for res_stats, res_opp_stats in results:
            for team_id, count_dict in res_stats.items():
                if team_id in stats:
                    for stage, count in count_dict.items():
                        stats[team_id][stage] += count
            for team_id, count_dict in res_opp_stats.items():
                for opp_id, count in count_dict.items():
                    if opp_id not in opp_stats[team_id]:
                        opp_stats[team_id][opp_id] = 0
                    opp_stats[team_id][opp_id] += count

        return convert_counts_to_probabilities(
            stats=stats,
            opp_stats=opp_stats,
            teams_dict=teams_dict,
            n_simulations=n_simulations,
            base_elos_dict=base_elos_dict
        )

    print(f"Mode: {mode}")
    print(f"baseGoals={base_goals}, scale={scale}")

    if model_version == "ALL":
        print(f"Lancement de {n_simulations} simulations Monte Carlo (multi-cœur) pour TOUS les modèles...")
        start_time = time.time()
        probs_v1 = _run_single_model("V1")
        probs_v2 = _run_single_model("V2")
        probs_v3 = _run_single_model("V3")
        probs_v4 = _run_single_model("V4")
        probs_v5 = _run_single_model("V5")
        elapsed = time.time() - start_time
        print("Calcul des statistiques globales terminé.")
        probabilities = probs_v5
        comparisons = {"V1": probs_v1, "V2": probs_v2, "V3": probs_v3, "V4": probs_v4, "V5": probs_v5}
    else:
        print(f"Lancement de {n_simulations} simulations Monte Carlo (multi-cœur)...")
        start_time = time.time()
        probabilities = _run_single_model(model_version)
        elapsed = time.time() - start_time
        print("Calcul des statistiques globales terminé.")
        comparisons = None

    snapshot_path = None

    if save:
        # load save_snapshot module directly from file to avoid package import issues
        import importlib.util
        import pathlib
        snap_path = pathlib.Path("src") / "domain" / "evaluation" / "save_snapshot.py"
        spec = importlib.util.spec_from_file_location("cdm_save_snapshot", str(snap_path))
        if spec is None or spec.loader is None:
            raise ImportError(f"Cannot load spec for {snap_path}")
        snap_mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(snap_mod)

        build_snapshot_fn = getattr(snap_mod, "build_snapshot", None)
        save_snapshot_fn = getattr(snap_mod, "save_snapshot", None)
        if build_snapshot_fn is None or save_snapshot_fn is None:
            raise ImportError("Could not load save_snapshot functions from file")

        snapshot = build_snapshot_fn(
            results=probabilities,
            model_version=model_version,
            state=mode,
            n_simulations=n_simulations,
            base_goals=base_goals,
            scale=scale,
            metadata={
                "elapsedSeconds": round(elapsed, 2),
                "nTeams": len(tournament_team_ids),
            },
        )
        if comparisons:
            snapshot["comparisons"] = comparisons
            
        # build a descriptive filename depending on mode and available real_results
        from datetime import datetime

        # try to detect a precise suffix for live mode (matchday or knockout round)
        suffix = None
        if mode == "pre_tournament":
            suffix = "pre_tournament"
        else:
            # attempt to read real results from simulation module context
            real_results = None
            try:
                # re-load tournament data to get latest real_results and bracket info
                _, groups_info, group_matches_info, bracket_rules_info, real_results = sim_tournament_module.load_tournament_data()
            except Exception:
                real_results = {}

            # detect played group matchdays
            try:
                played_md = set()
                if real_results and "groups" in real_results:
                    groups_results = real_results.get("groups", {})
                    for gm in group_matches_info:
                        mid = gm.get("id")
                        if mid and groups_results.get(mid) is not None:
                            md = gm.get("matchday")
                            if md is not None:
                                played_md.add(int(md))

                if played_md:
                    suffix = f"j{max(played_md)}"
                else:
                    # check knockouts
                    played_knock = real_results.get("knockouts", {}) if real_results else {}
                    if played_knock:
                        round_map = {
                            "roundOf32": "r32",
                            "roundOf16": "r16",
                            "quarterFinals": "quarter",
                            "semiFinals": "semi",
                            "final": "final",
                            "thirdPlace": "3rd",
                        }
                        found = None
                        for rk, tag in round_map.items():
                            rules = bracket_rules_info.get(rk, []) if bracket_rules_info else []
                            ids = {m.get("id") for m in rules}
                            if any(mid in ids for mid in played_knock.keys()):
                                found = tag
                                break

                        suffix = found or "live"
                    else:
                        suffix = "live"
            except Exception:
                suffix = "live"

        timestamp = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
        filename = f"snapshot_{mode}_{suffix}_{model_version}_{timestamp}.json"

        snapshot_path = save_snapshot_fn(
            snapshot=snapshot,
            output_dir="outputs/snapshots",
            filename=filename,
        )

        print(f"Snapshot sauvegardé dans {snapshot_path}")

    return probabilities


def print_top_teams(probabilities, n=15):
    sorted_teams = sorted(
        probabilities.items(),
        key=lambda x: x[1]["champion"],
        reverse=True,
    )

    print("\n=== TOP FAVORIS ===")
    print(
        f"{'Equipe':<22} | {'Champion':<9} | {'Finale':<9} | "
        f"{'Demies':<9} | {'Quarts':<9} | {'8es':<9}"
    )
    print("-" * 85)

    for team_id, prob in sorted_teams[:n]:
        print(
            f"{prob['name']:<22} | "
            f"{prob['champion'] * 100:>7.1f}% | "
            f"{prob['final'] * 100:>7.1f}% | "
            f"{prob['semiFinal'] * 100:>7.1f}% | "
            f"{prob['quarterFinal'] * 100:>7.1f}% | "
            f"{prob['roundOf16'] * 100:>7.1f}%"
        )


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--n", type=int, default=1000)
    parser.add_argument("--base-goals", type=float, default=1.35)
    parser.add_argument("--scale", type=float, default=800.0)
    parser.add_argument("--mode", choices=["pre_tournament", "live"], default="pre_tournament")
    parser.add_argument("--model-version", default="V1")
    parser.add_argument("--no-save", action="store_true")

    args = parser.parse_args()

    # allow using calibration outputs if the user didn't override defaults
    import json
    from pathlib import Path

    base_goals = args.base_goals
    scale = args.scale

    base_path = Path("outputs") / "calibration" / "base_goals.json"
    scale_path = Path("outputs") / "calibration" / "scale_search.json"

    if (base_goals == 1.35) and base_path.exists():
        try:
            with base_path.open("r", encoding="utf-8") as f:
                data = json.load(f)
                base_goals = float(data.get("baseGoals", base_goals))
                print(f"[INFO] base_goals lu depuis {base_path}: {base_goals}")
        except Exception as e:
            print(f"[WARN] impossible de lire {base_path}: {e}")

    if (scale == 800.0) and scale_path.exists():
        try:
            with scale_path.open("r", encoding="utf-8") as f:
                data = json.load(f)
                best = data.get("best") or {}
                scale = float(best.get("scale", data.get("best_scale", scale)))
                print(f"[INFO] scale lu depuis {scale_path}: {scale}")
        except Exception as e:
            print(f"[WARN] impossible de lire {scale_path}: {e}")

    probs = run_monte_carlo(
        n_simulations=args.n,
        base_goals=base_goals,
        scale=scale,
        mode=args.mode,
        model_version=args.model_version,
        save=not args.no_save,
    )

    print_top_teams(probs, n=15)