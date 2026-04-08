import json, os

FILE = "ranking.json"

def load():
    if not os.path.exists(FILE):
        return []
    return json.load(open(FILE))

def save(name, score):
    r = load()
    r.append({"name":name,"score":score})
    r = sorted(r, key=lambda x:x["score"], reverse=True)[:10]
    json.dump(r, open(FILE,"w"))