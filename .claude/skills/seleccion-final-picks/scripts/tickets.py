#!/usr/bin/env python3
"""Armador de tickets PROVISIONALES con dos perfiles (por defecto ×1.20–1.28 «seguridad» y ×4.0–4.8 «amplio»).

Uso:  tickets.py --run runs/2026-10-13 [--target NOMBRE:LO:HI:MAX_PATAS:SOPORTE_MIN ...] [--top 5]
Lee inventory.json + matrix.json. Solo usa partidos con HISTORIAL PROPIO (apifootball) o de la misma liga (Football-Data), nunca proxy
de otra competición. Para cada partido evalúa TODOS los mercados con dato: resultado (1X2, doble oportunidad), hándicap asiático de media
línea, más/menos goles (0.5–5.5), ambos anotan, córners y tarjetas. Un «ítem» es una pata o DOS patas del mismo partido (como «1X + menos de
5.5 goles»); el apoyo de las dos patas juntas se mide sobre los MISMOS partidos pasados (frecuencia conjunta), no multiplicando.
Cuota = PROMEDIO de ≥3 casas (agregador): no ejecutable; la casa recalcula las combinadas del mismo partido (su cuota real suele ser menor).
Córners/tarjetas no tienen cuota media en ninguna fuente usada: se listan aparte con la «cuota mínima de equilibrio» para que la persona
usuaria compare con su casa.

NO es valor esperado ni probabilidad predictiva: apoyo = frecuencia descriptiva conservadora (límite inferior de Wilson). El producto de
apoyos entre partidos supone independencia. Contrastar con la cuota real y con el Nivel 2 (bajas, alineaciones, 2.ª fuente de calendario).
"""
import argparse
import json
import glob
import re
import importlib.util
import itertools
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common
import rotation_risk  # noqa: E402

_CALC = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "evaluacion-probabilidad-valor", "scripts", "calc.py"))
_spec = importlib.util.spec_from_file_location("calc", _CALC)
calc = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(calc)

# nombre, lo, hi, máx. patas (cada pata cuenta), apoyo conservador mínimo por ítem
# Con n=10 el límite inferior de Wilson de un 10/10 es 0.722 y el de 9/10 es 0.66: por eso el mínimo de «seguridad» es 0.65 (≈ ≥9/10 en cada equipo)
# (nombre, lo, hi, máx patas, apoyo mín por ítem, colchón sobre `lo`): el multiplicador CONSERVADOR (pares −5 %) debe quedar ≥ lo·(1+colchón)
DEFAULT_TARGETS = [("seguridad", 1.20, 1.28, 2, 0.65, 0.01), ("amplio", 4.0, 4.8, 6, 0.55, 0.04)]
# Variante «solo Champions» (--champions): el historial de la Champions es mixto (liga+copa+pretemporada, rivales de otro nivel) y no alcanza los pisos normales;
# se relaja el apoyo mínimo (0.45) y el piso por equipo (0.35) y se rotula como VARIANTE de menor respaldo. Se mantienen vetos, ≥4 casas, sin «12», 2 fuentes de calendario.
CHAMPIONS_TARGETS = [("seguridad_champions", 1.20, 1.28, 2, 0.45, 0.01), ("amplio_champions", 4.0, 4.8, 6, 0.45, 0.04)]
CHAMPIONS_TEAM_FLOOR = 0.35
OK_KINDS = ("apifootball_misma_competicion", "apifootball_historial_propio", "football-data_misma_liga")
MIN_N, MIN_BOOKS = 6, 3
TEAM_FLOOR = 0.55        # revisión del auditor: el apoyo es el promedio de dos equipos y un 10/10 tapa al flojo; en tickets CADA equipo debe alcanzar este piso (8/10 → 0.49 no pasa)
PROFILE_DIVERSITY = {"amplio": (0.6, 3)}      # (solape máx. de partidos entre borradores, veces máx. que se repite una pata): el amplio tiene pocas combinaciones y se piden varios
TEAM_FLOOR_BY_PROFILE = {"amplio": 0.45}    # el perfil amplio acepta 8/10 por equipo (Wilson 0.49): relajado y rotulado; seguridad usa TEAM_FLOOR
EXCLUDE_TICKET_SELECTIONS = ("Gana alguno, sin empate",)    # auditor ronda 2: las patas «12» salen con ~8 % de empates frente a 22–30 % de mercado (¿empate registrado como victoria en copas?): fuera de tickets hasta verificar marcadores a 90'
MAX_LEG_REUSE = 2       # una misma pata (partido+selección) aparece como máximo en 2 borradores de un perfil (evita que un solo fallo hunda todos)
MAX_SAME_DIRECTION = 2    # auditoría 13-oct: máx. 2 patas under (o over) por ticket: los unders del mismo día comparten el régimen de goles
SAFE_P_MIN = 0.85         # un ticket solo se rotula «seguridad» si P(mercado, sin margen) ≥ 85 % y EV ≥ 0; si no, «bajo riesgo (EV<0)» con su P(pérdida)
SHRINK_M = 40             # peso del mercado en el encogimiento p = (N·f + m·p_mercado)/(N + m): con n≈10–20 casi todo el peso es del mercado
MAX_GAP = 0.15            # brecha muestra−mercado ≥ 15 pp = DESCARTE (artefacto de escoger el máximo entre muchas patas), no «salvedad»
# Niveles de entrega (la persona usuaria decide; el sistema informa los riesgos): si el nivel estándar no da ≥ MIN_DRAFTS borradores para un multiplicador, se completan con
# niveles de RIESGO EXPLÍCITO y cada borrador sale rotulado con su nivel, su P(pérdida) y la brecha de cada pata. Los vetos y los defectos de veracidad NO se relajan nunca.
TIERS = ({"n": 1, "nombre": "estándar", "gap": 0.15, "max_dir": 2, "extra_legs": 0, "soporte": 0.0},
         {"n": 2, "nombre": "riesgo explícito", "gap": 0.30, "max_dir": 3, "extra_legs": 1, "soporte": -0.10},
         {"n": 3, "nombre": "riesgo alto", "gap": 9.99, "max_dir": 4, "extra_legs": 2, "soporte": -0.15})
MIN_DRAFTS = 3
TIER_BUDGET = 300000    # nodos máx. por búsqueda de nivel de riesgo
TICKET_MIN_BOOKS = 4    # revisión por lotes: cuotas medias de 2–3 casas son frágiles (precios repetidos/extremos); las patas de TICKET exigen ≥4 casas (rankings: ≥3)
ODDS_MIN, ODDS_MAX = 1.03, 2.6
PAIR_TOP_PER_MATCH = 10
EST_MARGIN = 0.08     # SUPUESTO: margen típico de una casa en mercados secundarios; la cuota estimada NO es de ninguna casa
EXCLUDE_TICKET_CATEGORIES = ('youth', 'u23', 'reserve')    # plantillas juveniles/sub-23/reservas rotan y su historial es poco fiable: fuera de los tickets por defecto
# Reglas por PAR del mismo partido (reevaluación por agentes): runs/<fecha>/pair_rules.json = {"vetados": [{"partido","selecciones":[a,b],"motivo"}],
# "notas": [{"partido","selecciones":[a,b],"veredicto","condicion"}]}. Un par vetado no se genera; una nota se muestra junto al par en el ticket.
PAIR_RULES = {"vetados": {}, "notas": {}}


def _pair_key(partido, selecciones):
    return (common.norm_name(partido), frozenset(common.norm_name(x) for x in selecciones))


def load_pair_rules(run):
    path = os.path.join(run, "pair_rules.json")
    d = common.read_json(path, {}) if os.path.exists(path) else {}
    PAIR_RULES["vetados"] = {_pair_key(v["partido"], v["selecciones"]): v for v in d.get("vetados", [])}
    PAIR_RULES["notas"] = {_pair_key(v["partido"], v["selecciones"]): v for v in d.get("notas", [])}


PAIR_HAIRCUT = 0.95   # la casa suele pagar menos por combinar dos mercados del mismo partido: se descuenta un 5 % para decidir si el ticket sigue en rango
MAX_ESTIMATED_LEGS = 2  # como máximo dos patas con cuota ESTIMADA (córners/tarjetas/remates) por ticket; todo ticket con alguna se marca «cuota por confirmar»
MAX_OVERLAP = 0.34    # borradores de un mismo perfil: como máximo un tercio de sus partidos puede coincidir con uno ya elegido


def _res(h):
    return None if h["gf"] is None or h["ga"] is None else h["gf"] - h["ga"]


def _tot(h):
    return None if h["gf"] is None or h["ga"] is None else h["gf"] + h["ga"]


def _corners(h):
    return None if None in h["corners"] else h["corners"][0] + h["corners"][1]


def _cards_tuple(h):
    """Puntos de tarjetas (local, visitante) con la regla de la casa: amarilla 1, roja 2 (ver adapters._card_points). Sin `cards_pts` (filas antiguas) se
    deriva de las estadísticas agregadas; un 0-0 de tarjetas se considera DATO FALTANTE, no un 0."""
    t = h.get("cards_pts")
    if t is None:
        y, r = h.get("yellow"), h.get("red")
        if y is None or r is None or None in y or None in r:
            return None
        t = (y[0] + 2 * r[0], y[1] + 2 * r[1])
    if t is None or None in t or (t[0] + t[1]) == 0:
        return None
    return t


def _cards(h):
    t = _cards_tuple(h)
    return None if t is None else t[0] + t[1]


def _stat_tuple(h, key):
    return _cards_tuple(h) if key == "cards_pts" else h.get(key)


def _val(h, key, who):
    """Valor de una estadística de la fila: 'sum' (ambos equipos), 'own' (el equipo de la fila) u 'opp' (lo que concede/le hace el rival)."""
    t = _stat_tuple(h, key)
    if t is None or None in t:
        return None
    if who == "sum":
        return t[0] + t[1]
    i = 0 if h.get("venue") == "local" else 1
    return t[i] if who == "own" else t[1 - i]


def _drange(lo, hi, step=1.0):
    n = int(round((hi - lo) / step)) + 1
    return [round(lo + i * step, 1) for i in range(n)]


# Escalera COMPLETA de líneas por mercado (las casas ofrecen cada número): (clave de fila, mercado, nombre en la etiqueta, líneas del total, líneas por equipo).
# Tarjetas = PUNTOS con la regla de la casa (amarilla 1, roja 2, máx. 3 por jugador). Mismo proceso y mismos filtros que goles/hándicaps.
STAT_MARKETS = [
    ("corners", "córners", "córners", _drange(6.5, 14.5), _drange(2.5, 8.5)),
    ("cards_pts", "tarjetas", "tarjetas (A=1, R=2)", _drange(1.5, 9.5), _drange(0.5, 5.5)),
    ("sot", "remates a puerta", "remates a puerta", _drange(3.5, 14.5), _drange(1.5, 9.5)),
    ("shots", "remates", "remates totales", _drange(14.5, 32.5), _drange(6.5, 18.5)),
]


def _both(h):
    return None if h["gf"] is None else (h["gf"] > 0 and h["ga"] > 0)


def _pred(f, test):
    return lambda h: (lambda v: None if v is None else test(v))(f(h))


def atoms(ev, names=("Local", "Visitante")):
    """[(clave_cuota|None, índice, mercado, etiqueta, pred_local, pred_visit)] — pred_* se aplican a las filas de cada equipo."""
    A = []

    def add(price_key, idx, market, label, ph, pa):
        A.append((price_key, idx, market, label, ph, pa))

    m = lambda t: _pred(_res, t)
    add("resultado.1x2", 0, "resultado", "Local gana (1)", m(lambda v: v > 0), m(lambda v: v < 0))
    add("resultado.1x2", 1, "resultado", "Empate (X)", m(lambda v: v == 0), m(lambda v: v == 0))
    add("resultado.1x2", 2, "resultado", "Visitante gana (2)", m(lambda v: v < 0), m(lambda v: v > 0))
    add("resultado.doble_oportunidad", 0, "doble oportunidad", "Local o empate (1X)", m(lambda v: v >= 0), m(lambda v: v <= 0))
    add("resultado.doble_oportunidad", 1, "doble oportunidad", "Gana alguno, sin empate (12)", m(lambda v: v != 0), m(lambda v: v != 0))
    add("resultado.doble_oportunidad", 2, "doble oportunidad", "Empate o visitante (X2)", m(lambda v: v <= 0), m(lambda v: v >= 0))
    for L in (-2.5, -1.5, -0.5, 0.5, 1.5, 2.5):
        tag = f"{L:+.1f}"
        add(f"resultado.handicap{tag}", 0, "hándicap", f"Hándicap local {tag}", m(lambda v, L=L: v + L > 0), m(lambda v, L=L: v < L))
        add(f"resultado.handicap{tag}", 1, "hándicap", f"Hándicap visitante {-L:+.1f}", m(lambda v, L=L: v + L < 0), m(lambda v, L=L: v > L))
    for line in (0.5, 1.5, 2.5, 3.5, 4.5, 5.5):
        k = "goles.over_" + str(line).replace(".", "_")
        t = _pred(_tot, lambda v, l=line: v > l)
        u = _pred(_tot, lambda v, l=line: v < l)
        add(k, 0, "goles", f"Más de {line} goles", t, t)
        add(k, 1, "goles", f"Menos de {line} goles", u, u)
    bt = _pred(lambda h: None if h["gf"] is None else int(_both(h)), lambda v: v == 1)
    nb = _pred(lambda h: None if h["gf"] is None else int(_both(h)), lambda v: v == 0)
    add("goles.btts", 0, "goles", "Ambos anotan: sí", bt, bt)
    add("goles.btts", 1, "goles", "Ambos anotan: no", nb, nb)
    home, away = names
    for key, market, nm, tot_lines, team_lines in STAT_MARKETS:
        tot = lambda h, key=key: _val(h, key, "sum")
        own = lambda h, key=key: _val(h, key, "own")
        opp = lambda h, key=key: _val(h, key, "opp")
        for line in tot_lines:
            o, u = _pred(tot, lambda v, l=line: v > l), _pred(tot, lambda v, l=line: v < l)
            add(None, 0, market, f"Más de {line} {nm}", o, o)
            add(None, 1, market, f"Menos de {line} {nm}", u, u)
        for line in team_lines:          # por equipo: producción propia del equipo + lo que concede el rival (para cada lado de la muestra)
            for who, (fh_f, fa_f) in ((home, (own, opp)), (away, (opp, own))):
                add(None, 0, market, f"{who}: más de {line} {nm}", _pred(fh_f, lambda v, l=line: v > l), _pred(fa_f, lambda v, l=line: v > l))
                add(None, 1, market, f"{who}: menos de {line} {nm}", _pred(fh_f, lambda v, l=line: v < l), _pred(fa_f, lambda v, l=line: v < l))
    return A


def _support(fh, fa, ph, pa):
    hs = [x for x in (ph(h) for h in fh) if x is not None]
    as_ = [x for x in (pa(h) for h in fa) if x is not None]
    if len(hs) < MIN_N or len(as_) < MIN_N:
        return None
    kh, ka = sum(hs), sum(as_)
    wh, wa = calc.wilson(kh, len(hs))[0], calc.wilson(ka, len(as_))[0]
    lo = (wh + wa) / 2
    return {"apoyo_conservador": round(lo, 3), "apoyo_min_equipo": round(min(wh, wa), 3), "frec": [round(kh / len(hs), 3), round(ka / len(as_), 3)], "n": [len(hs), len(as_)]}


def _novig(c):
    inv = [1 / x for x in c]
    t = sum(inv)
    return [x / t for x in inv]


def _price(ev, key, idx):
    ap = ev.get("api_prices") or {}
    p = ap.get(key)
    if not p or p.get("n_casas", 0) < MIN_BOOKS:
        mk = (ev.get("markets") or {}).get(key, {}).get("price")        # compat: cuota ya guardada en el mercado
        p = {"cuotas_medias": mk["cuotas"], "n_casas": mk.get("n_casas", 0), "minmax": mk.get("minmax", [[None, None]] * len(mk["cuotas"]))} if mk and mk.get("tipo") == "promedio_de_mercado" else None
    if not p or p.get("n_casas", 0) < MIN_BOOKS:
        return None
    cs = p.get("cuotas_medianas") or p["cuotas_medias"]          # MEDIANA entre casas (una casa atípica no infla el multiplicador)
    odd = cs[idx]
    if key == "resultado.doble_oportunidad":                      # las 3 cuotas NO son excluyentes: la prob. implícita sale del 1X2 sin margen
        x = ap.get("resultado.1x2")
        if x and x.get("n_casas", 0) >= MIN_BOOKS:
            p1, px, p2 = _novig(x.get("cuotas_medianas") or x["cuotas_medias"])
            imp = [p1 + px, p1 + p2, px + p2][idx]
        else:
            imp = None
    else:
        imp = round(_novig(cs)[idx], 4)
    return {"cuota_media": odd, "minmax_casas": p["minmax"][idx], "n_casas": p["n_casas"], "n_precios_distintos": p.get("n_precios_distintos"),
            "prob_implicita_sin_margen": None if imp is None else round(imp, 4)}


STALE_DAYS = 100     # muestra representativa: cada equipo debe tener ≥MIN_N partidos de los últimos 100 días (auditor: FUS Rabat tenía 15 de 20 filas de jun–jul)


def _n_recent(rows, kickoff_iso):
    import datetime as dt
    k = dt.datetime.fromisoformat(kickoff_iso.replace("Z", "+00:00")).date()
    n = 0
    for h in rows:
        try:
            if (k - dt.date.fromisoformat(h["date"][:10])).days <= STALE_DAYS:
                n += 1
        except (KeyError, ValueError, TypeError):
            pass
    return n


def legs_for_match(m, ev, _unused=None):
    """Patas (con cuota media o sin ella) + predicados para medir apoyo conjunto. Nunca desde proxy ni sin muestra n>=6."""
    if ev.get("history_kind") not in OK_KINDS:
        return []
    fh, fa = ev["form"].get("local", []), ev["form"].get("visitante", [])
    out = []
    for key, idx, market, label, ph, pa in atoms(ev, (m["home_team"], m["away_team"])):
        sup = _support(fh, fa, ph, pa)
        if not sup:
            continue
        leg = {"match_id": m["match_id"], "partido": f"{m['home_team']} – {m['away_team']}", "competicion": m["competition"],
               "inicio_utc": m["normalized_datetime_utc"], "categoria": m.get("gender_or_category", "men"), "calendario_2_fuentes": m.get("selection_calendar_verification") == "SUFICIENTE", "mercado": market, "seleccion": label, "history_kind": ev["history_kind"],
               "cuota_media": None, "minmax_casas": None, "n_casas": 0, "prob_implicita_sin_margen": None,
               "cuota_equilibrio_minima": round(1 / max(sup["apoyo_conservador"], 1e-9), 2), **sup, "_ph": ph, "_pa": pa, "_fh": fh, "_fa": fa}
        leg["n_recientes"] = [_n_recent(fh, m["normalized_datetime_utc"]), _n_recent(fa, m["normalized_datetime_utc"])]
        leg["cuota_tipo"] = None
        if key:
            pr = _price(ev, key, idx)
            if pr and ODDS_MIN <= pr["cuota_media"] <= ODDS_MAX:
                leg.update(pr)
                leg["cuota_tipo"] = "promedio_de_mercado"
                if pr["prob_implicita_sin_margen"] is not None:
                    leg["indicador_descriptivo"] = round(sup["apoyo_conservador"] - pr["prob_implicita_sin_margen"], 3)
        else:        # córners/tarjetas: ninguna fuente usada publica cuota -> APROXIMADA por modelo, siempre rotulada
            p_est = (sum(round(f * n) for f, n in zip(sup["frec"], sup["n"])) + 2) / (sum(sup["n"]) + 4)      # frecuencia suavizada de ambos equipos
            est = round(1 / (p_est * (1 + EST_MARGIN)), 2)
            if 1.10 <= est <= ODDS_MAX:          # una casa no paga menos de ~1.10 por una línea de córners/tarjetas
                leg.update(cuota_media=est, cuota_tipo="estimada_por_modelo", n_casas=0, minmax_casas=[est, est], prob_implicita_sin_margen=round(p_est, 4))
        out.append(leg)
    return out


def apply_manual_odds(legs, path):
    """CSV/JSON de la persona usuaria: columnas home,away,seleccion,cuota. Sustituye cualquier cuota (estimada o media) por la real de su casa."""
    import csv
    rows = list(csv.DictReader(open(path, encoding="utf-8-sig"))) if path.endswith(".csv") else __import__("json").load(open(path, encoding="utf-8"))
    idx = {(common.norm_name(r["home"]), common.norm_name(r["away"]), r["seleccion"].strip().lower()): float(r["cuota"]) for r in rows}
    n = 0
    for l in legs:
        h, a = l["partido"].split(" – ")
        k = (common.norm_name(h), common.norm_name(a), l["seleccion"].strip().lower())
        if k in idx:
            l.update(cuota_media=idx[k], cuota_tipo="manual_usuario", n_casas=1, minmax_casas=[idx[k], idx[k]])
            n += 1
    return n


def _team_scope(leg):
    """'home' / 'away' si la pata es de un equipo concreto (gana, o empata, hándicap de ese lado); None si es de ambos equipos (goles, BTTS…)."""
    t = (leg.get("seleccion") or "").lower()
    if t.startswith("local") or "hándicap local" in t:
        return "home"
    if t.startswith("visitante") or "hándicap visitante" in t:
        return "away"
    return None


def apply_rotation(legs, path):
    """rotation.json (de `rotation_prior.py`): vetar unders y rebajar patas de ganador del equipo con riesgo de rotación ALTO/MEDIO (NO bloquea el ticket por falta de once).
    Devuelve (patas, vetadas_por_rotacion, hay_datos). Sin fichero: no cambia nada."""
    if not os.path.exists(path):
        return legs, [], False
    rot = common.read_json(path, {})
    out, removed = [], []
    for l in legs:
        rec = rot.get(l["match_id"])
        if not rec:
            out.append(l)
            continue
        scope = _team_scope(l)
        lv = [rec[sd]["nivel"] for sd in ((scope,) if scope else ("home", "away")) if rec.get(sd)]
        level = max(lv, key=rotation_risk.LEVELS.index) if lv else None
        sel = (l.get("seleccion") or "").lower()
        team_win = scope is not None and ("gana" in sel or "empate" in sel)
        act = rotation_risk.penalty_for_leg(level, _direction(l), team_win) if level else None
        if act == "veto":
            removed.append({"partido": l["partido"], "seleccion": l["seleccion"], "motivo": f"riesgo de rotación ALTO ({'; '.join(rec[scope or 'home']['motivos'])})"})
            continue
        if act == "rebajar":
            l = dict(l, apoyo_conservador=round(max(0.0, l["apoyo_conservador"] - 0.05), 3), rotacion="PROVISIONAL por alineación: riesgo de rotación medio")
        out.append(l)
    return out, removed, True


def _league_teams(run):
    """league_samples/*.json -> {nombre normalizado: dif. de goles media por partido} (dominancia)."""
    import glob
    d = {}
    for f in glob.glob(os.path.join(run, "league_samples", "*.json")):
        for team, blk in (common.read_json(f, {}).get("resumen", {}).get("equipos") or {}).items():
            if blk.get("dif_goles") is not None:
                d[common.norm_name(team)] = blk["dif_goles"]
    return d


def favorites_table(legs, run, rotation_path, min_p=0.65, min_dom=0.5):
    """Mercados de GANADOR del favorito con filtro de dominancia (auditoría 13-oct): P(mercado, sin margen) ≥ min_p, brecha muestra−mercado < MAX_GAP,
    rotación del favorito baja y dominancia (dif. de goles de liga del favorito − la del rival) ≥ min_dom. Sin dato de liga o de rotación: no pasa (se dice)."""
    dom = _league_teams(run)
    rot = common.read_json(rotation_path, {}) if os.path.exists(rotation_path) else {}
    out = []
    for l in legs:
        sel = (l.get("seleccion") or "").lower()
        if l.get("mercado") != "resultado" or not sel.startswith(("local gana", "visitante gana")):
            continue
        pm = l.get("prob_implicita_sin_margen")
        pc, gap = p_central(l)
        if pm is None or pm < min_p or pc is None or gap >= MAX_GAP:
            continue
        side = "home" if sel.startswith("local") else "away"
        h, a = l["partido"].split(" – ")
        fav, opp = (h, a) if side == "home" else (a, h)
        lv = ((rot.get(l["match_id"]) or {}).get(side) or {}).get("nivel")
        d_f, d_o = dom.get(common.norm_name(fav)), dom.get(common.norm_name(opp))
        why = []
        if lv != "bajo":
            why.append("rotación sin verificar" if lv is None else f"rotación {lv}")
        if d_f is None or d_o is None:
            why.append("dominancia sin dato de liga")
        elif d_f - d_o < min_dom:
            why.append(f"dominancia insuficiente ({round(d_f - d_o, 2)})")
        if not why:
            out.append({k: v for k, v in l.items() if not k.startswith("_")} | {"p_central": pc, "brecha": gap, "dominancia": round(d_f - d_o, 2), "rotacion": lv,
                                                                                "ev_central": round(pc * l["cuota_media"] - 1, 3) if l.get("cuota_media") else None})
    out.sort(key=lambda x: -(x["p_central"]))
    return out


def drop_big_gap(legs, max_gap=None):
    """Quita de los TICKETS las patas con precio de mercado cuya frecuencia de muestra supera a la probabilidad de mercado en ≥ max_gap (maldición del ganador con n pequeño).
    Las patas sin precio de mercado (córners/tarjetas estimadas) no tienen brecha medible y se conservan. Devuelve (patas, n_descartadas)."""
    max_gap = MAX_GAP if max_gap is None else max_gap
    keep, n = [], 0
    for l in legs:
        _, gap = p_central(l)
        if gap is not None and gap >= max_gap:
            n += 1
            continue
        keep.append(l)
    return keep, n


def _direction(leg):
    """'under' / 'over' según el texto de la selección («Menos de …» / «Más de …»); None para ganador, hándicap, BTTS, doble oportunidad."""
    t = (leg.get("seleccion") or "").lower()
    if " menos de " in " " + t or t.startswith("menos de"):
        return "under"
    if " más de " in " " + t or t.startswith("más de"):
        return "over"
    return None


def _direction_counts(items):
    c = {"under": 0, "over": 0}
    for it in items:
        for l in it["patas"]:
            d = _direction(l)
            if d:
                c[d] += 1
    return c


def p_central(leg, m=SHRINK_M):
    """Probabilidad central de una pata: encogimiento de la frecuencia de ambos equipos hacia la probabilidad de mercado sin margen. Devuelve
    (p_central, brecha) con brecha = frecuencia agrupada − mercado, o (None, None) si falta precio de mercado o muestra."""
    pm, fr, ns = leg.get("prob_implicita_sin_margen"), leg.get("frec"), leg.get("n")
    if pm is None or not fr or not ns or sum(ns) == 0:
        return None, None
    N = sum(ns)
    f = sum(a * b for a, b in zip(fr, ns)) / N
    return round((N * f + m * pm) / (N + m), 4), round(f - pm, 3)


def risk_label(p_mercado, ev_mercado):
    """Rótulo honesto del ticket por su probabilidad de pérdida (auditoría 13-oct: un ×1.25 con 20 % de fallo no es «seguridad», y un ×3 con 75 % de fallo
    no es «bajo riesgo»). SEGURIDAD solo con P(mercado, sin margen) ≥ 85 % y EV ≥ 0."""
    if p_mercado is None or ev_mercado is None:
        return "SIN PROBABILIDAD DE MERCADO (no evaluable)"
    if p_mercado >= SAFE_P_MIN and ev_mercado >= 0:
        return "SEGURIDAD"
    tier = "RIESGO MEDIO" if p_mercado >= 0.70 else ("RIESGO ALTO" if p_mercado >= 0.50 else "RIESGO MUY ALTO")
    return f"{tier} (EV<0)" if ev_mercado < 0 else tier


def apply_vetoes(legs, path):
    """vetoes.json = [{"partido": "Local – Visitante" (o "match_id"), "seleccion": "texto exacto", "motivo": "…"}]: decisiones del director a partir de
    la revisión de los agentes. Una pata vetada no entra en tickets ni en rankings; el veto se registra en tickets.json."""
    vs = common.read_json(path, []) if os.path.exists(path) else []
    out, removed = [], []
    for l in legs:
        hit = next((v for v in vs if (v.get("match_id") == l["match_id"] or common.norm_name(v.get("partido", "")) == common.norm_name(l["partido"]))
                    and (not v.get("seleccion") or v["seleccion"].strip().lower() == l["seleccion"].strip().lower())), None)
        if hit:
            removed.append({"partido": l["partido"], "seleccion": l["seleccion"], "motivo": hit.get("motivo")})
        else:
            out.append(l)
    return out, removed


# Puerta de calidad de DATOS (veracidad): avisos GRAVES de los agentes de lote sobre una cifra defectuosa bloquean de forma automática el mercado afectado
# (o todo el partido si el aviso no nombra mercado). «Inflado por rivales débiles» o «el mercado discrepa» NO son defectos de veracidad: son señales de
# representatividad y se tratan con la separación por tipo de historial.
HARD_FLAW = re.compile(r"disparidad extrema|defectuos|sospechos|incoheren|denominador|duplicad|imposible|no cuadra|no es plausible|no plausible|descart|an[óo]mal", re.I)
SAME_COMPETITION_KINDS = ("apifootball_misma_competicion", "football-data_misma_liga")


def _flaw_families(text):
    t = text.lower()
    fams = set()
    if "tarjeta" in t:
        fams.add("tarjetas")
    if "corner" in t or "córner" in t:
        fams.add("córners")
    if re.search(r"btts|ambos", t):
        fams.add("ambos_anotan")
    if re.search(r"1x2|doble oportunidad|h[áa]ndicap|favorito|victoria|\bdc\b", t):
        fams.add("resultado")
    if re.search(r"\bgoles|\bgf\b|\bga\b|\bover|\bunder|o\d\.\d|u\d\.\d", t):
        fams.add("goles_total")
    return fams or {"ALL"}


def apply_quality_gate(legs, run):
    """Quita las patas cuyo mercado tiene un aviso grave de veracidad en la revisión por lotes. Devuelve (patas, bloqueos)."""
    block = {}
    for f in sorted(glob.glob(os.path.join(run, "reviews_raw", "batch", "*.json"))):
        d = common.read_json(f, [])
        for r in (d if isinstance(d, list) else [d]):
            for row in r.get("rows", []):
                for c in row.get("corrections", []) or []:
                    if HARD_FLAW.search(c):
                        for fam in _flaw_families(c):
                            block.setdefault(row["match_id"], {}).setdefault(fam, []).append(f"{str(r.get('agent', ''))[9:12]}: {c[:140]}")
    out, gated, seen = [], [], set()
    for l in legs:
        b = block.get(l["match_id"])
        fam = _family(l)
        hit = (b.get("ALL") or b.get(fam)) if b else None
        if hit:
            if (l["match_id"], fam) not in seen:
                seen.add((l["match_id"], fam))
                gated.append({"partido": l["partido"], "familia": "todo el partido" if b.get("ALL") else fam, "aviso": hit[0]})
        else:
            out.append(l)
    return out, gated


def filter_legs_time_and_matches(legs, after, excludes):
    """Quita partidos que ya empezaron (--after-utc) y los excluidos a mano (--exclude-match). Devuelve (patas, info) para registrarlo en tickets.json."""
    import datetime as dt
    info = {"despues_de_utc": None, "partidos_descartados_por_hora": 0, "partidos_excluidos_manualmente": list(excludes or [])}
    out = legs
    if after:
        cutoff = dt.datetime.now(dt.timezone.utc) + dt.timedelta(minutes=15) if after == "now" else dt.datetime.fromisoformat(after.replace("Z", "+00:00"))
        info["despues_de_utc"] = cutoff.strftime("%Y-%m-%dT%H:%M:%SZ")
        keep = [l for l in out if dt.datetime.fromisoformat(l["inicio_utc"].replace("Z", "+00:00")) >= cutoff]
        info["partidos_descartados_por_hora"] = len({l["match_id"] for l in out}) - len({l["match_id"] for l in keep})
        out = keep
    if excludes:
        ex = {common.norm_name(x) for x in excludes}
        out = [l for l in out if common.norm_name(l["partido"]) not in ex]
    return out, info


def _replacements(results_tickets, singles, lo, hi, taken_matches):
    """Por cada pata SUELTA de cada borrador: las 2 mejores alternativas de cuota parecida (±15 %) de OTRO partido libre, con el multiplicador resultante y si
    sigue en rango. Para no improvisar cuando se quita una pata (lección del ticket perdido). No deja un ticket sin pata de precio real ni pasa de MAX_ESTIMATED_LEGS."""
    out = []
    for n, tk in enumerate(results_tickets, 1):
        mids = {it["match_id"] for it in tk["items"]}
        n_est = sum(1 for it in tk["items"] for l in it["patas"] if l.get("cuota_tipo") == "estimada_por_modelo")
        n_real = sum(1 for it in tk["items"] for l in it["patas"] if l.get("cuota_tipo") != "estimada_por_modelo")
        for it in tk["items"]:
            if it["mismo_partido"]:
                continue
            l = it["patas"][0]
            was_est = l.get("cuota_tipo") == "estimada_por_modelo"
            base = tk["cuota_combinada_conservadora"] / it["cuota"]
            alts = []
            for c in sorted(singles, key=lambda c: (-c["apoyo"], -c["cuota"])):
                lc = c["patas"][0]
                if c["match_id"] in mids or c["match_id"] in taken_matches or not (0.85 * it["cuota"] <= c["cuota"] <= 1.15 * it["cuota"]):
                    continue
                c_est = lc.get("cuota_tipo") == "estimada_por_modelo"
                if n_est - was_est + c_est > MAX_ESTIMATED_LEGS or (n_real - (not was_est) + (not c_est)) < 1:
                    continue
                new = round(base * c["cuota"], 3)
                alts.append({"partido": lc["partido"], "seleccion": lc["seleccion"], "cuota": c["cuota"], "apoyo": c["apoyo"], "estimada": c_est,
                             "nuevo_multiplicador": new, "en_rango": lo <= new <= hi})
                if len(alts) >= 2:
                    break
            out.append({"borrador": n, "pata": f"{l['partido']} → {l['seleccion']}", "cuota": it["cuota"], "alternativas": alts})
    return out


def collect_legs(run):
    inv = common.read_json(os.path.join(run, "inventory.json"))
    mx = common.read_json(os.path.join(run, "matrix.json"), {"matches": {}})["matches"]
    legs = []
    for m in inv["matches"]:
        if m.get("analysis_required") and m["match_id"] in mx:
            legs += legs_for_match(m, mx[m["match_id"]])
    return legs


def _family(leg):
    """Familia de mercado para decidir qué patas pueden combinarse en el mismo partido (solo familias DISTINTAS)."""
    if leg["mercado"] in ("resultado", "doble oportunidad", "hándicap"):
        return "resultado"
    if leg["mercado"] == "goles":
        return "ambos_anotan" if leg["seleccion"].startswith("Ambos") else "goles_total"
    return leg["mercado"]


def _items(legs, min_support, with_pairs=True, require_calendar=False, exclude_categories=(), team_floor=TEAM_FLOOR, min_recent=MIN_N):
    """Ítems = pata suelta o par de patas del mismo partido (apoyo CONJUNTO sobre los mismos partidos pasados)."""
    by = {}
    for l in legs:
        if l["cuota_media"] is not None and (l.get("calendario_2_fuentes") or not require_calendar) and l.get("categoria", "men") not in exclude_categories \
                and not (require_calendar and l["seleccion"].startswith(EXCLUDE_TICKET_SELECTIONS)) \
                and (not require_calendar or l.get("cuota_tipo") in ("estimada_por_modelo", "manual_usuario") or l.get("n_casas", 0) >= TICKET_MIN_BOOKS):
            by.setdefault(l["match_id"], []).append(l)
    items = []
    for mid, ls in by.items():
        ls.sort(key=lambda l: -l["apoyo_conservador"])
        for l in ls:
            if l["apoyo_conservador"] >= min_support and (not require_calendar or (l.get("apoyo_min_equipo", 1) >= team_floor and min(l.get("n_recientes", [MIN_N, MIN_N])) >= min_recent)):
                items.append({"match_id": mid, "patas": [l], "cuota": l["cuota_media"], "cuota_cons": l["cuota_media"], "apoyo": l["apoyo_conservador"], "mismo_partido": False})
        if with_pairs:
            for a, b in itertools.combinations(ls[:PAIR_TOP_PER_MATCH], 2):
                if "estimada_por_modelo" in (a.get("cuota_tipo"), b.get("cuota_tipo")):   # un par solo se justifica con cuotas reales: la cuota de un par con pata estimada sería inventada
                    continue
                if _family(a) == _family(b):          # misma familia (p. ej. «más de 1.5» + «más de 2.5», o 1X + hándicap): una pata implica o contradice a la otra
                    continue
                pk = _pair_key(a["partido"], [a["seleccion"], b["seleccion"]])
                if pk in PAIR_RULES["vetados"]:
                    continue
                ph = lambda h, a=a, b=b: (lambda x, y: None if x is None or y is None else (x and y))(a["_ph"](h), b["_ph"](h))
                pa = lambda h, a=a, b=b: (lambda x, y: None if x is None or y is None else (x and y))(a["_pa"](h), b["_pa"](h))
                sup = _support(a["_fh"], a["_fa"], ph, pa)
                # «bien justificado»: el apoyo CONJUNTO medido sobre los mismos partidos pasados supera el mínimo del perfil y no es
                # peor que el de las dos patas tratadas como independientes (tolerancia 0.02): la segunda pata no debilita a la primera
                indep = a["apoyo_conservador"] * b["apoyo_conservador"]
                if sup and sup["apoyo_conservador"] >= min_support and sup["apoyo_conservador"] >= indep - 0.02 and (not require_calendar or sup["apoyo_min_equipo"] >= team_floor):
                    just = (f"Conjunto medido en los mismos partidos pasados: local {sup['frec'][0]} (n={sup['n'][0]}), visitante {sup['frec'][1]} (n={sup['n'][1]}); "
                            f"apoyo conservador conjunto {sup['apoyo_conservador']} (límite inferior de Wilson; techo 0.722 con n=10), frente a {round(indep, 3)} como producto de los apoyos "
                            f"individuales ({a['apoyo_conservador']} × {b['apoyo_conservador']}). Referencia descriptiva: no prueba dependencia ni es una probabilidad.")
                    nota = PAIR_RULES["notas"].get(pk)
                    if nota:
                        just += f" Reevaluación de agentes: {nota.get('veredicto')}. Condición: {nota.get('condicion')}"
                    items.append({"match_id": mid, "patas": [a, b], "cuota": round(a["cuota_media"] * b["cuota_media"], 3),
                                  "cuota_cons": round(a["cuota_media"] * b["cuota_media"] * PAIR_HAIRCUT, 3),
                                  "apoyo": sup["apoyo_conservador"], "mismo_partido": True, "apoyo_conjunto": sup, "justificacion": just})
    return items


def _hi_odds(it):
    """Cuota con la que se comprueba el TECHO del rango. Un par del mismo partido paga menos que el producto de sus cuotas (la casa recalcula):
    para el techo se usa la cuota conservadora (−5 %), igual que para el suelo; las patas sueltas usan su cuota media."""
    return it["cuota_cons"] if it["mismo_partido"] else it["cuota"]


def search(legs, lo, hi, max_legs, min_support, top=5, pool=60, exclude=frozenset(), require_calendar=True, exclude_categories=EXCLUDE_TICKET_CATEGORIES, buffer=0.0, team_floor=TEAM_FLOOR, max_overlap=None, max_reuse=None, items_override=None, require=None, with_pairs=True, min_recent=MIN_N, max_estimated=None, max_dir=None, budget=None):
    max_dir = MAX_SAME_DIRECTION if max_dir is None else max_dir
    max_est = MAX_ESTIMATED_LEGS if max_estimated is None else max_estimated
    max_overlap = MAX_OVERLAP if max_overlap is None else max_overlap
    max_reuse = MAX_LEG_REUSE if max_reuse is None else max_reuse
    base = items_override if items_override is not None else _items(legs, min_support, with_pairs=with_pairs, require_calendar=require_calendar, exclude_categories=exclude_categories, team_floor=team_floor, min_recent=min_recent)
    items = [i for i in base if i["match_id"] not in exclude]
    items.sort(key=lambda i: (-i["apoyo"], -i["cuota"]))      # a igual apoyo (= igual riesgo), la cuota más alta
    best_per_match, cand = {}, []
    for it in items:                                        # hasta 6 ítems por partido para no perder la variedad de mercados
        if _hi_odds(it) > hi:                               # un ítem cuya cuota ya supera el rango nunca puede formar parte del ticket
            continue
        if it["cuota"] ** (1 / len(it["patas"])) < 0.9 * lo ** (1 / max_legs):
            continue                                        # con max_legs patas no se llega a `lo` si cada pata paga menos de ~la media necesaria
        slot = (it["match_id"], any(l.get("cuota_tipo") == "estimada_por_modelo" for l in it["patas"]))       # tope por partido Y por tipo de precio: las patas estimadas no desplazan a las de cuota real
        if best_per_match.get(slot, 0) < 6:
            best_per_match[slot] = best_per_match.get(slot, 0) + 1
            cand.append(it)
    cand = cand[:pool]
    res = []

    lo_cons = lo * (1 + buffer)

    nodes = [0]

    def rec(start, chosen, prod, prod_cons, nlegs, nest):
        nodes[0] += 1
        if budget is not None and nodes[0] > budget:       # tope de nodos: la búsqueda de niveles de riesgo (más patas) crece exponencialmente
            return
        if prod_cons >= lo_cons and prod <= hi and chosen and any(l.get("cuota_tipo") != "estimada_por_modelo" for c_ in chosen for l in c_["patas"]) and (require is None or require(chosen)):   # un ticket sin NINGUNA cuota real no se propone
            res.append((calc.joint_prob([c["apoyo"] for c in chosen]), -nlegs, prod, tuple(chosen)))
        for i in range(start, len(cand)):
            it = cand[i]
            if it["match_id"] in {c["match_id"] for c in chosen}:
                continue
            n = nlegs + len(it["patas"])
            dc = _direction_counts(chosen + [it])
            if dc["under"] > max_dir or dc["over"] > max_dir:
                continue
            e = nest + sum(1 for l in it["patas"] if l.get("cuota_tipo") == "estimada_por_modelo")
            p = prod * _hi_odds(it)
            if n <= max_legs and p <= hi and e <= max_est:
                rec(i + 1, chosen + [it], p, prod_cons * it["cuota_cons"], n, e)
    rec(0, [], 1.0, 1.0, 0, 0)
    res.sort(key=lambda t: (-t[0], -t[1]))
    picked, taken, reuse = [], [], {}
    for r in res:                                       # borradores DISTINTOS: no repetir casi los mismos partidos
        ms = {x["match_id"] for x in r[3]}
        keys = {(l["match_id"], l["seleccion"]) for x in r[3] for l in x["patas"]}
        if all(len(ms & t) / min(len(ms), len(t)) <= max_overlap for t in taken) and all(reuse.get(k, 0) < max_reuse for k in keys):
            picked.append(r)
            taken.append(ms)
            for k in keys:
                reuse[k] = reuse.get(k, 0) + 1
        if len(picked) >= top:
            break
    out = []
    for s, nl, p, c in picked:
        _pm = (None if any(l["prob_implicita_sin_margen"] is None for x in c for l in x["patas"]) else
               calc.joint_prob([calc.joint_prob([l["prob_implicita_sin_margen"] for l in x["patas"]]) for x in c]))
        _cm = calc.combo_odds([x["cuota"] for x in c])
        _ev = None if _pm is None else round(_pm * _cm - 1, 3)
        _pcs = [p_central(l)[0] for x in c for l in x["patas"]]
        _pc = None if any(v is None for v in _pcs) else round(calc.joint_prob(_pcs), 3)
        _brechas = [p_central(l)[1] for x in c for l in x["patas"] if p_central(l)[1] is not None]
        out.append({"p_central_conjunta": _pc, "ev_central": None if _pc is None else round(_pc * _cm - 1, 3), "max_brecha_muestra_mercado": max(_brechas) if _brechas else None,
                    "p_mercado_conjunta": None if _pm is None else round(_pm, 3), "p_perdida_mercado": None if _pm is None else round(1 - _pm, 3), "ev_mercado": _ev,
                    "etiqueta_riesgo": risk_label(_pm, _ev), "direcciones": _direction_counts(c),
                    "cuota_combinada_media": round(calc.combo_odds([x["cuota"] for x in c]), 3),
                    "cuota_combinada_conservadora": round(calc.combo_odds([x["cuota_cons"] for x in c]), 3), "n_patas": -nl, "n_partidos": len(c),
                    "usa_cuota_estimada": any(l.get("cuota_tipo") == "estimada_por_modelo" for x in c for l in x["patas"]),
                    "usa_cuota_manual": any(l.get("cuota_tipo") == "manual_usuario" for x in c for l in x["patas"]),
                    "apoyo_conjunto_descriptivo": round(s, 3),
                    "prob_implicita_conjunta_sin_margen": (None if any(l["prob_implicita_sin_margen"] is None for x in c for l in x["patas"]) else
                                                          round(calc.joint_prob([calc.joint_prob([l["prob_implicita_sin_margen"] for l in x["patas"]]) for x in c]), 3)),
                    "items": [{"match_id": x["match_id"], "mismo_partido": x["mismo_partido"], "cuota": x["cuota"], "apoyo": x["apoyo"], "justificacion": x.get("justificacion"),
                               "patas": [{k: v for k, v in l.items() if not k.startswith("_")} for l in x["patas"]]} for x in c]})
    return out, len(cand)


def top_picks(legs, top=15, min_attr_support=0.55):
    """Dos rankings de patas SUELTAS con cuota media (una por partido): SEGURIDAD (mayor apoyo conservador) y ATRACTIVO
    (rentabilidad-cuota: EV descriptivo conservador = apoyo·cuota − 1, con apoyo ≥ min_attr_support). El EV descriptivo usa como
    «probabilidad» el límite inferior de Wilson de frecuencias pasadas: NO es EV real (no hay probabilidad predictiva defendible) y,
    al elegir el mejor entre cientos de patas, tiende a sobrestimar (maldición del ganador). Son un ranking, no tickets: pueden repetir partido con los tickets."""
    priced = [l for l in legs if l["cuota_media"] is not None]
    for l in priced:
        l["p_central"], l["brecha_muestra_mercado"] = p_central(l)
        l["ev_central"] = None if l["p_central"] is None or l.get("cuota_tipo") == "estimada_por_modelo" else round(l["p_central"] * l["cuota_media"] - 1, 3)
        l["sospechosa_por_brecha"] = l["brecha_muestra_mercado"] is not None and l["brecha_muestra_mercado"] >= MAX_GAP
        l["ev_descriptivo_conservador"] = round(l["apoyo_conservador"] * l["cuota_media"] - 1, 3)
        if l.get("cuota_tipo") == "estimada_por_modelo":
            l["ev_descriptivo_conservador"] = None          # circular: la cuota sale de la misma frecuencia; no se interpreta

    def pick(key, flt):
        seen, out = set(), []
        for l in sorted((x for x in priced if flt(x)), key=key):
            if l["match_id"] in seen:
                continue
            seen.add(l["match_id"])
            out.append({k: v for k, v in l.items() if not k.startswith("_")})
            if len(out) >= top:
                break
        return out
    return {"seguridad": pick(lambda l: (-(l["p_central"] if l["p_central"] is not None else l["apoyo_conservador"]), -l["cuota_media"]), lambda l: True),
            "atractivo": pick(lambda l: (-(l["ev_central"] if l["ev_central"] is not None else -9), -l["apoyo_conservador"]),
                              lambda l: l["apoyo_conservador"] >= min_attr_support and l["ev_descriptivo_conservador"] is not None)}


STAT_MARKET_NAMES = ("córners", "tarjetas", "remates a puerta", "remates")


def unpriced(legs, top=60, min_support=0.5, per_match=3):
    """Córners, tarjetas y remates (ninguna fuente permitida publica su cuota): para cada (partido, mercado, alcance, sentido) se elige la línea MÁS AJUSTADA que aún
    cumple el apoyo mínimo (la de mayor cuota estimada) en vez de repetir toda la escalera; se muestra la cuota APROXIMADA por modelo (✎, no de ninguna casa)
    y la cuota REAL mínima a exigir (1/apoyo). Ordenado por apoyo; como máximo `per_match` selecciones por partido."""
    best = {}
    for l in legs:
        if l["mercado"] not in STAT_MARKET_NAMES or l["apoyo_conservador"] < min_support or l.get("cuota_tipo") not in ("estimada_por_modelo", "manual_usuario") or min(l["n"]) < 8 \
                or min(l.get("n_recientes", [MIN_N, MIN_N])) < MIN_N:
            continue                       # sin cuota estimable (≥1.10) la línea es trivial: ninguna casa la paga, no es candidata
        scope = l["seleccion"].split(":")[0] if ":" in l["seleccion"] else "total"
        direction = "mas" if " más de " in (" " + l["seleccion"].lower()) or l["seleccion"].lower().startswith("más") else "menos"
        k = (l["match_id"], l["mercado"], scope, direction)
        key = (l["cuota_media"] or 0, l["apoyo_conservador"])
        if k not in best or key > (best[k]["cuota_media"] or 0, best[k]["apoyo_conservador"]):
            best[k] = l
    xs = sorted(best.values(), key=lambda l: (-l["apoyo_conservador"], -sum(l["n"]), -l.get("apoyo_min_equipo", 0), l["inicio_utc"], l["partido"]))
    seen, out = {}, []
    for l in xs:
        seen[l["match_id"]] = seen.get(l["match_id"], 0) + 1
        if seen[l["match_id"]] <= per_match:
            out.append({k: v for k, v in l.items() if not k.startswith("_")})
        if len(out) >= top:
            break
    return out


def write_stat_candidates_csv(run, legs):
    """candidatos_estadisticos.csv: TODAS las líneas de córners/tarjetas/remates evaluadas (la escalera completa) con su apoyo y la cuota real mínima a exigir;
    manual_odds_plantilla.csv: las candidatas principales con la columna `cuota` vacía para que la persona usuaria pegue la real de su casa (--manual-odds)."""
    import csv
    rows = [l for l in legs if l["mercado"] in STAT_MARKET_NAMES]
    rows.sort(key=lambda l: (l["partido"], l["mercado"], l["seleccion"]))
    with open(os.path.join(run, "candidatos_estadisticos.csv"), "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["partido", "inicio_utc", "competicion", "mercado", "seleccion", "apoyo", "apoyo_min_equipo", "n_local", "n_visitante", "cuota_minima_a_exigir", "cuota_estimada_modelo"])
        for l in rows:
            w.writerow([l["partido"], l["inicio_utc"], l["competicion"], l["mercado"], l["seleccion"], l["apoyo_conservador"], l.get("apoyo_min_equipo"), l["n"][0], l["n"][1],
                        l["cuota_equilibrio_minima"], l["cuota_media"] if l.get("cuota_tipo") == "estimada_por_modelo" else ""])
    return len(rows)


def _ranking_general(result):
    """Ranking de TODOS los borradores entregados, de primero a último, en cada familia de multiplicador (comparar un ×1.25 con un ×4.5 por margen
    favorecería a las cuotas altas). Criterio: mayor apoyo conjunto descriptivo (frecuencia conjunta conservadora de que TODAS las patas se cumplan);
    a igual apoyo, menor distancia al punto de equilibrio 1/cuota. NO es EV real. «champions» = variante con pisos relajados (menos respaldo)."""
    fam = {"×1.2–1.28 (seguridad)": [], "×4.0–4.8 (amplio)": []}
    for t in result["targets"]:
        for i, tk in enumerate(t["tickets"], 1):
            key = "×1.2–1.28 (seguridad)" if t["lo"] < 2 else "×4.0–4.8 (amplio)"
            eq = 1 / tk["cuota_combinada_conservadora"]
            fam[key].append((tk["apoyo_conjunto_descriptivo"], tk["apoyo_conjunto_descriptivo"] - eq, t["name"], i, f"×{tk['cuota_combinada_media']} ({tk['cuota_combinada_conservadora']})", tk["n_patas"], round(eq, 3)))
    for u in result.get("usuario", []):
        if u.get("apoyo_conjunto_gana_entera") is not None and u.get("multiplicador_usuario"):
            eq = 1 / u["multiplicador_usuario"]
            fam["×1.2–1.28 (seguridad)" if u["multiplicador_usuario"] < 2 else "×4.0–4.8 (amplio)"].append(
                (u["apoyo_conjunto_gana_entera"], u["apoyo_conjunto_gana_entera"] - eq, "usuario (cuota informada, no verificada)", "—", f"×{u['multiplicador_usuario']}", len(u["patas"]), round(eq, 3)))
    L = []
    for name, rows in fam.items():
        if not rows:
            continue
        rows.sort(key=lambda r: (-r[0], -r[1]))
        L += [f"## Ranking general — familia {name} (de primero a último)", "",
              "Criterio: mayor apoyo conjunto descriptivo; a igual apoyo, menor distancia al equilibrio 1/cuota. Un margen negativo = la frecuencia histórica no cubre lo que paga el ticket. NO es EV real.", "",
              "| Puesto | Perfil | Borrador | Cuota (cons.) | Patas | Apoyo conjunto | Equilibrio 1/cuota | Margen |", "|---|---|---|---|---|---|---|---|"]
        for k, (ap, m, pn, i, cuota, npatas, eq) in enumerate(rows, 1):
            L.append(f"| {k} | {pn} | {i} | {cuota} | {npatas} | {ap} | {eq} | {round(m, 3)} |")
        L.append("")
    return L


def _gapflag(p):
    g = p_central(p)[1]
    return f" ⚠ brecha {g}" if g is not None and g >= MAX_GAP else ""


def render(result):
    L = ["# Tickets provisionales por multiplicador objetivo", "",
         "> **Cuotas = promedio de ≥3 casas vía agregador (NO ejecutables); la casa recalcula las combinadas del mismo partido (cuota real menor). "
         "Apoyo = frecuencia descriptiva conservadora (Wilson inferior), NO probabilidad predictiva ni EV.** Entre partidos distintos el producto supone independencia. "
         "Las cuotas de cada pata son la MEDIANA entre casas; «conservadora» descuenta un 5 % a cada par del mismo partido y debe seguir ≥ el mínimo del rango más un colchón. "
         "Contrastar con la cuota REAL de la casa y con el Nivel 2 (bajas, alineaciones, 2.ª fuente de calendario) antes de apostar. "
         "**Regla: un partido no puede aparecer en dos tickets** (si falla en uno, no arrastra al otro): "
         "TODOS los borradores de un perfil excluyen los partidos de TODOS los borradores de los perfiles anteriores: escojas el que escojas de cada multiplicador, no comparten partido. "
         "Dos patas del mismo partido solo entran con justificación medida (apoyo conjunto sobre los mismos partidos pasados). "
         "Las patas de los tickets exigen **calendario confirmado por dos fuentes independientes** (hora del partido) y excluyen categorías juvenil/sub-23/reserva (plantillas rotativas); los rankings top lo marcan en columnas.", ""]
    L += [f"> **Puertas de calidad de datos.** (1) Veracidad: {len(result.get('bloqueadas_por_calidad', []))} mercados bloqueados automáticamente por avisos graves de los agentes (cifras defectuosas/imposibles/sospechosas). "
          f"(2) Representatividad: {result.get('excluidas_por_historial_mixto', 0)} patas con historial MIXTO (otra competición, copas, pretemporada) quedan fuera de los tickets y rankings principales; "
          "las de Champions pasan a las variantes `*_champions`, rotuladas de menor respaldo.", ""]
    fj = result.get("filtros_jornada") or {}
    if fj.get("despues_de_utc") or fj.get("partidos_excluidos_manualmente"):
        L += [f"> **Filtros de jornada:** solo partidos que empiezan después de {fj.get('despues_de_utc')} ({fj.get('partidos_descartados_por_hora', 0)} partidos descartados por hora); excluidos a mano: {', '.join(fj.get('partidos_excluidos_manualmente') or []) or 'ninguno'}. "
              "Comprueba en tu casa que cada partido siga prepartido.", ""]
    if result.get("filtro_relajado"):
        L += [f"> # ⚠ FILTRO RELAJADO — NO RECOMENDADO\n> Estos borradores se generaron con una brecha muestra−mercado máxima de {result.get('max_brecha_usada')} (el estándar es {MAX_GAP}) **solo porque la persona usuaria pidió ver un ticket de este multiplicador**. "
              "Con la brecha estándar no existe ningún borrador. La brecha grande es la señal que falló con Durban el 13-oct.", ""]
    _all = [tk for t in result["targets"] for tk in t["tickets"]]
    _evs = [tk["ev_mercado"] for tk in _all if tk.get("ev_mercado") is not None]
    if _all and (not _evs or max(_evs) < 0):
        L += ["> # ⚠ AVISO DE RIESGO (la decisión de apostar es tuya)",
              f"> Con las probabilidades de mercado sin margen, ningún borrador tiene EV ≥ 0 (mejor EV {max(_evs) if _evs else 'n/d'}). Cada ticket muestra su probabilidad de pérdida y cada pata su brecha muestra−mercado (⚠ si ≥ 0.15). "
              "Una pata con cuota 1.25 falla 1 de cada 5 veces; un ticket no es «seguro» por tener mucho apoyo histórico. Los borradores de nivel «riesgo explícito» o «riesgo alto» se entregan porque se pidió ese multiplicador, rotulados.", ""]
    L += _ranking_general(result)
    for t in result["targets"]:
        L += [f"## Perfil «{t['name']}»: ×{t['lo']}–{t['hi']} (≤{t['max_legs']} patas, apoyo mínimo por ítem {t['min_support']}, colchón {int(t.get('buffer', 0) * 100)} %) — {len(t['tickets'])} borradores", ""]
        if len(t["tickets"]) == 1:
            L += ["**Solo existe 1 borrador distinto con las patas disponibles** (se pidieron varios para poder escoger): ampliar patas, bajar el apoyo mínimo o aportar cuotas reales.", ""]
        if not t["tickets"]:
            L += ["Sin combinación posible con las patas disponibles: no se fuerza ningún ticket.", ""]
        for i, tk in enumerate(t["tickets"], 1):
            flag = (" · ⚠ incluye cuota ESTIMADA (córners/tarjetas): verifícala en tu casa" if tk.get("usa_cuota_estimada") else "") + (" · incluye cuota aportada por ti" if tk.get("usa_cuota_manual") else "")
            L += [f"**Nivel de entrega: {tk.get('nivel_nombre', 'estándar')} · Rótulo honesto: {tk.get('etiqueta_riesgo')} · P(mercado, sin margen) {tk.get('p_mercado_conjunta')} · P(pérdida) {tk.get('p_perdida_mercado')} · EV(mercado) {tk.get('ev_mercado')} · P central (encogida) {tk.get('p_central_conjunta')} · EV central {tk.get('ev_central')} · mayor brecha muestra−mercado {tk.get('max_brecha_muestra_mercado')} · direcciones {tk.get('direcciones')}**", ""]
            L += [f"### Puesto {i} · Borrador {i}{flag}: ×{tk['cuota_combinada_media']} (conservadora ×{tk['cuota_combinada_conservadora']}) · {tk['n_patas']} pata(s) en {tk['n_partidos']} partido(s) · apoyo conjunto descriptivo {tk['apoyo_conjunto_descriptivo']} "
                  f"(implícita de mercado sin margen {tk['prob_implicita_conjunta_sin_margen']})", "",
                  "| Partido | Inicio UTC | Selección | Cuota media (mín–máx, casas) | Apoyo cons. | n |", "|---|---|---|---|---|---|"]
            for it in tk["items"]:
                for p in it["patas"]:
                    L.append(f"| {p['partido']} ({p['competicion']}) | {p['inicio_utc']} | {p['seleccion']}{' ⚑' if it['mismo_partido'] else ''}{_gapflag(p)} | {p['cuota_media']}{(' ✎est. (cuota por confirmar: exige ≥ ' + str(p['cuota_equilibrio_minima']) + ')') if p.get('cuota_tipo') == 'estimada_por_modelo' else ''} "
                             f"({p['minmax_casas'][0]}–{p['minmax_casas'][1]}, {p['n_casas']}) | {p['apoyo_conservador']} (mín. equipo {p.get('apoyo_min_equipo', '—')}) | {p['n'][0]}/{p['n'][1]} |")
                if it["mismo_partido"]:
                    L.append(f"| ⚑ *dos patas del mismo partido (cuota combinada media {it['cuota']}; la casa suele pagar menos).* {it.get('justificacion') or ''} | | | | | |")
            L.append("")
    tp = result.get("top_picks")
    if tp:
        hdr = ["| # | Partido | Categoría | Inicio UTC | Calendario | Selección | Cuota media (mín–máx, casas) | Apoyo cons. | n | Implícita s/margen | EV desc. cons. |", "|---|---|---|---|---|---|---|---|---|---|---|"]
        rows = lambda lst: [f"| {i} | {p['partido']} ({p['competicion']}){_gapflag(p)} | {p.get('categoria', 'men')}{' ⚠' if p.get('categoria', 'men') in EXCLUDE_TICKET_CATEGORIES else ''} | {p['inicio_utc']} | {'2 fuentes' if p.get('calendario_2_fuentes') else '1 fuente'} | {p['seleccion']}{' ✎est.' if p.get('cuota_tipo') == 'estimada_por_modelo' else ''} | {p['cuota_media']} ({p['minmax_casas'][0]}–{p['minmax_casas'][1]}, {p['n_casas']}) | "
                            f"{p['apoyo_conservador']} | {p['n'][0]}/{p['n'][1]} | {p['prob_implicita_sin_margen']} | {p['ev_descriptivo_conservador'] if p['ev_descriptivo_conservador'] is not None else '—'} |" for i, p in enumerate(lst, 1)]
        L += ["## Top de picks por SEGURIDAD (mayor apoyo conservador; una pata por partido)", ""] + hdr + rows(tp["seguridad"]) + [""]
        L += ["## Top de picks por ATRACTIVO (rentabilidad-cuota: EV descriptivo conservador = apoyo × cuota − 1, apoyo ≥ 0.55; ordenado de mayor a menor; EV negativo = la estadística conservadora no cubre el precio)", ""] + hdr + rows(tp["atractivo"]) + [
              "", "*EV descriptivo conservador NO es valor esperado real: usa el límite inferior de frecuencias pasadas como «probabilidad», y al escoger lo mejor entre cientos de patas "
              "tiende a sobrestimar. Estos rankings acompañan a los tickets y no los reemplazan; pueden repetir partidos que estén en un ticket.*", ""]
    if result["unpriced"]:
        L += ["## Córners, tarjetas y remates: INVENTARIO DESCRIPTIVO (misma evaluación de datos que goles y hándicaps, n≥8; SIN cuota real: no es una lista de apuestas) — de mayor a menor apoyo", "",
              "| # | Partido | Mercado | Selección (línea más ajustada que aún pasa) | Cuota aprox. ✎ | Apoyo (mín. equipo) | n | Cuota REAL mínima a exigir |", "|---|---|---|---|---|---|---|---|"]
        for i_, u in enumerate(result["unpriced"], 1):
            est_ = f"{u['cuota_media']}{' (tuya)' if u.get('cuota_tipo') == 'manual_usuario' else ' ✎'}" if u.get("cuota_media") else "<1.10"
            L.append(f"| {i_} | {u['partido']} | {u['mercado']} | {u['seleccion']} | {est_} | {u['apoyo_conservador']} ({u.get('apoyo_min_equipo', '—')}) | {u['n'][0]}/{u['n'][1]} | {u['cuota_equilibrio_minima']} |")
        L += ["", f"*Cuota aproximada = 1 / (frecuencia suavizada de ambos equipos × (1 + {EST_MARGIN})): supone un margen típico de casa y SALE de la misma estadística, por eso no se usa para hablar de valor. "
              "Sirve para armar y ordenar borradores. Antes de apostar compárala con tu casa: solo tiene valor si paga claramente por encima de la «cuota real mínima»; "
              "OJO: una cuota real ≥ esa mínima (≈1.65) en una línea que la muestra da 80–100 % suele indicar una definición distinta (puntos de reserva, tiempo parcial, línea mal leída), no valor. "
              "Si me pasas tus cuotas reales (`--manual-odds archivo.csv` con columnas home,away,seleccion,cuota) sustituyen a las aproximadas.*", ""]
    if not result.get("rotacion_disponible", True):
        L += ["> ⚠ Sin `rotation.json`: no se aplicó la penalización por riesgo de rotación (ejecuta `rotation_prior.py --from-tickets`).", ""]
    if result.get("patas_vetadas_por_rotacion"):
        L += ["## Patas vetadas por RIESGO DE ROTACIÓN a priori (se reevalúan a T-60 con el once real)", "", "| Partido | Selección | Motivo |", "|---|---|---|"]
        L += [f"| {v['partido']} | {v['seleccion']} | {v['motivo']} |" for v in result["patas_vetadas_por_rotacion"]] + [""]
    fav = result.get("favoritos")
    if fav is not None:
        L += ["## Favoritos a GANAR con filtro de dominancia (P mercado ≥ 0.65, brecha < 0.15, rotación baja, dominancia de liga ≥ 0.5)", ""]
        if not fav:
            L += ["Ningún favorito pasa todos los filtros (o falta `rotation.json` / `league_samples`): no se propone ninguno.", ""]
        else:
            L += ["| # | Partido | Selección | Cuota | P mercado | P central | Dominancia | EV central |", "|---|---|---|---|---|---|---|---|"]
            L += [f"| {i} | {f['partido']} | {f['seleccion']} | {f['cuota_media']} | {f['prob_implicita_sin_margen']} | {f['p_central']} | {f['dominancia']} | {f['ev_central']} |" for i, f in enumerate(fav, 1)] + [""]
    if result.get("patas_vetadas"):
        seen = set()
        L += ["## Patas VETADAS por la revisión (no entran en ningún ticket ni ranking)", "", "| Partido | Selección | Motivo |", "|---|---|---|"]
        for v in result["patas_vetadas"]:
            if (v["partido"], v["seleccion"]) not in seen:
                seen.add((v["partido"], v["seleccion"]))
                L.append(f"| {v['partido']} | {v['seleccion']} | {v.get('motivo') or ''} |")
        L.append("")
    reem = [(t["name"], x) for t in result["targets"] for x in t.get("reemplazos", []) if x["alternativas"]]
    if reem:
        L += ["## Reemplazos por pata (si quitas una pata, esto es lo mejor que queda con los mismos filtros)", "",
              "| Perfil | Borrador | Pata | Cuota | Alternativa 1 | → multiplicador | Alternativa 2 | → multiplicador |", "|---|---|---|---|---|---|---|---|"]
        for nm, x in reem:
            cell = lambda a: (f"{a['partido']} → {a['seleccion']} @{a['cuota']}{' ✎' if a['estimada'] else ''} (apoyo {a['apoyo']})", f"×{a['nuevo_multiplicador']}{'' if a['en_rango'] else ' ⚠ fuera de rango'}")
            c1 = cell(x["alternativas"][0]); c2 = cell(x["alternativas"][1]) if len(x["alternativas"]) > 1 else ("—", "—")
            L.append(f"| {nm} | {x['borrador']} | {x['pata']} | {x['cuota']} | {c1[0]} | {c1[1]} | {c2[0]} | {c2[1]} |")
        L.append("")
    if result.get("pares_vetados"):
        L += ["## PARES del mismo partido vetados tras la reevaluación por agentes", "", "| Partido | Par | Motivo |", "|---|---|---|"]
        L += [f"| {v['partido']} | {' + '.join(v['selecciones'])} | {v.get('motivo') or ''} |" for v in result["pares_vetados"]]
        L.append("")
    L += ["---", f"Partidos usados en borradores de perfiles previos: {len(result.get('partidos_usados_en_principales', []))}; sin partidos repetidos entre multiplicadores: {result.get('sin_partidos_repetidos_entre_perfiles')}; cuotas manuales aplicadas: {result.get('cuotas_manuales_aplicadas', 0)}.",
          f"Patas evaluadas: {result['n_legs']} (con cuota media: {result['n_priced_legs']}) en {result['n_matches_with_legs']} partidos."]
    return "\n".join(L)


def write_snapshots(run, out, now_iso=None):
    """snapshots.jsonl (auditoría 13-oct): una línea por borrador con lo que el sistema DECLARÓ al proponerlo (probabilidades, cuotas, brecha, rótulo, direcciones, vetos
    vigentes) para poder calibrar después con `calibracion.py`; no se sobrescribe, se añade."""
    import datetime
    now_iso = now_iso or datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    n = 0
    with open(os.path.join(run, "snapshots.jsonl"), "a", encoding="utf-8") as f:
        for t in out.get("targets", []):
            for i, tk in enumerate(t["tickets"], 1):
                f.write(json.dumps({"ts_utc": now_iso, "perfil": t["name"], "borrador": i, "cuota_media": tk["cuota_combinada_media"], "cuota_conservadora": tk["cuota_combinada_conservadora"],
                                    "p_mercado": tk.get("p_mercado_conjunta"), "p_central": tk.get("p_central_conjunta"), "ev_mercado": tk.get("ev_mercado"), "ev_central": tk.get("ev_central"),
                                    "max_brecha": tk.get("max_brecha_muestra_mercado"), "etiqueta": tk.get("etiqueta_riesgo"), "direcciones": tk.get("direcciones"),
                                    "n_vetos_vigentes": len(out.get("patas_vetadas", [])),
                                    "patas": [{"partido": l["partido"], "seleccion": l["seleccion"], "cuota": l["cuota_media"], "tipo_cuota": l.get("cuota_tipo"), "p_mercado": l.get("prob_implicita_sin_margen"),
                                               "frec": l.get("frec"), "n": l.get("n"), "inicio_utc": l.get("inicio_utc")} for it in tk["items"] for l in it["patas"]]}, ensure_ascii=False) + "\n")
                n += 1
    return n


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--run", required=True)
    ap.add_argument("--target", action="append", help="NOMBRE:LO:HI:MAX_PATAS:APOYO_MIN (repetible)")
    ap.add_argument("--top", type=int, default=5, help="borradores por perfil (siempre se piden varios para poder escoger)")
    ap.add_argument("--manual-odds", help="CSV/JSON con cuotas reales de la persona usuaria: home,away,seleccion,cuota")
    ap.add_argument("--pool", type=int, default=60)
    ap.add_argument("--after-utc", help="ISO UTC (p. ej. 2026-10-13T15:30:00Z) o «now»: descarta los partidos que empiezan antes (ya jugados o en juego); «now» suma 15 min de margen")
    ap.add_argument("--exclude-match", action="append", default=[], help="«Local – Visitante» a excluir de todos los tickets (repetible), p. ej. el partido de otro ticket ya puesto")
    ap.add_argument("--only-profile", action="append", default=[], help="NOMBRE de perfil a generar (repetible): seguridad, amplio (las variantes champions siguen a --champions)")
    ap.add_argument("--relax-champions-once", action="store_true", help="EXPERIMENTO ÚNICO a pedido: añade un borrador solo-UEFA Champions League y una combinada Champions + otras ligas con filtros relajados SOLO para las patas de Champions (apoyo 0.40, piso por equipo 0.30, ≥4 partidos de los últimos 100 días, sin pares); el resto de reglas se mantiene")
    ap.add_argument("--max-gap", type=float, default=None, help="brecha muestra−mercado máxima de las patas de TICKET (por defecto MAX_GAP=0.15). Subirla es una RELAJACIÓN explícita a petición de la persona usuaria: el ticket sale rotulado y no es recomendable")
    ap.add_argument("--champions", action="store_true", help="añade las variantes solo-UEFA Champions League (apoyo y piso por equipo relajados y rotulados)")
    a = ap.parse_args(argv)
    targets = DEFAULT_TARGETS
    if a.target:
        targets = []
        for t in a.target:
            parts = t.split(":")
            n, lo, hi, mx, ms = parts[:5]
            targets.append((n, float(lo), float(hi), int(mx), float(ms), float(parts[5]) if len(parts) > 5 else 0.0))
    if not os.path.exists(os.path.join(a.run, "matrix.json")):
        print("error: falta matrix.json (ejecuta level1.py)", file=sys.stderr)
        return 2
    legs = collect_legs(a.run)
    n_manual = apply_manual_odds(legs, a.manual_odds) if a.manual_odds else 0
    load_pair_rules(a.run)
    if a.only_profile:
        targets = [t for t in targets if t[0] in a.only_profile]
    legs, filtros = filter_legs_time_and_matches(legs, a.after_utc, [])              # la exclusión a mano vale SOLO para armar tickets (abajo), no para tops ni inventario
    filtros["partidos_excluidos_manualmente"] = list(a.exclude_match or [])
    excluded_names = {common.norm_name(x) for x in (a.exclude_match or [])}
    legs, vetoed = apply_vetoes(legs, os.path.join(a.run, "vetoes.json"))
    legs, gated = apply_quality_gate(legs, a.run)
    rot_path = os.path.join(a.run, "rotation.json")
    legs, vetoed_rot, has_rot = apply_rotation(legs, rot_path)
    legs_all = legs
    legs = [l for l in legs_all if l["history_kind"] in SAME_COMPETITION_KINDS]          # tickets y rankings PRINCIPALES: solo historial de la misma competición
    mixed_champ = [l for l in legs_all if l["history_kind"] not in SAME_COMPETITION_KINDS and "champions league" in (l.get("competicion") or "").lower()
                   and common.norm_name(l["partido"]) not in excluded_names]
    legs_tk = [l for l in legs if common.norm_name(l["partido"]) not in excluded_names]      # patas para TICKETS (sin los partidos excluidos a mano)
    legs_tk_all = legs_tk
    legs_tk, big_gap = drop_big_gap(legs_tk, a.max_gap)                                                  # auditoría 13-oct: brecha muestra−mercado ≥ 15 pp = descarte, no «salvedad"
    out = {"targets": [], "n_legs": len(legs), "n_priced_legs": sum(1 for l in legs if l["cuota_media"] is not None),
           "n_matches_with_legs": len({l["match_id"] for l in legs})}
    results = [dict(name=n, lo=lo, hi=hi, max_legs=mx, min_support=ms, buffer=bf) for n, lo, hi, mx, ms, bf in targets]
    if a.champions:
        results += [dict(name=n, lo=lo, hi=hi, max_legs=mx, min_support=ms, buffer=bf, solo_champions=True) for n, lo, hi, mx, ms, bf in CHAMPIONS_TARGETS
                    if not a.only_profile or n.split("_")[0] in a.only_profile]
    used, chosen = frozenset(), []
    ucl = mixed_champ
    for r in results:                                   # perfiles en orden: el primero (seguridad) fija partidos que los demás NO pueden usar
        r_legs, r_floor = (ucl, CHAMPIONS_TEAM_FLOOR) if r.get("solo_champions") else (legs_tk, TEAM_FLOOR_BY_PROFILE.get(r["name"], TEAM_FLOOR))
        _div = dict(zip(("max_overlap", "max_reuse"), PROFILE_DIVERSITY.get(r["name"], (None, None))))
        tk, npool = search(r_legs, r["lo"], r["hi"], r["max_legs"], r["min_support"], a.top, a.pool, exclude=used, buffer=r["buffer"], team_floor=r_floor, **_div)
        for t_ in tk:
            t_["nivel"], t_["nivel_nombre"] = 1, TIERS[0]["nombre"]
        if not r.get("solo_champions") and a.max_gap is None:
            seen_ = {frozenset((l["match_id"], l["seleccion"]) for it in t_["items"] for l in it["patas"]) for t_ in tk}
            for tr in TIERS[1:]:
                if len(tk) >= MIN_DRAFTS:
                    break
                lg_ = [l for l in legs_tk_all if (p_central(l)[1] is None or p_central(l)[1] < tr["gap"])]
                more, _ = search(lg_, r["lo"], r["hi"], r["max_legs"] + tr["extra_legs"], max(0.30, r["min_support"] + tr["soporte"]), a.top, a.pool, exclude=used, buffer=r["buffer"],
                                 team_floor=max(0.30, r_floor + tr["soporte"]), max_dir=tr["max_dir"], budget=TIER_BUDGET, **_div)
                for t_ in more:
                    key_ = frozenset((l["match_id"], l["seleccion"]) for it in t_["items"] for l in it["patas"])
                    if key_ not in seen_ and len(tk) < max(a.top, MIN_DRAFTS):
                        t_["nivel"], t_["nivel_nombre"] = tr["n"], tr["nombre"]
                        tk.append(t_)
                        seen_.add(key_)
        r.update(pool=npool, tickets=tk)
        r["_singles"] = [i for i in _items(r_legs, r["min_support"], with_pairs=False, require_calendar=True, exclude_categories=EXCLUDE_TICKET_CATEGORIES, team_floor=r_floor)]
        if tk:                                           # CUALQUIER borrador de un perfil queda excluido de los perfiles siguientes:
            used = used | {it["match_id"] for t_ in tk for it in t_["items"]}        # sea cual escojas de cada uno, no comparten partido
            chosen.append(tk[0])
    taken = {it["match_id"] for r in results for t_ in r["tickets"] for it in t_["items"]}
    for r in results:
        r["reemplazos"] = _replacements(r["tickets"], r.pop("_singles", []), r["lo"], r["hi"], taken)
    out["filtros_jornada"] = filtros
    out["targets"] = results
    out["partidos_usados_en_principales"] = sorted(used)
    sets = [{it["match_id"] for t_ in r["tickets"] for it in t_["items"]} for r in results]
    out["sin_partidos_repetidos_entre_perfiles"] = all(not (sets[i] & sets[j]) for i in range(len(sets)) for j in range(i + 1, len(sets)))
    out["sin_partidos_repetidos_entre_principales"] = out["sin_partidos_repetidos_entre_perfiles"]
    if a.relax_champions_once:
        ucl_legs = [l for l in legs_all if l["history_kind"] not in SAME_COMPETITION_KINDS and "uefa champions league" in (l.get("competicion") or "").lower()
                   and common.norm_name(l["partido"]) not in excluded_names]
        items_ucl = _items(ucl_legs, 0.40, with_pairs=False, require_calendar=True, exclude_categories=EXCLUDE_TICKET_CATEGORIES, team_floor=0.30, min_recent=4)
        items_main = _items(legs_tk, 0.55, with_pairs=False, require_calendar=True, exclude_categories=EXCLUDE_TICKET_CATEGORIES, team_floor=0.45)
        ucl_ids = {i["match_id"] for i in items_ucl}
        div = dict(max_overlap=0.6, max_reuse=3, buffer=0.04)
        main_top = sorted(items_main, key=lambda i: (-i["apoyo"], -i["cuota"]))[:60]
        specs = (("experimento_champions_solo_real", items_ucl, None, 0), ("experimento_champions_solo_con_estimadas", items_ucl, None, 2),
                 ("experimento_champions_mixto_real", main_top + items_ucl, lambda ch: any(c["match_id"] in ucl_ids for c in ch), 0),
                 ("experimento_champions_mixto_con_estimadas", main_top + items_ucl, lambda ch: any(c["match_id"] in ucl_ids for c in ch), 2))
        counts = {}
        for nm, its, req, me in specs:
            tk, _ = search(None, 4.0, 4.8, 6, 0.40, top=1, pool=220, items_override=its, require=req, max_estimated=me, **div)
            counts[nm] = len(tk)
            results.append(dict(name=nm, lo=4.0, hi=4.8, max_legs=6, min_support=0.40, buffer=0.04, tickets=tk, pool=len(its), reemplazos=[], experimento=True))
        out["experimento_champions"] = {"parametros": "apoyo mínimo 0.40, piso por equipo 0.30, ≥4 partidos de los últimos 100 días, sin pares; solo patas de la UEFA Champions League; el resto de reglas igual",
                                        "patas_champions_elegibles": len(items_ucl), "borradores": counts}
    out["cuotas_manuales_aplicadas"] = n_manual
    out["patas_vetadas"] = vetoed
    out["patas_vetadas_por_rotacion"] = vetoed_rot
    out["patas_descartadas_por_brecha"] = big_gap
    out["max_brecha_usada"] = MAX_GAP if a.max_gap is None else a.max_gap
    out["filtro_relajado"] = a.max_gap is not None and a.max_gap > MAX_GAP
    out["rotacion_disponible"] = has_rot
    out["favoritos"] = favorites_table(legs, a.run, rot_path)
    out["bloqueadas_por_calidad"] = gated
    out["pares_vetados"] = [{"partido": v["partido"], "selecciones": v["selecciones"], "motivo": v.get("motivo")} for v in PAIR_RULES["vetados"].values()]
    out["excluidas_por_historial_mixto"] = len(legs_all) - len(legs)
    eligible = [l for l in legs if l.get("calendario_2_fuentes") and l.get("categoria", "men") not in EXCLUDE_TICKET_CATEGORIES
                and (l.get("cuota_tipo") in ("estimada_por_modelo", "manual_usuario") or l.get("n_casas", 0) >= TICKET_MIN_BOOKS)]
    up = os.path.join(a.run, "user_tickets_eval.json")
    out["usuario"] = common.read_json(up, []) if os.path.exists(up) else []
    stat_pool = [l for l in legs if l.get("calendario_2_fuentes") and l.get("categoria", "men") not in EXCLUDE_TICKET_CATEGORIES]
    out["unpriced"] = unpriced(stat_pool)
    out["candidatos_estadisticos"] = {"lineas_evaluadas": write_stat_candidates_csv(a.run, stat_pool), "archivo": "candidatos_estadisticos.csv"}
    with open(os.path.join(a.run, "manual_odds_plantilla.csv"), "w", encoding="utf-8", newline="") as fh_:
        import csv as _csv
        w_ = _csv.writer(fh_)
        w_.writerow(["home", "away", "seleccion", "cuota", "mercado", "apoyo", "cuota_minima_a_exigir"])
        for u in out["unpriced"]:
            h_, a_ = u["partido"].split(" – ")
            w_.writerow([h_, a_, u["seleccion"], "", u["mercado"], u["apoyo_conservador"], u["cuota_equilibrio_minima"]])
    out["top_picks"] = top_picks(eligible)
    common.write_json_atomic(os.path.join(a.run, "tickets.json"), out)
    write_snapshots(a.run, out)
    text = render(out)
    with open(os.path.join(a.run, "tickets.md"), "w", encoding="utf-8") as f:
        f.write(text + "\n")
    print(text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
