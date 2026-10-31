#!/usr/bin/env python3
"""Dossier de cada equipo de las patas finalistas, SOLO con TheStatsAPI y con los marcadores ORIENTADOS en código.

El deportivo (Sonnet) invertía marcadores de partidos de visita al leerlos en bruto: aquí cada partido se resume desde el
punto de vista del equipo (G/E/P, goles a favor y en contra, local/visita, rival), con tasas de más de 2.5 y ambos anotan.
Incluye bajas y sanciones activas (cantidad, motivo, regreso esperado).

Uso:  dossier_equipo.py --run runs/2026-11-01 [--n 8]
Entrada: <run>/pool/finalistas.json ; salida: <run>/dossier/dossier_finalistas.json y <run>/dossier/<team_id>.json (caché)."""
import argparse
import json
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pool_mercado as pm  # noqa: E402


def orientar(match, team_id):
    """Resumen de un partido TERMINADO desde el punto de vista de `team_id`; None si no hay marcador o el equipo no juega."""
    h, a = match["home_team"], match["away_team"]
    sc = match.get("score") or {}
    gh, ga = sc.get("home"), sc.get("away")
    if gh is None or ga is None or match.get("status") != "finished":
        return None
    if team_id == h["id"]:
        gf, gc, lado, rival = gh, ga, "local", a["name"]
    elif team_id == a["id"]:
        gf, gc, lado, rival = ga, gh, "visita", h["name"]
    else:
        return None
    return {"fecha": match["utc_date"][:10], "competition_id": match.get("competition_id"), "lado": lado, "rival": rival,
            "gf": gf, "gc": gc, "resultado": "G" if gf > gc else ("E" if gf == gc else "P"), "marcador_equipo": f"{gf}-{gc}", "total_goles": gf + gc}


def resumen(partidos):
    n = len(partidos)
    if not n:
        return {"n": 0}
    def tasa(f):
        return round(sum(1 for p in partidos if f(p)) / n, 3)
    por_lado = {}
    for lado in ("local", "visita"):
        s = [p for p in partidos if p["lado"] == lado]
        por_lado[lado] = {"n": len(s), "G": sum(p["resultado"] == "G" for p in s), "E": sum(p["resultado"] == "E" for p in s), "P": sum(p["resultado"] == "P" for p in s)}
    return {"n": n, "G": sum(p["resultado"] == "G" for p in partidos), "E": sum(p["resultado"] == "E" for p in partidos), "P": sum(p["resultado"] == "P" for p in partidos),
            "gf_medio": round(sum(p["gf"] for p in partidos) / n, 2), "gc_medio": round(sum(p["gc"] for p in partidos) / n, 2),
            "mas_2_5": tasa(lambda p: p["total_goles"] > 2.5), "ambos_anotan": tasa(lambda p: p["gf"] > 0 and p["gc"] > 0),
            "sin_perder": tasa(lambda p: p["resultado"] != "P"), "por_lado": por_lado}


def bajas(body):
    d = (body or {}).get("data") or {}
    inj = [{"estado": i.get("status"), "motivo": i.get("reason"), "regreso": (i.get("expected_return") or "")[:10]} for i in d.get("injuries", []) if i.get("active", True)]
    sus = [{"motivo": s.get("reason"), "partidos": s.get("matches"), "fin": (s.get("end_date") or "")[:10]} for s in d.get("suspensions", []) if s.get("active", True)]
    return {"lesiones_activas": len(inj), "sanciones_activas": len(sus), "lesiones": inj[:8], "sanciones": sus[:8]}


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--run", required=True)
    ap.add_argument("--n", type=int, default=8)
    a = ap.parse_args(argv)
    key = pm._key()
    fin = json.load(open(os.path.join(a.run, "pool", "finalistas.json")))["patas"]
    matches = {m["id"]: m for m in json.load(open(os.path.join(a.run, "thestatsapi", "matches.json")))}
    os.makedirs(os.path.join(a.run, "dossier"), exist_ok=True)
    equipos = {}
    for p in fin:
        m = matches[p["match_id"]]
        for lado in ("home_team", "away_team"):
            equipos[m[lado]["id"]] = m[lado]["name"]
    for tid, nombre in equipos.items():
        ruta = os.path.join(a.run, "dossier", tid + ".json")
        if os.path.exists(ruta):
            continue
        st, body = pm._get(f"/football/matches?team_id={tid}&status=finished&per_page={a.n}&sort=-utc_date", key)
        time.sleep(2.3)
        st2, inj = pm._get(f"/football/teams/{tid}/injuries-suspensions", key)
        time.sleep(2.3)
        st3, prox = pm._get(f"/football/matches?team_id={tid}&status=scheduled&sort=utc_date&per_page=2", key)
        time.sleep(2.3)
        partidos = [x for x in (orientar(m, tid) for m in (body or {}).get("data", [])) if x]
        proximos = [{"id": x["id"], "utc": x["utc_date"], "rival": (x["away_team"] if x["home_team"]["id"] == tid else x["home_team"])["name"], "competition_id": x.get("competition_id")} for x in (prox or {}).get("data", [])]
        json.dump({"team_id": tid, "equipo": nombre, "ultimos": partidos, "resumen": resumen(partidos), "bajas": bajas(inj), "proximos": proximos}, open(ruta, "w"), ensure_ascii=False)
    salida = []
    for p in fin:
        m = matches[p["match_id"]]
        fila = {"key": p["match_id"] + "|" + p["seleccion"], "partido": p["partido"], "seleccion": p["seleccion"], "hora_caracas": p["hora_caracas"],
                "competition_id": m.get("competition_id"), "matchday": m.get("matchday"), "stage": m.get("stage")}
        fila["alertas_fuente"] = []
        for lado, rol in (("home_team", "local"), ("away_team", "visitante")):
            fila[rol] = json.load(open(os.path.join(a.run, "dossier", m[lado]["id"] + ".json")))
            prox = fila[rol].get("proximos") or []
            if not prox or prox[0]["id"] != p["match_id"]:
                fila["alertas_fuente"].append(f"{fila[rol]['equipo']}: su próximo partido en TheStatsAPI no es este (primero: {prox[0]['rival'] + ' ' + prox[0]['utc'][:16] if prox else 'ninguno'})")
        salida.append(fila)
    json.dump({"patas": salida}, open(os.path.join(a.run, "dossier", "dossier_finalistas.json"), "w"), ensure_ascii=False, indent=1)
    print(f"{len(salida)} patas, {len(equipos)} equipos")
    return 0


if __name__ == "__main__":
    sys.exit(main())
