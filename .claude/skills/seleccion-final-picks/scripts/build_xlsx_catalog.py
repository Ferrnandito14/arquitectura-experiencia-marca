#!/usr/bin/env python3
"""Fase 7: libro Excel v2 construido desde el CATÁLOGO COMPLETO (partido × entrada), los tres controles de cobertura, la revisión de agentes y los rankings/combinadas de `catalog_rankings`.

No sustituye ni sobrescribe `dist/ligas-14-oct.xlsx` (la versión anterior, de solo 76 patas de la captura). El nombre definitivo `<name>.xlsx` exige a la vez: investigación certificada, revisión de agentes COMPLETA sobre los
MISMOS partidos y alcance de catálogo; si falta algo sale `<name>-PROVISIONAL.xlsx`. Que el libro tenga nombre definitivo NO significa que algo esté listo para apostar: eso lo dice `preparación para apostar` (siempre NO_APTA con el modelo sin validar).
Todas las horas en America/Caracas (UTC−4)."""
import argparse
import json
import os
import sys
from collections import Counter
from datetime import datetime
from zoneinfo import ZoneInfo

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import agent_review as ar  # noqa: E402
import catalog_rankings as cr  # noqa: E402
import common  # noqa: E402
import market_coverage as cov  # noqa: E402

CCS = ZoneInfo("America/Caracas")
PC = lambda v: None if v is None else round(v * 100, 1)


def caracas(iso):
    if not iso:
        return None
    try:
        return datetime.fromisoformat(iso.replace("Z", "+00:00")).astimezone(CCS).strftime("%d-%b %H:%M")
    except ValueError:
        return iso


def workbook_name(name, summary, ids, review_state, scope="catalog"):
    """(nombre de archivo, [motivos por los que es PROVISIONAL])."""
    why = []
    if scope != "catalog":
        why.append("el libro no contiene el catálogo investigado completo")
    if not summary.get("investigacion_certificada"):
        why.append("investigación no certificada como exhaustiva")
    if summary.get("modo") != "enforce":
        why.append(f"cobertura en modo «{summary.get('modo')}»")
    if not (review_state and review_state.get("estado") == "COMPLETA" and set(review_state.get("partidos_ids", [])) == set(ids)):
        why.append("revisión de agentes no COMPLETA sobre estos partidos")
    return (f"{name}.xlsx" if not why else f"{name}-PROVISIONAL.xlsx"), why


def _inv_text(entry):
    return ",".join(f"{k[:10]}={ar.RES_CODE.get(v, v)}" for k, v in entry["investigacion"].items())


def make_workbook(units, summary, legs, rankings, combos, consolidated, rotation, fname, why):
    from openpyxl import Workbook
    from openpyxl.styles import Alignment, Font
    wb = Workbook()
    wb.remove(wb.active)

    def sheet(name, header, rows, widths=None):
        w = wb.create_sheet(name[:31])
        w.append(header)
        for r in rows:
            w.append(r)
        for c in w[1]:
            c.font = Font(bold=True)
        for col in w.columns:
            w.column_dimensions[col[0].column_letter].width = min(60, max(9, max(len(str(c.value or "")) for c in list(col)[:200]) + 2))
        for row in w.iter_rows(min_row=2, max_row=min(w.max_row, 500)):
            for c in row:
                c.alignment = Alignment(wrap_text=True, vertical="top")
        w.freeze_panes = "A2"
        if w.max_row > 1:
            w.auto_filter.ref = w.dimensions
        return w

    bet = summary["preparacion_para_apostar"]
    rev = summary["revision_agentes"]
    ids = summary["partidos_ids"]
    matches = {u["match_id"]: u for u in units}
    L = [[f"ARCHIVO: {fname}" + ("" if not why else " — PROVISIONAL: " + "; ".join(why))],
         [f"Estado de las tres dimensiones: {cov.banner(summary)}"],
         ["Certificación de la investigación ≠ aprobación para apostar: significa solo que, para estos partidos, cada combinación partido × mercado × canal (datos deportivos, precios) fue consultada o consta por qué no se pudo."],
         ["El modelo propio NO está validado (docs/BACKTEST-modelo-v1.md): sus probabilidades son una segunda opinión, no un veredicto, y por eso ninguna fila ni combinada es «APTA»."],
         ["Precios: «real» = precio de tu casa/captura; «referencia» = mediana de casas de un agregador (no ejecutable). La mayoría de los mercados (córners, tarjetas, goles por equipo, 1.ª parte) no tienen precio en ninguna fuente: ver hoja «Sin precio» para completarlos con los de tu casa."],
         ["Cuota mínima justa = 1/p del modelo: la cuota a partir de la cual el modelo no vería precio desfavorable; no es una recomendación. EV teórico = p × cuota − 1 con ese mismo p."],
         [f"Tope por pata: {cr.MAX_LEG_ODDS}. Combinadas: una pata por partido, topes por dirección/liga/ventana horaria y exposición (ver política en la hoja «Combinadas»); P(pérdida) = 1 − producto de las p (independencia declarada)."],
         [f"Cifras: {len(units)} unidades, {len(ids)} partidos, {sum(len(u['entradas']) for u in units)} filas partido × entrada ({len(cov.mc.CATALOG)} entradas del catálogo por partido); estimador propio en {sum(1 for l in legs if l['p_modelo'] is not None)}; precio de alguna fuente en {sum(1 for l in legs if l['cuota'])}; elegibles para combinadas: {len(cr.eligible(legs))}."],
         ["Horas en America/Caracas (UTC−4). Sin alineaciones oficiales garantizadas: ver «Resumen por partido»."]]
    sheet("Léeme", ["Nota"], L)

    inv, ana, pri = summary["investigacion"], summary["analitica"], summary["precios"]
    sheet("Cobertura", ["Control", "Estado", "Detalle"],
          [["A. Investigación", inv["estado"], "; ".join(f"{i['tipo']}: {i['cantidad']}" for i in inv["incidencias"][:8]) or "sin incidencias"],
           ["B. Analítica (datos / estimador / validación)", ana["estado"], "; ".join(f"{i['tipo']}: {i['cantidad']}" for i in ana["incidencias"][:8]) or "sin incidencias"],
           ["C. Precios (límite 2.10 por pata)", pri["estado"], "; ".join(f"{i['tipo']}: {i['cantidad']}" for i in pri["incidencias"][:8]) or "sin incidencias"],
           ["D. Revisión de agentes", rev["estado"], f"{rev.get('incidencias', 0)} incidencias; unidades esperadas: {rev.get('unidades_esperadas')}"],
           ["E. Preparación para apostar (independiente)", bet["estado"], "requisitos incumplidos: " + ", ".join(f"{k}: {v}" for k, v in bet["requisitos_incumplidos"].items())]])

    uidx = {(u["match_id"], e["id"]): (u, e) for u in units for e in u["entradas"]}
    rows = []
    for l in legs:
        u, e = uidx[(l["match_id"], l["entry_id"])]
        rows.append([l["partido"], caracas(u.get("hora_utc")), u.get("liga"), l["grupo"], l["entry_id"], l["etiqueta"], l["precio_estado"], l["cuota"], l["precio_tipo"], l["fuente_precio"], l["limite_2_10"],
                     PC(l["p_modelo"]), l["cuota_minima_justa"], None if l["brecha_vs_precio"] is None else round(l["brecha_vs_precio"] * 100, 1), PC(l["ev_teorico"]) if l["ev_teorico"] is not None else None,
                     e["datos"], e["validacion"], l["agentes"], "; ".join(l["motivos_exclusion"]) or "elegible", _inv_text(e)])
    sheet("Catálogo completo", ["Partido", "Hora Caracas", "Liga (id)", "Grupo", "Entrada", "Etiqueta", "Precio: estado", "Cuota", "Tipo de precio", "Fuente", "Límite 2.10", "P modelo %", "Cuota mínima justa",
                                "Brecha vs 1/cuota (pp)", "EV teórico %", "Datos", "Validación", "Agentes", "Motivos de exclusión", "Investigación por canal"], rows)

    rk = []
    for g, r in rankings["por_grupo"].items():
        for kind, key in (("más probables (cuota mínima justa ≤ 2.10)", "mas_probables"), ("mayor EV teórico con precio ≤ 2.10", "mayor_ev_teorico_con_precio")):
            for i, x in enumerate(r[key], 1):
                rk.append([g, kind, i, x["partido"], x["etiqueta"], x["cuota"], x["precio_tipo"], PC(x["p_modelo"]), x["cuota_minima_justa"], x["ev_teorico"] and PC(x["ev_teorico"]), x["agentes"]])
    sheet("Rankings por grupo", ["Grupo", "Ranking", "#", "Partido", "Selección", "Cuota", "Tipo de precio", "P modelo %", "Cuota mínima justa", "EV teórico %", "Agentes"], rk)
    sheet("Ranking general", ["#", "Grupo", "Partido", "Selección", "Cuota", "Tipo de precio", "P modelo %", "Cuota mínima justa", "Agentes"],
          [[i, x["grupo"], x["partido"], x["etiqueta"], x["cuota"], x["precio_tipo"], PC(x["p_modelo"]), x["cuota_minima_justa"], x["agentes"]] for i, x in enumerate(rankings["general_mas_probables"], 1)])

    cb = []
    for name, b in combos.items():
        for k, c in enumerate(b["combinadas"], 1):
            for p in c["patas"]:
                cb.append([name, k, c["cuota_total"], PC(c["p_conjunta_independiente"]), PC(c["p_perdida"]), c["ev_teorico"] and PC(c["ev_teorico"]), c["tipo_cuota"], c["estado_agentes"], c["preparacion_para_apostar"]["estado"],
                           ", ".join(c["preparacion_para_apostar"]["incumplidos"]), caracas(p["hora_utc"]), p["partido"], p["etiqueta"], p["cuota"], p["precio_tipo"], PC(p["p_modelo"]), p["agentes"]])
        if not b["combinadas"]:
            cb.append([name, None, None, None, None, None, b["aviso"]] + [None] * 10)
    sheet("Combinadas", ["Objetivo", "Opción", "Cuota total", "P gana (modelo, independencia) %", "P pierde %", "EV teórico %", "Tipo de cuota", "Estado agentes", "Preparación para apostar", "Requisitos que faltan", "Hora Caracas",
                         "Partido", "Selección", "Cuota", "Tipo de precio", "P modelo %", "Agentes pata"], cb)

    sp = sorted([l for l in legs if l["cuota"] is None and l["p_modelo"] is not None and l["cuota_minima_justa"] <= cr.MAX_LEG_ODDS and not any(m.startswith("rechazada") for m in l["motivos_exclusion"])],
                key=lambda l: (l["grupo"], -l["p_modelo"]))
    sheet("Sin precio", ["Partido", "Hora Caracas", "Grupo", "Selección", "P modelo %", "Cuota mínima justa", "Cuota de tu casa (completar)"],
          [[l["partido"], caracas(matches[l["match_id"]].get("hora_utc")), l["grupo"], l["etiqueta"], PC(l["p_modelo"]), l["cuota_minima_justa"], None] for l in sp])

    ag = []
    for uid, c in consolidated.items():
        if c["conflictos"] or c["objeciones"]:
            ag.append([c["partido"], c["grupo"], "; ".join(c["conflictos"]), len(c["objeciones"]),
                       "; ".join(f"{o['agente']}.{o['campo']}:{o['problema']}" for o in c["objeciones"])])
    sheet("Agentes", ["Partido", "Grupo", "Conflictos", "Objeciones del auditor", "Detalle de objeciones"], ag)

    cnt = {}
    for l in legs:
        d = cnt.setdefault(l["match_id"], Counter())
        d["estimador"] += l["p_modelo"] is not None
        d["elegibles"] += not l["motivos_exclusion"]
        d["rechazadas"] += l["agentes"].startswith("rechazada")
        d["aprobadas"] += l["agentes"] == "aprobada"
    rs = []
    for mid in ids:
        u = matches.get(mid)
        if not u:
            continue
        c = u.get("contexto") or {}
        rot = rotation.get(mid) or {}
        rs.append([u["partido"], caracas(u.get("hora_utc")), u.get("liga"), (c.get("arbitro") or {}).get("designado"), (c.get("alineaciones") or {}).get("estado"),
                   f"{(rot.get('home') or {}).get('nivel', 's/d')} | {(rot.get('away') or {}).get('nivel', 's/d')}", cnt[mid]["estimador"], cnt[mid]["elegibles"], cnt[mid]["aprobadas"], cnt[mid]["rechazadas"]])
    sheet("Resumen por partido", ["Partido", "Hora Caracas", "Liga (id)", "Árbitro", "Alineaciones", "Rotación local | visitante", "Entradas con estimador", "Elegibles combinadas", "Aprobadas por agentes", "Rechazadas por agentes"], rs)
    return wb


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--run", required=True)
    ap.add_argument("--ids", required=True, help="JSON {«local|visitante»: match_id}: los valores definen los partidos")
    ap.add_argument("--capture", nargs=2, metavar=("PARTIDOS_USUARIO", "IDS"))
    ap.add_argument("--out-dir", default="dist")
    ap.add_argument("--name", default="ligas-14-oct-v2")
    a = ap.parse_args(argv)
    ids = sorted(set(common.read_json(a.ids).values()))
    units, s = ar.build_units(a.run, ids, tuple(a.capture) if a.capture else None)
    reports = ar.load_reports(a.run)
    legs = cr.legs_from_units(units, cr.agent_status(units, reports))
    consolidated = ar.consolidate(units, reports)
    combos = cr.build_combos(legs, s["investigacion_certificada"])
    fname, why = workbook_name(a.name, s, s["partidos_ids"], ar.load_gate(a.run))
    if os.path.basename(fname).startswith("ligas-14-oct.xlsx"):
        raise SystemExit("el libro v2 nunca puede llamarse como el original")
    rotation = common.read_json(os.path.join(a.run, "rotation.json"), {})
    wb = make_workbook(units, s, legs, cr.build_rankings(legs), combos, consolidated, rotation, fname, why)
    os.makedirs(a.out_dir, exist_ok=True)
    out = os.path.join(a.out_dir, fname)
    wb.save(out)
    print(out)
    print(cov.banner(s))
    print("PROVISIONAL por:" if why else "nombre definitivo (sin implicar aptitud para apostar)", "; ".join(why))
    return 0


if __name__ == "__main__":
    sys.exit(main())
