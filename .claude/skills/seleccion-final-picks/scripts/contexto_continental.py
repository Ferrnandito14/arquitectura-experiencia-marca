#!/usr/bin/env python3
"""Referencia AMPLIADA para torneos continentales/internacionales (indicación de la persona usuaria, 15-oct): en copas cortas la muestra de la misma competición es pequeña (≈7–8 partidos),
así que se complementa con el historial de LIGA y COPA de cada equipo y con los ENFRENTAMIENTOS PREVIOS entre ambos (get_H2H). Es REFERENCIA descriptiva para los agentes y el libro:
NO cambia `p_modelo` ni ningún peso (sin pesos arbitrarios; el modelo sigue sin validar). Cada ámbito se resume por separado (liga doméstica / copa nacional / continental) con su n.

Guardia de identidad: la API reutiliza un mismo team_id para clubes homónimos de otros países (el id 989 «Estudiantes» devuelve también la liga de Aruba, con goleadas 10-0). Se toma como país
doméstico el más frecuente entre las filas no internacionales y se EXCLUYEN (con aviso) las filas de otro país. Amistosos fuera. Sin ajuste por rival: se dice en la nota.

Uso:  contexto_continental.py --run runs/2026-10-15 [--ids ligas/ids.json] [--days 240]   ->   runs/<fecha>/contexto_continental.json"""
import argparse
import datetime
import os
import re
import sys
from collections import Counter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import adapters  # noqa: E402
import common  # noqa: E402
import rotation_risk  # noqa: E402

INTL_COUNTRIES = {"intl", "world", "eurocups", ""}
CONTINENTAL_RE = re.compile(r"libertadores|sudamericana|champions league|europa|conference|concacaf|afc |caf |nations league|world cup|euro |copa am[eé]rica|recopa|supercopa|super cup", re.I)
CUP_RE = re.compile(r"copa|cup|coupe|pokal|trophy|coppa|taça|beker|fa cup|knock", re.I)
FINAL = ("finished", "after pen.", "after extra time")


def is_continental(league_name):
    return bool(CONTINENTAL_RE.search(league_name or ""))


def ambito(league_name, country):
    """continental | copa_nacional | liga (por nombre y país de la competición)."""
    if is_continental(league_name) or (country or "").lower() == "intl":
        return "continental"
    return "copa_nacional" if CUP_RE.search(league_name or "") else "liga"


def identity_filter(events):
    """(eventos válidos, nº excluidos, país doméstico). Excluye amistosos y filas de otro país distinto del doméstico (club homónimo)."""
    ev = [e for e in events if "friendl" not in (e.get("league_name") or "").lower()]
    intl = lambda e: (e.get("country_name") or "").lower() in INTL_COUNTRIES or is_continental(e.get("league_name"))      # UEFA llega con país «Europe», CONMEBOL con «intl»
    cnt = Counter((e.get("country_name") or "").lower() for e in ev if not intl(e))
    home = cnt.most_common(1)[0][0] if cnt else None
    keep, out = [], 0
    for e in ev:
        c = (e.get("country_name") or "").lower()
        if home and not intl(e) and c != home:
            out += 1
            continue
        keep.append(e)
    return keep, out, home


def summarize(rows):
    """Resumen descriptivo de filas de historial (gf, ga): n, goles por partido, % menos/más de 2.5, % ambos anotan."""
    rows = [r for r in rows if r.get("gf") is not None and r.get("ga") is not None]
    n = len(rows)
    if not n:
        return {"n": 0}
    tot = [r["gf"] + r["ga"] for r in rows]
    return {"n": n, "goles_por_partido": round(sum(tot) / n, 2), "gf": round(sum(r["gf"] for r in rows) / n, 2), "ga": round(sum(r["ga"] for r in rows) / n, 2),
            "pct_menos_2_5": round(100 * sum(t <= 2 for t in tot) / n), "pct_mas_2_5": round(100 * sum(t >= 3 for t in tot) / n),
            "pct_ambos_anotan": round(100 * sum(r["gf"] > 0 and r["ga"] > 0 for r in rows) / n)}


def team_context(call, tid, md, days):
    d0 = (datetime.date.fromisoformat(md) - datetime.timedelta(days=days)).isoformat()
    evs = call(action="get_events", **{"from": d0, "to": md, "team_id": tid, "timezone": "UTC"})
    evs = [e for e in evs if (e.get("match_status") or "").lower() in FINAL and e["match_date"] < md]
    keep, excl, home = identity_filter(evs)
    by = {"liga": [], "copa_nacional": [], "continental": []}
    for e in keep:
        r = adapters.apif_history_row(e, tid)
        if r:
            by[ambito(e.get("league_name"), e.get("country_name"))].append(r)
    return {"pais_domestico": home, "excluidas_por_identidad": excl, "ambitos": {k: summarize(v) for k, v in by.items()}}


def h2h_context(call, home_id, away_id, md):
    h = call(action="get_H2H", firstTeamId=str(home_id), secondTeamId=str(away_id))
    rows = [e for e in (h.get("firstTeam_VS_secondTeam") or []) if (e.get("match_status") or "").lower() in FINAL and e["match_date"] < md]
    rows.sort(key=lambda e: e["match_date"], reverse=True)
    out, tot = [], []
    for e in rows[:10]:
        try:
            a, b = int(e["match_hometeam_score"]), int(e["match_awayteam_score"])
        except (TypeError, ValueError):
            continue
        out.append({"fecha": e["match_date"], "competicion": e.get("league_name"), "local": e["match_hometeam_name"], "visitante": e["match_awayteam_name"], "marcador": f"{a}-{b}"})
        tot.append(a + b)
    n = len(tot)
    return {"n": n, "partidos": out, "goles_por_partido": round(sum(tot) / n, 2) if n else None, "pct_menos_2_5": round(100 * sum(t <= 2 for t in tot) / n) if n else None}


NOTE = ("Referencia descriptiva (no entra en p_modelo): historial de liga, copa nacional y continental del equipo por separado, con n; sin ajuste por rival ni por nivel de la liga "
        "(un 2.8 de goles en el Brasileirão no es comparable con un 1.4 en Argentina); H2H = últimos enfrentamientos directos (pocos y de contextos distintos).")


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--run", required=True)
    ap.add_argument("--days", type=int, default=240)
    ap.add_argument("--max-matches", type=int, default=120)
    a = ap.parse_args(argv)
    key = adapters.apif_key()
    if not key:
        print("error: sin clave de apifootball", file=sys.stderr)
        return 2
    inv = common.read_json(os.path.join(a.run, "inventory.json"))["matches"]
    client = common.Client(os.path.join(a.run, "cache"), os.path.join(a.run, "sources", "consultas.jsonl"), policy=common.Policy(), min_interval=1.0, ttl=3600)
    call = lambda **p: adapters.apif_call(client, key, **p)  # noqa: E731
    path = os.path.join(a.run, "contexto_continental.json")
    out = common.read_json(path, {}) or {}
    todo = [m for m in inv if m.get("analysis_required") and ((m.get("extra") or {}).get("api") or {}).get("match_id")
            and is_continental(m["extra"]["api"].get("league_name")) and m["match_id"] not in out]
    stopped = None
    for m in todo[:a.max_matches]:
        ap_ = m["extra"]["api"]
        try:
            md = m["normalized_datetime_utc"][:10]
            rec = {"partido": f"{m['home_team']} – {m['away_team']}", "competicion": ap_["league_name"], "nota": NOTE,
                   "local": team_context(call, ap_["home_id"], md, a.days), "visitante": team_context(call, ap_["away_id"], md, a.days),
                   "h2h": h2h_context(call, ap_["home_id"], ap_["away_id"], md), "decisiva": rotation_risk.decisive_phase(ap_["league_name"])}
        except common.PolicyError as err:
            stopped = str(err)
            break
        out[m["match_id"]] = rec
    common.write_json_atomic(path, out)
    if stopped:
        print(f"AVISO: tope de descargas del proceso ({stopped}); relanza el mismo comando (lo hecho se conserva).")
    print(f"contexto_continental.json: {len(out)} partidos; pendientes: {len([m for m in todo if m['match_id'] not in out])}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
