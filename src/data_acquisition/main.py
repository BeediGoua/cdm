import argparse
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
SRC_DIR = SCRIPT_DIR.parent
# Ensure local `src/data_acquisition` is searched first so `pipeline` imports the
# local module `src/data_acquisition/pipeline.py` rather than `src/pipeline` package.
sys.path.insert(0, str(SCRIPT_DIR))
sys.path.insert(1, str(SRC_DIR))

from data_pipeline import run_full_pipeline


def parse_args():
    parser = argparse.ArgumentParser(
        description="Run the full data acquisition pipeline for World Cup 2026."
    )
    parser.add_argument("--no-fetch", action="store_true", help="Skip raw data acquisition")
    parser.add_argument("--no-validate", action="store_true", help="Skip raw data validation")
    parser.add_argument("--no-normalize", action="store_true", help="Skip data normalization")
    parser.add_argument("--no-import", action="store_true", help="Skip SQLite import")
    return parser.parse_args()


def main():
    args = parse_args()
    run_full_pipeline(
        fetch=not args.no_fetch,
        validate=not args.no_validate,
        normalize=not args.no_normalize,
        import_db=not args.no_import,
    )


if __name__ == "__main__":
    main()
