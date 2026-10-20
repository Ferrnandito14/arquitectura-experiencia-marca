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


def settle_total_quarter(total, op, line):
    """Totales con línea de cuarto (2.25, 2.75…): mitad a cada línea vecina. 'win'|'half_win'|'void'|'half_loss'|'lose'; en líneas .0/.5 equivale a settle_total."""
    if abs(line * 4 - round(line * 4)) < 1e-9 and round(line * 4) % 2 == 1:
        a, b = settle_total(total, op, line - 0.25), settle_total(total, op, line + 0.25)
        if a == b:
            return a
        return {frozenset(("win", "void")): "half_win", frozenset(("lose", "void")): "half_loss"}[frozenset((a, b))]
    return settle_total(total, op, line)


def settle_handicap(h, a, lado, linea):
    """Hándicap asiático +linea para `lado` (home/away). Gana si goles propios + linea > rival; devuelve win/lose/void (líneas .5 y enteras)."""
    own, opp = (h, a) if lado == "home" else (a, h)
    d = own + linea - opp
    return "win" if d > 0 else ("void" if d == 0 else "lose")


def _et_started(e):
    """True si el partido ya está en prórroga/penales (la API trae marcador de prórroga o de penales): los 90' están cerrados aunque el feed no marque «Finished»."""
    return any((e.get(k) or "").strip() != "" for k in ("match_hometeam_extra_score", "match_awayteam_extra_score", "match_hometeam_penalty_score", "match_awayteam_penalty_score"))


def score90(e):
    """Marcador a los 90' + descuento: si la API trae `match_hometeam_ft_score` (tiempo completo, sin prórroga ni penales) se usa ese; si no, el marcador general.
    Las apuestas de goles/hándicap/1X2 se liquidan a 90'; la prórroga y los penales no cuentan."""
    ft_h, ft_a = _int(e.get("match_hometeam_ft_score")), _int(e.get("match_awayteam_ft_score"))
    if ft_h is not None and ft_a is not None:
        return ft_h, ft_a
    h, a = score(e)
    ex_h, ex_a = _int(e.get("match_hometeam_extra_score")), _int(e.get("match_awayteam_extra_score"))
    if h is not None and a is not None and ex_h is not None and ex_a is not None:     # el marcador general incluye la prórroga: se resta
        return h - ex_h, a - ex_a
    return h, a


def settle_handicap_quarter(h, a, lado, linea):
    """Hándicap asiático con líneas de cuarto (±.25/.75): la apuesta se divide a partes iguales entre las dos líneas vecinas.
    Devuelve 'win' | 'half_win' | 'void' | 'half_loss' | 'lose' (para líneas enteras o .5 equivale a settle_handicap)."""
    if round(linea * 4) % 2 == 0:                     # línea entera o .5
        return settle_handicap(h, a, lado, linea)
    lo, hi = linea - 0.25, linea + 0.25
    r = [settle_handicap(h, a, lado, lo), settle_handicap(h, a, lado, hi)]
    if r == ["win", "win"]:
        return "win"
    if r == ["lose", "lose"]:
        return "lose"
    if "win" in r and "void" in r:
        return "half_win"
    if "lose" in r and "void" in r:
        return "half_loss"
    return "void"


def _corner_pair(e):
    """(local, visitante) de córners. La API trae dos bloques (`statistics` del partido y `statistics_1half`) que a veces no coinciden porque el del partido va retrasado
    (15-oct: Sparta 3 vs 5 córners al descanso). Los córners no bajan, así que se toma el mayor de cada lado entre ambos bloques; None si ninguno los trae."""
    best = None
    for key in ("statistics", "statistics_1half"):
        for x in e.get(key) or []:
            if x.get("type") == "Corners":
                try:
                    v = (int(x.get("home") or 0), int(x.get("away") or 0))
                except ValueError:
                    continue
                best = v if best is None else (max(best[0], v[0]), max(best[1], v[1]))
    return best


def _minute(e):
    m = (e.get("match_status") or "").replace("'", "").split("+")[0]
    return int(m) if m.isdigit() else None


def _first_half(e, h, a):
    """(goles de la 1.ª mitad, cerrada?). En la 1.ª mitad se usa el marcador actual (abierta); desde el descanso, el del descanso (cerrada)."""
    hh, ha = half_score(e)
    mn, ms = _minute(e), (e.get("match_status") or "").lower()
    closed = state(e) == "finished" or ms.startswith("half") or (mn is not None and mn > 45 and hh is not None)
    if hh is not None and ha is not None and closed:
        return hh + ha, True
    return h + a, False


def provisional(final_fn, e, leg):
    """Para totales en juego: 'under' se pierde ya si supera la línea; 'over' se gana ya si la supera; si no, EN_JUEGO."""
    return None


def _corners(e):
    cp = _corner_pair(e)
    return None if cp is None else cp[0] + cp[1]


def _first_goal_side(e):
    def side_of(g):
        if g.get("home_scorer"):
            return "home"
        if g.get("away_scorer"):
            return "away"
        return g.get("info") if g.get("info") in ("home", "away") else None
    gs = [dict(g, info=side_of(g)) for g in (e.get("goalscorer") or []) if side_of(g)]
    if not gs:
        return None
    def t(g):
        try:
            return float(str(g.get("time")).split("+")[0])
        except ValueError:
            return 999
    return min(gs, key=t)["info"]


def _sub_status(sub, e, h, a, fin):
    """Sub-pata de una 'Crear apuesta': (win|lose|pending, texto). Con partido en juego, win/lose son PROVISIONALES salvo el primer gol."""
    k = sub["tipo"]
    if k == "corners_equipo":
        cp = _corner_pair(e)
        if cp is None:
            return "pending", "córners no disponibles"
        v = cp[0] if sub["lado"] == "home" else cp[1]
        res = settle_total(v, sub["op"], sub["linea"])
        if fin:
            return res, f"{v} córners del equipo"
        if sub["op"] == "over":
            return ("win", f"{v}/{sub['linea']} córners del equipo (cumplida provisional)") if res == "win" else ("pending", f"{v} córners del equipo, falta superar {sub['linea']}")
        return ("lose", f"{v} córners del equipo: ya superó {sub['linea']}") if res == "lose" else ("pending", f"{v} córners del equipo (menos de {sub['linea']} va bien)")
    if k == "handicap":
        res = settle_handicap(h, a, sub["lado"], sub["linea"])
        txt = f"hándicap {sub['lado']} +{sub['linea']}: va {'ganando' if res == 'win' else ('devolución' if res == 'void' else 'perdiendo')}" + ("" if fin else " (provisional)")
        return (res if fin else "pending"), txt
    if k == "btts":
        if h > 0 and a > 0:
            return ("win" if fin else "pending"), f"ambos anotaron ({h}-{a})" + ("" if fin else " — cumplida provisional hasta el final (VAR)")
        return ("lose", f"no anotaron ambos ({h}-{a})") if fin else ("pending", f"falta que anoten ambos ({h}-{a})")
    if k == "total_equipo":
        v = h if sub["lado"] == "home" else a
        res = settle_total(v, sub["op"], sub["linea"])
        if fin:
            return res, f"{v} goles del equipo"
        if sub["op"] == "over":
            return ("win", f"{v} goles del equipo (cumplida provisional)") if res == "win" else ("pending", f"{v} goles del equipo, falta superar {sub['linea']}")
        return ("lose", f"{v} goles del equipo: ya superó {sub['linea']} (provisional)") if res == "lose" else ("pending", f"{v} goles del equipo")
    if k == "dc":
        ok = (h != a) if sub["lado"] == "12" else ((h >= a) if sub["lado"] == "home_or_draw" else (a >= h))
        return ("win" if ok else "lose"), f"doble oportunidad {'sí' if ok else 'no'} ({h}-{a})" + ("" if fin else " (provisional)")
    if k == "1x2":
        ok = (h > a) if sub["lado"] == "home" else ((a > h) if sub["lado"] == "away" else (h == a))
        return ("win" if ok else "lose"), f"1X2 {sub['lado']} {'sí' if ok else 'no'} ({h}-{a})" + ("" if fin else " (provisional)")
    if k == "total_1t":
        g, closed = _first_half(e, h, a)
        res = settle_total(g, sub["op"], sub["linea"])
        if closed:
            return res, f"{g} goles en la 1.ª mitad"
        if sub["op"] == "under":
            return ("lose", f"{g} goles en la 1.ª mitad: ya superó {sub['linea']} (provisional)") if res == "lose" else ("pending", f"{g} goles en la 1.ª mitad")
        return ("win", f"{g} goles en la 1.ª mitad (cumplida provisional)") if res == "win" else ("pending", f"{g} goles en la 1.ª mitad")
    if k == "primer_gol":
        side = _first_goal_side(e)
        if side is None:
            return ("lose", "terminó sin goles") if fin else ("pending", "aún sin goles")
        return ("win" if side == sub["lado"] else "lose"), f"primer gol: {side}"
    if k in ("total", "tarjetas", "corners"):
        if k == "total":
            v, nm = h + a, "goles"
        elif k == "tarjetas":
            pts = adapters._card_points(e) or (0, 0)
            v, nm = pts[0] + pts[1], "pts tarjetas"
        else:
            v, nm = _corners(e), "córners"
            if v is None:
                return "pending", "córners no disponibles"
        res = settle_total(v, sub["op"], sub["linea"])
        if fin:
            return res, f"{v} {nm}"
        if sub["op"] == "over":
            return ("win", f"{v}/{sub['linea']} {nm} (cumplida provisional)") if res == "win" else ("pending", f"{v} {nm}, falta superar {sub['linea']}")
        return ("lose", f"{v} {nm}: ya superó {sub['linea']} (provisional)") if res == "lose" else ("pending", f"{v} {nm} (menos de {sub['linea']} va bien)")
    return "pending", f"sub-mercado {k} no soportado"


def eval_leg(leg, e):
    """Devuelve (estado, detalle). e = evento de la API (dict) o None."""
    if not e:
        return "PENDIENTE", "sin datos de la API"
    st = state(e)
    h, a = score(e)
    mk = leg["mercado"]
    et = _et_started(e) and mk in ("total", "total_equipo", "handicap", "1x2", "dc", "btts")
    if et:                           # prórroga/penales en curso: estos mercados se liquidan a 90'
        h, a = score90(e)
        st = "finished"
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
        res = settle_total_quarter(t, leg["op"], leg["linea"])
        if fin and res in ("half_win", "half_loss"):
            return {"half_win": "MEDIA_GANADA", "half_loss": "MEDIA_PERDIDA"}[res], f"{tag}: {t} goles (línea {leg['linea']:g}: media {'ganada' if res == 'half_win' else 'perdida'})"
        if res in ("half_win", "half_loss"):
            res = "win" if res == "half_win" else "lose"
        if fin:
            return final(res), f"{tag}: {t} goles"
        if leg["op"] == "under" and t >= leg["linea"] and res != "win":
            return "EN_JUEGO", (f"{tag}: ya superó la línea ({t} goles) — FALLO PROVISIONAL hasta el final (VAR)" if res == "lose" else f"{tag}: en la línea (devolución si termina así)")
        if leg["op"] == "over" and res == "win":
            return "EN_JUEGO", f"{tag}: ya supera la línea ({t} goles) — CUMPLIDA PROVISIONAL hasta el final (VAR)"
        return "EN_JUEGO", f"{tag}: {t} goles; va {'ganando' if res == 'win' else 'perdiendo'} provisional"
    if mk == "total_equipo":
        v = h if leg["lado"] == "home" else a
        res = settle_total(v, leg["op"], leg["linea"])
        if fin:
            return final(res), f"{tag}: {v} goles del equipo"
        if leg["op"] == "under" and res != "win":
            return "EN_JUEGO", f"{tag}: ya superó la línea ({v} goles del equipo) — FALLO PROVISIONAL hasta el final (VAR)" if res == "lose" else f"{tag}: en la línea (devolución si termina así)"
        if leg["op"] == "over" and res == "win":
            return "EN_JUEGO", f"{tag}: ya supera la línea ({v} goles del equipo) — CUMPLIDA PROVISIONAL hasta el final (VAR)"
        return "EN_JUEGO", f"{tag}: {v} goles del equipo; va {'ganando' if res == 'win' else 'perdiendo'} provisional"
    if mk in ("corners", "corners_equipo"):
        cp = _corner_pair(e)
        if cp is None:
            return ("EN_JUEGO", f"{tag}: córners no disponibles todavía") if not fin else ("PENDIENTE", f"{tag}: terminado sin estadística de córners: revisar a mano")
        v = cp[0] + cp[1] if mk == "corners" else (cp[0] if leg["lado"] == "home" else cp[1])
        nm = "córners" if mk == "corners" else "córners del equipo"
        res = settle_total(v, leg["op"], leg["linea"])
        if fin:
            return final(res), f"{tag}: {v} {nm}"
        if leg["op"] == "over" and res == "win":
            return "EN_JUEGO", f"{tag}: {v} {nm} — CUMPLIDA PROVISIONAL (ya superó {leg['linea']})"
        if leg["op"] == "under" and res == "lose":
            return "EN_JUEGO", f"{tag}: {v} {nm} — FALLO PROVISIONAL (ya superó {leg['linea']})"
        return "EN_JUEGO", f"{tag}: {v} {nm} (línea {leg['op']} {leg['linea']})"
    if mk == "total_1t":
        g, closed = _first_half(e, h, a)
        res = settle_total(g, leg["op"], leg["linea"])
        if closed:
            return final(res), f"{tag}: {g} goles en la 1.ª mitad"
        if leg["op"] == "over" and res == "win":
            return "EN_JUEGO", f"{tag}: {g} gol(es) en la 1.ª mitad — CUMPLIDA PROVISIONAL (VAR)"
        return "EN_JUEGO", f"{tag}: {g} goles en la 1.ª mitad (línea {leg['op']} {leg['linea']})"
    if mk == "handicap":
        h90, a90 = score90(e) if fin else (h, a)
        res = settle_handicap_quarter(h90, a90, leg["lado"], leg["linea"])
        name = {"win": "ganando", "half_win": "ganando la mitad (media ganada)", "void": "en devolución", "half_loss": "perdiendo la mitad (media perdida)", "lose": "perdiendo"}[res]
        if fin:
            return {"win": "ACERTADA", "lose": "FALLADA", "void": "ANULADA", "half_win": "MEDIA_GANADA", "half_loss": "MEDIA_PERDIDA"}[res], f"{tag}: hándicap {leg['lado']} {leg['linea']:+g}: {name}"
        return "EN_JUEGO", f"{tag}: hándicap {leg['lado']} {leg['linea']:+g} va {name} provisional (puede cambiar)"
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
            return ("ACERTADA", f"{tag}: ambos anotaron") if fin else ("EN_JUEGO", f"{tag}: ambos anotaron — CUMPLIDA PROVISIONAL hasta el final (VAR)")
        if fin:
            return "FALLADA", f"{tag}: no anotaron ambos"
        return "EN_JUEGO", f"{tag}: falta que anoten ambos"
    if mk == "dc":
        ok = (h != a) if leg["lado"] == "12" else ((h >= a) if leg["lado"] == "home_or_draw" else (a >= h))
        if fin:
            return ("ACERTADA" if ok else "FALLADA"), f"{tag}: doble oportunidad {'sí' if ok else 'no'}"
        return "EN_JUEGO", f"{tag}: va {'cumpliendo' if ok else 'perdiendo'} provisional"
    if mk == "goles_tarjetas":
        pts = adapters._card_points(e) or (0, 0)
        cur_p, goals = pts[0] + pts[1], h + a
        both = goals >= leg["min_goles"] and cur_p >= leg["min_puntos"]
        if fin:
            return ("ACERTADA" if both else "FALLADA"), f"{tag}: {goals} goles y {cur_p} pts de tarjetas (A=1,R=2)"
        return "EN_JUEGO", f"{tag}: {goals}/{leg['min_goles']} goles, {cur_p}/{leg['min_puntos']} pts de tarjetas" + (" — CUMPLIDA PROVISIONAL hasta el final (VAR)" if both else "")
    if mk == "tarjetas":
        pts = adapters._card_points(e) or (0, 0)
        tot = pts[0] + pts[1]
        res = settle_total(tot, leg["op"], leg["linea"])
        if fin:
            return final(res), f"{tag}: {tot} pts de tarjetas (A=1,R=2)"
        if leg["op"] == "under" and res == "lose":
            return "EN_JUEGO", f"{tag}: {tot} pts, ya superó la línea — FALLO PROVISIONAL (revisar tarjetas al final)"
        return "EN_JUEGO", f"{tag}: {tot} pts de tarjetas (línea {leg['op']} {leg['linea']})"
    if mk == "combo":
        rs = [(_sub_status(sb, e, h, a, fin), sb) for sb in leg["subs"]]
        det = " · ".join(f"{sb['tipo']}: {t[1]}" for t, sb in rs)
        if any(t[0] == "lose" for t, _ in rs):
            return ("FALLADA" if fin or any(sb["tipo"] == "primer_gol" and t[0] == "lose" for t, sb in rs) else "EN_JUEGO"), f"{tag}: {det}" + ("" if fin else " — alguna sub-pata va perdida")
        if fin and all(t[0] == "win" for t, _ in rs):
            return "ACERTADA", f"{tag}: {det}"
        return "EN_JUEGO", f"{tag}: {det}"
    if mk == "cards_dc":
        pts = adapters._card_points(e)
        if pts is None:
            return ("EN_JUEGO", f"{tag}; sin tarjetas registradas todavía (0 pts)") if not fin else ("PENDIENTE", f"{tag}: terminado sin eventos de tarjetas: revisar a mano")
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
    if all(s in ("ACERTADA", "ANULADA", "MEDIA_GANADA", "MEDIA_PERDIDA") for s in ss):
        return "GANADO" if any(s in ("ACERTADA", "MEDIA_GANADA", "MEDIA_PERDIDA") for s in ss) else "ANULADO"      # una media pérdida reduce el pago (no es pérdida total)
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
            legs.append({**l, "estado": st, "detalle": det, "fin": bool(cache[l["apif"]]) and state(cache[l["apif"]]) == "finished"})
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
                if l["estado"] in ("ACERTADA", "FALLADA", "ANULADA") and l.get("fin") and k not in seen:     # auditoría 13-oct: solo con el partido FINALIZADO (un gol anulado dejó un «2-0 ACERTADA» falso)
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
