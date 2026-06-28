import sys, importlib, traceback, inspect
root=r'C:\Users\gouab\Desktop\Projet_perso\cdm'
if root not in sys.path: sys.path.insert(0,root)
try:
    m=importlib.import_module('src.domain.evaluation.calibration_curve')
    print('imported', getattr(m,'__file__',None))
    print('has calibration_curve?', hasattr(m,'calibration_curve'))
    print('attrs', [k for k in dir(m) if not k.startswith('__')])
    print('source len', len(inspect.getsource(m)))
except Exception:
    traceback.print_exc()
