#!/usr/bin/env python3
"""Lista ANCHA reproducible del día (sustituye el filtro estrecho p_suav>=0.75 / cuota 1.22-1.50 / máx 2 por partido).

Uso:  lista_ancha.py --run runs/2026-11-05 [--p-min 0.65] [--cuota-min 1.20] [--cuota-max 2.10] [--casas-min 2] [--lotes 4]
Cruza pool/est_patas.json (estadística) con pool/patas.json (precio solo como medida), escribe pool/est_shortlist_ancha.json y
pool/est_ancha_lote<k>.json (partidos repartidos entre lotes para los deportivos en paralelo)."""
import argparse
import json
import os


def construir(run, p_min=0.65, c_min=1.20, c_max=2.10, casas=2):
    pa = json.load(open(os.path.join(run, "pool", "patas.json")))
    precios = [x for v in pa.values() if isinstance(v, list) for x in v]
    idx = {(x["match_id"], x["seleccion"]): x for x in precios}
    est = json.load(open(os.path.join(run, "pool", "est_patas.json")))
    est = est if isinstance(est, list) else est["patas"]
    out = []
    for e in est:
        x = idx.get((e["match_id"], e["seleccion"]))
        if x and e["p_suav"] >= p_min and c_min <= x["cuota"] <= c_max and x["n_casas"] >= casas:
            out.append({**e, "cuota_ref": x["cuota"], "p_mercado": x["p"], "n_casas": x["n_casas"]})
    out.sort(key=lambda z: (z["hora_caracas"], z["partido"]))
    return out, len(est)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--run", required=True)
    ap.add_argument("--p-min", type=float, default=0.65)
    ap.add_argument("--cuota-min", type=float, default=1.20)
    ap.add_argument("--cuota-max", type=float, default=2.10)
    ap.add_argument("--casas-min", type=int, default=2)
    ap.add_argument("--lotes", type=int, default=4)
    a = ap.parse_args(argv)
    out, n_est = construir(a.run, a.p_min, a.cuota_min, a.cuota_max, a.casas_min)
    json.dump(out, open(os.path.join(a.run, "pool", "est_shortlist_ancha.json"), "w"), ensure_ascii=False, indent=0)
    partidos = sorted({z["match_id"] for z in out})
    lotes = [[] for _ in range(a.lotes)]
    for i, mid in enumerate(partidos):
        lotes[i % a.lotes].append(mid)
    for i, l in enumerate(lotes, 1):
        json.dump([z for z in out if z["match_id"] in l], open(os.path.join(a.run, "pool", f"est_ancha_lote{i}.json"), "w"), ensure_ascii=False, indent=0)
    print(f"{len(out)} patas de {len(partidos)} partidos (de {n_est} con estadística) en {a.lotes} lotes")


if __name__ == "__main__":
    main()
