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


def p_team_over(g, side, line):
    """P(goles del equipo > line): side = 'home' | 'away'."""
    return sum(g[i][j] for i in range(MAX_G + 1) for j in range(MAX_G + 1) if ((i > line) if side == "home" else (j > line)))


HANDICAP_HALF = (-2.5, -1.5, -0.5, 0.5, 1.5, 2.5)
TEAM_GOAL_LINES = (0.5, 1.5, 2.5)
HALF_LINES = (0.5, 1.5, 2.5)


def half_share(form_home, form_away, min_rows=6):
    """Fracción de los goles que cae en la 1.ª parte, medida en las filas de historial de AMBOS equipos (`ht_goals` vs resultado final). None si no hay datos suficientes."""
    ht = ft = n = 0
    for r in list(form_home) + list(form_away):
        t = r.get("ht_goals")
        if t and None not in t and r.get("gf") is not None and r.get("ga") is not None:
            ht += t[0] + t[1]
            ft += r["gf"] + r["ga"]
            n += 1
    return (ht / ft) if n >= min_rows and ft > 0 else None


def model_probs(form_home, form_away, mu, adv, k=8, share=None):
    """Probabilidades propias del partido (Poisson independiente con fuerzas de ataque/defensa encogidas). `share` = fracción de goles de la 1.ª parte (si se mide);
    sin ella no se calculan los mercados de 1.ª parte. NUNCA usa cuotas."""
    lh, la = expected_goals(form_home, form_away, mu, adv, k)
    g = grid(lh, la)
    h, d, a = p_1x2(g)
    out = {"lambda_local": round(lh, 3), "lambda_visit": round(la, 3), "btts": p_btts(g), "p1": h, "px": d, "p2": a, "1x": h + d, "x2": d + a, "12": h + a,
           "dnb_home": h / (h + a) if h + a else 0.5, "dnb_away": a / (h + a) if h + a else 0.5}
    for ln in (0.5, 1.5, 2.5, 3.5, 4.5, 5.5):
        out[f"over_{ln}"] = p_over(g, ln)
    for ln in TEAM_GOAL_LINES:
        out[f"home_over_{ln}"] = p_team_over(g, "home", ln)
        out[f"away_over_{ln}"] = p_team_over(g, "away", ln)
    for L in HANDICAP_HALF:                                # hándicap asiático de media línea: clave con la línea DEL PROPIO lado (como en el catálogo)
        out[f"ah_home_{L:+.1f}"] = p_handicap(g, "home", L)
        out[f"ah_away_{-L:+.1f}"] = p_handicap(g, "away", -L)
    if share is not None:
        g1 = grid(lh * share, la * share)
        h1, d1, a1 = p_1x2(g1)
        out.update({"ht_p1": h1, "ht_px": d1, "ht_p2": a1, "half_share": share})
        for ln in HALF_LINES:
            out[f"ht_over_{ln}"] = p_over(g1, ln)
    return out
