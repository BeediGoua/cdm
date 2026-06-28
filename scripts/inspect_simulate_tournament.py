import importlib, traceback, sys, inspect
root=r'C:\Users\gouab\Desktop\Projet_perso\cdm'
if root not in sys.path: sys.path.insert(0,root)
try:
    m=importlib.import_module('src.domain.simulation.simulate_tournament')
    print('file',m.__file__)
    print('attrs', [k for k in dir(m) if not k.startswith('__')])
    print('has get_tournament_team_ids', hasattr(m,'get_tournament_team_ids'))
    print('source len', len(inspect.getsource(m)))
except Exception:
    traceback.print_exc()
