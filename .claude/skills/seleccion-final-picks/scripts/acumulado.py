#!/usr/bin/env python3
"""Estadística acumulada de los registros de patas y combinadas liquidadas (data/ledger_patas.jsonl, data/ledger_combinadas.jsonl).
- `cluster_ci`: IC 95 % de % acierto y ROI remuestreando PARTIDOS completos (las patas de un mismo partido no son independientes).
- `tabla`: agrupa el registro por una clave (ranking, banda de cuota, mercado, liga, estado de agentes, tipo y antigüedad de la cuota…) con ese IC.
- `curva_calibracion`: P del modelo vs frecuencia real por tramos, Brier, log-loss y ECE; `guardar_historial` añade una línea por día para ver cómo evoluciona.
Solo cuenta ganadas y perdidas (anuladas y sin dato quedan fuera). Es descriptivo: con pocos días NO valida ni descarta el modelo."""
import json
import math
import os
import random
from collections import defaultdict
from datetime import datetime, timezone

WIN, LOSE = "GANADA", "PERDIDA"


def payoff(res, odds):
    if res.startswith(WIN):
        return (odds - 1) * (0.5 if "½" in res else 1)
    if res.startswith(LOSE):
        return -0.5 if "½" in res else -1.0
    return None


def cluster_ci(items, b=2000, seed=7):
    """items: (res, cuota, p, cluster). ("lo–hi", "lo a hi") o ("n/d", "n/d") si hay < 2 grupos con patas liquidadas."""
    cl = defaultdict(lambda: [0, 0, 0.0])
    for it in items:
        r_, o = it[0], it[1]
        if not (r_.startswith(WIN) or r_.startswith(LOSE)) or not o:
            continue
        c = cl[it[3] if len(it) > 3 and it[3] is not None else id(it)]
        c[0] += 1 if r_.startswith(WIN) else 0
        c[1] += 1
        c[2] += payoff(r_, o)
    keys = list(cl.values())
    if len(keys) < 2:
        return "n/d", "n/d"
    rnd = random.Random(seed)
    accs, rois = [], []
    for _ in range(b):
        w = n = pf = 0
        for c in (keys[rnd.randrange(len(keys))] for _ in keys):
            w += c[0]
            n += c[1]
            pf += c[2]
        if n:
            accs.append(w / n * 100)
            rois.append(pf / n * 100)
    accs.sort()
    rois.sort()
    lo, hi = int(0.025 * len(accs)), int(0.975 * len(accs)) - 1
    return f"{accs[lo]:.1f}–{accs[hi]:.1f}", f"{rois[lo]:+.1f} a {rois[hi]:+.1f}"


def leer(path):
    out = []
    if path and os.path.exists(path):
        with open(path, encoding="utf-8") as fh:
            for ln in fh:
                if ln.strip():
                    try:
                        out.append(json.loads(ln))
                    except ValueError:
                        pass
    return out


def liquidadas(rows, favorecido=True):
    """Patas ganadas/perdidas; con `favorecido`, solo el lado que el modelo favorece (P ≥ 50 %) con cuota ≤ 2.10 (lo que el libro puede recomendar)."""
    out = [r for r in rows if r.get("p") is not None and r.get("cuota") and r.get("res") in (WIN, LOSE)]
    return [r for r in out if r["p"] >= 0.5 and r["cuota"] <= 2.10] if favorecido else out


def banda_cuota(c):
    for lo, hi in ((1.0, 1.25), (1.25, 1.4), (1.4, 1.6), (1.6, 1.8), (1.8, 2.11)):
        if lo <= c < hi:
            return f"{lo:g}–{hi:g}"
    return ">2.10"


def antiguedad(r):
    """Horas entre la captura de la cuota y el inicio del partido, en tramos; None si el registro no trae la hora."""
    o, h = r.get("observado_utc"), r.get("hora_utc")
    if not o or not h:
        return None
    def _utc(x):
        d_ = datetime.fromisoformat(x.replace("Z", "+00:00"))
        return d_ if d_.tzinfo else d_.replace(tzinfo=timezone.utc)
    dt = (_utc(h) - _utc(o)).total_seconds() / 3600
    return "≤ 6 h" if dt <= 6 else "6–24 h" if dt <= 24 else "> 24 h"


def fila(nombre, rs):
    if not rs:
        return None
    w = sum(1 for r in rs if r["res"] == WIN)
    n = len(rs)
    roi = sum(payoff(r["res"], r["cuota"]) for r in rs) / n * 100
    ci_a, ci_r = cluster_ci([(r["res"], r["cuota"], r["p"], (r["run"], r["partido_id"])) for r in rs])
    return [nombre, n, w, n - w, round(w / n * 100, 1), ci_a, round(roi, 1), ci_r, round(sum(r["p"] for r in rs) / n * 100, 1), round(sum(1 / r["cuota"] for r in rs) / n * 100, 1)]


ENCABEZADO = ["Grupo", "Patas", "Ganadas", "Perdidas", "% acierto", "IC 95 % acierto (por partido)", "ROI teórico %", "IC 95 % ROI % (por partido)", "P modelo media %", "1/cuota media %"]


def tabla(rows, clave, orden=None):
    g = defaultdict(list)
    for r in rows:
        k = clave(r)
        if k is not None:
            g[k].append(r)
    keys = orden or sorted(g, key=str)
    return [x for k in keys for x in [fila(str(k), g.get(k, []))] if x]


def curva_calibracion(rows, edges=(0, .1, .2, .3, .4, .5, .6, .7, .8, .9, 1.0001)):
    """Tramos de P (todas las patas, ambos lados): n, P media, frecuencia real, IC por partido y diferencia (real − P) en puntos."""
    out = []
    for lo, hi in zip(edges, edges[1:]):
        rs = [r for r in rows if lo <= r["p"] < hi]
        if not rs:
            continue
        w = sum(1 for r in rs if r["res"] == WIN)
        pm = sum(r["p"] for r in rs) / len(rs)
        ci = cluster_ci([(r["res"], r["cuota"], r["p"], (r["run"], r["partido_id"])) for r in rs])[0]
        out.append({"tramo": f"{lo * 100:.0f}–{min(hi, 1) * 100:.0f}", "n": len(rs), "p_media": round(pm * 100, 1), "frecuencia": round(w / len(rs) * 100, 1), "ic95": ci, "diferencia_pp": round((w / len(rs) - pm) * 100, 1)})
    return out


def metricas(rows):
    """Brier, log-loss y ECE de todas las patas liquidadas."""
    if not rows:
        return {"n": 0}
    eps = 1e-6
    y = [1 if r["res"] == WIN else 0 for r in rows]
    p = [min(1 - eps, max(eps, r["p"])) for r in rows]
    brier = sum((pi - yi) ** 2 for pi, yi in zip(p, y)) / len(y)
    ll = -sum(yi * math.log(pi) + (1 - yi) * math.log(1 - pi) for pi, yi in zip(p, y)) / len(y)
    ece = 0.0
    for lo in [i / 10 for i in range(10)]:
        b = [(pi, yi) for pi, yi in zip(p, y) if lo <= pi < lo + 0.1 or (lo == 0.9 and pi >= 0.9)]
        if b:
            ece += len(b) / len(y) * abs(sum(x for x, _ in b) / len(b) - sum(z for _, z in b) / len(b))
    return {"n": len(y), "brier": round(brier, 4), "logloss": round(ll, 4), "ece": round(ece, 4)}


def guardar_historial(path, rows, runs):
    """Una línea por ejecución con la métrica global y la curva: permite ver día a día si la calibración mejora. Idempotente por (fecha, runs)."""
    entrada = {"generado_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"), "runs": sorted(runs), "metricas": metricas(rows), "curva": curva_calibracion(rows)}
    previas = leer(path)
    previas = [x for x in previas if not (x["generado_utc"][:10] == entrada["generado_utc"][:10] and x["runs"] == entrada["runs"])]
    previas.append(entrada)
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        for x in previas:
            fh.write(json.dumps(x, ensure_ascii=False) + "\n")
    return entrada


CSV_COLUMNAS = ["dia_caracas", "run", "hora_utc", "liga", "partido_id", "partido", "grupo", "entry_id", "p_modelo", "cuota", "precio_tipo", "cuota_usuario", "p_mercado", "p_pinnacle", "n_casas",
                "agentes", "clase_agentes", "elegible", "resultado", "acierto", "goles_reales_partido", "observado_utc"]


def clase_agentes(s):
    for k in ("aprobada", "degradada", "rechazada", "objetada", "sin_revision", "precio_nuevo_sin_revisar"):
        if (s or "").startswith(k):
            return k
    return "otra"


def _dia_caracas(utc_iso):
    from datetime import timedelta
    return (datetime.fromisoformat(utc_iso.replace("Z", "+00:00")) - timedelta(hours=4)).strftime("%Y-%m-%d")


def exportar_csv(rows, out_path, goles=None):
    """Historial acumulativo: UNA FILA POR PATA Y DÍA (run + pata), con P del modelo, cuota y tipo de precio, P de mercado, estado de agentes, resultado y partido, para repetir las pruebas sin reconstruir nada.
    `goles` opcional: {(run, partido_id): goles a 90'}. Orden determinista; se reescribe completo desde el registro (que es la fuente)."""
    import csv
    goles = goles or {}
    filas = sorted(rows, key=lambda r: (r["run"], r["hora_utc"], r["partido_id"], r["leg_id"]))
    os.makedirs(os.path.dirname(out_path) or ".", exist_ok=True)
    tmp = out_path + ".tmp"
    with open(tmp, "w", encoding="utf-8", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(CSV_COLUMNAS)
        for r in filas:
            res = r["res"]
            w.writerow([r.get("dia_caracas") or _dia_caracas(r["hora_utc"]), r["run"], r["hora_utc"], r.get("liga") or "", r["partido_id"], r.get("partido") or "", r["grupo"], r.get("entry_id") or r["leg_id"].split("|", 1)[-1],
                        r["p"], r["cuota"], r.get("precio_tipo") or "", r.get("cuota_usuario") if r.get("cuota_usuario") is not None else "", r.get("p_mercado") if r.get("p_mercado") is not None else "",
                        r.get("p_pinnacle") if r.get("p_pinnacle") is not None else "", r.get("n_casas") if r.get("n_casas") is not None else "", r.get("agentes") or "", clase_agentes(r.get("agentes")),
                        int(bool(r.get("elegible"))), res, 1 if res.startswith(WIN) else (0 if res.startswith(LOSE) else ""), goles.get((r["run"], r["partido_id"]), ""), r.get("observado_utc") or ""])
    os.replace(tmp, out_path)
    return len(filas)
