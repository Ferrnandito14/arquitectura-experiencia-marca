#!/usr/bin/env python3
"""Memoria persistente e incremental de equipos (partidos terminados de TheStatsAPI).

Almacén: data/memoria_equipos/partidos.jsonl  (una línea por partido terminado, sin duplicados por id).
Solo guarda lo necesario: ids, nombres, fecha UTC, marcador a 90' (regulation) y marcador final. Nunca la clave.

Comandos:
  importar  --desde-listado ARCHIVO.json       Carga un listado ya descargado (sin consultas a la API).
  actualizar [--hasta AAAA-MM-DD] [--key-file R] Pide SOLO partidos posteriores al último guardado (menos 2 días de solape).
  resumen   --equipo NOMBRE [--n 8]            Últimos n partidos y frecuencias (más de 1.5/2.5/3.5, ambos anotan, victoria).
  importar-est [--runs-dir runs]                 Recoge córners/tarjetas ya descargados en runs/*/est/stats_*.json (sin consultas).
  completar-stats --max N [--key-file R]         Pide /stats de los N partidos más recientes aún sin córners/tarjetas (tanda gradual).
  info                                          Cantidad de partidos, equipos y rango de fechas.
La clave se lee de THESTATSAPI_KEY / THESTATSAPI_KEY_FILE / --key-file (vía tsa_fetch.api_key)."""
import argparse
import json
import os
import sys
import unicodedata
from datetime import datetime, timedelta, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
STORE = os.path.join(ROOT, "data", "memoria_equipos", "partidos.jsonl")
STATS = os.path.join(ROOT, "data", "memoria_equipos", "stats.jsonl")
SOLAPE_DIAS = 2


def _norm(s):
    s = unicodedata.normalize("NFKD", s or "").encode("ascii", "ignore").decode().lower()
    return " ".join(s.split())


def compactar(m):
    """Fila mínima de un partido terminado, o None si no sirve (sin marcador a 90')."""
    if m.get("status") != "finished":
        return None
    sc = m.get("score") or {}
    reg = sc.get("regulation") or {}
    if reg.get("home") is None or reg.get("away") is None:
        return None
    return {"id": m["id"], "utc": m["utc_date"][:16], "h_id": m["home_team"]["id"], "h": m["home_team"]["name"],
            "a_id": m["away_team"]["id"], "a": m["away_team"]["name"], "gh": reg["home"], "ga": reg["away"],
            "extra": bool(sc.get("went_to_extra_time")), "pen": bool(sc.get("went_to_penalties"))}


def cargar(store=STORE):
    d = {}
    if os.path.exists(store):
        with open(store, encoding="utf-8") as f:
            for ln in f:
                if ln.strip():
                    r = json.loads(ln)
                    d[r["id"]] = r
    return d


def guardar(d, store=STORE):
    os.makedirs(os.path.dirname(store), exist_ok=True)
    tmp = store + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        for r in sorted(d.values(), key=lambda r: (r["utc"], r["id"])):
            f.write(json.dumps(r, ensure_ascii=False, separators=(",", ":")) + "\n")
    os.replace(tmp, store)


def fusionar(d, partidos):
    """Añade/actualiza partidos terminados. Devuelve (nuevos, corregidos)."""
    nuevos = corr = 0
    for m in partidos:
        r = compactar(m)
        if not r:
            continue
        if r["id"] not in d:
            nuevos += 1
        elif d[r["id"]] != r:
            corr += 1
        d[r["id"]] = r
    return nuevos, corr


def ultimo(d):
    return max((r["utc"] for r in d.values()), default=None)


def rango_nuevo(d, hasta):
    u = ultimo(d)
    if not u:
        raise SystemExit("memoria vacía: primero 'importar --desde-listado' o indica --desde")
    desde = (datetime.fromisoformat(u[:10]) - timedelta(days=SOLAPE_DIAS)).date().isoformat()
    return desde, hasta


def partidos_equipo(d, equipo, n=8, antes=None):
    q = _norm(equipo)
    xs = [r for r in d.values() if q in (_norm(r["h"]), _norm(r["a"])) and (antes is None or r["utc"] < antes)]
    xs.sort(key=lambda r: r["utc"], reverse=True)
    return xs[:n]


def partidos_por_id(d, team_id, n=8):
    xs = [r for r in d.values() if team_id in (r["h_id"], r["a_id"])]
    xs.sort(key=lambda r: r["utc"], reverse=True)
    return xs[:n]


def cargar_stats(path=STATS):
    """{match_id: {"ok", "corners":[h,a]|None, "amarillas":[h,a]|None, "rojas":[h,a]|None}}. Último registro gana."""
    d = {}
    if os.path.exists(path):
        with open(path, encoding="utf-8") as f:
            for ln in f:
                if ln.strip():
                    r = json.loads(ln)
                    d[r.pop("id")] = r
    return d


def anotar_stats(match_id, reg, path=STATS):
    """Añade UNA línea (append atómico: seguro con procesos en paralelo)."""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    linea = json.dumps({"id": match_id, **reg}, ensure_ascii=False, separators=(",", ":")) + "\n"
    fd = os.open(path, os.O_WRONLY | os.O_APPEND | os.O_CREAT, 0o644)
    try:
        os.write(fd, linea.encode("utf-8"))
    finally:
        os.close(fd)


def resumen(d, equipo, n=8, antes=None, team_id=None):
    """Con team_id (recomendado) no se mezclan equipos de igual nombre (p. ej. masculino y femenino)."""
    xs = partidos_por_id(d, team_id, n) if team_id else partidos_equipo(d, equipo, n, antes)
    q = _norm(equipo)
    filas, k = [], {"o15": 0, "o25": 0, "o35": 0, "btts": 0, "gana": 0, "empata": 0}
    for r in xs:
        local = (r["h_id"] == team_id) if team_id else (_norm(r["h"]) == q)
        gf, gc = (r["gh"], r["ga"]) if local else (r["ga"], r["gh"])
        t = r["gh"] + r["ga"]
        k["o15"] += t >= 2; k["o25"] += t >= 3; k["o35"] += t >= 4
        k["btts"] += r["gh"] > 0 and r["ga"] > 0
        k["gana"] += gf > gc; k["empata"] += gf == gc
        filas.append({"fecha": r["utc"], "rival": r["a"] if local else r["h"], "local": local, "marcador": f"{gf}-{gc}"})
    return {"equipo": equipo, "n": len(xs), "frecuencias": k, "partidos": filas}


def _fetcher(key_file):
    sys.path.insert(0, HERE)
    import tsa_fetch
    key = tsa_fetch.api_key(key_file)
    if not key:
        raise SystemExit("error: sin clave (THESTATSAPI_KEY / THESTATSAPI_KEY_FILE / --key-file)")
    return tsa_fetch.Fetcher(key)


def listar(fetcher, desde, hasta):
    rows, page = [], 1
    while True:
        code, body = fetcher.get(f"/football/matches?date_from={desde}&date_to={hasta}&per_page=100&sort=utc_date&page={page}")
        if code in (401, 403):
            raise SystemExit(f"TheStatsAPI rechazó la clave ({code})")
        if code != 200:
            raise SystemExit(f"error {code} al listar (página {page})")
        d = json.loads(body)
        rows += d["data"]
        if page >= (d.get("meta") or {}).get("total_pages", 1):
            return rows
        page += 1


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("cmd", choices=["importar", "actualizar", "resumen", "info", "importar-est", "completar-stats"])
    ap.add_argument("--desde-listado")
    ap.add_argument("--hasta")
    ap.add_argument("--key-file")
    ap.add_argument("--equipo")
    ap.add_argument("--team-id")
    ap.add_argument("--n", type=int, default=8)
    ap.add_argument("--store", default=STORE)
    ap.add_argument("--stats", default=STATS)
    ap.add_argument("--runs-dir", default=os.path.join(ROOT, "runs"))
    ap.add_argument("--max", type=int, default=100)
    a = ap.parse_args(argv)
    d = cargar(a.store)
    if a.cmd == "importar":
        if not a.desde_listado:
            raise SystemExit("falta --desde-listado")
        data = json.load(open(a.desde_listado, encoding="utf-8"))
        n, c = fusionar(d, data.get("data", data) if isinstance(data, dict) else data)
        guardar(d, a.store)
        print(f"importados {n} nuevos, {c} corregidos; total {len(d)}")
    elif a.cmd == "actualizar":
        hasta = a.hasta or datetime.now(timezone.utc).date().isoformat()
        desde, hasta = rango_nuevo(d, hasta)
        rows = listar(_fetcher(a.key_file), desde, hasta)
        n, c = fusionar(d, rows)
        guardar(d, a.store)
        print(f"consultado {desde}..{hasta}: {len(rows)} partidos, {n} nuevos, {c} corregidos; total {len(d)}")
    elif a.cmd == "importar-est":
        import glob
        st, nuevos = cargar_stats(a.stats), 0
        for fn in sorted(glob.glob(os.path.join(a.runs_dir, "*", "est", "stats_*.json"))):
            mid = os.path.basename(fn)[6:-5]
            reg = json.load(open(fn))
            if mid not in st or (reg.get("ok") and not st[mid].get("ok")):
                anotar_stats(mid, reg, a.stats)
                st[mid] = reg
                nuevos += 1
        print(f"importados {nuevos} registros de stats; total {len(st)}")
    elif a.cmd == "completar-stats":
        import time
        sys.path.insert(0, HERE)
        import pool_mercado as pm
        key = pm._key()
        st, hechos = cargar_stats(a.stats), 0
        for r in sorted(d.values(), key=lambda r: r["utc"], reverse=True):
            if hechos >= a.max:
                break
            if r["id"] in st:
                continue
            code, s_ = pm._get(f"/football/matches/{r['id']}/stats", key)
            time.sleep(2.2)
            if code in (401, 403):
                raise SystemExit(f"TheStatsAPI rechazó la clave ({code})")
            reg = {"ok": False}
            if code == 200 and s_:
                import estadistica_primero as ep
                reg = {"ok": True, "corners": ep._par(s_, "corner_kicks"), "amarillas": ep._par(s_, "yellow_cards"), "rojas": ep._par(s_, "red_cards")}
            anotar_stats(r["id"], reg, a.stats)
            st[r["id"]] = reg
            hechos += 1
        print(f"consultados {hechos} partidos; con stats {sum(1 for v in st.values() if v.get('ok'))} de {len(d)}")
    elif a.cmd == "resumen":
        if not (a.equipo or a.team_id):
            raise SystemExit("falta --equipo o --team-id")
        print(json.dumps(resumen(d, a.equipo or a.team_id, a.n, team_id=a.team_id), ensure_ascii=False, indent=1))
    else:
        eq = {r["h_id"] for r in d.values()} | {r["a_id"] for r in d.values()}
        print(json.dumps({"partidos": len(d), "equipos": len(eq), "desde": min((r["utc"] for r in d.values()), default=None), "hasta": ultimo(d)}))


if __name__ == "__main__":
    main()
