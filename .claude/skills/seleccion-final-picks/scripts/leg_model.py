#!/usr/bin/env python3
"""Modelo pata por pata v0 (partido a partido): probabilidad de cada mercado de goles/resultado desde las fuerzas de ataque y defensa de los DOS equipos (muestra reciente,
encogida hacia la media de la competición) con goles Poisson independientes. NO usa la cuota para fijar la probabilidad: el mercado es un prior que se compara, no el juez.
Funciones puras (sin red) para poder probarlas offline."""
import math

MAX_G = 12


def _pois(lmb):
    p = [math.exp(-lmb)]
    for k in range(1, MAX_G + 1):
        p.append(p[-1] * lmb / k)
    return p


def grid(lh, la):
    ph, pa = _pois(lh), _pois(la)
    return [[ph[i] * pa[j] for j in range(MAX_G + 1)] for i in range(MAX_G + 1)]


def league_means(rows_by_team):
    """rows_by_team: lista de filas de historial (gf, ga, venue) de varios equipos de la MISMA competición. Devuelve (mu, ventaja_local) con mu = goles por equipo y partido."""
    gf = [r["gf"] for rs in rows_by_team for r in rs if r.get("gf") is not None]
    if not gf:
        return None, 1.0
    mu = sum(gf) / len(gf)
    h = [r["gf"] for rs in rows_by_team for r in rs if r.get("venue") == "local"]
    v = [r["gf"] for rs in rows_by_team for r in rs if r.get("venue") == "visitante"]
    adv = (sum(h) / len(h)) / (sum(v) / len(v)) if h and v and sum(v) > 0 else 1.0
    return mu, min(max(adv, 0.85), 1.5)


def strengths(rows, mu, k=8):
    """(ataque, defensa) relativos a la media, con encogimiento: (n·media + k·mu)/(n + k) / mu."""
    rows = [r for r in rows if r.get("gf") is not None and r.get("ga") is not None]
    n = len(rows)
    if n == 0 or not mu:
        return 1.0, 1.0
    gf = sum(r["gf"] for r in rows) / n
    ga = sum(r["ga"] for r in rows) / n
    return ((n * gf + k * mu) / (n + k)) / mu, ((n * ga + k * mu) / (n + k)) / mu


def expected_goals(form_home, form_away, mu, adv, k=8):
    ah, dh = strengths(form_home, mu, k)
    aa, da = strengths(form_away, mu, k)
    base = mu * math.sqrt(adv)
    lh = base * ah * da
    la = (mu / math.sqrt(adv)) * aa * dh
    return lh, la


def p_over(g, line):
    return sum(g[i][j] for i in range(MAX_G + 1) for j in range(MAX_G + 1) if i + j > line)


def p_btts(g):
    return sum(g[i][j] for i in range(1, MAX_G + 1) for j in range(1, MAX_G + 1))


def p_1x2(g):
    h = sum(g[i][j] for i in range(MAX_G + 1) for j in range(MAX_G + 1) if i > j)
    d = sum(g[i][i] for i in range(MAX_G + 1))
    return h, d, 1 - h - d


def p_handicap(g, side, line):
    """Hándicap asiático +line (línea .5) para 'home' o 'away'."""
    return sum(g[i][j] for i in range(MAX_G + 1) for j in range(MAX_G + 1) if ((i + line > j) if side == "home" else (j + line > i)))


def model_probs(form_home, form_away, mu, adv, k=8):
    lh, la = expected_goals(form_home, form_away, mu, adv, k)
    g = grid(lh, la)
    h, d, a = p_1x2(g)
    out = {"lambda_local": round(lh, 3), "lambda_visit": round(la, 3), "btts": p_btts(g), "p1": h, "px": d, "p2": a, "1x": h + d, "x2": d + a}
    for ln in (0.5, 1.5, 2.5, 3.5, 4.5, 5.5):
        out[f"over_{ln}"] = p_over(g, ln)
    return out
