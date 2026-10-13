#!/usr/bin/env python3
"""Inventario maestro de partidos de una jornada LOCAL (por defecto America/Caracas).

Uso:  inventory.py --date 2026-10-13 [--tz America/Caracas] [--run-dir runs] [--manual calendario.csv|json]
Genera runs/<fecha>/inventory.json y sources/ (registro bruto + consultas). Estados INDEPENDIENTES:
  calendario  CONFIRMADO | NO_CONFIRMADO | DUPLICADO | FECHA_DISCREPANTE | INFORMACION_INSUFICIENTE
  encuentro   PROGRAMADO | EN_JUEGO | FINALIZADO | APLAZADO | CANCELADO | DESCONOCIDO
  elegibilidad ELEGIBLE | NO_ELEGIBLE | PENDIENTE_DE_VERIFICAR
  análisis    PENDIENTE | EN_CURSO | COMPLETADO | NO_EVALUABLE_TRAS_INTENTOS
Sólo consulta fuentes permitidas por sources_policy.json (ver common.py). Nada se elimina del inventario.
"""
import argparse
import hashlib
import os
import re
import sys
from datetime import datetime, timedelta, timezone

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import adapters  # noqa: E402
import common  # noqa: E402

TOL_DISCREPANCY_MIN = 15      # diferencia de hora entre fuentes que ya es discrepancia
CLUSTER_HOURS = 36            # ventana para considerar que dos registros pueden ser el mismo encuentro

_CAT = [("women", r"\b(women|woman|femin\w*|ladies|w)\b|\(w\)|\bfem\b"),
        ("youth", r"\bu-?(1[5-9]|2[0-3])\b|\b(youth|juvenil|junior\w*|academy)\b"),
        ("reserve", r"\b(reserves?|reserva\w*|ii|b team|u21 team)\b| b$")]


def detect_category(home, away, competition, hint=None):
    if hint:
        return hint
    text = " ".join([home or "", away or "", competition or ""]).lower()
    for cat, rx in _CAT:
        if re.search(rx, text):
            return cat
    return "men"


def _tokens(s):
    return {t for t in common.norm_name(s).split() if len(t) > 2}


def competitions_compatible(a, b):
    na, nb = common.norm_name(a), common.norm_name(b)
    if not na or not nb or na == nb or na in nb or nb in na:
        return True
    ta, tb = _tokens(a), _tokens(b)
    return bool(ta and tb and len(ta & tb) / len(ta | tb) >= 0.34)


def raw_to_utc(r):
    """datetime UTC del registro bruto o None."""
    if r.get("utc_epoch") is not None:
        return datetime.fromtimestamp(int(r["utc_epoch"]), tz=timezone.utc)
    s, tz = r.get("original_datetime"), r.get("source_timezone")
    if not s or not tz:
        return None
    for fmt in ("%Y-%m-%d %H:%M", "%Y-%m-%dT%H:%M", "%Y-%m-%d"):
        try:
            d = datetime.strptime(s, fmt)
            if fmt == "%Y-%m-%d":
                return None          # sin hora: no se puede normalizar
            return common.source_dt_to_utc(d, tz)
        except ValueError:
            continue
    return None


def _norm_record(r):
    r = dict(r)
    r["_utc"] = raw_to_utc(r)
    r["_home"], r["_away"] = common.norm_name(r["home"]), common.norm_name(r["away"])
    r["_cat"] = detect_category(r["home"], r["away"], r.get("competition"), r.get("category_hint"))
    return r


def _same_event(a, b):
    if (a["_home"], a["_away"], a["_cat"]) != (b["_home"], b["_away"], b["_cat"]):
        return False
    if a["_utc"] and b["_utc"] and abs(a["_utc"] - b["_utc"]) > timedelta(hours=CLUSTER_HOURS):
        return False
    return True


def cluster(raws):
    """Agrupa registros que son el mismo encuentro. Ambigüedad de competición => NO se fusiona."""
    groups, ambiguous = [], []
    for r in raws:
        placed = False
        for g in groups:
            if _same_event(g[0], r):
                comps_ok = all(competitions_compatible(x.get("competition"), r.get("competition")) for x in g)
                if comps_ok:
                    g.append(r)
                    placed = True
                    break
                ambiguous.append((g[0], r))
        if not placed:
            groups.append([r])
    return groups, ambiguous


def match_id(home_n, away_n, cat, local_date):
    return "m-" + hashlib.sha1(f"{home_n}|{away_n}|{cat}|{local_date}".encode()).hexdigest()[:12]


def _group_status(map_event_status, raw, now, start):
    s = map_event_status(raw) if raw else None
    if s and s != "DESCONOCIDO":
        if s == "PROGRAMADO" and start and now >= start:
            return "DESCONOCIDO", "fuente dice 'programado' pero la hora ya pasó"
        return s, None
    if start and now < start:
        return "PROGRAMADO", None
    return "DESCONOCIDO", None


def build_inventory(raws_by_source, day, tz, now, policy, status_mappers=None):
    """raws_by_source: {fuente: [registros brutos]}. Devuelve (matches, raw_duplicates)."""
    win_start, win_end = common.window_for_local_date(day, tz)
    status_mappers = status_mappers or {"apwin": adapters.apwin_status}
    allraw = []
    for src, lst in raws_by_source.items():
        allraw.extend(_norm_record(x) for x in lst)
    # duplicados dentro de la misma fuente (mismo equipo/hora): se conservan como DUPLICADO
    seen, uniq, dups = {}, [], []
    for r in allraw:
        k = (r["source"], r["_home"], r["_away"], r["_cat"], r["_utc"].isoformat() if r["_utc"] else r["original_datetime"])
        if k in seen:
            d = {kk: vv for kk, vv in r.items() if not kk.startswith("_")}
            d.update(calendar_verification_status="DUPLICADO", duplicate_of=seen[k])
            dups.append(d)
        else:
            seen[k] = r["source"] + ":" + str(r["source_match_id"])
            uniq.append(r)
    groups, ambiguous = cluster(uniq)
    amb_ids = {id(a) for a, _ in ambiguous} | {id(b) for _, b in ambiguous}
    matches = []
    for g in groups:
        g.sort(key=lambda x: (x["_utc"] is None, x["_utc"] or datetime.max.replace(tzinfo=timezone.utc)))
        base = g[0]
        times = [x["_utc"] for x in g if x["_utc"]]
        utc = times[0] if times else None
        local = common.utc_to_local(utc, tz) if utc else None
        discrepancies = []
        spread = (max(times) - min(times)) if len(times) > 1 else timedelta(0)
        if spread > timedelta(minutes=TOL_DISCREPANCY_MIN):
            discrepancies.append({"kind": "hora", "detail": f"las fuentes difieren {int(spread.total_seconds() // 60)} min",
                                  "sources": [x["source"] for x in g]})
        for x in g:
            if id(x) in amb_ids:
                discrepancies.append({"kind": "posible_duplicado_ambiguo",
                                      "detail": "mismo par de equipos y hora con competición no compatible; se mantienen registros separados",
                                      "sources": [x["source"]]})
        groups_ind = set()
        reliab = []
        for x in g:
            prov = x["source"].split(":")[0]
            prov_cfg = policy.data["providers"].get(prov, {})
            groups_ind.add(prov_cfg.get("independence_group", prov))
            reliab.append(prov_cfg.get("reliability", "usuario" if prov == "usuario" else "agregada"))
        in_window = bool(utc and win_start <= utc < win_end)
        ev_raw = next((x["event_status_raw"] for x in g if x.get("event_status_raw")), None)
        mapper = status_mappers.get(base["source"].split(":")[0], lambda s: s.upper() if s else None)
        ev, ev_note = _group_status(mapper, ev_raw, now, utc)
        if ev_note:
            discrepancies.append({"kind": "estado", "detail": ev_note, "sources": [base["source"]]})
        # estado de calendario + base de confirmación
        if utc is None:
            cal, basis = "INFORMACION_INSUFICIENTE", "ninguna"
        elif any(d["kind"] == "hora" for d in discrepancies):
            cal, basis = "FECHA_DISCREPANTE", "ninguna"
        elif len(groups_ind) >= 2:
            cal, basis = "CONFIRMADO", "dos_fuentes_independientes"
        elif "estructurada" in reliab:
            cal, basis = "CONFIRMADO", "una_fuente_estructurada_fiable_sin_discrepancias"
        else:
            cal, basis = "NO_CONFIRMADO", "ninguna"
        # elegibilidad prepartido
        if cal != "CONFIRMADO":
            elig, disp = "PENDIENTE_DE_VERIFICAR", f"calendario {cal}: verificar con fuentes adicionales"
        elif not in_window:
            elig, disp = "NO_ELEGIBLE", "NO_ELEGIBLE — fuera de la fecha local solicitada"
        elif ev in ("APLAZADO", "CANCELADO"):
            elig, disp = "NO_ELEGIBLE", f"NO_ELEGIBLE — encuentro {ev.lower()}"
        elif ev in ("EN_JUEGO", "FINALIZADO") or (utc and now >= utc):
            elig, disp = "NO_ELEGIBLE", "NO_ELEGIBLE_PREPARTIDO — el encuentro ya ha comenzado"
        else:
            elig, disp = "ELEGIBLE", "elegible para evaluación prepartido"
        mid = match_id(base["_home"], base["_away"], base["_cat"], local.date().isoformat() if local else "sin-fecha")
        comp = next((x["competition"] for x in g if x.get("competition")), "")
        matches.append({
            "match_id": mid, "home_team": base["home"], "away_team": base["away"], "competition": comp,
            "country": next((x["country"] for x in g if x.get("country")), ""), "gender_or_category": base["_cat"],
            "source_match_ids": {x["source"]: x["source_match_id"] for x in g}, "source_names": sorted({x["source"] for x in g}),
            "original_datetime": {x["source"]: x["original_datetime"] for x in g},
            "source_timezone": {x["source"]: {"tz": x["source_timezone"], "confirmada": bool(x["tz_confirmed"])} for x in g},
            "normalized_datetime_utc": utc.strftime("%Y-%m-%dT%H:%M:%SZ") if utc else None,
            "normalized_datetime_local": local.isoformat() if local else None,
            "calendar_verification_status": cal, "confirmation_basis": basis,
            "event_status": ev, "prematch_eligibility": elig, "disposition": disp,
            "analysis_required": bool(cal == "CONFIRMADO" and elig == "ELEGIBLE"),
            "sports_analysis_status": "PENDIENTE", "market_analysis_status": "PENDIENTE",
            "verification_sources": sorted({x["source"] for x in g}), "discrepancies": discrepancies,
            "extra": {k: next((x[k] for x in g if x.get(k)), None) for k in ("div", "odds", "referee")},
            "last_updated": now.strftime("%Y-%m-%dT%H:%M:%SZ"),
        })
    matches.sort(key=lambda m: (m["normalized_datetime_utc"] or "9", m["match_id"]))
    return matches, dups


def source_registry(policy, attempts):
    """Tabla de 8 campos: las consultadas (attempts) y las del catálogo excluidas por política."""
    rows = list(attempts)
    done = {a["Fuente"] for a in rows}
    for name, p in policy.data["providers"].items():
        if name not in done and p["status"] == "excluida":
            rows.append({"Fuente": name, "URL o ficha": p["evidence"][0] if p.get("evidence") else "",
                         "Dato buscado": "calendario", "Información obtenida": "—", "Fecha de consulta": "—",
                         "Estado": "No consultada", "Discrepancias": "—",
                         "Alternativa consultada": "EXCLUIDA por política: " + p["reason"]})
    return rows


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--date", required=True)
    ap.add_argument("--tz", default=common.DEFAULT_TZ)
    ap.add_argument("--run-dir", default="runs")
    ap.add_argument("--manual", action="append", default=[], help="calendario aportado por el usuario (CSV/JSON)")
    ap.add_argument("--no-apwin", action="store_true")
    a = ap.parse_args(argv)
    now = datetime.now(timezone.utc)
    run = os.path.join(a.run_dir, a.date)
    policy = common.Policy()
    client = common.Client(os.path.join(run, "cache"), os.path.join(run, "sources", "consultas.jsonl"), policy=policy)
    win = common.window_for_local_date(a.date, a.tz)
    raws, attempts = {}, []

    def attempt(name, url, what, fn):
        t = now.strftime("%Y-%m-%d %H:%M UTC")
        try:
            res = fn()
            raws[name] = raws.get(name, []) + res
            attempts.append({"Fuente": name, "URL o ficha": url, "Dato buscado": what,
                             "Información obtenida": f"{len(res)} registros", "Fecha de consulta": t,
                             "Estado": "Consultada y útil" if res else "Consultada con datos insuficientes",
                             "Discrepancias": "—", "Alternativa consultada": "—"})
        except (common.PolicyError, common.FetchError) as e:
            attempts.append({"Fuente": name, "URL o ficha": url, "Dato buscado": what, "Información obtenida": "—",
                             "Fecha de consulta": t, "Estado": "Acceso fallido", "Discrepancias": "—",
                             "Alternativa consultada": f"{type(e).__name__}: {e}"})

    attempt("football-data", adapters.FD_BASE + "/fixtures.csv", "calendario (fixtures.csv)", lambda: adapters.fd_fixtures(client))
    if not a.no_apwin:
        attempt("apwin", adapters.APWIN_BASE + "/", "calendario (portada del día; HTML parcial)", lambda: adapters.apwin_home(client))
    for path in a.manual:
        attempt("usuario", path, "calendario aportado por el usuario", lambda p=path: adapters.manual_calendar(p))
    matches, dups = build_inventory(raws, a.date, a.tz, now, policy)
    brutos = {k: len(v) for k, v in raws.items()}
    for k, v in raws.items():
        common.write_json_atomic(os.path.join(run, "sources", f"raw_{k.replace(':', '_')}.json"), v)
    inv = {"meta": {"date": a.date, "tz": a.tz, "window_utc": [win[0].strftime("%Y-%m-%dT%H:%M:%SZ"), win[1].strftime("%Y-%m-%dT%H:%M:%SZ")],
                    "generated_at": now.strftime("%Y-%m-%dT%H:%M:%SZ"), "raw_counts": brutos,
                    "source_registry": source_registry(policy, attempts)},
           "matches": matches, "raw_duplicates": dups}
    common.write_json_atomic(os.path.join(run, "inventory.json"), inv)
    n_el = sum(1 for m in matches if m["analysis_required"])
    print(f"inventario: {len(matches)} únicos (brutos {brutos}); en ventana local y elegibles: {n_el}; ->", os.path.join(run, "inventory.json"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
