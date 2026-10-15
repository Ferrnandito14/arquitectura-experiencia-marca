#!/usr/bin/env python3
"""Recalibración de las probabilidades del modelo propio (independiente de cualquier casa: solo usa RESULTADOS pasados).

Motivo (comparativo del 14-oct): en las patas de 75–85 % el modelo esperaba 79.6 % y acertó 72.5 % (sobreconfianza ≈ 7 pp); en las de 0–30 % esperaba 18 % y acertó 26 %.
Método declarado (política, no un hecho estadístico): por grupo de mercado, regresión logística de recalibración  p' = σ(a·logit(p) + b)  ajustada por máxima verosimilitud con las
predicciones WALK-FORWARD del modelo (cada partido se predice solo con partidos anteriores de su liga) y sus resultados reales.
Validación FUERA DE TIEMPO: se ajusta con el 60 % más antiguo de las fechas y se mide en el 40 % más reciente (Brier y log-loss, IC 95 % por bootstrap de partidos).
Solo se APLICA un grupo si mejora el Brier fuera de tiempo con IC que excluye 0 y no empeora el log-loss; si no, queda `aplicar: false` (identidad) y se dice.
Uso:  model_calibration.py fit --runs runs/2026-10-14 … [--out data/model_calibration.json] [--doc docs/BACKTEST-calibracion.md]
      (desde código)  model_calibration.apply(clave_del_modelo, p) → p calibrada si el grupo está aplicado; de lo contrario p sin cambios."""
import argparse
import json
import math
import os
import random
import sys
from datetime import datetime, timezone

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common  # noqa: E402

DEFAULT_PATH = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "..", "data", "model_calibration.json"))
MIN_TRAIN = 300
BOOT = 1000
SEED = 7
EPS = 1e-4
_CACHE = {}


def group_of_family(fam):
    return fam if fam in ("goals_total", "btts", "1x2", "dc", "team_goals", "corners_total", "cards_total") else None


def group_of_key(key):
    """Grupo de calibración de una CLAVE del modelo (leg_model.model_probs / count_model.model_probs)."""
    if key.startswith("over_"):
        return "goals_total"
    if key == "btts":
        return "btts"
    if key in ("p1", "px", "p2"):
        return "1x2"
    if key in ("1x", "x2"):
        return "dc"
    if key.startswith(("home_over_", "away_over_")):
        return "team_goals"
    if key.startswith("corners_total_over_"):
        return "corners_total"
    if key.startswith("cards_total_over_"):
        return "cards_total"
    return None


def logit(p):
    p = np.clip(np.asarray(p, dtype=float), EPS, 1 - EPS)
    return np.log(p / (1 - p))


def sigmoid(z):
    return 1.0 / (1.0 + np.exp(-z))


def fit_platt(p, y, iters=60):
    """(a, b) por Newton-Raphson sobre el log-verosimilitud de y ~ σ(a·logit(p)+b)."""
    x, y = logit(p), np.asarray(y, dtype=float)
    a, b = 1.0, 0.0
    for _ in range(iters):
        q = sigmoid(a * x + b)
        g = np.array([np.sum((y - q) * x), np.sum(y - q)])
        w = q * (1 - q)
        H = np.array([[np.sum(w * x * x), np.sum(w * x)], [np.sum(w * x), np.sum(w)]]) + np.eye(2) * 1e-9
        step = np.linalg.solve(H, g)
        a, b = a + step[0], b + step[1]
        if np.max(np.abs(step)) < 1e-8:
            break
    return float(a), float(b)


def calibrate(p, a, b):
    return sigmoid(a * logit(p) + b)


def brier(p, y):
    return (np.asarray(p) - np.asarray(y)) ** 2


def logloss(p, y):
    p = np.clip(np.asarray(p, dtype=float), EPS, 1 - EPS)
    y = np.asarray(y, dtype=float)
    return -(y * np.log(p) + (1 - y) * np.log(1 - p))


def ece(p, y, bins=10):
    p, y = np.asarray(p), np.asarray(y)
    tot, n = 0.0, len(p)
    for k in range(bins):
        m = (p >= k / bins) & (p < (k + 1) / bins) if k < bins - 1 else (p >= k / bins)
        if m.any():
            tot += m.sum() / n * abs(p[m].mean() - y[m].mean())
    return float(tot)


def bootstrap_mean_diff(clusters, reps=BOOT, seed=SEED):
    """IC 95 % de la media de (a − b) remuestreando PARTIDOS (cada cluster = (suma_dif, n))."""
    rnd = random.Random(seed)
    k = len(clusters)
    out = []
    for _ in range(reps):
        s = n = 0.0
        for _i in range(k):
            c = clusters[rnd.randrange(k)]
            s += c[0]
            n += c[1]
        out.append(s / n)
    out.sort()
    return out[int(0.025 * reps)], out[int(0.975 * reps)]


def fit_groups(preds):
    """preds: [{fecha, partido, familia, p, y}] del walk-forward. Devuelve {grupo: info} con ajuste fuera de tiempo y ajuste final."""
    dates = sorted({p["fecha"] for p in preds})
    split = dates[int(len(dates) * 0.6)] if dates else None
    out = {"_corte_fecha": split}
    for g in sorted({group_of_family(p["familia"]) for p in preds} - {None}):
        ps = [p for p in preds if group_of_family(p["familia"]) == g]
        tr, te = [p for p in ps if p["fecha"] < split], [p for p in ps if p["fecha"] >= split]
        info = {"n_total": len(ps), "n_train": len(tr), "n_test": len(te), "aplicar": False}
        if len(tr) < MIN_TRAIN or len(te) < MIN_TRAIN // 2:
            info["motivo"] = "muestra insuficiente para ajustar y validar fuera de tiempo"
            out[g] = info
            continue
        a, b = fit_platt([p["p"] for p in tr], [p["y"] for p in tr])
        pt, yt = np.array([p["p"] for p in te]), np.array([p["y"] for p in te])
        pc = calibrate(pt, a, b)
        per = {}
        for p, raw, cal, yy in zip(te, pt, pc, yt):
            c = per.setdefault(p["partido"], [0.0, 0])
            c[0] += float(brier(cal, yy) - brier(raw, yy))
            c[1] += 1
        lo, hi = bootstrap_mean_diff(list(per.values()))
        ll_raw, ll_cal = float(logloss(pt, yt).mean()), float(logloss(pc, yt).mean())
        info.update({"a_train": round(a, 4), "b_train": round(b, 4), "brier_test_bruta": round(float(brier(pt, yt).mean()), 4), "brier_test_calibrada": round(float(brier(pc, yt).mean()), 4),
                     "dif_brier_ic95": [round(lo, 5), round(hi, 5)], "logloss_test_bruta": round(ll_raw, 4), "logloss_test_calibrada": round(ll_cal, 4),
                     "ece_test_bruta": round(ece(pt, yt), 4), "ece_test_calibrada": round(ece(pc, yt), 4)})
        info["aplicar"] = bool(hi < 0 and ll_cal <= ll_raw)
        info["motivo"] = ("mejora el Brier fuera de tiempo con IC que excluye 0 y no empeora el log-loss" if info["aplicar"]
                          else "no mejora de forma concluyente fuera de tiempo: se deja la probabilidad sin cambios")
        af, bf = fit_platt([p["p"] for p in ps], [p["y"] for p in ps])
        info["a"], info["b"] = round(af, 4), round(bf, 4)
        # curva de calibración fuera de tiempo (cruda vs calibrada)
        curve = []
        for k in range(10):
            m = (pt >= k / 10) & (pt < (k + 1) / 10 if k < 9 else pt <= 1.0)
            if m.sum() >= 20:
                curve.append({"bin": f"{k / 10:.1f}-{(k + 1) / 10:.1f}", "n": int(m.sum()), "p_bruta": round(float(pt[m].mean()), 3), "p_calibrada": round(float(pc[m].mean()), 3), "frecuencia": round(float(yt[m].mean()), 3)})
        info["curva_test"] = curve
        out[g] = info
    return out


def load(path=None):
    path = path or DEFAULT_PATH
    if path not in _CACHE:
        _CACHE[path] = common.read_json(path, None)
    return _CACHE[path]


def apply(key, p, path=None):
    """p calibrada si el grupo de la clave está aplicado; si no, p sin cambios. Devuelve (p, grupo|None, aplicada)."""
    g = group_of_key(key)
    cal = load(path)
    info = (cal or {}).get("grupos", {}).get(g) if g else None
    if not info or not info.get("aplicar") or "a" not in info:
        return p, g, False
    return float(calibrate(p, info["a"], info["b"])), g, True


def render_md(res):
    L = ["# Recalibración del modelo propio (fuera de tiempo)", "", f"Generado: {res['generado_utc']} · corte entre ajuste y prueba: {res['grupos'].get('_corte_fecha')}", "",
         "Método: `p' = σ(a·logit(p) + b)` por grupo de mercado, ajustado con predicciones walk-forward y resultados reales (sin cuotas de ninguna casa). Se aplica solo si mejora el Brier fuera de tiempo con IC 95 % que excluye 0 y no empeora el log-loss.", "",
         "| Grupo | n ajuste | n prueba | Brier bruta | Brier calibrada | Dif. IC 95 % | Log-loss bruta → cal. | ECE bruta → cal. | ¿Se aplica? |", "|---|---|---|---|---|---|---|---|---|"]
    for g, v in res["grupos"].items():
        if g.startswith("_"):
            continue
        if "brier_test_bruta" not in v:
            L.append(f"| {g} | {v['n_train']} | {v['n_test']} | — | — | — | — | — | no ({v['motivo']}) |")
            continue
        L.append(f"| {g} | {v['n_train']} | {v['n_test']} | {v['brier_test_bruta']} | {v['brier_test_calibrada']} | {v['dif_brier_ic95']} | {v['logloss_test_bruta']} → {v['logloss_test_calibrada']} | {v['ece_test_bruta']} → {v['ece_test_calibrada']} | {'**sí**' if v['aplicar'] else 'no'} |")
    L += ["", "## Curvas fuera de tiempo (probabilidad bruta → calibrada vs. frecuencia real)", ""]
    for g, v in res["grupos"].items():
        if g.startswith("_") or not v.get("curva_test"):
            continue
        L += [f"**{g}** (a={v.get('a')}, b={v.get('b')})", "", "| Tramo | n | p bruta | p calibrada | frecuencia real |", "|---|---|---|---|---|"]
        L += [f"| {c['bin']} | {c['n']} | {c['p_bruta']} | {c['p_calibrada']} | {c['frecuencia']} |" for c in v["curva_test"]]
        L.append("")
    L += ["Limitaciones: las predicciones del backtest usan las muestras de liga (últimos 10 partidos de la MISMA liga); el flujo de producción usa el historial de cada equipo (puede mezclar competiciones), así que la calibración es una aproximación. Un grupo sin mejora concluyente no se toca."]
    return "\n".join(L) + "\n"


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("cmd", choices=["fit"])
    ap.add_argument("--runs", nargs="+", required=True)
    ap.add_argument("--out", default=DEFAULT_PATH)
    ap.add_argument("--doc")
    a = ap.parse_args(argv)
    import backtest_modelo as bt
    from tsa_history import load_rows
    rows = {lid: list(v.values()) for lid, v in load_rows(a.runs).items()}
    preds = bt.walk_forward(rows)
    res = {"generado_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"), "n_predicciones": len(preds), "metodo": "p' = sigmoide(a*logit(p)+b) por grupo; ajuste walk-forward; validación fuera de tiempo 60/40", "grupos": fit_groups(preds)}
    common.write_json_atomic(a.out, res)
    if a.doc:
        with open(a.doc, "w", encoding="utf-8") as f:
            f.write(render_md(res))
    print(f"{len(preds)} predicciones walk-forward; corte {res['grupos']['_corte_fecha']}")
    for g, v in res["grupos"].items():
        if g.startswith("_"):
            continue
        print(f"  {g}: n_train={v['n_train']} n_test={v['n_test']} " + (f"Brier {v['brier_test_bruta']} → {v['brier_test_calibrada']} IC {v['dif_brier_ic95']} aplicar={v['aplicar']}" if "brier_test_bruta" in v else v["motivo"]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
