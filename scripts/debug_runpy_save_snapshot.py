import runpy, pathlib, sys
p = pathlib.Path('src') / 'domain' / 'evaluation' / 'save_snapshot.py'
print('path exists', p.exists(), 'absolute', p.resolve())
print('file preview:\n')
print(p.read_text())
print('\n--- runpy ---')
d = runpy.run_path(str(p))
print('keys:', sorted(k for k in d.keys() if not k.startswith('__')))
print('len', len(d))
print('module __name__:', d.get('__name__'))
print('module __file__:', d.get('__file__'))
print('sys.path[0]:', sys.path[0])
