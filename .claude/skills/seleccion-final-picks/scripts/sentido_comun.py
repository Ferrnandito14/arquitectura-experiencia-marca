#!/usr/bin/env python3
"""Chequeo de SENTIDO COMÚN de los datos del paquete (reglas fijas, sin agente ni tokens).

Detecta lo que los agentes hallaban a mano: cuotas imposibles o planas, escaleras de líneas sin lógica,
brechas extremas modelo-mercado y partidos que no están programados. No decide nada: deja banderas con la regla
y el detalle para que verificador y auditor las traten como HECHOS.

Reglas:
  par_imposible       par complementario con suma de probabilidades implícitas < 0.98 (arbitraje) o > 1.25.
  cuota_plana         over y under de la misma línea con la misma cuota (par sin información).
  cuota_repetida      la misma cuota en 2+ líneas distintas de una misma escalera (over o under).
  escalera_no_monotona  en una escalera over la cuota baja al subir la línea (o al revés en under).
  brecha_extrema      |p_modelo - P de mercado sin margen| >= 40 pp (probable dato defectuoso).
  partido_no_programado  el inventario trae estado APLAZADO/CANCELADO/FINALIZADO/EN_JUEGO.

Uso:  sentido_comun.py --run runs/2026-10-26 [--out RUTA]
Salida: <run>/agentes/sentido_comun.json (banderas por unit_id/entry_id y resumen)."""
import argparse
import json
import os
import sys
from collections import defaultdict

PAR_MIN, PAR_MAX = 0.98, 1.25
BRECHA_EXTREMA = 0.40
ESTADOS_NO_PROGRAMADO = {"APLAZADO", "CANCELADO", "FINALIZADO", "EN_JUEGO"}


def _cuota(e):
    c = (e.get("precio") or {}).get("cuota")
    return float(c) if c else None


def _pmerc(e):
    pm = (e.get("precio") or {}).get("p_mercado")
    p = pm.get("p") if isinstance(pm, dict) else pm
    return float(p) if p is not None else None


def _bandera(unit_id, entry_id, regla, detalle):
    return {"unit_id": unit_id, "entry_id": entry_id, "regla": regla, "detalle": detalle}


def _pares(entradas):
    """Pares complementarios (id_a, id_b) dentro de una unidad."""
    por_id = {e["id"]: e for e in entradas}
    vistos = set()
    pares = []
    for e in entradas:
        partes = e["id"].split(".")
        otro = None
        if "over" in partes:
            otro = e["id"].replace(".over.", ".under.")
        elif "under" in partes:
            continue
        elif e["id"].endswith(".yes"):
            otro = e["id"][:-4] + ".no"
        elif ".home" in e["id"] and e["id"].count(".") == 2 and e["id"].startswith("resultado.dnb"):
            otro = e["id"].replace(".home", ".away")
        elif e.get("direccion") == "home" and e["id"].startswith(("resultado.ah.", "resultado.ah_entero.")):
            linea = e.get("linea")
            if linea is None:
                continue
            base = e["id"].split(".home.")[0]
            signo = "+" if -linea > 0 else ""
            lado = -linea
            cand = f"{base}.away.{signo}{lado:g}"
            otro = cand if cand in por_id else None
        if otro and otro in por_id and (e["id"], otro) not in vistos:
            vistos.add((e["id"], otro))
            pares.append((e["id"], otro))
    return pares


def revisar_unidad(unidad):
    uid = unidad["unit_id"]
    entradas = unidad["entradas"]
    por_id = {e["id"]: e for e in entradas}
    banderas = []
    for a, b in _pares(entradas):
        ca, cb = _cuota(por_id[a]), _cuota(por_id[b])
        if not ca or not cb:
            continue
        suma = 1 / ca + 1 / cb
        if suma < PAR_MIN or suma > PAR_MAX:
            for eid in (a, b):
                banderas.append(_bandera(uid, eid, "par_imposible", f"{a} {ca} / {b} {cb}: suma de implícitas {suma:.2f}"))
        elif abs(ca - cb) < 1e-9 and ".over." in a:
            for eid in (a, b):
                banderas.append(_bandera(uid, eid, "cuota_plana", f"over y under a {ca}"))
    # tres vías (1X2): resultado.NxN.{home,draw,away}
    tri = defaultdict(dict)
    for e in entradas:
        p = e["id"].split(".")
        if len(p) == 3 and p[2] in ("home", "draw", "away") and p[0] in ("resultado", "primera_parte") and "x" in p[1].lower() and p[1] != "dc":
            tri[(p[0], p[1])][p[2]] = e
    for k, d in tri.items():
        if len(d) == 3 and all(_cuota(x) for x in d.values()):
            s = sum(1 / _cuota(x) for x in d.values())
            if s < PAR_MIN or s > 1.30:
                for x in d.values():
                    banderas.append(_bandera(uid, x["id"], "par_imposible", f"1X2 {'.'.join(k)}: suma de implícitas {s:.2f}"))
    # escaleras over/under
    esc = defaultdict(list)
    for e in entradas:
        p = e["id"].split(".")
        lado = "over" if "over" in p else ("under" if "under" in p else None)
        if lado and e.get("linea") is not None and _cuota(e):
            esc[(".".join(p[:p.index(lado)]), lado)].append((float(e["linea"]), _cuota(e), e["id"]))
    for (pref, lado), pts in esc.items():
        pts.sort()
        distintas = {}
        for lin, c, eid in pts:
            distintas.setdefault(round(c, 3), []).append((lin, eid))
        for c, lst in distintas.items():
            if len({l for l, _ in lst}) >= 2 and c > 1.05:
                for _, eid in lst:
                    banderas.append(_bandera(uid, eid, "cuota_repetida", f"{pref}.{lado}: cuota {c} en {len(lst)} líneas"))
        for (l1, c1, id1), (l2, c2, id2) in zip(pts, pts[1:]):
            if l2 > l1 and ((lado == "over" and c2 < c1 - 0.02) or (lado == "under" and c2 > c1 + 0.02)):
                banderas.append(_bandera(uid, id2, "escalera_no_monotona", f"{pref}.{lado}: línea {l1}→{l2}, cuota {c1}→{c2}"))
    for e in entradas:
        pm, pmod = _pmerc(e), e.get("p_modelo")
        if pm is not None and pmod is not None and abs(pm - 0.5) > 1e-9 and abs(pmod - pm) >= BRECHA_EXTREMA:
            banderas.append(_bandera(uid, e["id"], "brecha_extrema", f"p_modelo {pmod:.2f} vs mercado {pm:.2f}"))
    return banderas


def revisar(paquete, inventario=None):
    banderas = []
    estados = {}
    for m in (inventario or {}).get("matches", inventario or []) if inventario else []:
        estados[m.get("match_id")] = m.get("event_status")
    for u in paquete["unidades"]:
        banderas.extend(revisar_unidad(u))
        est = estados.get(u.get("match_id"))
        if est in ESTADOS_NO_PROGRAMADO:
            banderas.append(_bandera(u["unit_id"], None, "partido_no_programado", f"estado del inventario: {est}"))
    resumen = defaultdict(int)
    for b in banderas:
        resumen[b["regla"]] += 1
    return {"run": paquete.get("run"), "banderas": banderas, "resumen": dict(resumen),
            "unidades_con_bandera": len({b["unit_id"] for b in banderas})}


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--run", required=True)
    ap.add_argument("--out")
    a = ap.parse_args(argv)
    paquete = json.load(open(os.path.join(a.run, "agentes", "paquete.json"), encoding="utf-8"))
    ruta_inv = os.path.join(a.run, "inventory.json")
    inventario = json.load(open(ruta_inv, encoding="utf-8")) if os.path.exists(ruta_inv) else None
    res = revisar(paquete, inventario)
    out = a.out or os.path.join(a.run, "agentes", "sentido_comun.json")
    with open(out, "w", encoding="utf-8") as fh:
        json.dump(res, fh, ensure_ascii=False, indent=1)
    print(f"{len(res['banderas'])} banderas en {res['unidades_con_bandera']} unidades -> {out}")
    for r, n in sorted(res["resumen"].items()):
        print(f"  {r}: {n}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
