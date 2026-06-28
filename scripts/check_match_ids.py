import json
fr='src/data/raw/fifa_rankings_current.json'
me='src/data/raw/elo_ratings_manual.json'
frj=json.load(open(fr,encoding='utf-8'))
mj=json.load(open(me,encoding='utf-8'))
elo_map={e['teamId'].lower():e for e in mj}
# find teams in fifa_rankings with IdCountry or IdTeam
for team in frj.get('Results',[]):
    code=(team.get('IdCountry') or team.get('IdTeam') or '').lower()
    if code in ('irl','prk'):
        print(code,'->', team.get('TeamName'))
        print('manual exists?', code in elo_map)

print('manual keys include irl?', 'irl' in elo_map)
print('manual keys include prk?', 'prk' in elo_map)
