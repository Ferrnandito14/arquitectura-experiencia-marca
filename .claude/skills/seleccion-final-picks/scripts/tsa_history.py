#!/usr/bin/env python3
"""Cuotas de CIERRE históricas de TheStatsAPI para validar el modelo (backtest contra el mercado).

Uso:  tsa_history.py --runs runs/2026-10-14 runs/2026-10-15 … --from 2026-08-01 --to 2026-10-13 --max-odds 1800 --key-file RUTA [--out data/tsa_closing_odds.json]
1) Une las muestras de liga (`<run>/league_samples/*.json`: resultados + córners + tarjetas de apifootball) de los runs indicados.
2) Lista los partidos de TheStatsAPI del rango (página a página, ritmo y tope de la política) y empareja cada partido de la muestra por FECHA (±1 día) y los DOS equipos (nunca por uno solo ni por parecido de un equipo).
3) De los emparejados con `odds_available` toma una muestra estratificada por liga (semilla fija) y consulta sus cuotas.
4) Guarda SOLO lo derivado y necesario para el backtest (`--out`): por partido y mercado, la probabilidad sin margen mediana entre casas y la cuota mediana del ÚLTIMO precio visto (`last_seen`, cierre aproximado), con el nº de casas.
   Las respuestas crudas no se guardan (términos de uso: no almacenar más de lo necesario). Reanudable: los partidos ya guardados no se vuelven a pedir.
Nunca imprime ni guarda la clave. Un 401/403 detiene todo."""
import argparse
import json
import os
import random
import statistics
import sys
from datetime import datetime, timedelta, timezone

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common  # noqa: E402
import tsa_fetch  # noqa: E402

OVERROUND = (0.98, 1.25)


def load_rows(runs):
    """{league_id: {row_id: fila}} de las muestras de liga de varios runs (sin duplicados)."""
    out = {}
    for run in runs:
        d = os.path.join(run, "league_samples")
        for f in sorted(os.listdir(d)) if os.path.isdir(d) else []:
            if f.endswith(".json"):
                for r in common.read_json(os.path.join(d, f)).get("filas", []):
                    if r.get("id") and r.get("fecha"):
                        out.setdefault(f[:-5], {})[r["id"]] = r
    return out


def list_tsa(fetcher, d0, d1):
    rows, page = [], 1
    while True:
        code, body = fetcher.get(f"/football/matches?date_from={d0}&date_to={d1}&per_page=100&sort=utc_date&page={page}")
        if code in (401, 403):
            raise SystemExit(f"TheStatsAPI rechazó la clave ({code})")
        if code != 200:
            raise SystemExit(f"error {code} al listar partidos (página {page})")
        d = json.loads(body)
        rows += d["data"]
        if page >= (d.get("meta") or {}).get("total_pages", 1):
            return rows
        page += 1


def pair_rows(sample_rows, tsa_rows):
    """{apif_id: fila TSA}: misma fecha (±1 día), local con local y visitante con visitante (palabras compartidas en AMBOS) y candidato único."""
    by_date = {}
    for r in tsa_rows:
        if r.get("status") == "finished" and r.get("odds_available"):
            by_date.setdefault(r["utc_date"][:10], []).append(r)
    out, ambiguous = {}, 0
    for lid, rows in sample_rows.items():
        for rid, r in rows.items():
            d = datetime.fromisoformat(r["fecha"]).date()
            h, a = tsa_fetch._tokens(r["local"]), tsa_fetch._tokens(r["visitante"])
            cands = []
            for k in (-1, 0, 1):
                for t in by_date.get((d + timedelta(days=k)).isoformat(), []):
                    if tsa_fetch._share(h, tsa_fetch._tokens(t["home_team"]["name"])) and tsa_fetch._share(a, tsa_fetch._tokens(t["away_team"]["name"])):
                        # el resultado debe coincidir: evita emparejar la ida con la vuelta del mismo cruce
                        sc = (t.get("score") or {}).get("regulation") or {}
                        if sc.get("home") == r["gl"] and sc.get("away") == r["gv"]:
                            cands.append(t)
            if len(cands) == 1:
                out[rid] = (lid, cands[0])
            elif len(cands) > 1:
                ambiguous += 1
    return out, ambiguous


def _f(x):
    try:
        return float(x)
    except (TypeError, ValueError):
        return None


def _last(leaf):
    return _f((leaf or {}).get("last_seen"))


def _nv(odds):
    """Probabilidades sin margen de un conjunto de cuotas del mismo mercado (None si falta alguna o el margen es absurdo)."""
    if any(o is None or o <= 1.0 for o in odds):
        return None
    q = [1 / o for o in odds]
    s = sum(q)
    return [x / s for x in q] if OVERROUND[0] <= s <= OVERROUND[1] * (len(odds) / 2 if len(odds) > 2 else 1) else None


def _med(xs):
    xs = [x for x in xs if x is not None]
    return statistics.median(xs) if xs else None


def extract(resp):
    """Mercados mediana entre casas (cierre = último precio visto). Pares over/under → p_over y cuota over; 1X2 → [p1, pX, p2]."""
    books = resp["data"]["bookmakers"]
    out = {"n_casas": len(books)}
    acc = {"1x2": [], "btts": [], "goles": {}, "equipo": {}, "corners": {}, "corners_equipo": {}, "tarjetas": {}}
    for b in books:
        m = b["markets"]
        mo = m.get("match_odds")
        if mo:
            o = [_last(mo.get(k)) for k in ("home", "draw", "away")]
            p = _nv(o)
            if p:
                acc["1x2"].append((p, o))
        bt = m.get("btts")
        if bt:
            o = [_last(bt.get("yes")), _last(bt.get("no"))]
            p = _nv(o)
            if p:
                acc["btts"].append((p[0], o[0]))
        for mk, dest in (("total_goals", "goles"), ("match_corners", "corners"), ("total_cards", "tarjetas")):
            for line, v in (m.get(mk) or {}).items():
                if not isinstance(v, dict):
                    continue
                o = [_last(v.get("over")), _last(v.get("under"))]
                p = _nv(o)
                if p:
                    acc[dest].setdefault(line, []).append((p[0], o[0]))
        for side, v in (m.get("team_total_goals") or {}).items():
            for line, w in (v or {}).items():
                o = [_last((w or {}).get("over")), _last((w or {}).get("under"))]
                p = _nv(o)
                if p:
                    acc["equipo"].setdefault(f"{side}:{line}", []).append((p[0], o[0]))
        for side, v in (m.get("team_corners") or {}).items():
            for line, w in (v or {}).items():
                o = [_last((w or {}).get("over")), _last((w or {}).get("under"))]
                p = _nv(o)
                if p:
                    acc["corners_equipo"].setdefault(f"{side}:{line}", []).append((p[0], o[0]))
    if acc["1x2"]:
        ps = [_med([x[0][i] for x in acc["1x2"]]) for i in range(3)]
        s = sum(ps)
        out["1x2"] = {"p": [round(x / s, 4) for x in ps], "cuota": [round(_med([x[1][i] for x in acc["1x2"]]), 3) for i in range(3)], "n": len(acc["1x2"])}
    if acc["btts"]:
        out["btts"] = {"p": round(_med([x[0] for x in acc["btts"]]), 4), "cuota": round(_med([x[1] for x in acc["btts"]]), 3), "n": len(acc["btts"])}
    for dest in ("goles", "equipo", "corners", "corners_equipo", "tarjetas"):
        if acc[dest]:
            out[dest] = {k: {"p": round(_med([x[0] for x in v]), 4), "cuota": round(_med([x[1] for x in v]), 3), "n": len(v)} for k, v in acc[dest].items()}
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--runs", nargs="+", required=True)
    ap.add_argument("--from", dest="d0", required=True)
    ap.add_argument("--to", dest="d1", required=True)
    ap.add_argument("--max-odds", type=int, default=1800)
    ap.add_argument("--out", default="data/tsa_closing_odds.json")
    ap.add_argument("--cache-dir", default="data/tsa_history")
    ap.add_argument("--key-file")
    ap.add_argument("--seed", type=int, default=7)
    a = ap.parse_args(argv)
    key = tsa_fetch.api_key(a.key_file)
    if not key:
        print("error: sin clave (THESTATSAPI_KEY / THESTATSAPI_KEY_FILE / --key-file)", file=sys.stderr)
        return 2
    os.makedirs(a.cache_dir, exist_ok=True)
    f = tsa_fetch.Fetcher(key)
    f.log_path = os.path.join(a.cache_dir, "consultas.jsonl")
    sample = load_rows(a.runs)
    window = {lid: {rid: r for rid, r in rows.items() if a.d0 <= r["fecha"] <= a.d1} for lid, rows in sample.items()}
    n_win = sum(len(v) for v in window.values())
    lpath = os.path.join(a.cache_dir, f"listado_{a.d0}_{a.d1}.json")
    tsa_rows = common.read_json(lpath)
    if not tsa_rows:
        d0 = (datetime.fromisoformat(a.d0) - timedelta(days=1)).strftime("%Y-%m-%d")
        d1 = (datetime.fromisoformat(a.d1) + timedelta(days=1)).strftime("%Y-%m-%d")
        tsa_rows = list_tsa(f, d0, d1)
        common.write_json_atomic(lpath, [{k: r[k] for k in ("id", "status", "utc_date", "home_team", "away_team", "score", "odds_available")} for r in tsa_rows])
    paired, amb = pair_rows(window, tsa_rows)
    print(f"partidos de la muestra en la ventana: {n_win}; con listado TSA ({len(tsa_rows)} filas): emparejados {len(paired)}, ambiguos {amb}", flush=True)
    store = common.read_json(a.out, {"generado_utc": None, "nota": "", "partidos": {}})
    done = store["partidos"]
    todo = [(rid, lid, t) for rid, (lid, t) in paired.items() if rid not in done]
    random.Random(a.seed).shuffle(todo)
    by_league = {}
    for x in todo:
        by_league.setdefault(x[1], []).append(x)
    order = []
    while any(by_league.values()) and len(order) < a.max_odds - len(done):
        for lid in sorted(by_league):               # reparto por liga (ronda a ronda) para no sesgar hacia las ligas con más partidos
            if by_league[lid] and len(order) < a.max_odds - len(done):
                order.append(by_league[lid].pop())
    print(f"consultas de cuotas a hacer: {len(order)} (ya guardadas: {len(done)})", flush=True)
    for i, (rid, lid, t) in enumerate(order, 1):
        code, body = f.get(f"/football/matches/{t['id']}/odds")
        if code in (401, 403):
            raise SystemExit(f"TheStatsAPI rechazó la clave ({code})")
        if code == 200:
            try:
                ex = extract(json.loads(body))
            except (KeyError, ValueError, TypeError):
                ex = None
            if ex and len(ex) > 1:
                r = sample[lid][rid]
                done[rid] = {"tsa_id": t["id"], "liga": lid, "fecha": r["fecha"], "local": r["local"], "visitante": r["visitante"], **ex}
        elif code != 404:
            print(f"aviso: {code} en {t['id']}", flush=True)
        if i % 50 == 0 or i == len(order):
            store["generado_utc"] = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
            store["nota"] = "cierre aproximado = último precio visto; probabilidades sin margen, mediana entre casas; derivado de TheStatsAPI (sin respuestas crudas)"
            common.write_json_atomic(a.out, store)
            print(f"{i}/{len(order)} consultados; guardados {len(done)}", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
