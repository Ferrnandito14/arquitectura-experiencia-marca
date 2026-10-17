#!/usr/bin/env python3
"""Comparativo de un libro `ligas-<día>-oct-v2.xlsx` contra los RESULTADOS REALES: cómo le fue a cada pick (rankings, top por liga y combinadas) y a todo el catálogo con modelo y precio.

Uso:  comparativo_resultados.py --run runs/2026-10-14 --book dist/ligas-14-oct-v2.xlsx --out dist/comparativo-ligas-14-oct-resultados.xlsx [--refresh]
Pasos: (1) resultados finales de cada partido (apifootball get_events: marcador a 90', descanso, córners, tarjetas A=1/R=2, remates, fueras de juego) → `<run>/resultados/resultados.json`;
(2) liquidación de CADA entrada del catálogo con la regla de su mercado (líneas enteras = anulada; hándicap asiático y europeo; sin dato = «sin dato», nunca se inventa);
(3) los picks del libro (tal como se entregaron: misma cuota y mismo texto) se cruzan con el catálogo vivo del run por (partido, selección);
(4) libro de comparación: resumen de acierto, resultados, picks liquidados, combinadas con el resultado de cada pata y el catálogo evaluado (calibración del modelo, filtros de los agentes).
Todo en hora de Caracas. Es una muestra de UN día: sirve para ver el orden de magnitud, no demuestra ventaja ni la descarta (el modelo sigue sin validar)."""
import argparse
import json
import math
import os
import re
import sys
from collections import defaultdict
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import adapters  # noqa: E402
import agent_review as ar  # noqa: E402
import catalog_rankings as cr  # noqa: E402
import common  # noqa: E402
import market_catalog as mc  # noqa: E402
from acumulado import cluster_ci  # noqa: E402
import acumulado as acu  # noqa: E402
import api_detalle as ad  # noqa: E402
import seguimiento as sg  # noqa: E402

CCS = ZoneInfo("America/Caracas")
WIN, LOSE, VOID, NODATA = "GANADA", "PERDIDA", "ANULADA", "SIN DATO"
FINAL_STATES = ("Finished", "After ET", "After Pen.")       # a 90' + descuento: la prórroga y los penales no cuentan (ver seguimiento.score90)


# ── (1) resultados ──
def _int(v):
    try:
        return int(v)
    except (TypeError, ValueError):
        return None


def _goal_minute(t):
    """(minuto base, ¿con descuento?) de «45», «45+2», «90+7»; None si no se entiende."""
    t = str(t or "").replace("'", "").strip()
    try:
        base, _, extra = t.partition("+")
        return int(base), bool(extra)
    except ValueError:
        return None


def _is_shootout_or_extra(g):
    """Gol de la tanda de penales (`score_info_time` = «Penalty», minutos 1–5) o de la prórroga: no cuenta a 90' + descuento. Sin este filtro la tanda 4–3 de un partido 0–0 a 90' parecía «4–3 en goles»
    y el resultado se marcaba DATO INVÁLIDO (Boston River – River Plate, 14-oct)."""
    t = str(g.get("score_info_time") or "").strip().lower()
    return t.startswith(("penalty", "extra", "shootout"))


def goals_from_events(e):
    """Goles por lado a partir de la lista de goleadores (`goalscorer`): total a 90' + descuento y 1.ª parte (min ≤ 45 + descuento). None si la lista no existe.
    Es una segunda lectura DEL MISMO proveedor: confirma o desmiente el marcador, no es una fuente independiente."""
    gs = e.get("goalscorer")
    if not isinstance(gs, list):
        return None
    tot, ht = [0, 0], [0, 0]
    for g in gs:
        if _is_shootout_or_extra(g):
            continue
        side = 0 if (g.get("home_scorer") or "").strip() else 1 if (g.get("away_scorer") or "").strip() else None
        m = _goal_minute(g.get("time"))
        if side is None or m is None:
            continue
        base, plus = m
        if base < 90 or (base == 90):
            tot[side] += 1
        if base < 45 or (base == 45):
            ht[side] += 1
    return tot, ht


def parse_result(e):
    """Hechos liquidables de un evento de apifootball (None donde la fuente no los trae: nunca 0 inventado) y su procedencia: de qué bloque sale cada dato y si las lecturas coinciden."""
    h, a = sg.score90(e)
    cards = adapters._card_points(e)
    cv = adapters._card_points_variants(e)
    blocks = {}
    for key in ("statistics", "statistics_1half"):
        for x in e.get(key) or []:
            if x.get("type") == "Corners":
                try:
                    blocks[key] = (int(x.get("home") or 0), int(x.get("away") or 0))
                except ValueError:
                    pass
    cp = sg._corner_pair(e)                                  # máximo por lado entre los dos bloques (los córners no bajan; el bloque del partido a veces va retrasado)
    ev = goals_from_events(e)
    pg = None
    gl = [g for g in (e.get("goalscorer") or []) if isinstance(g, dict) and _goal_minute(g.get("time")) and not _is_shootout_or_extra(g)]
    if gl:
        g0 = min(gl, key=lambda g: (_goal_minute(g["time"])[0], _goal_minute(g["time"])[1]))
        pg = "home" if (g0.get("home_scorer") or "").strip() else "away" if (g0.get("away_scorer") or "").strip() else None
    r = {"primer_gol": pg, "estado": e.get("match_status") or "", "h": h, "a": a, "h1": _int(e.get("match_hometeam_halftime_score")), "a1": _int(e.get("match_awayteam_halftime_score")),
         "marcador_90_directo": _int(e.get("match_hometeam_ft_score")) is not None and _int(e.get("match_awayteam_ft_score")) is not None,
         "corners": list(cp) if cp else adapters._stat(e, "Corners"), "tarjetas": list(cards) if cards else None,
         "tarjetas_alt": list(cv[1]) if (cards and cv and cv[2]) else None, "tarjetas_ambiguas": cv[2] if (cards and cv) else 0, "remates": adapters._stat(e, "Shots Total"),
         "a_puerta": adapters._stat(e, "Shots On Goal"), "fueras": adapters._stat(e, "Offsides"), "arbitro": (e.get("match_referee") or "").strip() or None,
         "local": e.get("match_hometeam_name"), "visitante": e.get("match_awayteam_name"), "fecha": e.get("match_date"), "hora": e.get("match_time"),
         "procedencia": {"proveedor": "apifootball get_events", "fuentes_independientes": 1,
                         "corners_bloques": {k: list(v) for k, v in blocks.items()},
                         "corners_conflicto": bool(blocks.get("statistics") and blocks.get("statistics_1half") and (blocks["statistics"][0] < blocks["statistics_1half"][0] or blocks["statistics"][1] < blocks["statistics_1half"][1])),
                         "goles_eventos": None if ev is None else {"total": ev[0], "descanso": ev[1]}}}
    return r


def provenance_text(r, kind):
    """Texto de procedencia del dato decisivo (kind: goles | 1t | corners | tarjetas | otro) con el nº de lecturas que lo confirman. Todas son del mismo proveedor: se dice."""
    pv = r.get("procedencia") or {}
    if not pv:
        return "apifootball (sin detalle de procedencia: resultado anterior al registro de fuentes)"
    base = "apifootball (1 fuente)"
    ev = pv.get("goles_eventos")
    if kind == "goles":
        if ev is None:
            return base + "; sin lista de goleadores para contrastar"
        ok = r.get("h") is not None and ev["total"] == [r["h"], r["a"]]
        return base + ("; lista de goleadores coincide con el marcador (2 lecturas)" if ok else f"; CONFLICTO: goleadores {ev['total'][0]}–{ev['total'][1]} vs marcador {r.get('h')}–{r.get('a')}")
    if kind == "1t":
        if ev is None:
            return base + "; sin lista de goleadores para contrastar"
        ok = r.get("h1") is not None and ev["descanso"] == [r["h1"], r["a1"]]
        return base + ("; goleadores ≤ 45' coinciden con el descanso (2 lecturas)" if ok else f"; CONFLICTO: goleadores ≤ 45' {ev['descanso'][0]}–{ev['descanso'][1]} vs descanso {r.get('h1')}–{r.get('a1')}")
    if kind == "corners":
        b = pv.get("corners_bloques") or {}
        if not b:
            return base + "; sin estadísticas de córners"
        if pv.get("corners_conflicto"):
            return base + "; CONFLICTO: el bloque del partido va por detrás del de la 1.ª parte (" + " vs ".join(f"{k}={v[0]}–{v[1]}" for k, v in b.items()) + ") → se usa el máximo por lado"
        return base + f"; {len(b)} bloque(s) de estadísticas {'coinciden' if len(b) > 1 else '(solo uno)'}"
    return base


def result_status(r):
    """Estado normalizado del resultado: FINALIZADO | APLAZADO | CANCELADO | SUSPENDIDO | EN JUEGO | DATO INVÁLIDO | SIN RESULTADO. Solo FINALIZADO entra en los cálculos."""
    est = (r.get("estado") or "").strip()
    if not r or est in ("", "sin_resultado_en_la_api"):
        return "SIN RESULTADO"
    low = est.lower()
    if low in ("postponed", "pospuesto"):
        return "APLAZADO"
    if low in ("cancelled", "canceled", "cancelado"):
        return "CANCELADO"
    if low in ("abandoned", "interrupted", "suspended"):
        return "SUSPENDIDO"
    if est in FINAL_STATES:
        h, a, h1, a1 = r.get("h"), r.get("a"), r.get("h1"), r.get("a1")
        if not (isinstance(h, int) and isinstance(a, int)) or h < 0 or a < 0 or h > 15 or a > 15:
            return "DATO INVÁLIDO"
        if h1 is not None and a1 is not None and (h1 > h or a1 > a):
            return "DATO INVÁLIDO"
        pv = (r.get("procedencia") or {}).get("goles_eventos")
        if pv is not None and (pv["total"][0] > h or pv["total"][1] > a):
            return "DATO INVÁLIDO"
        return "FINALIZADO"
    if est.isdigit() or low in ("half time", "halftime", "ht") or low.endswith("'") or "+" in est:
        return "EN JUEGO"
    if low in ("not started", ""):
        return "SIN RESULTADO"
    return "DATO INVÁLIDO"


def is_final(r):
    return result_status(r) == "FINALIZADO"


def find_api_event(client, key, m):
    """Partido de apifootball de un registro del inventario sin id de la API: mismo día UTC, misma hora (±30 min) y nombres de AMBOS equipos parecidos (no se adivina con uno solo)."""
    import resolve_ids
    day = m["normalized_datetime_utc"][:10]
    t0 = datetime.fromisoformat(m["normalized_datetime_utc"].replace("Z", "+00:00"))
    best = None
    for e in adapters.apif_call(client, key, action="get_events", **{"from": day, "to": day, "timezone": "UTC"}) or []:
        try:
            t = datetime.strptime(f"{e['match_date']} {e['match_time']}", "%Y-%m-%d %H:%M").replace(tzinfo=timezone.utc)
        except (KeyError, ValueError):
            continue
        if abs((t - t0).total_seconds()) > 1800:
            continue
        sc = resolve_ids.sim(m["home_team"], e.get("match_hometeam_name", "")) + resolve_ids.sim(m["away_team"], e.get("match_awayteam_name", ""))
        if sc >= 1.4 and (best is None or sc > best[0]):
            best = (sc, e)
    return best[1] if best else None


def fetch_results(run, refresh=False):
    path = os.path.join(run, "resultados", "resultados.json")
    cur = common.read_json(path, {}) or {}
    inv = {m["match_id"]: m for m in common.read_json(os.path.join(run, "inventory.json"))["matches"]}
    ids = sorted(set(common.read_json(os.path.join(run, "ligas", "ids.json")).values()))
    key = adapters.apif_key()
    if not key:
        raise SystemExit("error: sin clave de apifootball")
    client = common.Client(os.path.join(run, "cache"), os.path.join(run, "sources", "consultas.jsonl"), policy=common.Policy(), min_interval=1.0, ttl=60)
    for mid in ids:
        if mid in cur and is_final(cur[mid]) and cur[mid].get("procedencia") and not refresh:
            continue
        aid = (inv[mid].get("source_match_ids") or {}).get("apifootball")
        if aid:
            ev = adapters.apif_call(client, key, action="get_events", match_id=aid, timezone="UTC")
            ev = ev if isinstance(ev, list) and ev and isinstance(ev[0], dict) else None
            how = "id del inventario"
        else:
            e0 = find_api_event(client, key, inv[mid])
            ev, aid, how = ([e0], e0["match_id"], "búsqueda por día, hora y nombres de ambos equipos") if e0 else (None, None, None)
        cur[mid] = parse_result(ev[0]) if ev else {"estado": "sin_resultado_en_la_api"}
        cur[mid]["api_match_id"] = aid
        cur[mid]["vinculo"] = how
        cur[mid]["consultado_utc"] = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    common.write_json_atomic(path, cur)
    return cur


# ── (2) liquidación de entradas del catálogo ──
def _cmp(total, line, op):
    if total == line:
        return VOID
    return WIN if ((total > line) == (op == "over")) else LOSE


def _ah(h, a, side, line):
    r = sg.settle_handicap_quarter(h, a, side, line)
    return {"win": WIN, "lose": LOSE, "void": VOID, "half_win": WIN + " (½)", "half_loss": LOSE + " (½)"}[r]


def settle_entry(e, r):
    """(resultado, dato_usado). Regla por mercado; sin dato → (SIN DATO, motivo). 'half' solo en hándicaps de cuarto de línea."""
    if not is_final(r):
        return NODATA, "partido sin resultado final (" + result_status(r).lower() + "): excluido del cálculo"
    h, a, h1, a1 = r["h"], r["a"], r.get("h1"), r.get("a1")
    eid, d, line = e["id"], e["direction"], e.get("line")
    if r.get("estado") in ("After ET", "After Pen.") and r.get("marcador_90_directo") is False and not eid.startswith(("primera_parte.", "corners.", "cards_pts.", "sot.", "shots.", "otros.")):
        return NODATA, "regla no confirmada: partido con prórroga/penales y la fuente no trae el marcador a 90' (el marcador general los incluye)"
    mk = e["market"]
    sel = lambda cond: WIN if cond else LOSE
    if eid.startswith("resultado.1x2."):
        return sel({"home": h > a, "draw": h == a, "away": h < a}[d]), f"{h}–{a}"
    if eid.startswith("resultado.dc."):
        return sel({"1x": h >= a, "12": h != a, "x2": h <= a}[d]), f"{h}–{a}"
    if eid.startswith("resultado.dnb."):
        return (VOID if h == a else sel((h > a) == (d == "home"))), f"{h}–{a}"
    if eid.startswith(("resultado.ah.", "resultado.ah_entero.")):
        return _ah(h, a, d, float(line)), f"{h}–{a}"
    if eid.startswith("resultado.eh."):
        hh = h + float(line)
        return sel({"home": hh > a, "draw": hh == a, "away": hh < a}[d]), f"{h}–{a} (hándicap {line:+g} al local)"
    if eid.startswith("primera_parte.1x2."):
        if h1 is None or a1 is None:
            return NODATA, "sin marcador al descanso"
        return sel({"home": h1 > a1, "draw": h1 == a1, "away": h1 < a1}[d]), f"descanso {h1}–{a1}"
    if eid.startswith("primera_parte.total."):
        if h1 is None or a1 is None:
            return NODATA, "sin marcador al descanso"
        return _cmp(h1 + a1, float(line), d), f"goles 1.ª parte {h1 + a1}"
    if eid.startswith(("goles.total.", "goles.total_entero.")):
        return _cmp(h + a, float(line), d), f"goles {h + a}"
    if eid.startswith("goles.btts."):
        return sel((h > 0 and a > 0) == (d == "yes")), f"{h}–{a}"
    if eid.startswith("goles.equipo."):
        return _cmp(h if e["scope"] == "home" else a, float(line), d), f"goles del equipo {h if e['scope'] == 'home' else a}"
    stat = {"corners": ("corners", "córners"), "cards_pts": ("tarjetas", "tarjetas (A=1, R=2)"), "sot": ("a_puerta", "remates a puerta"), "shots": ("remates", "remates"), "otros": ("fueras", "fueras de juego")}
    for pre, (k, name) in stat.items():
        if eid.startswith(pre + "."):
            v = r.get(k)
            if pre != "cards_pts" and r.get("estado") in ("After ET", "After Pen.") and v:
                return NODATA, f"regla no confirmada: partido con prórroga/penales y la fuente no separa los {name} de los 90'"
            if not v:
                return NODATA, f"la fuente no trae {name} de este partido"
            if pre == "corners" and sum(v) == 0:
                return NODATA, "córners 0–0: un cero total es dato dudoso de la fuente"      # un equipo con 0 y el otro con córners SÍ es un dato válido (5 partidos del 14 al 16-oct, bloques coincidentes)
            if pre == "otros":
                return NODATA, "regla no definida: la entrada de fueras de juego no trae línea"

            def total(vv):
                return vv[0] + vv[1] if e["scope"] == "match" else (vv[0] if e["scope"] == "home" else vv[1])
            tot = total(v)
            res_ = _cmp(tot, float(line), d)
            alt = r.get("tarjetas_alt") if pre == "cards_pts" else None
            if alt and _cmp(total(alt), float(line), d) != res_:
                return NODATA, f"regla no confirmada: una amarilla y una roja del mismo jugador en el mismo minuto (¿doble amarilla = 2 pts o amarilla + roja = 3 pts?): {tot} o {total(alt)} puntos cambian el resultado de esta línea"
            return res_, f"{name} {tot}"
    return NODATA, "mercado sin regla de liquidación"


# Reglas de liquidación por familia. estado: «estándar» (convención de las casas), «confirmada por la persona usuaria» o «NO CONFIRMADA» (se marca SIN DATO en vez de asumir).
RULES = [
    ("resultado.1x2", "1X2", "Marcador a 90' + descuento; la prórroga y los penales no cuentan.", "estándar"),
    ("resultado.dc", "Doble oportunidad", "Gana si se cumple cualquiera de los dos resultados a 90'.", "estándar"),
    ("resultado.dnb", "Empate no válido", "Empate = ANULADA (se devuelve la apuesta).", "estándar"),
    ("resultado.ah.", "Hándicap asiático, media línea", "Se suma la línea al equipo; sin devolución posible.", "estándar"),
    ("resultado.ah_entero", "Hándicap asiático, línea entera", "Si tras sumar la línea hay empate = ANULADA.", "estándar"),
    ("asian_handicap|", "Hándicap asiático de cuarto de línea (±.25/.75)", "La apuesta se divide en dos mitades en las líneas vecinas: ganada/perdida a medias o una mitad anulada.", "estándar"),
    ("resultado.eh", "Hándicap europeo (3 resultados)", "La línea se suma al local; 1 = local gana tras el hándicap, X = empate tras el hándicap, 2 = visitante.", "estándar"),
    ("goles.total.", "Goles totales, línea .5", "Más/menos de la línea a 90'; sin devolución.", "estándar"),
    ("goles.total_entero", "Goles totales, línea entera", "Si el total iguala la línea = ANULADA.", "estándar"),
    ("goles.equipo", "Goles de un equipo", "Goles de ese equipo a 90' + descuento.", "estándar"),
    ("goles.btts", "Ambos anotan", "Sí si ambos marcan ≥ 1 a 90'.", "estándar"),
    ("primera_parte", "1.ª parte (resultado y goles)", "Marcador al descanso (45' + descuento).", "estándar"),
    ("corners.", "Córners (total y por equipo)", "Córners de los 90' + descuento; se toma el mayor de los dos bloques de estadísticas de la fuente. Un equipo con 0 es un dato válido; 0–0 se trata como dato dudoso (SIN DATO). En partidos con prórroga/penales la fuente no separa los 90': NO CONFIRMADA.", "estándar (prórroga: NO CONFIRMADA)"),
    ("cards_pts", "Tarjetas (puntos)", "Amarilla = 1, roja = 2, máx. 3 por jugador; la 2.ª amarilla cuenta 2 EN TOTAL (confirmado por la persona usuaria el 13-oct); solo jugadores, 90' + descuento. Una amarilla y una roja del mismo jugador en el mismo minuto es ambiguo (¿2 o 3 puntos?): NO CONFIRMADA, solo se liquida si ambas lecturas dan el mismo resultado.", "confirmada por la persona usuaria (caso del mismo minuto: NO CONFIRMADA)"),
    ("sot.", "Remates a puerta", "Remates a puerta del partido según la fuente; en prórroga/penales NO CONFIRMADA.", "estándar (prórroga: NO CONFIRMADA)"),
    ("shots.", "Remates", "Remates totales del partido según la fuente; en prórroga/penales NO CONFIRMADA.", "estándar (prórroga: NO CONFIRMADA)"),
    ("otros.", "Fueras de juego", "La entrada del catálogo no define línea: no se liquida.", "NO CONFIRMADA"),
    ("total_goals_btts", "Total de goles + ambos anotan (combinado)", "Si el total iguala una línea entera se anula todo el combinado (la casa podría pagar solo el tramo restante).", "NO CONFIRMADA"),
    ("(estado)", "Partido en juego, aplazado, cancelado, suspendido o con dato inválido", "No se liquida ni entra en ningún cálculo (SIN DATO). Una casa suele anular o devolver; aquí solo se excluye.", "estándar (suspendido: NO CONFIRMADA)"),
    ("(combinada)", "Combinada del libro", "Pierde si alguna pata pierde; las patas ANULADAS se descartan (cuota 1); si todas se anulan, ANULADA; una pata SIN DATO sin ninguna perdida deja la combinada SIN DATO.", "estándar"),
]


def combo_status(res_list, odds_list):
    """(estado, cuota efectiva) de una combinada a partir de los resultados de sus patas. PERDIDA si alguna pata pierde (aunque otra no tenga dato);
    SIN DATO si ninguna perdió pero alguna no tiene dato; ANULADA si todas se anulan; GANADA en los demás casos, a la cuota de las patas ganadas (las anuladas valen 1)."""
    if any(r.startswith(LOSE) for r in res_list):
        return LOSE, None
    if any(r == NODATA for r in res_list):
        return NODATA, None
    wins = [o for r, o in zip(res_list, odds_list) if r.startswith(WIN)]
    if not wins:
        return VOID, 1.0
    eff = 1.0
    for o in wins:
        eff *= o
    return WIN, eff


def payoff(res, odds):
    """Beneficio por 1 unidad apostada (teórico, a la cuota del libro)."""
    if res.startswith(WIN):
        return (odds - 1) * (0.5 if "½" in res else 1)
    if res.startswith(LOSE):
        return -0.5 if "½" in res else -1.0
    return 0.0 if res == VOID else None


def hit(res):
    return 1 if res.startswith(WIN) else (0 if res.startswith(LOSE) else None)


# ── (3) picks del libro ──
def read_book(path):
    import openpyxl
    wb = openpyxl.load_workbook(path, read_only=True, data_only=True)
    out = {}
    for name in ("Ranking seguridad", "Ranking atractivo-cuota", "Top por liga", "Combinadas"):
        rows = list(wb[name].iter_rows(values_only=True))
        out[name] = [dict(zip(rows[0], r)) for r in rows[1:] if any(c is not None for c in r)]
    return out


def match_leg(legs_by_key, partido, seleccion):
    return legs_by_key.get((partido, seleccion))


def hhmm(utc_iso):
    return datetime.fromisoformat(utc_iso.replace("Z", "+00:00")).astimezone(CCS).strftime("%d-%b %H:%M")


# ── (4) libro ──
def dia_caracas(utc_iso):
    """Fecha local de Caracas (UTC−4) de un instante UTC ISO; `dia` del ledger es la fecha UTC (heredada) y no debe usarse para agrupar por día local."""
    dt = datetime.fromisoformat(utc_iso.replace("Z", "+00:00"))
    return (dt - timedelta(hours=4)).strftime("%Y-%m-%d")


def append_ledger(path, run, legs, inv, extra=None):
    """Registro acumulado de patas liquidadas (una línea por run+pata): probabilidad del modelo, cuota, estado de agentes, resultado y, desde el 16-oct, liga, hora de captura de la cuota,
    hora del partido, en qué rankings/combinadas salió y si la persona usuaria la jugó. Si la línea ya existe se COMPLETA con los campos nuevos (idempotente); nunca se borra nada."""
    rows = acu.leer(path)
    idx = {(d["run"], d["leg_id"]): d for d in rows}
    n = 0
    for l in legs:
        if l.get("p_modelo") is None or l.get("cuota") is None or l["res"] == NODATA:
            continue
        nuevo = {"run": run, "dia": inv[l["match_id"]]["normalized_datetime_utc"][:10], "dia_caracas": dia_caracas(inv[l["match_id"]]["normalized_datetime_utc"]), "leg_id": l["leg_id"], "partido_id": l["match_id"], "grupo": l["grupo"], "p": l["p_modelo"], "cuota": l["cuota"],
                 "precio_tipo": l["precio_tipo"], "agentes": l["agentes"], "elegible": not l["motivos_exclusion"], "res": l["res"],
                 "hora_utc": inv[l["match_id"]]["normalized_datetime_utc"], "observado_utc": l.get("observado_utc"), "liga": (extra or {}).get("liga", {}).get(l["match_id"]),
                 "partido": l.get("partido"), "cuota_usuario": l.get("cuota_usuario"), "p_mercado": l.get("p_mercado"), "p_pinnacle": l.get("p_pinnacle"), "n_casas": l.get("n_casas"), "entry_id": l.get("entry_id")}
        nuevo.update((extra or {}).get("legs", {}).get(l["leg_id"], {}))
        cur = idx.get((run, l["leg_id"]))
        if cur is None:
            rows.append(nuevo)
            idx[(run, l["leg_id"])] = nuevo
            n += 1
        else:
            cur.update({k: v for k, v in nuevo.items() if v is not None})
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as fh:
        for d in rows:
            fh.write(json.dumps(d, ensure_ascii=False) + "\n")
    os.replace(tmp, path)
    return n


def append_combos(path, run, filas):
    """Registro acumulado de combinadas liquidadas (se reescriben las del run). filas: dicts con objetivo, opcion, cuota_total, estado, beneficio, p_libro, agentes, patas."""
    rows = [d for d in acu.leer(path) if d.get("run") != run]
    rows += [dict(run=run, **f) for f in filas]
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as fh:
        for d in rows:
            fh.write(json.dumps(d, ensure_ascii=False) + "\n")
    os.replace(tmp, path)
    return len(filas)


def agents_at_commit(run, sha):
    """Informes de agentes del run tal como estaban en un commit: (reports, unidades del paquete). Permite ver qué estado tenía cada pata cuando se decidió."""
    import subprocess
    import tempfile
    tmp = tempfile.mkdtemp(prefix="agentes_commit_")
    os.makedirs(os.path.join(tmp, "agentes"))
    for f in ("informe_verificador.json", "informe_deportivo.json", "informe_cuantitativo.json", "informe_auditor.json", "paquete.json"):
        out = subprocess.run(["git", "show", f"{sha}:{run.rstrip('/')}/agentes/{f}"], capture_output=True, text=True)
        if out.returncode == 0:
            with open(os.path.join(tmp, "agentes", f), "w", encoding="utf-8") as fh:
                fh.write(out.stdout)
    pack = common.read_json(os.path.join(tmp, "agentes", "paquete.json"), None)
    return ar.load_reports(tmp), (pack or {}).get("unidades") or None


def build(run, book_path, out_path, refresh=False, ledger=None, user_picks=None, agentes_commit=None):
    from openpyxl import Workbook
    from openpyxl.styles import Alignment, Font, PatternFill
    from openpyxl.utils import get_column_letter

    results = fetch_results(run, refresh)
    ids_map = common.read_json(os.path.join(run, "ligas", "ids.json"))
    ids = sorted(set(ids_map.values()))
    cap = (os.path.join(run, "ligas", "partidos_usuario.json"), os.path.join(run, "ligas", "ids.json"))
    units, summary = ar.build_units(run, ids, cap)
    reports = ar.load_reports(run)
    rev = cr.reviewed_prices(run)
    pack = common.read_json(os.path.join(run, "agentes", "paquete.json"), None)
    legs = cr.legs_from_units(units, cr.agent_status(units, reports, rev, (pack or {}).get("unidades") or None), rev)
    then = {}
    if agentes_commit:
        rep_then, pack_then = agents_at_commit(run, agentes_commit)
        then = {l["leg_id"]: l["agentes"] for l in cr.legs_from_units(units, cr.agent_status(units, rep_then, rev, pack_then), rev)}
    ent = {e["id"]: e for e in mc.CATALOG}
    inv = {m["match_id"]: m for m in common.read_json(os.path.join(run, "inventory.json"))["matches"]}
    liga_de = {}
    for u in units:
        liga_de[u["match_id"]] = u.get("liga")
    cap_json = common.read_json(cap[0])
    liga_cap = {}
    for liga, h, a, *_ in cap_json["partidos"]:
        mid = ids_map.get(f"{h}|{a}")
        if mid:
            liga_cap[mid] = liga

    # liquidar todo el catálogo con modelo y precio
    for l in legs:
        eid = l["leg_id"].split("|", 1)[1]
        l["entry_id"] = eid
        l["res"], l["dato"] = settle_entry(ent[eid], results.get(l["match_id"], {}))
    def kind_of(eid):
        return "1t" if eid.startswith("primera_parte.") else "corners" if eid.startswith("corners.") else "goles" if eid.startswith(("goles.", "resultado.")) else "otro"

    def src(l):
        return provenance_text(results.get(l["match_id"], {}), kind_of(l["entry_id"]))

    def px(l):
        """(hora de captura de la cuota en Caracas, horas entre la captura y el inicio del partido)."""
        o = l.get("observado_utc")
        if not o:
            return None, None
        def _utc(x):
            d_ = datetime.fromisoformat(x.replace("Z", "+00:00"))
            return d_ if d_.tzinfo else d_.replace(tzinfo=timezone.utc)
        t0, k0 = _utc(o), _utc(inv[l["match_id"]]["normalized_datetime_utc"])
        return t0.astimezone(CCS).strftime("%d-%b %H:%M"), round((k0 - t0).total_seconds() / 3600, 1)
    by_key = {(l["partido"], l["etiqueta"]): l for l in legs}
    by_key_nm = {}
    for l in legs:
        by_key_nm.setdefault((l["partido"], l["etiqueta"]), l)

    book = read_book(book_path)
    miss = []

    # picks de la persona usuaria (*): línea EXACTA del catálogo cuando existe
    import registrar_tickets as rt
    fecha_run = re.search(r"(\d{4}-\d{2}-\d{2})", run).group(1)
    day_label = f"{int(fecha_run[8:])}-oct"
    spec_u = common.read_json(os.path.join(run, "seguimiento", "tickets_abiertos.json"), None)
    reg_u = [json.loads(x) for x in open(user_picks, encoding="utf-8") if x.strip()] if user_picks and os.path.exists(user_picks) else []
    reg_u = [r for r in reg_u if r.get("fecha") == fecha_run]
    user_star = defaultdict(list)       # (partido, etiqueta) -> tickets
    user_rows = []                      # (ticket, pata, patas del catálogo que la componen, nota, registro de resultado)
    if spec_u:
        res_by = {(r["ticket"], r["partido"], r["mercado"]): r for r in reg_u}
        for t in spec_u["tickets"]:
            for p in t["patas"]:
                found, nota = rt.catalog_legs(legs, p["mid"], p)
                for lg_ in found:
                    user_star[(lg_["partido"], lg_["etiqueta"])].append(t["id"])
                user_rows.append((t, p, found, nota, res_by.get((t["id"], p["partido"], p["mercado"]))))

    def star(partido, sel):
        return sel + " *" if user_star.get((partido, sel)) else sel

    def settle_row(row, partido_col="Partido", sel_col="Selección", odds_col="Cuota"):
        l = by_key.get((row[partido_col], row[sel_col]))
        if not l:
            miss.append((row[partido_col], row[sel_col]))
            return None
        odds = row.get(odds_col)
        return l, l["res"], l["dato"], odds

    wb = Workbook()
    H = PatternFill("solid", fgColor="1F3864")
    GREEN, RED, GREY, AMBER = (PatternFill("solid", fgColor=c) for c in ("C6EFCE", "FFC7CE", "E7E6E6", "FFEB9C"))

    def sheet(title, headers, rows, widths=None, color_col=None, freeze="A2"):
        ws = wb.create_sheet(title[:31])
        ws.append(headers)
        for c in ws[1]:
            c.font, c.fill, c.alignment = Font(bold=True, color="FFFFFF"), H, Alignment(wrap_text=True, vertical="center")
        for r in rows:
            ws.append(r)
        ws.freeze_panes = freeze
        for i, hd in enumerate(headers, 1):
            w = (widths or {}).get(hd) or min(48, max(10, len(str(hd)) + 2))
            ws.column_dimensions[get_column_letter(i)].width = w
        if color_col:
            ci = headers.index(color_col) + 1
            for row in ws.iter_rows(min_row=2, min_col=ci, max_col=ci):
                for c in row:
                    v = str(c.value or "")
                    c.fill = GREEN if v.startswith(WIN) else RED if v.startswith(LOSE) else AMBER if v == VOID else GREY if v in (NODATA, "SIN DATO") else c.fill
        ws.auto_filter.ref = ws.dimensions
        return ws

    # resultados por partido
    res_rows = []
    for mid in ids:
        r, m = results.get(mid, {}), inv[mid]
        t = hhmm(m["normalized_datetime_utc"])
        stt = result_status(r)
        if stt == "FINALIZADO":
            marcador = f"{r['h']}–{r['a']}" + (" (prórroga/penales después)" if r.get("estado") != "Finished" else "")
            ht = f"{r['h1']}–{r['a1']}" if r.get("h1") is not None and r.get("a1") is not None else None
        else:                                               # aplazado, en juego o dato inválido: no se muestra marcador como si fuera final y no entra en ningún cálculo
            marcador, ht = f"— ({stt.lower()}: {r.get('estado') or 'sin estado'}{'; marcador recibido ' + str(r.get('h')) + '–' + str(r.get('a')) if stt in ('DATO INVÁLIDO', 'EN JUEGO') and r.get('h') is not None else ''})", None
        res_rows.append([t, liga_cap.get(mid) or m.get("competition"), f"{m['home_team']} – {m['away_team']}", marcador, ht,
                         f"{r['corners'][0]}–{r['corners'][1]} ({sum(r['corners'])})" if r.get("corners") else "sin dato",
                         f"{r['tarjetas'][0]}–{r['tarjetas'][1]} ({sum(r['tarjetas'])})" if r.get("tarjetas") else "sin dato",
                         f"{r['a_puerta'][0]}–{r['a_puerta'][1]}" if r.get("a_puerta") else "sin dato", f"{r['remates'][0]}–{r['remates'][1]}" if r.get("remates") else "sin dato",
                         r.get("arbitro"), stt, provenance_text(r, "goles") + " | 1.ª parte: " + provenance_text(r, "1t").split("; ", 1)[-1] + " | córners: " + provenance_text(r, "corners").split("; ", 1)[-1]])
    # orden cronológico real
    order = {mid: inv[mid]["normalized_datetime_utc"] for mid in ids}
    res_rows = [x for _, x in sorted(zip([order[mid] for mid in ids], res_rows), key=lambda t: t[0])]

    # picks de cada hoja
    def pick_rows(name):
        rows = []
        for row in book[name]:
            s = settle_row(row)
            if not s:
                continue
            l, res, dato, odds = s
            pf = payoff(res, odds) if odds else None
            rows.append((row, l, res, dato, odds, pf))
        return rows

    picks = {n: pick_rows(n) for n in ("Ranking seguridad", "Ranking atractivo-cuota", "Top por liga")}
    base_hdr = ["Hora Caracas", "Liga", "Partido", "Mercado", "Selección", "Cuota", "Tipo de precio", "P modelo %", "Agentes", "Resultado del partido", "Dato que decide", "Resultado del pick", "Beneficio por 1 u (teórico)", "Fuente del dato (lecturas que confirman)", "Cuota observada (Caracas)", "Horas entre la cuota y el inicio"]

    def fmt_row(row, l, res, dato, odds, pf, extra=None):
        r = results.get(l["match_id"], {})
        marcador = f"{r['h']}–{r['a']}" if r.get("h") is not None else r.get("estado")
        return ([row.get("Hora Caracas") or hhmm(inv[l["match_id"]]["normalized_datetime_utc"]), row.get("Liga") or liga_cap.get(l["match_id"]), row["Partido"], row.get("Mercado") or l["grupo"], star(row["Partido"], row["Selección"]), odds,
                 row.get("Tipo de precio"), row.get("P modelo %"), row.get("Agentes") or l.get("agentes"), marcador, dato, res, None if pf is None else round(pf, 2), src(l), *px(l)])

    pick_sheets = {}
    for n in ("Ranking seguridad", "Ranking atractivo-cuota"):
        pick_sheets[n] = [([row.get("#")] + fmt_row(row, l, res, dato, odds, pf)) for row, l, res, dato, odds, pf in picks[n]]
    top_rows = [[row.get("Ranking")] + fmt_row(row, l, res, dato, odds, pf) for row, l, res, dato, odds, pf in picks["Top por liga"]]

    # combinadas
    combos = defaultdict(list)
    for row in book["Combinadas"]:
        if row.get("Opción") is None:
            continue
        combos[(row["Objetivo"], row["Opción"])].append(row)
    comb_rows, comb_summary = [], []
    for (obj, opt), rows in combos.items():
        legs_res = []
        for row in rows:
            l = by_key.get((row["Partido"], row["Selección"]))
            if not l:
                miss.append((row["Partido"], row["Selección"]))
                continue
            res, dato = l["res"], l["dato"]
            legs_res.append((row, l, res, dato))
        estado, tot_odds_eff = combo_status([x[2] for x in legs_res], [x[0]["Cuota de la pata"] for x in legs_res])
        head = rows[0]
        n_w = sum(1 for _, _, r_, _ in legs_res if r_.startswith(WIN))
        pf = None if estado == NODATA else ((tot_odds_eff - 1) if estado == WIN else (0.0 if estado == VOID else -1.0))
        comb_summary.append((obj, opt, head["Cuota total"], head.get("P gana si fueran independientes %"), head.get("Estado agentes"), head.get("Tipo de cuota"), len(legs_res), n_w, estado, pf, [l_["leg_id"] for _, l_, _, _ in legs_res]))
        for row, l, res, dato in legs_res:
            r = results.get(l["match_id"], {})
            comb_rows.append([obj, opt, head["Cuota total"], estado, None if pf is None else round(pf, 2), row["Hora Caracas"], row["Partido"], star(row["Partido"], row["Selección"]), row["Cuota de la pata"],
                              f"{r['h']}–{r['a']}" if r.get("h") is not None else r.get("estado"), dato, res, src(l), *px(l)])

    # catálogo evaluado (todas las patas con modelo y precio)
    cat_rows, evald = [], []
    for l in legs:
        if l["p_modelo"] is None or l["cuota"] is None:
            continue
        h_ = hit(l["res"])
        cat_rows.append([hhmm(inv[l["match_id"]]["normalized_datetime_utc"]), liga_cap.get(l["match_id"]), l["partido"], l["grupo"], star(l["partido"], l["etiqueta"]), l["cuota"], l["precio_tipo"], round(l["p_modelo"] * 100, 1),
                         round(100 / l["cuota"], 1), l["agentes"], "sí" if not l["motivos_exclusion"] else "no", l["dato"], l["res"], src(l), *px(l)])
        if l["res"] not in (NODATA,):
            evald.append(l)

    # resúmenes
    def agg(items):
        """items: [(res, odds, p)] → n, ganadas, perdidas, anuladas, % acierto, ROI, p media, 1/cuota media"""
        g = sum(1 for r_, *_ in items if r_.startswith(WIN))
        pdd = sum(1 for r_, *_ in items if r_.startswith(LOSE))
        v = sum(1 for r_, *_ in items if r_ == VOID)
        sd = sum(1 for r_, *_ in items if r_ == NODATA)
        liq = [(x[0], x[1], x[2]) for x in items if x[0] != NODATA]
        pfs = [payoff(r_, o) for r_, o, _ in liq if o]
        roi = (sum(pfs) / len(pfs)) if pfs else None
        pm = [p for r_, o, p in liq if p is not None and (r_.startswith(WIN) or r_.startswith(LOSE))]
        im = [1 / o for r_, o, p in liq if o and (r_.startswith(WIN) or r_.startswith(LOSE))]
        acc = g / (g + pdd) if (g + pdd) else None
        ci_a, ci_r = cluster_ci(items)
        return [len(items), g, pdd, v, sd, None if acc is None else round(acc * 100, 1), None if roi is None else round(roi * 100, 1),
                None if not pm else round(sum(pm) / len(pm) * 100, 1), None if not im else round(sum(im) / len(im) * 100, 1), ci_a, ci_r, len({x[3] for x in items if len(x) > 3})]

    def items_from(prows):
        return [(res, odds, (row.get("P modelo %") / 100) if row.get("P modelo %") is not None else None, l["match_id"]) for row, l, res, dato, odds, pf in prows]

    sum_hdr = ["Conjunto", "Picks", "Ganados", "Perdidos", "Anulados", "Sin dato", "% acierto (ganados / liquidados)", "ROI teórico % (1 u por pick, a la cuota del libro)", "P modelo media %", "Prob. implícita media (1/cuota) %", "IC 95 % acierto (por partido)", "IC 95 % ROI % (por partido)", "Partidos distintos"]
    sum_rows = []
    for n in ("Ranking seguridad", "Ranking atractivo-cuota"):
        sum_rows.append([n] + agg(items_from(picks[n])))
    top_seg = [x for x in picks["Top por liga"] if x[0].get("Ranking") == "Seguridad"]
    top_atr = [x for x in picks["Top por liga"] if x[0].get("Ranking") != "Seguridad"]
    sum_rows.append(["Top por liga — seguridad"] + agg(items_from(top_seg)))
    sum_rows.append(["Top por liga — atractivo-cuota"] + agg(items_from(top_atr)))
    uniq = {}
    for n in picks:
        for row, l, res, dato, odds, pf in picks[n]:
            uniq[(l["leg_id"])] = (res, odds, (row.get("P modelo %") / 100) if row.get("P modelo %") is not None else None, l["match_id"])
    sum_rows.append(["Todos los picks de los rankings (sin repetir)"] + agg(list(uniq.values())))

    # combinadas
    comb_hdr = ["Objetivo", "Combinadas", "Ganadas", "Perdidas", "Sin dato", "% acierto", "Beneficio total por 1 u por combinada (teórico)", "P gana media según el libro %", "Patas ganadas / patas"]
    by_obj = defaultdict(list)
    for s_ in comb_summary:
        by_obj[s_[0]].append(s_)
    comb_sum_rows = []
    for obj, lst in by_obj.items():
        g = sum(1 for x in lst if x[8] == WIN)
        pdd = sum(1 for x in lst if x[8] == LOSE)
        sd = sum(1 for x in lst if x[8] == NODATA)
        pfs = [x[9] for x in lst if x[9] is not None]
        pm = [x[3] for x in lst if x[3] is not None]
        comb_sum_rows.append([obj, len(lst), g, pdd, sd, round(g / (g + pdd) * 100, 1) if g + pdd else None, round(sum(pfs), 2) if pfs else None, round(sum(pm) / len(pm), 1) if pm else None,
                              f"{sum(x[7] for x in lst)} / {sum(x[6] for x in lst)}"])
    gg = sum(1 for x in comb_summary if x[8] == WIN)
    pp = sum(1 for x in comb_summary if x[8] == LOSE)
    comb_sum_rows.append(["TODAS", len(comb_summary), gg, pp, sum(1 for x in comb_summary if x[8] == NODATA), round(gg / (gg + pp) * 100, 1) if gg + pp else None,
                          round(sum(x[9] for x in comb_summary if x[9] is not None), 2), None, f"{sum(x[7] for x in comb_summary)} / {sum(x[6] for x in comb_summary)}"])

    # catálogo: por estado de agentes, por familia, por banda de cuota, calibración por banda de p
    def band(x, edges):
        for lo, hi in edges:
            if lo <= x < hi:
                return f"{lo:g}–{hi:g}" if hi < 99 else f"≥ {lo:g}"
    cat_items = [(l["res"], l["cuota"], l["p_modelo"], l) for l in evald]
    # el catálogo trae AMBOS lados de cada línea (más y menos): la tasa global es ~50 % por construcción. Las tablas por filtro usan solo el lado que el modelo favorece (P ≥ 50 %) con cuota ≤ 2.10
    pick_items = [x for x in cat_items if x[2] >= 0.5 and x[1] <= 2.10]

    def table(keyf, title, order=None, items=None):
        grp = defaultdict(list)
        for res, o, p, l in (items if items is not None else pick_items):
            k = keyf(l)
            if k is not None:
                grp[k].append((res, o, p, l["match_id"]))
        keys = order or sorted(grp)
        return [[f"{title}: {k}"] + agg(grp[k]) for k in keys if k in grp]

    def agente_k(l):
        a = l["agentes"] or ""
        return a.split(":")[0]

    t_ag = table(agente_k, "Estado de agentes", ["aprobada", "objetada", "degradada", "rechazada", "sin_revision", "precio_nuevo_sin_revisar"])
    t_el = table(lambda l: "elegible para combinadas" if not l["motivos_exclusion"] else "no elegible", "Elegibilidad", ["elegible para combinadas", "no elegible"])
    t_gr = table(lambda l: l["grupo"], "Mercado")
    t_bc = table(lambda l: band(l["cuota"], [(1.0, 1.25), (1.25, 1.4), (1.4, 1.6), (1.6, 1.8), (1.8, 2.11)]), "Banda de cuota", ["1–1.25", "1.25–1.4", "1.4–1.6", "1.6–1.8", "1.8–2.11"])
    t_pm = table(lambda l: band(l["p_modelo"] * 100, [(0, 30), (30, 45), (45, 55), (55, 65), (65, 75), (75, 85), (85, 101)]), "P del modelo (%), todas las patas (ambos lados)", ["0–30", "30–45", "45–55", "55–65", "65–75", "75–85", "85–101"], cat_items)
    t_pr = table(lambda l: l["precio_tipo"], "Tipo de precio")
    t_lg = table(lambda l: liga_cap.get(l["match_id"]), "Liga")

    # hoja Léeme
    ws0 = wb.active
    ws0.title = "Léeme"
    from collections import Counter as _C
    stc = _C(result_status(results.get(mid, {})) for mid in ids)
    n_fin = stc.get("FINALIZADO", 0)
    exc = "; ".join(f"{v} {k.lower()}" for k, v in stc.items() if k != "FINALIZADO")
    sin_final = {k: v for k, v in stc.items() if k != "FINALIZADO"}
    lines = [
        (f"Comparativo de {os.path.basename(book_path)} contra los resultados reales (hora de Caracas)", True)] + ([
        (f"PROVISIONAL: {sum(sin_final.values())} de {len(ids)} partido(s) sin resultado final ({exc}). Sus patas salen SIN DATO y no entran en ningún porcentaje; vuelve a generar este archivo cuando terminen antes de usarlo como cierre del día.", True)] if sin_final else []) + [
        (f"Partidos: {len(ids)} del {day_label}; con resultado final: {n_fin}{(' · EXCLUIDOS del cálculo: ' + exc) if exc else ''}. Resultados y estadísticas: apifootball (marcador a 90', descanso, córners, tarjetas con A=1/R=2, remates).", False),
        ("Qué se evalúa: (1) los picks del libro tal como se entregaron — Ranking seguridad, Ranking atractivo-cuota, Top por liga y Combinadas — con su cuota de referencia; (2) TODAS las patas del catálogo con modelo y precio, para medir calibración y el efecto de los filtros de los agentes.", False),
        ("Liquidación (reglas completas y su estado en la hoja «Reglas de liquidación»): totales de línea entera y empate no válido = ANULADA (beneficio 0); hándicap asiático de cuarto de línea = mitad ganada/perdida; hándicap europeo aplica la línea al local; 1.ª parte = marcador al descanso. Queda SIN DATO (y no cuenta como acierto ni fallo) cuando la fuente no trae el dato (p. ej. tarjetas de una copa), cuando trae 0–0 de córners (dato dudoso; un equipo con 0 y el otro con córners SÍ es válido) o cuando la regla no está confirmada (prórroga/penales sin separar los 90', una amarilla y una roja del mismo jugador en el mismo minuto).", False),
        ("Beneficio/ROI teórico: se apuesta 1 unidad por pick a la cuota que mostraba el libro (referencia de agregador salvo las marcadas «ejecutable»). Las combinadas ganan solo si TODAS sus patas ganan (una pata anulada cuenta con cuota 1). No incluye margen de tu casa ni cuotas que se movieron.", False),
        ("Cómo leer el acierto: % acierto = ganados / (ganados + perdidos). Compáralo con la P media del modelo y con la probabilidad implícita 1/cuota: un modelo bien calibrado acierta cerca de su P media; el mercado, cerca de 1/cuota.", False),
        ("Advertencia de muestra: es UN día y pocas patas por tabla. Sirve para ver el orden de magnitud y detectar fallos de método; NO valida ni descarta el modelo (sigue sin validar) y no es una promesa de resultados futuros.", False),
        ("Asterisco (*): marca los picks que la persona usuaria jugó en sus propios tickets (hoja «Mis picks (asterisco)»). Se marcan las patas con línea en el catálogo (totales, córners del partido y por equipo, 1X2, doble oportunidad, hándicap, ambos anotan, 1.ª parte); los combos («Crear apuesta») se evalúan como producto de sus tramos asumiendo independencia (aproximación) y los cuartos de línea con la media línea contigua (cota inferior); ambas aproximaciones se rotulan en «Mis picks (asterisco)».", False),
        ("El libro original no se modifica. Las patas que no se pudieron cruzar con el catálogo del run se listan al final de esta hoja.", False)]
    for t, b in lines:
        ws0.append([t])
        ws0.cell(ws0.max_row, 1).font = Font(bold=b, size=13 if b else 11)
        ws0.cell(ws0.max_row, 1).alignment = Alignment(wrap_text=True, vertical="top")
    import congelar_version as cv
    ver = cv.lookup(book_path)
    if ver is None:
        fz, _ = cv.freeze(book_path, run, "congelada al hacer el comparativo (no se sabe cuándo se entregó esta versión)")
        ver = cv.lookup(book_path)
    ws0.append([f"Versión del libro evaluado: sha256 {cv.sha256(book_path)[:16]}…, congelada el {ver['creado_caracas']} (Caracas) como {ver['archivo']} (versión {ver['version']} de ese libro; nota: {ver.get('nota')})."])
    ws0.cell(ws0.max_row, 1).alignment = Alignment(wrap_text=True, vertical="top")
    if agentes_commit:
        ws0.append([f"Estados de agentes «cuando se decidió»: informes del commit {agentes_commit} (solo cambian los estados de agentes; precios y modelo son los actuales)."])
    if miss:
        ws0.append([f"Sin cruce con el catálogo ({len(miss)}): " + "; ".join(f"{a} / {b}" for a, b in miss[:20])])
    ws0.column_dimensions["A"].width = 150

    sheet("Resumen de acierto", sum_hdr, sum_rows, {"Conjunto": 46})
    ws = wb["Resumen de acierto"]
    ws.append([])
    ws.append(["COMBINADAS"] + [None] * 9)
    ws.append(comb_hdr)
    for r_ in comb_sum_rows:
        ws.append(r_)
    ws.append([])
    ws.append(["CATÁLOGO COMPLETO CON MODELO Y PRECIO (patas liquidables)"] + [None] * 9)
    ws.append(["Las tablas «P del modelo» usan todas las patas (más y menos de cada línea, por eso la tasa global ronda el 50 %); el resto usa solo el lado que el modelo favorece (P ≥ 50 %) con cuota ≤ 2.10."] + [None] * 9)
    ws.append(sum_hdr)
    ws.append(["Todas las patas con modelo y precio (ambos lados)"] + agg([(res, o, p, l["match_id"]) for res, o, p, l in cat_items]))
    ws.append(["Lado favorecido por el modelo, cuota ≤ 2.10"] + agg([(res, o, p, l["match_id"]) for res, o, p, l in pick_items]))
    for tbl in (t_el, t_ag, t_pm, t_bc, t_gr, t_pr, t_lg):
        for r_ in tbl:
            ws.append(r_)
    # modelo contra mercado (patas con P del mercado sin margen: par o trío completo): quién se acerca más al resultado
    ws.append([])
    ws.append(["MODELO CONTRA MERCADO (patas con P de mercado sin margen; ambos lados de cada línea)"] + [None] * 9)
    ws.append(["Conjunto", "Patas", "% real", "P modelo media %", "P mercado media %", "Brier modelo", "Brier mercado", "Brier Pinnacle (solo patas con Pinnacle)", "Patas con |modelo − mercado| > 10 pp", "% real en esas patas"])
    wm = [l for l in evald if l.get("p_mercado") is not None and l["res"].startswith((WIN, LOSE))]
    wp = [l for l in wm if l.get("p_pinnacle") is not None]
    def _br(lst, key):
        return None if not lst else round(sum((l[key] - (1 if l["res"].startswith(WIN) else 0)) ** 2 for l in lst) / len(lst), 4)
    for nom, lst in (("Todas las patas con P de mercado", wm), ("Lado favorecido por el modelo (P ≥ 50 %)", [l for l in wm if l["p_modelo"] >= 0.5])):
        dis = [l for l in lst if abs(l["p_modelo"] - l["p_mercado"]) > 0.10]
        pin = [l for l in lst if l.get("p_pinnacle") is not None]
        ws.append([nom, len(lst), None if not lst else round(sum(1 for l in lst if l["res"].startswith(WIN)) / len(lst) * 100, 1), None if not lst else round(sum(l["p_modelo"] for l in lst) / len(lst) * 100, 1),
                   None if not lst else round(sum(l["p_mercado"] for l in lst) / len(lst) * 100, 1), _br(lst, "p_modelo"), _br(lst, "p_mercado"),
                   None if not pin else round(sum((l["p_pinnacle"] - (1 if l["res"].startswith(WIN) else 0)) ** 2 for l in pin) / len(pin), 4), len(dis),
                   None if not dis else round(sum(1 for l in dis if l["res"].startswith(WIN)) / len(dis) * 100, 1)])
    for row in ws.iter_rows():
        if row[0].value in ("COMBINADAS", "CATÁLOGO COMPLETO CON MODELO Y PRECIO (patas liquidables)"):
            row[0].font = Font(bold=True, size=12)
    sheet("Resultados", ["Hora Caracas", "Liga", "Partido", "Marcador (90')", "Descanso", "Córners (total)", "Tarjetas A=1/R=2 (total)", "Remates a puerta", "Remates", "Árbitro", "Estado del resultado", "Fuente y lecturas que confirman"], res_rows, {"Partido": 42, "Liga": 28, "Marcador (90')": 38, "Fuente y lecturas que confirman": 110})
    sheet("Ranking seguridad", ["#"] + base_hdr, pick_sheets["Ranking seguridad"], {"Partido": 40, "Selección": 34, "Dato que decide": 30}, "Resultado del pick")
    sheet("Ranking atractivo-cuota", ["#"] + base_hdr, pick_sheets["Ranking atractivo-cuota"], {"Partido": 40, "Selección": 34, "Dato que decide": 30}, "Resultado del pick")
    sheet("Top por liga", ["Ranking"] + base_hdr, top_rows, {"Partido": 40, "Selección": 34, "Dato que decide": 30}, "Resultado del pick")
    sheet("Combinadas", ["Objetivo", "Opción", "Cuota total", "Resultado de la combinada", "Beneficio por 1 u (teórico)", "Hora Caracas", "Partido", "Selección", "Cuota de la pata", "Resultado del partido", "Dato que decide", "Resultado de la pata", "Fuente del dato (lecturas que confirman)", "Cuota observada (Caracas)", "Horas entre la cuota y el inicio"],
          comb_rows, {"Partido": 40, "Selección": 34, "Dato que decide": 30, "Resultado de la combinada": 16}, "Resultado de la pata")
    ws = wb["Combinadas"]
    ci = 4
    for row in ws.iter_rows(min_row=2, min_col=ci, max_col=ci):
        for c in row:
            v = str(c.value or "")
            c.fill = GREEN if v.startswith(WIN) else RED if v.startswith(LOSE) else GREY
    sheet("Catálogo evaluado", ["Hora Caracas", "Liga", "Partido", "Mercado", "Selección", "Cuota", "Tipo de precio", "P modelo %", "1/cuota %", "Agentes", "Elegible para combinadas", "Dato que decide", "Resultado de la pata", "Fuente del dato (lecturas que confirman)", "Cuota observada (Caracas)", "Horas entre la cuota y el inicio"],
          cat_rows, {"Partido": 40, "Selección": 36, "Dato que decide": 30}, "Resultado de la pata")
    # reglas de liquidación y motivos de SIN DATO del catálogo con modelo y precio (qué quedó fuera y por qué)
    nd_rows = _C(re.sub(r"\d+", "#", l["dato"]) for l in legs if l["res"] == NODATA and l["p_modelo"] is not None and l["cuota"] is not None)
    sheet("Reglas de liquidación", ["Prefijo / mercado", "Familia", "Regla aplicada", "Estado de la regla"], [list(x) for x in RULES], {"Prefijo / mercado": 20, "Familia": 40, "Regla aplicada": 110, "Estado de la regla": 40})
    wsr = wb["Reglas de liquidación"]
    wsr.append([])
    wsr.append(["PATAS SIN DATO por motivo (catálogo con modelo y precio de este día)"])
    wsr.cell(wsr.max_row, 1).font = Font(bold=True, size=12)
    wsr.append(["Motivo", "Patas", "¿Regla no confirmada?"])
    for c_ in wsr[wsr.max_row]:
        c_.font, c_.fill = Font(bold=True, color="FFFFFF"), H
    for mot, n_ in sorted(nd_rows.items(), key=lambda t: -t[1]):
        wsr.append([mot, n_, "sí" if "regla no confirmada" in mot or "regla no definida" in mot else "no"])
    # ── picks de la persona usuaria (*) ──
    def _rg(x):
        return WIN if x == "ACERTADA" else LOSE if x == "FALLADA" else NODATA
    appear = defaultdict(set)
    for nm, rows_ in (("Ranking seguridad", pick_sheets["Ranking seguridad"]), ("Ranking atractivo-cuota", pick_sheets["Ranking atractivo-cuota"]), ("Top por liga", top_rows), ("Combinadas", comb_rows)):
        for r_ in rows_:
            for c_ in r_:
                if isinstance(c_, str) and c_.endswith(" *"):
                    appear[(r_[3] if nm != "Combinadas" else r_[6], c_)].add(nm)
    mp_rows, mp_items = [], []
    for t, pata, found, nota, rr in user_rows:
        if not rr:
            continue
        res_u = _rg(rr["resultado"])
        p_u, ag_u, el_u = rt.combine(found) if found else (None, None, None)
        k = (found[0]["partido"], star(found[0]["partido"], found[0]["etiqueta"])) if found else None
        modelo = ("catálogo" if len(found) == 1 and not nota else "catálogo, " + nota) if found else ("sin evaluación: " + (nota or ""))
        mp_rows.append([t["id"], pata["partido"], pata["mercado"] + (" (" + " + ".join(l["etiqueta"] for l in found) + ")" if found else ""), pata["cuota"], round(100 / pata["cuota"], 1), res_u, rr.get("detalle"),
                        None if p_u is None else round(p_u * 100, 1), ag_u, None if el_u is None else ("sí" if el_u else "no"), modelo,
                        ", ".join(sorted(appear.get(k, []))) if k else None] + ([";".join(then.get(l["leg_id"], "—") for l in found) or None, None if not found else ("sí" if ";".join(then.get(l["leg_id"], "—") for l in found) != ag_u else "no")] if agentes_commit else []))
        mp_items.append({"res": res_u, "o": pata["cuota"], "p": p_u, "mid": pata["mid"], "ag": ag_u, "el": el_u, "found": bool(found), "exacta": bool(found) and not nota})
    if mp_rows:
        mp_rows.sort(key=lambda r_: (r_[0], r_[1]))
        sheet("Mis picks (asterisco)", ["Ticket", "Partido", "Pata", "Cuota", "1/cuota %", "Resultado", "Detalle", "P modelo %", "Agentes (sistema)", "Elegible para combinadas", "Cómo se evaluó con el modelo", "Aparece en el libro"] + (["Agentes cuando se decidió (commit %s)" % agentes_commit, "¿Cambió después?"] if agentes_commit else []), mp_rows,
              {"Partido": 40, "Pata": 52, "Detalle": 30, "Cómo se evaluó con el modelo": 54, "Aparece en el libro": 36}, "Resultado")
        ws = wb["Mis picks (asterisco)"]
        ws.append([])
        ws.append(["Resumen (con IC 95 % remuestreando partidos)"] + [None] * 11)
        hd_ = ["Conjunto", "Patas", "Ganadas", "Perdidas", "% acierto", "1/cuota media %", "P modelo media %", "IC 95 % acierto (por partido)"]
        ws.append(hd_)

        def agg_u(items):
            liq = [x for x in items if x["res"] in (WIN, LOSE)]
            g_ = sum(1 for x in liq if x["res"] == WIN)
            pm_ = [x["p"] for x in liq if x["p"] is not None]
            ci_ = cluster_ci([(x["res"], x["o"], x["p"], x["mid"]) for x in liq])[0]
            return [len(liq), g_, len(liq) - g_, None if not liq else round(g_ / len(liq) * 100, 1), None if not liq else round(sum(100 / x["o"] for x in liq) / len(liq), 1), None if not pm_ else round(sum(pm_) / len(pm_) * 100, 1), ci_]
        ws.append(["Todas las patas jugadas*"] + agg_u(mp_items))
        ws.append(["Evaluadas con el modelo (línea exacta, o producto/cota para combos y cuartos de línea)"] + agg_u([x for x in mp_items if x["found"]]))
        ws.append(["   de ellas, línea exacta del catálogo"] + agg_u([x for x in mp_items if x["exacta"]]))
        ws.append(["Sin evaluación posible (mercado sin equivalente en el catálogo)"] + agg_u([x for x in mp_items if not x["found"]]))
        for lab_, f_ in (("Elegibles para combinadas", lambda x: x["el"] is True), ("No elegibles", lambda x: x["el"] is False)):
            ws.append([lab_] + agg_u([x for x in mp_items if f_(x)]))
        for st in ("aprobada", "degradada", "rechazada", "objetada"):
            its = [x for x in mp_items if x["ag"] and x["ag"].startswith(st)]
            if its:
                ws.append([f"Agentes: {st}"] + agg_u(its))
        jug = [(res, o, p, l["match_id"]) for res, o, p, l in pick_items if user_star.get((l["partido"], l["etiqueta"]))]
        nojug = [(res, o, p, l["match_id"]) for res, o, p, l in pick_items if not user_star.get((l["partido"], l["etiqueta"]))]
        ws.append([])
        ws.append(["Comparación con el sistema (lado favorecido por el modelo, cuota ≤ 2.10)"] + [None] * 11)
        ws.append(sum_hdr)
        ws.append(["Líneas que jugó la persona usuaria*"] + agg(jug))
        ws.append(["Resto del catálogo"] + agg(nojug))
        ws.append(["Rankings y top del libro (sin repetir)"] + agg(list(uniq.values())))
        ws.append([])
        ws.append(["Las patas de un mismo partido no son independientes: el IC remuestrea partidos completos, no patas. Con tan pocos partidos el intervalo es muy ancho; sirve para NO sobre-interpretar la diferencia."] + [None] * 11)
        for row in ws.iter_rows():
            if row[0].value and str(row[0].value).startswith(("Resumen (con IC", "Comparación con el sistema")):
                row[0].font = Font(bold=True, size=12)

    # ── mercados adicionales de TheStatsAPI (fuera del catálogo): liquidación y acierto ──
    try:
        _, _, adic = ad.build(run, lambda mid: hhmm(inv[mid]["normalized_datetime_utc"]) if mid in inv else None, set(ids))
    except Exception:
        adic = []
    if adic:
        name_to_mid = {f"{inv[m]['home_team']} – {inv[m]['away_team']}": m for m in ids}
        ar_rows, items_ad = [], defaultdict(list)
        for row in adic:
            mid = name_to_mid.get(row[1])
            r_ = results.get(mid, {}) if mid else {}
            if not mid or not is_final(r_):
                continue
            res_, dato_ = ad.settle_additional(row[-1], r_)
            odds_ = row[5]
            pf_ = payoff(res_, odds_) if odds_ else None
            ar_rows.append(row[:11] + [dato_, res_, None if pf_ is None else round(pf_, 2)])
            if res_ != NODATA:
                items_ad[row[2]].append((res_, odds_, None, mid))
        if ar_rows:
            sheet("Adicionales evaluados", ["Hora Caracas", "Partido", "Mercado", "Línea", "Selección", "Cuota (mediana)", "N.º de casas", "P modelo % / distribución", "Cuota mínima justa", "Brecha (pp)", "EV teórico %", "Dato que decide", "Resultado", "Beneficio por 1 u (teórico)"],
                  ar_rows, {"Partido": 40, "Selección": 34, "P modelo % / distribución": 40}, "Resultado")
            wsx = wb["Adicionales evaluados"]
            wsx.append([])
            wsx.append(["Resumen por mercado (mercados que el catálogo no tiene; sin revisión de agentes; referencias de agregador)"])
            wsx.cell(wsx.max_row, 1).font = Font(bold=True, size=12)
            wsx.append(["Mercado"] + sum_hdr[1:])
            for k_, its_ in sorted(items_ad.items()):
                wsx.append([k_] + agg(its_))

    # ── registro acumulado (patas y combinadas) y estadística acumulada ──
    n_led = 0
    if ledger:
        memb = defaultdict(lambda: {"rankings": [], "combinadas": 0, "usuario": []})
        for nm in ("Ranking seguridad", "Ranking atractivo-cuota", "Top por liga"):
            for row, l, *_ in picks[nm]:
                if nm not in memb[l["leg_id"]]["rankings"]:
                    memb[l["leg_id"]]["rankings"].append(nm)
        for cs in comb_summary:
            for lid in cs[10]:
                memb[lid]["combinadas"] += 1
        for l in legs:
            tk = user_star.get((l["partido"], l["etiqueta"]))
            if tk:
                memb[l["leg_id"]]["usuario"] = sorted(set(tk))
        n_led = append_ledger(ledger, run, legs, inv, {"liga": liga_cap, "legs": {k: v for k, v in memb.items()}})
        goles_ = {}
        for r_ in acu.leer(ledger):
            rp = os.path.join(r_["run"], "resultados", "resultados.json")
            if r_["run"] not in goles_ and os.path.exists(rp):
                goles_[r_["run"]] = json.load(open(rp, encoding="utf-8"))
        acu.exportar_csv(acu.leer(ledger), os.path.join(os.path.dirname(ledger) or ".", "historial_patas.csv"),
                         {(run_, mid): v["h"] + v["a"] for run_, d_ in goles_.items() for mid, v in d_.items() if v.get("estado") == "Finished" and v.get("h") is not None and v.get("marcador_90_directo") is not False})
        comb_path = os.path.join(os.path.dirname(ledger) or ".", "ledger_combinadas.jsonl")
        append_combos(comb_path, run, [{"objetivo": c[0], "opcion": c[1], "cuota_total": c[2], "p_libro": c[3], "agentes": c[4], "tipo_cuota": c[5], "patas": c[6], "patas_ganadas": c[7], "estado": c[8], "beneficio": None if c[9] is None else round(c[9], 2), "leg_ids": c[10]} for c in comb_summary])
        led = acu.leer(ledger)
        runs_ = sorted({r["run"] for r in led})
        fav = acu.liquidadas(led, True)
        todas = acu.liquidadas(led, False)

        def blank(ws_, n_=10):
            ws_.append([None] * n_)

        def seccion(ws_, titulo, filas, nota=None):
            ws_.append([titulo] + [None] * 9)
            ws_.cell(ws_.max_row, 1).font = Font(bold=True, size=12)
            if nota:
                ws_.append([nota] + [None] * 9)
            ws_.append(acu.ENCABEZADO)
            for c_ in ws_[ws_.max_row]:
                c_.font, c_.fill = Font(bold=True, color="FFFFFF"), H
            for f_ in filas:
                ws_.append(f_)
            blank(ws_)

        wa = wb.create_sheet("Acumulado")
        wa.append([f"Acumulado de {len(runs_)} run(s): {', '.join(x.split('/')[-1] for x in runs_)}. Lado favorecido por el modelo (P ≥ 50 %), cuota ≤ 2.10, ganadas+perdidas. Intervalos remuestreando PARTIDOS completos (las patas del mismo partido no son independientes). Se actualiza en cada ejecución del comparativo."])
        wa.cell(1, 1).alignment = Alignment(wrap_text=True)
        wa.row_dimensions[1].height = 48
        wa.column_dimensions["A"].width = 58
        for col in "BCDEFGHIJ":
            wa.column_dimensions[col].width = 16
        seccion(wa, "Todo el lado favorecido", [acu.fila("Lado favorecido, cuota ≤ 2.10", fav)])
        rk_rows = []
        for nm in ("Ranking seguridad", "Ranking atractivo-cuota", "Top por liga"):
            f_ = acu.fila(nm, [r for r in fav if nm in (r.get("rankings") or [])])
            if f_:
                rk_rows.append(f_)
        f_ = acu.fila("Patas que salieron en alguna combinada", [r for r in fav if r.get("combinadas")])
        if f_:
            rk_rows.append(f_)
        f_ = acu.fila("Patas que jugó la persona usuaria*", [r for r in fav if r.get("usuario")])
        if f_:
            rk_rows.append(f_)
        seccion(wa, "Rankings del libro y picks del usuario*", rk_rows, "Cada pata cuenta una vez por ranking en el que salió. Las patas de usuario son solo las que tienen línea exacta en el catálogo.")
        seccion(wa, "Estado de agentes", acu.tabla(fav, lambda r: r["agentes"].split(":")[0]))
        seccion(wa, "Motivo del rechazo (solo estado «rechazada»)", acu.tabla([r for r in fav if r["agentes"].startswith("rechazada")], lambda r: r["agentes"]),
                "«Rechazada» suele significar dato no verificable, no riesgo deportivo: aquí se ve si esos motivos predicen o no la pérdida.")
        seccion(wa, "Elegibilidad para combinadas", acu.tabla(fav, lambda r: "elegible" if r["elegible"] else "no elegible"))
        seccion(wa, "Banda de cuota", acu.tabla(fav, lambda r: acu.banda_cuota(r["cuota"]), ["1–1.25", "1.25–1.4", "1.4–1.6", "1.6–1.8", "1.8–2.11"]))
        seccion(wa, "Mercado", acu.tabla(fav, lambda r: r["grupo"]))
        seccion(wa, "Liga (solo runs con liga registrada)", acu.tabla(fav, lambda r: r.get("liga")))
        seccion(wa, "Tipo de precio × antigüedad de la cuota", acu.tabla(fav, lambda r: f"{r['precio_tipo']} · {acu.antiguedad(r) or 'sin hora de captura'}"),
                "Antigüedad = horas entre la captura de la cuota y el inicio del partido. «Sin hora de captura»: las cuotas ejecutables vienen de capturas de pantalla de la persona usuaria sin hora registrada (se puede añadir «capturado_utc» en partidos_usuario.json) y las filas anteriores al 16-oct no la guardaban.")
        seccion(wa, "Por run (día)", acu.tabla(fav, lambda r: r["run"].split("/")[-1] + " · día " + r.get("dia_caracas", r["dia"])))
        comb_led = acu.leer(os.path.join(os.path.dirname(ledger) or ".", "ledger_combinadas.jsonl"))
        wa.append(["Combinadas acumuladas"] + [None] * 9)
        wa.cell(wa.max_row, 1).font = Font(bold=True, size=12)
        wa.append(["Objetivo", "Combinadas", "Ganadas", "Perdidas", "% acierto", "IC Wilson 95 % (patas correlacionadas: orientativo)", "Beneficio por 1 u", "Patas ganadas / patas", None, None])
        for c_ in wa[wa.max_row]:
            c_.font, c_.fill = Font(bold=True, color="FFFFFF"), H
        gobj = defaultdict(list)
        for c in comb_led:
            if c["estado"] in (WIN, LOSE):
                gobj[c["objetivo"]].append(c)
        for k, cs in sorted(gobj.items()) + [("TODAS", [c for v in gobj.values() for c in v])]:
            n_ = len(cs)
            w_ = sum(1 for c in cs if c["estado"] == WIN)
            z_ = 1.96
            ph = w_ / n_
            den = 1 + z_ * z_ / n_
            ctr = (ph + z_ * z_ / (2 * n_)) / den
            hw = z_ * math.sqrt(ph * (1 - ph) / n_ + z_ * z_ / (4 * n_ * n_)) / den
            wa.append([k, n_, w_, n_ - w_, round(ph * 100, 1), f"{(ctr - hw) * 100:.0f}–{(ctr + hw) * 100:.0f}", round(sum(c["beneficio"] or 0 for c in cs), 2), f"{sum(c['patas_ganadas'] for c in cs)} / {sum(c['patas'] for c in cs)}"])
        wa.freeze_panes = "B2"

        # curva de calibración (todas las patas, ambos lados) y su historial diario
        wc = wb.create_sheet("Calibración")
        curva = acu.curva_calibracion(todas)
        met = acu.metricas(todas)
        acu.guardar_historial(os.path.join(os.path.dirname(ledger) or ".", "calibracion_historial.jsonl"), todas, runs_)
        wc.append([f"Curva de calibración con {met.get('n', 0)} patas (ambos lados de cada línea) de {len(runs_)} run(s). Brier {met.get('brier')}, log-loss {met.get('logloss')}, ECE {met.get('ece')}. Una curva calibrada cae sobre la diagonal (frecuencia = P)."])
        wc.cell(1, 1).alignment = Alignment(wrap_text=True)
        wc.row_dimensions[1].height = 36
        wc.append(["Tramo de P %", "Patas", "P media %", "Frecuencia real %", "IC 95 % (por partido)", "Real − P (pp)"])
        for c_ in wc[2]:
            c_.font, c_.fill = Font(bold=True, color="FFFFFF"), H
        for c in curva:
            wc.append([c["tramo"], c["n"], c["p_media"], c["frecuencia"], c["ic95"], c["diferencia_pp"]])
        for col, w_ in zip("ABCDEF", (14, 10, 12, 18, 22, 14)):
            wc.column_dimensions[col].width = w_
        from openpyxl.chart import Reference, ScatterChart, Series
        ch = ScatterChart()
        ch.title, ch.style = "Calibración: P del modelo vs frecuencia real", 13
        ch.x_axis.title, ch.y_axis.title = "P media del modelo %", "Frecuencia real %"
        ch.x_axis.scaling.min, ch.x_axis.scaling.max = 0, 100
        ch.y_axis.scaling.min, ch.y_axis.scaling.max = 0, 100
        n_c = len(curva)
        xs, ys = Reference(wc, min_col=3, min_row=3, max_row=2 + n_c), Reference(wc, min_col=4, min_row=3, max_row=2 + n_c)
        sr = Series(ys, xs, title="Real")
        sr.marker.symbol = "circle"
        ch.series.append(sr)
        wc.append([])
        base_r = wc.max_row + 1
        wc.cell(base_r, 8, "diagonal x")
        wc.cell(base_r, 9, "diagonal y")
        for k_, v_ in enumerate((0, 100)):
            wc.cell(base_r + 1 + k_, 8, v_)
            wc.cell(base_r + 1 + k_, 9, v_)
        dg = Series(Reference(wc, min_col=9, min_row=base_r + 1, max_row=base_r + 2), Reference(wc, min_col=8, min_row=base_r + 1, max_row=base_r + 2), title="Calibrada")
        ch.series.append(dg)
        ch.height, ch.width = 9, 14
        wc.add_chart(ch, "H2")
        hist = acu.leer(os.path.join(os.path.dirname(ledger) or ".", "calibracion_historial.jsonl"))
        wc.append([])
        wc.append(["Historial (una línea por día de ejecución)"])
        wc.cell(wc.max_row, 1).font = Font(bold=True, size=12)
        wc.append(["Generado (UTC)", "Patas", "Brier", "Log-loss", "ECE", "Runs"])
        for c_ in wc[wc.max_row]:
            c_.font, c_.fill = Font(bold=True, color="FFFFFF"), H
        for h_ in hist:
            m_ = h_["metricas"]
            wc.append([h_["generado_utc"], m_.get("n"), m_.get("brier"), m_.get("logloss"), m_.get("ece"), ", ".join(x.split("/")[-1] for x in h_["runs"])])

    wb.save(out_path)
    return {"ledger_agregadas": n_led, "partidos": len(ids), "finalizados": n_fin, "sin_cruce": miss, "resumen": sum_rows, "combinadas": comb_sum_rows, "catalogo": [["Todas"] + agg([(res, o, p, l["match_id"]) for res, o, p, l in cat_items]), ["Lado favorecido"] + agg([(res, o, p, l["match_id"]) for res, o, p, l in pick_items])], "por_agentes": t_ag, "por_p": t_pm, "elegibles": t_el, "por_grupo": t_gr}


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--run", required=True)
    ap.add_argument("--book", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--refresh", action="store_true")
    ap.add_argument("--agentes-commit", help="commit de git con los informes de agentes tal como estaban al decidir; añade en «Mis picks» el estado de cada pata en ese momento")
    ap.add_argument("--user-picks", help="registro de las patas de la persona usuaria (data/registro_tickets_usuario.jsonl): sus picks se marcan con * y salen en la hoja «Mis picks (asterisco)»")
    ap.add_argument("--ledger", help="añade las patas liquidadas a este registro acumulado (p. ej. data/ledger_patas.jsonl) para auditar los filtros")
    a = ap.parse_args(argv)
    if os.path.basename(a.out) in ("ligas-14-oct.xlsx", "ligas-14-oct-v2.xlsx"):
        raise SystemExit("el comparativo nunca puede llamarse como un libro original")
    info = build(a.run, a.book, a.out, a.refresh, a.ledger, a.user_picks, a.agentes_commit)
    print(json.dumps({k: v for k, v in info.items() if k in ("partidos", "finalizados", "sin_cruce", "ledger_agregadas")}, ensure_ascii=False))
    for k in ("resumen", "combinadas", "catalogo", "por_agentes", "por_p", "elegibles"):
        print(k)
        for r in info[k]:
            print("  ", r)
    return 0


if __name__ == "__main__":
    sys.exit(main())
