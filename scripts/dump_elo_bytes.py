p='src/data/raw/elo_ratings_manual.json'
with open(p,'rb') as f:
    b=f.read()
    print(len(b))
    # show last 200 bytes
    tail=b[-200:]
    print(tail)
    print(tail.decode('utf-8','backslashreplace'))
