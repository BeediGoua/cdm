from pathlib import Path
p = Path('src') / 'domain' / 'evaluation'
for f in sorted(p.glob('*.py')):
    txt = f.read_text()
    lines = txt.strip().splitlines()
    print(f.name, 'lines=', len(lines))
    if len(lines) < 10:
        print('---- CONTENT ----')
        print(txt)
        print('-----------------')
