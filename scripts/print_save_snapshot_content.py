from pathlib import Path
p = Path('src') / 'domain' / 'evaluation' / 'save_snapshot.py'
print('exists', p.exists())
print('size', p.stat().st_size)
print('--- head ---')
print(p.read_text()[:800])
print('--- done ---')
