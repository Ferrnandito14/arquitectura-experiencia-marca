#!/usr/bin/env python3
"""Instantánea de ALINEACIONES por partido (Fase 3): ¿hay once publicado? ¿hay bajas registradas? Cada ejecución escribe un archivo NUEVO `runs/<fecha>/lineups/snapshot_<UTC>.json`
(historial append-only; nunca sobrescribe). Sirve de evidencia para la analítica de `market_coverage.py` y para decidir cuándo ejecutar `lineup_check.py` (revisión a T-60 con el once real).

Uso:  lineups_snapshot.py --run runs/2026-10-14 [--matches ids.json|id1,id2] [--window-minutes 90] [--now-utc 2026-10-14T16:00:00Z]
  --window-minutes  solo consulta los partidos que empiezan dentro de esa ventana (T-60: 90); sin él consulta todos los indicados.
Sin once publicado NO se inventa nada: `publicada: false` es el resultado real de la consulta."""
import argparse
import datetime as dt
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import adapters  # noqa: E402
import common  # noqa: E402


def _side(lu, side):
    s = (lu or {}).get(side) or {}
    return {"titulares": len(s.get("starting_lineups") or []), "suplentes": len(s.get("substitutes") or []), "bajas_registradas": len(s.get("missing_players") or [])}


def snapshot_match(match, call, now):
    """Consulta get_lineups de un partido con id de apifootball y resume qué hay publicado. `call(**params)` devuelve la respuesta de la API."""
    mid = (match.get("source_match_ids") or {}).get("apifootball")
    kick = dt.datetime.fromisoformat(match["normalized_datetime_utc"].replace("Z", "+00:00"))
    rec = {"match_id": match["match_id"], "apif_match_id": mid, "partido": f"{match['home_team']} – {match['away_team']}", "inicio_utc": match["normalized_datetime_utc"],
           "minutos_hasta_inicio": round((kick - now).total_seconds() / 60), "consultado_utc": now.strftime("%Y-%m-%dT%H:%M:%SZ")}
    if not mid:
        return dict(rec, consulta="no_realizada", nota="el partido no tiene id en apifootball")
    resp = call(action="get_lineups", match_id=mid)
    lu = ((resp or {}).get(mid) or {}).get("lineup", {}) if isinstance(resp, dict) else {}
    home, away = _side(lu, "home"), _side(lu, "away")
    return dict(rec, consulta="realizada", local=home, visitante=away, publicada=home["titulares"] >= 11 and away["titulares"] >= 11,
                bajas_registradas=home["bajas_registradas"] + away["bajas_registradas"])


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--run", required=True)
    ap.add_argument("--matches", help="ids.json ({etiqueta: match_id}) o ids separados por comas; por defecto, los partidos autorizados del run")
    ap.add_argument("--window-minutes", type=int)
    ap.add_argument("--now-utc", help="instante de referencia (pruebas); por defecto, ahora")
    a = ap.parse_args(argv)
    key = adapters.apif_key()
    if not key:
        print("error: sin clave de apifootball", file=sys.stderr)
        return 2
    import json
    inv = {m["match_id"]: m for m in common.read_json(os.path.join(a.run, "inventory.json"))["matches"]}
    if a.matches:
        ids = list(json.load(open(a.matches, encoding="utf-8")).values()) if os.path.exists(a.matches) else a.matches.split(",")
    else:
        import market_coverage
        ids = [m["match_id"] for m in market_coverage.authorized_from_run(a.run)]
    now = dt.datetime.fromisoformat(a.now_utc.replace("Z", "+00:00")) if a.now_utc else dt.datetime.now(dt.timezone.utc)
    client = common.Client(os.path.join(a.run, "cache"), os.path.join(a.run, "sources", "consultas.jsonl"), policy=common.Policy(), min_interval=1.0, ttl=60)
    call = lambda **p: adapters.apif_call(client, key, **p)  # noqa: E731
    recs, fuera = [], 0
    for i in ids:
        m = inv.get(i)
        if not m:
            continue
        mins = (dt.datetime.fromisoformat(m["normalized_datetime_utc"].replace("Z", "+00:00")) - now).total_seconds() / 60
        if a.window_minutes is not None and not (-120 <= mins <= a.window_minutes):
            fuera += 1
            continue
        recs.append(snapshot_match(m, call, now))
    stamp = now.strftime("%Y%m%dT%H%M%SZ")
    out = {"consultado_utc": now.strftime("%Y-%m-%dT%H:%M:%SZ"), "ventana_minutos": a.window_minutes, "partidos_fuera_de_ventana": fuera, "partidos": recs}
    path = os.path.join(a.run, "lineups", f"snapshot_{stamp}.json")
    if os.path.exists(path):
        print(f"error: {path} ya existe (los snapshots no se sobrescriben)", file=sys.stderr)
        return 2
    common.write_json_atomic(path, out)
    pub = sum(1 for r in recs if r.get("publicada"))
    print(f"{len(recs)} partidos consultados ({fuera} fuera de ventana); once publicado en {pub}; archivo {path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
