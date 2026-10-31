#!/usr/bin/env python3
"""Genera los dos archivos de un día para los retos: ×1,20 y ×4, a partir del pool de mercado y la revisión de agentes.

Uso:  build_retos_xlsx.py --run runs/2026-11-01 --dia 2026-11-01 --saldo-x12 26704.02 --saldo-x4 834.35 --out-dir dist
Lee: <run>/pool/patas.json, tickets_x12.json, tickets_x4.json, finalistas.json y, si existen, <run>/agentes/{verificador,deportivo,auditor}.json.
Escribe: <out-dir>/reto-x12-<DD>-<mes>.xlsx y <out-dir>/plan-x4-dia1-<DD>-<mes>.xlsx (hora de Caracas)."""
import argparse
import json
import os
import sys
from datetime import datetime

from openpyxl import Workbook
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.utils import get_column_letter

MESES = ["ene", "feb", "mar", "abr", "may", "jun", "jul", "ago", "sep", "oct", "nov", "dic"]
BONO = 1.09
AVISO_COBERTURA = "NO CERTIFICADO COMO EXHAUSTIVO: pool de mercado (3-5 casas); no evalúa la cobertura del catálogo ni la preparación para apostar"
NEG = Font(bold=True, color="FFFFFF")
FONDO = PatternFill("solid", fgColor="1F4E78")


def leer(ruta, defecto=None):
    return json.load(open(ruta, encoding="utf-8")) if os.path.exists(ruta) else defecto


def hoja(wb, titulo, cabecera, filas, anchos=None):
    ws = wb.create_sheet(titulo)
    ws.append(cabecera)
    for c in ws[1]:
        c.font = NEG; c.fill = FONDO; c.alignment = Alignment(wrap_text=True, vertical="center")
    for f in filas:
        ws.append(f)
    for i, _ in enumerate(cabecera, 1):
        ws.column_dimensions[get_column_letter(i)].width = (anchos or {}).get(i, 18)
    for fila in ws.iter_rows(min_row=2):
        for c in fila:
            c.alignment = Alignment(wrap_text=True, vertical="top")
    ws.freeze_panes = "A2"
    return ws


def revision(agentes):
    por = {}
    for rol in ("verificador", "deportivo", "auditor"):
        d = leer(os.path.join(agentes, rol + ".json"), {"patas": []})
        for p in d.get("patas", []):
            por.setdefault(p["key"], {})[rol] = p
    return por


def etiqueta(rev):
    v, d, a = rev.get("verificador"), rev.get("deportivo"), rev.get("auditor")
    alertas = []
    if v and (not v.get("mercado_ok", True) or not v.get("precio_ok", True) or v.get("estado") not in (None, "programado")):
        alertas.append("verificador: " + (v.get("nota") or "problema"))
    if a and a.get("recomendacion") in ("degradar", "descartar"):
        alertas.append("auditor: " + a["recomendacion"])
    if not rev:
        return "sin revisión"
    return "con alertas" if alertas else "sin alertas"


def fila_pata(p, rev):
    k = p["match_id"] + "|" + p["seleccion"]
    r = rev.get(k, {})
    a = r.get("auditor") or {}
    v = r.get("verificador") or {}
    fuentes = len(v.get("fuentes") or [])
    return [p["hora_caracas"], p["partido"], p["seleccion"], p["cuota"], round(p["p"] * 100, 1), p["n_casas"],
            v.get("hora_confirmada_caracas") or "", ("1 fuente" if fuentes < 2 and v else ("2+ fuentes" if v else "")),
            (a.get("recomendacion", "") + (f" ({a['severidad']})" if a.get("severidad") else "")), etiqueta(r), (a.get("riesgo_principal") or a.get("nota") or v.get("nota") or "")]


CAB_PATA = ["Hora Caracas", "Partido", "Selección", "Cuota (mediana de casas)", "P mercado sin margen %", "Casas", "Hora confirmada", "Fuentes de la hora", "Auditor", "Revisión", "Riesgo principal (auditor)"]
ANCH_PATA = {1: 12, 2: 34, 3: 34, 4: 12, 5: 12, 6: 8, 7: 14, 8: 12, 9: 18, 10: 14, 11: 70}


def tickets_filas(grupos, saldo, rev, bono):
    filas = []
    n = 0
    for etiqueta_g, lista in grupos.items():
        for i, t in enumerate(lista[:3], 1):
            n += 1
            cuota = t["cuota_base"] * (BONO if bono else 1)
            pago = saldo * cuota
            pg = t["p_ganar"]
            for j, p in enumerate(t["patas"]):
                f = fila_pata(p, rev)
                if j == 0:
                    f = [f"Ticket {n} ({etiqueta_g}, opción {i})", round(pg * 100, 1), round((1 - pg) * 100, 1), round(t["cuota_base"], 2), round(cuota, 2), round(pago, 2), round(pago - saldo, 2), round(-saldo, 2)] + f
                else:
                    f = [""] * 8 + f
                filas.append(f)
            filas.append([""] * 20)
    return filas


CAB_TICKET = ["Ticket", "P ganar %", "P perder %", "Cuota base", "Cuota con bono" , "Si gana: cobras (Bs)", "Ganancia (Bs)", "Si pierde (Bs)"] + CAB_PATA


def libro(nombre, dia, saldo, objetivo, grupos, patas_pool, rev, bono, out):
    wb = Workbook()
    ws = wb.active; ws.title = "Léeme"
    dd, mm = dia[8:10], MESES[int(dia[5:7]) - 1]
    lineas = [
        f"{'RETO ×1,20' if objetivo == 'x12' else 'PLAN ×4 (día 1)'} — {int(dd)} de {mm}. Todas las horas son de Caracas.",
        "",
        f"Saldo de partida: {saldo:,.2f} Bs" + ("" if objetivo == "x12" else " (condicionado a que el día 0 pague; si no paga, este archivo no se usa)."),
        "",
        "Cómo se armó: probabilidad de cada pata = promedio de la probabilidad SIN margen de 3 a 5 casas (TheStatsAPI); cuota = mediana entre casas. No se usa el modelo propio (no le gana al mercado) ni cuotas de tu casa: tu casa puede pagar distinto, compara antes de jugar.",
        "Los tickets se ordenan por probabilidad conjunta de ganar entre las combinaciones que dan el producto de cuotas buscado, con partidos distintos (se supone independencia).",
        "Revisión: verificador (hora, estado, precio) y auditor (argumento en contra) sobre las patas finalistas. El análisis del deportivo NO se usa: el auditor halló marcadores invertidos en partidos de visita. 'Todas mantener' = el auditor no puso alertas; 'incluye patas degradadas' = al menos una pata con observación; las patas descartadas no se usan.",
        AVISO_COBERTURA + ".",
        "Una probabilidad no es una garantía: ninguna pata es segura. P perder = 100 − P ganar.",
        "Liquidación: las reglas de TU casa mandan (línea 1.25 con devolución a 1 gol, PA con 2 goles de diferencia, etc.). Las patas de este archivo son líneas .5 y doble oportunidad (90 minutos), sin devolución.",
    ]
    if bono:
        lineas.append("Pago con bono: cuota base × 1,09 (9 %), como en tu hoja. La casa exige mínimo 3 patas (tu regla: 3 a 5) y cuota ≥1,20 por pata.")
    for l in lineas:
        ws.append([l])
    ws.column_dimensions["A"].width = 140
    for c in ws["A"]:
        c.alignment = Alignment(wrap_text=True, vertical="top")
    hoja(wb, "Tickets propuestos", CAB_TICKET, tickets_filas(grupos, saldo, rev, bono), {**{i: 14 for i in range(1, 9)}, **{i + 8: w for i, w in ANCH_PATA.items()}})
    cand = sorted(patas_pool, key=lambda p: -p["p"])[:150] if objetivo == "x12" else sorted([p for p in patas_pool if 1.2 <= p["cuota"] <= 2.1], key=lambda p: -p["valor"])[:150]
    hoja(wb, "Candidatas", CAB_PATA, [fila_pata(p, rev) for p in cand], ANCH_PATA)
    revs = []
    for k, r in rev.items():
        for rol in ("verificador", "deportivo", "auditor"):
            if rol in r:
                x = r[rol]
                revs.append([k.split("|", 1)[1], rol, json.dumps({kk: vv for kk, vv in x.items() if kk != "key"}, ensure_ascii=False)])
    hoja(wb, "Revisión de agentes", ["Pata", "Rol", "Detalle"], revs, {1: 40, 2: 14, 3: 120})
    wb.save(out)


def grupos(run, obj):
    """Tickets con patas todas «mantener» y, aparte, los que incluyen patas degradadas por el auditor (sin duplicados)."""
    salida, vistos = {}, set()
    for suf, rotulo in (("_revisado", "todas mantener"), ("_conalertas", "incluye patas degradadas")):
        d = leer(os.path.join(run, "pool", f"tickets_{obj}{suf}.json"), {})
        for k, lista in d.items():
            nuevos = []
            for t in lista:
                clave = frozenset((p["match_id"], p["seleccion"]) for p in t["patas"])
                if clave not in vistos:
                    vistos.add(clave); nuevos.append(t)
            if nuevos:
                salida[f"{k}, {rotulo}"] = nuevos
    return salida


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--run", required=True); ap.add_argument("--dia", required=True)
    ap.add_argument("--saldo-x12", type=float, required=True); ap.add_argument("--saldo-x4", type=float, required=True)
    ap.add_argument("--out-dir", default="dist")
    a = ap.parse_args(argv)
    patas = leer(os.path.join(a.run, "pool", "patas.json"))["patas"]
    rev = revision(os.path.join(a.run, "agentes"))
    dd, mm = a.dia[8:10], MESES[int(a.dia[5:7]) - 1]
    os.makedirs(a.out_dir, exist_ok=True)
    o12 = os.path.join(a.out_dir, f"reto-x12-{dd}-{mm}.xlsx")
    o4 = os.path.join(a.out_dir, f"plan-x4-dia1-{dd}-{mm}.xlsx")
    libro("x12", a.dia, a.saldo_x12, "x12", grupos(a.run, "x12"), patas, rev, False, o12)
    libro("x4", a.dia, a.saldo_x4, "x4", grupos(a.run, "x4"), patas, rev, True, o4)
    print(o12); print(o4)
    return 0


if __name__ == "__main__":
    sys.exit(main())
