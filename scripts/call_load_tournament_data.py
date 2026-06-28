import importlib, sys
root=r'C:\Users\gouab\Desktop\Projet_perso\cdm'
if root not in sys.path: sys.path.insert(0,root)
mod = importlib.import_module('src.domain.simulation.simulate_tournament')
print('module file', mod.__file__)
res = mod.load_tournament_data()
print('len returned', len(res))
print(type(res))
try:
    print('keys if dict? ', getattr(res,'keys', lambda:None)())
except Exception:
    pass
