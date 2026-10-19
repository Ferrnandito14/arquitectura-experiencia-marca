#!/usr/bin/env python3
"""Estado de los tickets abiertos CON PORCENTAJES, en texto plano (para chat o correo): por pata, la probabilidad de que se cumpla (acertada = 100 %, fallada = 0 %,
en juego = condicionada a marcador/córners y minuto con las tasas del modelo, pendiente = modelo antes del partido) y la probabilidad del ticket (producto: supone patas independientes).
Lee seguimiento/tickets_abiertos.json y vivo_estado.json (los escribe vivo.py); solo consulta la API de los partidos EN JUEGO de tickets abiertos. Sale con código 3 si no hay tickets abiertos.
Uso:  estado_tickets.py --run runs/2026-10-17 --book dist/ligas-17-oct-v3.xlsx"""
import argparse
import json
import os
import sys
from datetime import datetime, timedelta, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import adapters  # noqa: E402
import analisis_dia as ad  # noqa: E402
import api_detalle  # noqa: E402
import common  # noqa: E402
import live_prob  # noqa: E402
import seguimiento as sg  # noqa: E402

CARACAS = timezone(timedelta(hours=-4))
DC = {"home_or_draw": "1x", "away_or_draw": "x2", "12": "12"}


def entry_id(l):
    mk = l["mercado"]
    if mk == "total":
        return f"goles.total.{l['op']}.{l['linea']:g}"
    if mk == "total_equipo":
        return f"goles.equipo.{l['lado']}.{l['op']}.{l['linea']:g}"
    if mk == "btts":
        return "goles.btts.yes"
    if mk == "1x2":
        return f"resultado.1x2.{l['lado']}"
    if mk == "dc":
        return f"resultado.dc.{DC[l['lado']]}"
    if mk == "handicap":
        return f"resultado.ah.{l['lado']}.{l['linea']:+g}"
    if mk == "corners":
        return f"corners.total.{l['op']}.{l['linea']:g}"
    if mk == "corners_equipo":
        return f"corners.equipo.{l['lado']}.{l['op']}.{l['linea']:g}"
    if mk == "tarjetas":
        return f"cards_pts.total.{l['op']}.{l['linea']:g}"
    return None


def goal_p(l, ctx):
    """P por distribución de goles para líneas de cuarto y 'Crear apuesta' (total_equipo + doble oportunidad); None si no aplica."""
    if ctx.get("lh") is None:
        return None
    g = ad.goal_dist(ctx["lh"], ctx["la"], ctx["f"], ctx["h"], ctx["a"])
    tot = sum(g.values())
    if l["mercado"] == "total":
        return sum(p * {"win": 1, "half_win": .5}.get(sg.settle_total_quarter(x + y, l["op"], l["linea"]), 0) for (x, y), p in g.items()) / tot
    if l["mercado"] == "handicap":      # devolución (void) cuenta como «no perdida»; media ganada pesa 0.5
        return sum(p * {"win": 1, "void": 1, "half_win": .5}.get(sg.settle_handicap_quarter(x, y, l["lado"], l["linea"]), 0) for (x, y), p in g.items()) / tot
    if l["mercado"] == "combo":
        subs_g = [sb for sb in l["subs"] if sb["tipo"] != "corners"]
        subs_c = [sb for sb in l["subs"] if sb["tipo"] == "corners"]

        def ok(x, y):
            for sb in subs_g:
                t = sb["tipo"]
                if t == "total_equipo":
                    v = x if sb["lado"] == "home" else y
                    if sg.settle_total(v, sb["op"], sb["linea"]) != "win":
                        return False
                elif t == "dc":
                    if not ((x != y) if sb["lado"] == "12" else ((x >= y) if sb["lado"] == "home_or_draw" else (y >= x))):
                        return False
                elif t == "btts":
                    if not (x > 0 and y > 0):
                        return False
                elif t == "total":
                    if sg.settle_total(x + y, sb["op"], sb["linea"]) != "win":
                        return False
                elif t == "handicap":
                    if sg.settle_handicap(x, y, sb["lado"], sb["linea"]) == "lose":
                        return False
                elif t == "1x2":
                    if not ((x > y) if sb["lado"] == "home" else ((y > x) if sb["lado"] == "away" else (x == y))):
                        return False
                else:
                    return False
            return True
        pg = sum(p for (x, y), p in g.items() if ok(x, y)) / tot
        for sb in subs_c:                  # córners: independientes de los goles; en vivo con el conteo actual, antes del partido con la P del modelo guardada en la sub-pata
            eid = f"corners.total.{sb['op']}.{sb['linea']:g}"
            pc = ad.prob_pick(eid, sb.get("p_modelo"), ctx) if ctx.get("corners") else sb.get("p_modelo")
            pg *= 1.0 if pc is None else pc
        return pg
    return None


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--run", required=True)
    ap.add_argument("--book", required=True)
    a = ap.parse_args(argv)
    import openpyxl
    sp = os.path.join(a.run, "seguimiento")
    spec = common.read_json(os.path.join(sp, "tickets_abiertos.json"))
    st = common.read_json(os.path.join(sp, "vivo_estado.json"))
    inv = {m["match_id"]: m for m in common.read_json(os.path.join(a.run, "inventory.json"))["matches"]}
    cat = {(r["Partido"], r["Entrada"]): r for r in ad.leer_hoja(openpyxl.load_workbook(a.book, read_only=True, data_only=True), "Catálogo completo")}
    client = common.Client(os.path.join(a.run, "cache_vivo"), os.path.join(a.run, "sources", "consultas_vivo.jsonl"), policy=common.Policy(), min_interval=0.3, ttl=20)
    key = adapters.apif_key()
    ctx_cache = {}

    def live_ctx(l):
        if l["mid"] in ctx_cache:
            return ctx_cache[l["mid"]]
        e = adapters.apif_call(client, key, action="get_events", match_id=l["apif"], timezone="UTC")[0]
        h, aw = sg.score(e)
        mn = live_prob.minute_of(e)
        cp = sg._corner_pair(e)
        mp = api_detalle.model_params(a.run, l["mid"])
        c = {"h": h or 0, "a": aw or 0, "minute": mn, "f": max(0.0, 95.0 - mn) / 95.0, "lh": mp[0] if mp else None, "la": mp[1] if mp else None, "share": mp[2] if mp else None,
             "corners": tuple(cp) if cp else None, "cards": tuple(adapters._card_points(e) or ()) or None, "h1": 0, "a1": 0, "fin1": mn > 45}
        ctx_cache[l["mid"]] = c
        return c

    now = datetime.now(CARACAS).strftime("%H:%M")
    out, cerrados, abiertos = [f"ESTADO DE TUS TICKETS · {now} (hora de Caracas)", ""], [], 0
    for t in spec["tickets"]:
        ts = (st["legs"].get("T|" + t["id"]) or ["ABIERTO"])[0]
        if ts != "ABIERTO":
            cerrados.append(f"{t['id']} {'PERDIDO' if ts == 'PERDIDO' else ts}")
            continue
        abiertos += 1
        prod, lines = 1.0, []
        for l in t["patas"]:
            es, det = st["legs"].get(f"{t['id']}|{l['apif']}|{l['mercado']}", ["PENDIENTE", ""])
            nm = l["partido"]
            if es == "ACERTADA":
                p, tag = 100.0, "ACERTADA"
            elif es == "FALLADA":
                p, tag = 0.0, "FALLADA"
            elif es == "EN_JUEGO":
                c = live_ctx(l)
                pr = goal_p(l, c)
                if pr is None and entry_id(l):
                    pr = ad.prob_pick(entry_id(l), (cat.get((nm, entry_id(l))) or {}).get("P modelo %", None) and cat[(nm, entry_id(l))]["P modelo %"] / 100, c)
                p = None if pr is None else round(pr * 100, 1)
                tag = f"EN JUEGO {c['h']}-{c['a']} min {c['minute']:.0f}"
                if p is None:            # sin estadística en vivo (p. ej. córners al inicio): se usa la P del modelo antes del partido, rotulada
                    p = (cat.get((nm, entry_id(l))) or {}).get("P modelo %")
                    tag += " (sin estadística en vivo: P del modelo)"
            else:
                pr = None
                if l["mercado"] in ("combo", "total", "handicap") and (l["mercado"] != "total" or abs(l["linea"] * 4 % 2 - 1) < 1e-9):
                    pr = goal_p(l, {"h": 0, "a": 0, "f": 1.0, "lh": (api_detalle.model_params(a.run, l["mid"]) or [None])[0], "la": (api_detalle.model_params(a.run, l["mid"]) or [None, None])[1]})
                if pr is not None:
                    p = round(pr * 100, 1)
                else:
                    p = (cat.get((nm, entry_id(l))) or {}).get("P modelo %")
                h = (inv.get(l["mid"]) or {}).get("normalized_datetime_utc")
                tag = "pendiente " + (datetime.fromisoformat(h.replace("Z", "+00:00")).astimezone(CARACAS).strftime("%H:%M") if h else "")
            if p is not None:
                prod *= p / 100
            lines.append(f"   {nm} | cuota {l['cuota']} | {'?' if p is None else f'{p:.1f} %'} | {tag}")
        out.append(f"TICKET {t['id']} ({t['monto']} Bs, x{t['cuota_total']}) · probabilidad del ticket: {prod * 100:.1f} %")
        out += lines
        out.append("")
    if cerrados:
        out.append("Cerrados: " + ", ".join(cerrados))
    out.append("Probabilidades: acertada = 100 %, en juego = según marcador y minuto, pendiente = modelo (no validado). Ticket = producto de sus patas.")
    print("\n".join(out), flush=True)
    return 0 if abiertos else 3


if __name__ == "__main__":
    sys.exit(main())
