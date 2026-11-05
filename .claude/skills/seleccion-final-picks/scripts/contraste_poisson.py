#!/usr/bin/env python3
"""Contraste PROPIO con Poisson para mercados de goles, con muestras de 15 partidos y desglose casa/visita.

Cierra el vacío detectado el 4-nov: el deportivo estima con 8 partidos (p_dep) y sobreestima patas 'saturadas'; el auditor usó 15-16.
Uso:  contraste_poisson.py --memoria data/memoria_equipos/partidos.jsonl --local TM_ID --visita TM_ID [--n 15]
Salida (JSON): goles esperados de cada equipo (media de ataque propio y defensa rival, con localía si hay >=4 partidos de esa condición),
P de totales Más/Menos 0.5..5.5, P de que cada equipo marque 1+, 2+, BTTS, y frecuencias empíricas n=15 para comparar.
No usa cuotas. Es un contraste, no sustituye al deportivo ni al auditor."""
import argparse
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
MEM = os.path.join(ROOT, "data", "memoria_equipos", "partidos.jsonl")


def _pois(l, k):
    return math.exp(-l) * l ** k / math.factorial(k)


def filas(d, tid, n):
    xs = sorted((r for r in d.values() if tid in (r["h_id"], r["a_id"])), key=lambda r: r["utc"], reverse=True)[:n]
    out = []
    for r in xs:
        loc = r["h_id"] == tid
        gf, gc = (r["gh"], r["ga"]) if loc else (r["ga"], r["gh"])
        out.append((loc, gf, gc))
    return out


def _media(rs, i, cond=None, minimo=4):
    sel = [r for r in rs if cond is None or r[0] == cond]
    if cond is not None and len(sel) < minimo:
        sel = rs
    return sum(r[i] for r in sel) / len(sel) if sel else 0.0


def contraste(d, local_id, visita_id, n=15):
    fl, fv = filas(d, local_id, n), filas(d, visita_id, n)
    if len(fl) < 6 or len(fv) < 6:
        return {"error": "muestra insuficiente (<6 partidos)", "n_local": len(fl), "n_visita": len(fv)}
    lam_l = (_media(fl, 1, True) + _media(fv, 2, False)) / 2
    lam_v = (_media(fv, 1, False) + _media(fl, 2, True)) / 2
    tot = lam_l + lam_v
    res = {"n_local": len(fl), "n_visita": len(fv), "lambda_local": round(lam_l, 3), "lambda_visita": round(lam_v, 3), "lambda_total": round(tot, 3)}
    res["menos"] = {str(l): round(sum(_pois(tot, k) for k in range(int(l + 0.5))), 4) for l in (0.5, 1.5, 2.5, 3.5, 4.5, 5.5)}
    res["mas"] = {k: round(1 - v, 4) for k, v in res["menos"].items()}
    res["local_marca_1+"] = round(1 - math.exp(-lam_l), 4)
    res["visita_marca_1+"] = round(1 - math.exp(-lam_v), 4)
    res["btts"] = round((1 - math.exp(-lam_l)) * (1 - math.exp(-lam_v)), 4)
    res["empirico"] = {
        "local_marco": f"{sum(1 for r in fl if r[1] > 0)}/{len(fl)}", "visita_marco": f"{sum(1 for r in fv if r[1] > 0)}/{len(fv)}",
        "total<=4": f"{sum(1 for r in fl if r[1] + r[2] <= 4)}/{len(fl)} y {sum(1 for r in fv if r[1] + r[2] <= 4)}/{len(fv)}",
        "total>=2": f"{sum(1 for r in fl if r[1] + r[2] >= 2)}/{len(fl)} y {sum(1 for r in fv if r[1] + r[2] >= 2)}/{len(fv)}"}
    res["nota"] = "Poisson independiente: ignora correlación, rotación y estado del partido; contraste, no veredicto."
    return res


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--memoria", default=MEM)
    ap.add_argument("--local", required=True)
    ap.add_argument("--visita", required=True)
    ap.add_argument("--n", type=int, default=15)
    a = ap.parse_args(argv)
    sys.path.insert(0, HERE)
    import memoria_equipos as me
    d = me.cargar(a.memoria)
    print(json.dumps(contraste(d, a.local, a.visita, a.n), ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
