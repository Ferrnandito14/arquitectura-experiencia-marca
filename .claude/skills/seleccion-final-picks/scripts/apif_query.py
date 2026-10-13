#!/usr/bin/env python3
"""Consulta puntual y SEGURA a apifootball para agentes (Nivel 2). La clave sale del entorno (APIFOOTBALL_KEY / APIFOOTBALL_KEY_FILE) o de --key-file;
nunca se imprime ni se registra (common.redact_url). Pasa por la política de fuentes, caché y límite por ejecución.

Uso:  apif_query.py ACCION [clave=valor ...] [--run runs/2026-10-13] [--key-file RUTA] [--max-chars 6000]
Acciones permitidas: get_events, get_standings, get_H2H, get_lineups, get_statistics, get_odds, get_teams, get_leagues.
Ejemplos:  apif_query.py get_events match_id=123 timezone=UTC
           apif_query.py get_H2H firstTeamId=10 secondTeamId=20
Límite de cortesía para agentes: 120 consultas NO cacheadas por ejecución de la sesión (contador en <run>/sources/agent_api_calls.json).
"""
import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import adapters  # noqa: E402
import common  # noqa: E402

ALLOWED = {"get_events", "get_standings", "get_H2H", "get_lineups", "get_statistics", "get_odds", "get_teams", "get_leagues"}
AGENT_CAP = 120


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("action")
    ap.add_argument("params", nargs="*")
    ap.add_argument("--run", default="runs/2026-10-13")
    ap.add_argument("--key-file")
    ap.add_argument("--max-chars", type=int, default=6000)
    a = ap.parse_args(argv)
    if a.action not in ALLOWED:
        print(f"error: acción no permitida ({sorted(ALLOWED)})", file=sys.stderr)
        return 2
    if a.key_file:
        os.environ["APIFOOTBALL_KEY_FILE"] = a.key_file
    key = adapters.apif_key()
    if not key:
        print("error: sin clave (APIFOOTBALL_KEY / APIFOOTBALL_KEY_FILE / --key-file)", file=sys.stderr)
        return 2
    params = {}
    for p in a.params:
        if "=" not in p:
            print(f"error: parámetro inválido {p!r} (usa clave=valor)", file=sys.stderr)
            return 2
        k, v = p.split("=", 1)
        if k.lower() in ("apikey", "api_key", "key", "token"):
            print("error: no se admite pasar la clave como parámetro", file=sys.stderr)
            return 2
        params[k] = v
    counter_path = os.path.join(a.run, "sources", "agent_api_calls.json")
    cnt = common.read_json(counter_path, {"n": 0})
    if cnt["n"] >= AGENT_CAP:
        print(f"error: tope de {AGENT_CAP} consultas de agentes alcanzado", file=sys.stderr)
        return 3
    client = common.Client(os.path.join(a.run, "cache"), os.path.join(a.run, "sources", "consultas.jsonl"), policy=common.Policy(),
                           min_interval=2.0, ttl=24 * 3600)
    try:
        data = adapters.apif_call(client, key, action=a.action, **params)
    except adapters.ApiLimit as e:
        print(f"error: límite/clave de la API: {e}", file=sys.stderr)
        return 3
    except (common.PolicyError, common.FetchError) as e:
        print(f"error: {e}", file=sys.stderr)
        return 3
    cnt["n"] += 1
    common.write_json_atomic(counter_path, cnt)
    text = json.dumps(data, ensure_ascii=False, indent=None, separators=(",", ":"))
    if len(text) > a.max_chars:
        text = text[:a.max_chars] + f"…[truncado: {len(text)} caracteres; usa parámetros más específicos]"
    print(text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
