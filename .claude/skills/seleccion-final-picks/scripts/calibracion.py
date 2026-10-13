#!/usr/bin/env python3
"""Calibración del sistema a partir de `seguimiento/registro_resultados.jsonl`: Brier, log-loss, tasa de acierto y ROI (1 unidad por pata) por tipo de mercado,
rango de cuota y dirección, con intervalo de Wilson. Regla de la auditoría 13-oct: con menos de 30 patas por tipo NO se concluye; se congela un tipo con ROI < −10 % y n ≥ 30.
Uso: calibracion.py --run runs/2026-10-13 [--origen sistema|usuario]"""
import argparse
import json
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common  # noqa: E402

MIN_N = 30
FREEZE_ROI = -0.10


def wilson(k, n, z=1.2816):
    if n == 0:
        return (0.0, 1.0)
    p = k / n
    d = 1 + z * z / n
    c = p + z * z / (2 * n)
    r = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n))
    return ((c - r) / d, (c + r) / d)


def kind_of(row):
    m = row["mercado"].lower()
    if "menos" in m or " u" in " " + m[:3] or m.startswith("total u"):
        direction = "under"
    elif "más" in m or m.startswith("total o"):
        direction = "over"
    else:
        direction = "otro"
    fam = "goles" if m.startswith("total") else ("tarjetas" if "tarjeta" in m else ("córners" if "córner" in m or "corner" in m else ("hándicap" if "hándicap" in m else "resultado/otro")))
    return fam, direction


def odds_bucket(c):
    return "<1.30" if c < 1.30 else ("1.30–1.59" if c < 1.60 else ("1.60–1.99" if c < 2.0 else "≥2.00"))


def evaluate(rows):
    done = [r for r in rows if r.get("resultado") in ("ACERTADA", "FALLADA") and r.get("p_mercado_sin_margen_aprox") is not None]
    hit = [1 if r["resultado"] == "ACERTADA" else 0 for r in done]
    n = len(done)
    out = {"n": n}
    if n:
        ps = [r["p_mercado_sin_margen_aprox"] for r in done]
        out["brier"] = round(sum((p - y) ** 2 for p, y in zip(ps, hit)) / n, 4)
        out["log_loss"] = round(-sum(y * math.log(max(p, 1e-9)) + (1 - y) * math.log(max(1 - p, 1e-9)) for p, y in zip(ps, hit)) / n, 4)
        out["aciertos_esperados"] = round(sum(ps), 2)
        out["aciertos_reales"] = sum(hit)
    groups = {}
    for r, y in zip(done, hit):
        fam, d = kind_of(r)
        for label in (f"mercado:{fam}", f"direccion:{d}", f"cuota:{odds_bucket(r['cuota'])}"):
            groups.setdefault(label, []).append((y, r["cuota"]))
    out["grupos"] = {}
    for label, xs in sorted(groups.items()):
        k, m = sum(y for y, _ in xs), len(xs)
        roi = sum((c - 1) if y else -1 for y, c in xs) / m
        lo, hi = wilson(k, m)
        action = "sin base estadística (n<30)" if m < MIN_N else ("CONGELAR tipo" if roi < FREEZE_ROI else "mantener")
        out["grupos"][label] = {"n": m, "aciertos": k, "tasa": round(k / m, 3), "wilson80": [round(lo, 3), round(hi, 3)], "roi": round(roi, 3), "accion": action}
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--run", default="runs/2026-10-13")
    ap.add_argument("--origen", default=None)
    a = ap.parse_args(argv)
    path = os.path.join(a.run, "seguimiento", "registro_resultados.jsonl")
    rows = [json.loads(x) for x in open(path, encoding="utf-8") if x.strip()]
    if a.origen:
        rows = [r for r in rows if r.get("origen", "").startswith(a.origen)]
    res = evaluate(rows)
    common.write_json_atomic(os.path.join(a.run, "seguimiento", "calibracion.json"), res)
    print(json.dumps(res, ensure_ascii=False, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
