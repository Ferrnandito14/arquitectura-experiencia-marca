"""Resuelve cada partido de partidos_usuario.json a su match_id del inventario (descarta categorías juveniles)."""
import json, unicodedata, sys
n = lambda s: "".join(c for c in unicodedata.normalize("NFD", s.lower()) if unicodedata.category(c) != "Mn").replace("-", " ").replace("/", " ")
ALIAS = {"ny red bulls": "new york red bulls", "sk slovan bratislava": "slovan bratislava", "borussia dortmund": "dortmund", "fk bodo glimt": "bodo glimt", "river plate-uru": "river plate",
         "saint louis city sc": "st louis city", "inter miami cf": "inter miami", "new york city": "new york city", "fc toronto": "toronto", "los angeles galaxy": "la galaxy"}
def toks(s):
    s = ALIAS.get(n(s), n(s)); return [t for t in s.replace(".", "").split() if t not in ("fc", "sc", "cf", "united", "utd", "fk", "sk", "city")] or s.split()
def ok(a, b):
    ta, tb = toks(a), toks(b); return any(x in " ".join(tb) for x in ta) or any(x in " ".join(ta) for x in tb)
import difflib
inv = json.load(open("runs/2026-10-14/inventory.json"))["matches"]
mx = json.load(open("runs/2026-10-14/matrix.json"))["matches"]
P = json.load(open("runs/2026-10-14/ligas/partidos_usuario.json"))["partidos"]
sim = lambda x, y: difflib.SequenceMatcher(None, " ".join(toks(x)), " ".join(toks(y))).ratio()
out, miss = {}, []
for lg, h, a, hora, *_ in P:
    c = [(sim(h, m["home_team"]) + sim(a, m["away_team"]), m) for m in inv
         if not any(k in (m["competition"] + m["home_team"]).lower() for k in ("youth", "u19", "u21", "u23", "women")) and "elegible" in m["disposition"] and m["normalized_datetime_utc"] >= "2026-10-14T04:00:00Z"]
    c.sort(key=lambda t: (-t[0], 0 if (mx.get(t[1]["match_id"]) or {}).get("form", {}).get("local") else 1))
    if c and c[0][0] >= 1.4: out[f"{h}|{a}"] = c[0][1]["match_id"]
    else: miss.append((h, a, [(round(x, 2), m["home_team"], m["away_team"]) for x, m in c[:2]]))
json.dump(out, open("runs/2026-10-14/ligas/ids.json", "w"), indent=1)
print(len(out), "resueltos; sin resolver:", miss)
