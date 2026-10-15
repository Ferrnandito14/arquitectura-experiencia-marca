#!/usr/bin/env python3
"""Backtest del modelo propio contra las cuotas de CIERRE de TheStatsAPI (`tsa_history.py` → data/tsa_closing_odds.json).

Cada partido se predice SOLO con partidos anteriores de su liga (walk-forward, como en backtest_modelo.py) y se compara con la probabilidad sin margen del mercado al cierre
(mediana entre casas; cierre aproximado = último precio visto). Métricas por familia: Brier y log-loss del modelo, del modelo recalibrado y del mercado, diferencia con IC 95 % (bootstrap de partidos),
mezcla modelo/mercado con peso elegido en la 1.ª mitad (por fecha) y evaluado en la 2.ª, y ROI de las selecciones donde el modelo ve ventaja (≥ 3 y ≥ 5 pp) a la cuota mediana de cierre.
La recalibración usa los parámetros ajustados ANTES del corte (`a_train`, `b_train`), nunca los de todo el periodo (sin fuga).
Escribe `docs/BACKTEST-cierre.md`, `data/model_blend.json` (pesos medidos; NO se aplican: el sistema sigue sin depender de ningún mercado) y, con --write-validation, la decisión por familia.
Uso: backtest_cierre.py --runs runs/2026-10-14 … [--closing data/tsa_closing_odds.json] [--cal data/model_calibration.json] [--doc docs/BACKTEST-cierre.md] [--write-validation data/model_validation.json]"""
import argparse
import json
import os
import random
import sys
from datetime import datetime, timezone

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import backtest_modelo as bt  # noqa: E402
import common  # noqa: E402
import model_calibration as mcal  # noqa: E402
import tsa_history  # noqa: E402

EDGES = (0.03, 0.05)


def market_for(pred, c):
    """(p_mercado, cuota_mediana | None) del cierre para una predicción del backtest, o None si el mercado no lo cotiza."""
    fam, mk = pred["familia"], pred["mercado"]
    if fam == "goals_total":
        x = (c.get("goles") or {}).get(mk.split("_", 1)[1])
        return (x["p"], x["cuota"]) if x else None
    if fam == "btts":
        x = c.get("btts")
        return (x["p"], x["cuota"]) if x else None
    if fam == "1x2" and c.get("1x2"):
        i = {"1": 0, "X": 1, "2": 2}[mk]
        return c["1x2"]["p"][i], c["1x2"]["cuota"][i]
    if fam == "dc" and c.get("1x2"):
        p = c["1x2"]["p"]
        return (p[0] + p[1] if mk == "1x" else p[1] + p[2]), None          # derivado del 1X2 sin margen: sin cuota propia (no se calcula ROI)
    if fam == "team_goals":
        side, _o, line = mk.split("_")
        x = (c.get("equipo") or {}).get(f"{side}:{line}")
        return (x["p"], x["cuota"]) if x else None
    if fam == "corners_total":
        x = (c.get("corners") or {}).get(mk.split("_", 1)[1])
        return (x["p"], x["cuota"]) if x else None
    return None


def cluster_ci(pairs, reps=1000, seed=7):
    """IC 95 % de la media de valores agrupados por partido: pairs = {partido: [valores]}."""
    keys = list(pairs)
    rnd = random.Random(seed)
    out = []
    for _ in range(reps):
        s = n = 0.0
        for _i in range(len(keys)):
            v = pairs[keys[rnd.randrange(len(keys))]]
            s += sum(v)
            n += len(v)
        out.append(s / n if n else 0.0)
    out.sort()
    return round(out[int(0.025 * reps)], 4), round(out[int(0.975 * reps)], 4)


def brier(p, y):
    return (p - y) ** 2


def evaluate(records, cal):
    out = {}
    for fam in sorted({r["familia"] for r in records}):
        rs = sorted((r for r in records if r["familia"] == fam), key=lambda r: (r["fecha"], r["partido"]))
        g = mcal.group_of_family(fam)
        info = (cal or {}).get("grupos", {}).get(g) or {}
        for r in rs:
            r["p_cal"] = float(mcal.calibrate(r["p_modelo"], info["a_train"], info["b_train"])) if "a_train" in info else r["p_modelo"]
        base = bt.evaluate_vs_market(rs)[fam]
        per_cal, per_mkt = {}, {}
        for r in rs:
            per_cal.setdefault(r["partido"], []).append(brier(r["p_cal"], r["y"]) - brier(r["p_mercado"], r["y"]))
        d_cal = cluster_ci(per_cal)
        base["brier_modelo_recalibrado"] = round(sum(brier(r["p_cal"], r["y"]) for r in rs) / len(rs), 4)
        base["diff_brier_recalibrado_menos_mercado"] = list(d_cal)
        # mezcla: peso elegido en la 1.ª mitad por fecha y evaluado en la 2.ª
        half = len(rs) // 2
        a, b = rs[:half], rs[half:]
        grid = [i / 20 for i in range(21)]
        w_best = min(grid, key=lambda w: sum(brier(w * r["p_cal"] + (1 - w) * r["p_mercado"], r["y"]) for r in a)) if a else 0.0
        if b:
            base["mezcla"] = {"peso_modelo_elegido_1a_mitad": w_best, "brier_2a_mitad_mezcla": round(sum(brier(w_best * r["p_cal"] + (1 - w_best) * r["p_mercado"], r["y"]) for r in b) / len(b), 4),
                              "brier_2a_mitad_mercado": round(sum(brier(r["p_mercado"], r["y"]) for r in b) / len(b), 4),
                              "brier_2a_mitad_modelo_recalibrado": round(sum(brier(r["p_cal"], r["y"]) for r in b) / len(b), 4)}
        # ROI por ventaja del modelo (recalibrado) sobre el mercado
        roi = {}
        for e in EDGES:
            sel = [r for r in rs if r.get("cuota") and r["p_cal"] - r["p_mercado"] >= e]
            if len(sel) >= 30:
                per = {}
                for r in sel:
                    per.setdefault(r["partido"], []).append((r["cuota"] - 1) if r["y"] else -1.0)
                roi[f"ventaja>={int(e * 100)}pp"] = {"n": len(sel), "roi": round(sum(sum(v) for v in per.values()) / len(sel), 4), "ic95": list(cluster_ci(per))}
        base["roi_por_ventaja"] = roi
        out[fam] = base
    return out


def _fmt(x):
    """[dif, lo, hi] o [lo, hi] → «dif [lo, hi]» (sin dif cuando solo vienen los extremos del IC)."""
    return f"{x[0]:+.4f} [{x[1]:+.4f}, {x[2]:+.4f}]" if len(x) == 3 else f"[{x[0]:+.4f}, {x[1]:+.4f}]"


def render(res):
    L = ["# Backtest del modelo propio contra cuotas de cierre (TheStatsAPI)", "",
         f"Generado: {res['generado_utc']} · partidos con cuotas: {res['partidos_con_cuotas']} · predicciones emparejadas: {res['predicciones']} · corte de la recalibración: {res['corte']}", "",
         "Cierre aproximado = último precio visto; probabilidad del mercado sin margen, mediana entre casas. Cada partido se predice solo con partidos anteriores de su liga. Diferencias = modelo − mercado (negativo = el modelo predice mejor).", "",
         "| Familia | Partidos | Brier modelo | Brier recalibrado | Brier mercado | Dif. modelo [IC 95 %] | Dif. recalibrado [IC 95 %] | Frente al mercado |", "|---|---|---|---|---|---|---|---|"]
    for f, v in res["familias"].items():
        L.append(f"| {f} | {v['partidos']} | {v['brier_modelo']} | {v['brier_modelo_recalibrado']} | {v['brier_mercado']} | {_fmt(v['diff_brier_modelo_menos_mercado'])} | {_fmt(v['diff_brier_recalibrado_menos_mercado'])} | {v['vs_mercado']} |")
    L += ["", "## Mezcla modelo/mercado (peso elegido en la 1.ª mitad, medido en la 2.ª)", "", "| Familia | Peso del modelo | Brier mezcla | Brier mercado | Brier modelo recal. |", "|---|---|---|---|---|"]
    for f, v in res["familias"].items():
        m = v.get("mezcla")
        if m:
            L.append(f"| {f} | {m['peso_modelo_elegido_1a_mitad']} | {m['brier_2a_mitad_mezcla']} | {m['brier_2a_mitad_mercado']} | {m['brier_2a_mitad_modelo_recalibrado']} |")
    L += ["", "## ROI de las selecciones donde el modelo (recalibrado) ve ventaja sobre el mercado (cuota mediana de cierre, 1 u por selección)", "", "| Familia | Ventaja | n | ROI | IC 95 % |", "|---|---|---|---|---|"]
    for f, v in res["familias"].items():
        for k, r in (v.get("roi_por_ventaja") or {}).items():
            L.append(f"| {f} | {k} | {r['n']} | {r['roi']} | {r['ic95']} |")
    L += ["", "## Lectura", "", res["lectura"], "", "Limitaciones: es un cierre aproximado (último precio visto, no siempre el cierre real); la muestra de partidos con cuotas es un subconjunto del periodo y de las ligas; las tarjetas no se contrastan porque la definición de la fuente no está confirmada."]
    return "\n".join(L) + "\n"


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--runs", nargs="+", required=True)
    ap.add_argument("--closing", default="data/tsa_closing_odds.json")
    ap.add_argument("--cal", default=mcal.DEFAULT_PATH)
    ap.add_argument("--doc")
    ap.add_argument("--out-json")
    ap.add_argument("--blend-out")
    ap.add_argument("--write-validation")
    a = ap.parse_args(argv)
    closing = common.read_json(a.closing)["partidos"]
    cal = common.read_json(a.cal, None)
    rows = {lid: list(v.values()) for lid, v in tsa_history.load_rows(a.runs).items()}
    preds = bt.walk_forward(rows)
    recs = []
    for p in preds:
        c = closing.get(p["partido"])
        if not c:
            continue
        m = market_for(p, c)
        if m is None:
            continue
        recs.append({"partido": p["partido"], "fecha": p["fecha"], "familia": p["familia"], "mercado": p["mercado"], "p_modelo": p["p"], "p_mercado": m[0], "cuota": m[1], "y": p["y"]})
    recs = [r for r in recs if r["familia"] != "cards_total"]
    fams = evaluate(recs, cal)
    wf = bt.summarize_walk_forward(preds)
    mejores = [f for f, v in fams.items() if v["vs_mercado"] == "no_peor"]
    peores = [f for f, v in fams.items() if v["vs_mercado"] == "peor"]
    ruido = [f for f, v in fams.items() if v["diff_brier_recalibrado_menos_mercado"][0] <= 0 <= v["diff_brier_recalibrado_menos_mercado"][1]]
    lectura = (f"Familias donde el modelo no es peor que el mercado: {', '.join(mejores) or 'ninguna'}. Familias donde es peor con IC que excluye 0: {', '.join(peores) or 'ninguna'}. "
               f"Con la recalibración (parámetros ajustados antes del corte) la diferencia con el mercado ya no se distingue de cero en: {', '.join(ruido) or 'ninguna'} (no es lo mismo que superarlo: la mezcla óptima da casi todo el peso al mercado). "
               "El mercado incorpora información (alineaciones, lesiones, dinero) que el modelo no ve; una mezcla solo se aplicaría con el peso medido aquí y el sistema no depende de ninguna casa, así que los pesos se guardan como evidencia y no se usan en producción.")
    res = {"generado_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"), "partidos_con_cuotas": len({r["partido"] for r in recs}), "predicciones": len(recs),
           "corte": (cal or {}).get("grupos", {}).get("_corte_fecha"), "familias": fams, "lectura": lectura}
    if a.out_json:
        common.write_json_atomic(a.out_json, res)
    if a.doc:
        with open(a.doc, "w", encoding="utf-8") as f:
            f.write(render(res))
    if a.blend_out:
        common.write_json_atomic(a.blend_out, {"generado_utc": res["generado_utc"], "nota": "pesos medidos fuera de muestra; NO se aplican en producción", "pesos": {f: v.get("mezcla", {}).get("peso_modelo_elegido_1a_mitad") for f, v in fams.items()}})
    if a.write_validation:
        val = bt.decide_validation(wf, fams)
        val["referencia"] = "docs/BACKTEST-cierre.md"
        common.write_json_atomic(a.write_validation, val)
    print(f"{res['partidos_con_cuotas']} partidos con cuotas; {res['predicciones']} predicciones")
    for f, v in fams.items():
        print(f"  {f}: n={v['partidos']} Brier modelo {v['brier_modelo']} recal {v['brier_modelo_recalibrado']} mercado {v['brier_mercado']} dif {v['diff_brier_modelo_menos_mercado']} → {v['vs_mercado']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
