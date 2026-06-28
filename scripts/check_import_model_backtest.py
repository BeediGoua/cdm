import importlib,traceback
try:
    m = importlib.import_module('src.domain.evaluation.model_backtest')
    print('OK', getattr(m,'__file__',None))
    names = [n for n in dir(m) if not n.startswith('__')]
    print('NAMES:', names)
except Exception:
    traceback.print_exc()
