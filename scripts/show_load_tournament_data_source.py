import importlib, sys, inspect
root=r'C:\Users\gouab\Desktop\Projet_perso\cdm'
if root not in sys.path: sys.path.insert(0,root)
mod = importlib.import_module('src.domain.simulation.simulate_tournament')
print('module', mod.__file__)
print('function source:\n')
print(inspect.getsource(mod.load_tournament_data))
