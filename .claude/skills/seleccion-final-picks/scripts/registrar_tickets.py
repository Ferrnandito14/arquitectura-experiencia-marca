#!/usr/bin/env python3
"""Registro consolidado de las patas de los TICKETS DE LA PERSONA USUARIA ya liquidadas (una línea por pata y día) para medir con datos reales cuánto acierta cada tipo de pata,
qué probabilidad le daba el mercado (1/cuota) y, cuando la línea EXACTA está en el catálogo del día, qué probabilidad y qué veredicto de agentes tenía el sistema.
Entradas: `<run>/seguimiento/registro_resultados.jsonl` (lo escribe seguimiento.py solo con el partido FINALIZADO) y `<run>/seguimiento/tickets_abiertos.json`.
Salida: data/registro_tickets_usuario.jsonl (se reescribe completo desde los runs indicados; idempotente).
Uso:  registrar_tickets.py --runs runs/2026-10-13 runs/2026-10-15 [--out data/registro_tickets_usuario.jsonl] [--enrich]   (--enrich necesita los paquetes de agentes del run)"""
import argparse
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common  # noqa: E402


def _fecha(run, row):
    return row.get("fecha") or re.search(r"(\d{4}-\d{2}-\d{2})", run).group(1)


def catalog_label(leg):
    """Texto de la etiqueta del catálogo para una pata simple (línea EXACTA), o None si no hay equivalente exacto (combos, hándicaps de cuarto de línea, córners por equipo...)."""
    mk = leg.get("mercado")
    if mk == "total":
        return ("Más de %g goles" if leg["op"] == "over" else "Menos de %g goles") % leg["linea"]
    if mk == "corners":
        return ("Más de %g córners" if leg["op"] == "over" else "Menos de %g córners") % leg["linea"]
    if mk == "btts":
        return "Ambos anotan: sí"
    if mk == "dc":
        return "o empate"
    if mk == "total_1t":
        return "1.ª parte: %s %g goles" % ("más de" if leg["op"] == "over" else "menos de", leg["linea"])
    return None


def enrich(run, rows, spec):
    """Añade p_modelo y estado de agentes del sistema a las filas cuya línea exacta esté en el catálogo del día."""
    import agent_review as ar
    import catalog_rankings as cr
    ids = sorted(set(common.read_json(os.path.join(run, "ligas", "ids.json")).values()))
    units, _ = ar.build_units(run, ids, (os.path.join(run, "ligas", "partidos_usuario.json"), os.path.join(run, "ligas", "ids.json")))
    reports = ar.load_reports(run)
    rp = cr.reviewed_prices(run)
    pack = common.read_json(os.path.join(run, "agentes", "paquete.json"), None)
    legs = cr.legs_from_units(units, cr.agent_status(units, reports, rp, (pack or {}).get("unidades")), rp)
    el = {l["leg_id"] for l in cr.eligible(legs)}
    by = {(t["id"], p["partido"], p["mercado"]): p for t in spec["tickets"] for p in t["patas"]}
    for r in rows:
        leg = by.get((r["ticket"], r["partido"], r["mercado"]))
        lab = catalog_label(leg) if leg else None
        r["p_modelo"] = r["agentes_sistema"] = r["elegible_sistema"] = None
        if not lab:
            continue
        mid = leg["mid"]
        c = [l for l in legs if l["match_id"] == mid and lab.lower() in l["etiqueta"].lower() and (leg.get("mercado") != "dc" or "empate" in l["etiqueta"].lower())]
        if len(c) >= 1:
            r["p_modelo"] = None if c[0]["p_modelo"] is None else round(c[0]["p_modelo"], 3)
            r["agentes_sistema"] = c[0]["agentes"]
            r["elegible_sistema"] = c[0]["leg_id"] in el
    return rows


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--runs", nargs="+", required=True)
    ap.add_argument("--out", default="data/registro_tickets_usuario.jsonl")
    ap.add_argument("--enrich", action="store_true")
    a = ap.parse_args(argv)
    allrows = []
    for run in a.runs:
        reg = os.path.join(run, "seguimiento", "registro_resultados.jsonl")
        if not os.path.exists(reg):
            continue
        rows = []
        for x in open(reg, encoding="utf-8"):
            if not x.strip():
                continue
            d = json.loads(x)
            rows.append({"fecha": _fecha(run, d), "ticket": d["ticket"], "origen": d.get("origen", "persona usuaria"), "partido": d["partido"], "mercado": d["mercado"],
                         "cuota": d["cuota"], "p_implicita_con_margen": round(1 / d["cuota"], 3), "resultado": d["resultado"], "detalle": d.get("detalle")})
        if a.enrich and rows and os.path.exists(os.path.join(run, "agentes", "paquete.json")):
            spec = common.read_json(os.path.join(run, "seguimiento", "tickets_abiertos.json"))
            rows = enrich(run, rows, spec)
        allrows += rows
    os.makedirs(os.path.dirname(a.out) or ".", exist_ok=True)
    with open(a.out, "w", encoding="utf-8") as f:
        for r in allrows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    done = [r for r in allrows if r["resultado"] in ("ACERTADA", "FALLADA")]
    print(f"{len(allrows)} patas registradas ({len(done)} con resultado ganada/perdida: {sum(r['resultado'] == 'ACERTADA' for r in done)} ganadas)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
