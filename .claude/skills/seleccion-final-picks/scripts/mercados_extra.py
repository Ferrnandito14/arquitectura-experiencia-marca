#!/usr/bin/env python3
"""Mercados adicionales de TheStatsAPI (hándicap asiático, totales por equipo, 1.ª parte, córners, tarjetas, BTTS 1.ª parte)
y GUARDIA DE COBERTURA: todo mercado que aparezca en los archivos de cuotas debe estar declarado como EXTRAIDO o EXCLUIDO (con motivo).
Un mercado desconocido hace fallar `auditar` (y el test), para que una omisión como la del 1-nov no vuelva a pasar en silencio.

Solo líneas .5 (sin devolución) en hándicap/totales: las líneas enteras y de cuarto dependen de reglas de liquidación de la casa no confirmadas.
Probabilidad: sin margen por casa (mercado de 2 vías) y promedio entre casas; cuota = mediana. Mínimo de casas: 3 (2 en córners/tarjetas, de menor cobertura).
"""
import glob
import json
import math
import os
import statistics
from datetime import datetime, timedelta, timezone

CARACAS = timezone(timedelta(hours=-4))
PAR_MIN, PAR_MAX = 1.0, 1.15

# Mercados que este módulo (o pool_mercado) convierte en patas.
EXTRAIDOS = {
    "match_odds", "double_chance", "total_goals", "btts",          # pool_mercado
    "asian_handicap", "team_total_goals", "first_half_total_goals", "first_half_result", "btts_first_half",
    "match_corners", "team_corners", "total_cards",
}
# Mercados vistos en los datos y NO usados, con el motivo.
EXCLUIDOS = {
    "draw_no_bet": "devuelve en empate: regla de liquidación de la casa por confirmar",
    "handicap_result": "hándicap europeo de 3 vías: regla de liquidación por confirmar",
    "correct_score": "marcador exacto: cuotas de cola (>2.10 casi siempre) y muy poca probabilidad",
    "first_team_to_score": "primer gol: reglas de 0-0 y cuotas por confirmar",
    "second_half_result": "2.ª parte: sin dossier de apoyo; baja prioridad",
    "btts_second_half": "2.ª parte: sin dossier de apoyo; baja prioridad",
    "half_time_double_chance": "descanso: sin dossier de apoyo; baja prioridad",
    "total_goals_btts": "combinado goles+BTTS: la casa lo arma distinto (Crear apuesta)",
    "to_score_a_penalty": "penal: cobertura mínima",
    "to_miss_a_penalty": "penal: cobertura mínima",
    "a_penalty_in_match": "penal: cobertura mínima",
}
# Familias con cobertura baja por naturaleza (se acepta con 2 casas).
POCAS_CASAS = {"match_corners", "team_corners", "total_cards", "team_total_goals"}
PREFIJOS_EXCLUIDOS = ("team_shots", "match_shots", "first_half_match_shots", "first_half_team_shots", "second_half_match_shots",
                      "second_half_team_shots", "first_half_match_shots_on_target", "first_half_team_shots_on_target",
                      "second_half_match_shots_on_target", "second_half_team_shots_on_target", "match_throw_ins", "team_throw_ins",
                      "first_half_match_throw_ins", "first_half_team_throw_ins", "second_half_match_throw_ins", "second_half_team_throw_ins")
MOTIVO_PREFIJOS = "tiros, saques de banda/puerta, fueras de juego y entradas: cobertura <15 partidos y una sola casa"


def clasificar(mercado):
    """'extraido' | 'excluido' | 'desconocido'."""
    if mercado in EXTRAIDOS:
        return "extraido"
    if mercado in EXCLUIDOS or mercado in PREFIJOS_EXCLUIDOS or mercado.endswith(("_shots", "_shots_on_target", "_throw_ins", "_goal_kicks", "_offsides", "_tackles")):
        return "excluido"
    return "desconocido"


def auditar(odds_dir):
    """Cuenta cada mercado visto en los archivos de cuotas y lo clasifica. Devuelve (conteo, desconocidos)."""
    conteo = {}
    for fn in sorted(glob.glob(os.path.join(odds_dir, "*.json"))):
        try:
            d = json.load(open(fn))["data"]
        except Exception:
            continue
        for b in d.get("bookmakers", []):
            for k in (b.get("markets") or {}):
                conteo[k] = conteo.get(k, 0) + 1
    desconocidos = sorted(k for k in conteo if clasificar(k) == "desconocido")
    return conteo, desconocidos


def _f(x):
    try:
        return float(x["last_seen"])
    except Exception:
        return None


def _nov2(a, b):
    pa, pb = 1 / a, 1 / b
    s = pa + pb
    return pa / s, s


def _nov3(a, b, c):
    p = [1 / a, 1 / b, 1 / c]
    s = sum(p)
    return [x / s for x in p], s


def _media_linea(lf):
    return abs(lf - math.floor(lf) - 0.5) < 1e-9


def patas_extra(match, odds):
    """Patas de los mercados adicionales de un partido. Devuelve lista de dicts con el formato del pool."""
    acum = {}

    def put(clave, casa, cuota, p, mercado_api):
        d = acum.setdefault(clave, {"cuotas": [], "ps": [], "casas": [], "api": mercado_api})
        d["cuotas"].append(cuota); d["ps"].append(p); d["casas"].append(casa)

    local, visit = match["home_team"]["name"], match["away_team"]["name"]
    for b in odds["data"]["bookmakers"]:
        casa, m = b["bookmaker"], b["markets"]
        # Hándicap asiático, solo líneas .5
        ah = m.get("asian_handicap") or {}
        for lado_h, lado_a in (("home", "away"),):
            for linea, vh in (ah.get(lado_h) or {}).items():
                try:
                    lf = float(linea)
                except ValueError:
                    continue
                if not _media_linea(lf):
                    continue
                va = (ah.get(lado_a) or {}).get(f"{-lf:+.1f}".replace("+-", "-")) or (ah.get(lado_a) or {}).get(f"{-lf:g}")
                if va is None:
                    for kk, vv in (ah.get(lado_a) or {}).items():
                        try:
                            if abs(float(kk) + lf) < 1e-9:
                                va = vv
                        except ValueError:
                            pass
                ch, ca = _f(vh), _f(va or {})
                if ch and ca:
                    ph, s = _nov2(ch, ca)
                    if PAR_MIN <= s <= PAR_MAX:
                        put(("ah", f"home {lf:+g}"), casa, ch, ph, "asian_handicap")
                        put(("ah", f"away {-lf:+g}"), casa, ca, 1 - ph, "asian_handicap")
        # Totales .5 (total, 1.ª parte, córners, tarjetas)
        for mk, merc, etq in (("first_half_total_goals", "goles_1t", "1.ª parte: {s} de {l} goles"), ("match_corners", "corners", "{s} de {l} córners"),
                              ("total_cards", "tarjetas", "{s} de {l} tarjetas")):
            for linea, v in (m.get(mk) or {}).items():
                try:
                    lf = float(linea)
                except ValueError:
                    continue
                if not _media_linea(lf):
                    continue
                o, u = _f(v.get("over") or {}), _f(v.get("under") or {})
                if o and u:
                    po, s = _nov2(o, u)
                    if PAR_MIN <= s <= PAR_MAX:
                        put((merc, f"over {linea}"), casa, o, po, mk)
                        put((merc, f"under {linea}"), casa, u, 1 - po, mk)
        # Totales por equipo (goles y córners)
        for mk, merc in (("team_total_goals", "goles_equipo"), ("team_corners", "corners_equipo")):
            for lado, tabla in (m.get(mk) or {}).items():
                if lado not in ("home", "away"):
                    continue
                for linea, v in tabla.items():
                    try:
                        lf = float(linea)
                    except ValueError:
                        continue
                    if not _media_linea(lf):
                        continue
                    o, u = _f(v.get("over") or {}), _f(v.get("under") or {})
                    if o and u:
                        po, s = _nov2(o, u)
                        if PAR_MIN <= s <= PAR_MAX:
                            put((merc, f"{lado} over {linea}"), casa, o, po, mk)
                            put((merc, f"{lado} under {linea}"), casa, u, 1 - po, mk)
        # 1X2 de la 1.ª parte
        fh = m.get("first_half_result")
        if fh and all(_f(fh.get(k) or {}) for k in ("home", "draw", "away")):
            h, d_, a = (_f(fh[k]) for k in ("home", "draw", "away"))
            ps, s = _nov3(h, d_, a)
            if 1.0 <= s <= 1.30:
                for k, c, p in zip(("home", "draw", "away"), (h, d_, a), ps):
                    put(("1x2_1t", k), casa, c, p, "first_half_result")
        # BTTS 1.ª parte
        bt = m.get("btts_first_half")
        if bt:
            y, n = _f(bt.get("yes") or {}), _f(bt.get("no") or {})
            if y and n:
                py, s = _nov2(y, n)
                if PAR_MIN <= s <= PAR_MAX:
                    put(("btts_1t", "yes"), casa, y, py, "btts_first_half")
                    put(("btts_1t", "no"), casa, n, 1 - py, "btts_first_half")

    hora = datetime.strptime(match["utc_date"][:16], "%Y-%m-%dT%H:%M").replace(tzinfo=timezone.utc).astimezone(CARACAS).strftime("%d-%m %H:%M")
    patas = []
    for (mer, sel), d in acum.items():
        minimo = 2 if d["api"] in POCAS_CASAS else 3
        if len(set(d["casas"])) < minimo:
            continue
        cuota = statistics.median(d["cuotas"])
        p = sum(d["ps"]) / len(d["ps"])
        patas.append({"match_id": match["id"], "partido": f"{local} – {visit}", "utc": match["utc_date"], "hora_caracas": hora,
                      "mercado": mer, "seleccion": nombre(mer, sel, local, visit), "cuota": round(cuota, 3), "p": round(p, 4),
                      "n_casas": len(set(d["casas"])), "cuota_min": round(min(d["cuotas"]), 3), "cuota_max": round(max(d["cuotas"]), 3),
                      "valor": round(p * cuota, 4), "mercado_api": d["api"]})
    return patas


def nombre(mer, sel, local, visit):
    if mer == "ah":
        lado, h = sel.split()
        return f"Hándicap {local if lado == 'home' else visit} {h}"
    if mer in ("goles_1t", "corners", "tarjetas"):
        lado, linea = sel.split()
        s = "Más" if lado == "over" else "Menos"
        return {"goles_1t": f"1.ª parte: {s} de {linea} goles", "corners": f"{s} de {linea} córners", "tarjetas": f"{s} de {linea} tarjetas"}[mer]
    if mer in ("goles_equipo", "corners_equipo"):
        lado, ou, linea = sel.split()
        eq = local if lado == "home" else visit
        s = "Más" if ou == "over" else "Menos"
        return f"{eq}: {s} de {linea} " + ("goles" if mer == "goles_equipo" else "córners")
    if mer == "1x2_1t":
        return {"home": f"1.ª parte: gana {local}", "draw": "1.ª parte: empate", "away": f"1.ª parte: gana {visit}"}[sel]
    if mer == "btts_1t":
        return "1.ª parte: ambos anotan " + ("sí" if sel == "yes" else "no")
    return sel
