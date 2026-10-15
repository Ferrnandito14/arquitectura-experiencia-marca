#!/usr/bin/env python3
"""Riesgo de rotación A PRIORI por equipo (la persona usuaria arma los picks horas antes: no se espera al once). Para los partidos indicados calcula
días de descanso, si hay competición europea/copa en ≤4 días y la tasa de cambios entre los últimos once, y escribe runs/<fecha>/rotation.json que
`tickets.py` usa para vetar unders / rebajar patas de ganador del equipo con riesgo alto.
Uso: rotation_prior.py --run runs/2026-10-13 (--matches id1,id2 | --from-tickets) [--max-teams 40]"""
import argparse
import datetime
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import adapters  # noqa: E402
import common  # noqa: E402
import rotation_risk  # noqa: E402

CUP_RE = re.compile(r"champions|europa|conference|libertadores|sudamericana|copa|cup|coupe|pokal|trophy|coppa|taça|beker", re.I)


def _d(s):
    return datetime.date.fromisoformat(str(s)[:10])


def rest_days(prev_date, match_date):
    """Días entre el último partido del equipo y este (None si no hay dato)."""
    if not prev_date or not match_date:
        return None
    return (_d(match_date) - _d(prev_date)).days


def euro_or_cup_soon(next_events, match_date, window=4):
    """True si hay un partido de competición continental/copa programado en los `window` días posteriores a match_date. next_events: [{'fecha','competicion'}]."""
    md = _d(match_date)
    for e in next_events:
        try:
            delta = (_d(e["fecha"]) - md).days
        except (KeyError, ValueError):
            continue
        if 0 < delta <= window and CUP_RE.search(e.get("competicion") or ""):
            return True
    return False


def team_prior(prev_dates, prev_xis, next_events, match_date):
    cr = rotation_risk.change_rate(prev_xis)
    rd = rest_days(max(prev_dates) if prev_dates else None, match_date)
    r = rotation_risk.prior_risk(rd, euro_or_cup_soon(next_events, match_date), cr)
    r.update({"descanso_dias": rd, "cambios_medios": None if cr is None else round(cr, 2), "partidos_previos": len(prev_dates)})
    return r


def _xi(lineup_side):
    return {p.get("player_key") for p in (lineup_side or {}).get("starting_lineups", []) if p.get("player_key")}


def _one(call, inv, mid, aid):
    """Riesgo a priori de los dos equipos de un partido: (registro, nº de equipos calculados)."""
    n = 0
    e = call(action="get_events", match_id=aid, timezone="UTC")[0]
    md = e["match_date"]
    rec = {"partido": f"{e['match_hometeam_name']} – {e['match_awayteam_name']}", "fecha": md}
    for side, tid in (("home", e["match_hometeam_id"]), ("away", e["match_awayteam_id"])):
        d0 = (_d(md) - datetime.timedelta(days=45)).isoformat()
        d1 = (_d(md) + datetime.timedelta(days=5)).isoformat()
        evs = call(action="get_events", **{"from": d0, "to": d1, "team_id": tid, "timezone": "UTC"})
        prev = [x for x in evs if x.get("match_status") == "Finished" and x["match_date"] < md][-4:]
        nxt = [{"fecha": x["match_date"], "competicion": x.get("league_name")} for x in evs if x["match_date"] > md and x.get("match_status") != "Finished"]
        xis = []
        for x in reversed(prev):          # del más reciente al más antiguo
            L = (call(action="get_lineups", match_id=x["match_id"]).get(x["match_id"]) or {}).get("lineup", {})
            xis.append(_xi(L.get("home" if x["match_hometeam_id"] == tid else "away")))
        rec[side] = team_prior([x["match_date"] for x in prev], xis, nxt, md)
        n += 1
    return rec, n


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--run", default="runs/2026-10-13")
    ap.add_argument("--matches", default="")
    ap.add_argument("--from-tickets", action="store_true")
    ap.add_argument("--max-teams", type=int, default=40)
    a = ap.parse_args(argv)
    key = adapters.apif_key()
    if not key:
        print("error: sin clave de apifootball", file=sys.stderr)
        return 2
    inv = {m["match_id"]: m for m in common.read_json(os.path.join(a.run, "inventory.json"))["matches"]}
    ids = [x for x in a.matches.split(",") if x]
    if a.from_tickets:
        tj = common.read_json(os.path.join(a.run, "tickets.json"))
        for lst in (tj.get("top_picks") or {}).values():
            ids += [p["match_id"] for p in lst]
        for t in tj.get("targets", []):
            for tk in t["tickets"]:
                ids += [it["match_id"] for it in tk["items"]]
    ids = [i for i in dict.fromkeys(ids) if i in inv and (inv[i].get("source_match_ids") or {}).get("apifootball")]
    client = common.Client(os.path.join(a.run, "cache"), os.path.join(a.run, "sources", "consultas.jsonl"), policy=common.Policy(), min_interval=1.0, ttl=3600)
    call = lambda **p: adapters.apif_call(client, key, **p)  # noqa: E731
    out, teams_done = dict(common.read_json(os.path.join(a.run, "rotation.json"), {}) or {}), 0      # reanudable: lo ya calculado se conserva (el tope de descargas es por proceso)
    pending = [i for i in ids if i not in out]
    stopped = None
    for mid in pending:
        if teams_done >= a.max_teams:
            break
        aid = inv[mid]["source_match_ids"]["apifootball"]
        try:
            rec = _one(call, inv, mid, aid)
        except common.PolicyError as err:           # tope de descargas por proceso: se guarda lo hecho y se puede relanzar el mismo comando
            stopped = str(err)
            break
        out[mid], n_teams = rec
        teams_done += n_teams
    common.write_json_atomic(os.path.join(a.run, "rotation.json"), out)
    if stopped:
        print(f"AVISO: se detuvo por el tope de descargas del proceso ({stopped}); vuelve a lanzar el mismo comando para continuar (lo hecho se conserva).")
    print(f"rotation.json: {len(out)} partidos ({teams_done} equipos en esta pasada; {len([i for i in ids if i not in out])} pendientes)")
    for mid, r in out.items():
        print(f"- {r['partido']}: local {r['home']['nivel']} ({'; '.join(r['home']['motivos']) or '—'}) · visitante {r['away']['nivel']} ({'; '.join(r['away']['motivos']) or '—'})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
