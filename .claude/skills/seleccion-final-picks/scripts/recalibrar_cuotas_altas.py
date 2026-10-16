#!/usr/bin/env python3
"""¿Mejora la calibración recortar la P del modelo en cuotas altas (≥ 1.8)? Prueba FUERA DE MUESTRA entre runs (se ajusta con un run y se evalúa en el otro, y al revés) con tres recortes
derivados de los datos de entrenamiento (sin pesos arbitrarios):  desplazamiento p−δ · encogimiento hacia 1/cuota · logística (Platt) en la banda.
Métricas: Brier, log-loss, P media vs frecuencia real; diferencia de Brier contra «sin recorte» con IC remuestreando partidos. Es un ANÁLISIS: no modifica el modelo ni la recalibración vigente.
Uso:  recalibrar_cuotas_altas.py --ledger data/ledger_patas.jsonl --doc docs/RECALIBRACION-cuotas-altas.md --out data/recalib_cuotas_altas.json [--min 1.8 --max 2.10]"""
import argparse
import json
import math
import os
import random
import sys
from collections import defaultdict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import acumulado as acu  # noqa: E402

EPS = 1e-4


def _clip(p):
    return min(1 - EPS, max(EPS, p))


def _logit(p):
    p = _clip(p)
    return math.log(p / (1 - p))


def _sig(x):
    return 1 / (1 + math.exp(-x))


def banda(rows, lo, hi):
    return [r for r in rows if lo <= r["cuota"] <= hi and r["p"] >= 0.5]


def fit_shift(tr):
    return {"delta": sum(r["p"] - (1 if r["res"] == acu.WIN else 0) for r in tr) / len(tr)}


def fit_shrink(tr):
    num = den = 0.0
    for r in tr:
        y, p, q = (1 if r["res"] == acu.WIN else 0), r["p"], 1 / r["cuota"]
        num += (y - p) * (q - p)
        den += (q - p) ** 2
    return {"w": (num / den) if den else 0.0}


def fit_platt(tr, it=50):
    a, b = 0.0, 1.0
    for _ in range(it):
        g = [0.0, 0.0]
        h = [[1e-6, 0.0], [0.0, 1e-6]]
        for r in tr:
            y = 1 if r["res"] == acu.WIN else 0
            x = _logit(r["p"])
            p = _sig(a + b * x)
            g[0] += p - y
            g[1] += (p - y) * x
            w = p * (1 - p)
            h[0][0] += w
            h[0][1] += w * x
            h[1][0] += w * x
            h[1][1] += w * x * x
        det = h[0][0] * h[1][1] - h[0][1] * h[1][0]
        if abs(det) < 1e-12:
            break
        da = (h[1][1] * g[0] - h[0][1] * g[1]) / det
        db = (-h[1][0] * g[0] + h[0][0] * g[1]) / det
        a, b = a - da, b - db
        if abs(da) + abs(db) < 1e-8:
            break
    return {"a": a, "b": b}


def fit_const(tr):
    return {"c": sum(1 for r in tr if r["res"] == acu.WIN) / len(tr)}


def apply(method, par, r):
    p = r["p"]
    if method == "sin recorte":
        return p
    if method == "desplazamiento":
        return _clip(p - par["delta"])
    if method == "frecuencia de la banda":
        return _clip(par["c"])
    if method == "encogimiento a 1/cuota":
        return _clip(p + par["w"] * (1 / r["cuota"] - p))
    return _sig(par["a"] + par["b"] * _logit(p))


FITS = {"frecuencia de la banda": fit_const, "desplazamiento": fit_shift, "encogimiento a 1/cuota": fit_shrink, "logística (Platt)": fit_platt}


def brier(rs, ps):
    return sum((p - (1 if r["res"] == acu.WIN else 0)) ** 2 for r, p in zip(rs, ps)) / len(rs)


def logloss(rs, ps):
    return -sum((1 if r["res"] == acu.WIN else 0) * math.log(_clip(p)) + (0 if r["res"] == acu.WIN else 1) * math.log(1 - _clip(p)) for r, p in zip(rs, ps)) / len(rs)


def cluster_diff(rs, p0, p1, b=2000, seed=7):
    """IC 95 % de Brier(recorte) − Brier(sin recorte) remuestreando partidos; negativo = el recorte mejora."""
    g = defaultdict(lambda: [0.0, 0])
    for r, a, c in zip(rs, p0, p1):
        y = 1 if r["res"] == acu.WIN else 0
        k = (r["run"], r["partido_id"])
        g[k][0] += (c - y) ** 2 - (a - y) ** 2
        g[k][1] += 1
    ks = list(g.values())
    if len(ks) < 2:
        return None
    rnd = random.Random(seed)
    out = []
    for _ in range(b):
        s = n = 0
        for k in (ks[rnd.randrange(len(ks))] for _ in ks):
            s += k[0]
            n += k[1]
        out.append(s / n)
    out.sort()
    return out[int(0.025 * b)], out[int(0.975 * b) - 1]


def evaluar(ledger, lo, hi):
    rows = acu.liquidadas(acu.leer(ledger), False)
    runs = sorted({r["run"] for r in rows})
    res = {"banda": [lo, hi], "runs": runs, "folds": [], "agrupado": {}}
    oof = defaultdict(list)                                           # método -> [(fila, p_recortada)]
    base_n = []
    for test in runs:
        tr = banda([r for r in rows if r["run"] != test], lo, hi)
        te = banda([r for r in rows if r["run"] == test], lo, hi)
        if len(tr) < 30 or len(te) < 30:
            continue
        fold = {"test": test, "n_train": len(tr), "n_test": len(te), "frec_train": round(sum(r["res"] == acu.WIN for r in tr) / len(tr), 3), "frec_test": round(sum(r["res"] == acu.WIN for r in te) / len(te), 3),
                "p_media_test": round(sum(r["p"] for r in te) / len(te), 3), "metodos": {}}
        for r in te:
            oof["sin recorte"].append((r, r["p"]))
        fold["metodos"]["sin recorte"] = {"brier": round(brier(te, [r["p"] for r in te]), 4), "logloss": round(logloss(te, [r["p"] for r in te]), 4)}
        for name, fit in FITS.items():
            par = fit(tr)
            ps = [apply(name, par, r) for r in te]
            fold["metodos"][name] = {"parametros": {k: round(v, 4) for k, v in par.items()}, "p_media": round(sum(ps) / len(ps), 3), "brier": round(brier(te, ps), 4), "logloss": round(logloss(te, ps), 4)}
            oof[name] += list(zip(te, ps))
        res["folds"].append(fold)
    if oof.get("sin recorte"):
        rs = [r for r, _ in oof["sin recorte"]]
        p0 = [p for _, p in oof["sin recorte"]]
        for name in ["sin recorte"] + list(FITS):
            if name not in oof:
                continue
            idx = {id(r): p for r, p in oof[name]}
            ps = [idx[id(r)] for r in rs]
            d = {"n": len(rs), "p_media": round(sum(ps) / len(ps), 3), "frecuencia": round(sum(r["res"] == acu.WIN for r in rs) / len(rs), 3), "brier": round(brier(rs, ps), 4), "logloss": round(logloss(rs, ps), 4)}
            if name != "sin recorte":
                ci = cluster_diff(rs, p0, ps)
                d["delta_brier_vs_sin_recorte"] = round(brier(rs, ps) - brier(rs, p0), 4)
                d["ic95_delta_brier"] = None if ci is None else [round(ci[0], 4), round(ci[1], 4)]
            res["agrupado"][name] = d
    # parámetros ajustados con TODO el registro (candidatos; no se aplican)
    todo = banda(rows, lo, hi)
    if todo:
        res["ajuste_completo"] = {"n": len(todo), "frecuencia": round(sum(r["res"] == acu.WIN for r in todo) / len(todo), 3), "p_media": round(sum(r["p"] for r in todo) / len(todo), 3),
                                  **{name: {k: round(v, 4) for k, v in fit(todo).items()} for name, fit in FITS.items()}}
    return res


def render(res):
    L = ["# Recorte de P en cuotas altas — prueba fuera de muestra", ""]
    lo, hi = res["banda"]
    L.append(f"Banda de cuota {lo}–{hi}, lado favorecido por el modelo (P ≥ 50 %). Runs en el registro: {', '.join(x.split('/')[-1] for x in res['runs'])}. Ajuste con un run, evaluación en el otro (y al revés). **Análisis: no se aplica al modelo.**")
    L.append("")
    if not res["folds"]:
        L.append("No hay suficientes patas (≥ 30 por run en la banda) para una prueba cruzada.")
        return "\n".join(L) + "\n"
    L += ["## Por pliegue (se ajusta con el otro run)", "", "| Evaluado en | n ajuste | n prueba | Frecuencia real | P media | Método | P media recortada | Brier | Log-loss |", "|---|---|---|---|---|---|---|---|---|"]
    for f in res["folds"]:
        for name, m in f["metodos"].items():
            L.append(f"| {f['test'].split('/')[-1]} | {f['n_train']} | {f['n_test']} | {f['frec_test']:.1%} | {f['p_media_test']:.1%} | {name} | {'' if 'p_media' not in m else format(m['p_media'], '.1%')} | {m['brier']} | {m['logloss']} |")
    L += ["", "## Agrupado fuera de muestra", "", "| Método | n | P media | Frecuencia real | Brier | Δ Brier vs sin recorte | IC 95 % Δ (por partido) | Log-loss |", "|---|---|---|---|---|---|---|---|"]
    for name, d in res["agrupado"].items():
        L.append(f"| {name} | {d['n']} | {d['p_media']:.1%} | {d['frecuencia']:.1%} | {d['brier']} | {d.get('delta_brier_vs_sin_recorte', '—')} | {d.get('ic95_delta_brier') or '—'} | {d['logloss']} |")
    mejora = [n for n, d in res["agrupado"].items() if d.get("ic95_delta_brier") and d["ic95_delta_brier"][1] < 0]
    L += ["", "## Lectura", "",
          ("Mejoran el Brier con IC que excluye 0: " + ", ".join(mejora) + "." if mejora else "Ningún recorte mejora el Brier con un IC que excluya 0: con tan pocos runs/partidos la mejora, si existe, no se distingue del ruido."),
          "Δ Brier negativo = el recorte mejora. El IC remuestrea partidos completos. Con 2 runs cada pliegue se ajusta con un solo día; el resultado puede cambiar al sumar jornadas.",
          "La pendiente de la logística en la banda es la prueba de si la P del modelo ordena patas DENTRO de la banda: pendiente ≤ 0 = no discrimina (solo sirve la tasa base de la banda). El encogimiento con w > 1 sobrepasa 1/cuota y no es defendible como regla.",
          "El recorte solo se promovería a la recalibración vigente tras repetirse en más días; hoy es un candidato.", ""]
    if "ajuste_completo" in res:
        a = res["ajuste_completo"]
        L += ["## Parámetros candidatos (ajustados con todo el registro; NO aplicados)", "", f"n={a['n']}, frecuencia real {a['frecuencia']:.1%}, P media {a['p_media']:.1%}.", ""]
        for k, v in a.items():
            if isinstance(v, dict):
                L.append(f"- {k}: {v}")
    return "\n".join(L) + "\n"


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--ledger", default="data/ledger_patas.jsonl")
    ap.add_argument("--doc", default="docs/RECALIBRACION-cuotas-altas.md")
    ap.add_argument("--out", default="data/recalib_cuotas_altas.json")
    ap.add_argument("--min", type=float, default=1.8)
    ap.add_argument("--max", type=float, default=2.10)
    a = ap.parse_args(argv)
    res = evaluar(a.ledger, a.min, a.max)
    res["estado"] = "candidato: análisis fuera de muestra; no aplicado al modelo"
    os.makedirs(os.path.dirname(a.out) or ".", exist_ok=True)
    with open(a.out, "w", encoding="utf-8") as fh:
        json.dump(res, fh, ensure_ascii=False, indent=1)
    os.makedirs(os.path.dirname(a.doc) or ".", exist_ok=True)
    with open(a.doc, "w", encoding="utf-8") as fh:
        fh.write(render(res))
    print(render(res))
    return 0


if __name__ == "__main__":
    sys.exit(main())
