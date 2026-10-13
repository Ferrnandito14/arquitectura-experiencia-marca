#!/usr/bin/env python3
"""Seguimiento de tickets abiertos: liquida cada pata con el marcador/eventos de apifootball (get_events por match_id).
Uso: seguimiento.py --run runs/2026-10-13 [--events-json ARCHIVO]   (--events-json: {apif_id: evento} para pruebas/offline)
Estados de pata: PENDIENTE / EN_JUEGO (con lectura provisional) / ACERTADA / FALLADA / ANULADA. Ticket: ABIERTO / PERDIDO / GANADO.
Escribe seguimiento/estado.json|md y añade una línea por pata resuelta a registro_resultados.jsonl (sin duplicar). La clave nunca se imprime."""
import argparse
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import adapters  # noqa: E402
import common  # noqa: E402


def _int(x):
    try:
        return int(x)
    except (TypeError, ValueError):
        return None


def score(e):
    return _int(e.get("match_hometeam_score")), _int(e.get("match_awayteam_score"))


def half_score(e):
    return _int(e.get("match_hometeam_halftime_score")), _int(e.get("match_awayteam_halftime_score"))


def state(e):
    return adapters.apif_status(e.get("match_status"))      # upcoming / live / finished / postponed / cancelled


def _cmp(v, line, op):
    """(gana, push) para una línea simple; op over/under."""
    if op == "over":
        return v > line, v == line
    return v < line, v == line


def settle_total(total, op, line):
    """'win'|'lose'|'void' con liquidación completa (líneas .5 y enteras)."""
    w, p = _cmp(total, line, op)
    return "win" if w else ("void" if p else "lose")


def settle_handicap(h, a, lado, linea):
    """Hándicap asiático +linea para `lado` (home/away). Gana si goles propios + linea > rival; devuelve win/lose/void (líneas .5 y enteras)."""
    own, opp = (h, a) if lado == "home" else (a, h)
    d = own + linea - opp
    return "win" if d > 0 else ("void" if d == 0 else "lose")


def provisional(final_fn, e, leg):
    """Para totales en juego: 'under' se pierde ya si supera la línea; 'over' se gana ya si la supera; si no, EN_JUEGO."""
    return None


def eval_leg(leg, e):
    """Devuelve (estado, detalle). e = evento de la API (dict) o None."""
    if not e:
        return "PENDIENTE", "sin datos de la API"
    st = state(e)
    h, a = score(e)
    mk = leg["mercado"]
    if st in ("postponed", "cancelled"):
        return "ANULADA", f"partido {e.get('match_status')}"
    if st == "upcoming":
        return "PENDIENTE", "no ha empezado"
    fin = st == "finished"
    minuto = e.get("match_status") or ""
    if h is None or a is None:
        return ("PENDIENTE", "marcador no disponible")
    tag = f"{h}-{a}" + ("" if fin else f" ({minuto})")

    def final(res):
        return {"win": "ACERTADA", "lose": "FALLADA", "void": "ANULADA"}[res]

    if mk == "total":
        t = h + a
        res = settle_total(t, leg["op"], leg["linea"])
        if fin:
            return final(res), f"{tag}: {t} goles"
        if leg["op"] == "under" and t >= leg["linea"] and res != "win":
            return "FALLADA", f"{tag}: ya superó la línea ({t} goles)" if res == "lose" else f"{tag}: en la línea (devolución si termina así)"
        if leg["op"] == "over" and res == "win":
            return "ACERTADA", f"{tag}: ya supera la línea ({t} goles)"
        return "EN_JUEGO", f"{tag}: {t} goles; va {'ganando' if res == 'win' else 'perdiendo'} provisional"
    if mk == "handicap":
        res = settle_handicap(h, a, leg["lado"], leg["linea"])
        if fin:
            return final(res), f"{tag}: hándicap {leg['lado']} +{leg['linea']}"
        return "EN_JUEGO", f"{tag}: va {'ganando' if res == 'win' else ('en devolución' if res == 'void' else 'perdiendo')} provisional (puede cambiar)"
    if mk == "1x2":
        res = "win" if (h > a if leg["lado"] == "home" else a > h) else "lose"
        if fin:
            return final(res), tag
        return "EN_JUEGO", f"{tag}: va {'ganando' if res == 'win' else 'perdiendo/empatando'} provisional"
    if mk == "1x2_1t":
        hh, ha = half_score(e)
        if hh is None or ha is None:
            return ("EN_JUEGO", f"{tag}: sin marcador de la 1.ª mitad") if not fin else ("PENDIENTE", "sin marcador de la 1.ª mitad")
        res = "win" if (hh > ha if leg["lado"] == "home" else ha > hh) else "lose"
        # la 1.ª mitad está cerrada cuando hay marcador de descanso y el partido pasó del minuto 45 / descanso
        closed = fin or minuto.lower().startswith("half") or (minuto.replace("'", "").isdigit() and int(minuto.replace("'", "")) > 45)
        return (final(res) if closed else "EN_JUEGO"), f"1.ª mitad {hh}-{ha}; partido {tag}"
    if mk == "btts":
        both = h > 0 and a > 0
        if both:
            return "ACERTADA", f"{tag}: ambos anotaron"
        if fin:
            return "FALLADA", f"{tag}: no anotaron ambos"
        return "EN_JUEGO", f"{tag}: falta que anoten ambos"
    if mk == "cards_dc":
        pts = adapters._card_points(e)
        if pts is None:
            return ("PENDIENTE", "sin eventos de tarjetas") if not fin else ("PENDIENTE", "partido terminado sin eventos de tarjetas: revisar a mano")
        tot = pts[0] + pts[1]
        dc = (h >= a) if leg["lado"] == "home_or_draw" else (a >= h)
        if fin:
            ok = tot >= leg["min_puntos"] and dc
            return ("ACERTADA" if ok else "FALLADA"), f"{tag}; tarjetas {tot} pts (A=1,R=2); doble oportunidad {'sí' if dc else 'no'}"
        if not dc and False:
            pass
        return "EN_JUEGO", f"{tag}; tarjetas {tot} pts de {leg['min_puntos']}; Atlético/empate {'sí' if dc else 'no'} ahora"
    return "PENDIENTE", f"mercado {mk} no soportado"


def ticket_status(legs):
    ss = [l["estado"] for l in legs]
    if "FALLADA" in ss:
        return "PERDIDO"
    if all(s in ("ACERTADA", "ANULADA") for s in ss):
        return "GANADO" if any(s == "ACERTADA" for s in ss) else "ANULADO"
    return "ABIERTO"


def run(run_dir, fetch):
    spec = common.read_json(os.path.join(run_dir, "seguimiento", "tickets_abiertos.json"))
    cache, out = {}, []
    for t in spec["tickets"]:
        legs = []
        for l in t["patas"]:
            if l["apif"] not in cache:
                cache[l["apif"]] = fetch(l["apif"])
            st, det = eval_leg(l, cache[l["apif"]])
            legs.append({**l, "estado": st, "detalle": det})
        out.append({"id": t["id"], "nombre": t["nombre"], "monto": t["monto"], "estado": ticket_status(legs), "patas": legs})
    return out


def write_all(run_dir, res):
    d = os.path.join(run_dir, "seguimiento")
    common.write_json_atomic(os.path.join(d, "estado.json"), res)
    L = ["# Seguimiento de tickets abiertos", ""]
    for t in res:
        L += [f"## {t['id']} · {t['nombre']} — **{t['estado']}** (monto {t['monto']})", "", "| Pata | Cuota | Estado | Detalle |", "|---|---|---|---|"]
        for l in t["patas"]:
            L.append(f"| {l['partido']} · {l['mercado']} | {l['cuota']} | {l['estado']} | {l['detalle']} |")
        L.append("")
    with open(os.path.join(d, "estado.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(L))
    reg = os.path.join(d, "registro_resultados.jsonl")
    seen = set()
    if os.path.exists(reg):
        seen = {(json.loads(x)["ticket"], json.loads(x)["partido"], json.loads(x)["mercado"]) for x in open(reg, encoding="utf-8") if x.strip()}
    with open(reg, "a", encoding="utf-8") as f:
        for t in res:
            for l in t["patas"]:
                k = (t["id"], l["partido"], l["mercado"])
                if l["estado"] in ("ACERTADA", "FALLADA", "ANULADA") and k not in seen:
                    f.write(json.dumps({"ticket": t["id"], "partido": l["partido"], "mercado": l["mercado"], "cuota": l["cuota"],
                                        "resultado": l["estado"], "detalle": l["detalle"]}, ensure_ascii=False) + "\n")
    return "\n".join(L)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--run", default="runs/2026-10-13")
    ap.add_argument("--events-json")
    a = ap.parse_args(argv)
    if a.events_json:
        evs = common.read_json(a.events_json)
        fetch = lambda mid: evs.get(mid)  # noqa: E731
    else:
        key = adapters.apif_key()
        if not key:
            print("error: sin clave de apifootball (APIFOOTBALL_KEY / APIFOOTBALL_KEY_FILE)", file=sys.stderr)
            return 2
        client = common.Client(os.path.join(a.run, "cache"), os.path.join(a.run, "sources", "consultas.jsonl"), policy=common.Policy(),
                               min_interval=2.0, ttl=60)
        def fetch(mid):
            data = adapters.apif_call(client, key, action="get_events", match_id=mid, timezone="UTC")
            return data[0] if isinstance(data, list) and data else None
    print(write_all(a.run, run(a.run, fetch)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
