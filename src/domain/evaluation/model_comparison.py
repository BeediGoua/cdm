import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Dict, List
import glob


def run_models(
    model_versions: List[str],
    n_simulations: int,
    base_goals: float,
    scale: float,
    mode: str,
):
    """
    Pour éviter les problèmes d'import/package, on exécute `run_monte_carlo`
    dans un sous-processus (même interpréteur Python) pour chaque version de
    modèle, puis on lit le snapshot produit dans `outputs/snapshots`.
    """
    reports = {}

    snapshots_dir = Path("outputs") / "snapshots"
    snapshots_dir.mkdir(parents=True, exist_ok=True)

    for model_version in model_versions:
        print(f"\n=== RUN MODEL {model_version} ===")

        cmd = [
            sys.executable,
            "-m",
            "src.domain.simulation.run_monte_carlo",
            "--n",
            str(n_simulations),
            "--mode",
            mode,
            "--model-version",
            model_version,
        ]

        # run subprocess and stream output
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        if proc.stdout:
            for line in proc.stdout:
                print(line, end="")
        proc.wait()

        # after run, find latest snapshot for this model_version
        pattern = str(snapshots_dir / f"*_{model_version}_*.json")
        matches = glob.glob(pattern)
        if not matches:
            print(f"[WARN] Aucun snapshot trouvé pour le modèle {model_version} (pattern={pattern})")
            reports[model_version] = {}
            continue

        latest = max(matches, key=lambda p: Path(p).stat().st_mtime)
        try:
            with open(latest, "r", encoding="utf-8") as f:
                data = json.load(f)
                results = data.get("results") or {}
                reports[model_version] = results
        except Exception as e:
            print(f"[ERROR] Impossible de lire {latest}: {e}")
            reports[model_version] = {}

    return reports


def save_all_model_results(
    reports: Dict,
    output_path: str = "outputs/model_comparisons/all_model_results.json",
):
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    with path.open("w", encoding="utf-8") as f:
        json.dump(reports, f, ensure_ascii=False, indent=2)

    return str(path)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--models",
        default="V1,V1_5,V2",
        help="Liste de modèles séparés par virgule",
    )
    parser.add_argument("--n", type=int, default=1000)
    parser.add_argument("--base-goals", type=float, default=1.35)
    parser.add_argument("--scale", type=float, default=800.0)
    parser.add_argument(
        "--mode",
        choices=["pre_tournament", "live"],
        default="pre_tournament",
    )
    parser.add_argument(
        "--output",
        default="outputs/model_comparisons/all_model_results.json",
    )

    args = parser.parse_args()

    model_versions = [
        m.strip()
        for m in args.models.split(",")
        if m.strip()
    ]

    reports = run_models(
        model_versions=model_versions,
        n_simulations=args.n,
        base_goals=args.base_goals,
        scale=args.scale,
        mode=args.mode,
    )

    output_path = save_all_model_results(reports, args.output)

    print(f"\nRésultats modèles sauvegardés : {output_path}")


if __name__ == "__main__":
    main()