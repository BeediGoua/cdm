import json
p='src/data/raw/elo_ratings_manual.json'
with open(p,encoding='utf-8') as f:
    data=json.load(f)
print([e.get('teamId') for e in data])
elo_map={e.get('teamId').lower():e for e in data}
print('keys:',sorted(elo_map.keys())[:20])
print('irl in map?', 'irl' in elo_map)
print('prk in map?', 'prk' in elo_map)
