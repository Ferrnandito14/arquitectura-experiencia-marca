#!/usr/bin/env python3
"""Modelo propio de CONTEOS (córners y tarjetas) por equipo y total (Fase 4). No usa cuotas.

Idea: cada equipo tiene un conteo «propio» (lo que produce) y uno «concedido» (lo que provoca en el rival), medidos en sus últimos partidos y encogidos hacia la media de la liga
(`k` partidos virtuales); el conteo esperado del equipo es media_liga × ataque × defensa_rival (con ventaja local medida en la liga). Para tarjetas se multiplica por un factor del árbitro
(media del árbitro encogida hacia la de la liga). La cola se calcula con una Binomial Negativa cuya dispersión sale de la varianza de la LIGA (método de momentos); si no hay sobredispersión,
Poisson. Tarjetas = puntos con la regla de la casa (amarilla 1, roja 2).

Filas de entrada orientadas al equipo: {"venue": "local"|"visitante", "own": int|None, "opp": int|None}. Funciones puras (sin red)."""
import math

MAX_K = 80


def _nb_pmf_list(mean, r, kmax=MAX_K):
    """pmf de Binomial Negativa (media `mean`, dispersión r) o Poisson si r es None."""
    if mean <= 0:
        return [1.0] + [0.0] * kmax
    if r is None:
        p = [math.exp(-mean)]
        for k in range(1, kmax + 1):
            p.append(p[-1] * mean / k)
        return p
    q = r / (r + mean)
    p = [q ** r]
    for k in range(kmax):
        p.append(p[-1] * (k + r) / (k + 1) * (1 - q))
    return p


def p_over(mean, r, line):
    """P(X > line) para una línea de media (x.5)."""
    pm = _nb_pmf_list(mean, r)
    return max(0.0, min(1.0, 1.0 - sum(pm[: int(math.floor(line)) + 1])))


def dispersion(values):
    """Parámetro r de la Binomial Negativa por momentos (r = m²/(var−m)); None si no hay sobredispersión o faltan datos."""
    v = [x for x in values if x is not None]
    if len(v) < 20:
        return None
    m = sum(v) / len(v)
    var = sum((x - m) ** 2 for x in v) / (len(v) - 1)
    return None if var <= m * 1.02 or m <= 0 else m * m / (var - m)


def league_stats(match_rows):
    """match_rows = [(home_count, away_count)] de la liga (solo partidos ANTERIORES). Devuelve (media por equipo, ventaja local, dispersión del total) o None si no hay datos."""
    mr = [t for t in match_rows if t is not None and None not in t]
    if len(mr) < 20:
        return None
    mh, ma = sum(t[0] for t in mr) / len(mr), sum(t[1] for t in mr) / len(mr)
    mu = (mh + ma) / 2
    return {"mu": mu, "adv": min(max(mh / ma, 0.7), 1.6) if ma > 0 else 1.0, "r_total": dispersion([t[0] + t[1] for t in mr]), "r_team": dispersion([x for t in mr for x in t]), "n": len(mr)}


def strengths(rows, mu, k=8):
    rows = [r for r in rows if r.get("own") is not None and r.get("opp") is not None]
    n = len(rows)
    if n == 0 or mu <= 0:
        return 1.0, 1.0
    own = sum(r["own"] for r in rows) / n
    opp = sum(r["opp"] for r in rows) / n
    return ((n * own + k * mu) / (n + k)) / mu, ((n * opp + k * mu) / (n + k)) / mu


def referee_factor(ref_mean, ref_n, league_total_mean, k=10):
    """Multiplicador del árbitro: su media de total por partido encogida hacia la de la liga ((n·media + k·liga)/(n+k) / liga). 1.0 si no hay árbitro o datos."""
    if ref_mean is None or not ref_n or not league_total_mean:
        return 1.0
    return ((ref_n * ref_mean + k * league_total_mean) / (ref_n + k)) / league_total_mean


def expected_counts(rows_home, rows_away, stats, ref_factor=1.0, k=8):
    ah, dh = strengths(rows_home, stats["mu"], k)
    aa, da = strengths(rows_away, stats["mu"], k)
    base = stats["mu"] * ref_factor
    return base * math.sqrt(stats["adv"]) * ah * da, (base / math.sqrt(stats["adv"])) * aa * dh


def model_probs(name, rows_home, rows_away, stats, total_lines, team_lines, ref_factor=1.0, k=8):
    """{f'{name}_total_over_{L}', f'{name}_home_over_{L}', f'{name}_away_over_{L}'} con name = 'corners' | 'cards'. `stats` = league_stats(...) (None => sin modelo)."""
    if not stats:
        return {}
    mh, ma = expected_counts(rows_home, rows_away, stats, ref_factor, k)
    out = {f"{name}_mean_home": round(mh, 3), f"{name}_mean_away": round(ma, 3)}
    for L in total_lines:
        out[f"{name}_total_over_{L}"] = p_over(mh + ma, stats["r_total"], L)
    for L in team_lines:
        out[f"{name}_home_over_{L}"] = p_over(mh, stats["r_team"], L)
        out[f"{name}_away_over_{L}"] = p_over(ma, stats["r_team"], L)
    return out


CORNER_TOTAL = [6.5 + i for i in range(9)]
CORNER_TEAM = [2.5 + i for i in range(7)]
CARD_TOTAL = [1.5 + i for i in range(9)]
CARD_TEAM = [0.5 + i for i in range(6)]

SOT_TOTAL = [3.5 + i for i in range(12)]
SOT_TEAM = [1.5 + i for i in range(9)]
SHOTS_TOTAL = [14.5 + i for i in range(19)]
SHOTS_TEAM = [6.5 + i for i in range(13)]
