#!/usr/bin/env python3
"""Revisión a T-60 min con el once REAL. Uso: lineup_check.py --run runs/2026-10-13 --match-id 853232 [--last 4]
Compara los titulares de hoy con los de los últimos partidos de cada equipo (get_events por equipo + get_lineups), calcula habituales y riesgo, y lista los
habituales que NO están en el once (OJO: eso no es una baja confirmada: puede ser rotación, suplencia habitual o lesión; la API no lo distingue)."""
import argparse
import os
import sys
from collections import Counter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import adapters  # noqa: E402
import common  # noqa: E402
import rotation_risk  # noqa: E402


def xi_from(lineup_side):
    return {p.get("player_key"): p.get("lineup_player") for p in (lineup_side or {}).get("starting_lineups", []) if p.get("player_key")}


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--run", default="runs/2026-10-13")
    ap.add_argument("--match-id", required=True)
    ap.add_argument("--last", type=int, default=4)
    a = ap.parse_args(argv)
    key = adapters.apif_key()
    if not key:
        print("error: sin clave de apifootball", file=sys.stderr)
        return 2
    client = common.Client(os.path.join(a.run, "cache"), os.path.join(a.run, "sources", "consultas.jsonl"), policy=common.Policy(), min_interval=1.0, ttl=60)
    call = lambda **p: adapters.apif_call(client, key, **p)  # noqa: E731
    e = call(action="get_events", match_id=a.match_id, timezone="UTC")[0]
    lu = (call(action="get_lineups", match_id=a.match_id).get(a.match_id) or {}).get("lineup", {})
    print(f"# {e['match_hometeam_name']} – {e['match_awayteam_name']} ({e.get('match_date')} {e.get('match_time')} UTC)")
    for side, tid, name in (("home", e["match_hometeam_id"], e["match_hometeam_name"]), ("away", e["match_awayteam_id"], e["match_awayteam_name"])):
        today = xi_from(lu.get(side))
        if not today:
            print(f"- {name}: SIN ONCE PUBLICADO todavía (usa el riesgo de rotación a priori; vuelve a consultar a T-60 min)")
            continue
        evs = [x for x in call(action="get_events", **{"from": "2026-08-01", "to": e["match_date"], "team_id": tid, "timezone": "UTC"}) if x.get("match_status") == "Finished"][-a.last:]
        prev = []
        for x in evs:
            L = (call(action="get_lineups", match_id=x["match_id"]).get(x["match_id"]) or {}).get("lineup", {})
            prev.append(set(xi_from(L.get("home" if x["match_hometeam_id"] == tid else "away"))))
        r = rotation_risk.real_risk(set(today), prev)
        cnt = Counter(p for xi in prev for p in xi)
        absent = [today.get(p) or p for p, n in cnt.most_common(13) if p not in today and n >= max(2, len(prev) - 1)]
        print(f"- {name}: habituales en el once {r['habituales']}/11 → riesgo de rotación {r['nivel']}; habituales fuera del once (NO es baja confirmada): {absent or '—'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
