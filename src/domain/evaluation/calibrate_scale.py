import argparse
import json
from pathlib import Path
from typing import Optional

# import model_backtest lazily inside functions to avoid import-time failures

DEFAULT_BASE_GOALS_JSON = "outputs/calibration/base_goals.json"
DEFAULT_OUTPUT = "reports/calibration/scale_search.json"


def calibrate_scale(
    matches_csv: str,
    teams_path: str,
    base_goals: float,
    scales: list[float],
    min_year: int = 2018,
    max_matches: int | None = None,
):
    # import here to avoid import-time issues
    try:
        from src.domain.evaluation.model_backtest import backtest_v1
        # sanity check: module should expose the function
        if not callable(backtest_v1):
            raise ImportError("backtest_v1 not callable")
    except Exception:
        # fallback: execute the file with runpy to get its globals
        import runpy
        from pathlib import Path

        mb_path = Path("src") / "domain" / "evaluation" / "model_backtest.py"
        globals_dict = runpy.run_path(str(mb_path))
        if "backtest_v1" in globals_dict:
            backtest_v1 = globals_dict["backtest_v1"]
        else:
            raise ImportError("backtest_v1 not found when loading model_backtest via runpy")
    results = []

    for scale in scales:
        print(f"Test scale={scale}...")

        try:
            result = backtest_v1(
                matches_csv=matches_csv,
                teams_path=teams_path,
                base_goals=base_goals,
                scale=scale,
                min_year=min_year,
                max_matches=max_matches,
            )
            results.append(result)
        except Exception as e:
            results.append({
                "baseGoals": base_goals,
                "scale": scale,
                "error": str(e),
            })

    valid = [r for r in results if "logLoss" in r]

    best = min(valid, key=lambda x: x["logLoss"]) if valid else None

    return {
        "baseGoals": base_goals,
        "minYear": min_year,
        "scalesTested": scales,
        "best": best,
        "best_scale": (best.get("scale") if best else None),
        "log_loss": (best.get("logLoss") if best else None),
        "results": results,
    }


def save_report(report: dict, path: str = DEFAULT_OUTPUT):
    out = Path(path)
    out.parent.mkdir(parents=True, exist_ok=True)

    with out.open("w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)

    return str(out)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--matches", default="src/data/processed/matches_clean.csv")
    parser.add_argument("--teams", default="src/data/normalized/teams.json")
    parser.add_argument("--base-goals", type=float, default=1.35)
    parser.add_argument("--min-year", type=int, default=2018)
    parser.add_argument("--max-matches", type=int, default=None)
    parser.add_argument(
        "--scales",
        default="400,600,800,1000,1200",
    )
    parser.add_argument(
        "--output",
        default=DEFAULT_OUTPUT,
    )
    # tolerate extra args when called from tooling
    args, _ = parser.parse_known_args()

    scales = [float(x.strip()) for x in args.scales.split(",") if x.strip()]

    # determine base_goals: prefer explicit arg, else read from known JSON
    base_goals_value: Optional[float] = args.base_goals

    if (base_goals_value is None) or (base_goals_value == 1.35):
        # try to read the computed base_goals JSON
        base_path = Path(DEFAULT_BASE_GOALS_JSON)
        if base_path.exists():
            try:
                with base_path.open("r", encoding="utf-8") as f:
                    data = json.load(f)
                    # prefer `baseGoals` then `baseGoalsRounded` then None
                    base_goals_value = data.get("baseGoals") or data.get("baseGoalsRounded") or base_goals_value
                    print(f"[INFO] base_goals lu depuis {base_path}: {base_goals_value}")
            except Exception as e:
                print(f"[WARN] impossible de lire {base_path}: {e}")

    report = calibrate_scale(
        matches_csv=args.matches,
        teams_path=args.teams,
        base_goals=float(base_goals_value),
        scales=scales,
        min_year=args.min_year,
        max_matches=args.max_matches,
    )

    output_path = save_report(report, args.output)

    print("\n=== CALIBRATION scale ===")
    print(f"Rapport sauvegardé : {output_path}")
    if report.get("best"):
        print(json.dumps(report["best"], ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
    
# python -m src.domain.evaluation.calibrate_scale \
#  --base-goals 1.35 \
#  --min-year 2018 \
#  --max-matches 2000