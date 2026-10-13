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
import importlib.util
import itertools
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common  # noqa: E402

_CALC = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "evaluacion-probabilidad-valor", "scripts", "calc.py"))
_spec = importlib.util.spec_from_file_location("calc", _CALC)
calc = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(calc)

# nombre, lo, hi, máx. patas (cada pata cuenta), apoyo conservador mínimo por ítem
# Con n=10 el límite inferior de Wilson de un 10/10 es 0.722 y el de 9/10 es 0.66: por eso el mínimo de «seguridad» es 0.65 (≈ ≥9/10 en cada equipo)
# (nombre, lo, hi, máx patas, apoyo mín por ítem, colchón sobre `lo`): el multiplicador CONSERVADOR (pares −5 %) debe quedar ≥ lo·(1+colchón)
DEFAULT_TARGETS = [("seguridad", 1.20, 1.28, 2, 0.65, 0.01), ("amplio", 4.0, 4.8, 6, 0.55, 0.04)]
OK_KINDS = ("apifootball_misma_competicion", "apifootball_historial_propio", "football-data_misma_liga")
MIN_N, MIN_BOOKS = 6, 3
TEAM_FLOOR = 0.55        # revisión del auditor: el apoyo es el promedio de dos equipos y un 10/10 tapa al flojo; en tickets CADA equipo debe alcanzar este piso (8/10 → 0.49 no pasa)
TEAM_FLOOR_BY_PROFILE = {"amplio": 0.45}    # el perfil amplio acepta 8/10 por equipo (Wilson 0.49): relajado y rotulado; seguridad usa TEAM_FLOOR
EXCLUDE_TICKET_SELECTIONS = ("Gana alguno, sin empate",)    # auditor ronda 2: las patas «12» salen con ~8 % de empates frente a 22–30 % de mercado (¿empate registrado como victoria en copas?): fuera de tickets hasta verificar marcadores a 90'
MAX_LEG_REUSE = 2       # una misma pata (partido+selección) aparece como máximo en 2 borradores de un perfil (evita que un solo fallo hunda todos)
TICKET_MIN_BOOKS = 4    # revisión por lotes: cuotas medias de 2–3 casas son frágiles (precios repetidos/extremos); las patas de TICKET exigen ≥4 casas (rankings: ≥3)
ODDS_MIN, ODDS_MAX = 1.03, 2.6
PAIR_TOP_PER_MATCH = 10
EST_MARGIN = 0.08     # SUPUESTO: margen típico de una casa en mercados secundarios; la cuota estimada NO es de ninguna casa
EXCLUDE_TICKET_CATEGORIES = ('youth', 'u23', 'reserve')    # plantillas juveniles/sub-23/reservas rotan y su historial es poco fiable: fuera de los tickets por defecto
PAIR_HAIRCUT = 0.95   # la casa suele pagar menos por combinar dos mercados del mismo partido: se descuenta un 5 % para decidir si el ticket sigue en rango
MAX_ESTIMATED_LEGS = 1  # como máximo una pata con cuota ESTIMADA (córners/tarjetas) por ticket
MAX_OVERLAP = 0.34    # borradores de un mismo perfil: como máximo un tercio de sus partidos puede coincidir con uno ya elegido


def _res(h):
    return None if h["gf"] is None or h["ga"] is None else h["gf"] - h["ga"]


def _tot(h):
    return None if h["gf"] is None or h["ga"] is None else h["gf"] + h["ga"]


def _corners(h):
    return None if None in h["corners"] else h["corners"][0] + h["corners"][1]


def _cards(h):
    return None if None in h["yellow"] or None in h["red"] else sum(h["yellow"]) + sum(h["red"])


def _both(h):
    return None if h["gf"] is None else (h["gf"] > 0 and h["ga"] > 0)


def _pred(f, test):
    return lambda h: (lambda v: None if v is None else test(v))(f(h))


def atoms(ev):
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
    for line in (8.5, 9.5, 10.5, 11.5):
        o, u = _pred(_corners, lambda v, l=line: v > l), _pred(_corners, lambda v, l=line: v < l)
        add(None, 0, "córners", f"Más de {line} córners", o, o)
        add(None, 1, "córners", f"Menos de {line} córners", u, u)
    for line in (2.5, 3.5, 4.5, 5.5):
        o, u = _pred(_cards, lambda v, l=line: v > l), _pred(_cards, lambda v, l=line: v < l)
        add(None, 0, "tarjetas", f"Más de {line} tarjetas (A+R)", o, o)
        add(None, 1, "tarjetas", f"Menos de {line} tarjetas (A+R)", u, u)
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


def legs_for_match(m, ev, _unused=None):
    """Patas (con cuota media o sin ella) + predicados para medir apoyo conjunto. Nunca desde proxy ni sin muestra n>=6."""
    if ev.get("history_kind") not in OK_KINDS:
        return []
    fh, fa = ev["form"].get("local", []), ev["form"].get("visitante", [])
    out = []
    for key, idx, market, label, ph, pa in atoms(ev):
        sup = _support(fh, fa, ph, pa)
        if not sup:
            continue
        leg = {"match_id": m["match_id"], "partido": f"{m['home_team']} – {m['away_team']}", "competicion": m["competition"],
               "inicio_utc": m["normalized_datetime_utc"], "categoria": m.get("gender_or_category", "men"), "calendario_2_fuentes": m.get("selection_calendar_verification") == "SUFICIENTE", "mercado": market, "seleccion": label, "history_kind": ev["history_kind"],
               "cuota_media": None, "minmax_casas": None, "n_casas": 0, "prob_implicita_sin_margen": None,
               "cuota_equilibrio_minima": round(1 / max(sup["apoyo_conservador"], 1e-9), 2), **sup, "_ph": ph, "_pa": pa, "_fh": fh, "_fa": fa}
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


def _items(legs, min_support, with_pairs=True, require_calendar=False, exclude_categories=(), team_floor=TEAM_FLOOR):
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
            if l["apoyo_conservador"] >= min_support and (not require_calendar or l.get("apoyo_min_equipo", 1) >= team_floor):
                items.append({"match_id": mid, "patas": [l], "cuota": l["cuota_media"], "cuota_cons": l["cuota_media"], "apoyo": l["apoyo_conservador"], "mismo_partido": False})
        if with_pairs:
            for a, b in itertools.combinations(ls[:PAIR_TOP_PER_MATCH], 2):
                if _family(a) == _family(b):          # misma familia (p. ej. «más de 1.5» + «más de 2.5», o 1X + hándicap): una pata implica o contradice a la otra
                    continue
                ph = lambda h, a=a, b=b: (lambda x, y: None if x is None or y is None else (x and y))(a["_ph"](h), b["_ph"](h))
                pa = lambda h, a=a, b=b: (lambda x, y: None if x is None or y is None else (x and y))(a["_pa"](h), b["_pa"](h))
                sup = _support(a["_fh"], a["_fa"], ph, pa)
                # «bien justificado»: el apoyo CONJUNTO medido sobre los mismos partidos pasados supera el mínimo del perfil y no es
                # peor que el de las dos patas tratadas como independientes (tolerancia 0.02): la segunda pata no debilita a la primera
                indep = a["apoyo_conservador"] * b["apoyo_conservador"]
                if sup and sup["apoyo_conservador"] >= min_support and sup["apoyo_conservador"] >= indep - 0.02 and (not require_calendar or sup["apoyo_min_equipo"] >= team_floor):
                    just = (f"Conjunto medido en los mismos partidos pasados: local {sup['frec'][0]} (n={sup['n'][0]}), visitante {sup['frec'][1]} (n={sup['n'][1]}); "
                            f"apoyo conservador conjunto {sup['apoyo_conservador']} frente a {round(indep, 3)} si las patas fueran independientes "
                            f"({a['apoyo_conservador']} × {b['apoyo_conservador']}): " +
                            ("las patas se refuerzan entre sí." if sup["apoyo_conservador"] >= indep else "casi sin pérdida respecto a la independencia."))
                    items.append({"match_id": mid, "patas": [a, b], "cuota": round(a["cuota_media"] * b["cuota_media"], 3),
                                  "cuota_cons": round(a["cuota_media"] * b["cuota_media"] * PAIR_HAIRCUT, 3),
                                  "apoyo": sup["apoyo_conservador"], "mismo_partido": True, "apoyo_conjunto": sup, "justificacion": just})
    return items


def search(legs, lo, hi, max_legs, min_support, top=5, pool=60, exclude=frozenset(), require_calendar=True, exclude_categories=EXCLUDE_TICKET_CATEGORIES, buffer=0.0, team_floor=TEAM_FLOOR):
    items = [i for i in _items(legs, min_support, require_calendar=require_calendar, exclude_categories=exclude_categories, team_floor=team_floor) if i["match_id"] not in exclude]
    items.sort(key=lambda i: (-i["apoyo"], -i["cuota"]))      # a igual apoyo (= igual riesgo), la cuota más alta
    best_per_match, cand = {}, []
    for it in items:                                        # hasta 6 ítems por partido para no perder la variedad de mercados
        if it["cuota"] > hi:                                # un ítem cuya cuota ya supera el rango nunca puede formar parte del ticket
            continue
        if it["cuota"] ** (1 / len(it["patas"])) < 0.9 * lo ** (1 / max_legs):
            continue                                        # con max_legs patas no se llega a `lo` si cada pata paga menos de ~la media necesaria
        if best_per_match.get(it["match_id"], 0) < 6:
            best_per_match[it["match_id"]] = best_per_match.get(it["match_id"], 0) + 1
            cand.append(it)
    cand = cand[:pool]
    res = []

    lo_cons = lo * (1 + buffer)

    def rec(start, chosen, prod, prod_cons, nlegs, nest):
        if prod_cons >= lo_cons and prod <= hi and chosen:
            res.append((calc.joint_prob([c["apoyo"] for c in chosen]), -nlegs, prod, tuple(chosen)))
        for i in range(start, len(cand)):
            it = cand[i]
            if it["match_id"] in {c["match_id"] for c in chosen}:
                continue
            n = nlegs + len(it["patas"])
            e = nest + sum(1 for l in it["patas"] if l.get("cuota_tipo") == "estimada_por_modelo")
            p = prod * it["cuota"]
            if n <= max_legs and p <= hi and e <= MAX_ESTIMATED_LEGS:
                rec(i + 1, chosen + [it], p, prod_cons * it["cuota_cons"], n, e)
    rec(0, [], 1.0, 1.0, 0, 0)
    res.sort(key=lambda t: (-t[0], -t[1]))
    picked, taken, reuse = [], [], {}
    for r in res:                                       # borradores DISTINTOS: no repetir casi los mismos partidos
        ms = {x["match_id"] for x in r[3]}
        keys = {(l["match_id"], l["seleccion"]) for x in r[3] for l in x["patas"]}
        if all(len(ms & t) / min(len(ms), len(t)) <= MAX_OVERLAP for t in taken) and all(reuse.get(k, 0) < MAX_LEG_REUSE for k in keys):
            picked.append(r)
            taken.append(ms)
            for k in keys:
                reuse[k] = reuse.get(k, 0) + 1
        if len(picked) >= top:
            break
    out = []
    for s, nl, p, c in picked:
        out.append({"cuota_combinada_media": round(calc.combo_odds([x["cuota"] for x in c]), 3),
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
    return {"seguridad": pick(lambda l: (-l["apoyo_conservador"], -l["cuota_media"]), lambda l: True),
            "atractivo": pick(lambda l: (-(l["ev_descriptivo_conservador"] or -9), -l["apoyo_conservador"]),
                              lambda l: l["apoyo_conservador"] >= min_attr_support and l["ev_descriptivo_conservador"] is not None and l["ev_descriptivo_conservador"] > 0)}


def unpriced(legs, top=20, min_support=0.5):
    """Córners/tarjetas (sin cuota publicada en ninguna fuente usada): cuota APROXIMADA por modelo y cuota real mínima a exigir."""
    xs = [{k: v for k, v in l.items() if not k.startswith("_")} for l in legs if l.get("cuota_tipo") in ("estimada_por_modelo", "manual_usuario")
          and l["apoyo_conservador"] >= min_support]
    xs.sort(key=lambda l: (-l["apoyo_conservador"], l["partido"]))
    seen, out = {}, []
    for l in xs:                                        # máx. 2 selecciones por partido en la lista
        seen[l["match_id"]] = seen.get(l["match_id"], 0) + 1
        if seen[l["match_id"]] <= 2:
            out.append(l)
        if len(out) >= top:
            break
    return out


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
    for t in result["targets"]:
        L += [f"## Perfil «{t['name']}»: ×{t['lo']}–{t['hi']} (≤{t['max_legs']} patas, apoyo mínimo por ítem {t['min_support']}, colchón {int(t.get('buffer', 0) * 100)} %) — {len(t['tickets'])} borradores", ""]
        if len(t["tickets"]) == 1:
            L += ["**Solo existe 1 borrador distinto con las patas disponibles** (se pidieron varios para poder escoger): ampliar patas, bajar el apoyo mínimo o aportar cuotas reales.", ""]
        if not t["tickets"]:
            L += ["Sin combinación posible con las patas disponibles: no se fuerza ningún ticket.", ""]
        for i, tk in enumerate(t["tickets"], 1):
            flag = (" · ⚠ incluye cuota ESTIMADA (córners/tarjetas): verifícala en tu casa" if tk.get("usa_cuota_estimada") else "") + (" · incluye cuota aportada por ti" if tk.get("usa_cuota_manual") else "")
            L += [f"### Borrador {i}{flag}: ×{tk['cuota_combinada_media']} (conservadora ×{tk['cuota_combinada_conservadora']}) · {tk['n_patas']} pata(s) en {tk['n_partidos']} partido(s) · apoyo conjunto descriptivo {tk['apoyo_conjunto_descriptivo']} "
                  f"(implícita de mercado sin margen {tk['prob_implicita_conjunta_sin_margen']})", "",
                  "| Partido | Inicio UTC | Selección | Cuota media (mín–máx, casas) | Apoyo cons. | n |", "|---|---|---|---|---|---|"]
            for it in tk["items"]:
                for p in it["patas"]:
                    L.append(f"| {p['partido']} ({p['competicion']}) | {p['inicio_utc']} | {p['seleccion']}{' ⚑' if it['mismo_partido'] else ''} | {p['cuota_media']}{' ✎est.' if p.get('cuota_tipo') == 'estimada_por_modelo' else ''} "
                             f"({p['minmax_casas'][0]}–{p['minmax_casas'][1]}, {p['n_casas']}) | {p['apoyo_conservador']} (mín. equipo {p.get('apoyo_min_equipo', '—')}) | {p['n'][0]}/{p['n'][1]} |")
                if it["mismo_partido"]:
                    L.append(f"| ⚑ *dos patas del mismo partido (cuota combinada media {it['cuota']}; la casa suele pagar menos).* {it.get('justificacion') or ''} | | | | | |")
            L.append("")
    tp = result.get("top_picks")
    if tp:
        hdr = ["| # | Partido | Categoría | Inicio UTC | Calendario | Selección | Cuota media (mín–máx, casas) | Apoyo cons. | n | Implícita s/margen | EV desc. cons. |", "|---|---|---|---|---|---|---|---|---|---|---|"]
        rows = lambda lst: [f"| {i} | {p['partido']} ({p['competicion']}) | {p.get('categoria', 'men')}{' ⚠' if p.get('categoria', 'men') in EXCLUDE_TICKET_CATEGORIES else ''} | {p['inicio_utc']} | {'2 fuentes' if p.get('calendario_2_fuentes') else '1 fuente'} | {p['seleccion']}{' ✎est.' if p.get('cuota_tipo') == 'estimada_por_modelo' else ''} | {p['cuota_media']} ({p['minmax_casas'][0]}–{p['minmax_casas'][1]}, {p['n_casas']}) | "
                            f"{p['apoyo_conservador']} | {p['n'][0]}/{p['n'][1]} | {p['prob_implicita_sin_margen']} | {p['ev_descriptivo_conservador'] if p['ev_descriptivo_conservador'] is not None else '—'} |" for i, p in enumerate(lst, 1)]
        L += ["## Top de picks por SEGURIDAD (mayor apoyo conservador; una pata por partido)", ""] + hdr + rows(tp["seguridad"]) + [""]
        L += ["## Top de picks por ATRACTIVO (rentabilidad-cuota: EV descriptivo conservador = apoyo × cuota − 1, apoyo ≥ 0.55)", ""] + hdr + rows(tp["atractivo"]) + [
              "", "*EV descriptivo conservador NO es valor esperado real: usa el límite inferior de frecuencias pasadas como «probabilidad», y al escoger lo mejor entre cientos de patas "
              "tiende a sobrestimar. Estos rankings acompañan a los tickets y no los reemplazan; pueden repetir partidos que estén en un ticket.*", ""]
    if result["unpriced"]:
        L += ["## Córners y tarjetas: cuota APROXIMADA por modelo (✎ no es de ninguna casa) y cuota real mínima a exigir", "",
              "| Partido | Selección | Cuota aprox. | Apoyo cons. | n | Cuota real mínima para tener valor |", "|---|---|---|---|---|---|"]
        for u in result["unpriced"]:
            L.append(f"| {u['partido']} | {u['seleccion']} | {u['cuota_media']}{' (tuya)' if u.get('cuota_tipo') == 'manual_usuario' else ' ✎'} | {u['apoyo_conservador']} | {u['n'][0]}/{u['n'][1]} | {u['cuota_equilibrio_minima']} |")
        L += ["", f"*Cuota aproximada = 1 / (frecuencia suavizada de ambos equipos × (1 + {EST_MARGIN})): supone un margen típico de casa y SALE de la misma estadística, por eso no se usa para hablar de valor. "
              "Sirve para armar y ordenar borradores. Antes de apostar compárala con tu casa: solo tiene valor si paga claramente por encima de la «cuota real mínima». "
              "Si me pasas tus cuotas reales (`--manual-odds archivo.csv` con columnas home,away,seleccion,cuota) sustituyen a las aproximadas.*", ""]
    if result.get("patas_vetadas"):
        seen = set()
        L += ["## Patas VETADAS por la revisión (no entran en ningún ticket ni ranking)", "", "| Partido | Selección | Motivo |", "|---|---|---|"]
        for v in result["patas_vetadas"]:
            if (v["partido"], v["seleccion"]) not in seen:
                seen.add((v["partido"], v["seleccion"]))
                L.append(f"| {v['partido']} | {v['seleccion']} | {v.get('motivo') or ''} |")
        L.append("")
    L += ["---", f"Partidos usados en borradores de perfiles previos: {len(result.get('partidos_usados_en_principales', []))}; sin partidos repetidos entre multiplicadores: {result.get('sin_partidos_repetidos_entre_perfiles')}; cuotas manuales aplicadas: {result.get('cuotas_manuales_aplicadas', 0)}.",
          f"Patas evaluadas: {result['n_legs']} (con cuota media: {result['n_priced_legs']}) en {result['n_matches_with_legs']} partidos."]
    return "\n".join(L)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--run", required=True)
    ap.add_argument("--target", action="append", help="NOMBRE:LO:HI:MAX_PATAS:APOYO_MIN (repetible)")
    ap.add_argument("--top", type=int, default=5, help="borradores por perfil (siempre se piden varios para poder escoger)")
    ap.add_argument("--manual-odds", help="CSV/JSON con cuotas reales de la persona usuaria: home,away,seleccion,cuota")
    ap.add_argument("--pool", type=int, default=60)
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
    legs, vetoed = apply_vetoes(legs, os.path.join(a.run, "vetoes.json"))
    out = {"targets": [], "n_legs": len(legs), "n_priced_legs": sum(1 for l in legs if l["cuota_media"] is not None),
           "n_matches_with_legs": len({l["match_id"] for l in legs})}
    results = [dict(name=n, lo=lo, hi=hi, max_legs=mx, min_support=ms, buffer=bf) for n, lo, hi, mx, ms, bf in targets]
    used, chosen = frozenset(), []
    for r in results:                                   # perfiles en orden: el primero (seguridad) fija partidos que los demás NO pueden usar
        tk, npool = search(legs, r["lo"], r["hi"], r["max_legs"], r["min_support"], a.top, a.pool, exclude=used, buffer=r["buffer"], team_floor=TEAM_FLOOR_BY_PROFILE.get(r["name"], TEAM_FLOOR))
        r.update(pool=npool, tickets=tk)
        if tk:                                           # CUALQUIER borrador de un perfil queda excluido de los perfiles siguientes:
            used = used | {it["match_id"] for t_ in tk for it in t_["items"]}        # sea cual escojas de cada uno, no comparten partido
            chosen.append(tk[0])
    out["targets"] = results
    out["partidos_usados_en_principales"] = sorted(used)
    sets = [{it["match_id"] for t_ in r["tickets"] for it in t_["items"]} for r in results]
    out["sin_partidos_repetidos_entre_perfiles"] = all(not (sets[i] & sets[j]) for i in range(len(sets)) for j in range(i + 1, len(sets)))
    out["sin_partidos_repetidos_entre_principales"] = out["sin_partidos_repetidos_entre_perfiles"]
    out["cuotas_manuales_aplicadas"] = n_manual
    out["patas_vetadas"] = vetoed
    eligible = [l for l in legs if l.get("calendario_2_fuentes") and l.get("categoria", "men") not in EXCLUDE_TICKET_CATEGORIES
                and (l.get("cuota_tipo") in ("estimada_por_modelo", "manual_usuario") or l.get("n_casas", 0) >= TICKET_MIN_BOOKS)]
    out["unpriced"] = unpriced(eligible)
    out["top_picks"] = top_picks(eligible)
    common.write_json_atomic(os.path.join(a.run, "tickets.json"), out)
    text = render(out)
    with open(os.path.join(a.run, "tickets.md"), "w", encoding="utf-8") as f:
        f.write(text + "\n")
    print(text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
