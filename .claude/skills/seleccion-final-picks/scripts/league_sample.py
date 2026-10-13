#!/usr/bin/env python3
"""Muestras de LIGA/TEMPORADA COMPLETA (auditoría 13-oct: los últimos ≤10 partidos dan n=6–10 y ordenan por ruido). Descarga los partidos finalizados de una liga con
`get_events` por `league_id` (tarjetas con la regla de la casa, córners, árbitro) y calcula medias de la liga, de cada equipo y de cada árbitro.
Uso: league_sample.py --run runs/2026-10-13 --league-id 75 [--from 2026-03-01 --to 2026-10-12] -> runs/<fecha>/league_samples/<id>.json"""
import argparse
import json
import os
import statistics
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import adapters  # noqa: E402
import common  # noqa: E402


def compact(e):
    """Fila mínima de un partido finalizado (para guardar sin los miles de KB de estadísticas por jugador)."""
    try:
        h, a = int(e["match_hometeam_score"]), int(e["match_awayteam_score"])
    except (KeyError, TypeError, ValueError):
        return None
    pts = adapters._card_points(e)
    cs = adapters._stat(e, "Corners")
    return {"id": e.get("match_id"), "fecha": e.get("match_date"), "local": e.get("match_hometeam_name"), "visitante": e.get("match_awayteam_name"), "gl": h, "gv": a,
            "tarjetas": None if pts is None else list(pts), "corners": None if not cs else list(cs), "arbitro": (e.get("match_referee") or "").strip() or None}


def _stats(vals, lines):
    vals = [v for v in vals if v is not None]
    if not vals:
        return None
    return {"n": len(vals), "media": round(statistics.mean(vals), 2), **{f"mas_{l}": round(sum(v > l for v in vals) / len(vals), 3) for l in lines}}


def summarize(rows, min_ref=6):
    """Medias de la liga, de cada equipo (partidos en los que juega) y de cada árbitro con ≥min_ref partidos."""
    tot_g = lambda r: r["gl"] + r["gv"]
    tot_c = lambda r: None if r["tarjetas"] is None else sum(r["tarjetas"])
    tot_k = lambda r: None if r["corners"] is None else sum(r["corners"])

    def block(rs):
        return {"goles": _stats([tot_g(r) for r in rs], (1.5, 2.5, 3.5, 4.5)), "tarjetas": _stats([tot_c(r) for r in rs], (3.5, 4.5, 5.5, 6.5)),
                "corners": _stats([tot_k(r) for r in rs], (8.5, 9.5, 10.5))}
    teams, refs = {}, {}
    for r in rows:
        for t in (r["local"], r["visitante"]):
            teams.setdefault(t, []).append(r)
        if r["arbitro"]:
            refs.setdefault(r["arbitro"], []).append(r)
    return {"liga": block(rows), "equipos": {t: block(rs) for t, rs in teams.items()}, "arbitros": {a: block(rs) for a, rs in refs.items() if len(rs) >= min_ref}, "n_partidos": len(rows)}


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--run", default="runs/2026-10-13")
    ap.add_argument("--league-id", required=True)
    ap.add_argument("--from", dest="d_from", default="2026-03-01")
    ap.add_argument("--to", dest="d_to", default="2026-10-12")
    a = ap.parse_args(argv)
    key = adapters.apif_key()
    if not key:
        print("error: sin clave de apifootball", file=sys.stderr)
        return 2
    client = common.Client(os.path.join(a.run, "cache"), os.path.join(a.run, "sources", "consultas.jsonl"), policy=common.Policy(), min_interval=2.0, ttl=3600)
    ev = adapters.apif_call(client, key, action="get_events", **{"from": a.d_from, "to": a.d_to, "league_id": a.league_id, "timezone": "UTC"})
    rows = [r for r in (compact(e) for e in ev if isinstance(e, dict) and e.get("match_status") == "Finished") if r]
    out = {"league_id": a.league_id, "desde": a.d_from, "hasta": a.d_to, "filas": rows, "resumen": summarize(rows)}
    os.makedirs(os.path.join(a.run, "league_samples"), exist_ok=True)
    common.write_json_atomic(os.path.join(a.run, "league_samples", f"{a.league_id}.json"), out)
    print(f"liga {a.league_id}: {len(rows)} partidos finalizados; media de goles {out['resumen']['liga']['goles']['media'] if out['resumen']['liga']['goles'] else 'n/d'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
