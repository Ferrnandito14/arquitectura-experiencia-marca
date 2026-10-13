#!/usr/bin/env python3
"""Lotes de revisión por agentes e integridad de la conciliación.

  batches.py make  --run runs/<fecha> [--max-chars 50000]      -> batches.json
  batches.py check --run runs/<fecha> --results resultados.json -> reviews.json (exit 0 sólo si TODO está conciliado)

El tamaño de lote se calcula del volumen real (caracteres por fila), agrupando por competición; una competición
grande se parte. Un resumen por competición NO es evidencia: cada match_id debe aparecer revisado por cada agente
asignado. Una fila no revisada queda PENDIENTE. Formato de resultados:
  {"agent": "analista-deportivo", "batch_id": "b01", "rows": [{"match_id": "...", "review_status": "REVISADO|PENDIENTE",
   "corrections": ["..."], "note": "..."}]}   (puede ser una lista de estos objetos)
"""
import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common  # noqa: E402

AGENTS_PER_BATCH = ["analista-deportivo", "analista-cuantitativo"]


def row_size(m, ev):
    return len(json.dumps({"m": {k: m[k] for k in ("match_id", "home_team", "away_team", "competition", "normalized_datetime_utc")},
                           "ev": ev}, ensure_ascii=False))


def make_batches(inv, matrix, max_chars=50000):
    rows = [m for m in inv["matches"] if m["analysis_required"]]
    rows.sort(key=lambda m: (m["competition"], m["normalized_datetime_utc"] or "", m["match_id"]))
    batches, cur, size = [], [], 0
    for m in rows:
        s = row_size(m, matrix["matches"].get(m["match_id"], {}))
        new_comp = bool(cur) and m["competition"] != cur[-1]["competition"]
        if cur and (size + s > max_chars):
            batches.append(cur)
            cur, size = [], 0
        elif cur and new_comp and size > max_chars * 0.6:
            batches.append(cur)
            cur, size = [], 0
        cur.append(m)
        size += s
    if cur:
        batches.append(cur)
    disc = [m["match_id"] for m in inv["matches"] if m["discrepancies"] or m["calendar_verification_status"] in ("FECHA_DISCREPANTE", "NO_CONFIRMADO", "INFORMACION_INSUFICIENTE")]
    return {"max_chars": max_chars, "n_required": len(rows),
            "batches": [{"batch_id": f"b{i+1:02d}", "match_ids": [m["match_id"] for m in b], "competitions": sorted({m["competition"] for m in b}),
                         "agents": list(AGENTS_PER_BATCH)} for i, b in enumerate(batches)],
            "discrepancy_batch": {"batch_id": "disc", "match_ids": disc, "agents": ["verificador-mercados"], "sampling": "NINGUNO: todas las discrepancias se revisan"}}


def check_results(batches, results):
    if isinstance(results, dict):
        results = [results]
    expected = {}
    for b in batches["batches"] + [batches["discrepancy_batch"]]:
        for ag in b["agents"]:
            expected.setdefault((b["batch_id"], ag), set(b["match_ids"]))
    seen, dups, unknown, pend = {}, [], [], []
    for r in results:
        key = (r["batch_id"], r["agent"])
        if key not in expected:
            unknown.append({"key": key, "motivo": "lote/agente no asignado"})
            continue
        ids = seen.setdefault(key, {})
        for row in r["rows"]:
            mid = row["match_id"]
            if mid not in expected[key]:
                unknown.append({"key": key, "match_id": mid})
            elif mid in ids:
                dups.append({"key": key, "match_id": mid})
            else:
                ids[mid] = row
            if row.get("review_status") != "REVISADO":
                pend.append({"key": key, "match_id": mid, "status": row.get("review_status")})
    missing = {f"{k[0]}/{k[1]}": sorted(exp - set(seen.get(k, {}))) for k, exp in expected.items() if exp - set(seen.get(k, {}))}
    per_agent = {}
    for (bid, ag), exp in expected.items():
        d = per_agent.setdefault(ag, {"asignadas": 0, "revisadas": 0})
        d["asignadas"] += len(exp)
        d["revisadas"] += sum(1 for row in seen.get((bid, ag), {}).values() if row.get("review_status") == "REVISADO")
    corrections = [{"key": k, "match_id": mid, "corrections": row.get("corrections")} for k, ids in seen.items() for mid, row in ids.items() if row.get("corrections")]
    ok = not (missing or dups or unknown or pend)
    return {"ok": ok, "missing": missing, "duplicates": dups, "unknown": unknown, "pending_rows": pend,
            "per_agent": per_agent, "corrections": corrections}


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("cmd", choices=["make", "check"])
    ap.add_argument("--run", required=True)
    ap.add_argument("--max-chars", type=int, default=50000)
    ap.add_argument("--results")
    a = ap.parse_args(argv)
    inv = common.read_json(os.path.join(a.run, "inventory.json"))
    mx = common.read_json(os.path.join(a.run, "matrix.json"), {"matches": {}})
    if not inv:
        print("error: falta inventory.json", file=sys.stderr)
        return 2
    if a.cmd == "make":
        b = make_batches(inv, mx, a.max_chars)
        common.write_json_atomic(os.path.join(a.run, "batches.json"), b)
        print(f"{len(b['batches'])} lotes para {b['n_required']} partidos requeridos; lote de discrepancias: {len(b['discrepancy_batch']['match_ids'])}")
        return 0
    if not a.results:
        print("error: check requiere --results", file=sys.stderr)
        return 2
    batches = common.read_json(os.path.join(a.run, "batches.json"))
    res = json.load(open(a.results, encoding="utf-8"))
    rep = check_results(batches, res)
    common.write_json_atomic(os.path.join(a.run, "reviews.json"), rep)
    print(json.dumps(rep, ensure_ascii=False, indent=2))
    return 0 if rep["ok"] else 3


if __name__ == "__main__":
    sys.exit(main())
