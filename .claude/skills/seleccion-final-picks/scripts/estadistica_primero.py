#!/usr/bin/env python3
"""ESTADÍSTICA PRIMERO: la probabilidad de cada pata sale del historial deportivo de los dos equipos, NO del mercado.

El mercado (cuotas de la casa o de referencia) NO participa en la elección de patas: solo se compara DESPUÉS (precio justo, EV).
Cada pata lleva su muestra (n de cada equipo); sin muestra suficiente (n < MIN_N) la pata no existe.

Uso:
  estadistica_primero.py fetch   --run runs/2026-11-02 [--desde 14:00] [--n 8] [--sin-stats]   # descarga historial (+ stats de córners/tarjetas) a <run>/est/
  estadistica_primero.py analisis --run runs/2026-11-02 [--desde 14:00]                         # calcula P deportiva por pata -> <run>/pool/est_patas.json

Fuentes: TheStatsAPI /football/matches (marcadores) y /football/matches/{id}/stats (córners, amarillas, rojas).
Tarjetas: puntos de la casa = amarillas + 2 × rojas (aproximación: la API no separa la roja de la doble amarilla).
"""
import argparse
import json
import math
import os
import sys
import time
from datetime import datetime, timedelta, timezone

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pool_mercado as pm  # noqa: E402

CARACAS = timezone(timedelta(hours=-4))
MIN_N = 8
LINEAS_GOLES = (1.5, 2.5, 3.5, 4.5)
LINEAS_GOLES_EQ = (0.5, 1.5)
LINEAS_CORNERS = (8.5, 9.5, 10.5, 11.5)
LINEAS_CORNERS_EQ = (2.5, 3.5, 4.5, 5.5, 6.5)
LINEAS_TARJETAS = (2.5, 3.5, 4.5, 5.5, 6.5)


def hora_caracas(utc):
    return datetime.strptime(utc[:16], "%Y-%m-%dT%H:%M").replace(tzinfo=timezone.utc).astimezone(CARACAS)


def universo(run, desde, dia):
    """Partidos programados, masculinos, del día local `dia` con hora >= desde (HH:MM) y con cuotas descargadas."""
    base = os.path.join(run, "thestatsapi")
    matches = json.load(open(os.path.join(base, "matches.json")))
    malos, sin_ficha = pm.equipos_no_masculinos(run)
    ruta_ex = os.path.join(run, "pool", "excluidos.json")
    ex = {x["match_id"] for x in json.load(open(ruta_ex))} if os.path.exists(ruta_ex) else set()
    hh, mm = (int(x) for x in desde.split(":"))
    out = []
    for m in matches:
        if m["status"] != "scheduled" or m["id"] in malos or m["id"] in ex or m["id"] in sin_ficha:
            continue
        if pm.EXCLUIR_EQUIPO.search(m["home_team"]["name"] + " " + m["away_team"]["name"]):
            continue
        h = hora_caracas(m["utc_date"])
        if h.strftime("%Y-%m-%d") != dia or (h.hour, h.minute) < (hh, mm):
            continue
        out.append(m)
    return out


def _find(d, clave):
    if isinstance(d, dict):
        if clave in d:
            return d[clave]
        for v in d.values():
            r = _find(v, clave)
            if r is not None:
                return r
    return None


def _par(stats, clave):
    c = _find(stats, clave)
    a = (c or {}).get("all") if isinstance(c, dict) else None
    if not isinstance(a, dict) or a.get("home") is None or a.get("away") is None:
        return None
    return a["home"], a["away"]


def cmd_fetch(a):
    key = pm._key()
    est = os.path.join(a.run, "est")
    os.makedirs(est, exist_ok=True)
    U = universo(a.run, a.desde, a.dia)
    equipos = {}
    for m in U:
        for l in ("home_team", "away_team"):
            equipos[m[l]["id"]] = m[l]["name"]
    print(f"{len(U)} partidos, {len(equipos)} equipos", flush=True)
    items = list(equipos.items())
    if a.orden == "atras":
        items.reverse()
    elif a.orden == "azar":
        import random
        random.Random(7).shuffle(items)
    for i, (tid, nom) in enumerate(items, 1):
        ruta = os.path.join(est, f"lista_{tid}.json")
        if os.path.exists(ruta):
            filas = json.load(open(ruta))
        else:
            st, b = pm._get(f"/football/matches?team_id={tid}&status=finished&per_page={a.n}&sort=-utc_date", key)
            time.sleep(2.2)
            filas = []
            for x in (b or {}).get("data", [])[: a.n]:
                sc = x.get("score") or {}
                if sc.get("home") is None or sc.get("away") is None:
                    continue
                filas.append({"id": x["id"], "fecha": x["utc_date"][:10], "h": x["home_team"]["id"], "a": x["away_team"]["id"],
                              "hn": x["home_team"]["name"], "an": x["away_team"]["name"], "gh": sc["home"], "ga": sc["away"], "comp": x.get("competition_id")})
            json.dump(filas, open(ruta, "w"), ensure_ascii=False)
        if not a.sin_stats:
            for f in filas:
                rs = os.path.join(est, f"stats_{f['id']}.json")
                if os.path.exists(rs):
                    continue
                st, s = pm._get(f"/football/matches/{f['id']}/stats", key)
                time.sleep(2.2)
                if st != 200 or not s:
                    json.dump({"ok": False}, open(rs, "w"))
                    continue
                co, ye, re_ = _par(s, "corner_kicks"), _par(s, "yellow_cards"), _par(s, "red_cards")
                json.dump({"ok": True, "corners": co, "amarillas": ye, "rojas": re_}, open(rs, "w"))
        if i % 10 == 0:
            print(f"  {i}/{len(equipos)} equipos", flush=True)
    print("LISTO fetch", flush=True)


def _filas_equipo(est, tid):
    ruta = os.path.join(est, f"lista_{tid}.json")
    if not os.path.exists(ruta):
        return []
    out = []
    for f in json.load(open(ruta)):
        local = f["h"] == tid
        gf, gc = (f["gh"], f["ga"]) if local else (f["ga"], f["gh"])
        fila = {"id": f["id"], "local": local, "gf": gf, "gc": gc, "total": gf + gc}
        rs = os.path.join(est, f"stats_{f['id']}.json")
        if os.path.exists(rs):
            s = json.load(open(rs))
            if s.get("ok") and s.get("corners"):
                ch, ca = s["corners"]
                fila["cf"], fila["cc"] = (ch, ca) if local else (ca, ch)
                fila["ct"] = ch + ca
            if s.get("ok") and s.get("amarillas") and s.get("rojas"):
                ph = s["amarillas"][0] + 2 * s["rojas"][0]
                pa = s["amarillas"][1] + 2 * s["rojas"][1]
                fila["kt"] = ph + pa
        out.append(fila)
    return out


def _freq(filas, f, clave=None):
    sel = [x for x in filas if (clave is None or clave in x)]
    if not sel:
        return None, 0
    return sum(1 for x in sel if f(x)) / len(sel), len(sel)


def _mix(filas, f, clave=None, local=None):
    """Frecuencia general; si hay >= 3 partidos del mismo lado se promedia con la del lado."""
    g, n = _freq(filas, f, clave)
    if g is None:
        return None, 0
    if local is not None:
        lado = [x for x in filas if x["local"] == local]
        v, nv = _freq(lado, f, clave)
        if v is not None and nv >= 3:
            return (g + v) / 2, n
    return g, n


def _p2(fa, na, fb, nb):
    if fa is None or fb is None or min(na, nb) < MIN_N:
        return None
    return (fa + fb) / 2


def patas_deportivas(m, est):
    h, a = m["home_team"], m["away_team"]
    H, A = _filas_equipo(est, h["id"]), _filas_equipo(est, a["id"])
    if len(H) < MIN_N or len(A) < MIN_N:
        return []
    nm = {"H": h["name"], "A": a["name"]}
    patas = []

    def add(mercado, sel, p, nh, na, nota=""):
        if p is None:
            return
        patas.append({"match_id": m["id"], "partido": f"{h['name']} – {a['name']}", "hora_caracas": hora_caracas(m["utc_date"]).strftime("%d-%m %H:%M"),
                      "mercado": mercado, "seleccion": sel, "p_dep": round(p, 4), "n_local": nh, "n_visita": na, "nota": nota})

    # Totales de goles del partido
    for L in LINEAS_GOLES:
        fa, na_ = _freq(H, lambda x: x["total"] > L)
        fb, nb_ = _freq(A, lambda x: x["total"] > L)
        p = _p2(fa, na_, fb, nb_)
        if p is not None:
            add("goles", f"Más de {L} goles", p, na_, nb_)
            add("goles", f"Menos de {L} goles", 1 - p, na_, nb_)
    # Ambos anotan
    fa, na_ = _freq(H, lambda x: x["gf"] > 0 and x["gc"] > 0)
    fb, nb_ = _freq(A, lambda x: x["gf"] > 0 and x["gc"] > 0)
    p = _p2(fa, na_, fb, nb_)
    if p is not None:
        add("btts", "Ambos anotan: sí", p, na_, nb_)
        add("btts", "Ambos anotan: no", 1 - p, na_, nb_)
    # Goles por equipo: el equipo marca vs. el rival concede
    for lado, T, O, tn, on in (("H", H, A, h["name"], a["name"]), ("A", A, H, a["name"], h["name"])):
        loc = lado == "H"
        for L in LINEAS_GOLES_EQ:
            f1, n1 = _mix(T, lambda x: x["gf"] > L, None, loc)
            f2, n2 = _mix(O, lambda x: x["gc"] > L, None, not loc)
            p = _p2(f1, n1, f2, n2)
            if p is not None:
                add("goles_equipo", f"{tn}: Más de {L} goles", p, n1, n2)
                add("goles_equipo", f"{tn}: Menos de {L} goles", 1 - p, n1, n2)
    # Doble oportunidad y 1X2 (promedio general/lado)
    nl_h, nh_ = _mix(H, lambda x: x["gf"] >= x["gc"], None, True)
    nw_a, na2 = _mix(A, lambda x: x["gf"] <= x["gc"], None, False)
    p1x = _p2(nl_h, nh_, nw_a, na2)
    nl_a, nb2 = _mix(A, lambda x: x["gf"] >= x["gc"], None, False)
    nw_h, nh2 = _mix(H, lambda x: x["gf"] <= x["gc"], None, True)
    px2 = _p2(nl_a, nb2, nw_h, nh2)
    if p1x is not None:
        add("dc", f"{h['name']} o empate", p1x, nh_, na2)
    if px2 is not None:
        add("dc", f"{a['name']} o empate", px2, nb2, nh2)
    wh, n1 = _mix(H, lambda x: x["gf"] > x["gc"], None, True)
    la, n2 = _mix(A, lambda x: x["gf"] < x["gc"], None, False)
    p = _p2(wh, n1, la, n2)
    if p is not None:
        add("1x2", f"Gana {h['name']}", p, n1, n2)
    wa, n3 = _mix(A, lambda x: x["gf"] > x["gc"], None, False)
    lh, n4 = _mix(H, lambda x: x["gf"] < x["gc"], None, True)
    p = _p2(wa, n3, lh, n4)
    if p is not None:
        add("1x2", f"Gana {a['name']}", p, n3, n4)
    # Córners del partido y por equipo
    for L in LINEAS_CORNERS:
        fa, na_ = _freq(H, lambda x: x["ct"] > L, "ct")
        fb, nb_ = _freq(A, lambda x: x["ct"] > L, "ct")
        p = _p2(fa, na_, fb, nb_)
        if p is not None:
            add("corners", f"Más de {L} córners", p, na_, nb_)
            add("corners", f"Menos de {L} córners", 1 - p, na_, nb_)
    for lado, T, O, tn in (("H", H, A, h["name"]), ("A", A, H, a["name"])):
        loc = lado == "H"
        for L in LINEAS_CORNERS_EQ:
            f1, n1 = _mix(T, lambda x: x["cf"] > L, "cf", loc)
            f2, n2 = _mix(O, lambda x: x["cc"] > L, "cc", not loc)
            p = _p2(f1, n1, f2, n2)
            if p is not None:
                add("corners_equipo", f"{tn}: Más de {L} córners", p, n1, n2)
                add("corners_equipo", f"{tn}: Menos de {L} córners", 1 - p, n1, n2)
    # Tarjetas (puntos de la casa aproximados)
    for L in LINEAS_TARJETAS:
        fa, na_ = _freq(H, lambda x: x["kt"] > L, "kt")
        fb, nb_ = _freq(A, lambda x: x["kt"] > L, "kt")
        p = _p2(fa, na_, fb, nb_)
        if p is not None:
            add("tarjetas", f"Más de {L} tarjetas", p, na_, nb_, "puntos = amarillas + 2×rojas (aprox.)")
            add("tarjetas", f"Menos de {L} tarjetas", 1 - p, na_, nb_, "puntos = amarillas + 2×rojas (aprox.)")
    return patas


def cmd_analisis(a):
    est = os.path.join(a.run, "est")
    U = universo(a.run, a.desde, a.dia)
    todas = []
    for m in U:
        todas += patas_deportivas(m, est)
    json.dump({"patas": todas, "partidos": len(U), "min_n": MIN_N, "nota": "p_dep = promedio de las frecuencias históricas de los dos equipos; el mercado NO interviene"},
              open(os.path.join(a.run, "pool", "est_patas.json"), "w"), ensure_ascii=False, indent=0)
    con = {p["match_id"] for p in todas}
    print(f"{len(todas)} patas deportivas en {len(con)} de {len(U)} partidos (muestra mínima {MIN_N})")


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    for n in ("fetch", "analisis"):
        s = sub.add_parser(n)
        s.add_argument("--run", required=True)
        s.add_argument("--desde", default="14:00")
        s.add_argument("--dia", default="2026-11-02")
        if n == "fetch":
            s.add_argument("--n", type=int, default=8)
            s.add_argument("--sin-stats", action="store_true")
            s.add_argument("--orden", choices=["adelante", "atras", "azar"], default="adelante", help="para correr varios procesos en paralelo sin repetir")
    a = ap.parse_args(argv)
    return {"fetch": cmd_fetch, "analisis": cmd_analisis}[a.cmd](a) or 0


if __name__ == "__main__":
    sys.exit(main())
