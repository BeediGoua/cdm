import sys,importlib,traceback,inspect,os
root=r'C:\Users\gouab\Desktop\Projet_perso\cdm'
if root not in sys.path:
    sys.path.insert(0, root)
mod='src.domain.evaluation.model_backtest'
if mod in sys.modules:
    del sys.modules[mod]
try:
    m=importlib.import_module(mod)
    print('imported file=', getattr(m,'__file__',None))
    keys=[k for k in m.__dict__.keys() if not k.startswith('__')]
    print('keys:', keys)
    try:
        print('\nsource len:', len(inspect.getsource(m)))
    except Exception as e:
        print('could not get source:', e)
except Exception:
    traceback.print_exc()
