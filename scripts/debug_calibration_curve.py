from pathlib import Path
p = Path('src') / 'domain' / 'evaluation' / 'calibration_curve.py'
print('exists', p.exists())
print('disk content:\n')
print(p.read_text())
import runpy
print('\nrunpy.run_path keys:')
d = runpy.run_path(str(p))
print(sorted(k for k in d.keys() if not k.startswith('__')))
