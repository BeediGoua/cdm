import requests, re, json
urls = {
    "irl": "https://www.eloratings.net/Ireland",
    "prk": "https://www.eloratings.net/North_Korea",
}
res = {}
for k, u in urls.items():
    try:
        r = requests.get(u, timeout=20)
        if not r.ok:
            res[k] = None
            continue
        text = r.text
        # Try common patterns
        m = re.search(r"Latest\s*Elo\s*rating[^0-9]*([0-9]{3,4})", text, re.I)
        if not m:
            m = re.search(r"Elo\s*rating[^0-9]*([0-9]{3,4})", text, re.I)
        if not m:
            # fallback: find first 3-4 digit number in page (risky)
            m = re.search(r"([0-9]{3,4})", text)
        res[k] = int(m.group(1)) if m else None
    except Exception as e:
        res[k] = None
print(json.dumps(res, ensure_ascii=False))
