#!/usr/bin/env python3
"""Une dataset.json + informes de agentes (agentes/grupo_*.json) -> rankings, combinadas y dist/ligas-14-oct.xlsx."""
import json, itertools, sys
sys.path.insert(0, ".claude/skills/seleccion-final-picks/scripts")
import tickets as T  # noqa: E402
import market_coverage as MC  # noqa: E402
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment

import argparse, os  # noqa: E402
_ap = argparse.ArgumentParser(description=__doc__)
_ap.add_argument("--ligas-dir", default="runs/2026-10-14/ligas", help="carpeta con dataset.json, dataset_meta.json, market_coverage.json y agentes/")
_ap.add_argument("--out-dir", default="dist")
_ap.add_argument("--content-scope", choices=("capture_legs_only", "catalog"), default="capture_legs_only",
                help="qué contiene el libro: solo las patas de la captura (1X2 + una línea) o el catálogo investigado completo; con «capture_legs_only» nunca se escribe el nombre definitivo")
_args = _ap.parse_args()
RUN = _args.ligas_dir
D = json.load(open(f"{RUN}/dataset.json", encoding="utf-8"))


def _certification():
    """La salida definitiva exige que los tres controles se hayan EJECUTADOS sobre ESTOS partidos (build_dataset.py) y que la investigación esté COMPLETA."""
    meta_p, cov_p = os.path.join(RUN, "dataset_meta.json"), os.path.join(RUN, "market_coverage.json")
    if not (os.path.exists(meta_p) and os.path.exists(cov_p)):
        return False, ["no consta la ejecución de los controles de cobertura (faltan dataset_meta.json / market_coverage.json): ejecuta build_dataset.py"], None
    cov, meta = json.load(open(cov_p, encoding="utf-8")), json.load(open(meta_p, encoding="utf-8"))
    ids = {m["match_id"] for m in D}
    why = []
    if _args.content_scope != "catalog":
        why.append("el libro solo contiene las patas de la captura (1X2 + una línea de goles), no los mercados del catálogo investigados: su contenido no es exhaustivo aunque la investigación esté certificada")
    if cov.get("modo") != "enforce":
        why.append(f"cobertura en modo «{cov.get('modo')}»")
    if set(cov.get("partidos_ids", [])) != ids or set(meta.get("partidos_ids", [])) != ids:
        why.append("la cobertura NO corresponde a los partidos de este dataset (resultado obsoleto o de otro conjunto)")
    if not cov.get("investigacion_certificada", cov.get("certificado_investigacion")):
        why.append(cov.get("aviso", "investigación no certificada"))
    return not why, why, cov


_ok, _why, _cov = _certification()
OUT = os.path.join(_args.out_dir, "ligas-14-oct.xlsx" if _ok else "ligas-14-oct-PROVISIONAL.xlsx")

AG = {}
for g in "ABC":
    try: AG.update(json.load(open(f"{RUN}/agentes/grupo_{g}.json")))
    except Exception as e: print("falta grupo", g, e)
legs = []
for m in D:
    ag = AG.get(m["partido"], {})
    for l in m["patas"]:
        a = (ag.get("patas") or {}).get(l["seleccion"], {})
        legs.append({**l, "liga": m["liga"], "partido": m["partido"], "hora": m["hora_caracas"], "match_id": m["match_id"], "solidez": a.get("solidez", "s/d"), "escenario": a.get("escenario_perdida", ""),
                     "rot_local": m["rotacion"]["home"], "rot_visit": m["rotacion"]["away"]})
def excl(l): return l["rotacion"] == "veto"
SEC = sorted([l for l in legs if not excl(l) and l["solidez"] != "BAJA"], key=lambda l: -l["p_central"])
ATR = sorted([l for l in legs if not excl(l) and l["solidez"] != "BAJA" and l["p_central"] >= 0.45], key=lambda l: -l["ev_central"])

# combinadas: una pata por partido, solidez ALTA/MEDIA, brecha < 0.15, máx. 2 de la misma dirección, p_central ≥ 0.55
pool = [l for l in legs if not excl(l) and l["solidez"] in ("ALTA", "MEDIA") and l["p_central"] >= 0.55 and (l["brecha"] is None or abs(l["brecha"]) < 0.15)]
pool.sort(key=lambda l: -l["p_central"]); pool = pool[:26]
RANGES = {"×1.5–1.8": (1.5, 1.8, 2), "×2–2.6": (2.0, 2.6, 3), "×3–3.8": (3.0, 3.8, 4)}
combos = {}
for nm, (lo, hi, nmax) in RANGES.items():
    best = []
    for n in range(2, nmax + 1):
        for c in itertools.combinations(pool, n):
            if len({x["match_id"] for x in c}) < n: continue
            dirs = [x["direccion"] for x in c]
            if dirs.count("under") > 2 or dirs.count("over") > 2: continue
            odds = 1
            for x in c: odds *= x["cuota"]
            if not lo <= odds <= hi: continue
            pj = 1; pm = 1
            for x in c: pj *= x["p_central"]; pm *= x["p_mercado"]
            best.append((pj, odds, pm, c))
    best.sort(key=lambda t: -t[0]); combos[nm] = best[:3]

wb = Workbook(); wb.remove(wb.active)
def sheet(name, header, rows):
    w = wb.create_sheet(name[:31]); w.append(header)
    for r in rows: w.append(r)
    for c in w[1]: c.font = Font(bold=True)
    for col in w.columns: w.column_dimensions[col[0].column_letter].width = min(70, max(9, max(len(str(c.value or "")) for c in col) + 2))
    for row in w.iter_rows(min_row=2):
        for c in row: c.alignment = Alignment(wrap_text=True, vertical="top")
    w.freeze_panes = "A2"; return w
pc = lambda v: None if v is None else round(v * 100, 1)
H = ["Hora", "Partido", "Selección", "Cuota", "P mercado %", "P modelo %", "P central %", "Brecha pp", "EV central %", "Solidez agente", "Rotación (local|visit.)", "Veto rot.", "Escenario de pérdida"]
row = lambda l: [l["hora"], l["partido"], l["seleccion"], l["cuota"], pc(l["p_mercado"]), pc(l["p_modelo"]), pc(l["p_central"]), None if l["brecha"] is None else round(l["brecha"] * 100), pc(l["ev_central"]), l["solidez"], f"{l['rot_local']} | {l['rot_visit']}", l["rotacion"] or "", l["escenario"]]
# 1 resumen
sheet("Léeme", ["Nota"], ([[f"PREPARACIÓN PARA APOSTAR (independiente de la certificación): {(_cov or {}).get('preparacion_para_apostar', {}).get('estado', 'NO_EVALUADA')}. El nombre del archivo y «investigación certificada» NO equivalen a una aprobación para apostar."]] if True else []) + ([["NO CERTIFICADO COMO EXHAUSTIVO: " + w] for w in _why] + [["Este libro usa solo 1X2 y una línea de goles de la captura (catálogo parcial)."]] if not _ok else []) + [["Solo patas con cuota ≤ 2.10 de TU casa (capturas del 14-oct, horas de Caracas)."], ["P mercado = probabilidad sin margen de tu casa; P modelo = Poisson ataque/defensa v0 (el backtest muestra que NO supera al mercado); P central = 80 % mercado + 20 % modelo."],
    ["EV central = P central × cuota − 1: es una referencia, no un veredicto (casi siempre negativa por el margen de la casa)."], ["Brecha = modelo − mercado; |brecha| ≥ 15 pp = señal de ruido o de información que el modelo no ve."],
    ["Solidez ALTA/MEDIA/BAJA = juicio del analista deportivo con k/n, forma, rotación y escenario de pérdida. Los rankings excluyen las patas BAJA y las vetadas por rotación."],
    ["Sin alineaciones ni bajas verificadas (la API las trae vacías); rotación a priori calculada por descanso y cambios recientes."], ["Córners y tarjetas: sin cuota en tu casa; van como información en la hoja «Mercados extra»."]])
# 2 por liga
ligas = []
for m in D:
    if m["liga"] not in ligas: ligas.append(m["liga"])
for lg in ligas:
    sheet(lg.replace("(", "").replace(")", "")[:28], H, [row(l) for l in legs if l["liga"] == lg])
sheet("Ranking seguridad", ["#", "Liga"] + H, [[i, l["liga"]] + row(l) for i, l in enumerate(SEC[:25], 1)])
sheet("Ranking atractivo-cuota", ["#", "Liga"] + H, [[i, l["liga"]] + row(l) for i, l in enumerate(ATR[:25], 1)])
tops = []
for lg in ligas:
    for i, l in enumerate([x for x in SEC if x["liga"] == lg][:3], 1): tops.append(["Seguridad", lg, i] + row(l))
    for i, l in enumerate([x for x in ATR if x["liga"] == lg][:3], 1): tops.append(["Atractivo", lg, i] + row(l))
sheet("Top por liga", ["Ranking", "Liga", "#"] + H, tops)
crow = []
for nm, lst in combos.items():
    for k, (pj, odds, pm, c) in enumerate(lst, 1):
        ev = pm * odds - 1
        for x in c: crow.append([nm, k, round(odds, 2), pc(pj), pc(pm), pc(1 - pm), pc(ev), T.risk_label(pm, ev), ("APTA" if MC.MODEL_VALIDATION["nivel"] == "suficiente" else "NO_APTA (modelo sin validar)")] + [x["hora"], x["partido"], x["seleccion"], x["cuota"], pc(x["p_central"]), x["solidez"]])
sheet("Combinadas", ["Rango", "Opción", "Cuota total", "P gana central %", "P gana mercado %", "P pierde mercado %", "EV mercado %", "Rótulo de riesgo", "Preparación para apostar", "Hora", "Partido", "Selección", "Cuota", "P central %", "Solidez"], crow)
ex = []
for p, v in AG.items():
    for e in v.get("mercados_extra", []) or []:
        ex.append([p, e.get("mercado"), e.get("linea"), e.get("frecuencia"), e.get("solidez"), e.get("nota")])
sheet("Mercados extra", ["Partido", "Mercado", "Línea", "Frecuencia", "Solidez", "Nota"], ex)
sheet("Resumen por partido", ["Partido", "Resumen", "Árbitro", "Alineaciones/bajas"], [[p, v.get("resumen"), v.get("arbitro"), v.get("alineaciones_bajas")] for p, v in AG.items()])
if _cov:
    _w = wb.create_sheet("Cobertura (3 controles)")
    for r in [["Control", "Estado", "Incidencias principales"],
              ["A. Investigación", _cov["investigacion"]["estado"], "; ".join(f"{i['tipo']}: {i['cantidad']}" for i in _cov["investigacion"]["incidencias"][:5]) or "ninguna"],
              ["B. Analítica (datos / estimador / validación)", _cov["analitica"]["estado"], "; ".join(f"{i['tipo']}: {i['cantidad']}" for i in _cov["analitica"]["incidencias"][:5]) or "ninguna"],
              ["C. Precios (límite individual 2.10)", _cov["precios"]["estado"], "; ".join(f"{i['tipo']}: {i['cantidad']}" for i in _cov["precios"]["incidencias"][:5]) or "ninguna"],
              ["D. Preparación para apostar (independiente)", _cov["preparacion_para_apostar"]["estado"], "requisitos incumplidos: " + ", ".join(f"{k}: {v}" for k, v in _cov["preparacion_para_apostar"].get("requisitos_incumplidos", {}).items())]]:
        _w.append(r)
os.makedirs(_args.out_dir, exist_ok=True)
wb.save(OUT)
print(len(legs), "patas;", {k: len(v) for k, v in combos.items()}, "pool", len(pool))
for nm, lst in combos.items():
    for pj, odds, pm, c in lst[:1]: print(nm, round(odds, 2), round(pj, 3), round(pm, 3), [(x["partido"], x["seleccion"], x["cuota"], x["solidez"]) for x in c])
