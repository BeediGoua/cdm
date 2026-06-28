"""Utility to generate base_goals report by loading module from path.

This avoids import/pyc ambiguity by loading the source file directly.
"""
import importlib.util
import json
from pathlib import Path
import sys

MODULE_PATH = Path(__file__).parent.parent / "src" / "domain" / "evaluation" / "calibrate_base_goals.py"
DEFAULT_OUTPUT = Path(__file__).parent.parent / "outputs" / "calibration" / "base_goals.json"

spec = importlib.util.spec_from_file_location("cal_mod", str(MODULE_PATH))
mod = importlib.util.module_from_spec(spec)
loader = spec.loader
assert loader is not None
loader.exec_module(mod)

# default args
csv = "src/data/processed/matches_clean.csv"
min_year = 2000

if len(sys.argv) > 1:
    # allow passing min-year and output
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("--min-year", type=int, default=min_year)
    p.add_argument("--output", default=str(DEFAULT_OUTPUT))
    a = p.parse_args(sys.argv[1:])
    min_year = a.min_year
    out = Path(a.output)
else:
    out = DEFAULT_OUTPUT

print("Running compute_base_goals...")
report = mod.compute_base_goals(csv, min_year)

if not report:
    print("No report produced (compute returned empty).")
    sys.exit(1)

out.parent.mkdir(parents=True, exist_ok=True)
with out.open("w", encoding="utf-8") as f:
    json.dump(report, f, ensure_ascii=False, indent=2)

print(f"Saved: {out}")
