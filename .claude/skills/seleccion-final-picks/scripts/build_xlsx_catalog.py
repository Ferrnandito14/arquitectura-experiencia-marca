#!/usr/bin/env python3
"""Fase 7: libro Excel con el FORMATO CLÁSICO (una hoja por liga, rankings de seguridad y de atractivo-cuota, top por liga y combinadas) alimentado por el CATÁLOGO COMPLETO de mercados
(goles totales y por equipo, 1X2, doble oportunidad, empate no válido, hándicaps, córners, tarjetas, 1.ª parte, remates…), los tres controles de cobertura y la revisión de agentes.

No sustituye ni sobrescribe `dist/ligas-14-oct.xlsx` (versión anterior, de solo las patas de las capturas). El nombre definitivo `<name>.xlsx` exige a la vez: investigación certificada, revisión de agentes COMPLETA sobre los
MISMOS partidos y alcance de catálogo; si falta algo sale `<name>-PROVISIONAL.xlsx`. Un nombre definitivo NO significa que algo esté listo para apostar: eso lo dice `preparación para apostar` (NO_APTA con el modelo sin validar).
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
CLASSIC_TARGETS = (("×1.5–1.8", 1.5, 1.8, 2), ("×2–2.6", 2.0, 2.6, 3), ("×3–3.8", 3.0, 3.8, 4))
CORE_GROUPS = ("resultado", "goles")
RANK_MIN_ODDS = 1.10      # las patas a ~1.01–1.09 (p ≈ 1) no informan: pagan casi nada y llenarían los rankings de «seguridad»


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
    return "; ".join(f"{k}={v}" for k, v in entry["investigacion"].items())


def liga_map(units, capture=None):
    """{match_id: nombre de liga}: de las capturas de la persona usuaria si existen; si no, «Liga <id>»."""
    out = {u["match_id"]: f"Liga {u.get('liga')}" for u in units}
    if capture:
        p = common.read_json(capture[0], {}).get("partidos", [])
        ids = common.read_json(capture[1], {})
        for lg, h, a, *_ in p:
            if f"{h}|{a}" in ids:
                out[ids[f"{h}|{a}"]] = lg
    return out


EV_ALERT = cr.EV_ALERT


def alerta(l):
    a = []
    if l["brecha_vs_precio"] is not None and abs(l["brecha_vs_precio"]) >= cr.MAX_GAP:
        a.append("desacuerdo con el mercado (|brecha| ≥ 15 pp)")
    if l["ev_teorico"] is not None and l["ev_teorico"] >= EV_ALERT:
        a.append("EV alto: probable ruido del modelo (no validado)")
    return "; ".join(a) or None


LEYENDA = [
    ("Investigación por canal (Catálogo completo)", "encontrado", "El canal tiene el dato/precio para esa entrada (con evidencia registrada)."),
    ("Investigación por canal (Catálogo completo)", "consultado_no_encontrado", "Se consultó la fuente y no trajo ese dato/precio."),
    ("Investigación por canal (Catálogo completo)", "fuente_no_ofrece", "La fuente no publica ese mercado (p. ej. la API de cuotas no trae córners ni tarjetas) o no cubre el partido."),
    ("Investigación por canal (Catálogo completo)", "no_verificable", "No se pudo comprobar con la fuente disponible."),
    ("Investigación por canal (Catálogo completo)", "pendiente", "Aún no se consultó (con certificación, siempre 0)."),
    ("Canales", "datos_deportivos", "Historial del equipo (goles, córners, tarjetas…) de la API."),
    ("Canales", "apifootball (agregador)", "Mediana de cuotas de varias casas de un agregador: REFERENCIA, no ejecutable."),
    ("Canales", "football-data (fixtures, Bet365)", "Cuotas de una casa publicadas por football-data, solo donde esa fuente cubre el partido."),
    ("Canales", "usuario:partidos_usuario.json", "Tus capturas de cuotas (precio real de tu casa)."),
    ("Tipo de precio", "ejecutable", "Cuota real de tu casa/captura."),
    ("Tipo de precio", "referencia", "Mediana de agregador: confírmala en tu casa; no se puede apostar tal cual."),
    ("Precio: estado", "real_verificada / otra_fuente / no_verificable / sin_precio", "Clasificación de la cuota: real de tu casa / agregador / no comprobable / no hay cuota en ninguna fuente."),
    ("Agentes", "aprobada", "Los 4 roles la revisaron y ninguno la objeta."),
    ("Agentes", "objetada:<rol>", "El auditor objeta el veredicto de ese rol (dato contradictorio): no cuenta como aprobada."),
    ("Agentes", "degradada:deportivo:BAJA|NO_EVALUABLE", "Solidez deportiva baja: sale de combinadas y rankings, se muestra en las hojas de liga."),
    ("Agentes", "rechazada:<rol>:<motivo>", "Defecto de dato o de modelo (no verificable, descarte del auditor, sin estimador…): fuera de combinadas y rankings."),
    ("Agentes", "sin_revision", "La unidad no entró en la muestra del auditor: revisada por 3 de 4 roles."),
    ("Límite 2.10", "cumple / excede / sin_precio_justa_ok / sin_precio_justa_excede", "Cuota ≤ 2.10 / mayor / sin precio pero la cuota mínima justa ≤ 2.10 / sin precio y la justa ya supera 2.10."),
    ("P modelo %", "", "Probabilidad del modelo propio (NO validado): segunda opinión, no veredicto."),
    ("Cuota mínima justa", "", "1 / p del modelo: cuota por debajo de la cual el modelo vería precio desfavorable."),
    ("Brecha vs 1/cuota (pp)", "", "p modelo − 1/cuota. |brecha| ≥ 15 pp = desacuerdo fuerte con el mercado (se excluye de rankings y combinadas)."),
    ("EV teórico %", "", "p × cuota − 1 con p del modelo. Con modelo sin validar, un EV alto casi siempre significa que el modelo discrepa del mercado, no que haya ventaja."),
    ("Combinadas", "P gana / P pierde", "Producto de las p de las patas bajo independencia declarada (no validada) / su complemento."),
    ("Combinadas", "Preparación para apostar", "NO_APTA mientras falte algún requisito (precio real, modelo validado, etc.)."),
    ("Alerta", "", "Aviso automático: desacuerdo con el mercado o EV alto. No cambia la selección, solo advierte."),
    ("Hora Caracas", "", "America/Caracas (UTC−4)."),
]


def _verdicts(consolidated, l):
    c = consolidated.get(f"{l['match_id']}|{l['grupo']}") or {"roles": {}}
    roles = c.get("roles") or {}
    aud = roles.get("auditor") or {}
    dep = roles.get("deportivo") or {}
    return {"deportivo": ar.entry_verdict(c, "deportivo", l["entry_id"]) if dep else None,
            "cuantitativo": ar.entry_verdict(c, "cuantitativo", l["entry_id"]) if roles.get("cuantitativo") else None,
            "verificador": ar.entry_verdict(c, "verificador", l["entry_id"]) if roles.get("verificador") else None,
            "auditor": aud.get("recomendacion"), "escenario": dep.get("escenario_perdida")}


def make_workbook(units, summary, legs, rankings, combos, consolidated, rotation, fname, why, ligas=None):
    from openpyxl import Workbook
    from openpyxl.styles import Alignment, Font
    wb = Workbook()
    wb.remove(wb.active)

    def sheet(name, header, rows):
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

    bet, rev, ids = summary["preparacion_para_apostar"], summary["revision_agentes"], summary["partidos_ids"]
    matches = {u["match_id"]: u for u in units}
    ligas = ligas or liga_map(units)
    verd = {l["leg_id"]: _verdicts(consolidated, l) for l in legs}
    hora = lambda l: matches[l["match_id"]].get("hora_utc")
    visible = [l for l in legs if l["p_modelo"] is not None and not any(m.startswith("rechazada") for m in l["motivos_exclusion"])]
    elig = cr.eligible(legs)

    sheet("Léeme", ["Nota"], [
        [f"ARCHIVO: {fname}" + ("" if not why else " — PROVISIONAL: " + "; ".join(why))],
        [f"Estado de las tres dimensiones: {cov.banner(summary)}"],
        ["Cada hoja de liga lista TODOS los mercados investigados de sus partidos (goles totales y por equipo, 1X2, doble oportunidad, empate no válido, hándicaps, córners, tarjetas con A=1/R=2, 1.ª parte, remates…) que tienen probabilidad del modelo propio y no fueron rechazados por los agentes."],
        ["Certificación de la investigación ≠ aprobación para apostar: significa solo que, para estos partidos, cada combinación partido × mercado × canal (datos deportivos, precios) fue consultada o consta por qué no se pudo."],
        ["El modelo propio NO está validado (docs/BACKTEST-modelo-v1.md): sus probabilidades son una segunda opinión, no un veredicto; por eso ninguna fila ni combinada es «APTA»."],
        ["Precios: «real» = tu casa/captura; «referencia» = mediana de casas de un agregador (no ejecutable). Córners, tarjetas, goles por equipo, 1.ª parte y remates no tienen precio en ninguna fuente: usa «Mercados extra» / «Sin precio» y pega la cuota de tu casa."],
        ["Cuota mínima justa = 1/p del modelo (no es una recomendación). EV teórico = p × cuota − 1 con ese p; es una referencia, no el veredicto. Brecha = p modelo − 1/cuota (pp); ≥ 15 pp = señal de ruido o de información que el modelo no tiene."],
        ["Solidez deportiva / cuantitativo / verificador / auditor = veredicto de cada agente por entrada (contrato cerrado). BAJA o NO_EVALUABLE = degradada: sale de las combinadas pero se muestra."],
        [f"Tope por pata: {cr.MAX_LEG_ODDS}. Rankings y combinadas usan solo patas con precio de alguna fuente (los rankings, además, cuota ≥ 1.10), no rechazadas ni degradadas y sin brecha ≥ 15 pp. Combinadas: una pata por partido, topes por dirección/liga/ventana horaria y exposición; P(pérdida) = 1 − producto de las p (independencia declarada)."],
        [f"Cifras: {len(units)} unidades, {len(ids)} partidos, {sum(len(u['entradas']) for u in units)} filas partido × entrada; con estimador propio: {sum(1 for l in legs if l['p_modelo'] is not None)}; con precio de alguna fuente: {sum(1 for l in legs if l['cuota'])}; elegibles para rankings/combinadas: {len(elig)}."],
        ["Un EV teórico alto (≥ +10 %) con el modelo sin validar suele indicar que el modelo discrepa del mercado, no una ventaja: la columna «Alerta» lo marca. Los «seguros» del ranking de seguridad usan en su mayoría precio de referencia, no ejecutable."],
        ["La hoja «Leyenda» explica cada código y columna. Horas en America/Caracas (UTC−4). Alineaciones no publicadas al generar: ver «Resumen por partido»."]])

    sheet("Leyenda", ["Tema", "Valor", "Qué significa"], [list(x) for x in LEYENDA])
    H = ["Hora Caracas", "Partido", "Mercado", "Selección", "Cuota", "Tipo de precio", "P modelo %", "Cuota mínima justa", "Brecha vs 1/cuota (pp)", "EV teórico %", "Límite 2.10", "Agentes",
         "Solidez deportiva", "Cuantitativo", "Verificador", "Auditor", "Rotación local | visitante", "Escenario de pérdida", "Alerta"]

    def row(l):
        v = verd[l["leg_id"]]
        rot = rotation.get(l["match_id"]) or {}
        return [caracas(hora(l)), l["partido"], l["grupo"], l["etiqueta"], l["cuota"], l["precio_tipo"], PC(l["p_modelo"]), l["cuota_minima_justa"], None if l["brecha_vs_precio"] is None else round(l["brecha_vs_precio"] * 100, 1),
                PC(l["ev_teorico"]) if l["ev_teorico"] is not None else None, l["limite_2_10"], l["agentes"], v["deportivo"], v["cuantitativo"], v["verificador"], v["auditor"],
                f"{(rot.get('home') or {}).get('nivel', 's/d')} | {(rot.get('away') or {}).get('nivel', 's/d')}", v["escenario"], alerta(l)]

    order = lambda l: (hora(l) or "", l["partido"], l["grupo"], -(l["p_modelo"] or 0))
    seen = []
    for u in units:
        if ligas[u["match_id"]] not in seen:
            seen.append(ligas[u["match_id"]])
    for lg in seen:
        rows_lg = [row(l) for l in sorted([x for x in visible if ligas[x["match_id"]] == lg], key=order)]
        if not rows_lg:
            rows_lg = [[None, "; ".join(sorted({u["partido"] for u in units if ligas[u["match_id"]] == lg})), "sin probabilidad del modelo propio para estos partidos (muestra insuficiente o sin media de liga): ver «Catálogo completo»"] + [None] * (len(H) - 3)]
        sheet(lg.replace("(", "").replace(")", "").replace("/", "-")[:28], H, rows_lg)

    SEC = sorted([l for l in elig if l["cuota"] >= RANK_MIN_ODDS], key=lambda l: -l["p_modelo"])
    ATR = sorted([l for l in elig if l["cuota"] >= RANK_MIN_ODDS and l["p_modelo"] >= 0.45 and l["ev_teorico"] is not None], key=lambda l: -l["ev_teorico"])
    sheet("Ranking seguridad", ["#", "Liga"] + H, [[i, ligas[l["match_id"]]] + row(l) for i, l in enumerate(SEC[:25], 1)])
    sheet("Ranking atractivo-cuota", ["#", "Liga"] + H, [[i, ligas[l["match_id"]]] + row(l) for i, l in enumerate(ATR[:25], 1)])
    tops = []
    for lg in seen:
        for i, l in enumerate([x for x in SEC if ligas[x["match_id"]] == lg][:3], 1):
            tops.append(["Seguridad", lg, i] + row(l))
        for i, l in enumerate([x for x in ATR if ligas[x["match_id"]] == lg][:3], 1):
            tops.append(["Atractivo", lg, i] + row(l))
    sheet("Top por liga", ["Ranking", "Liga", "#"] + H, tops)

    cb = []
    for name, b in combos.items():
        for k, c in enumerate(b["combinadas"], 1):
            for p in c["patas"]:
                cb.append([name, k, c["cuota_total"], PC(c["p_conjunta_independiente"]), PC(c["p_perdida"]), PC(c["ev_teorico"]) if c["ev_teorico"] is not None else None, c["tipo_cuota"], c["estado_agentes"],
                           c["preparacion_para_apostar"]["estado"], ", ".join(c["preparacion_para_apostar"]["incumplidos"]), caracas(p["hora_utc"]), p["partido"], p["etiqueta"], p["cuota"], p["precio_tipo"], PC(p["p_modelo"]), p["agentes"], c.get("alerta")])
        if not b["combinadas"]:
            cb.append([name, None, None, None, None, None, b["aviso"]] + [None] * 11)
    sheet("Combinadas", ["Objetivo", "Opción", "Cuota total", "P gana (modelo, independencia) %", "P pierde %", "EV teórico %", "Tipo de cuota", "Estado agentes", "Preparación para apostar", "Requisitos que faltan", "Hora Caracas",
                         "Partido", "Selección", "Cuota", "Tipo de precio", "P modelo %", "Agentes pata", "Alerta"], cb)

    ex = []
    per_unit = {}
    for l in visible:
        if l["grupo"] in CORE_GROUPS or l["cuota_minima_justa"] > cr.MAX_LEG_ODDS:
            continue
        per_unit.setdefault((l["match_id"], l["grupo"]), []).append(l)
    for (mid, g), ls in sorted(per_unit.items(), key=lambda t: (hora(t[1][0]) or "", t[1][0]["partido"], t[0][1])):
        for l in sorted(ls, key=lambda x: -x["p_modelo"])[:3]:
            v = verd[l["leg_id"]]
            ex.append([caracas(hora(l)), l["partido"], g, l["etiqueta"], PC(l["p_modelo"]), l["cuota_minima_justa"], l["cuota"], None, v["deportivo"], v["cuantitativo"], v["auditor"]])
    sheet("Mercados extra", ["Hora Caracas", "Partido", "Mercado", "Selección (top 3 por p)", "P modelo %", "Cuota mínima justa", "Cuota fuente", "Cuota de tu casa (completar)", "Solidez deportiva", "Cuantitativo", "Auditor"], ex)

    cnt = {}
    for l in legs:
        d = cnt.setdefault(l["match_id"], Counter())
        d["estimador"] += l["p_modelo"] is not None
        d["elegibles"] += not l["motivos_exclusion"]
        d["aprobadas"] += l["agentes"] == "aprobada"
        d["degradadas"] += l["agentes"].startswith("degradada")
        d["rechazadas"] += l["agentes"].startswith("rechazada")
    rs = []
    for mid in ids:
        u = matches.get(mid)
        if not u:
            continue
        c = u.get("contexto") or {}
        rot = rotation.get(mid) or {}
        mot = "; ".join(f"{k}: {', '.join((rot.get(k) or {}).get('motivos') or [])}" for k in ("home", "away") if (rot.get(k) or {}).get("motivos"))
        rs.append([caracas(u.get("hora_utc")), u["partido"], ligas[mid], (c.get("arbitro") or {}).get("designado"), (c.get("alineaciones") or {}).get("estado"),
                   f"{(rot.get('home') or {}).get('nivel', 's/d')} | {(rot.get('away') or {}).get('nivel', 's/d')}", mot, cnt[mid]["estimador"], cnt[mid]["elegibles"], cnt[mid]["aprobadas"], cnt[mid]["degradadas"], cnt[mid]["rechazadas"]])
    sheet("Resumen por partido", ["Hora Caracas", "Partido", "Liga", "Árbitro", "Alineaciones", "Rotación local | visitante", "Motivos de rotación", "Entradas con estimador", "Elegibles", "Aprobadas", "Degradadas", "Rechazadas"], rs)

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
        rows.append([l["partido"], caracas(u.get("hora_utc")), ligas[l["match_id"]], l["grupo"], l["entry_id"], l["etiqueta"], l["precio_estado"], l["cuota"], l["precio_tipo"], l["fuente_precio"], l["limite_2_10"],
                     PC(l["p_modelo"]), l["cuota_minima_justa"], None if l["brecha_vs_precio"] is None else round(l["brecha_vs_precio"] * 100, 1), PC(l["ev_teorico"]) if l["ev_teorico"] is not None else None,
                     e["datos"], e["validacion"], l["agentes"], "; ".join(l["motivos_exclusion"]) or "elegible", _inv_text(e)])
    sheet("Catálogo completo", ["Partido", "Hora Caracas", "Liga", "Grupo", "Entrada", "Etiqueta", "Precio: estado", "Cuota", "Tipo de precio", "Fuente", "Límite 2.10", "P modelo %", "Cuota mínima justa",
                                "Brecha vs 1/cuota (pp)", "EV teórico %", "Datos", "Validación", "Agentes", "Motivos de exclusión", "Investigación por canal"], rows)

    sp = sorted([l for l in legs if l["cuota"] is None and l["p_modelo"] is not None and l["cuota_minima_justa"] <= cr.MAX_LEG_ODDS and not any(m.startswith("rechazada") for m in l["motivos_exclusion"])],
                key=lambda l: (l["grupo"], -l["p_modelo"]))
    sheet("Sin precio", ["Partido", "Hora Caracas", "Grupo", "Selección", "P modelo %", "Cuota mínima justa", "Cuota de tu casa (completar)"],
          [[l["partido"], caracas(hora(l)), l["grupo"], l["etiqueta"], PC(l["p_modelo"]), l["cuota_minima_justa"], None] for l in sp])

    ag = []
    for uid, c in consolidated.items():
        if c["conflictos"] or c["objeciones"]:
            ag.append([c["partido"], c["grupo"], "; ".join(c["conflictos"]), len(c["objeciones"]), "; ".join(f"{o['agente']}.{o['campo']}:{o['problema']}" for o in c["objeciones"])])
    sheet("Agentes", ["Partido", "Grupo", "Conflictos", "Objeciones del auditor", "Detalle de objeciones"], ag)
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
    combos = cr.build_combos(legs, s["investigacion_certificada"], targets=CLASSIC_TARGETS + cr.DEFAULT_TARGETS)
    fname, why = workbook_name(a.name, s, s["partidos_ids"], ar.load_gate(a.run))
    if os.path.basename(fname).startswith("ligas-14-oct.xlsx"):
        raise SystemExit("el libro v2 nunca puede llamarse como el original")
    rotation = common.read_json(os.path.join(a.run, "rotation.json"), {})
    wb = make_workbook(units, s, legs, cr.build_rankings(legs), combos, consolidated, rotation, fname, why, liga_map(units, a.capture))
    os.makedirs(a.out_dir, exist_ok=True)
    out = os.path.join(a.out_dir, fname)
    wb.save(out)
    print(out)
    print(cov.banner(s))
    print("PROVISIONAL por:" if why else "nombre definitivo (sin implicar aptitud para apostar)", "; ".join(why))
    return 0


if __name__ == "__main__":
    sys.exit(main())
