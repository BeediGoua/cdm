import importlib, sys, inspect
root=r'C:\Users\gouab\Desktop\Projet_perso\cdm'
if root not in sys.path: sys.path.insert(0,root)
mod = importlib.import_module('src.domain.evaluation.save_snapshot')
print('file', mod.__file__)
print('attrs', [k for k in dir(mod) if not k.startswith('__')])
print('source len', len(inspect.getsource(mod)))
