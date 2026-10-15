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

_WOMEN = re.compile(r"\b(women|woman|femin\w*|ladies|w)\b|\(w\)|\bfem\b")
_YOUTH = re.compile(r"\bu-?(1[5-9]|20)\b|\b(youth|juvenil|junior\w*|academy)\b")
_YOUTH_TEAM = re.compile(r"\bu-?(1[5-9]|20)\b|\b(youth|juvenil|academy)\b")      # «Juniors» en el nombre de un equipo (Boca Juniors, Argentinos Juniors) NO es categoría juvenil
_U23 = re.compile(r"\bu-?(2[1-3])\b")
_RESERVE_TEAM = re.compile(r"(\s(b|ii|iii)$|\bb team\b|\breserves?\b|\bcastilla\b)")
_RESERVE_COMP = re.compile(r"\b(reserves?|reserva\w*|development)\b")
_FIRST_TEAM_EXCEPTIONS = {"willem ii", "juan pablo ii"}      # clubes de primer equipo cuyo nombre termina en II


def detect_category(home, away, competition, hint=None):
    """women > youth (U15-U20) > u23 (U21-U23) > reserve > men. Se mira el NOMBRE DE CADA EQUIPO para reservas
    (no la competición: 'Serie B' es primera plantilla). Es una etiqueta de apoyo, no decide elegibilidad."""
    if hint:
        return hint
    teams = [(home or "").lower().strip(), (away or "").lower().strip()]
    text = " ".join(teams + [(competition or "").lower()])
    if _WOMEN.search(text):
        return "women"
    if _YOUTH_TEAM.search(" ".join(teams)) or _YOUTH.search((competition or "").lower()):
        return "youth"
    if _U23.search(text):
        return "u23"
    if _RESERVE_COMP.search((competition or "").lower()) or any(
            _RESERVE_TEAM.search(t) and t not in _FIRST_TEAM_EXCEPTIONS for t in teams):
        return "reserve"
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


def match_id(home_n, away_n, local_date):
    """ID estable: NO depende de la categoría ni de la competición (cambian al corregir clasificaciones)."""
    return "m-" + hashlib.sha1(f"{home_n}|{away_n}|{local_date}".encode()).hexdigest()[:12]


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
    status_mappers = status_mappers or {"apwin": adapters.apwin_status, "apifootball": adapters.apwin_status}
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
        if cal == "CONFIRMADO" and discrepancies:
            basis = basis.replace("_sin_discrepancias", "") + "_con_discrepancias_abiertas"
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
        mid = match_id(base["_home"], base["_away"], local.date().isoformat() if local else "sin-fecha")
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
            "selection_calendar_verification": ("SUFICIENTE" if cal == "CONFIRMADO" and basis in ("oficial", "dos_fuentes_independientes")
                                                else "REQUIERE_VERIFICACION_ADICIONAL"),
            "event_status": ev, "prematch_eligibility": elig, "disposition": disp,
            "analysis_required": bool(cal == "CONFIRMADO" and elig == "ELEGIBLE"),
            "sports_analysis_status": "PENDIENTE", "market_analysis_status": "PENDIENTE",
            "verification_sources": sorted({x["source"] for x in g}), "discrepancies": discrepancies,
            "extra": {k: next((x[k] for x in g if x.get(k)), None) for k in ("div", "odds", "referee", "api")},
            "last_updated": now.strftime("%Y-%m-%dT%H:%M:%SZ"),
        })
    matches.sort(key=lambda m: (m["normalized_datetime_utc"] or "9", m["competition"], m["gender_or_category"]))
    seen_ids = {}
    for m in matches:                                   # colisión (mismo par y día, p. ej. dos categorías): sufijo determinista
        n = seen_ids.get(m["match_id"], 0)
        seen_ids[m["match_id"]] = n + 1
        if n:
            m["match_id"] = f'{m["match_id"]}-{n + 1}'
    return matches, dups


def carry_over_progress(matches, prev_matches):
    """Conserva sports/market_analysis_status de una ejecución anterior si el partido (mismo id y misma hora) no cambió."""
    prev = {m["match_id"]: m for m in prev_matches}
    for m in matches:
        old = prev.get(m["match_id"])
        if old and old.get("normalized_datetime_utc") == m["normalized_datetime_utc"]:
            for k in ("sports_analysis_status", "market_analysis_status"):
                if old.get(k) not in (None, "PENDIENTE"):
                    m[k] = old[k]
            pr = (old.get("extra") or {}).get("proxy_resolution")
            if pr and m.get("sports_analysis_status") == old.get("sports_analysis_status"):
                m.setdefault("extra", {})["proxy_resolution"] = pr     # sin esto la trazabilidad del proxy se pierde al regenerar
    return matches


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


_GENERIC_TOKENS = re.compile(r"^(u-?\d{2}|women|woman|w|youth|juvenil|reserves?|team|academy|ii|iii)$")


def _distinct_tokens(s):
    """Tokens que identifican al club (sin marcadores de categoría como U19/Women, que comparten equipos distintos)."""
    return {t for t in _tokens(s) if not _GENERIC_TOKENS.match(t)}


def _prefix_token(ta, tb):
    """Un token (≥3 letras) es prefijo de un token del otro nombre: «van» ~ «vanspor», «pohang» ~ «pohangs»."""
    return any(len(x) >= 3 and (y.startswith(x) or x.startswith(y)) and min(len(x), len(y)) >= 3 for x in ta for y in tb)


def _team_compat(a, b):
    na, nb = common.norm_name(a), common.norm_name(b)
    return bool(na and nb and (na == nb or na in nb or nb in na or (_distinct_tokens(a) & _distinct_tokens(b))
                               or _prefix_token(_distinct_tokens(a), _distinct_tokens(b))))


def align_api_records(api_recs, other_raws, tol_min=10):
    """Alinea los eventos de la API con los de otras fuentes SIN fusión difusa a ciegas: mismo instante (±tol_min), misma
    categoría y compatibilidad de nombre en AMBOS equipos, con candidato único en ambos sentidos. Si hay ambigüedad el evento
    de la API NO entra al inventario (evita doble conteo) y queda listado. Devuelve (registros_a_incluir, informe)."""
    others = [_norm_record(r) for r in other_raws]
    cand = []
    for r in api_recs:
        nr = _norm_record(r)
        cs = [i for i, o in enumerate(others) if nr["_utc"] and o["_utc"] and abs(nr["_utc"] - o["_utc"]) <= timedelta(minutes=tol_min)
              and nr["_cat"] == o["_cat"] and _team_compat(r["home"], o["home"]) and _team_compat(r["away"], o["away"])]
        cand.append(cs)
    taken = {}
    for i, cs in enumerate(cand):
        if len(cs) == 1:
            taken.setdefault(cs[0], []).append(i)
    keep, ambiguous, aligned = [], [], 0
    for i, (r, cs) in enumerate(zip(api_recs, cand)):
        if len(cs) == 0:
            keep.append(r)
        elif len(cs) == 1 and len(taken[cs[0]]) == 1:
            o = other_raws[cs[0]]
            r = dict(r, home=o["home"], away=o["away"], competition=o.get("competition") or r.get("competition"),
                     country=o.get("country") or r.get("country"), aligned_to=o["source"] + ":" + str(o["source_match_id"]))
            keep.append(r)
            aligned += 1
        else:
            ambiguous.append({"api": r["api"]["home_name"] + " – " + r["api"]["away_name"], "api_match_id": r["source_match_id"],
                              "candidates": [other_raws[c]["home"] + " – " + other_raws[c]["away"] for c in cs]})
    rep = {"api_total": len(api_recs), "aligned_with_other_source": aligned, "api_only_added": len(keep) - aligned,
           "ambiguous_excluded": len(ambiguous), "ambiguous": ambiguous}
    return keep, rep


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--date", required=True)
    ap.add_argument("--tz", default=common.DEFAULT_TZ)
    ap.add_argument("--run-dir", default="runs")
    ap.add_argument("--manual", action="append", default=[], help="calendario aportado por el usuario (CSV/JSON)")
    ap.add_argument("--no-apwin", action="store_true")
    ap.add_argument("--no-api", action="store_true", help="no consultar apifootball (clave en APIFOOTBALL_KEY / APIFOOTBALL_KEY_FILE)")
    a = ap.parse_args(argv)
    now = datetime.now(timezone.utc)
    run = os.path.join(a.run_dir, a.date)
    policy = common.Policy()
    client = common.Client(os.path.join(run, "cache"), os.path.join(run, "sources", "consultas.jsonl"), policy=policy)
    win = common.window_for_local_date(a.date, a.tz)
    raws, attempts, completeness = {}, [], []

    def attempt(name, url, what, fn):
        t = now.strftime("%Y-%m-%d %H:%M UTC")
        try:
            res = fn()
            raws[name] = raws.get(name, []) + res
            attempts.append({"Fuente": name, "URL o ficha": url, "Dato buscado": what,
                             "Información obtenida": f"{len(res)} registros", "Fecha de consulta": t,
                             "Estado": "Consultada y útil" if res else "Consultada con datos insuficientes",
                             "Discrepancias": "—", "Alternativa consultada": "—"})
        except (common.PolicyError, common.FetchError, adapters.ApiLimit) as e:
            attempts.append({"Fuente": name, "URL o ficha": url, "Dato buscado": what, "Información obtenida": "—",
                             "Fecha de consulta": t, "Estado": "Acceso fallido", "Discrepancias": "—",
                             "Alternativa consultada": f"{type(e).__name__}: {e}"})

    attempt("football-data", adapters.FD_BASE + "/fixtures.csv", "calendario (fixtures.csv)", lambda: adapters.fd_fixtures(client))
    if not a.no_apwin:
        for dday in common.days_to_query(a.date, a.tz):     # semántica de fecha de la fuente no certificada: día -1, 0, +1
            u = f"{adapters.APWIN_BASE}/?date={dday.isoformat()}"
            def _apw(x=dday.isoformat()):
                recs, pag = adapters.apwin_fetch_all(client, x)
                if pag:
                    completeness.append(dict(pag, source="apwin"))
                return recs
            attempt("apwin", u, f"calendario del día {dday.isoformat()} (HTML público + JSON público paginado /api/home/calendar)", _apw)
    api_report = None
    key = None if a.no_api else adapters.apif_key()
    if key:
        d0, d1 = (d.isoformat() for d in (lambda ds: (ds[0], ds[-1]))(common.days_to_query(a.date, a.tz)))
        def _api():
            global_recs = adapters.apif_event_records(adapters.apif_events(client, key, d0, d1))
            others = [r for lst in raws.values() for r in lst]
            keep, rep = align_api_records(global_recs, others)
            nonlocal api_report
            api_report = rep
            completeness.append({"source": "apifootball", "loaded": len(global_recs), "declared_total": len(global_recs), "complete": True,
                                 "note": "get_events del rango de días UTC; sin paginación"})
            return keep
        attempt("apifootball", adapters.APIF_BASE + f"?action=get_events&from={d0}&to={d1}", "calendario (get_events, timezone=UTC)", _api)
    else:
        attempts.append({"Fuente": "apifootball", "URL o ficha": adapters.APIF_BASE, "Dato buscado": "calendario", "Información obtenida": "—",
                         "Fecha de consulta": now.strftime("%Y-%m-%d %H:%M UTC"), "Estado": "No consultada",
                         "Discrepancias": "—", "Alternativa consultada": "sin clave en el entorno (APIFOOTBALL_KEY) o --no-api"})
    for path in a.manual:
        attempt("usuario", path, "calendario aportado por el usuario", lambda p=path: adapters.manual_calendar(p))
    matches, dups = build_inventory(raws, a.date, a.tz, now, policy)
    prev = common.read_json(os.path.join(run, "inventory.json"), {"matches": []})
    carry_over_progress(matches, prev.get("matches", []))     # regenerar el inventario NO borra el avance de la evaluación
    brutos = {k: len(v) for k, v in raws.items()}
    for k, v in raws.items():
        common.write_json_atomic(os.path.join(run, "sources", f"raw_{k.replace(':', '_')}.json"), v)
    inv = {"meta": {"date": a.date, "tz": a.tz, "window_utc": [win[0].strftime("%Y-%m-%dT%H:%M:%SZ"), win[1].strftime("%Y-%m-%dT%H:%M:%SZ")],
                    "generated_at": now.strftime("%Y-%m-%dT%H:%M:%SZ"), "raw_counts": brutos,
                    "source_completeness": completeness, "api_alignment": api_report,
                    "source_registry": source_registry(policy, attempts)},
           "matches": matches, "raw_duplicates": dups}
    common.write_json_atomic(os.path.join(run, "inventory.json"), inv)
    n_el = sum(1 for m in matches if m["analysis_required"])
    print(f"inventario: {len(matches)} únicos (brutos {brutos}); en ventana local y elegibles: {n_el}; ->", os.path.join(run, "inventory.json"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
