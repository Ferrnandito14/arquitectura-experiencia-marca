#!/usr/bin/env python3
"""Vincula a mano un partido del inventario con su registro de apifootball cuando la alineación automática por nombre falló
(p. ej. «ABB» = «Academia del Balompie», «Al Hazm» = «Al Hazem»). No decide por parecido: exige que el partido de la API tenga la MISMA hora de inicio (±30 min)
y deja constancia (`manual_link`) en el propio registro del inventario. Después reinicia su entrada en la cola para que level1.py la procese.

Uso:  link_api.py --run runs/2026-10-15 --match-id m-… --api-id 825173
El inventario se reescribe con el mismo contenido más: source_match_ids.apifootball, extra.api, source_names += apifootball, y `manual_link` con la evidencia."""
import argparse
import os
import sys
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import adapters  # noqa: E402
import common  # noqa: E402


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--run", required=True)
    ap.add_argument("--match-id", required=True)
    ap.add_argument("--api-id", required=True)
    ap.add_argument("--tolerance-min", type=int, default=30)
    a = ap.parse_args(argv)
    key = adapters.apif_key()
    if not key:
        print("error: sin clave de apifootball", file=sys.stderr)
        return 2
    inv_path = os.path.join(a.run, "inventory.json")
    inv = common.read_json(inv_path)
    m = next((x for x in inv["matches"] if x["match_id"] == a.match_id), None)
    if m is None:
        print("error: match_id no está en el inventario", file=sys.stderr)
        return 2
    client = common.Client(os.path.join(a.run, "cache"), os.path.join(a.run, "sources", "consultas.jsonl"), policy=common.Policy(), min_interval=1.0, ttl=3600)
    ev = adapters.apif_call(client, key, action="get_events", match_id=a.api_id, timezone="UTC")
    if not ev or not isinstance(ev, list) or not isinstance(ev[0], dict):
        print("error: la API no devolvió el partido", file=sys.stderr)
        return 2
    e = ev[0]
    t_api = datetime.strptime(f"{e['match_date']} {e['match_time']}", "%Y-%m-%d %H:%M").replace(tzinfo=timezone.utc)
    t_inv = datetime.fromisoformat(m["normalized_datetime_utc"].replace("Z", "+00:00"))
    dmin = abs((t_api - t_inv).total_seconds()) / 60
    if dmin > a.tolerance_min:
        print(f"error: la hora no coincide ({dmin:.0f} min de diferencia); no se vincula", file=sys.stderr)
        return 2
    m.setdefault("extra", {})["api"] = {"away_id": e["match_awayteam_id"], "away_name": e["match_awayteam_name"], "home_id": e["match_hometeam_id"], "home_name": e["match_hometeam_name"],
                                        "league_id": e["league_id"], "league_name": e["league_name"], "match_id": e["match_id"], "referee": (e.get("match_referee") or None), "status_raw": e.get("match_status", "")}
    m.setdefault("source_match_ids", {})["apifootball"] = e["match_id"]
    if "apifootball" not in m.setdefault("source_names", []):
        m["source_names"].append("apifootball")
    m.setdefault("verification_sources", [])
    if "apifootball" not in m["verification_sources"]:
        m["verification_sources"].append("apifootball")
    m["manual_link"] = {"api_match_id": e["match_id"], "api_teams": f"{e['match_hometeam_name']} – {e['match_awayteam_name']}", "api_utc": t_api.strftime("%Y-%m-%dT%H:%M:%SZ"),
                        "diferencia_min": round(dmin, 1), "criterio": "misma hora de inicio (±%d min) y mismos equipos según la persona que revisó; la alineación automática por nombre falló" % a.tolerance_min,
                        "vinculado_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")}
    common.write_json_atomic(inv_path, inv)
    st_path = os.path.join(a.run, "state.json")
    st = common.read_json(st_path, {"matches": {}})
    if a.match_id in st["matches"]:
        st["matches"][a.match_id].update({"status": "PENDIENTE", "attempts": 0})
        common.write_json_atomic(st_path, st)
    print(f"vinculado {m['home_team']} – {m['away_team']} ({a.match_id}) con apifootball {e['match_id']}: {e['match_hometeam_name']} – {e['match_awayteam_name']} (hora igual, Δ {dmin:.0f} min); cola reiniciada")
    return 0


if __name__ == "__main__":
    sys.exit(main())
