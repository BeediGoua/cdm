import importlib
import sys

pkg_name = 'src.domain.evaluation'
mods = [
    'calibrate_base_goals', 'calibrate_scale', 'model_backtest', 'model_comparison',
    'model_registry', 'log_loss', 'brier_score', 'calibration_curve',
    'compare_snapshots', 'compare_model_outputs', 'save_snapshot', 'team_history',
    'snapshot_types', 'experiment_registry', '__init__'
]

print('Python:', sys.executable)
for m in mods:
    name = f"{pkg_name}.{m}"
    try:
        importlib.import_module(name)
        print('OK', name)
    except Exception as e:
        print('ERROR', name, repr(e))
        import traceback; traceback.print_exc()
