import importlib.util, sys
from pathlib import Path
mb_path = Path('src') / 'domain' / 'evaluation' / 'model_backtest.py'
print('path exists', mb_path.exists(), mb_path)
spec = importlib.util.spec_from_file_location('model_backtest_fallback', str(mb_path))
mod = importlib.util.module_from_spec(spec)
print('spec loader', spec.loader)
spec.loader.exec_module(mod)
print('module attrs:', [k for k in dir(mod) if not k.startswith('__')])
import inspect
try:
    src = inspect.getsource(mod)
    print('\n--- SOURCE ---\n')
    print(src)
    print('--- END SOURCE ---')
    print('has source length', len(src))
except Exception as e:
    print('inspect failed', e)
print('backtest present?', hasattr(mod,'backtest_v1'))
