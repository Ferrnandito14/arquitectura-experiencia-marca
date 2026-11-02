#!/usr/bin/env python3
"""Tickets ×4 con los PRECIOS REALES de la casa (leídos por la sesión local en el navegador) y la probabilidad del mercado.

Entrada:  <run>/pool/patas_casa.json (patas candidatas), <run>/pool/casa_precios.json ({"<n>": {"disponible": bool, "cuota": float, "mercado": "..."}}, n = posición 1..N en patas_casa.json),
          <run>/agentes/auditor.json y <run>/pool/modelo_ligero.json (filtros).
Reglas: se excluyen patas que la casa no ofrece, las que el auditor descartó (o degradó con severidad alta) y las que el modelo ligero contradice por ≥15 pp.
La probabilidad de cada pata es la del mercado sin margen (TheStatsAPI); la cuota es la de la casa; EV = P × cuota total con bono − 1. Probabilidad conjunta suponiendo independencia entre partidos.

Uso:  tickets_casa.py --run runs/2026-11-01 [--bono 1.09] [--top 5]
Salida: <run>/pool/tickets_x4_casa.json"""
import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pool_mercado as pm  # noqa: E402


def filtrar(patas, casa, aud, modelo):
    """Devuelve (candidatas con cuota de la casa, excluidas con motivo)."""
    ok, fuera = [], []
    for i, p in enumerate(patas, 1):
        k = p["match_id"] + "|" + p["seleccion"]
        c = casa.get(str(i))
        if not c or not c.get("disponible") or not c.get("cuota"):
            fuera.append((p["partido"], p["seleccion"], "la casa no la ofrece o no se leyó"))
            continue
        a = aud.get(k, {})
        if a.get("recomendacion") == "descartar" or (a.get("recomendacion") == "degradar" and a.get("severidad") == "alta"):
            fuera.append((p["partido"], p["seleccion"], f"auditor: {a.get('recomendacion')} ({a.get('severidad')})"))
            continue
        mo = modelo.get(k, {})
        if mo.get("discrepa") and mo.get("dif", 0) < 0:
            fuera.append((p["partido"], p["seleccion"], f"el modelo ligero la ve {abs(mo['dif']) * 100:.0f} pp por debajo del mercado"))
            continue
        q = dict(p)
        q["cuota_ref"] = p["cuota"]
        q["cuota"] = float(c["cuota"])
        q["valor"] = q["p"] * q["cuota"]
        q["mercado_casa"] = c.get("mercado", "")
        q["cuenta_bono"] = c.get("cuenta_bono")
        q["auditor"] = a.get("recomendacion", "")
        q["p_modelo"] = mo.get("p_modelo")
        ok.append(q)
    return ok, fuera


ESCALA_BONO = {0: 0.0, 1: 0.0, 2: 0.0, 3: 0.04, 4: 0.05, 5: 0.07, 6: 0.09, 7: 0.10}   # medida el 1-nov en el cupón de la casa del usuario (patas «válidas»)


def bono_ticket(patas):
    """Bono esperado: solo cuentan las patas probadas como válidas (cuenta_bono True); sin probar = no cuenta (criterio prudente)."""
    n = sum(1 for p in patas if p.get("cuenta_bono") is True)
    return n, ESCALA_BONO.get(min(n, 7), 0.10)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--run", required=True)
    ap.add_argument("--bono", type=float, default=1.09)
    ap.add_argument("--top", type=int, default=5)
    ap.add_argument("--prod-min", type=float, default=3.7)
    ap.add_argument("--prod-max", type=float, default=4.6)
    a = ap.parse_args(argv)
    R = os.path.join(a.run, "pool")
    patas = json.load(open(os.path.join(R, "patas_casa.json")))
    casa = json.load(open(os.path.join(R, "casa_precios.json")))
    aud = {p["key"]: p for p in json.load(open(os.path.join(a.run, "agentes", "auditor.json")))["patas"]}
    modelo = json.load(open(os.path.join(R, "modelo_ligero.json")))
    ok, fuera = filtrar(patas, casa, aud, modelo)
    res = {}
    for n in (3, 4, 5):
        lista = pm.buscar(ok, 1.20, 2.10, a.prod_min, a.prod_max, n, n, 400, max_overs=1)
        lista = pm.diversificar(lista, 2, a.top, max_rep=2)
        for t in lista:
            nval, bono = bono_ticket(t["patas"])
            t["patas_validas_bono"] = nval
            t["bono"] = bono
            t["cuota_con_bono"] = round(t["cuota_base"] * (1 + bono), 3)
            t["ev_sin_bono"] = round(t["p_ganar"] * t["cuota_base"] - 1, 4)
            t["ev_casa"] = round(t["p_ganar"] * t["cuota_con_bono"] - 1, 4)
        res[f"{n} patas"] = lista
    json.dump({"candidatas": len(ok), "excluidas": fuera, "tickets": res}, open(os.path.join(R, "tickets_x4_casa.json"), "w"), ensure_ascii=False, indent=1)
    print(f"{len(ok)} patas candidatas con precio de la casa; {len(fuera)} excluidas")
    for g, v in res.items():
        print(g, len(v), (f"mejor P={v[0]['p_ganar']:.3f} cuota {v[0]['cuota_base']} EV {v[0]['ev_casa']:+.3f}" if v else ""))
    return 0


if __name__ == "__main__":
    sys.exit(main())
