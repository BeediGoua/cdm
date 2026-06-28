import json
from pathlib import Path
base = Path(__file__).resolve().parent.parent
teams_path = base / 'data' / 'normalized' / 'teams.json'
groups_path = base / 'data' / 'normalized' / 'groups.json'
matches_path = base / 'data' / 'normalized' / 'groupMatches.json'
man_path = base / 'data' / 'raw' / 'elo_ratings_manual.json'

teams = json.loads(teams_path.read_text(encoding='utf-8'))
team_ids = {t['id'] for t in teams}
manual = json.loads(man_path.read_text(encoding='utf-8'))
manual_ids = [entry['teamId'].strip().lower() for entry in manual if 'teamId' in entry]

print('teams count', len(team_ids))
print('manual count', len(manual_ids))
missing_manual = [tid for tid in manual_ids if tid not in team_ids]
print('missing manual ids in teams', missing_manual)

# groups
groups = json.loads(groups_path.read_text(encoding='utf-8'))
used_ids = set()
for ids in groups.values():
    used_ids.update(ids)

# matches
matches = json.loads(matches_path.read_text(encoding='utf-8'))
for m in matches:
    used_ids.add(m['homeTeamId'])
    used_ids.add(m['awayTeamId'])

print('used ids count', len(used_ids))
missing_used = sorted(tid for tid in used_ids if tid not in team_ids)
print('missing used ids in teams', missing_used, 'total', len(missing_used))

from collections import Counter
print('manual duplicate ids', [tid for tid, count in Counter(manual_ids).items() if count > 1])
print('manual unique ids', len(set(manual_ids)))

applied_manual = {t['id'] for t in teams if t.get('sourceConfidence') == 'manual'}
print('sourceConfidence manual count', len(applied_manual))
print('manual ids not marked manual in teams', sorted(tid for tid in set(manual_ids) if tid in team_ids and tid not in applied_manual))
print('manual ids extra not in team_ids', sorted(set(manual_ids) - team_ids))

# sample bad team IDs maybe empty strings
bad_ids = [tid for tid in used_ids if not tid or tid.strip() == '']
print('bad used ids empty', bad_ids)
