#!/usr/bin/env python3
"""Backtest del modelo pata por pata (leg_model.py) contra el mercado sin margen, sobre los partidos de runs/<fecha> ya FINALIZADOS (historial previo + cuotas de la matriz).
Mide Brier y log-loss de: modelo, mercado y mezcla 50/50. Uso: python3 data/backtest_leg_model.py runs/2026-10-13"""
import json, math, os, sys
from collections import defaultdict
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".claude", "skills", "seleccion-final-picks", "scripts"))
import adapters, common, leg_model as L  # noqa: E402

run = sys.argv[1] if len(sys.argv) > 1 else "runs/2026-10-13"
matrix = json.load(open(f"{run}/matrix.json"))["matches"]
inv = {m["match_id"]: m for m in json.load(open(f"{run}/inventory.json"))["matches"]}
client = common.Client(run + "/cache", run + "/sources/consultas.jsonl", policy=common.Policy(), min_interval=2.0, ttl=60)
key = adapters.apif_key()
days = sorted({(inv[m]["normalized_datetime_utc"][:10]) for m in matrix if m in inv})
events = {}
for d0 in days:
    for e in adapters.apif_call(client, key, action="get_events", **{"from": d0, "to": d0, "timezone": "UTC"}):
        events[str(e["match_id"])] = e

by_comp = defaultdict(list)
for mid, v in matrix.items():
    for side in ("local", "visitante"):
        for r in (v.get("form") or {}).get(side, []):
            if r.get("misma_competicion"):
                by_comp[inv[mid]["competition"] if mid in inv else "?"].append(r)

def novig(odds):
    p = [1 / o for o in odds]; s = sum(p); return [x / s for x in p]

rows = []   # (mercado, p_modelo, p_mercado, resultado)
for mid, v in matrix.items():
    m = inv.get(mid); ap = v.get("api_prices") or {}
    form = v.get("form") or {}
    api = (m or {}).get("source_match_ids", {}).get("apifootball")
    e = events.get(str(api))
    if not (m and e and e.get("match_status") == "Finished" and form.get("local") and form.get("visitante")):
        continue
    try:
        h, a = int(e["match_hometeam_score"]), int(e["match_awayteam_score"])
    except (ValueError, TypeError, KeyError):
        continue
    mu, adv = L.league_means([by_comp[m["competition"]]]) if by_comp.get(m["competition"]) else (None, 1.0)
    if not mu:
        continue
    mp = L.model_probs(form["local"], form["visitante"], mu, adv)
    for ln in (1.5, 2.5, 3.5):
        pr = ap.get(f"goles.over_{str(ln).replace('.', '_')}")
        if pr and pr.get("cuotas_medias") and len(pr["cuotas_medias"]) == 2:
            rows.append((f"over {ln}", mp[f"over_{ln}"], novig(pr["cuotas_medias"])[0], int(h + a > ln)))
    pr = ap.get("goles.btts")
    if pr and pr.get("cuotas_medias") and len(pr["cuotas_medias"]) == 2:
        rows.append(("btts", mp["btts"], novig(pr["cuotas_medias"])[0], int(h > 0 and a > 0)))
    pr = ap.get("resultado.1x2")
    if pr and pr.get("cuotas_medias") and len(pr["cuotas_medias"]) == 3:
        q = novig(pr["cuotas_medias"])
        for lab, pm, pq, res in (("1", mp["p1"], q[0], int(h > a)), ("X", mp["px"], q[1], int(h == a)), ("2", mp["p2"], q[2], int(a > h))):
            rows.append((f"1x2 {lab}", pm, pq, res))

def score(rs, f):
    n = len(rs)
    br = sum((f(r) - r[3]) ** 2 for r in rs) / n
    ll = -sum(math.log(min(max(f(r) if r[3] else 1 - f(r), 1e-6), 1)) for r in rs) / n
    return round(br, 4), round(ll, 4)

print(f"partidos finalizados con datos: {len({id(r) for r in rows}) and len(rows)} filas de mercado")
groups = defaultdict(list)
for r in rows:
    groups[r[0]].append(r); groups["TODOS"].append(r)
print(f"{'mercado':10} {'n':>4}  {'Brier modelo':>12} {'Brier mercado':>13} {'Brier mezcla':>12}  {'LL modelo':>9} {'LL mercado':>10} {'LL mezcla':>9}")
for k, rs in sorted(groups.items()):
    a, b, c = score(rs, lambda r: r[1]), score(rs, lambda r: r[2]), score(rs, lambda r: (r[1] + r[2]) / 2)
    print(f"{k:10} {len(rs):>4}  {a[0]:>12} {b[0]:>13} {c[0]:>12}  {a[1]:>9} {b[1]:>10} {c[1]:>9}")
