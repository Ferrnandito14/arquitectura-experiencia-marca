#!/usr/bin/env python3
"""Verifica con apifootball el resultado REAL de cada pata de los cupones aportados por la persona usuaria (data/picks_usuario.json) y escribe
data/picks_usuario_resultados.json. Regla de tarjetas de la casa (A=1, R=2, 2.ª amarilla=2, solo jugadores que jugaron). Uso: python3 data/verificar_picks_usuario.py"""
import json, os, sys, unicodedata
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".claude", "skills", "seleccion-final-picks", "scripts"))
import adapters, common  # noqa: E402

run = "runs/2026-10-13"
client = common.Client(run + "/cache", run + "/sources/consultas.jsonl", policy=common.Policy(), min_interval=2.0, ttl=86400)
key = adapters.apif_key()
norm = lambda s: "".join(c for c in unicodedata.normalize("NFD", s.lower()) if unicodedata.category(c) != "Mn").replace("-", " ").replace(".", "")
picks = json.load(open("data/picks_usuario.json", encoding="utf-8"))
days = {}
for d in sorted({p["fecha"] for p in picks}):
    prev = (__import__("datetime").date.fromisoformat(d) - __import__("datetime").timedelta(days=0)).isoformat()
    days[d] = adapters.apif_call(client, key, action="get_events", **{"from": d, "to": d, "timezone": "America/Caracas"})
def find(p):
    for e in days[p["fecha"]]:
        h, a = norm(e["match_hometeam_name"]), norm(e["match_awayteam_name"])
        if norm(p["home"]) in h and norm(p["away"]) in a:
            return e
    return None
def stat(e, n):
    s = adapters._stat(e, n); return None if not s else s
out = []
for p in picks:
    e = find(p)
    r = dict(p)
    if not e or e.get("match_status") != "Finished":
        r.update(estado="NO ENCONTRADO/NO FINALIZADO" if not e else e.get("match_status"), acierto=None)
        out.append(r); continue
    h, a = int(e["match_hometeam_score"]), int(e["match_awayteam_score"])
    ht = (e.get("match_hometeam_halftime_score"), e.get("match_awayteam_halftime_score"))
    r["partido_api"] = f"{e['match_hometeam_name']} {h}-{a} {e['match_awayteam_name']} ({e.get('league_name')})"
    m, ok = p["mercado"], None
    if m == "total": ok = (h + a > p["linea"]) if p["op"] == "over" else (h + a < p["linea"])
    elif m == "btts": ok = h > 0 and a > 0
    elif m == "1x2": ok = (h > a) if p["lado"] == "home" else (a > h)
    elif m == "dc_total": ok = ((a >= h) if p["lado"] == "away_or_draw" else (h >= a)) and h + a > p["linea"]
    elif m == "1x2_1t" and ht[0] not in (None, ""): ok = (int(ht[0]) > int(ht[1])) if p["lado"] == "home" else (int(ht[1]) > int(ht[0]))
    elif m == "goles_equipo_1t" and ht[0] not in (None, ""): ok = int(ht[0]) > p["linea"] if p["lado"] == "home" else int(ht[1]) > p["linea"]
    elif m == "corners":
        c = stat(e, "Corners"); r["corners"] = c; ok = None if not c else sum(c) > p["linea"]
    elif m == "cards_corners":
        c = stat(e, "Corners"); pts = adapters._card_points(e); r.update(corners=c, tarjetas=pts)
        ok = None if (not c or pts is None) else (sum(pts) >= p["min_puntos"] and sum(c) >= p["min_corners"])
    elif m == "corners_golesvisit":
        c = stat(e, "Corners"); r["corners"] = c; ok = None if not c else (sum(c) >= p["min_corners"] and a <= p["max_goles_visit"])
    r.update(estado="Finished", acierto=ok, marcador=f"{h}-{a}", descanso=f"{ht[0]}-{ht[1]}")
    out.append(r)
json.dump(out, open("data/picks_usuario_resultados.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
for r in out:
    print(f"{r['slip'][:22]:22s} | {r['home']} – {r['away']} | {r['mercado']} {r.get('linea','')} @{r['cuota']} | {r.get('marcador','?')} | {r.get('partido_api','')[:60]} | {'✅' if r['acierto'] else ('❌' if r['acierto'] is False else '??')}")
