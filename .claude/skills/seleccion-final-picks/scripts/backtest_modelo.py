#!/usr/bin/env python3
"""Backtest de los modelos propios (leg_model.py + count_model.py) — Fase 4.

A. WALK-FORWARD sobre las muestras de liga (`league_samples/*.json`, sin cuotas): cada partido se predice SOLO con partidos de su liga con fecha ESTRICTAMENTE anterior; se compara con la
   tasa base de la liga (misma información sin el modelo). Mide si el modelo APORTA información propia (skill = 1 − Brier_modelo / Brier_base) con IC por bootstrap de partidos.
B. VS MERCADO sobre partidos con cuotas previas al inicio: solo entran partidos cuya consulta de cuotas es ANTERIOR al inicio y filas de casa con `odd_date` anterior al inicio
   (se registran los excluidos). Compara Brier/log-loss del modelo contra el mercado sin margen, una rejilla de mezclas y el ROI a cuota de mercado.
C. DECISIÓN DE VALIDACIÓN (`decide_validation`): política DECLARADA (no un hecho estadístico) en POLICY; el resultado se guarda en data/model_validation.json y lo lee market_coverage.py.
   Una familia sin cuotas históricas (córners, tarjetas, goles por equipo) no puede probarse contra el mercado: su nivel máximo es «parcial».
Una muestra pequeña NO demuestra rentabilidad: los IC se informan siempre y «no_concluyente» es un resultado válido.

Uso: backtest_modelo.py --run runs/2026-10-14 [--odds-run runs/2026-10-13 --odds-days 2026-10-13] [--out-json ...] [--write-validation data/model_validation.json] [--doc docs/BACKTEST-modelo-v1.md]"""
import argparse
import datetime as dt
import json
import math
import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common  # noqa: E402
import count_model  # noqa: E402
import leg_model  # noqa: E402

POLICY = {"n_min_walk_forward": 300, "n_min_vs_mercado": 200, "ic": 0.95, "bootstrap": 1000, "semilla": 7, "min_partidos_previos_equipo": 5, "min_partidos_previos_liga": 30,
          "nota": "decisión de política (no un hecho estadístico): se puede endurecer; con menos partidos el resultado es «no_concluyente»"}
FAMILIES_WITH_ODDS = ("goals_total", "btts", "1x2", "dc")
LAST_N = 10


# ── métricas ──
def brier(p, y):
    return (p - y) ** 2


def logloss(p, y):
    p = min(max(p, 1e-6), 1 - 1e-6)
    return -math.log(p if y else 1 - p)


def _quantiles(xs, ic):
    xs = sorted(xs)
    lo, hi = (1 - ic) / 2, 1 - (1 - ic) / 2
    return xs[max(0, int(lo * len(xs)))], xs[min(len(xs) - 1, int(hi * len(xs)) - 1)]


def bootstrap_diff(clusters, reps, ic, seed):
    """clusters = [(suma_brier_A, suma_brier_B, n_pred)] por partido. Devuelve (diff_media, lo, hi) de (ΣA − ΣB)/Σn por remuestreo de PARTIDOS."""
    rnd = random.Random(seed)
    n = len(clusters)
    if n == 0:
        return None
    tot = lambda cs: sum(c[2] for c in cs) or 1
    point = (sum(c[0] for c in clusters) - sum(c[1] for c in clusters)) / tot(clusters)
    ds = []
    for _ in range(reps):
        cs = [clusters[rnd.randrange(n)] for _ in range(n)]
        ds.append((sum(c[0] for c in cs) - sum(c[1] for c in cs)) / tot(cs))
    lo, hi = _quantiles(ds, ic)
    return point, lo, hi


def skill_ci(clusters, reps, ic, seed):
    """skill = 1 − ΣBrier_modelo/ΣBrier_base con IC por bootstrap de partidos. clusters = [(brier_modelo, brier_base, n)]."""
    n = len(clusters)
    if n == 0:
        return None
    rnd = random.Random(seed)
    sk = lambda cs: 1 - sum(c[0] for c in cs) / max(sum(c[1] for c in cs), 1e-12)
    ds = [sk([clusters[rnd.randrange(n)] for _ in range(n)]) for _ in range(reps)]
    lo, hi = _quantiles(ds, ic)
    return sk(clusters), lo, hi


def calibration(preds, bins=10):
    out = []
    for b in range(bins):
        sel = [(p, y) for p, y in preds if b / bins <= p < (b + 1) / bins or (b == bins - 1 and p == 1.0)]
        if sel:
            out.append({"bin": f"{b / bins:.1f}-{(b + 1) / bins:.1f}", "n": len(sel), "p_media": round(sum(p for p, _ in sel) / len(sel), 3), "frecuencia": round(sum(y for _, y in sel) / len(sel), 3)})
    return out


# ── A. walk-forward ──
def _team_rows(prior, team):
    """Filas de un equipo orientadas a él: gf/ga/venue (+ own/opp de córners y tarjetas) a partir de partidos anteriores de la liga."""
    out = []
    for r in prior:
        if team not in (r["local"], r["visitante"]):
            continue
        home = r["local"] == team
        row = {"venue": "local" if home else "visitante", "gf": r["gl"] if home else r["gv"], "ga": r["gv"] if home else r["gl"]}
        for key, name in (("corners", "corners"), ("tarjetas", "cards")):
            t = r.get(key)
            row[name] = None if not t or None in t else {"own": t[0] if home else t[1], "opp": t[1] if home else t[0], "venue": row["venue"]}
        out.append(row)
    return out


def _freq(prior, test):
    v = [test(r) for r in prior]
    v = [x for x in v if x is not None]
    return (sum(v) + 1) / (len(v) + 2)


def predict_match(m, prior):
    """Predicciones del modelo y de la tasa base para UN partido, con `prior` = partidos anteriores de la liga. Devuelve lista de (familia, mercado, p_modelo, p_base, resultado)."""
    pol = POLICY
    rh, ra = _team_rows(prior, m["local"])[-LAST_N:], _team_rows(prior, m["visitante"])[-LAST_N:]
    if len(rh) < pol["min_partidos_previos_equipo"] or len(ra) < pol["min_partidos_previos_equipo"] or len(prior) < pol["min_partidos_previos_liga"]:
        return []
    mu, adv = leg_model.league_means([[{"gf": r["gl"], "ga": r["gv"], "venue": "local"} for r in prior] + [{"gf": r["gv"], "ga": r["gl"], "venue": "visitante"} for r in prior]])
    if not mu:
        return []
    pr = leg_model.model_probs(rh, ra, mu, adv)
    gl, gv = m["gl"], m["gv"]
    out = []
    tot = lambda r: r["gl"] + r["gv"]
    for L in (1.5, 2.5, 3.5):
        out.append(("goals_total", f"over_{L}", pr[f"over_{L}"], _freq(prior, lambda r, L=L: tot(r) > L), int(gl + gv > L)))
    out.append(("btts", "btts", pr["btts"], _freq(prior, lambda r: r["gl"] > 0 and r["gv"] > 0), int(gl > 0 and gv > 0)))
    for k, name, test in (("p1", "1", lambda r: r["gl"] > r["gv"]), ("px", "X", lambda r: r["gl"] == r["gv"]), ("p2", "2", lambda r: r["gl"] < r["gv"])):
        out.append(("1x2", name, pr[k], _freq(prior, test), int(test(m))))
    out.append(("dc", "1x", pr["1x"], _freq(prior, lambda r: r["gl"] >= r["gv"]), int(gl >= gv)))
    out.append(("dc", "x2", pr["x2"], _freq(prior, lambda r: r["gl"] <= r["gv"]), int(gl <= gv)))
    for L in (0.5, 1.5):
        out.append(("team_goals", f"home_over_{L}", pr[f"home_over_{L}"], _freq(prior, lambda r, L=L: r["gl"] > L), int(gl > L)))
        out.append(("team_goals", f"away_over_{L}", pr[f"away_over_{L}"], _freq(prior, lambda r, L=L: r["gv"] > L), int(gv > L)))
    for key, name, lines in (("corners", "corners", (8.5, 9.5, 10.5)), ("tarjetas", "cards", (3.5, 4.5, 5.5))):
        if not m.get(key) or None in m[key]:
            continue
        st = count_model.league_stats([tuple(r[key]) if r.get(key) and None not in r[key] else None for r in prior])
        ch = [r[name] for r in rh if r.get(name)]
        ca = [r[name] for r in ra if r.get(name)]
        if not st or len(ch) < pol["min_partidos_previos_equipo"] or len(ca) < pol["min_partidos_previos_equipo"]:
            continue
        rf = 1.0
        if name == "cards" and m.get("arbitro"):
            rt = [sum(r["tarjetas"]) for r in prior if r.get("arbitro") == m["arbitro"] and r.get("tarjetas") and None not in r["tarjetas"]]
            lt = [sum(r["tarjetas"]) for r in prior if r.get("tarjetas") and None not in r["tarjetas"]]
            if rt and lt:
                rf = count_model.referee_factor(sum(rt) / len(rt), len(rt), sum(lt) / len(lt))
        cp = count_model.model_probs(name, ch, ca, st, lines, (), rf)
        y = sum(m[key])
        for L in lines:
            out.append((f"{name}_total", f"over_{L}", cp[f"{name}_total_over_{L}"],
                        _freq(prior, lambda r, L=L, key=key: None if not r.get(key) or None in r[key] else int(sum(r[key]) > L)), int(y > L)))
    return out


def walk_forward(rows_by_league):
    """rows_by_league = {league_id: [filas compactas de league_sample.py]}. Predice cada partido con partidos de FECHA ESTRICTAMENTE anterior de su liga."""
    preds = []
    for lid, rows in rows_by_league.items():
        rows = sorted((r for r in rows if r.get("fecha")), key=lambda r: (r["fecha"], r.get("id") or ""))
        by_date = {}
        for r in rows:
            by_date.setdefault(r["fecha"], []).append(r)
        prior = []
        for d in sorted(by_date):
            for m in by_date[d]:
                for fam, mk, p, pb, y in predict_match(m, prior):
                    preds.append({"liga": lid, "fecha": d, "partido": m.get("id"), "familia": fam, "mercado": mk, "p": p, "p_base": pb, "y": y})
            prior += by_date[d]                                    # el partido del día d solo está disponible para los días posteriores
    return preds


def summarize_walk_forward(preds, pol=POLICY):
    fams = {}
    for fam in sorted({p["familia"] for p in preds}):
        ps = [p for p in preds if p["familia"] == fam]
        per = {}
        for p in ps:
            c = per.setdefault((p["liga"], p["partido"]), [0.0, 0.0, 0])
            c[0] += brier(p["p"], p["y"])
            c[1] += brier(p["p_base"], p["y"])
            c[2] += 1
        clusters = list(per.values())
        sk = skill_ci(clusters, pol["bootstrap"], pol["ic"], pol["semilla"])
        n_match = len(clusters)
        fams[fam] = {"partidos": n_match, "predicciones": len(ps), "brier_modelo": round(sum(brier(p["p"], p["y"]) for p in ps) / len(ps), 4),
                     "brier_base": round(sum(brier(p["p_base"], p["y"]) for p in ps) / len(ps), 4), "logloss_modelo": round(sum(logloss(p["p"], p["y"]) for p in ps) / len(ps), 4),
                     "logloss_base": round(sum(logloss(p["p_base"], p["y"]) for p in ps) / len(ps), 4), "skill": round(sk[0], 4), "skill_ic": [round(sk[1], 4), round(sk[2], 4)],
                     "calibracion": calibration([(p["p"], p["y"]) for p in ps])}
        fams[fam]["vs_tasa_base"] = ("supera" if n_match >= pol["n_min_walk_forward"] and sk[1] > 0 else "no_supera" if n_match >= pol["n_min_walk_forward"] and sk[2] < 0 else "no_concluyente")
    return fams


# ── B. vs mercado (cuotas previas al inicio) ──
def novig(odds):
    q = [1 / o for o in odds]
    s = sum(q)
    return [x / s for x in q]


def evaluate_vs_market(records, pol=POLICY):
    """records = [{partido, familia, mercado, p_modelo, p_mercado, cuota, y}] de partidos con cuotas PREVIAS al inicio. Devuelve métricas por familia + rejilla de mezclas + ROI."""
    out = {}
    for fam in sorted({r["familia"] for r in records}):
        rs = [r for r in records if r["familia"] == fam]
        per = {}
        for r in rs:
            c = per.setdefault(r["partido"], [0.0, 0.0, 0])
            c[0] += brier(r["p_modelo"], r["y"])
            c[1] += brier(r["p_mercado"], r["y"])
            c[2] += 1
        cl = list(per.values())
        d = bootstrap_diff(cl, pol["bootstrap"], pol["ic"], pol["semilla"])
        n = len(cl)
        grid = {f"w={w}": round(sum(brier(w * r["p_modelo"] + (1 - w) * r["p_mercado"], r["y"]) for r in rs) / len(rs), 4) for w in (0, 0.25, 0.5, 0.75, 1)}
        edge = [r for r in rs if r["p_modelo"] > r["p_mercado"]]
        roi = None if not edge else round(sum((r["cuota"] - 1) if r["y"] else -1 for r in edge) / len(edge), 4)
        out[fam] = {"partidos": n, "predicciones": len(rs), "brier_modelo": round(sum(brier(r["p_modelo"], r["y"]) for r in rs) / len(rs), 4),
                    "brier_mercado": round(sum(brier(r["p_mercado"], r["y"]) for r in rs) / len(rs), 4), "logloss_modelo": round(sum(logloss(r["p_modelo"], r["y"]) for r in rs) / len(rs), 4),
                    "logloss_mercado": round(sum(logloss(r["p_mercado"], r["y"]) for r in rs) / len(rs), 4), "diff_brier_modelo_menos_mercado": [round(x, 4) for x in d],
                    "mezclas_brier": grid, "roi_selecciones_con_ventaja_del_modelo": roi, "n_selecciones_con_ventaja": len(edge),
                    "vs_mercado": ("no_peor" if n >= pol["n_min_vs_mercado"] and d[2] <= 0 else "peor" if n >= pol["n_min_vs_mercado"] and d[1] > 0 else "no_concluyente")}
    return out


def decide_validation(wf, vs_market, pol=POLICY, generado_utc=None):
    """Nivel por familia y global. suficiente = supera la tasa base Y no es peor que el mercado; parcial = supera la tasa base (o no es evaluable contra el mercado); insuficiente = el resto."""
    fams = {}
    for fam, w in wf.items():
        vm = (vs_market or {}).get(fam)
        if fam in FAMILIES_WITH_ODDS:
            v = vm["vs_mercado"] if vm else "no_concluyente"
        else:
            v = "no_evaluable_sin_cuotas_historicas"
        if w["vs_tasa_base"] == "supera" and v == "no_peor":
            nivel = "suficiente"
        elif w["vs_tasa_base"] == "supera":
            nivel = "parcial"
        else:
            nivel = "insuficiente"
        fams[fam] = {"nivel": nivel, "vs_tasa_base": w["vs_tasa_base"], "vs_mercado": v, "partidos_walk_forward": w["partidos"], "partidos_vs_mercado": (vm or {}).get("partidos", 0)}
    levels = {f["nivel"] for f in fams.values()}
    nivel = "suficiente" if fams and levels == {"suficiente"} else "parcial" if levels & {"suficiente", "parcial"} else "insuficiente"
    motivo = ("; ".join(f"{k}: {v['nivel']} (base {v['vs_tasa_base']}, mercado {v['vs_mercado']})" for k, v in fams.items())) or "sin predicciones"
    return {"generado_utc": generado_utc or dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"), "nivel": nivel, "familias": fams, "reglas": pol, "motivo": motivo,
            "referencia": "docs/BACKTEST-modelo-v1.md"}


# ── registros vs mercado (cuotas previas al inicio) ──
def build_market_records(matches, mx, provider, results, pol=POLICY):
    """matches = inventario; mx = matrix.json['matches']; provider = ApifootballOddsProvider del run de cuotas; results = {apif_match_id: (goles_local, goles_visitante)} de partidos FINALIZADOS.
    Excluye (y cuenta) los partidos cuya consulta de cuotas no es anterior al inicio o sin filas de casa previas al inicio."""
    import adapters
    rows_by_comp = {}
    for m in matches:
        ev = mx.get(m["match_id"]) or {}
        for side in ("local", "visitante"):
            for r in (ev.get("form") or {}).get(side, []):
                if r.get("misma_competicion"):
                    rows_by_comp.setdefault(m["competition"], []).append(r)
    excl = {"sin_resultado_final": 0, "sin_historial": 0, "consulta_de_cuotas_posterior_al_inicio": 0, "sin_filas_de_casa_previas_al_inicio": 0, "sin_consulta_de_cuotas": 0}
    recs, used = [], 0
    for m in matches:
        apif = (m.get("source_match_ids") or {}).get("apifootball")
        ev = mx.get(m["match_id"]) or {}
        f = ev.get("form") or {}
        if not apif or apif not in results:
            excl["sin_resultado_final"] += 1
            continue
        if len(f.get("local", [])) < 6 or len(f.get("visitante", [])) < 6 or not rows_by_comp.get(m["competition"]):
            excl["sin_historial"] += 1
            continue
        q = provider._cover(m)
        if q is None:
            excl["sin_consulta_de_cuotas"] += 1
            continue
        kick = dt.datetime.fromisoformat(m["normalized_datetime_utc"].replace("Z", "+00:00"))
        if dt.datetime.fromisoformat(str(q["ts"]).replace("Z", "+00:00")) >= kick:
            excl["consulta_de_cuotas_posterior_al_inicio"] += 1
            continue
        kick_s = kick.strftime("%Y-%m-%d %H:%M:%S")
        prev = [r for (mid, _), r in provider.rows.items() if mid == str(apif) and str(r.get("odd_date", "")) < kick_s]
        if not prev:
            excl["sin_filas_de_casa_previas_al_inicio"] += 1
            continue
        avg = adapters.apif_odds_average(prev, min_books=3).get(str(apif), {})
        mu, adv = leg_model.league_means([rows_by_comp[m["competition"]]])
        if not mu:
            excl["sin_historial"] += 1
            continue
        pr = leg_model.model_probs(f["local"], f["visitante"], mu, adv)
        gl, gv = results[apif]
        used += 1

        def add(fam, mk, key, idx, pm, y, pairs=None):
            a = avg.get(key)
            if not a:
                return
            odds = a["cuotas_medias"]
            pmk = novig(odds)[idx] if pairs is None else pairs(odds)
            recs.append({"partido": m["match_id"], "familia": fam, "mercado": mk, "p_modelo": pm, "p_mercado": pmk, "cuota": odds[idx], "y": int(y)})
        for L in (1.5, 2.5, 3.5):
            k = "goles.over_" + str(L).replace(".", "_")
            add("goals_total", f"over_{L}", k, 0, pr[f"over_{L}"], gl + gv > L)
        add("btts", "btts", "goles.btts", 0, pr["btts"], gl > 0 and gv > 0)
        for i, (k, nm, y) in enumerate((("p1", "1", gl > gv), ("px", "X", gl == gv), ("p2", "2", gl < gv))):
            add("1x2", nm, "resultado.1x2", i, pr[k], y)
        p3 = lambda o: novig(o)
        x = avg.get("resultado.1x2")
        if x:
            q1, qx, q2 = novig(x["cuotas_medias"])
            for key, mk, pm, pmk, y in (("resultado.doble_oportunidad", "1x", pr["1x"], q1 + qx, gl >= gv), ("resultado.doble_oportunidad", "x2", pr["x2"], qx + q2, gl <= gv)):
                d = avg.get(key)
                if d:
                    recs.append({"partido": m["match_id"], "familia": "dc", "mercado": mk, "p_modelo": pm, "p_mercado": pmk, "cuota": d["cuotas_medias"][0 if mk == "1x" else 2], "y": int(y)})
    return recs, {"partidos_usados": used, "excluidos": excl}


# ── CLI ──
def load_league_rows(run):
    d = os.path.join(run, "league_samples")
    out = {}
    for f in sorted(os.listdir(d)) if os.path.isdir(d) else []:
        if f.endswith(".json"):
            out[f[:-5]] = common.read_json(os.path.join(d, f)).get("filas", [])
    return out


def render_md(wf, vs, val, excl):
    L = ["# Backtest de los modelos propios (v1)", "", f"Generado: {val['generado_utc']} · **Validación global: {val['nivel']}** · política: {json.dumps(POLICY['nota'], ensure_ascii=False)}", "",
         "## A. Walk-forward contra la tasa base de la liga (sin cuotas)", "", "| Familia | Partidos | Brier modelo | Brier base | Skill [IC 95 %] | Frente a la tasa base |", "|---|---|---|---|---|---|"]
    L += [f"| {k} | {v['partidos']} | {v['brier_modelo']} | {v['brier_base']} | {v['skill']} {v['skill_ic']} | {v['vs_tasa_base']} |" for k, v in wf.items()]
    L += ["", "## B. Frente al mercado (solo cuotas previas al inicio)", ""]
    if vs:
        L += ["| Familia | Partidos | Brier modelo | Brier mercado | Dif. [IC 95 %] | ROI selecciones con ventaja (n) | Frente al mercado |", "|---|---|---|---|---|---|---|"]
        L += [f"| {k} | {v['partidos']} | {v['brier_modelo']} | {v['brier_mercado']} | {v['diff_brier_modelo_menos_mercado']} | {v['roi_selecciones_con_ventaja_del_modelo']} ({v['n_selecciones_con_ventaja']}) | {v['vs_mercado']} |" for k, v in vs.items()]
        L += ["", f"Exclusiones: {json.dumps(excl, ensure_ascii=False)}"]
    else:
        L += ["Sin registros con cuotas previas al inicio."]
    L += ["", "## C. Decisión de validación", ""] + [f"- **{k}**: {v['nivel']} (base: {v['vs_tasa_base']}; mercado: {v['vs_mercado']})" for k, v in val["familias"].items()]
    L += ["", "Una muestra pequeña no demuestra rentabilidad; los intervalos se muestran siempre y «no_concluyente» es un resultado válido."]
    return "\n".join(L) + "\n"


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--run", required=True, help="run con league_samples/")
    ap.add_argument("--odds-run", help="run con cuotas previas y resultados (p. ej. runs/2026-10-13)")
    ap.add_argument("--odds-days", default="", help="fechas (YYYY-MM-DD) de ese run para pedir resultados a la API")
    ap.add_argument("--write-validation", help="escribe la decisión (p. ej. data/model_validation.json)")
    ap.add_argument("--doc", help="escribe el informe markdown (p. ej. docs/BACKTEST-modelo-v1.md)")
    ap.add_argument("--out-json", help="detalle completo en JSON")
    a = ap.parse_args(argv)
    wf_preds = walk_forward(load_league_rows(a.run))
    wf = summarize_walk_forward(wf_preds)
    vs, excl = {}, {}
    if a.odds_run:
        import adapters
        import price_sources as ps
        inv = common.read_json(os.path.join(a.odds_run, "inventory.json"))["matches"]
        mx = common.read_json(os.path.join(a.odds_run, "matrix.json"))["matches"]
        provider = ps.ApifootballOddsProvider(a.odds_run)
        key = adapters.apif_key()
        results = {}
        if key and a.odds_days:
            client = common.Client(os.path.join(a.odds_run, "cache"), os.path.join(a.odds_run, "sources", "consultas.jsonl"), policy=common.Policy(), min_interval=2.0, ttl=86400)
            for d0 in a.odds_days.split(","):
                for e in adapters.apif_call(client, key, action="get_events", **{"from": d0, "to": d0, "timezone": "UTC"}):
                    if e.get("match_status") == "Finished":
                        try:
                            results[str(e["match_id"])] = (int(e["match_hometeam_score"]), int(e["match_awayteam_score"]))
                        except (KeyError, ValueError, TypeError):
                            pass
        recs, excl = build_market_records(inv, mx, provider, results)
        vs = evaluate_vs_market(recs)
    val = decide_validation(wf, vs)
    if a.write_validation:
        common.write_json_atomic(a.write_validation, val)
    if a.out_json:
        common.write_json_atomic(a.out_json, {"walk_forward": wf, "vs_mercado": vs, "exclusiones_vs_mercado": excl, "validacion": val, "n_predicciones_walk_forward": len(wf_preds)})
    if a.doc:
        with open(a.doc, "w", encoding="utf-8") as f:
            f.write(render_md(wf, vs, val, excl))
    print(f"walk-forward: {len(wf_preds)} predicciones, {sum(v['partidos'] for v in wf.values())} partido-familia; validación global: {val['nivel']}")
    for k, v in val["familias"].items():
        print(f"  {k}: {v['nivel']} (tasa base: {v['vs_tasa_base']}; mercado: {v['vs_mercado']}; n={v['partidos_walk_forward']})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
