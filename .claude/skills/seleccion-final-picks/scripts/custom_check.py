#!/usr/bin/env python3
"""Evalúa una combinada PROPUESTA POR LA PERSONA USUARIA con las mismas reglas que los borradores de `tickets.py`.

Uso:  custom_check.py --run runs/2026-10-13 --spec runs/2026-10-13/user_tickets.json

spec = [{"nombre": "...", "multiplicador_usuario": 1.27 (opcional, dato de la persona usuaria, no verificado),
         "patas": [{"partido": "Local – Visitante", "tipo": "total_goles", "operador": "over|under", "linea": 1.75}]}]

Por cada pata mide, sobre los últimos partidos propios de CADA equipo (mismo historial que `tickets.py`; nunca proxy), la frecuencia de
«gana entera» y de «no pierde» según la regla de liquidación de la línea (cuarto de línea = mitad a cada línea vecina; línea entera = devolución
en el empate exacto), con límite inferior de Wilson POR EQUIPO. Calcula además, con las líneas vecinas que SÍ tienen cuota media de mercado, una
COTA de la probabilidad implícita (la cuota exacta de líneas 1.75 o 7 no existe en la API). No es probabilidad predictiva ni EV."""
import argparse
import importlib.util
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import common  # noqa: E402
import tickets  # noqa: E402

calc = tickets.calc


def _total(h):
    return None if h.get("gf") is None or h.get("ga") is None else h["gf"] + h["ga"]


def settle(total, op, line):
    """Devuelve (gana_entera, no_pierde) para un total de goles. Líneas .25/.75: mitad a cada línea vecina (media victoria / media derrota)."""
    def one(l):               # (win, push) para una línea simple (entera o .5)
        if op == "over":
            return (total > l, total == l)
        return (total < l, total == l)
    q = round(line * 4) % 4
    ls = [line] if q in (0, 2) else [line - 0.25, line + 0.25]
    res = [one(l) for l in ls]
    full = all(w for w, _ in res)
    notlose = all(w or p for w, p in res)
    return full, notlose


def leg_support(fh, fa, op, line):
    out = {}
    for tag, rows in (("local", fh), ("visitante", fa)):
        ts = [t for t in (_total(h) for h in rows) if t is not None]
        n = len(ts)
        if n < tickets.MIN_N:
            return None
        full = sum(settle(t, op, line)[0] for t in ts)
        nl = sum(settle(t, op, line)[1] for t in ts)
        out[tag] = {"n": n, "gana_entera": f"{full}/{n}", "no_pierde": f"{nl}/{n}",
                    "wilson_gana_entera": round(calc.wilson(full, n)[0], 3), "wilson_no_pierde": round(calc.wilson(nl, n)[0], 3)}
    out["apoyo_gana_entera"] = round((out["local"]["wilson_gana_entera"] + out["visitante"]["wilson_gana_entera"]) / 2, 3)
    out["apoyo_no_pierde"] = round((out["local"]["wilson_no_pierde"] + out["visitante"]["wilson_no_pierde"]) / 2, 3)
    out["apoyo_min_equipo_gana_entera"] = min(out["local"]["wilson_gana_entera"], out["visitante"]["wilson_gana_entera"])
    return out


def _price(api, key, idx):
    p = (api or {}).get(key)
    if not p or p.get("n_casas", 0) < tickets.MIN_BOOKS:
        return None
    med = p.get("cuotas_medianas") or p.get("cuotas_medias")
    return {"cuota": med[idx], "n_casas": p["n_casas"], "implicita_sin_margen": round(tickets._novig(med)[idx], 4)}


def neighbours(api, op, line):
    """Cuotas medianas de las líneas .5 vecinas (las únicas que la API ofrece); la línea pedida queda ENTRE ellas."""
    idx = 0 if op == "over" else 1
    below = [l for l in (0.5, 1.5, 2.5, 3.5, 4.5, 5.5) if l < line]
    above = [l for l in (0.5, 1.5, 2.5, 3.5, 4.5, 5.5) if l > line]
    out = {}
    if below:
        out["linea_inferior"] = {"linea": below[-1], **(_price(api, f"goles.over_{str(below[-1]).replace('.', '_')}", idx) or {})}
    if above:
        out["linea_superior"] = {"linea": above[0], **(_price(api, f"goles.over_{str(above[0]).replace('.', '_')}", idx) or {})}
    return out


def evaluate(run, spec):
    inv = common.read_json(os.path.join(run, "inventory.json"))["matches"]
    mx = common.read_json(os.path.join(run, "matrix.json"))["matches"]
    by = {common.norm_name(f"{m['home_team']} – {m['away_team']}"): m for m in inv}
    res = []
    for t in spec:
        legs, notes = [], []
        for p in t["patas"]:
            m = by.get(common.norm_name(p["partido"]))
            if not m:
                legs.append({"partido": p["partido"], "error": "partido no encontrado en el inventario"})
                continue
            ev = mx.get(m["match_id"]) or {}
            leg = {"match_id": m["match_id"], "partido": p["partido"], "competicion": m["competition"], "inicio_utc": m["normalized_datetime_utc"],
                   "calendario_2_fuentes": m.get("selection_calendar_verification") == "SUFICIENTE", "operador": p["operador"], "linea": p["linea"]}
            if ev.get("history_kind") not in tickets.OK_KINDS:
                leg["error"] = "sin historial propio utilizable"
                legs.append(leg)
                continue
            leg["historial"] = ev["history_kind"]
            leg["soporte"] = leg_support(ev["form"].get("local", []), ev["form"].get("visitante", []), p["operador"], p["linea"])
            leg["lineas_vecinas_mercado"] = neighbours(ev.get("api_prices"), p["operador"], p["linea"])
            legs.append(leg)
        ok = [l for l in legs if l.get("soporte")]
        joint = calc.joint_prob([l["soporte"]["apoyo_gana_entera"] for l in ok]) if ok and len(ok) == len(legs) else None
        res.append({"nombre": t.get("nombre"), "multiplicador_usuario": t.get("multiplicador_usuario"), "patas": legs,
                    "apoyo_conjunto_gana_entera": None if joint is None else round(joint, 3),
                    "equilibrio_con_multiplicador_usuario": None if not t.get("multiplicador_usuario") else round(1 / t["multiplicador_usuario"], 3),
                    "nota": "El multiplicador es el que informó la persona usuaria (casa no verificada). Líneas 1.75 y 7 sin cuota en la API: solo hay cotas con líneas vecinas."})
    return res


def render(res):
    L = ["# Combinadas propuestas por la persona usuaria — evaluación con los mismos filtros", "",
         "> Apoyo = límite inferior de Wilson de una frecuencia descriptiva (NO probabilidad); techo 0.722 con n=10. Se reporta por equipo y la liquidación de cada línea.", ""]
    for r in res:
        L += [f"## {r['nombre']} — multiplicador informado ×{r['multiplicador_usuario']}", ""]
        for l in r["patas"]:
            if l.get("error"):
                L.append(f"- **{l['partido']}**: {l['error']}")
                continue
            s = l["soporte"]
            L += [f"- **{l['partido']}** ({l['competicion']}, {l['inicio_utc']}, calendario {'2 fuentes' if l['calendario_2_fuentes'] else '1 fuente'}) — {'Más' if l['operador'] == 'over' else 'Menos'} de {l['linea']} goles totales",
                  f"  - Local: gana entera {s['local']['gana_entera']} (Wilson {s['local']['wilson_gana_entera']}); no pierde {s['local']['no_pierde']} (Wilson {s['local']['wilson_no_pierde']})",
                  f"  - Visitante: gana entera {s['visitante']['gana_entera']} (Wilson {s['visitante']['wilson_gana_entera']}); no pierde {s['visitante']['no_pierde']} (Wilson {s['visitante']['wilson_no_pierde']})",
                  f"  - Apoyo (promedio de equipos) gana entera {s['apoyo_gana_entera']} · mínimo por equipo {s['apoyo_min_equipo_gana_entera']} · no pierde {s['apoyo_no_pierde']}"]
            for k, v in l["lineas_vecinas_mercado"].items():
                L.append(f"  - {k.replace('_', ' ')}: línea {v.get('linea')} → " + (f"cuota {v['cuota']} ({v['n_casas']} casas), implícita sin margen {v['implicita_sin_margen']}" if v.get("cuota") else "sin cuota media con ≥3 casas"))
        L += ["", f"**Apoyo conjunto (gana entera): {r['apoyo_conjunto_gana_entera']}** · punto de equilibrio del multiplicador informado: {r['equilibrio_con_multiplicador_usuario']}", f"_{r['nota']}_", ""]
    return "\n".join(L)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--run", required=True)
    ap.add_argument("--spec", required=True)
    a = ap.parse_args(argv)
    res = evaluate(a.run, common.read_json(a.spec))
    for r in (res if isinstance(res, list) else [res]):          # esta ruta NO ejecuta la cobertura de mercados: nunca presenta su salida como exhaustiva ni como apta para apostar
        r["investigacion_certificada"] = False
        r["preparacion_para_apostar"] = "NO_EVALUADA"
        r["cobertura_mercados"] = "no evaluada por esta ruta (market_coverage.py no se ejecuta aquí)"
    common.write_json_atomic(os.path.join(a.run, "user_tickets_eval.json"), res)
    text = ("> ⚠ NO CERTIFICADO COMO EXHAUSTIVO — evaluación descriptiva de las patas que aportó la persona usuaria; no ejecuta la cobertura de mercados ni evalúa la preparación para apostar.\n\n"
            + render(res))
    with open(os.path.join(a.run, "user_tickets_eval.md"), "w", encoding="utf-8") as f:
        f.write(text + "\n")
    print(text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
