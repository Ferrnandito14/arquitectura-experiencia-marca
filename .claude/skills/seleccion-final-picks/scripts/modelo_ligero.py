#!/usr/bin/env python3
"""Modelo LIGERO v0 (Poisson) para contrastar las patas finalistas con el mercado. NO VALIDADO.

λ_local = (goles a favor del local + goles en contra del visitante) / 2 ; λ_visita = (a favor del visitante + en contra del local) / 2,
con las medias de los últimos 8 partidos de cada equipo (dossier de TheStatsAPI). Sin pesos arbitrarios: promedio simple de ataque propio y defensa rival.
Devuelve P(pata) para: doble oportunidad con empate, «sin empate» (12), más/menos de una línea de goles.
Sirve solo como contraste: si |p_modelo − p_mercado| ≥ 15 pp (umbral del proyecto) se marca «discrepa».

Uso:  modelo_ligero.py --run runs/2026-11-01"""
import argparse
import json
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import justificacion_patas as jp  # noqa: E402

UMBRAL_DISCREPA = 0.15
MAXG = 14


def pois(l, k):
    return math.exp(-l) * l ** k / math.factorial(k)


def lambdas(local, visita):
    rl, rv = local["resumen"], visita["resumen"]
    return (rl["gf_medio"] + rv["gc_medio"]) / 2, (rv["gf_medio"] + rl["gc_medio"]) / 2


def p_leg(tipo, det, lh, la):
    ph = [pois(lh, i) for i in range(MAXG)]
    pa = [pois(la, i) for i in range(MAXG)]
    gana_l = sum(ph[i] * pa[j] for i in range(MAXG) for j in range(MAXG) if i > j)
    gana_v = sum(ph[i] * pa[j] for i in range(MAXG) for j in range(MAXG) if i < j)
    emp = max(0.0, 1 - gana_l - gana_v)
    if tipo == "dc_local":
        return gana_l + emp
    if tipo == "dc_visita":
        return gana_v + emp
    if tipo == "sin_empate":
        return gana_l + gana_v
    if tipo in ("over", "under"):
        tot = lh + la
        under = sum(pois(tot, k) for k in range(int(math.floor(det)) + 1))
        return 1 - under if tipo == "over" else under
    return None


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--run", required=True)
    a = ap.parse_args(argv)
    fin = json.load(open(os.path.join(a.run, "pool", "finalistas.json")))["patas"]
    doss = {p["key"]: p for p in json.load(open(os.path.join(a.run, "dossier", "dossier_finalistas.json")))["patas"]}
    matches = {m["id"]: m for m in json.load(open(os.path.join(a.run, "thestatsapi", "matches.json")))}
    out = {}
    for p in fin:
        k = p["match_id"] + "|" + p["seleccion"]
        m = matches[p["match_id"]]
        tipo, det = jp.clasificar(p["seleccion"], m["home_team"]["name"], m["away_team"]["name"])
        f = doss[k]
        lh, la = lambdas(f["local"], f["visitante"])
        pm_ = p_leg(tipo, det, lh, la)
        if pm_ is None:
            continue
        dif = pm_ - p["p"]
        out[k] = {"p_modelo": round(pm_, 4), "p_mercado": p["p"], "dif": round(dif, 4), "lambda_local": round(lh, 2), "lambda_visita": round(la, 2),
                  "discrepa": abs(dif) >= UMBRAL_DISCREPA, "modelo": "poisson_ultimos8_v0_no_validado"}
    json.dump(out, open(os.path.join(a.run, "pool", "modelo_ligero.json"), "w"), ensure_ascii=False, indent=1)
    print(len(out), "patas;", sum(1 for v in out.values() if v["discrepa"]), "discrepan ≥15 pp")
    return 0


if __name__ == "__main__":
    sys.exit(main())
