#!/usr/bin/env python3
"""Análisis fuera de muestra sobre el registro acumulado de patas (data/ledger_patas.jsonl): recalibración, precio, agentes y régimen de goles del día.
Principios: (1) la P del modelo no usa precios de ninguna casa; el precio solo se usa para EVALUAR (nunca como entrada de un ajuste); (2) todo ajuste se entrena en unos días y se mide en el día
que no vio (rotación leave-one-day-out, incluida la partición pedida 14+15 → 16); (3) los IC remuestrean PARTIDOS completos (las patas de un partido no son independientes);
(4) un ajuste solo se publica si mejora fuera de muestra; si no, se informa y no se aplica. Es descriptivo con 3 días: no valida el modelo.
Uso:  analisis_tres_dias.py recalib|precio|agentes|regimen|todo [--ledger data/ledger_patas.jsonl] [--out-dir data/analisis]"""
import argparse
import json
import math
import os
import random
import sys
from collections import defaultdict

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import model_calibration as mc  # noqa: E402

ROOT = os.path.normpath(os.path.join(HERE, "..", "..", "..", ".."))
RUNS = ("runs/2026-10-14", "runs/2026-10-15", "runs/2026-10-16")
MAX_ODDS = 2.10
BOOT = 2000
MIN_FAMILY_TRAIN = 100


def cargar(path):
    rows = []
    with open(path, encoding="utf-8") as fh:
        for ln in fh:
            if ln.strip():
                r = json.loads(ln)
                if r["run"] in RUNS and r["res"] in ("GANADA", "PERDIDA"):
                    r["y"] = 1 if r["res"] == "GANADA" else 0
                    rows.append(r)
    return rows


def lado_favorecido(r):
    return r["p"] >= 0.5 and r["cuota"] <= MAX_ODDS


def metricas(p, y):
    p, y = np.asarray(p, float), np.asarray(y, float)
    return {"n": int(len(p)), "p_media": round(float(p.mean()), 4), "acierto": round(float(y.mean()), 4), "brier": round(float(mc.brier(p, y).mean()), 4),
            "logloss": round(float(mc.logloss(p, y).mean()), 4), "ece": round(mc.ece(p, y), 4)}


def ic_dif(grupos, difs, reps=BOOT, seed=11):
    """IC 95 % de la media de difs remuestreando partidos (grupos = id de partido por fila)."""
    cl = defaultdict(lambda: [0.0, 0])
    for g, d in zip(grupos, difs):
        cl[g][0] += float(d)
        cl[g][1] += 1
    c = list(cl.values())
    if len(c) < 2:
        return None
    rnd = random.Random(seed)
    out = []
    for _ in range(reps):
        s = n = 0.0
        for _i in range(len(c)):
            k = c[rnd.randrange(len(c))]
            s += k[0]
            n += k[1]
        out.append(s / n)
    out.sort()
    return [round(out[int(0.025 * reps)], 5), round(out[int(0.975 * reps)] if int(0.975 * reps) < reps else out[-1], 5)]


# ── isotónica (PAV) ──
def fit_iso(p, y):
    o = np.argsort(p, kind="stable")
    xs, ys = np.asarray(p, float)[o], np.asarray(y, float)[o]
    blocks = [[ys[i], 1, xs[i], xs[i]] for i in range(len(xs))]      # suma y, n, x_min, x_max
    out = []
    for b in blocks:
        out.append(b)
        while len(out) > 1 and out[-2][0] / out[-2][1] >= out[-1][0] / out[-1][1]:
            b2 = out.pop()
            b1 = out.pop()
            out.append([b1[0] + b2[0], b1[1] + b2[1], b1[2], b2[3]])
    cx = np.array([(b[2] + b[3]) / 2 for b in out])
    cy = np.array([b[0] / b[1] for b in out])
    return cx, cy


def pred_iso(m, p):
    cx, cy = m
    return np.clip(np.interp(np.asarray(p, float), cx, cy), 0.01, 0.99)


def metodos(train, test_p, test_fam):
    """Devuelve {método: P ajustada del conjunto de prueba}. train = filas. Los ajustes por familia caen al global si hay < MIN_FAMILY_TRAIN filas."""
    tp, ty = np.array([r["p"] for r in train]), np.array([r["y"] for r in train])
    tpa = np.asarray(test_p, float)
    out = {"sin_ajuste": tpa}
    a, b = mc.fit_platt(tp, ty)
    out["platt_global"] = mc.calibrate(tpa, a, b)
    iso_g = fit_iso(tp, ty)
    out["isotonica_global"] = pred_iso(iso_g, tpa)
    pf, isof = np.array(tpa), np.array(tpa)
    for fam in sorted(set(test_fam)):
        tr = [r for r in train if r["grupo"] == fam]
        m = np.array([f == fam for f in test_fam])
        if len(tr) >= MIN_FAMILY_TRAIN:
            fp, fy = np.array([r["p"] for r in tr]), np.array([r["y"] for r in tr])
            af, bf = mc.fit_platt(fp, fy)
            pf[m] = mc.calibrate(tpa[m], af, bf)
            isof[m] = pred_iso(fit_iso(fp, fy), tpa[m])
        else:
            pf[m] = out["platt_global"][m]
            isof[m] = out["isotonica_global"][m]
    out["platt_por_familia"] = pf
    out["isotonica_por_familia"] = isof
    return out


BANDAS = [(0.5, 0.6), (0.6, 0.7), (0.7, 0.8), (0.8, 0.9), (0.9, 1.01)]


def tabla_bandas(p, y):
    p, y = np.asarray(p), np.asarray(y)
    t = []
    for lo, hi in BANDAS:
        m = (p >= lo) & (p < hi)
        if m.sum():
            t.append({"banda": f"{lo * 100:.0f}-{min(hi, 1) * 100:.0f}", "n": int(m.sum()), "p_media": round(float(p[m].mean()), 3), "acierto": round(float(y[m].mean()), 3)})
    return t


def recalib(rows):
    """Lado con P≥0.5 de cada línea (la otra cara es su complemento y duplicaría la muestra). Rotación leave-one-day-out; pedido: entrenar 14+15 y probar 16."""
    base = [r for r in rows if r["p"] >= 0.5]
    folds = [("14+15 → 16", RUNS[2]), ("15+16 → 14", RUNS[0]), ("14+16 → 15", RUNS[1])]
    res = {"filas_lado_p50": len(base), "partidos": len({r["partido_id"] for r in base}), "folds": {}, "nota": "p del registro = ya pasada por model_calibration donde 'aplicar'"}
    pooled = defaultdict(lambda: {"p": [], "y": [], "g": [], "fav": []})
    for nombre, test_run in folds:
        tr = [r for r in base if r["run"] != test_run]
        te = [r for r in base if r["run"] == test_run]
        tp = [r["p"] for r in te]
        ty = np.array([r["y"] for r in te])
        mets = metodos(tr, tp, [r["grupo"] for r in te])
        f = {"n_train": len(tr), "n_test": len(te), "metodos": {}}
        for k, pa in mets.items():
            f["metodos"][k] = metricas(pa, ty)
            P = pooled[k]
            P["p"] += list(pa)
            P["y"] += list(ty)
            P["g"] += [r["partido_id"] for r in te]
            P["fav"] += [lado_favorecido(r) for r in te]
        res["folds"][nombre] = f
    res["agregado_fuera_de_muestra"] = {}
    y0 = np.array(pooled["sin_ajuste"]["y"])
    p0 = np.array(pooled["sin_ajuste"]["p"])
    for k, P in pooled.items():
        pa, y = np.array(P["p"]), np.array(P["y"])
        e = metricas(pa, y)
        if k != "sin_ajuste":
            dif = mc.brier(pa, y) - mc.brier(p0, y0)
            dll = mc.logloss(pa, y) - mc.logloss(p0, y0)
            e["dif_brier_vs_sin_ajuste"] = round(float(dif.mean()), 5)
            e["dif_brier_ic95"] = ic_dif(P["g"], dif)
            e["dif_logloss_vs_sin_ajuste"] = round(float(dll.mean()), 5)
            e["dif_logloss_ic95"] = ic_dif(P["g"], dll)
            e["folds_que_mejoran_brier"] = sum(1 for f in res["folds"].values() if f["metodos"][k]["brier"] < f["metodos"]["sin_ajuste"]["brier"])
            e["mejora_en_14+15→16"] = bool(res["folds"]["14+15 → 16"]["metodos"][k]["brier"] < res["folds"]["14+15 → 16"]["metodos"]["sin_ajuste"]["brier"]
                                          and res["folds"]["14+15 → 16"]["metodos"][k]["logloss"] < res["folds"]["14+15 → 16"]["metodos"]["sin_ajuste"]["logloss"])
        fav = np.array(P["fav"])
        e["lado_favorecido_cuota<=2.10"] = metricas(pa[fav], y[fav]) if fav.any() else None
        e["bandas"] = tabla_bandas(pa, y)
        res["agregado_fuera_de_muestra"][k] = e
    # criterio de publicación (declarado antes de mirar): IC95 del Δ Brier < 0, Δ log-loss ≤ 0, mejora en ≥ 2 de 3 folds y en el fold 14+15→16
    res["criterio"] = "Δ Brier con IC95 < 0 sobre todas las predicciones fuera de muestra, Δ log-loss ≤ 0, mejora en ≥ 2 de 3 folds y en 14+15→16"
    veredictos = {}
    for k, e in res["agregado_fuera_de_muestra"].items():
        if k == "sin_ajuste":
            continue
        ok = bool(e["dif_brier_ic95"] and e["dif_brier_ic95"][1] < 0 and e["dif_logloss_vs_sin_ajuste"] <= 0 and e["folds_que_mejoran_brier"] >= 2 and e["mejora_en_14+15→16"])
        veredictos[k] = ok
    res["publicar"] = {k: v for k, v in veredictos.items()}
    res["publicar_alguno"] = any(veredictos.values())
    # ajuste final (solo informativo; se guarda como candidato aunque no se publique)
    bp, by = np.array([r["p"] for r in base]), np.array([r["y"] for r in base])
    a, b = mc.fit_platt(bp, by)
    res["candidato_platt_global_3_dias"] = {"a": round(a, 4), "b": round(b, 4), "publicado": veredictos.get("platt_global", False)}
    return res


def md_recalib(res):
    L = ["# Recalibración con 3 días (14–16 oct 2026): validación fuera de muestra", "",
         f"Filas: {res['filas_lado_p50']} patas (lado con P≥50 % de cada línea) de {res['partidos']} partidos. Entrenar en dos días y probar en el tercero (rotación); la partición pedida es **14+15 → 16**.",
         "No se usa ningún precio como entrada del ajuste (solo P del modelo, familia de mercado y resultado). " + res["nota"] + ".", "",
         f"Criterio de publicación (fijado antes de mirar): {res['criterio']}.", "", "## Agregado fuera de muestra (3 folds)", "",
         "| Método | n | P media | Acierto | Brier | Log-loss | ECE | Δ Brier (IC95) | Δ log-loss (IC95) | Folds que mejoran | ¿Publicar? |", "|---|---|---|---|---|---|---|---|---|---|---|"]
    for k, e in res["agregado_fuera_de_muestra"].items():
        if k == "sin_ajuste":
            L.append(f"| {k} | {e['n']} | {e['p_media']} | {e['acierto']} | {e['brier']} | {e['logloss']} | {e['ece']} | — | — | — | — |")
        else:
            L.append(f"| {k} | {e['n']} | {e['p_media']} | {e['acierto']} | {e['brier']} | {e['logloss']} | {e['ece']} | {e['dif_brier_vs_sin_ajuste']} {e['dif_brier_ic95']} | {e['dif_logloss_vs_sin_ajuste']} {e['dif_logloss_ic95']} | {e['folds_que_mejoran_brier']}/3 | {'**sí**' if res['publicar'][k] else 'no'} |")
    L += ["", "## Fold pedido: entrenar 14+15, probar 16", "", "| Método | n prueba | Brier | Log-loss | ECE |", "|---|---|---|---|---|"]
    for k, m in res["folds"]["14+15 → 16"]["metodos"].items():
        L.append(f"| {k} | {m['n']} | {m['brier']} | {m['logloss']} | {m['ece']} |")
    L += ["", "## Otros folds (Brier)", "", "| Fold | " + " | ".join(res["folds"]["14+15 → 16"]["metodos"]) + " |", "|---|" + "---|" * len(res["folds"]["14+15 → 16"]["metodos"])]
    for nom, f in res["folds"].items():
        L.append(f"| {nom} (n={f['n_test']}) | " + " | ".join(str(m["brier"]) for m in f["metodos"].values()) + " |")
    L += ["", "## Bandas de P (agregado fuera de muestra): sin ajuste vs isotónica por familia", "", "| Banda | n | P media (sin ajuste) | Acierto | P media (isot. fam.) | Acierto |", "|---|---|---|---|---|---|"]
    b0 = {b["banda"]: b for b in res["agregado_fuera_de_muestra"]["sin_ajuste"]["bandas"]}
    b1 = {b["banda"]: b for b in res["agregado_fuera_de_muestra"]["isotonica_por_familia"]["bandas"]}
    for k, b in b0.items():
        c = b1.get(k)
        L.append(f"| {k} % | {b['n']} | {b['p_media']} | {b['acierto']} | {c['p_media'] if c else '—'} | {c['acierto'] if c else '—'} |")
    L += ["", "**Decisión:** " + ("se publica al menos un ajuste (ver tabla)." if res["publicar_alguno"] else "NINGÚN ajuste cumple el criterio fuera de muestra: la probabilidad del modelo queda sin cambios (no se publica la recalibración)."),
          "", "Limitaciones: 3 días, un solo régimen de goles por día, familias con pocas filas caen al ajuste global; el registro ya contiene la calibración por grupo vigente (`data/model_calibration.json`)."]
    return "\n".join(L) + "\n"


# ── precio ──
def precio(rows):
    out = {"definiciones": {
        "referencia": "mediana entre casas del agregador (apifootball/TheStatsAPI): precio de la pata (cuota) y P de mercado sin margen cuando existe el par over/under (normalización proporcional por casa, mediana)",
        "pinnacle_sin_margen": "P sin margen de Pinnacle (TheStatsAPI) cuando cotiza el par",
        "captura_usuario": "precio que la persona usuaria capturó de su casa; capa opcional de validación"},
        "p_final": "la P del modelo no usa ningún precio; la P de mercado es una comparación (mediana entre casas) y nunca entra en la P final"}
    lado = [r for r in rows if r["p"] >= 0.5]

    def bloque(sel, campo):
        s = [r for r in sel if r.get(campo) is not None]
        if len(s) < 30:
            return {"n": len(s)}
        y = np.array([r["y"] for r in s])
        pm = np.array([r[campo] for r in s])
        pp = np.array([r["p"] for r in s])
        g = [r["partido_id"] for r in s]
        d = mc.brier(pp, y) - mc.brier(pm, y)
        dll = mc.logloss(pp, y) - mc.logloss(pm, y)
        return {"n": len(s), "partidos": len(set(g)), "modelo": metricas(pp, y), "mercado": metricas(pm, y), "dif_brier_modelo_menos_mercado": round(float(d.mean()), 5),
                "ic95": ic_dif(g, d), "dif_logloss_modelo_menos_mercado": round(float(dll.mean()), 5), "ic95_logloss": ic_dif(g, dll)}
    out["P_mercado_agregador"] = bloque(lado, "p_mercado")
    out["P_pinnacle"] = bloque(lado, "p_pinnacle")
    # patas con |modelo − mercado| > 10 pp
    dis = [r for r in lado if r.get("p_mercado") is not None and abs(r["p"] - r["p_mercado"]) > 0.10]
    out["discrepancia_mayor_10pp"] = {"n": len(dis), "de": sum(1 for r in lado if r.get("p_mercado") is not None)}
    for nombre, f in (("modelo_mayor_que_mercado", lambda r: r["p"] > r["p_mercado"]), ("modelo_menor_que_mercado", lambda r: r["p"] < r["p_mercado"])):
        s = [r for r in dis if f(r)]
        if s:
            y = np.array([r["y"] for r in s])
            out["discrepancia_mayor_10pp"][nombre] = {"n": len(s), "partidos": len({r["partido_id"] for r in s}), "p_modelo": round(float(np.mean([r["p"] for r in s])), 3), "p_mercado": round(float(np.mean([r["p_mercado"] for r in s])), 3), "acierto": round(float(y.mean()), 3)}
    # por tipo de precio y captura del usuario
    out["por_tipo_de_precio"] = {}
    for nombre, sel in (("referencia_agregador (todas las patas)", lado), ("con_captura_usuario", [r for r in lado if r.get("cuota_usuario")]), ("con_P_pinnacle", [r for r in lado if r.get("p_pinnacle") is not None])):
        if sel:
            y = np.array([r["y"] for r in sel])
            c = np.array([r["cuota"] for r in sel])
            roi = float(np.where(y == 1, c - 1, -1.0).mean())
            out["por_tipo_de_precio"][nombre] = {"n": len(sel), "partidos": len({r["partido_id"] for r in sel}), "p_modelo": round(float(np.mean([r["p"] for r in sel])), 3), "acierto": round(float(y.mean()), 3), "roi_a_cuota_referencia": round(roi * 100, 1)}
    cu = [r for r in lado if r.get("cuota_usuario")]
    if cu:
        dif = np.array([r["cuota_usuario"] - r["cuota"] for r in cu])
        out["captura_vs_referencia"] = {"n": len(cu), "cuota_usuario_menos_referencia_media": round(float(dif.mean()), 3), "mediana": round(float(np.median(dif)), 3)}
    # lado favorecido por tramo de cuota (referencia)
    fav = [r for r in rows if lado_favorecido(r)]
    out["lado_favorecido"] = {"n": len(fav), **metricas([r["p"] for r in fav], [r["y"] for r in fav])}
    out["lado_favorecido"]["por_cuota"] = {}
    for lo, hi in ((1.0, 1.4), (1.4, 1.8), (1.8, 2.11)):
        s = [r for r in fav if lo <= r["cuota"] < hi]
        if s:
            out["lado_favorecido"]["por_cuota"][f"{lo}-{min(hi, 2.1)}"] = {"n": len(s), "p_modelo": round(float(np.mean([r["p"] for r in s])), 3), "acierto": round(float(np.mean([r["y"] for r in s])), 3),
                                                                           "p_implicita": round(float(np.mean([1 / r["cuota"] for r in s])), 3)}
    return out


# ── agentes ──
def clase_agentes(s):
    for k in ("aprobada", "degradada", "rechazada", "objetada", "sin_revision", "precio_nuevo_sin_revisar"):
        if s.startswith(k):
            return k
    return "otra"


def agentes(rows):
    out = {"nota": "Se compara el acierto REAL y el residuo (acierto − P del modelo) por etiqueta; si el IC95 de la diferencia incluye 0 no hay evidencia de que la etiqueta discrimine. No se usa como filtro duro."}
    for nombre, sel in (("lado_favorecido (P≥50 %, cuota≤2.10)", [r for r in rows if lado_favorecido(r)]), ("todas las patas con P≥50 %", [r for r in rows if r["p"] >= 0.5])):
        t = {}
        for k in sorted({clase_agentes(r["agentes"]) for r in sel}):
            s = [r for r in sel if clase_agentes(r["agentes"]) == k]
            y = np.array([r["y"] for r in s])
            p = np.array([r["p"] for r in s])
            ci_a, ci_roi = _ci_acc(s)
            t[k] = {"n": len(s), "partidos": len({r["partido_id"] for r in s}), "p_modelo": round(float(p.mean()), 3), "acierto": round(float(y.mean()), 3), "residuo": round(float((y - p).mean()), 3), "ic95_acierto": ci_a}
        difs = {}
        ap = [r for r in sel if clase_agentes(r["agentes"]) == "aprobada"]
        for k in ("degradada", "rechazada", "objetada", "sin_revision"):
            s = [r for r in sel if clase_agentes(r["agentes"]) == k]
            if len(ap) >= 20 and len(s) >= 20:
                difs[f"aprobada − {k}"] = _dif_grupos(ap, s)
        out[nombre] = {"por_etiqueta": t, "diferencias": difs}
    # por día: ¿cambia de signo?
    out["por_dia_lado_favorecido"] = {}
    fav = [r for r in rows if lado_favorecido(r)]
    for run in RUNS:
        ap = [r for r in fav if r["run"] == run and clase_agentes(r["agentes"]) == "aprobada"]
        dg = [r for r in fav if r["run"] == run and clase_agentes(r["agentes"]) == "degradada"]
        if ap and dg:
            out["por_dia_lado_favorecido"][run[-5:]] = {"aprobada": {"n": len(ap), "acierto": round(float(np.mean([r["y"] for r in ap])), 3)}, "degradada": {"n": len(dg), "acierto": round(float(np.mean([r["y"] for r in dg])), 3)}}
    return out


def _ci_acc(s, reps=BOOT, seed=5):
    cl = defaultdict(lambda: [0, 0])
    for r in s:
        cl[r["partido_id"]][0] += r["y"]
        cl[r["partido_id"]][1] += 1
    c = list(cl.values())
    if len(c) < 2:
        return None, None
    rnd = random.Random(seed)
    v = []
    for _ in range(reps):
        w = n = 0
        for _i in range(len(c)):
            k = c[rnd.randrange(len(c))]
            w += k[0]
            n += k[1]
        v.append(w / n)
    v.sort()
    return [round(v[int(0.025 * reps)], 3), round(v[int(0.975 * reps)], 3)], None


def _dif_grupos(a, b, reps=BOOT, seed=9):
    """Diferencia de acierto (a − b) y de residuo, remuestreando partidos en cada grupo por separado."""
    def cl(s):
        d = defaultdict(lambda: [0, 0, 0.0])
        for r in s:
            d[r["partido_id"]][0] += r["y"]
            d[r["partido_id"]][1] += 1
            d[r["partido_id"]][2] += r["y"] - r["p"]
        return list(d.values())
    ca, cb = cl(a), cl(b)
    rnd = random.Random(seed)

    def stat(c):
        n = sum(k[1] for k in c)
        return sum(k[0] for k in c) / n, sum(k[2] for k in c) / n
    acc, res = [], []
    for _ in range(reps):
        sa = stat([ca[rnd.randrange(len(ca))] for _ in ca])
        sb = stat([cb[rnd.randrange(len(cb))] for _ in cb])
        acc.append(sa[0] - sb[0])
        res.append(sa[1] - sb[1])
    acc.sort()
    res.sort()
    lo, hi = int(0.025 * reps), int(0.975 * reps) - 1
    pa, pb = stat(ca), stat(cb)
    return {"n_a": len(a), "n_b": len(b), "dif_acierto_pp": round((pa[0] - pb[0]) * 100, 1), "ic95_pp": [round(acc[lo] * 100, 1), round(acc[hi] * 100, 1)],
            "dif_residuo_pp": round((pa[1] - pb[1]) * 100, 1), "ic95_residuo_pp": [round(res[lo] * 100, 1), round(res[hi] * 100, 1)],
            "distinguible_de_cero": bool(acc[lo] > 0 or acc[hi] < 0)}


# ── régimen del día ──
def regimen(rows, root=ROOT):
    import api_detalle
    import leg_model
    por_dia = {}
    partidos = {}
    for run in RUNS:
        res = json.load(open(os.path.join(root, run, "resultados", "resultados.json")))
        lst = []
        for mid, r in res.items():
            if r.get("estado") != "Finished" or r.get("h") is None or r.get("a") is None:
                continue
            if r.get("marcador_90_directo") is False:
                continue
            mp = api_detalle.model_params(os.path.join(root, run), mid)
            if not mp:
                continue
            lst.append({"mid": mid, "lh": mp[0], "la": mp[1], "real": r["h"] + r["a"]})
        por_dia[run] = lst
        for x in lst:
            partidos[x["mid"]] = (run, x)
    resumen = {}
    for run, lst in por_dia.items():
        if lst:
            e = float(np.mean([x["lh"] + x["la"] for x in lst]))
            r = float(np.mean([x["real"] for x in lst]))
            resumen[run[-5:]] = {"partidos": len(lst), "goles_esperados_modelo": round(e, 3), "goles_reales": round(r, 3), "razon_real_esperado": round(r / e, 3), "sesgo": round(e - r, 3)}
    todos = [x for lst in por_dia.values() for x in lst]
    resumen["total"] = {"partidos": len(todos), "goles_esperados_modelo": round(float(np.mean([x["lh"] + x["la"] for x in todos])), 3), "goles_reales": round(float(np.mean([x["real"] for x in todos])), 3)}
    # factor de corrección k = Σ reales / Σ esperados entrenado en los OTROS días; se evalúa en las patas de goles totales del día no visto
    prueba = {}
    for test in RUNS:
        tr = [x for r, l in por_dia.items() if r != test for x in l]
        te = por_dia[test]
        if not tr or not te:
            continue
        k = sum(x["real"] for x in tr) / sum(x["lh"] + x["la"] for x in tr)
        legs = [r for r in rows if r["run"] == test and r["entry_id"].startswith("goles.total.") and r["partido_id"] in {x["mid"] for x in te}]
        lam = {x["mid"]: x for x in te}
        pb, pk, ys, gs = [], [], [], []
        for r in legs:
            _, _, lado, linea = r["entry_id"].split(".", 3)
            x = lam[r["partido_id"]]
            base = leg_model.p_over(leg_model.grid(x["lh"], x["la"]), float(linea))
            corr = leg_model.p_over(leg_model.grid(x["lh"] * k, x["la"] * k), float(linea))
            if lado == "under":
                base, corr = 1 - base, 1 - corr
            pb.append(base)
            pk.append(corr)
            ys.append(r["y"])
            gs.append(r["partido_id"])
        if not ys:
            continue
        y = np.array(ys)
        pb, pk = np.array(pb), np.array(pk)
        d = mc.brier(pk, y) - mc.brier(pb, y)
        dl = mc.logloss(pk, y) - mc.logloss(pb, y)
        prueba[test[-5:]] = {"k_entrenado_en_otros_dias": round(k, 3), "n_patas_goles": len(ys), "partidos": len(set(gs)), "sin_correccion": metricas(pb, y), "con_correccion": metricas(pk, y),
                             "dif_brier": round(float(d.mean()), 5), "ic95": ic_dif(gs, d), "dif_logloss": round(float(dl.mean()), 5)}
    ks = [v["k_entrenado_en_otros_dias"] for v in prueba.values()]
    mejoras = sum(1 for v in prueba.values() if v["dif_brier"] < 0)
    res_out = {"resumen_por_dia": resumen, "correccion_fuera_de_muestra": prueba,
               "criterio": "publicar el factor solo si baja el Brier en ≥ 2 de 3 días no vistos y el IC95 del Δ Brier agregado excluye 0",
               "dias_que_mejoran": mejoras}
    # IC agregado
    agg_d, agg_g = [], []
    for test in RUNS:
        v = prueba.get(test[-5:])
        if not v:
            continue
        k = v["k_entrenado_en_otros_dias"]
        te = {x["mid"]: x for x in por_dia[test]}
        for r in rows:
            if r["run"] == test and r["entry_id"].startswith("goles.total.") and r["partido_id"] in te:
                _, _, lado, linea = r["entry_id"].split(".", 3)
                x = te[r["partido_id"]]
                b = leg_model.p_over(leg_model.grid(x["lh"], x["la"]), float(linea))
                c = leg_model.p_over(leg_model.grid(x["lh"] * k, x["la"] * k), float(linea))
                if lado == "under":
                    b, c = 1 - b, 1 - c
                agg_d.append(float(mc.brier(c, r["y"]) - mc.brier(b, r["y"])))
                agg_g.append(r["partido_id"])
    res_out["dif_brier_agregado"] = round(float(np.mean(agg_d)), 5) if agg_d else None
    res_out["ic95_agregado"] = ic_dif(agg_g, agg_d) if agg_d else None
    res_out["publicar_factor"] = bool(mejoras >= 2 and res_out["ic95_agregado"] and res_out["ic95_agregado"][1] < 0)
    res_out["factores_por_dia_entrenados"] = ks
    return res_out


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("cmd", choices=["recalib", "precio", "agentes", "regimen", "todo"])
    ap.add_argument("--ledger", default=os.path.join(ROOT, "data", "ledger_patas.jsonl"))
    ap.add_argument("--out-dir", default=os.path.join(ROOT, "data", "analisis"))
    a = ap.parse_args(argv)
    rows = cargar(a.ledger)
    os.makedirs(a.out_dir, exist_ok=True)
    cmds = ["recalib", "precio", "agentes", "regimen"] if a.cmd == "todo" else [a.cmd]
    for c in cmds:
        r = {"recalib": recalib, "precio": precio, "agentes": agentes, "regimen": regimen}[c](rows)
        with open(os.path.join(a.out_dir, f"{c}.json"), "w", encoding="utf-8") as fh:
            json.dump(r, fh, ensure_ascii=False, indent=1)
        if c == "recalib":
            with open(os.path.join(ROOT, "docs", "RECALIBRACION-modelo-3-dias.md"), "w", encoding="utf-8") as fh:
                fh.write(md_recalib(r))
        print(f"== {c}: {os.path.join(a.out_dir, c + '.json')}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
