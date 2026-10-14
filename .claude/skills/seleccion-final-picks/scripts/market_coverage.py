#!/usr/bin/env python3
"""TRES CONTROLES INDEPENDIENTES sobre las combinaciones REQUERIDAS partido × mercado/línea × canal (Fase 1, cierre).

Una combinación requerida = (partido autorizado, entrada del catálogo `market_catalog.py`, canal). Canales: «datos_deportivos» + un canal por cada proveedor de precios
registrado. Cada combinación debe tener un REGISTRO con resultado y evidencia; la completitud se mide sobre ese conjunto generado, no comparando etiquetas.

A. INVESTIGACIÓN (`investigation_gate`): ¿se examinó cada combinación? Resultado por registro:
     encontrado | consultado_no_encontrado | fuente_no_ofrece | no_verificable | pendiente
   Está resuelto si el resultado es distinto de «pendiente» y lleva evidencia. «fuente_no_ofrece» resuelve la combinación SOLO respecto de esa fuente (no prueba que el
   mercado no exista en otras). La ausencia de cuota, de estadística o de modelo NO decide nada aquí. Estado: INVESTIGACION_COMPLETA | INVESTIGACION_INCOMPLETA + incidencias.
   No hay umbral porcentual: el % de cobertura es solo un indicador informativo.
B. ANALÍTICA (`analytic_report`): datos suficientes, estimador propio implementado (lo que `leg_model.model_probs` devuelve de verdad) y nivel de validación del modelo.
   Una investigación puede estar completa con limitaciones analíticas; nunca se inventan probabilidades.
C. PRECIOS (`pricing_report`): cuota real verificable de una fuente identificada y cumplimiento del límite individual MAX_LEG_ODDS. Un precio ausente NO es investigación incompleta.

`certified(summary)` = modo «enforce» y A completa. SIGNIFICA SOLO «la investigación del catálogo es exhaustiva»: se expone como `investigacion_certificada` (alias antiguo
`certificado_investigacion`/`certificado`, mismo valor). NO es una aprobación para apostar. Una salida omitida (`modo: omitida`) o con A incompleta nunca se certifica.
PREPARACIÓN PARA APOSTAR (`row_readiness`, `ticket_readiness`, `betting_summary`): estado INDEPENDIENTE; exige a la vez precio real verificado de fuente identificada, cuota
≤ MAX_LEG_ODDS, datos suficientes, estimador propio calculable, MODELO VALIDADO (hoy «insuficiente»: nunca se convierte automáticamente en apto) e investigación resuelta.
Uso: market_coverage.py --run runs/<fecha> [--matches ids.json|id1,id2] [--prices csv|json ...] [--out-dir DIR]
"""
import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common  # noqa: E402
import leg_model  # noqa: E402
import market_catalog as mc  # noqa: E402
import price_sources as ps  # noqa: E402
import tickets  # noqa: E402

RESULTADOS = ("encontrado", "consultado_no_encontrado", "fuente_no_ofrece", "no_verificable", "pendiente")
CANAL_DATOS = "datos_deportivos"
MAX_LEG_ODDS = 2.10          # límite individual de cuota por pata (decisión de la persona usuaria)
MIN_N = tickets.MIN_N
# Nivel de validación declarado del modelo propio: lo escribe `backtest_modelo.py --write-validation data/model_validation.json` (política declarada en POLICY); sin ese archivo,
# o mientras ningún backtest lo justifique, es «insuficiente». Nunca se sube a mano.
MODEL_VALIDATION = {"nivel": "insuficiente", "referencia": "docs/BACKTEST-modelo-v1.md", "familias": {}, "blend_weight": None,
                    "motivo": "sin backtest vigente: ningún modelo se considera validado"}
_VALIDATION_FILE = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "..", "data", "model_validation.json"))


def load_model_validation(path=_VALIDATION_FILE):
    if os.path.exists(path):
        try:
            v = common.read_json(path)
            MODEL_VALIDATION.update({k: v[k] for k in ("nivel", "familias", "motivo", "referencia", "generado_utc") if k in v})
            MODEL_VALIDATION["blend_weight"] = v.get("blend_weight")
        except (OSError, ValueError):
            pass
    return MODEL_VALIDATION


load_model_validation()
# Familia de validación (backtest_modelo.py) de cada capacidad del catálogo; las no probadas (DNB, hándicaps, 1.ª parte) no tienen familia => no validadas.
VALIDATION_FAMILY = {"1x2": "1x2", "dc": "dc", "goals_total": "goals_total", "btts": "btts", "team_goals": "team_goals", "count:corners": "corners_total", "count:cards": "cards_total"}


def validation_level(entry):
    """Nivel de validación del estimador de esta entrada: el de su familia en el backtest; sin familia (no probada) o sin archivo, el global."""
    fam = VALIDATION_FAMILY.get(entry.get("model"))
    fams = MODEL_VALIDATION.get("familias") or {}
    if fam and fam in fams:
        return fams[fam]["nivel"]
    return "no_evaluada" if fams and entry.get("model") else MODEL_VALIDATION["nivel"]


CHANNEL_SEMANTICS = {
    "datos": "encontrado = el historial obtenido por una consulta externa REGISTRADA contiene el campo que el mercado necesita en ≥1 fila; consultado_no_encontrado = el campo falta en todas las filas; "
             "NO significa estadística suficiente (analítica) ni que el mercado/línea concreto se consultara en una fuente externa",
    "precios": "encontrado = la fuente, consultada para este partido, devolvió precio; consultado_no_encontrado = consultada sin precio; fuente_no_ofrece = la fuente no publica el mercado; pendiente = sin constancia de consulta o adaptador sin mapear"}


# ── ¿el estimador está validado? ──
def model_validated(entry):
    """True solo con validación suficiente (de su familia, o global): un modelo no validado nunca habilita recomendar."""
    return MODEL_VALIDATION["nivel"] == "suficiente" or validation_level(entry) == "suficiente"


# ── helpers de datos deportivos ──
def _field_present(h, field):
    if field == "cards_pts":
        return tickets._cards_tuple(h) is not None
    v = h.get(field)
    if v is None:
        return False
    if isinstance(v, (tuple, list)):
        return None not in v
    return True


def _probe_model_keys():
    """Claves que los modelos propios devuelven DE VERDAD (no las que prometa la documentación): leg_model.model_probs y count_model.model_probs."""
    import count_model
    rows = [{"gf": 1, "ga": 1, "venue": "local", "ht_goals": (1, 0)}] * 8
    keys = set(leg_model.model_probs(rows, rows, 1.3, 1.1, share=0.45).keys())
    crows = [{"venue": "local", "own": 5, "opp": 4}] * 8
    st = {"mu": 5.0, "adv": 1.1, "r_total": None, "r_team": None, "n": 100}
    for name, tl, ml in (("corners", count_model.CORNER_TOTAL, count_model.CORNER_TEAM), ("cards", count_model.CARD_TOTAL, count_model.CARD_TEAM)):
        keys |= set(count_model.model_probs(name, crows, crows, st, tl, ml))
    return keys


def model_key(entry, keys):
    """Clave de salida del modelo propio que cubre la entrada, o None si ningún modelo la calcula."""
    m, d, ln = entry.get("model"), entry.get("direction"), entry.get("line")
    if m == "1x2":
        k = {"home": "p1", "draw": "px", "away": "p2"}[d]
    elif m == "dc":
        k = {"1x": "1x", "x2": "x2", "12": "12"}[d]
    elif m == "goals_total":
        k = f"over_{ln}"
    elif m == "btts":
        k = "btts"
    elif m == "dnb":
        k = f"dnb_{d}"
    elif m == "handicap":
        k = f"ah_{d}_{ln:+.1f}"
    elif m == "team_goals":
        k = f"{entry['scope']}_over_{ln}"
    elif m == "half_1x2":
        k = {"home": "ht_p1", "draw": "ht_px", "away": "ht_p2"}[d]
    elif m == "half_total":
        k = f"ht_over_{ln}"
    elif m in ("count:corners", "count:cards"):
        name = m.split(":")[1]
        k = f"{name}_{'total' if entry['scope'] == 'match' else entry['scope']}_over_{ln}"
    else:
        return None
    return k if k in keys else None


def _rec(canal, resultado, evidencia, nota=None):
    assert resultado in RESULTADOS
    return {"canal": canal, "resultado": resultado, "evidencia": evidencia, "nota": nota}


def _external_consultation(ev):
    """Evidencia de que el historial de este partido se obtuvo por una CONSULTA EXTERNA registrada por level1.py (`attempts`), no solo que haya filas en un archivo local."""
    prov = str(ev.get("history_kind") or "").split("_")[0]
    for a in ev.get("attempts") or []:
        if a.get("provider") == prov and str(a.get("resultado", "")).startswith("consultada"):
            return {"proveedor": prov, "detalle": a["resultado"], "referencia": f"matrix.json:{ev.get('match_id', '?')}:attempts"}
    return None


def _datos_record(entry, ev):
    """Investigación deportiva = consulta externa REGISTRADA del historial del partido + comprobación de que el campo que el mercado necesita existe en esas filas.
    encontrado = consulta registrada y el campo está en ≥1 fila · consultado_no_encontrado = consulta registrada y el campo falta en TODAS las filas · pendiente = sin historial o sin
    constancia de consulta externa (filas en un archivo local no bastan) · no_verificable = historial de otra competición. NO implica estadística suficiente (eso es la analítica)."""
    if not ev or not ((ev.get("form") or {}).get("local") or (ev.get("form") or {}).get("visitante")):
        return _rec(CANAL_DATOS, "pendiente", None, "el partido no tiene historial consultado")
    fh, fa = ev["form"].get("local", []), ev["form"].get("visitante", [])
    consulta = _external_consultation(ev)
    evid = {"tipo_verificacion": "consulta_externa_registrada + campo_en_historial_local", "consulta_externa": consulta, "referencia": f"matrix.json:{ev.get('match_id', '?')}:form",
            "historial": ev.get("history_kind"), "filas_examinadas": [len(fh), len(fa)], "campos": entry["data_requirements"]}
    if ev.get("history_kind") not in tickets.OK_KINDS:
        return _rec(CANAL_DATOS, "no_verificable", evid, f"historial no propio de la competición ({ev.get('history_kind')})")
    if consulta is None:
        return _rec(CANAL_DATOS, "pendiente", None, "hay filas de historial pero no consta la consulta externa que las originó (solo archivo local)")
    n = [sum(1 for h in rows if all(_field_present(h, f) for f in entry["data_requirements"])) for rows in (fh, fa)]
    evid["filas_con_el_campo"] = n
    return _rec(CANAL_DATOS, "encontrado" if sum(n) > 0 else "consultado_no_encontrado", evid)


def _price_records(match, entry, providers, found, failed):
    out = []
    for p in providers:
        canal = getattr(p, "name", "proveedor")
        if canal in failed:
            out.append(_rec(canal, "pendiente", None, f"la consulta falló: {failed[canal]}"))
            continue
        cov_fn = getattr(p, "covers", None)
        if cov_fn:
            cubre, evid_c = cov_fn(match)
            if not cubre:
                out.append(_rec(canal, "fuente_no_ofrece", evid_c, "la_fuente_no_cubre_este_partido"))
                continue
        ok, why = p.supports(entry)
        if not ok:
            if why == "la_api_lo_entrega_pero_el_adaptador_no_lo_mapea":
                out.append(_rec(canal, "pendiente", None, "la fuente lo publica pero el adaptador no lo consulta todavía"))
            else:
                out.append(_rec(canal, "fuente_no_ofrece", {"fuente": canal, "referencia": "provider.vocabulary", "detalle": getattr(p, "vocabulary", ps.API_ODDS_VOCABULARY)}, why))
            continue
        cons, evid = p.consulted(match)
        if not cons:
            out.append(_rec(canal, "pendiente", None, "no consta que la fuente se consultara para este partido"))
            continue
        recs = found.get((match["match_id"], entry["id"]), [])
        recs = [r for r in recs if r["source"] == canal]
        out.append(_rec(canal, "encontrado" if recs else "consultado_no_encontrado", evid))
    return out


# ── contexto por partido: muestra de liga, árbitro y alineaciones (Fase 3). Son datos y limitaciones, NO puertas: no deciden la certificación ──
def load_league_samples(run):
    out = {}
    d = os.path.join(run, "league_samples")
    if os.path.isdir(d):
        for f in os.listdir(d):
            if f.endswith(".json"):
                try:
                    out[f[:-5]] = common.read_json(os.path.join(d, f))
                except (OSError, ValueError):
                    pass
    return out


def load_lineup_snapshots(run):
    """Última instantánea de alineaciones por partido (los archivos nuevos nunca sobrescriben a los anteriores)."""
    out = {}
    d = os.path.join(run, "lineups")
    if os.path.isdir(d):
        for f in sorted(os.listdir(d)):
            if f.endswith(".json"):
                try:
                    for r in common.read_json(os.path.join(d, f)).get("partidos", []):
                        out[r["match_id"]] = r
                except (OSError, ValueError, KeyError):
                    pass
    return out


def league_of(match, inv_matches):
    """league_id de apifootball del partido; si falta (p. ej. partidos que solo figuran en football-data) se toma el de otros partidos del inventario con la MISMA competición."""
    lid = ((match.get("extra") or {}).get("api") or {}).get("league_id")
    if lid:
        return str(lid)
    comp = str(match.get("competition", "")).lower()
    c = {}
    for m in inv_matches:
        l2 = ((m.get("extra") or {}).get("api") or {}).get("league_id")
        if l2 and str(m.get("competition", "")).lower() == comp:
            c[str(l2)] = c.get(str(l2), 0) + 1
    return max(c, key=c.get) if c else None


def match_context(match, inv_matches, samples, lineups):
    lid = league_of(match, inv_matches)
    smp = samples.get(lid) if lid else None
    rows = (smp or {}).get("filas") or []
    ref = ((match.get("extra") or {}).get("api") or {}).get("referee") or (match.get("extra") or {}).get("referee")
    ctx = {"liga_id": lid,
           "muestra_liga": {"ejecutada": smp is not None, "partidos": len(rows), "con_tarjetas": sum(1 for r in rows if r.get("tarjetas") is not None),
                            "con_corners": sum(1 for r in rows if r.get("corners") is not None), "con_arbitro": sum(1 for r in rows if r.get("arbitro"))},
           "arbitro": {"designado": ref or None, "partidos_en_muestra_liga": sum(1 for r in rows if ref and r.get("arbitro") == ref) if smp is not None else None}}
    snap = lineups.get(match["match_id"])
    ctx["alineaciones"] = ({"estado": "sin_snapshot"} if snap is None else
                           {"estado": "consulta_no_realizada" if snap.get("consulta") != "realizada" else ("publicada" if snap.get("publicada") else "no_publicada"),
                            "snapshot_utc": snap.get("consultado_utc"), "bajas_registradas": snap.get("bajas_registradas")})
    return ctx


def build_contexts(run, matches, inv_matches):
    samples, lineups = load_league_samples(run), load_lineup_snapshots(run)
    return {m["match_id"]: match_context(m, inv_matches, samples, lineups) for m in matches}


# ── analítica ──
def _datos_status(entry, atoms_by_label, ev, home, away):
    if entry["stats"] is None:
        return "sin_extractor", None
    if not ev or not (ev.get("form") or {}).get("local") and not (ev.get("form") or {}).get("visitante"):
        return "sin_datos", None
    if ev.get("history_kind") not in tickets.OK_KINDS:
        return "insuficientes", None
    a = atoms_by_label.get(mc.entry_label(entry, home, away))
    if a is None:
        return "sin_extractor", None
    ph, pa = a
    fh, fa = ev["form"].get("local", []), ev["form"].get("visitante", [])
    nh, na = sum(1 for h in fh if ph(h) is not None), sum(1 for h in fa if pa(h) is not None)
    return ("suficientes" if nh >= MIN_N and na >= MIN_N else "parciales" if nh >= 3 and na >= 3 else "insuficientes"), [nh, na]


def _estimator_status(entry, keys, ev):
    """calculable = existe estimador propio Y hay datos del campo que necesita; datos_insuficientes = hay estimador pero faltan datos; no_implementado = ningún modelo lo calcula."""
    k = model_key(entry, keys)
    if k is None:
        return "no_implementado", None
    f = (ev or {}).get("form") or {}
    need = entry["data_requirements"]
    ok = lambda rows: sum(1 for r in rows if all(_field_present(r, x) for x in need)) >= MIN_N
    return ("calculable" if ok(f.get("local", [])) and ok(f.get("visitante", [])) else "datos_insuficientes"), k


# ── precios ──
def _pricing(match, entry, providers, found, failed):
    if not providers:
        return {"estado": "no_consultado", "registro": None, "cumple_limite": None, "cumple_requisitos_de_precio": False, "nota": "sin proveedores de precio registrados"}
    recs = [r for r in found.get((match["match_id"], entry["id"]), [])]
    real = [r for r in recs if ps.is_real_price(r)]
    if real:
        best = max(real, key=lambda r: r["odds"])
        cumple = best["odds"] <= MAX_LEG_ODDS
        return {"estado": "real_verificada", "registro": best, "cumple_limite": cumple, "cumple_requisitos_de_precio": bool(cumple and best.get("source")), "nota": None}
    if recs:
        agg = [r for r in recs if r["source_type"] == "agregador" and (r.get("n_books") or 0) >= tickets.MIN_BOOKS]
        if agg:
            return {"estado": "otra_fuente", "registro": agg[0], "cumple_limite": agg[0]["odds"] <= MAX_LEG_ODDS, "cumple_requisitos_de_precio": False, "nota": "promedio de agregador: referencia, no precio ejecutable"}
        return {"estado": "no_verificable", "registro": recs[0], "cumple_limite": None, "cumple_requisitos_de_precio": False, "nota": "precio sin verificar o con pocas casas"}
    return {"estado": "sin_precio", "registro": None, "cumple_limite": None, "cumple_requisitos_de_precio": False, "nota": "ninguna fuente registrada aporta precio para esta combinación"}


def build_records(matches, ev_by_id, providers=(), catalog=None, contexts=None, revision_ok=False):
    """Un registro por combinación requerida (partido × entrada) con sus tres bloques. Devuelve (filas, errores_de_proveedores)."""
    catalog = mc.CATALOG if catalog is None else catalog
    providers = list(providers)
    found, errors = ps.collect_prices(providers, matches, catalog) if providers else ({}, [])
    failed = {e["provider"]: e["error"] for e in errors}
    keys = _probe_model_keys()
    rows = []
    for m in matches:
        ev = ev_by_id.get(m["match_id"])
        if ev is not None and "match_id" not in ev:
            ev = dict(ev, match_id=m["match_id"])
        home, away = m["home_team"], m["away_team"]
        atoms_by_label = {}
        if ev and (ev.get("form") or {}).get("local") is not None:
            atoms_by_label = {a[3]: (a[4], a[5]) for a in tickets.atoms(ev, (home, away), extended=True)}
        for e in catalog:
            canales = [_datos_record(e, ev)] + _price_records(m, e, providers, found, failed)
            datos, n = _datos_status(e, atoms_by_label, ev, home, away)
            est, mk = _estimator_status(e, keys, ev)
            rows.append({"match_id": m["match_id"], "partido": f"{home} – {away}", "entry_id": e["id"], "family": e["family"], "market": e["market"], "line": e["line"],
                         "investigacion": {"canales": canales, "resuelta": all(c["resultado"] != "pendiente" and c["evidencia"] for c in canales)},
                         "analitica": {"datos": datos, "datos_n": n, "estimador": est, "clave_modelo": mk, "validacion": validation_level(e) if est != "no_implementado" else None},
                         "precio": _pricing(m, e, providers, found, failed)})
            if contexts and e["data_requirements"][0] in ("corners", "cards_pts"):
                ml = (contexts.get(m["match_id"]) or {}).get("muestra_liga") or {}
                campo = "corners" if e["data_requirements"][0] == "corners" else "tarjetas"
                rows[-1]["analitica"]["muestra_liga"] = {"campo": campo, "ejecutada": ml.get("ejecutada", False), "partidos_liga": ml.get("partidos"), "con_campo": ml.get("con_" + ("corners" if campo == "corners" else "tarjetas"))}
            rows[-1]["preparacion_para_apostar"] = row_readiness(rows[-1], revision_ok)
    return rows, errors


# ── A. investigación ──
def required_combinations(authorized_ids, catalog, channels):
    return [(m, e["id"], c) for m in authorized_ids for e in catalog for c in channels]


def investigation_gate(rows, authorized_ids, catalog=None, channels=None):
    catalog = mc.CATALOG if catalog is None else catalog
    if channels is None:
        channels = sorted({c["canal"] for r in rows for c in r["investigacion"]["canales"]} | {CANAL_DATOS})
    auth = list(authorized_ids)
    required = required_combinations(auth, catalog, channels)
    got, dup, unknown, noev = {}, 0, 0, 0
    for r in rows:
        for c in r["investigacion"]["canales"]:
            k = (r["match_id"], r["entry_id"], c["canal"])
            if k in got:
                dup += 1
            got[k] = c
    inc = []

    def add(tipo, items):
        if items:
            inc.append({"tipo": tipo, "cantidad": len(items), "ejemplos": [list(x) if isinstance(x, tuple) else x for x in items[:3]]})
    add("combinacion_requerida_sin_registro", [k for k in required if k not in got])
    add("partido_no_autorizado", sorted({k[0] for k in got} - set(auth)))
    if dup:
        inc.append({"tipo": "registro_duplicado", "cantidad": dup, "ejemplos": []})
    for k, c in got.items():
        if c["resultado"] not in RESULTADOS:
            unknown += 1
        elif c["resultado"] != "pendiente" and not c["evidencia"]:
            noev += 1
    if unknown:
        inc.append({"tipo": "resultado_desconocido", "cantidad": unknown, "ejemplos": []})
    if noev:
        inc.append({"tipo": "resuelto_sin_evidencia", "cantidad": noev, "ejemplos": []})
    pend = [k for k, c in got.items() if c["resultado"] == "pendiente" and k[0] in set(auth)]
    for canal in channels:
        add(f"pendiente[{canal}]", [k for k in pend if k[2] == canal])
    por_canal = {}
    for canal in channels:
        cs = [c for k, c in got.items() if k[2] == canal and k[0] in set(auth)]
        cnt = {r: sum(1 for c in cs if c["resultado"] == r) for r in RESULTADOS}
        por_canal[canal] = {"requeridas": len(auth) * len(catalog), "registradas": len(cs), **cnt,
                            "cobertura_informativa": round((len(cs) - cnt["pendiente"]) / (len(auth) * len(catalog)), 3) if auth and catalog else 0.0,
                            "semantica": CHANNEL_SEMANTICS["datos"] if canal == CANAL_DATOS else CHANNEL_SEMANTICS["precios"]}
        if canal == CANAL_DATOS:
            por_canal[canal]["con_consulta_externa_registrada"] = sum(1 for c in cs if (c.get("evidencia") or {}).get("consulta_externa"))
            por_canal[canal]["campo_presente_en_historial_local"] = cnt["encontrado"]
            por_canal[canal]["campo_ausente_en_historial_local"] = cnt["consultado_no_encontrado"]
            por_canal[canal]["sin_constancia_de_consulta_externa"] = cnt["pendiente"]
    return {"estado": "INVESTIGACION_COMPLETA" if not inc else "INVESTIGACION_INCOMPLETA", "incidencias": inc, "combinaciones_requeridas": len(required), "canales": channels, "por_canal": por_canal}


# ── B. analítica ──
def analytic_report(rows, contexts=None):
    ent = {}
    for r in rows:
        a = r["analitica"]
        e = ent.setdefault(r["entry_id"], {"family": r["family"], "no_implementado": 0, "datos_insuf": 0, "filas": 0, "sin_extractor": 0})
        e["filas"] += 1
        e["no_implementado"] += a["estimador"] == "no_implementado"
        e["datos_insuf"] += a["datos"] in ("insuficientes", "sin_datos")
        e["sin_extractor"] += a["datos"] == "sin_extractor"
    sin_est = sorted(k for k, v in ent.items() if v["no_implementado"] == v["filas"])
    sin_ext = sorted(k for k, v in ent.items() if v["sin_extractor"] == v["filas"])
    inc = []
    if sin_est:
        inc.append({"tipo": "sin_estimador_propio", "cantidad": len(sin_est), "ejemplos": sin_est[:4]})
    if sin_ext:
        inc.append({"tipo": "sin_extractor_de_estadistica", "cantidad": len(sin_ext), "ejemplos": sin_ext[:4]})
    insuf = [r for r in rows if r["analitica"]["datos"] in ("insuficientes", "sin_datos")]
    if insuf:
        fam = {}
        for r in insuf:
            fam[r["family"]] = fam.get(r["family"], 0) + 1
        inc.append({"tipo": "datos_insuficientes", "cantidad": len(insuf), "por_familia": fam, "ejemplos": []})
    if any(r["analitica"]["estimador"] != "no_implementado" for r in rows):
        inc.append({"tipo": "modelo_sin_validacion_suficiente", "cantidad": sum(1 for r in rows if r["analitica"]["validacion"]), **MODEL_VALIDATION})
    if contexts:
        cx = list(contexts.values())
        ids = lambda f: [k for k, c in contexts.items() if f(c)]
        no_ej = ids(lambda c: not c["muestra_liga"]["ejecutada"])
        if no_ej:
            inc.append({"tipo": "muestra_de_liga_no_ejecutada", "cantidad": len(no_ej), "ejemplos": no_ej[:3]})
        for campo, key in (("tarjetas", "con_tarjetas"), ("corners", "con_corners")):
            por_liga = {}
            for c in cx:
                m_ = c["muestra_liga"]
                if m_["ejecutada"] and m_["partidos"] and m_[key] < m_["partidos"]:
                    por_liga[c["liga_id"]] = f"{m_[key]}/{m_['partidos']}"
            if por_liga:                                    # informativo, sin umbral: dónde la muestra de liga NO trae el dato en todos los partidos
                inc.append({"tipo": f"liga_con_registro_incompleto_de_{campo}", "cantidad": len(por_liga), "por_liga": por_liga, "ejemplos": sorted(por_liga),
                            "nota": "partidos de la muestra de liga con el dato / partidos de la muestra"})
        sin_ref = ids(lambda c: not c["arbitro"]["designado"])
        if sin_ref:
            inc.append({"tipo": "arbitro_no_designado", "cantidad": len(sin_ref), "ejemplos": sin_ref[:3]})
        ref_sin = ids(lambda c: c["arbitro"]["designado"] and not c["arbitro"]["partidos_en_muestra_liga"])
        if ref_sin:
            inc.append({"tipo": "arbitro_designado_sin_partidos_en_la_muestra", "cantidad": len(ref_sin), "ejemplos": ref_sin[:3]})
        no_pub = ids(lambda c: c["alineaciones"]["estado"] != "publicada")
        if no_pub:
            estados = {}
            for k in no_pub:
                e_ = contexts[k]["alineaciones"]["estado"]
                estados[e_] = estados.get(e_, 0) + 1
            inc.append({"tipo": "alineaciones_no_publicadas", "cantidad": len(no_pub), "por_estado": estados, "ejemplos": no_pub[:3]})
    cnt = lambda key, vals: {v: sum(1 for r in rows if r["analitica"][key] == v) for v in vals}
    return {"estado": "CON_LIMITACIONES" if inc else "SIN_LIMITACIONES", "incidencias": inc,
            "datos": cnt("datos", ("suficientes", "parciales", "insuficientes", "sin_datos", "sin_extractor")), "estimador": cnt("estimador", ("calculable", "datos_insuficientes", "no_implementado")),
            "modelo_validacion": MODEL_VALIDATION["nivel"]}


# ── C. precios ──
def pricing_report(rows):
    cnt = {e: sum(1 for r in rows if r["precio"]["estado"] == e) for e in ("real_verificada", "otra_fuente", "no_verificable", "sin_precio", "no_consultado")}
    aptas = sum(1 for r in rows if r["precio"]["cumple_requisitos_de_precio"])
    real = [r for r in rows if r["precio"]["estado"] == "real_verificada"]
    inc = []
    if not real:
        inc.append({"tipo": "sin_precios_reales_verificados", "cantidad": len(rows), "ejemplos": []})
    fuera = [r for r in real if r["precio"]["cumple_limite"] is False]
    if fuera:
        inc.append({"tipo": f"precio_real_sobre_{MAX_LEG_ODDS}", "cantidad": len(fuera), "ejemplos": [r["entry_id"] for r in fuera[:3]]})
    return {"estado": "SIN_PRECIOS_REALES" if not real else "PRECIOS_REALES_PARCIALES", "limite_individual": MAX_LEG_ODDS, "incidencias": inc, "por_estado": cnt, "filas_con_precio_que_cumple_requisitos": aptas, "nota": "cumplir los requisitos de PRECIO no equivale a estar preparado para apostar (ver preparacion_para_apostar)"}


# ── Rutas que generan rankings, candidatos, combinadas o libros (todas deben ejecutar la cobertura o declarar que NO la evalúan) ──
GENERATION_ROUTES = {
    ".claude/skills/seleccion-final-picks/scripts/tickets.py": {"produce": "tickets.json, tickets.md, candidatos_estadisticos.csv, snapshots.jsonl", "marker": "market_coverage.run_coverage",
                                                                "control": "ejecuta run_coverage; escribe investigacion_certificada y preparacion_para_apostar; avisa en cada ranking"},
    "runs/2026-10-14/ligas/build_dataset.py": {"produce": "dataset.json, dataset_meta.json, market_coverage.*", "marker": "MC.run_coverage", "control": "ejecuta run_coverage sobre los partidos del catálogo"},
    "runs/2026-10-14/ligas/build_xlsx.py": {"produce": "ligas-14-oct[-PROVISIONAL].xlsx", "marker": "_certification()", "control": "nombre definitivo solo con certificación vigente del mismo conjunto"},
    ".claude/skills/seleccion-final-picks/scripts/catalog_rankings.py": {"produce": "ranking_catalogo.json/.md", "marker": "agent_review.build_units", "control": "construye el catálogo con la cobertura (build_units ejecuta run_coverage), exige precio y cuota ≤ 2.10 por pata, topes de riesgo/exposición y estado de agentes; cada combinada lleva su preparación para apostar"},
    ".claude/skills/seleccion-final-picks/scripts/custom_check.py": {"produce": "user_tickets_eval.json/.md", "marker": "NO CERTIFICADO COMO EXHAUSTIVO", "control": "declara que NO evalúa cobertura ni preparación"},
}
# Menciona palabras como «ranking»/«combinada» pero no genera candidatos ni libros: motivo explícito.
NON_GENERATING = {
    ".claude/skills/seleccion-final-picks/scripts/coverage_report.py": "puerta de Nivel 1 (evaluación de partidos); su veredicto aclara que no certifica la investigación de mercados",
    ".claude/skills/seleccion-final-picks/scripts/market_coverage.py": "define los controles",
    ".claude/skills/seleccion-final-picks/scripts/live_prob.py": "imprime la probabilidad en vivo de tickets ya apostados; no genera candidatos",
    ".claude/skills/seleccion-final-picks/scripts/rotation_prior.py": "lee los partidos de tickets.json para calcular rotación; no genera candidatos",
    ".claude/skills/seleccion-final-picks/scripts/seguimiento.py": "liquida tickets ya apostados; «provisional» se refiere a un marcador en juego",
    ".claude/skills/seleccion-final-picks/scripts/agent_review.py": "genera paquetes y valida los informes de los agentes (contrato cerrado); no genera candidatos",
}


# ── PREPARACIÓN PARA APOSTAR (independiente de la certificación de investigación) ──
REQUISITOS_APUESTA = ("investigacion_resuelta", "precio_real_verificado", "cuota_dentro_del_limite", "datos_suficientes", "estimador_propio_disponible", "modelo_validado", "revision_agentes_completa")


def _readiness(checks):
    unmet = [k for k, v in checks.items() if not v]
    return {"estado": "APTA" if not unmet else "NO_APTA", "requisitos": checks, "incumplidos": unmet,
            "nota": "independiente de la certificación de la investigación: una investigación completa no vuelve apta una selección"}


def row_readiness(row, revision_ok=False):
    """Una fila (partido × entrada) está preparada para apostar solo si CUMPLE A LA VEZ todos los requisitos; el modelo no validado impide recomendarla."""
    p, a = row["precio"], row["analitica"]
    return _readiness({"investigacion_resuelta": bool(row["investigacion"]["resuelta"]),
                       "precio_real_verificado": p["estado"] == "real_verificada" and bool((p.get("registro") or {}).get("source")),
                       "cuota_dentro_del_limite": p.get("cumple_limite") is True,
                       "datos_suficientes": a["datos"] == "suficientes",
                       "estimador_propio_disponible": a["estimador"] == "calculable",
                       "modelo_validado": model_validated(mc.BY_ID.get(row["entry_id"], {})),
                       "revision_agentes_completa": bool(revision_ok)})


def ticket_readiness(tk, investigacion_certificada=False, revision_ok=False):
    """Preparación de un borrador: todas sus patas con precio REAL comunicado (no promedio), cada cuota ≤ límite, datos suficientes por equipo, modelo validado e investigación certificada."""
    legs = [l for it in tk.get("items", []) for l in it["patas"]]
    return _readiness({"investigacion_resuelta": bool(investigacion_certificada),
                       "precio_real_verificado": bool(legs) and all(l.get("cuota_tipo") == "manual_usuario" for l in legs),
                       "cuota_dentro_del_limite": bool(legs) and all((l.get("cuota_media") or 99) <= MAX_LEG_ODDS for l in legs),
                       "datos_suficientes": bool(legs) and all(min(l.get("n") or [0, 0]) >= MIN_N for l in legs),
                       "estimador_propio_disponible": bool(legs) and all(l.get("p_central") is not None or l.get("apoyo_conservador") is not None for l in legs),
                       "modelo_validado": MODEL_VALIDATION["nivel"] == "suficiente", "revision_agentes_completa": bool(revision_ok)})


def betting_summary(rows):
    unmet = {k: sum(1 for r in rows if k in r["preparacion_para_apostar"]["incumplidos"]) for k in REQUISITOS_APUESTA}
    n = sum(1 for r in rows if r["preparacion_para_apostar"]["estado"] == "APTA")
    return {"estado": "NINGUNA_FILA_APTA" if n == 0 else "FILAS_APTAS_PARCIALES", "filas_aptas": n, "filas": len(rows), "requisitos_incumplidos": unmet, "modelo_validacion": MODEL_VALIDATION["nivel"],
            "nota": "estado independiente de investigacion_certificada: con el modelo sin validar no hay filas aptas aunque la investigación esté certificada"}


# ── resumen, certificación y avisos ──
def certified(summary):
    """True = investigación exhaustiva (nada más): no mira precios, datos suficientes ni validación del modelo."""
    return bool(summary.get("modo") == "enforce" and summary.get("investigacion", {}).get("estado") == "INVESTIGACION_COMPLETA")


def summarize(rows, authorized_ids, errors=(), catalog=None, channels=None, modo="enforce", contexts=None, revision=None):
    catalog = mc.CATALOG if catalog is None else catalog
    a = investigation_gate(rows, authorized_ids, catalog, channels)
    authorized_ids = list(authorized_ids)
    s = {"modo": modo, "partidos_ids": authorized_ids, "partidos_autorizados": len(authorized_ids), "entradas_catalogo": len(catalog), "filas": len(rows), "investigacion": a, "analitica": analytic_report(rows, contexts), "precios": pricing_report(rows), "contexto_partidos": contexts or {}, "revision_agentes": _revision_block(revision),
         "errores_proveedores": list(errors)}
    s["preparacion_para_apostar"] = betting_summary(rows)
    _stamp_certification(s)
    return s


def _revision_block(rev):
    """Estado de la revisión por agentes (agent_review.review_gate): COMPLETA | INCOMPLETA | NO_EJECUTADA. Es un requisito de la preparación para apostar, NO de la certificación de la investigación."""
    return {"estado": (rev or {}).get("estado", "NO_EJECUTADA"), "incidencias": len((rev or {}).get("incidencias", [])), "unidades_esperadas": (rev or {}).get("unidades_esperadas")}


def _stamp_certification(s):
    """`investigacion_certificada` = SOLO exhaustividad de la investigación. `certificado_investigacion` y (en tickets.json) `certificado` son alias antiguos con el mismo valor."""
    s["investigacion_certificada"] = certified(s)
    s["certificado_investigacion"] = s["investigacion_certificada"]
    s["semantica"] = SEMANTICS
    s["aviso"] = banner(s)


SEMANTICS = {"investigacion_certificada": "SOLO significa que cada combinación requerida partido × mercado × canal tiene un registro resuelto con evidencia (modo enforce). NO aprueba apostar.",
             "preparacion_para_apostar": "estado independiente: exige precio real verificado, cuota ≤ límite, datos suficientes, estimador propio y modelo validado; el modelo no validado impide recomendar."}


def omitted_summary():
    s = {"modo": "omitida", "certificado_investigacion": False, "preparacion_para_apostar": {"estado": "NO_EVALUADA"}, "revision_agentes": {"estado": "NO_EVALUADA"}, "investigacion": {"estado": "NO_EVALUADA", "incidencias": [{"tipo": "cobertura_omitida_por_el_operador", "cantidad": 1, "ejemplos": []}]},
         "analitica": {"estado": "NO_EVALUADA"}, "precios": {"estado": "NO_EVALUADA"}}
    _stamp_certification(s)
    return s


def banner(s):
    """Aviso para tickets/rankings/entregables: las tres dimensiones por separado, qué significa la certificación y el estado de preparación para apostar."""
    if s.get("modo") == "omitida":
        return "NO VALIDADO — cobertura de mercados OMITIDA por el operador: esta salida no puede presentarse como exhaustiva ni definitiva"
    a, b, c = s["investigacion"], s["analitica"], s["precios"]
    pend = sum(i["cantidad"] for i in a["incidencias"])
    inv = ("INVESTIGACIÓN CERTIFICADA (solo exhaustividad de la investigación; no es una aprobación para apostar)" if s["investigacion_certificada"]
           else f"INVESTIGACIÓN NO CERTIFICADA COMO EXHAUSTIVA — {a['estado']} ({pend} incidencias)")
    bet = s["preparacion_para_apostar"]
    return " · ".join([inv, f"analítica: {b['estado']}", f"precios: {c['estado']}", f"revisión de agentes: {s['revision_agentes']['estado']}", f"preparación para apostar: {'NO APTA' if bet['estado'] == 'NINGUNA_FILA_APTA' else bet['estado']} ({bet['filas_aptas']} filas aptas)"])


def render_md(s):
    if s.get("modo") == "omitida":
        return f"# Cobertura de mercados — OMITIDA\n\n{s['aviso']}\n"
    a, b, c = s["investigacion"], s["analitica"], s["precios"]
    L = [f"# Cobertura de mercados — tres controles", "", f"> {s['aviso']}", "",
         f"Partidos autorizados: {s['partidos_autorizados']} · entradas del catálogo (mercado × selección × línea × alcance, GENERALES, no por partido): {s['entradas_catalogo']} · "
         f"canales: {', '.join(a['canales'])} · combinaciones requeridas = partidos × entradas × canales = {a['combinaciones_requeridas']} · filas (partido × entrada) = {s['filas']}", "",
         f"## A. Investigación — {a['estado']}", ""]
    L += [f"- {i['tipo']}: {i['cantidad']} {i.get('ejemplos') or ''}" for i in a["incidencias"]] or ["- sin incidencias"]
    L += ["", "| Canal | Requeridas | Encontrado | Consultado, no encontrado | La fuente no lo ofrece | No verificable | Pendiente | Cobertura (informativa) |", "|---|---|---|---|---|---|---|---|"]
    L += [f"| {k} | {v['requeridas']} | {v['encontrado']} | {v['consultado_no_encontrado']} | {v['fuente_no_ofrece']} | {v['no_verificable']} | {v['pendiente']} | {v['cobertura_informativa']} |" for k, v in a["por_canal"].items()]
    L += ["", f"## B. Analítica — {b['estado']} (modelo: validación {b['modelo_validacion']})", ""]
    L += [f"- {i['tipo']}: {i['cantidad']} {i.get('ejemplos') or i.get('por_familia') or ''}" for i in b["incidencias"]] or ["- sin limitaciones"]
    L += ["", f"Datos: {b['datos']} · Estimador: {b['estimador']}", "", f"## C. Precios — {c['estado']} (límite individual {c['limite_individual']})", ""]
    L += [f"- {i['tipo']}: {i['cantidad']} {i.get('ejemplos') or ''}" for i in c["incidencias"]] or ["- sin incidencias"]
    L += ["", f"Por estado: {c['por_estado']} · filas con precio que cumple los requisitos de precio: {c['filas_con_precio_que_cumple_requisitos']}"]
    d = s["preparacion_para_apostar"]
    L += ["", f"## D. Preparación para apostar — {d['estado']} (independiente de la certificación)", "", f"- filas aptas: {d['filas_aptas']} de {d['filas']} · modelo: validación {d['modelo_validacion']}",
          "- requisitos incumplidos (filas): " + ", ".join(f"{k}: {v}" for k, v in d["requisitos_incumplidos"].items()), f"- {d['nota']}"]
    if s["errores_proveedores"]:
        L += ["", "## Proveedores de precio con error (no detienen el análisis; sus combinaciones quedan «pendiente»)"] + [f"- {e['provider']}: {e['error']}" for e in s["errores_proveedores"]]
    return "\n".join(L) + "\n"


def authorized_from_run(run):
    inv = common.read_json(os.path.join(run, "inventory.json"))["matches"]
    mx = common.read_json(os.path.join(run, "matrix.json"), {"matches": {}})["matches"]
    return [m for m in inv if m.get("analysis_required") and m["match_id"] in mx]


def default_providers(run, inv, mx, price_files=(), capture=None, aggregator=True):
    """Proveedores de precio por defecto de un run (todos OPCIONALES e independientes): agregador apifootball desde la caché cruda (o, sin ella, lo guardado en matrix.json),
    football-data (Bet365, solo donde esa fuente cubre el partido), capturas de la persona usuaria (si se indican) y archivos de precios comunicados."""
    provs = []
    if aggregator:
        odds = ps.ApifootballOddsProvider(run)
        provs.append(odds if odds.queries else ps.MatrixAggregatorProvider(mx))
        provs.append(ps.FootballDataOddsProvider({m["match_id"]: m for m in inv}))
    if capture:
        provs.append(ps.UserCaptureProvider(*capture))
    provs += [ps.ManualCsvProvider(p) for p in price_files]
    return provs


def run_coverage(run, match_ids=None, price_files=(), out_dir=None, aggregator=True, write=True, capture=None, return_rows=False):
    """Punto de entrada ÚNICO que ejecutan CLI, tickets.py y los scripts de ligas: construye los registros, evalúa los tres controles y (opcional) escribe los archivos.
    `capture` = (partidos_usuario.json, ids.json) para registrar como precios las capturas de la persona usuaria."""
    inv = common.read_json(os.path.join(run, "inventory.json"))["matches"]
    mx = common.read_json(os.path.join(run, "matrix.json"), {"matches": {}})["matches"]
    if match_ids is not None:
        by = {m["match_id"]: m for m in inv}
        unknown = [i for i in match_ids if i not in by]
        if unknown:
            raise ValueError(f"ids fuera del inventario: {unknown}")
        matches = [by[i] for i in match_ids]
    else:
        matches = authorized_from_run(run)
    providers = default_providers(run, inv, mx, price_files, capture, aggregator)
    contexts = build_contexts(run, matches, inv)
    import agent_review
    rev = agent_review.load_gate(run)
    ids_ = [m["match_id"] for m in matches]
    # la revisión solo vale si cubre ESTOS partidos (un resultado de otro conjunto no habilita nada)
    rev_ok = bool(rev and rev.get("estado") == "COMPLETA" and set(rev.get("partidos_ids", [])) == set(ids_))
    if rev and rev.get("estado") == "COMPLETA" and not rev_ok:
        rev = dict(rev, estado="INCOMPLETA", incidencias=list(rev.get("incidencias", [])) + [{"tipo": "revision_de_otro_conjunto_de_partidos"}])
    rows, errors = build_records(matches, mx, providers, contexts=contexts, revision_ok=rev_ok)
    s = summarize(rows, ids_, errors, channels=[CANAL_DATOS] + [p.name for p in providers], contexts=contexts, revision=rev)
    if write:
        out = out_dir or run
        os.makedirs(out, exist_ok=True)
        common.write_json_atomic(os.path.join(out, "market_coverage.json"), s)
        with open(os.path.join(out, "market_coverage_rows.jsonl"), "w", encoding="utf-8") as fh:
            for r in rows:
                fh.write(json.dumps(r, ensure_ascii=False) + "\n")
        with open(os.path.join(out, "market_coverage.md"), "w", encoding="utf-8") as fh:
            fh.write(render_md(s))
    return (s, rows) if return_rows else s


FAMILIES_TEMPLATE = {"corners": ("corners",), "tarjetas": ("tarjetas",), "goles_equipo": ("goles por equipo",), "primera_parte": ("1.ª parte resultado", "1.ª parte goles")}


def write_price_template(rows, matches, path, families=("corners", "tarjetas", "goles_equipo")):
    """CSV para que la persona usuaria pegue los precios REALES de su casa de los mercados que ninguna fuente de precios publica (columna `cuota` vacía; se carga con --prices)."""
    import csv
    by = {m["match_id"]: m for m in matches}
    mk = {x for f in families for x in FAMILIES_TEMPLATE[f]}
    n = 0
    with open(path, "w", encoding="utf-8", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["home", "away", "seleccion", "cuota", "casa", "mercado"])
        for r in rows:
            if r["market"] in mk and r["precio"]["estado"] != "real_verificada":
                e = mc.BY_ID[r["entry_id"]]
                m = by[r["match_id"]]
                w.writerow([m["home_team"], m["away_team"], mc.entry_label(e, m["home_team"], m["away_team"]), "", "", r["market"]])
                n += 1
    return n


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--run", required=True)
    ap.add_argument("--matches", help="ids.json ({etiqueta: match_id}) o lista separada por comas: delimita los partidos AUTORIZADOS (no los mercados)")
    ap.add_argument("--prices", action="append", default=[], help="CSV/JSON de precios comunicados (home,away,seleccion,cuota[,casa]); opcional y repetible")
    ap.add_argument("--no-aggregator", action="store_true", help="no usar los promedios de agregador de matrix.json")
    ap.add_argument("--out-dir", help="carpeta de salida (por defecto, la del run)")
    ap.add_argument("--capture", help="partidos_usuario.json con las capturas de la persona usuaria (requiere --capture-ids)")
    ap.add_argument("--capture-ids", help="ids.json {local|visitante: match_id} de las capturas")
    ap.add_argument("--price-template", help="escribe un CSV de precios por rellenar (córners, tarjetas, goles por equipo) en esta ruta")
    ap.add_argument("--template-families", default="corners,tarjetas,goles_equipo", help="familias de la plantilla: " + ",".join(FAMILIES_TEMPLATE))
    a = ap.parse_args(argv)
    ids = None
    if a.matches:
        ids = list(json.load(open(a.matches)).values()) if os.path.exists(a.matches) else a.matches.split(",")
    try:
        s, rows_ = run_coverage(a.run, ids, a.prices, a.out_dir, aggregator=not a.no_aggregator, capture=(a.capture, a.capture_ids) if a.capture else None, return_rows=True)
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    if a.price_template:
        inv = common.read_json(os.path.join(a.run, "inventory.json"))["matches"]
        by = {m["match_id"]: m for m in inv}
        n = write_price_template(rows_, [by[i] for i in s["partidos_ids"]], a.price_template, tuple(a.template_families.split(",")))
        print(f"plantilla de precios: {n} filas -> {a.price_template}")
    print("A. INVESTIGACIÓN:", s["investigacion"]["estado"], "|", len(s["investigacion"]["incidencias"]), "tipos de incidencia")
    print("B. ANALÍTICA:", s["analitica"]["estado"], "| C. PRECIOS:", s["precios"]["estado"], "| investigacion_certificada:", s["investigacion_certificada"],
          "| preparación para apostar:", s["preparacion_para_apostar"]["estado"])
    return 0


if __name__ == "__main__":
    sys.exit(main())
