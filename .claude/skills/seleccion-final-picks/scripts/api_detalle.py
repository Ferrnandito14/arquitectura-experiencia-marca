#!/usr/bin/env python3
"""Detalle de cuotas de las APIs que el catálogo no muestra: (1) precio de CADA casa por selección, (2) movimiento apertura → último precio visto y (3) mercados adicionales que TheStatsAPI trae
y el catálogo no tiene (marcador exacto, 2.ª parte, ambos anotan por mitad, goles + ambos anotan, primer gol, hándicap de cuarto de línea…), con la probabilidad del modelo propio donde se puede calcular.
Todo son REFERENCIAS de agregador (no ejecutables). Los mercados adicionales NO pasan por los agentes ni entran en rankings ni combinadas: se muestran aparte y rotulados.
Funciones puras para poder probarlas sin red. Fuentes: `<run>/thestatsapi/odds/*.json` + `map.json` (cuotas por casa con apertura y último precio) y las respuestas `get_odds` de apifootball en la caché del run."""
import json
import math
import os
import statistics
import sys
from collections import defaultdict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import leg_model  # noqa: E402

SIDE = {"home": "Local", "away": "Visitante", "draw": "Empate", "yes": "Sí", "no": "No"}
DC = {"home_draw": "Local o empate (1X)", "home_away": "Gana alguno, sin empate (12)", "draw_away": "Empate o visitante (X2)"}
NAMES = {"match_odds": "Resultado 1X2", "btts": "Ambos anotan", "total_goals": "Goles totales", "match_corners": "Córners totales", "total_cards": "Tarjetas totales (regla de la casa de la fuente)",
         "match_shots": "Remates totales", "match_shots_on_target": "Remates a puerta totales", "asian_handicap": "Hándicap asiático", "draw_no_bet": "Empate no válido", "double_chance": "Doble oportunidad",
         "first_half_result": "1.ª parte: resultado", "second_half_result": "2.ª parte: resultado", "half_time_double_chance": "1.ª parte: doble oportunidad", "handicap_result": "Hándicap europeo",
         "team_total_goals": "Goles por equipo", "team_corners": "Córners por equipo", "team_shots": "Remates por equipo", "team_shots_on_target": "Remates a puerta por equipo",
         "btts_first_half": "1.ª parte: ambos anotan", "btts_second_half": "2.ª parte: ambos anotan", "first_half_total_goals": "1.ª parte: goles totales", "total_goals_btts": "Goles totales + ambos anotan",
         "correct_score": "Marcador exacto", "first_team_to_score": "Primer equipo en anotar", "a_penalty_in_match": "Hay penal en el partido", "to_score_a_penalty": "Equipo que anota un penal",
         "to_miss_a_penalty": "Equipo que falla un penal"}
BOOKS = ("Bet365", "Pinnacle", "Paddy Power", "BetMGM UK", "Betfair Exchange")
# mercados que el catálogo ya cubre (con esas líneas): el resto va a «Mercados adicionales»
CATALOGADOS = {"match_odds", "btts", "total_goals", "match_corners", "total_cards", "match_shots", "match_shots_on_target", "draw_no_bet", "double_chance", "first_half_result", "handicap_result",
               "team_total_goals", "team_corners", "team_shots", "team_shots_on_target", "first_half_total_goals"}


def walk(node, path=()):
    """Hojas {opening, last_seen} de un mercado anidado → (ruta, apertura, último)."""
    if isinstance(node, dict) and ("last_seen" in node or "opening" in node):
        f = lambda x: None if x in (None, "") else float(x)
        yield list(path), f(node.get("opening")), f(node.get("last_seen"))
    elif isinstance(node, dict):
        for k, v in node.items():
            yield from walk(v, path + (str(k),))


def describe(market, path):
    """(mercado en español, línea, selección en español, clave estable) de una hoja."""
    mk = NAMES.get(market, market)
    p = list(path)
    key = market + "|" + "|".join(p)
    ou = lambda w, l: f"{'Más' if w == 'over' else 'Menos'} de {l}"
    if market in ("total_goals", "match_corners", "total_cards", "match_shots", "match_shots_on_target", "first_half_total_goals") and len(p) == 2:
        return mk, p[0], ou(p[1], p[0]), key
    if market in ("team_total_goals", "team_corners", "team_shots", "team_shots_on_target") and len(p) == 3:
        return mk, p[1], f"{SIDE.get(p[0], p[0])}: {ou(p[2], p[1])}", key
    if market == "asian_handicap" and len(p) == 2:
        return mk, p[1], f"{SIDE.get(p[0], p[0])} {p[1]}", key
    if market == "handicap_result" and len(p) == 2:
        return mk, p[0], f"{SIDE.get(p[1], p[1])} (hándicap {p[0]} al local)", key
    if market in ("double_chance", "half_time_double_chance") and len(p) == 1:
        return mk, None, DC.get(p[0], p[0]), key
    if market == "total_goals_btts" and len(p) == 2:
        w, y = p[1].split("_")[0], p[1].split("_")[-1]
        return mk, p[0], f"{ou(w, p[0])} y ambos anotan {'sí' if y == 'yes' else 'no'}", key
    if market == "correct_score" and len(p) == 1:
        return mk, None, p[0].replace("-", "–"), key
    if len(p) == 1:
        return mk, None, SIDE.get(p[0], p[0]), key
    return mk, None, " / ".join(SIDE.get(x, x) for x in p), key


def load_tsa(run):
    """{match_id: {"home","away","utc","fetched_utc","books": {casa: {mercado: árbol}}}} de lo que TheStatsAPI devolvió para el run."""
    mp = os.path.join(run, "thestatsapi", "map.json")
    if not os.path.exists(mp):
        return {}
    with open(mp, encoding="utf-8") as fh:
        m = json.load(fh).get("partidos", {})
    out = {}
    for mid, info in m.items():
        f = os.path.join(run, "thestatsapi", "odds", f"{info.get('tsa_id')}.json")
        if not info.get("odds_available") or not os.path.exists(f):
            continue
        with open(f, encoding="utf-8") as fh:
            d = json.load(fh)
        data = ((d.get("response") or {}).get("data")) or {}
        out[mid] = {"home": info["home"], "away": info["away"], "utc": info.get("utc_date"), "fetched_utc": d.get("fetched_utc"), "books": {b["bookmaker"]: b.get("markets") or {} for b in data.get("bookmakers", [])}}
    return out


def selections(tsa_match):
    """{(mercado_clave, ruta): {"desc": (...), "casas": {casa: (apertura, último)}}} para un partido."""
    out = {}
    for book, markets in tsa_match["books"].items():
        for mk, tree in markets.items():
            for path, op, last in walk(tree):
                k = (mk, tuple(path))
                out.setdefault(k, {"desc": describe(mk, path), "casas": {}})["casas"][book] = (op, last)
    return out


def _med(xs):
    xs = [x for x in xs if x is not None]
    return round(statistics.median(xs), 3) if xs else None


def resumen(sel):
    """Mediana/mín/máx de apertura y último, nº de casas, y mejor casa."""
    ops = [v[0] for v in sel["casas"].values()]
    lst = [v[1] for v in sel["casas"].values()]
    lastc = {b: v[1] for b, v in sel["casas"].items() if v[1] is not None}
    best = max(lastc.values()) if lastc else None
    mo, ml = _med(ops), _med(lst)
    delta = None if not mo or not ml else round((ml / mo - 1) * 100, 1)
    return {"apertura": mo, "ultimo": ml, "min": min([x for x in lst if x is not None], default=None), "max": max([x for x in lst if x is not None], default=None), "n": len(lastc),
            "n_aper": sum(1 for x in ops if x is not None), "delta_pct": delta, "mejor": ", ".join(sorted(b for b, x in lastc.items() if x == best)) if best else None}


APIF_KEY = {"match_odds": ("resultado.1x2", {"home": 0, "draw": 1, "away": 2}), "double_chance": ("resultado.doble_oportunidad", {"home_draw": 0, "home_away": 1, "draw_away": 2}),
            "btts": ("goles.btts", {"yes": 0, "no": 1})}


def apif_key(market, path):
    """(clave de _ODDS_PAIRS de apifootball, posición) de la misma selección, o None si apifootball no publica ese mercado."""
    import adapters
    if market in APIF_KEY and len(path) == 1:
        k, idx = APIF_KEY[market]
        return (k, idx[path[0]]) if path[0] in idx else None
    if market == "total_goals" and len(path) == 2:
        return ("goles.over_" + adapters.line_tag(float(path[0])).replace(".", "_"), 0 if path[1] == "over" else 1)
    if market == "asian_handicap" and len(path) == 2:
        L = float(path[1])
        if round(L * 2) != L * 2:
            return None                                              # cuartos de línea: apifootball no los publica
        if path[0] == "home":
            return ("resultado.handicap" + adapters.line_tag(L, signed=True), 0)
        return ("resultado.handicap" + adapters.line_tag(-L, signed=True), 1)
    return None


# ── modelo propio para los mercados adicionales (mismo modelo Poisson que el catálogo; sin recalibrar) ──
def goal_grids(lh, la, share):
    full = leg_model.grid(lh, la)
    first = leg_model.grid(lh * share, la * share) if share is not None else None
    second = leg_model.grid(lh * (1 - share), la * (1 - share)) if share is not None else None
    return full, first, second


def _sum(g, cond):
    n = len(g)
    return sum(g[i][j] for i in range(n) for j in range(n) if cond(i, j))


def p_additional(market, path, lh, la, share):
    """P del modelo (o None si no hay modelo) de una selección de un mercado adicional. Para el hándicap de cuarto de línea devuelve un dict de resultados; para el resto, una probabilidad."""
    full, first, second = goal_grids(lh, la, share)
    p = list(path)
    if market == "correct_score" and len(p) == 1:
        try:
            i, j = (int(x) for x in p[0].split("-"))
        except ValueError:
            return None
        return full[i][j] if i < len(full) and j < len(full) else None
    if market == "second_half_result" and second:
        return _sum(second, {"home": lambda i, j: i > j, "draw": lambda i, j: i == j, "away": lambda i, j: i < j}[p[0]])
    if market == "half_time_double_chance" and first:
        return _sum(first, {"home_draw": lambda i, j: i >= j, "home_away": lambda i, j: i != j, "draw_away": lambda i, j: i <= j}[p[0]])
    if market == "btts_first_half" and first:
        q = _sum(first, lambda i, j: i > 0 and j > 0)
        return q if p[0] == "yes" else 1 - q
    if market == "btts_second_half" and second:
        q = _sum(second, lambda i, j: i > 0 and j > 0)
        return q if p[0] == "yes" else 1 - q
    if market == "total_goals_btts" and len(p) == 2:
        line = float(p[0])
        w, y = p[1].split("_")[0], p[1].split("_")[-1]
        return _sum(full, lambda i, j: ((i + j > line) == (w == "over")) and ((i > 0 and j > 0) == (y == "yes")))
    if market == "first_team_to_score":
        lam = lh + la
        if p[0] in ("home", "away") and lam > 0:
            return (lh if p[0] == "home" else la) / lam * (1 - math.exp(-lam))
        if p[0] in ("none", "no_goal", "no_goals"):
            return math.exp(-lam)
        return None
    if market == "asian_handicap" and len(p) == 2:
        import seguimiento as sg
        side, L = p[0], float(p[1])
        out = defaultdict(float)
        n = len(full)
        for i in range(n):
            for j in range(n):
                out[sg.settle_handicap_quarter(i, j, side, L)] += full[i][j]
        return dict(out)
    return None


ES = {"win": "gana", "half_win": "media ganada", "void": "devuelve", "half_loss": "media perdida", "lose": "pierde"}


def ah_ev(o, outs):
    """EV exacto de una apuesta de hándicap a cuota `o` con la distribución de resultados {win, half_win, void, half_loss, lose}."""
    return outs.get("win", 0) * (o - 1) + outs.get("half_win", 0) * 0.5 * (o - 1) - outs.get("half_loss", 0) * 0.5 - outs.get("lose", 0)


def model_params(run, match_id):
    """(λ local, λ visitante, fracción de goles de la 1.ª parte) del modelo propio para un partido, o None. Mismos datos que el catálogo (matrix.json, mismas filas de la competición)."""
    import common
    inv = common.read_json(os.path.join(run, "inventory.json"), {"matches": []})["matches"]
    mx = (common.read_json(os.path.join(run, "matrix.json"), {"matches": {}})["matches"]).get(match_id) or {}
    f = mx.get("form") or {}
    me = next((m for m in inv if m["match_id"] == match_id), None)
    if not me or len(f.get("local", [])) < 6 or len(f.get("visitante", [])) < 6:
        return None
    mx_all = common.read_json(os.path.join(run, "matrix.json"), {"matches": {}})["matches"]
    rows = []
    for m in inv:
        if m.get("competition") == me.get("competition"):
            ff = (mx_all.get(m["match_id"]) or {}).get("form") or {}
            for side in ("local", "visitante"):
                rows += [r for r in ff.get(side, []) if r.get("misma_competicion")]
    if not rows:
        return None
    mu, adv = leg_model.league_means([rows])
    if not mu:
        return None
    lh, la = leg_model.expected_goals(f["local"], f["visitante"], mu, adv)
    return lh, la, leg_model.half_share(f["local"], f["visitante"])


_PARES = ("total_goals", "match_corners", "total_cards", "match_shots", "match_shots_on_target", "first_half_total_goals")
_PARES_EQ = ("team_total_goals", "team_corners", "team_shots", "team_shots_on_target")
OVERROUND = {2: (0.97, 1.15), 3: (0.97, 1.20)}       # mismo criterio que price_sources: un par/trío fuera del rango es un precio roto, no una cuota


def _entera(x):
    try:
        return float(x) == int(float(x))
    except (TypeError, ValueError):
        return False


def grupo_excluyente(mk, path):
    """Rutas de los resultados mutuamente excluyentes a los que pertenece la selección (par más/menos, sí/no, 1X2, hándicap asiático de media línea…) o None si no hay grupo completo
    (líneas enteras o de cuarto, doble oportunidad: la probabilidad de ganar no sale de normalizar el par)."""
    p = tuple(path)
    if mk in _PARES and len(p) == 2:
        return None if _entera(p[0]) else [(p[0], "over"), (p[0], "under")]
    if mk in _PARES_EQ and len(p) == 3:
        return None if _entera(p[1]) else [(p[0], p[1], "over"), (p[0], p[1], "under")]
    if mk in ("btts", "btts_first_half", "btts_second_half") and len(p) == 1:
        return [("yes",), ("no",)]
    if mk == "draw_no_bet" and len(p) == 1:
        return [("home",), ("away",)]
    if mk in ("match_odds", "first_half_result", "second_half_result") and len(p) == 1:
        return [("home",), ("draw",), ("away",)]
    if mk == "handicap_result" and len(p) == 2:
        return [(p[0], "home"), (p[0], "draw"), (p[0], "away")]
    if mk == "asian_handicap" and len(p) == 2:
        try:
            L = float(p[1])
        except ValueError:
            return None
        if round(L * 2) != L * 2 or _entera(L):
            return None
        other = "away" if p[0] == "home" else "home"
        flip = ("-" if L > 0 else "+") + f"{abs(L):g}"
        return [(p[0], p[1]), (other, flip)]
    return None


def p_mercado_sin_margen(sels, mk, path):
    """(P mediana sin margen, nº de casas con el grupo completo, P de Pinnacle) de una selección: cada casa se normaliza por separado (1/cuota ÷ suma del grupo) y luego se toma la mediana."""
    g = grupo_excluyente(mk, path)
    if not g:
        return None, 0, None
    me = tuple(path)
    nodes = [sels.get((mk, x)) for x in g]
    if any(n is None for n in nodes):
        return None, 0, None
    ps_, pin = [], None
    for book in BOOKS:
        xs = [(n["casas"].get(book) or (None, None))[1] for n in nodes]
        if any(x is None or x <= 1.0 for x in xs):
            continue
        ov = sum(1 / x for x in xs)
        lo, hi = OVERROUND[len(g)]
        if not lo <= ov <= hi:
            continue
        pb = (1 / xs[g.index(me)]) / ov
        ps_.append(pb)
        if book == "Pinnacle":
            pin = pb
    return (round(statistics.median(ps_), 4) if ps_ else None), len(ps_), (round(pin, 4) if pin is not None else None)


def clave_catalogo(mk, path):
    """Clave (mercado, lado, línea, selección) como la entrega `price_sources.tsa_lookup` para las entradas del catálogo."""
    p = list(path)
    if mk in _PARES and len(p) == 2:
        return (mk, None, p[0], p[1])
    if mk in _PARES_EQ and len(p) == 3:
        return (mk, p[0], p[1], p[2])
    if mk == "asian_handicap" and len(p) == 2:
        return (mk, p[0], p[1], None)
    if mk == "handicap_result" and len(p) == 2:
        return (mk, None, p[0], p[1])
    if len(p) == 1:
        return (mk, None, None, p[0])
    return None


def build(run, hora_caracas, match_ids=None, p_cat=None):
    """Tres tablas (listas de filas) para el libro: precio por casa, movimiento y mercados adicionales. `hora_caracas(match_id)` da el texto de la hora."""
    tsa = load_tsa(run)
    por_casa, mov, adic = [], [], []
    for mid, tm in sorted(tsa.items(), key=lambda t: hora_caracas(t[0]) or ""):
        if match_ids and mid not in match_ids:
            continue
        partido = f"{tm['home']} – {tm['away']}"
        hh = hora_caracas(mid)
        par = model_params(run, mid)
        sels_m = selections(tm)
        for (mk, path), sel in sorted(sels_m.items(), key=lambda t: (t[0][0], t[1]["desc"][1] or "", t[1]["desc"][2])):
            mer, linea, etiqueta, key = sel["desc"]
            r = resumen(sel)
            if r["ultimo"] is None:
                continue
            ak = apif_key(mk, path)
            pmk, pmn, ppin = p_mercado_sin_margen(sels_m, mk, path)
            pmod = (p_cat or {}).get((mid,) + (clave_catalogo(mk, path) or (None,) * 4))
            dif = None if (pmk is None or pmod is None) else round((pmod - pmk) * 100, 1)
            por_casa.append([hh, partido, mer, linea, etiqueta, r["n"], r["ultimo"], r["min"], r["max"]] + [(sel["casas"].get(b) or (None, None))[1] for b in BOOKS] + [r["mejor"], ak and ak[0],
                             None if pmk is None else round(pmk * 100, 1), pmn or None, None if ppin is None else round(ppin * 100, 1), None if pmod is None else round(pmod * 100, 1), dif,
                             None if dif is None else ("modelo y mercado difieren más de 10 pp" if abs(dif) > 10 else "")])
            if r["apertura"] is not None and r["n_aper"] >= 1 and r["ultimo"] <= 15:
                mov.append([hh, partido, mer, linea, etiqueta, r["n_aper"], r["apertura"], r["ultimo"], r["delta_pct"], "sube" if (r["delta_pct"] or 0) > 0 else "baja" if (r["delta_pct"] or 0) < 0 else "igual",
                            round(100 / r["apertura"], 1), round(100 / r["ultimo"], 1), round(100 / r["ultimo"] - 100 / r["apertura"], 1)])
            quarter = mk == "asian_handicap" and round(float(path[1]) * 4) % 2 == 1
            if mk in CATALOGADOS or (mk == "asian_handicap" and not quarter):
                continue
            p = p_additional(mk, path, *par) if par else None
            o = r["ultimo"]
            if mk == "correct_score" and (o > 30 or (p is not None and p < 0.03)):
                continue                                                  # marcadores improbables: ruido (solo los de P ≥ 3 % y cuota ≤ 30)
            if isinstance(p, dict):                                        # cuarto de línea: se muestra la distribución y el EV exacto
                ev = ah_ev(o, p)
                adic.append([hh, partido, mer, linea, etiqueta, o, r["n"], "; ".join(f"{ES.get(k, k)} {v * 100:.0f} %" for k, v in sorted(p.items(), key=lambda t: -t[1])), None, None, round(ev * 100, 1), "cuarto de línea: no está en el catálogo", key])
            else:
                ev = None if p is None else p * o - 1
                adic.append([hh, partido, mer, linea, etiqueta, o, r["n"], None if p is None else round(p * 100, 1), None if not p else round(1 / p, 3), None if p is None else round((p - 1 / o) * 100, 1),
                             None if ev is None else round(ev * 100, 1), "sin modelo propio para este mercado (solo precio)" if p is None else "mercado que el catálogo no tiene", key])
    return por_casa, mov, adic


HDR_CASA = ["Hora Caracas", "Partido", "Mercado", "Línea", "Selección", "N.º de casas", "Mediana (último)", "Mín", "Máx"] + list(BOOKS) + ["Mejor precio en", "Clave apifootball",
                                                                                                                             "P mercado sin margen % (mediana de casas)", "Casas con el par completo", "P Pinnacle sin margen %", "P modelo % (catálogo)", "Modelo − mercado (pp)", "Alerta > 10 pp"]
HDR_MOV = ["Hora Caracas", "Partido", "Mercado", "Línea", "Selección", "Casas con apertura", "Apertura (mediana)", "Último (mediana)", "Cambio %", "Dirección", "1/apertura %", "1/último %", "Cambio de prob. implícita (pp)"]
HDR_ADIC = ["Hora Caracas", "Partido", "Mercado", "Línea", "Selección", "Cuota (mediana último)", "N.º de casas", "P modelo % / distribución", "Cuota mínima justa", "Brecha vs 1/cuota (pp)", "EV teórico %", "Por qué está aquí", "Clave"]


# ── liquidación de los mercados adicionales (para los comparativos) ──
WIN, LOSE, VOID, NODATA = "GANADA", "PERDIDA", "ANULADA", "SIN DATO"


def settle_additional(key, r):
    """(resultado, dato) de una selección adicional con los hechos de un partido FINALIZADO (r: h, a, h1, a1, primer_gol). Sin dato → (SIN DATO, motivo); nunca se inventa."""
    market, *p = key.split("|")
    h, a, h1, a1 = r.get("h"), r.get("a"), r.get("h1"), r.get("a1")
    if h is None or a is None:
        return NODATA, "sin marcador final"
    sel = lambda c: WIN if c else LOSE
    if market == "correct_score":
        i, j = (int(x) for x in p[0].split("-"))
        return sel((h, a) == (i, j)), f"{h}–{a}"
    if market == "asian_handicap":
        import seguimiento as sg
        out = {"win": WIN, "lose": LOSE, "void": VOID, "half_win": WIN + " (½)", "half_loss": LOSE + " (½)"}[sg.settle_handicap_quarter(h, a, p[0], float(p[1]))]
        return out, f"{h}–{a}"
    if market == "total_goals_btts":
        line = float(p[0])
        w, y = p[1].split("_")[0], p[1].split("_")[-1]
        tot = h + a
        if tot == line:
            return VOID, f"{h}–{a}"
        return sel(((tot > line) == (w == "over")) and ((h > 0 and a > 0) == (y == "yes"))), f"{h}–{a}"
    if market in ("second_half_result", "half_time_double_chance", "btts_first_half", "btts_second_half"):
        if h1 is None or a1 is None:
            return NODATA, "sin marcador al descanso"
        h2, a2 = h - h1, a - a1
        if h2 < 0 or a2 < 0:
            return NODATA, "descanso inconsistente con el marcador final"
        if market == "second_half_result":
            return sel({"home": h2 > a2, "draw": h2 == a2, "away": h2 < a2}[p[0]]), f"2.ª parte {h2}–{a2}"
        if market == "half_time_double_chance":
            return sel({"home_draw": h1 >= a1, "home_away": h1 != a1, "draw_away": h1 <= a1}[p[0]]), f"descanso {h1}–{a1}"
        both = (h1 > 0 and a1 > 0) if market == "btts_first_half" else (h2 > 0 and a2 > 0)
        return sel(both == (p[0] == "yes")), f"{h1}–{a1} / {h2}–{a2}"
    if market == "first_team_to_score":
        pg = r.get("primer_gol")
        if h + a == 0:
            return sel(p[0] in ("none", "no_goal", "no_goals")), "0–0"
        if pg is None:
            return NODATA, "la fuente no trae quién anotó primero"
        return sel(p[0] == pg), f"primer gol: {pg}"
    return NODATA, "mercado sin regla de liquidación"
