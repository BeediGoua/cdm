import requests
from requests.exceptions import RequestException

url = 'https://www.football-rankings.info/footballratings.html'
try:
    r = requests.get(url, timeout=15)
    print('status', r.status_code)
    print('len', len(r.text))
    # save a small snapshot
    with open('src/data/raw/footballratings_snapshot.html', 'w', encoding='utf-8') as f:
        f.write(r.text[:20000])
    print('saved snapshot')
except RequestException as e:
    print('error', repr(e))
