from fetch_data import run_all as fetch_data_run
from validate_data import run_validation as validate_data_run
from normalize_data import run_normalization as normalize_data_run
from import_sqlite import run_import as import_sqlite_run


def run_full_pipeline(fetch=True, validate=True, normalize=True, import_db=True):
    if fetch:
        print("\n=== STEP 1: Acquisition ===")
        fetch_data_run()

    if validate:
        print("\n=== STEP 2: Validation ===")
        valid = validate_data_run()
        if not valid:
            print("Pipeline stopped: raw data validation failed.")
            return False

    if normalize:
        print("\n=== STEP 3: Normalization ===")
        normalize_data_run()

    if import_db:
        print("\n=== STEP 4: SQLite import ===")
        import_sqlite_run()

    print("\nPipeline completed successfully.")
    return True
