#!/usr/bin/env python3
"""Pool de patas por MERCADO (TheStatsAPI, varias casas) y búsqueda de tickets ×1,20 / ×4.

No usa el modelo propio ni historial: la probabilidad de cada pata es el promedio de las P sin margen de cada casa
(par over/under, BTTS y 1X2 normalizados por casa) y el precio es la mediana de cuotas entre casas. Sirve cuando no hay
historial por equipo (apifootball recortada) y porque el modelo propio no le gana al mercado.

Subcomandos:
  fetch  --run RUN --day YYYY-MM-DD            descarga partidos del día (Caracas) y sus cuotas (caché, ritmo cortés)
  pool   --run RUN                             construye runs/<d>/pool/patas.json (+ banderas de sentido común)
  validar --run RUN                            ficha de cada equipo (is_mens_team); el pool excluye los no masculinos
  tickets --run RUN --objetivo x12|x4 [--top N]  busca combinaciones y escribe pool/tickets_<obj>.json
La clave sale de THESTATSAPI_KEY_FILE y nunca se imprime."""
import argparse
import itertools
import json
import math
import os
import re
import statistics
import sys
import time
import urllib.request
from datetime import datetime, timedelta, timezone

BASE = "https://api.thestatsapi.com/api"
UA = "football-picks-system/0.1"
MIN_CASAS = 3
PAR_MIN, PAR_MAX = 0.98, 1.25
EXCLUIR_EQUIPO = re.compile(r"\b(U-?1\d|U-?2\d|Sub-?\d+|Women|Femin|Feminino|Reserves?|Youth|Juvenil|\(W\)|\bII\b|B Team)\b", re.I)
CARACAS = timezone(timedelta(hours=-4))


def _key():
    ruta = os.environ.get("THESTATSAPI_KEY_FILE")
    if not ruta:
        raise SystemExit("falta THESTATSAPI_KEY_FILE")
    return open(ruta).read().strip()


def _get(path, key, tries=3):
    for i in range(tries):
        req = urllib.request.Request(BASE + path, headers={"Authorization": "Bearer " + key, "User-Agent": UA, "Accept": "application/json"})
        try:
            with urllib.request.urlopen(req, timeout=40) as r:
                return r.status, json.loads(r.read().decode())
        except urllib.error.HTTPError as e:
            if e.code == 429:
                time.sleep(int(e.headers.get("Retry-After", "10")))
                continue
            if e.code in (401, 403):
                raise SystemExit(f"TheStatsAPI {e.code}: plan o clave no válidos")
            return e.code, None
        except Exception:
            time.sleep(2 + 2 * i)
    return 0, None


def ventana(dia):
    d0 = datetime.strptime(dia, "%Y-%m-%d").replace(tzinfo=CARACAS)
    return d0.astimezone(timezone.utc), (d0 + timedelta(days=1)).astimezone(timezone.utc)


def cmd_fetch(a):
    key = _key()
    u0, u1 = ventana(a.day)
    d_from, d_to = u0.strftime("%Y-%m-%d"), u1.strftime("%Y-%m-%d")
    base = os.path.join(a.run, "thestatsapi")
    os.makedirs(os.path.join(base, "odds"), exist_ok=True)
    filas, page = [], 1
    while True:
        st, body = _get(f"/football/matches?date_from={d_from}&date_to={d_to}&per_page=100&sort=utc_date&page={page}", key)
        if not body or not body.get("data"):
            break
        filas += body["data"]
        if len(body["data"]) < 100:
            break
        page += 1
        time.sleep(2.3)
    sel = [r for r in filas if u0.strftime("%Y-%m-%dT%H:%M") <= r["utc_date"][:16] < u1.strftime("%Y-%m-%dT%H:%M")]
    json.dump(sel, open(os.path.join(base, "matches.json"), "w"), ensure_ascii=False)
    print(f"{len(sel)} partidos en la ventana; con cuotas: {sum(1 for r in sel if r.get('odds_available'))}", flush=True)
    n = 0
    k, tot = (int(x) for x in a.shard.split("/")) if getattr(a, "shard", None) else (0, 1)
    for idx, r in enumerate(sel):
        if idx % tot != k or not r.get("odds_available") or r["status"] != "scheduled":
            continue
        ruta = os.path.join(base, "odds", r["id"] + ".json")
        if os.path.exists(ruta):
            continue
        st, body = _get(f"/football/matches/{r['id']}/odds", key)
        if body:
            body["_consultado_utc"] = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
            json.dump(body, open(ruta, "w"), ensure_ascii=False)
        n += 1
        time.sleep(2.3)
    print(f"cuotas descargadas: {n}", flush=True)


def cmd_validar(a):
    """Ficha de cada equipo de los partidos del pool (is_mens_team, país, competición principal). Excluye femeninos: el listado de partidos NO trae el género."""
    key = _key()
    base = os.path.join(a.run, "thestatsapi")
    os.makedirs(os.path.join(base, "equipos"), exist_ok=True)
    matches = json.load(open(os.path.join(base, "matches.json")))
    k, tot = (int(x) for x in a.shard.split("/")) if a.shard else (0, 1)
    n = 0
    equipos = []
    for r in matches:
        if not os.path.exists(os.path.join(base, "odds", r["id"] + ".json")):
            continue
        for lado in ("home_team", "away_team"):
            if r[lado]["id"] not in equipos:
                equipos.append(r[lado]["id"])
    for i, tid in enumerate(equipos):
        if i % tot != k:
            continue
        ruta = os.path.join(base, "equipos", tid + ".json")
        if os.path.exists(ruta):
            continue
        st, body = _get(f"/football/teams/{tid}", key)
        if body:
            json.dump(body["data"], open(ruta, "w"), ensure_ascii=False)
        n += 1
        time.sleep(2.3)
    print(f"fichas descargadas: {n}", flush=True)


def equipos_no_masculinos(run):
    """match_id de partidos con algún equipo que NO es masculino (según la ficha del equipo) o sin ficha."""
    base = os.path.join(run, "thestatsapi")
    malos, sin_ficha = {}, set()
    for r in json.load(open(os.path.join(base, "matches.json"))):
        for lado in ("home_team", "away_team"):
            ruta = os.path.join(base, "equipos", r[lado]["id"] + ".json")
            if not os.path.exists(ruta):
                sin_ficha.add(r["id"])
                continue
            f = json.load(open(ruta))
            if f.get("is_mens_team") is not True:
                malos[r["id"]] = f"{f.get('name')} no es equipo masculino (is_mens_team={f.get('is_mens_team')})"
    return malos, sin_ficha


def _f(x):
    try:
        return float(x["last_seen"])
    except Exception:
        return None


def _nov2(a, b):
    pa, pb = 1 / a, 1 / b
    s = pa + pb
    return pa / s, s


def _nov3(a, b, c):
    p = [1 / a, 1 / b, 1 / c]
    s = sum(p)
    return [x / s for x in p], s


def patas_de_partido(match, odds):
    libros = odds["data"]["bookmakers"]
    acum = {}   # (mercado, seleccion) -> {"cuotas": [], "ps": [], "casas": set()}
    banderas = []

    def put(clave, casa, cuota, p):
        d = acum.setdefault(clave, {"cuotas": [], "ps": [], "casas": []})
        d["cuotas"].append(cuota); d["ps"].append(p); d["casas"].append(casa)

    for b in libros:
        casa, m = b["bookmaker"], b["markets"]
        mo = m.get("match_odds")
        p1 = {}
        if mo and all(_f(mo.get(k) or {}) for k in ("home", "draw", "away")):
            h, d, a = (_f(mo[k]) for k in ("home", "draw", "away"))
            ps, s = _nov3(h, d, a)
            if PAR_MIN <= s <= 1.30:
                p1 = dict(zip(("home", "draw", "away"), ps))
                for k, c, p in zip(("home", "draw", "away"), (h, d, a), ps):
                    put(("1x2", k), casa, c, p)
            else:
                banderas.append(f"{casa}: 1X2 suma implícitas {s:.2f}")
        dc = m.get("double_chance")
        if dc and p1:
            for k, ps_ in (("home_draw", p1["home"] + p1["draw"]), ("home_away", p1["home"] + p1["away"]), ("draw_away", p1["draw"] + p1["away"])):
                c = _f(dc.get(k) or {})
                if c:
                    put(("dc", k), casa, c, ps_)
        tg = m.get("total_goals") or {}
        for linea, v in tg.items():
            try:
                lf = float(linea)
            except ValueError:
                continue
            if abs(lf * 2 - round(lf * 2)) > 1e-9 or abs(lf - math.floor(lf) - 0.5) > 1e-9:
                continue   # solo líneas .5
            o, u = _f(v.get("over") or {}), _f(v.get("under") or {})
            if o and u:
                po, s = _nov2(o, u)
                if PAR_MIN <= s <= PAR_MAX:
                    put(("goles", f"over {linea}"), casa, o, po)
                    put(("goles", f"under {linea}"), casa, u, 1 - po)
                else:
                    banderas.append(f"{casa}: total {linea} suma implícitas {s:.2f}")
        bt = m.get("btts")
        if bt:
            y, n = _f(bt.get("yes") or {}), _f(bt.get("no") or {})
            if y and n:
                py, s = _nov2(y, n)
                if PAR_MIN <= s <= PAR_MAX:
                    put(("btts", "yes"), casa, y, py)
                    put(("btts", "no"), casa, n, 1 - py)
                else:
                    banderas.append(f"{casa}: BTTS suma implícitas {s:.2f}")
    local, visit = match["home_team"]["name"], match["away_team"]["name"]
    etiquetas = {("1x2", "home"): f"Gana {local}", ("1x2", "draw"): "Empate", ("1x2", "away"): f"Gana {visit}",
                 ("dc", "home_draw"): f"{local} o empate", ("dc", "home_away"): f"{local} o {visit} (sin empate)", ("dc", "draw_away"): f"{visit} o empate",
                 ("btts", "yes"): "Ambos anotan: sí", ("btts", "no"): "Ambos anotan: no"}
    patas = []
    for (mer, sel), d in acum.items():
        if len(set(d["casas"])) < MIN_CASAS:
            continue
        cuota = statistics.median(d["cuotas"])
        p = sum(d["ps"]) / len(d["ps"])
        if mer == "goles":
            lado, linea = sel.split()
            nom = f"{'Más' if lado == 'over' else 'Menos'} de {linea} goles"
        else:
            nom = etiquetas[(mer, sel)]
        patas.append({"match_id": match["id"], "partido": f"{local} – {visit}", "utc": match["utc_date"],
                      "hora_caracas": datetime.strptime(match["utc_date"][:16], "%Y-%m-%dT%H:%M").replace(tzinfo=timezone.utc).astimezone(CARACAS).strftime("%d-%m %H:%M"),
                      "mercado": mer, "seleccion": nom, "cuota": round(cuota, 3), "p": round(p, 4), "n_casas": len(set(d["casas"])),
                      "cuota_min": round(min(d["cuotas"]), 3), "cuota_max": round(max(d["cuotas"]), 3), "valor": round(p * cuota, 4)})
    return patas, banderas


def cmd_pool(a):
    base = os.path.join(a.run, "thestatsapi")
    matches = json.load(open(os.path.join(base, "matches.json")))
    todas, bands, usados = [], {}, 0
    ruta_ex = os.path.join(a.run, "pool", "excluidos.json")
    excluidos = {x["match_id"] for x in json.load(open(ruta_ex))} if os.path.exists(ruta_ex) else set()
    malos, sin_ficha = equipos_no_masculinos(a.run) if os.path.isdir(os.path.join(base, "equipos")) else ({}, set())
    for m in matches:
        if m["id"] in excluidos or m["id"] in malos:
            continue
        if os.path.isdir(os.path.join(base, "equipos")) and m["id"] in sin_ficha and not a.permitir_sin_ficha:
            continue
        ruta = os.path.join(base, "odds", m["id"] + ".json")
        if not os.path.exists(ruta) or m["status"] != "scheduled":
            continue
        nombres = m["home_team"]["name"] + " " + m["away_team"]["name"]
        if EXCLUIR_EQUIPO.search(nombres):
            continue
        patas, banderas = patas_de_partido(m, json.load(open(ruta)))
        if patas:
            usados += 1
        todas += patas
        if banderas:
            bands[m["id"]] = banderas
    os.makedirs(os.path.join(a.run, "pool"), exist_ok=True)
    json.dump({"patas": todas, "banderas": bands}, open(os.path.join(a.run, "pool", "patas.json"), "w"), ensure_ascii=False, indent=0)
    print(f"{len(todas)} patas en {usados} partidos; partidos con banderas de precio: {len(bands)}")


def es_over(p):
    return str(p.get("seleccion", "")).startswith("Más de")


def buscar(patas, lo, hi, prod_lo, prod_hi, nmin, nmax, top, max_overs=None):
    cand = [p for p in patas if lo <= p["cuota"] <= hi]
    cand.sort(key=lambda p: -p["valor"])
    cand = cand[:90]
    cand.sort(key=lambda p: p["cuota"])
    mejores = []

    def dfs(inicio, usados, prod, pj, elegidas):
        if len(elegidas) >= nmin and prod_lo <= prod <= prod_hi:
            mejores.append((pj, prod, list(elegidas)))
        if len(elegidas) == nmax:
            return
        for i in range(inicio, len(cand)):
            p = cand[i]
            if p["match_id"] in usados:
                continue
            if max_overs is not None and es_over(p) and sum(1 for x in elegidas if es_over(x)) >= max_overs:
                continue
            np_ = prod * p["cuota"]
            if np_ > prod_hi:
                break
            elegidas.append(p)
            dfs(i + 1, usados | {p["match_id"]}, np_, pj * p["p"], elegidas)
            elegidas.pop()
    dfs(0, frozenset(), 1.0, 1.0, [])
    mejores.sort(key=lambda t: -t[0])
    salida, vistos = [], set()
    for pj, prod, el in mejores:
        clave = frozenset((p["match_id"], p["seleccion"]) for p in el)
        if clave in vistos:
            continue
        vistos.add(clave)
        salida.append({"p_ganar": round(pj, 4), "cuota_base": round(prod, 3), "valor_esperado": round(pj * prod - 1, 4), "patas": el})
        if len(salida) >= top:
            break
    return salida


def diversificar(lista, max_comun, top, max_rep=None):
    """Elige tickets en orden de probabilidad sin repetir más de `max_comun` patas entre dos tickets ya elegidos,
    y (si max_rep) sin que una misma pata aparezca en más de `max_rep` tickets: evita que una sola pata hunda toda la cartera."""
    elegidos = []
    cuenta = {}
    for t in lista:
        claves = {(p["match_id"], p["seleccion"]) for p in t["patas"]}
        if max_rep is not None and any(cuenta.get(c, 0) >= max_rep for c in claves):
            continue
        if all(len(claves & {(p["match_id"], p["seleccion"]) for p in e["patas"]}) <= max_comun for e in elegidos):
            elegidos.append(t)
            for c in claves:
                cuenta[c] = cuenta.get(c, 0) + 1
        if len(elegidos) == top:
            break
    return elegidos


def cmd_tickets(a):
    patas = json.load(open(os.path.join(a.run, "pool", "patas.json")))["patas"]
    if a.permitidas:
        perm = set(json.load(open(a.permitidas)))
        patas = [p for p in patas if p["match_id"] + "|" + p["seleccion"] in perm]
    if a.objetivo == "x12":
        lo, hi = (a.prod_min or 1.18), (a.prod_max or 1.30)
        res = {"2 patas": buscar(patas, 1.04, 1.30, lo, hi, 2, 2, 200), "3 patas": buscar(patas, 1.04, 1.30, lo, hi, 3, 3, 200)}
    else:
        res = {f"{n} patas": buscar(patas, 1.20, 2.10, 3.9, 4.5, n, n, 200, max_overs=1) for n in (3, 4, 5)}
    if a.max_comun is not None:
        res = {k: diversificar(v, a.max_comun, a.top, max_rep=2) for k, v in res.items()}
    json.dump(res, open(os.path.join(a.run, "pool", f"tickets_{a.objetivo}{a.sufijo}.json"), "w"), ensure_ascii=False, indent=1)
    for k, v in res.items():
        print(k, len(v), (f"mejor P={v[0]['p_ganar']:.3f} cuota {v[0]['cuota_base']}" if v else ""))


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    f = sub.add_parser("fetch"); f.add_argument("--run", required=True); f.add_argument("--day", required=True); f.add_argument("--shard", help="k/N: reparte los partidos entre N procesos")
    p = sub.add_parser("pool"); p.add_argument("--run", required=True); p.add_argument("--permitir-sin-ficha", action="store_true")
    v = sub.add_parser("validar"); v.add_argument("--run", required=True); v.add_argument("--shard")
    t = sub.add_parser("tickets"); t.add_argument("--run", required=True); t.add_argument("--objetivo", choices=("x12", "x4"), required=True); t.add_argument("--top", type=int, default=10); t.add_argument("--permitidas", help="JSON con lista de claves match_id|seleccion permitidas"); t.add_argument("--max-comun", type=int, help="máximo de patas en común entre tickets elegidos"); t.add_argument("--sufijo", default=""); t.add_argument("--prod-min", type=float, help="producto mínimo de cuotas (solo x12)"); t.add_argument("--prod-max", type=float, help="producto máximo de cuotas (solo x12)")
    a = ap.parse_args(argv)
    return {"fetch": cmd_fetch, "pool": cmd_pool, "tickets": cmd_tickets, "validar": cmd_validar}[a.cmd](a) or 0


if __name__ == "__main__":
    sys.exit(main())
