import json
p='src/data/raw/elo_ratings_manual.json'
with open(p,encoding='utf-8') as f:
    data=json.load(f)
ids=[e.get('teamId').lower() for e in data]
added=0
for tid, name, elo, rank in [('irl','Republic of Ireland',1670,57),('prk','DPR Korea',1500,119)]:
    if tid not in ids:
        data.append({'teamId':tid,'teamName':name,'elo':elo,'rank':rank,'source':'manual_from_agent','date':'2026-06-14'})
        added+=1
if added:
    with open(p,'w',encoding='utf-8') as f:
        json.dump(data,f,ensure_ascii=False,indent=2)
print('added',added)
print('total',len(data))
