#!/usr/bin/env python3
"""Catálogo de patas por partido a partir de las capturas de la persona usuaria (cuotas REALES de su casa, solo patas ≤ 2.10) + modelo pata por pata + mercado + rotación.
Salida: runs/2026-10-14/ligas/dataset.json. p_central = 0.8·p_mercado(sin margen, su casa) + 0.2·p_modelo (el backtest muestra que el mercado predice mejor); brecha = modelo − mercado."""
import json, os, sys
sys.path.insert(0, ".claude/skills/seleccion-final-picks/scripts")
import leg_model as L, rotation_risk as R, tickets as T  # noqa: E402

MAX_ODDS, W_MODEL = 2.10, 0.2
RUN = "runs/2026-10-14"
P = json.load(open(f"{RUN}/ligas/partidos_usuario.json"))["partidos"]
ids = json.load(open(f"{RUN}/ligas/ids.json"))
mx = json.load(open(f"{RUN}/matrix.json"))["matches"]
inv = {m["match_id"]: m for m in json.load(open(f"{RUN}/inventory.json"))["matches"]}
rot = json.load(open(f"{RUN}/rotation.json"))
by_comp = {}
for mid, v in mx.items():
    c = inv.get(mid, {}).get("competition")
    for side in ("local", "visitante"):
        for r in (v.get("form") or {}).get(side, []):
            if r.get("misma_competicion"):
                by_comp.setdefault(c, []).append(r)

def novig(odds):
    q = [1 / o for o in odds]; s = sum(q); return [x / s for x in q]

def freq_for(v, key, label_part):
    m = (v.get("markets") or {}).get(key) or {}
    fs = [s for s in m.get("stats", []) if label_part in s["label"]]
    return [(s["freq"], s["n"]) for s in fs]

out = []
for lg, h, a, hora, o1x2, line, ou in P:
    mid = ids[f"{h}|{a}"]; v = mx[mid]; m = inv[mid]
    form = v.get("form") or {}
    mu, adv = L.league_means([by_comp.get(m["competition"], [])]) if by_comp.get(m["competition"]) else (None, 1.0)
    mp = L.model_probs(form["local"], form["visitante"], mu, adv) if (mu and form.get("local") and form.get("visitante")) else None
    r = rot.get(mid, {}); lv = {"home": (r.get("home") or {}).get("nivel", "s/d"), "away": (r.get("away") or {}).get("nivel", "s/d")}
    q3 = novig(o1x2); q2 = novig(ou)
    fkey = f"goles.over_{str(line).replace('.', '_')}"
    legs = []
    def add(sel, odds, pm, pmod, direction, team=None):
        if odds > MAX_ODDS:
            return
        pen = None
        if team in ("home", "away"):
            pen = R.penalty_for_leg(lv[team], direction, True)
        elif direction == "under":
            lvl = "alto" if "alto" in (lv["home"], lv["away"]) else ("medio" if "medio" in (lv["home"], lv["away"]) else "bajo")
            pen = R.penalty_for_leg(lvl, "under", False)
        pc = pm if pmod is None else (1 - W_MODEL) * pm + W_MODEL * pmod
        if pen == "rebajar":
            pc -= 0.05
        legs.append({"seleccion": sel, "cuota": odds, "tipo_precio": "su casa (captura)", "p_mercado": round(pm, 4), "p_modelo": None if pmod is None else round(pmod, 4),
                     "p_central": round(pc, 4), "brecha": None if pmod is None else round(pmod - pm, 3), "ev_central": round(pc * odds - 1, 3), "ev_mercado": round(pm * odds - 1, 3),
                     "rotacion": pen, "direccion": direction})
    add(f"Gana {h}", o1x2[0], q3[0], mp and mp["p1"], "win", "home")
    add("Empate", o1x2[1], q3[1], mp and mp["px"], "draw")
    add(f"Gana {a}", o1x2[2], q3[2], mp and mp["p2"], "win", "away")
    add(f"Más de {line}", ou[0], q2[0], mp and mp[f"over_{line}"], "over")
    add(f"Menos de {line}", ou[1], q2[1], mp and (1 - mp[f"over_{line}"]), "under")
    out.append({"liga": lg, "match_id": mid, "apif_match_id": (m.get("source_match_ids") or {}).get("apifootball"), "partido": f"{h} – {a}", "hora_caracas": hora, "cuotas_1x2": o1x2, "linea_goles": line, "cuotas_ou": ou, "competicion_api": m["competition"],
                "lambda": None if not mp else [mp["lambda_local"], mp["lambda_visit"]], "rotacion": lv, "rot_motivos": {k: (r.get(k) or {}).get("motivos") for k in ("home", "away")},
                "n_muestra": [len(form.get("local", [])), len(form.get("visitante", []))], "historial": v.get("history_kind"), "freq_linea": freq_for(v, fkey, "total>"), "patas": legs})
json.dump(out, open(f"{RUN}/ligas/dataset.json", "w"), ensure_ascii=False, indent=1)
print(len(out), "partidos;", sum(len(x["patas"]) for x in out), "patas ≤", MAX_ODDS)
