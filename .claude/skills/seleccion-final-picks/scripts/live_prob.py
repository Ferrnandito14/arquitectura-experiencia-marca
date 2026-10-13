#!/usr/bin/env python3
"""Probabilidad EN VIVO aproximada por pata (APROXIMACIÓN, no predicción calibrada).
Modelo: goles de cada equipo ~ Poisson con tasas (lam_h, lam_a) AJUSTADAS a las probabilidades sin margen del mercado previo (1X2 y más/menos de 2.5);
en vivo se condiciona al marcador actual y se escala la tasa por el tiempo que queda. No ve lesiones, rojas, ni cambios tácticos. Tarjetas: Poisson con la media
de la muestra y el supuesto (no verificado) de independencia respecto al resultado.
Uso: live_prob.py --run runs/2026-10-13 [--tickets A,C,D]"""
import argparse
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import adapters  # noqa: E402
import common  # noqa: E402
import seguimiento as sg  # noqa: E402

TOTAL_MIN = 95.0


def pois(k, lam):
    return math.exp(-lam) * lam ** k / math.factorial(k)


def dist(lam, n=12):
    return [pois(k, lam) for k in range(n)]


def novig(odds):
    inv = [1 / o for o in odds]
    s = sum(inv)
    return [x / s for x in inv]


def fit(p1x2, pover25):
    """Busca (lh, la) que minimiza el error contra P(1X2) y P(más de 2.5) del mercado."""
    best = None
    for i in range(3, 45):
        for j in range(3, 45):
            lh, la = i / 10, j / 10
            dh, da = dist(lh), dist(la)
            ph = sum(dh[a] * da[b] for a in range(12) for b in range(12) if a > b)
            pd = sum(dh[a] * da[a] for a in range(12))
            pa = 1 - ph - pd
            tot = [sum(dh[a] * da[t - a] for a in range(t + 1)) for t in range(12)]
            po = 1 - sum(tot[:3])
            err = (ph - p1x2[0]) ** 2 + (pd - p1x2[1]) ** 2 + (pa - p1x2[2]) ** 2 + (po - pover25) ** 2
            if best is None or err < best[0]:
                best = (err, lh, la)
    return best[1], best[2]


def minute_of(e):
    s = str(e.get("match_status") or "")
    if s.lower().startswith("half"):
        return 45.0
    s = s.replace("+", "").replace("'", "")
    return float(s) if s.isdigit() else (0.0 if sg.state(e) == "upcoming" else TOTAL_MIN)


def final_dist(h, a, lh, la, frac):
    dh, da = dist(lh * frac), dist(la * frac)
    out = {}
    for x in range(12):
        for y in range(12):
            out[(h + x, a + y)] = out.get((h + x, a + y), 0) + dh[x] * da[y]
    return out


def leg_prob(leg, e, lh, la, mean_cards):
    h, a = sg.score(e)
    st = sg.state(e)
    if h is None or a is None:
        return None, "sin marcador"
    if st == "upcoming":
        h = a = 0
    mn = minute_of(e)
    fin = st == "finished"
    frac = 0.0 if fin else max(0.0, (TOTAL_MIN - mn) / TOTAL_MIN)
    fd = final_dist(h, a, lh, la, frac)
    mk = leg["mercado"]
    if mk == "total":
        w = sum(p for (x, y), p in fd.items() if sg.settle_total(x + y, leg["op"], leg["linea"]) == "win")
        v = sum(p for (x, y), p in fd.items() if sg.settle_total(x + y, leg["op"], leg["linea"]) == "void")
        return w + v, ""
    if mk == "handicap":
        return sum(p for (x, y), p in fd.items() if sg.settle_handicap(x, y, leg["lado"], leg["linea"]) in ("win", "void")), ""
    if mk == "1x2":
        return sum(p for (x, y), p in fd.items() if (x > y if leg["lado"] == "home" else y > x)), ""
    if mk == "btts":
        return sum(p for (x, y), p in fd.items() if x > 0 and y > 0), ""
    if mk == "1x2_1t":
        hh, ha = sg.half_score(e)
        if hh is not None and (fin or mn > 45):
            return float(ha > hh if leg["lado"] == "away" else hh > ha), "1.ª mitad cerrada"
        h1, a1 = (hh, ha) if hh is not None else (h, a)
        f1 = max(0.0, (45.0 - mn) / 45.0)
        d1 = final_dist(h1, a1, 0.45 * lh, 0.45 * la, f1)
        return sum(p for (x, y), p in d1.items() if (y > x if leg["lado"] == "away" else x > y)), "1.ª mitad ≈45 % de los goles (supuesto)"
    if mk == "cards_dc":
        pts = adapters._card_points(e) or (0, 0)
        cur = pts[0] + pts[1]
        need = leg["min_puntos"] - cur
        lam = max(mean_cards * frac, 1e-9)
        pc = 1.0 if need <= 0 else 1 - sum(pois(k, lam) for k in range(int(need)))
        pdc = sum(p for (x, y), p in fd.items() if x >= y)
        return pc * pdc, f"tarjetas {cur} pts; independencia supuesta"
    return None, "no soportado"


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", default="runs/2026-10-13")
    ap.add_argument("--tickets", default="A,C,D")
    a = ap.parse_args(argv)
    key = adapters.apif_key()
    client = common.Client(os.path.join(a.run, "cache"), os.path.join(a.run, "sources", "consultas.jsonl"), policy=common.Policy(), min_interval=1.0, ttl=20)
    mx = common.read_json(os.path.join(a.run, "matrix.json"))["matches"]
    spec = common.read_json(os.path.join(a.run, "seguimiento", "tickets_abiertos.json"))["tickets"]
    cache, params = {}, {}
    lines = ["| Ticket | Partido | Pata | Marcador | Cuota | Prob. que se cumpla (aprox.) | Estado |", "|---|---|---|---|---|---|---|"]
    joint = []
    for t in spec:
        if t["id"] not in a.tickets.split(","):
            continue
        ps = []
        for l in t["patas"]:
            if l["apif"] not in cache:
                d = adapters.apif_call(client, key, action="get_events", match_id=l["apif"], timezone="UTC")
                cache[l["apif"]] = d[0]
            e = cache[l["apif"]]
            if l["mid"] not in params:
                ap_ = mx[l["mid"]].get("api_prices") or {}
                p12 = novig(ap_["resultado.1x2"]["cuotas_medianas"])
                po = novig(ap_["goles.over_2_5"]["cuotas_medianas"])[0]
                rows = mx[l["mid"]]["form"]["local"] + mx[l["mid"]]["form"]["visitante"]
                cs = [sum(r["cards_pts"]) for r in rows if r.get("cards_pts") and r["cards_pts"][0] is not None]
                params[l["mid"]] = (*fit(p12, po), (sum(cs) / len(cs)) if cs else 4.0)
            lh, la, mc = params[l["mid"]]
            p, note = leg_prob(l, e, lh, la, mc)
            st, det = sg.eval_leg(l, e)
            h, a_ = sg.score(e)
            mk = {"total": f"{'Más' if l.get('op') == 'over' else 'Menos'} de {l.get('linea')} goles", "handicap": f"Hándicap Brugge +{l.get('linea')}", "1x2": "Gana " + ("local" if l.get("lado") == "home" else "visitante"),
                  "1x2_1t": "Gana el visitante 1.ª mitad", "btts": "Ambos anotan", "cards_dc": "Tarjetas >2.5 + Atlético o empate"}[l["mercado"]]
            ps.append(p)
            lines.append(f"| {t['id']} | {l['partido']} | {mk} | {h}-{a_} ({e.get('match_status')}) | {l['cuota']} | {'—' if p is None else f'{p*100:.0f} %'} | {st} |")
        if all(x is not None for x in ps):
            joint.append((t["id"], math.prod(ps)))
    print("\n".join(lines))
    print("\nCombinadas completas (producto, suponiendo partidos independientes): " + " · ".join(f"{i}: {p*100:.1f} %" for i, p in joint))
    return 0


if __name__ == "__main__":
    sys.exit(main())
