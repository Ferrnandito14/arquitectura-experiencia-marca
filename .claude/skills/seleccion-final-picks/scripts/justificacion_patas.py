#!/usr/bin/env python3
"""Justificación de cada pata finalista con datos de TheStatsAPI y de nuestro registro, por reglas fijas (sin agente).

Por pata: posición en la tabla de su liga, forma de los últimos 8 por lado (orientada en el dossier), enfrentamientos
directos (últimos 100 partidos del local), contexto (descanso, próximo partido, bajas activas) y cuánto acertaron en
NUESTRO registro (data/ledger_patas.jsonl) las patas del mismo tipo y cuota. Cada dato lleva su marca: a favor (+),
en contra (−) o neutro (·), según umbrales fijos y declarados. La lectura final cuenta marcas; no es una probabilidad.

Uso:  justificacion_patas.py --run runs/2026-11-01 [--ledger data/ledger_patas.jsonl]
Salida: <run>/pool/justificaciones.json  (clave = match_id|seleccion)."""
import argparse
import json
import os
import re
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pool_mercado as pm  # noqa: E402

SIN_PERDER_ALTO, SIN_PERDER_BAJO = 0.75, 0.5
EMPATE_BAJO, EMPATE_ALTO = 0.15, 0.30
OVER_ALTO, OVER_BAJO = 0.55, 0.40


def clasificar(seleccion, local, visita):
    """(tipo, detalle): dc_local, dc_visita, sin_empate, over/under con línea, btts."""
    s = seleccion.strip()
    m = re.match(r"(Más|Menos) de ([\d.]+) goles", s)
    if m:
        return ("over" if m.group(1) == "Más" else "under"), float(m.group(2))
    if "(sin empate)" in s:
        return "sin_empate", None
    if s.endswith(" o empate"):
        eq = s[: -len(" o empate")]
        return ("dc_local", None) if eq.strip() == local.strip() else ("dc_visita", None)
    if s.startswith("Ambos anotan"):
        return ("btts_si" if "sí" in s else "btts_no"), None
    return "otro", None


def marca(valor, alto, bajo, invertido=False):
    if valor is None:
        return "·"
    if valor >= alto:
        return "−" if invertido else "+"
    if valor <= bajo:
        return "+" if invertido else "−"
    return "·"


def linea(m, texto):
    return {"m": m, "t": texto}


def pos_txt(t):
    return f"{t['team']['name']} {t['position']}.º ({t['points']} pts en {t['matches_played']} PJ, GD {t['goal_difference']:+d})"


def evaluar(tipo, det, fila, tabla, h2h):
    """Líneas marcadas a favor/en contra para una pata. `fila` = dossier (local, visitante, competition…), `tabla` = {team_id: fila de standings}."""
    L, V = fila["local"], fila["visitante"]
    rl, rv = L["resumen"], V["resumen"]
    out = []
    tl, tv = tabla.get(L["team_id"]), tabla.get(V["team_id"])
    if tl and tv:
        out.append(linea("·", f"Tabla: {pos_txt(tl)} vs {pos_txt(tv)}"))
    def forma(nombre, r, lado):
        pl = r["por_lado"][lado]
        return f"{nombre}: {r['G']}G-{r['E']}E-{r['P']}P en 8 · como {lado}: {pl['G']}G-{pl['E']}E-{pl['P']}P en {pl['n']} · goles {r['gf_medio']} a favor y {r['gc_medio']} en contra"
    if tipo in ("dc_local", "dc_visita"):
        T, R, lado, rival = (L, V, "local", "visita") if tipo == "dc_local" else (V, L, "visita", "local")
        r, ro = T["resumen"], R["resumen"]
        out.append(linea(marca(r["sin_perder"], SIN_PERDER_ALTO, SIN_PERDER_BAJO), f"{T['equipo']} no perdió {round(r['sin_perder'] * r['n'])} de {r['n']} últimos partidos ({forma(T['equipo'], r, lado)})"))
        pl = r["por_lado"][lado]
        out.append(linea("+" if pl["n"] >= 3 and pl["P"] <= 1 else ("−" if pl["P"] >= 2 else "·"), f"{T['equipo']} como {lado}: {pl['P']} derrota{'' if pl['P'] == 1 else 's'} en {pl['n']}"))
        pr = ro["por_lado"][rival]
        gana = pr["G"] / pr["n"] if pr["n"] else None
        out.append(linea(marca(gana, 0.6, 0.4, invertido=True), f"{R['equipo']} como {rival}: {pr['G']}G-{pr['E']}E-{pr['P']}P en {pr['n']} (rival que tendría que ganar)"))
        if tl and tv:
            mi, su = (tl, tv) if tipo == "dc_local" else (tv, tl)
            d = su["position"] - mi["position"]
            out.append(linea("+" if d >= 3 else ("−" if d <= -3 else "·"), f"Diferencia en la tabla a favor de {T['equipo']}: {d:+d} puestos"))
        if h2h and h2h["n"] >= 2:
            sp = h2h["sin_perder_local"] if tipo == "dc_local" else h2h["sin_perder_visita"]
            out.append(linea(marca(sp, SIN_PERDER_ALTO, SIN_PERDER_BAJO), f"Enfrentamientos directos ({h2h['n']}): {T['equipo']} no perdió en {round(sp * h2h['n'])}"))
        baj = T["bajas"]["lesiones_activas"] + T["bajas"]["sanciones_activas"]
        out.append(linea("−" if baj >= 4 else "·", f"{T['equipo']} tiene {T['bajas']['lesiones_activas']} lesionados y {T['bajas']['sanciones_activas']} sancionados activos (sin nombres: no se mide el impacto)"))
    elif tipo == "sin_empate":
        for X in (L, V):
            r = X["resumen"]
            out.append(linea(marca(r["E"] / r["n"], EMPATE_ALTO, EMPATE_BAJO, invertido=True), f"{X['equipo']} empató {r['E']} de {r['n']} últimos partidos"))
        if h2h and h2h["n"] >= 2:
            out.append(linea(marca(h2h["empates"] / h2h["n"], EMPATE_ALTO, EMPATE_BAJO, invertido=True), f"Enfrentamientos directos ({h2h['n']}): {h2h['empates']} empates"))
        out.append(linea("·", forma(L["equipo"], rl, "local")))
        out.append(linea("·", forma(V["equipo"], rv, "visita")))
    elif tipo in ("over", "under"):
        lin = det
        def tasa(X):
            return sum(1 for p in X["ultimos"] if p["total_goles"] > lin) / max(1, len(X["ultimos"]))
        tl_, tv_ = tasa(L), tasa(V)
        media = (rl["gf_medio"] + rl["gc_medio"] + rv["gf_medio"] + rv["gc_medio"]) / 2
        inv = tipo == "under"
        for X, t in ((L, tl_), (V, tv_)):
            out.append(linea(marca(t, OVER_ALTO, OVER_BAJO, invertido=inv), f"{X['equipo']}: {round(t * len(X['ultimos']))} de {len(X['ultimos'])} partidos con más de {lin} goles"))
        out.append(linea("+" if (media > lin if not inv else media < lin) else "−", f"Goles totales medios de sus partidos: {media:.2f} (línea {lin})"))
        if h2h and h2h["n"] >= 2:
            sup = h2h["goles_medios"] > lin if not inv else h2h["goles_medios"] < lin
            out.append(linea("+" if sup else "−", f"Enfrentamientos directos ({h2h['n']}): {h2h['goles_medios']:.2f} goles de media"))
    return out


def contexto_lineas(fila, fecha_partido):
    """Descanso y próximo partido de cada equipo (riesgo de rotación): marca − si descansó menos de 4 días o juega de nuevo en 4 días o menos."""
    from datetime import date
    d0 = date.fromisoformat(fecha_partido[:10])
    out = []
    for rol in ("local", "visitante"):
        X = fila[rol]
        partes = []
        marca_ = "·"
        if X.get("ultimos"):
            dias = (d0 - date.fromisoformat(X["ultimos"][0]["fecha"])).days
            partes.append(f"descansó {dias} días desde su último partido")
            if dias < 4:
                marca_ = "−"
        sig = (X.get("proximos") or [])[1:2]
        if sig:
            dd = (date.fromisoformat(sig[0]["utc"][:10]) - d0).days
            partes.append(f"después juega vs {sig[0]['rival']} en {dd} días")
            if dd <= 4:
                marca_ = "−"
        if partes:
            out.append(linea(marca_, f"{X['equipo']}: " + "; ".join(partes)))
    return out


def lectura(lineas):
    a, c = sum(1 for x in lineas if x["m"] == "+"), sum(1 for x in lineas if x["m"] == "−")
    if a + c == 0:
        return "El dossier no aporta señales claras para esta pata."
    s = lambda n: f"{n} señal" + ("" if n == 1 else "es")
    if a >= c + 2:
        return f"El dossier respalda la pata: {s(a)} a favor y {c} en contra."
    if c >= a + 2:
        return f"El dossier la debilita: {s(c)} en contra y {a} a favor."
    return f"El dossier está dividido: {s(a)} a favor y {c} en contra."


def h2h_de(partidos_local, local_id, rival_id):
    """Resumen de los enfrentamientos terminados entre ambos, visto desde el equipo local actual."""
    n, gl, el, gv, empates, goles = 0, 0, 0, 0, 0, 0
    rows = []
    for x in partidos_local:
        if x["status"] != "finished" or rival_id not in (x["home_team"]["id"], x["away_team"]["id"]):
            continue
        sc = x["score"]
        if sc.get("home") is None:
            continue
        mi, su = (sc["home"], sc["away"]) if x["home_team"]["id"] == local_id else (sc["away"], sc["home"])
        n += 1; goles += mi + su
        gl += mi > su; gv += mi < su; empates += mi == su
        rows.append(f"{x['utc_date'][:10]} {x['home_team']['name']} {sc['home']}-{sc['away']} {x['away_team']['name']}")
    if not n:
        return {"n": 0}
    return {"n": n, "G_local": gl, "E": empates, "G_visita": gv, "empates": empates, "goles_medios": round(goles / n, 2),
            "sin_perder_local": (gl + empates) / n, "sin_perder_visita": (gv + empates) / n, "partidos": rows[:5]}


def registro(ledger, seleccion, tipo, det, cuota, local):
    """Aciertos históricos de patas del mismo tipo y cuota (±10 %) en nuestro registro."""
    if tipo == "dc_local":
        ids = ["resultado.dc.1x"]
    elif tipo == "dc_visita":
        ids = ["resultado.dc.x2"]
    elif tipo == "sin_empate":
        ids = ["resultado.dc.12"]
    elif tipo in ("over", "under"):
        ids = [f"goles.total.{tipo}.{det}"]
    else:
        return None
    lo, hi = max(1.01, cuota * 0.9), cuota * 1.1
    def sel(ids_):
        r = [x for x in ledger if x.get("entry_id") in ids_ and x.get("res") in ("GANADA", "PERDIDA") and x.get("cuota") and lo <= x["cuota"] <= hi]
        return r
    r = sel(ids)
    amplio = False
    if len(r) < 30 and tipo in ("over", "under"):
        fam = {x["entry_id"] for x in ledger if x.get("entry_id", "").startswith(f"goles.total.{tipo}.")}
        r = sel(fam); amplio = True
    if not r:
        return {"n": 0, "etiqueta": ids[0]}
    ganadas = sum(1 for x in r if x["res"] == "GANADA")
    imp = sum(1 / x["cuota"] for x in r) / len(r)
    return {"n": len(r), "acierto": round(100 * ganadas / len(r), 1), "implicita": round(100 * imp, 1), "banda": [round(lo, 2), round(hi, 2)],
            "familia_amplia": amplio, "etiqueta": ids[0] if not amplio else f"goles.total.{tipo}.*",
            "dias": len({x.get("dia") for x in r})}


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--run", required=True)
    ap.add_argument("--ledger", default="data/ledger_patas.jsonl")
    a = ap.parse_args(argv)
    key = pm._key()
    fin = json.load(open(os.path.join(a.run, "pool", "finalistas.json")))["patas"]
    doss = {p["key"]: p for p in json.load(open(os.path.join(a.run, "dossier", "dossier_finalistas.json")))["patas"]}
    matches = {m["id"]: m for m in json.load(open(os.path.join(a.run, "thestatsapi", "matches.json")))}
    ledger = [json.loads(l) for l in open(a.ledger, encoding="utf-8")]
    cache_t, cache_h = {}, {}
    out = {}
    for p in fin:
        k = p["match_id"] + "|" + p["seleccion"]
        m = matches[p["match_id"]]
        f = doss[k]
        sk = (m["competition_id"], m["season_id"])
        if sk not in cache_t:
            st, body = pm._get(f"/football/competitions/{sk[0]}/seasons/{sk[1]}/standings", key)
            time.sleep(2.0)
            cache_t[sk] = {x["team"]["id"]: x for x in (body or {}).get("data", [])} if body else {}
        if p["match_id"] not in cache_h:
            st, body = pm._get(f"/football/matches?team_id={m['home_team']['id']}&status=finished&per_page=100&sort=-utc_date", key)
            time.sleep(2.0)
            cache_h[p["match_id"]] = h2h_de((body or {}).get("data", []), m["home_team"]["id"], m["away_team"]["id"])
        local, visita = m["home_team"]["name"], m["away_team"]["name"]
        tipo, det = clasificar(p["seleccion"], local, visita)
        lineas = evaluar(tipo, det, f, cache_t[sk], cache_h[p["match_id"]]) if tipo != "otro" else []
        lineas += contexto_lineas(f, m["utc_date"])
        out[k] = {"tipo": tipo, "tabla_ok": bool(cache_t[sk]), "h2h": cache_h[p["match_id"]], "lineas": lineas, "lectura": lectura(lineas),
                  "registro": registro(ledger, p["seleccion"], tipo, det, p["cuota"], local)}
    json.dump(out, open(os.path.join(a.run, "pool", "justificaciones.json"), "w"), ensure_ascii=False, indent=1)
    print(len(out), "justificaciones")
    return 0


if __name__ == "__main__":
    sys.exit(main())
