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


def catalog_matches(legs, mid, leg, lab):
    """Patas del catálogo del partido `mid` que corresponden a la pata del usuario. Línea EXACTA: igualdad de etiqueta (una subcadena casaría «Más de 2.5 goles» con «Hoffenheim: más de 2.5 goles», que es otra pata); la doble oportunidad busca «o empate»."""
    if leg.get("mercado") == "dc":
        c = [l for l in legs if l["match_id"] == mid and lab.lower() in l["etiqueta"].lower()]
        lado = str(leg.get("lado") or "")
        if lado.startswith(("home", "away")):
            tag = "(1x)" if lado.startswith("home") else "(x2)"
            c = [l for l in c if tag in l["etiqueta"].lower()] or c
        return c
    return [l for l in legs if l["match_id"] == mid and lab.lower() == l["etiqueta"].lower()]


def _fmt_line(x):
    return ("%g" % x)


def entry_ids(leg):
    """(ids de entradas del catálogo, nota) de una pata del usuario. Una pata simple devuelve 1 id; un combo («Crear apuesta»), uno por tramo.
    (None, motivo) si no hay equivalente. Líneas fuera del catálogo (p. ej. hándicap +2.75) usan la línea contigua del catálogo y lo dicen en la nota (cota, no probabilidad exacta)."""
    import market_catalog as mc
    cat = {e["id"] for e in mc.CATALOG}

    def one(t):
        mk = t.get("mercado") or t.get("tipo")
        op, ln, lado = t.get("op"), t.get("linea"), str(t.get("lado") or "")
        side = "home" if lado.startswith("home") else "away" if lado.startswith("away") else None
        if mk == "total" and ln is not None:
            eid = ("goles.total_entero.%s.%s" if float(ln).is_integer() else "goles.total.%s.%s") % (op, _fmt_line(ln if not float(ln).is_integer() else int(ln)))
        elif mk == "corners":
            eid = "corners.total.%s.%s" % (op, _fmt_line(ln))
        elif mk == "total_1t":
            eid = "primera_parte.total.%s.%s" % (op, _fmt_line(ln))
        elif mk == "btts":
            eid = "goles.btts.yes"
        elif mk == "dc":
            eid = "resultado.dc.1x" if lado.startswith("home") else "resultado.dc.x2" if lado.startswith("away") else "resultado.dc.12"
        elif mk == "1x2" and lado in ("home", "away", "draw"):
            eid = "resultado.1x2." + lado
        elif mk == "corners_equipo" and side:
            eid = "corners.equipo.%s.%s.%s" % (side, op, _fmt_line(ln))
        elif mk == "tarjetas":
            eid = "cards_pts.total.%s.%s" % (op, _fmt_line(ln))
        elif mk == "handicap" and side and ln is not None:
            eid = "resultado.ah.%s.%+g" % (side, float(ln)) if not float(ln).is_integer() else "resultado.ah_entero.%s.%+d" % (side, int(ln))
            if eid not in cat and round(float(ln) * 4) % 2 == 1:           # cuarto de línea: se acota con la media línea inferior (gana al menos esa)
                return "resultado.ah.%s.%+g" % (side, float(ln) - 0.25), "cota inferior: línea %+g del catálogo (la pata es %+g)" % (float(ln) - 0.25, float(ln))
        else:
            return None, "sin equivalente en el catálogo (%s)" % mk
        return (eid, None) if eid in cat else (None, "línea fuera del catálogo (%s)" % eid)

    if leg.get("mercado") == "combo":
        ids, notes = [], ["producto de las patas asumiendo independencia (aproximación)"]
        for sub in leg.get("subs") or []:
            i, n = one(sub)
            if i is None:
                return None, "combo con un tramo sin equivalente: " + (n or "")
            ids.append(i)
            if n:
                notes.append(n)
        return (ids or None), "; ".join(notes)
    i, n = one(leg)
    return ([i] if i else None), n


def catalog_legs(legs, mid, leg):
    """(patas del catálogo, nota) para una pata del usuario; busca por leg_id exacto «match|entrada»."""
    ids, nota = entry_ids(leg)
    if not ids:
        return [], nota
    by = {l["leg_id"]: l for l in legs}
    got = [by.get(f"{mid}|{i}") for i in ids]
    if any(g is None for g in got):
        return [], "entrada no disponible en el catálogo de ese partido"
    return got, nota


def combine(found):
    """p_modelo (producto), estados de agentes y elegibilidad de las patas del catálogo que componen una pata del usuario."""
    ps = [l["p_modelo"] for l in found]
    p = None if any(x is None for x in ps) else round(__import__("math").prod(ps), 3)
    return p, ";".join(l["agentes"] for l in found), all(not l["motivos_exclusion"] for l in found)


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
    by = {(t["id"], p["partido"], p["mercado"]): p for t in spec["tickets"] for p in t["patas"]}
    for r in rows:
        leg = by.get((r["ticket"], r["partido"], r["mercado"]))
        r["p_modelo"] = r["agentes_sistema"] = r["elegible_sistema"] = r["nota_modelo"] = None
        if not leg:
            continue
        found, nota = catalog_legs(legs, leg["mid"], leg)
        r["nota_modelo"] = nota
        if found:
            r["p_modelo"], r["agentes_sistema"], r["elegible_sistema"] = combine(found)
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
