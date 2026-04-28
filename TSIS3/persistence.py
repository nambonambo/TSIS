import json, os

def load_json(f, d):
    try: return json.load(open(f)) if os.path.exists(f) else d
    except: return d

def save_json(f, d): json.dump(d, open(f,"w"), indent=2)

def load_settings(): return load_json("settings.json", {"sound":False,"car_color":"red","difficulty":"normal"})
def save_settings(s): save_json("settings.json", s)
def load_leaderboard(): return load_json("leaderboard.json", [])

def save_score(name, score, dist):
    lb = sorted(load_leaderboard() + [{"name":name,"score":score,"distance":int(dist)}], key=lambda x:-x["score"])[:10]
    save_json("leaderboard.json", lb)
    return lb