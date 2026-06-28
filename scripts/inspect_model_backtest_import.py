import importlib, traceback, sys, inspect
modname='src.domain.evaluation.model_backtest'
try:
    if modname in sys.modules:
        del sys.modules[modname]
    m=importlib.import_module(modname)
    print('Imported', m, 'file=', getattr(m,'__file__',None))
    print('dict keys:', [k for k in m.__dict__.keys() if not k.startswith('__')])
    try:
        src=inspect.getsource(m)
        print('\n--- SOURCE START ---\n')
        print(src[:2000])
    except Exception as e:
        print('Cannot get source:', e)
except Exception:
    traceback.print_exc()
