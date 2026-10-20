#!/usr/bin/env python3
"""CONTRATO DE REVISIÓN POR AGENTES (Fase 5): paquetes de trabajo deterministas, informes en JSON con campos CERRADOS y un validador de completitud.

Problema que resuelve: la revisión anterior devolvía texto libre sobre las patas del catálogo y el resto (`mercados_extra`) no entraba en ninguna comparación. Aquí:
- La UNIDAD de revisión es (partido, grupo de mercado). Los grupos salen del catálogo (`market_catalog.py`: resultado, doble oportunidad, hándicaps, goles, goles por equipo, córners,
  tarjetas, remates…). Cada unidad lista TODAS sus entradas (líneas) con los hechos deterministas del paquete: estados de investigación por canal, precio, datos, estimador propio,
  probabilidad del modelo (si existe) y nivel de validación. Un veredicto de unidad vale para todas sus entradas salvo `excepciones` por entry_id.
- Cada rol responde con campos de LISTA CERRADA (enums) + una nota corta (≤ NOTE_MAX) + evidencia obligatoria. Cualquier campo no previsto es inválido: no hay texto libre.
- `validate_report` comprueba esquema, cobertura (toda unidad esperada, sin duplicados) y COHERENCIA con los hechos del paquete (un agente no puede afirmar un precio real, un
  estimador o datos que el paquete no tiene). El auditor debe cubrir una muestra mínima definida (`audit_sample_required`).
- `review_gate` / `consolidate`: estado COMPLETA | INCOMPLETA | NO_EJECUTADA de la revisión y conflictos entre agentes. market_coverage.py lo carga: SIN revisión completa
  ningún resultado cumple el requisito `revision_agentes_completa` de la preparación para apostar.
Uso:  agent_review.py packages --run runs/<fecha> [--matches ids.json] [--only m-…,m-…]   ·   validate --run … --role R --file informe.json   ·   gate --run …   ·   contract"""
import argparse
import glob
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common  # noqa: E402
import market_catalog as mc  # noqa: E402

CONTRACT_VERSION = 1
ROLES = ("verificador", "deportivo", "cuantitativo", "auditor")
NOTE_MAX = 200
GROUPS = sorted({e["market"] for e in mc.CATALOG})
EVIDENCE_PREFIXES = ("paquete:", "apif_query:", "archivo:", "web:", "cache:")

ENUMS = {
    "deportivo": {"solidez": ("ALTA", "MEDIA", "BAJA", "NO_EVALUABLE"),
                  "factor_principal": ("forma", "localia", "rotacion", "calendario_descanso", "bajas_alineaciones", "arbitro", "estilo_ritmo", "muestra_insuficiente", "contexto_competicion"),
                  "direccion_favorable": ("over", "under", "local", "empate", "visitante", "sin_sesgo"),
                  "escenario_perdida": ("goleada_local", "goleada_visitante", "partido_cerrado", "partido_abierto", "rotacion_inesperada", "tarjetas_atipicas", "penal_o_expulsion", "sin_escenario_definido")},
    "cuantitativo": {"consistencia_modelo": ("coherente", "discrepa_del_mercado", "datos_insuficientes", "sin_precio_para_contrastar", "defecto_del_modelo", "sin_estimador"),
                     "riesgo_correlacion": ("ninguno", "misma_direccion", "mismo_partido", "mismo_equipo_en_otras_patas"),
                     "validacion_aplicable": ("no_validado", "parcial", "validado")},
    "verificador": {"disponibilidad": ("verificada_en_fuente", "no_encontrada", "no_ofrecida", "no_verificable"),
                    "precio": ("real_verificado", "comunicado_usuario", "referencia_agregador", "sin_precio")},
    "auditor": {"objecion": ("ninguna", "muestra_debil", "brecha_muestra_mercado", "rotacion_no_cuantificada", "fuente_unica", "dato_defectuoso", "correlacion", "cuota_no_ejecutable", "estimador_sin_validar"),
                "severidad": ("baja", "media", "alta"), "recomendacion": ("mantener", "degradar", "descartar_de_rankings", "verificar_manualmente")},
}
LIST_ENUMS = {"verificador": {"discrepancias": ("ninguna", "calendario", "hora", "identidad_partido", "precio_anomalo", "linea_distinta", "mercado_mal_etiquetado", "paquete_desactualizado_vs_fuente")}}
LIST_STR = {"verificador": ("fuentes_consultadas",)}
EXCEPTION_FIELD = {"deportivo": "solidez", "cuantitativo": "consistencia_modelo", "verificador": "disponibilidad", "auditor": "objecion"}
# Solo el auditor: errores de OTROS agentes que detectó al contrastar con el paquete o la fuente (campo opcional; una objeción es un hallazgo, no un fallo de completitud).
OBJECTION_FIELD = "objeciones_a_agentes"
OBJECTION_ROLES = tuple(r for r in ROLES if r != "auditor")
OBJECTION_PROBLEMS = ("valor_contradice_paquete", "valor_contradice_fuente", "afirmacion_sin_evidencia", "omision", "dato_citado_incorrecto")
OPTIONAL_FIELDS = {"auditor": (OBJECTION_FIELD,)}
FIELDS = {r: tuple(ENUMS[r]) + tuple(LIST_ENUMS.get(r, {})) + LIST_STR.get(r, ()) + ("nota", "excepciones", "evidencia") + OPTIONAL_FIELDS.get(r, ()) for r in ROLES}


def unit_id(match_id, grupo):
    return f"{match_id}|{grupo}"


# ── paquetes ──
def _model_probs_by_match(run, matches, mx, samples, raw=None):
    """p_modelo por (match_id, entry_id): solo para entradas con estimador y datos. Reutiliza los modelos de la Fase 4 (no usa cuotas).
    La probabilidad pasa por la recalibración fuera de tiempo (`model_calibration.apply`) solo en los grupos donde el backtest la validó; `raw` (dict opcional) recibe la probabilidad sin recalibrar."""
    import count_model
    import leg_model
    import model_calibration
    import market_coverage as cov
    keys = cov._probe_model_keys()
    by_comp = {}
    for m in matches:
        for side in ("local", "visitante"):
            for r in ((mx.get(m["match_id"]) or {}).get("form") or {}).get(side, []):
                if r.get("misma_competicion"):
                    by_comp.setdefault(m["competition"], []).append(r)
    out = {}
    inv_all = matches
    for m in matches:
        ev = mx.get(m["match_id"]) or {}
        f = ev.get("form") or {}
        if len(f.get("local", [])) < 6 or len(f.get("visitante", [])) < 6 or not by_comp.get(m["competition"]):
            continue
        mu, adv = leg_model.league_means([by_comp[m["competition"]]])
        if not mu:
            continue
        gp = leg_model.model_probs(f["local"], f["visitante"], mu, adv, share=leg_model.half_share(f["local"], f["visitante"]))
        cp = {}
        lid = cov.league_of(m, inv_all)
        filas = (samples.get(lid) or {}).get("filas") or []
        for name, field, key, tl, ml in (("corners", "corners", "corners", count_model.CORNER_TOTAL, count_model.CORNER_TEAM), ("cards", "cards_pts", "tarjetas", count_model.CARD_TOTAL, count_model.CARD_TEAM),
                                         ("sot", "sot", "sot", count_model.SOT_TOTAL, count_model.SOT_TEAM), ("shots", "shots", "shots", count_model.SHOTS_TOTAL, count_model.SHOTS_TEAM)):
            if name in ("sot", "shots"):      # las muestras de liga no traen remates: la media y la dispersión salen de las filas de forma de la MISMA competición (todos los equipos del día), ya orientadas local-visitante
                comp_rows = [r for r in by_comp.get(m["competition"], []) if r.get(field) and None not in r[field]]
                orient_h = [(r[field][0], r[field][1]) if r.get("venue") == "local" else (r[field][1], r[field][0]) for r in comp_rows]
                st = count_model.league_stats(orient_h)
            else:
                st = count_model.league_stats([tuple(r[key]) if r.get(key) and None not in r[key] else None for r in filas])
            def orient(rows):
                o = []
                for r in rows:
                    t = r.get(field) if field in ("corners", "sot", "shots") else r.get("cards_pts")
                    if t and None not in t:
                        home = r.get("venue") == "local"
                        o.append({"venue": r.get("venue"), "own": t[0] if home else t[1], "opp": t[1] if home else t[0]})
                return o
            hh, aa = orient(f["local"]), orient(f["visitante"])
            if st and len(hh) >= 6 and len(aa) >= 6:
                cp.update(count_model.model_probs(name, hh, aa, st, tl, ml))
        for e in mc.CATALOG:
            k = cov.model_key(e, keys)
            if k is None:
                continue
            p = gp.get(k, cp.get(k))
            if p is None:
                continue
            pc, _grp, aplicada = model_calibration.apply(k, p)
            out[(m["match_id"], e["id"])] = round(1 - pc if e["direction"] in ("under", "no") else pc, 4)        # «no»/«menos» son el complemento de la clave del modelo
            if raw is not None and aplicada:
                raw[(m["match_id"], e["id"])] = round(1 - p if e["direction"] in ("under", "no") else p, 4)
    return out


def build_units(run, match_ids=None, capture=None):
    """Unidades (partido × grupo) con los hechos deterministas de cada entrada. Devuelve (unidades, resumen_de_cobertura)."""
    import market_coverage as cov
    s, rows = cov.run_coverage(run, match_ids, write=False, capture=capture, return_rows=True)
    inv = common.read_json(os.path.join(run, "inventory.json"))["matches"]
    mx = common.read_json(os.path.join(run, "matrix.json"), {"matches": {}})["matches"]
    by = {m["match_id"]: m for m in inv}
    matches = [by[i] for i in s["partidos_ids"]]
    samples = cov.load_league_samples(run)
    raw = {}
    pm = _model_probs_by_match(run, matches, mx, samples, raw)
    units = {}
    for r in rows:
        e = mc.BY_ID[r["entry_id"]]
        u = units.setdefault(unit_id(r["match_id"], e["market"]), {"unit_id": unit_id(r["match_id"], e["market"]), "match_id": r["match_id"], "partido": r["partido"], "grupo": e["market"],
                                                                      "hora_utc": by[r["match_id"]]["normalized_datetime_utc"], "liga": (s["contexto_partidos"].get(r["match_id"]) or {}).get("liga_id"),
                                                                      "contexto": s["contexto_partidos"].get(r["match_id"]), "entradas": []})
        rec = r["precio"].get("registro") or {}
        u["entradas"].append({"id": e["id"], "linea": e["line"], "direccion": e["direction"], "alcance": e["scope"],
                              "investigacion": {c["canal"]: c["resultado"] for c in r["investigacion"]["canales"]},
                              "precio": {"estado": r["precio"]["estado"], "cuota": rec.get("odds"), "fuente": rec.get("source"), "tipo": rec.get("source_type"), "cumple_limite_2_10": r["precio"]["cumple_limite"],
                                        "observado_utc": rec.get("observed_utc"), "n_casas": rec.get("n_books"),
                                        # capas separadas (17-oct): referencia de agregador (independiente de cualquier casa), captura de la persona usuaria (opcional) y P del mercado sin margen
                                        "cuota_referencia": (r["precio"].get("referencia") or {}).get("odds"), "fuente_referencia": (r["precio"].get("referencia") or {}).get("source"),
                                        "observado_referencia_utc": (r["precio"].get("referencia") or {}).get("observed_utc"), "n_casas_referencia": (r["precio"].get("referencia") or {}).get("n_books"),
                                        "cuota_usuario": (r["precio"].get("usuario") or {}).get("odds"), "p_mercado": r["precio"].get("p_mercado")},
                              "datos": r["analitica"]["datos"], "estimador": r["analitica"]["estimador"], "validacion": r["analitica"]["validacion"], "p_modelo": pm.get((r["match_id"], e["id"]))})
        if (r["match_id"], e["id"]) in raw:
            u["entradas"][-1]["p_modelo_bruta"] = raw[(r["match_id"], e["id"])]          # solo cuando la recalibración cambió la probabilidad
    for u in units.values():
        es = u["entradas"]
        for x in es:
            # coherencia con la realidad: «estimador calculable» sin probabilidad calculada (p. ej. sin media de liga para ese torneo) NO es calculable (hallazgo de los agentes, Fase 7)
            if x["estimador"] == "calculable" and x["p_modelo"] is None:
                x["estimador"] = "sin_probabilidad_calculada"
        cnt = lambda f: {k: sum(1 for x in es if f(x) == k) for k in sorted({f(x) for x in es})}
        u["resumen"] = {"entradas": len(es), "precio": cnt(lambda x: x["precio"]["estado"]), "datos": cnt(lambda x: x["datos"]), "estimador": cnt(lambda x: x["estimador"]),
                        "validacion": cnt(lambda x: x["validacion"] or "sin_estimador"), "investigacion": cnt(lambda x: "resuelta" if all(v != "pendiente" for v in x["investigacion"].values()) else "pendiente")}
    return sorted(units.values(), key=lambda u: u["unit_id"]), s


def contract_text(role):
    L = [f"# Contrato de salida — {role} (versión {CONTRACT_VERSION})", "",
         "Devuelve UN archivo JSON: {\"agente\": \"%s\", \"version_contrato\": %d, \"run\": \"<run>\", \"unidades\": [ … ], \"limitaciones\": [\"…\"]}." % (role, CONTRACT_VERSION),
         f"Una entrada en `unidades` por CADA unit_id del paquete (partido|grupo). Campos permitidos por unidad (cualquier otro es inválido): {', '.join(FIELDS[role])}, unit_id.", ""]
    for k, v in ENUMS[role].items():
        L.append(f"- `{k}`: una de {list(v)}")
    for k, v in LIST_ENUMS.get(role, {}).items():
        L.append(f"- `{k}`: lista con valores de {list(v)}")
    for k in LIST_STR.get(role, ()):
        L.append(f"- `{k}`: lista de textos cortos (fuentes realmente consultadas)")
    L += [f"- `nota`: texto ≤ {NOTE_MAX} caracteres (puede ir vacío)", "- `excepciones`: lista de {\"entry_id\": <`id` de UNA LÍNEA (entrada) de la unidad, no el id de la unidad>, \"%s\": <valor>} cuando esa línea difiere del veredicto de la unidad" % EXCEPTION_FIELD[role],
          f"- `evidencia`: lista NO vacía de referencias que empiecen por {list(EVIDENCE_PREFIXES)} (p. ej. `paquete:{'<unit_id>'}`, `apif_query:get_events match_id=…`)", "",
          "Reglas de coherencia (las comprueba el validador): no afirmes un precio real, un estimador, datos suficientes ni una validación que el paquete no tenga; si dudas, usa el valor conservador."]
    if role == "auditor":
        L.append(f"- Muestra mínima del auditor: {AUDIT_SAMPLE_TEXT}")
        L.append(f"- `{OBJECTION_FIELD}` (OPCIONAL; omítelo o déjalo vacío si no hay): lista de {{\"entry_id\": <id de línea de la unidad o null si afecta a toda la unidad>, \"agente\": una de {list(OBJECTION_ROLES)}, "
                 f"\"campo\": <campo del contrato de ese agente>, \"problema\": uno de {list(OBJECTION_PROBLEMS)}}}. Úsalo cuando el valor de otro agente contradice el paquete o la fuente; la explicación va en `nota` y la prueba en `evidencia`.")
    return "\n".join(L) + "\n"


AUDIT_SAMPLE_FRACTION = 0.20
AUDIT_SAMPLE_MIN = 10
AUDIT_SAMPLE_TEXT = (f"TODAS las unidades que otro agente marque con solidez BAJA, discrepancia o mercado no verificable, más al menos max({AUDIT_SAMPLE_MIN}, {int(AUDIT_SAMPLE_FRACTION * 100)} % de las unidades restantes) "
                     "con al menos una unidad de cada grupo de mercado presente (política declarada, no un hecho estadístico).")


# ── validación ──
def _err(errs, uid, campo, motivo):
    errs.append({"unit_id": uid, "campo": campo, "motivo": motivo})


def _coherence(role, u, pack):
    """Comprobaciones contra los hechos del paquete: un agente no puede afirmar lo que el paquete no tiene."""
    errs = []
    r = pack["resumen"]
    uid = u["unit_id"]
    if role == "verificador":
        tipos = {e["precio"].get("tipo") for e in pack["entradas"] if e["precio"]["estado"] == "real_verificada"}
        if u.get("precio") == "real_verificado" and "casa" not in tipos:
            _err(errs, uid, "precio", "afirma precio real verificado de una casa y el paquete no tiene ninguno")
        if u.get("precio") == "comunicado_usuario" and "usuario" not in tipos:
            _err(errs, uid, "precio", "afirma precio comunicado por la persona usuaria y el paquete no tiene ninguno")
        if u.get("precio") == "referencia_agregador" and not (r["precio"].get("otra_fuente", 0) or r["precio"].get("real_verificada", 0) or r["precio"].get("no_verificable", 0)):
            _err(errs, uid, "precio", "afirma referencia de agregador y el paquete no tiene precio de ninguna fuente")
        if u.get("disponibilidad") == "verificada_en_fuente" and not any(v == "encontrado" for e in pack["entradas"] for c, v in e["investigacion"].items() if c != "datos_deportivos"):
            _err(errs, uid, "disponibilidad", "afirma mercado verificado en una fuente y ningún canal de precios lo encontró")
    if role == "cuantitativo":
        if u.get("consistencia_modelo") == "sin_estimador" and r["estimador"].get("calculable", 0):
            _err(errs, uid, "consistencia_modelo", "declara «sin_estimador» pero el paquete tiene estimador calculable")
        if u.get("consistencia_modelo") in ("coherente", "discrepa_del_mercado", "sin_precio_para_contrastar") and not r["estimador"].get("calculable", 0):
            _err(errs, uid, "consistencia_modelo", "juzga el modelo y el paquete no tiene ninguna entrada calculable")
        niveles = set(r["validacion"])
        if u.get("validacion_aplicable") == "validado" and niveles - {"suficiente"}:
            _err(errs, uid, "validacion_aplicable", "afirma modelo validado y el paquete indica otro nivel")
    if role == "deportivo":
        sin_datos = all(k in ("insuficientes", "sin_datos", "sin_extractor") for k in r["datos"])
        if u.get("solidez") == "ALTA" and sin_datos:
            _err(errs, uid, "solidez", "solidez ALTA sin ninguna entrada con datos suficientes o parciales")
    return errs


def validate_report(role, report, units, run=None):
    """Devuelve {valido, completo, esperadas, recibidas, faltantes, duplicadas, no_esperadas, errores}. `units` = lista de unidades del paquete."""
    pk = {u["unit_id"]: u for u in units}
    errs = []
    if not isinstance(report, dict):
        return {"valido": False, "completo": False, "esperadas": len(pk), "recibidas": 0, "faltantes": list(pk), "duplicadas": [], "no_esperadas": [], "errores": [{"unit_id": None, "campo": "informe", "motivo": "no es un objeto JSON"}]}
    if report.get("agente") != role:
        _err(errs, None, "agente", f"debe ser «{role}»")
    if report.get("version_contrato") != CONTRACT_VERSION:
        _err(errs, None, "version_contrato", f"debe ser {CONTRACT_VERSION}")
    if run is not None and report.get("run") != run:
        _err(errs, None, "run", f"debe ser «{run}»")
    seen, dup, extra = {}, [], []
    allowed = set(FIELDS[role]) | {"unit_id"}
    for u in report.get("unidades", []) if isinstance(report.get("unidades"), list) else []:
        uid = u.get("unit_id") if isinstance(u, dict) else None
        if uid not in pk:
            extra.append(uid)
            continue
        if uid in seen:
            dup.append(uid)
            continue
        seen[uid] = u
        for k in u:
            if k not in allowed:
                _err(errs, uid, k, "campo no permitido (no hay texto libre)")
        for k, vals in ENUMS[role].items():
            if u.get(k) not in vals:
                _err(errs, uid, k, f"valor inválido {u.get(k)!r}; permitido {list(vals)}")
        for k, vals in LIST_ENUMS.get(role, {}).items():
            v = u.get(k)
            if not isinstance(v, list) or not v or any(x not in vals for x in v):
                _err(errs, uid, k, f"debe ser una lista no vacía de {list(vals)}")
        for k in LIST_STR.get(role, ()):
            v = u.get(k)
            if not isinstance(v, list) or not v or any(not isinstance(x, str) or not x.strip() or len(x) > NOTE_MAX for x in v):
                _err(errs, uid, k, "debe ser una lista no vacía de textos cortos")
        if not isinstance(u.get("nota", ""), str) or len(u.get("nota", "")) > NOTE_MAX:
            _err(errs, uid, "nota", f"debe ser texto de ≤ {NOTE_MAX} caracteres")
        ev = u.get("evidencia")
        if not isinstance(ev, list) or not ev or any(not isinstance(x, str) or not x.startswith(EVIDENCE_PREFIXES) for x in ev):
            _err(errs, uid, "evidencia", f"lista no vacía de referencias que empiecen por {list(EVIDENCE_PREFIXES)}")
        ids = {e["id"] for e in pk[uid]["entradas"]}
        exc_f = EXCEPTION_FIELD[role]
        seen_e = set()
        for ex in u.get("excepciones", []) if isinstance(u.get("excepciones", []), list) else [None]:
            if not isinstance(ex, dict) or set(ex) != {"entry_id", exc_f} or ex["entry_id"] not in ids or ex[exc_f] not in ENUMS[role][exc_f] or ex["entry_id"] in seen_e:
                _err(errs, uid, "excepciones", f"cada excepción: {{entry_id de la unidad (sin repetir), {exc_f} válido}}")
                break
            seen_e.add(ex["entry_id"])
        if role == "auditor" and OBJECTION_FIELD in u:
            obs = u[OBJECTION_FIELD]
            seen_o = set()
            for ob in obs if isinstance(obs, list) else [None]:
                ok = isinstance(ob, dict) and set(ob) == {"entry_id", "agente", "campo", "problema"} and ob["agente"] in OBJECTION_ROLES \
                    and ob["campo"] in FIELDS[ob["agente"]] and ob["problema"] in OBJECTION_PROBLEMS and (ob["entry_id"] is None or (isinstance(ob["entry_id"], str) and ob["entry_id"] in ids))
                key = (ob["entry_id"], ob["agente"], ob["campo"]) if ok else None
                if not ok or key in seen_o:
                    _err(errs, uid, OBJECTION_FIELD, f"cada objeción: {{entry_id de la unidad o null, agente {list(OBJECTION_ROLES)}, campo de ese agente, problema {list(OBJECTION_PROBLEMS)}}} sin repetir (entry_id, agente, campo)")
                    break
                seen_o.add(key)
        errs += _coherence(role, u, pk[uid])
    faltantes = [i for i in pk if i not in seen]
    return {"valido": not errs and not dup and not extra, "completo": not faltantes and not errs and not dup and not extra, "esperadas": len(pk), "recibidas": len(seen),
            "faltantes": faltantes, "duplicadas": dup, "no_esperadas": extra, "errores": errs}


def audit_sample_required(units, reports):
    """Unidades que el auditor DEBE revisar: las marcadas por otros agentes + la muestra mínima estratificada por grupo (determinista: orden de unit_id)."""
    flagged = set()
    for role, rep in reports.items():
        if role == "auditor" or not rep:
            continue
        for u in rep.get("unidades", []):
            if u.get("solidez") == "BAJA" or u.get("disponibilidad") == "no_verificable" or (u.get("discrepancias") and u["discrepancias"] != ["ninguna"]) \
                    or u.get("consistencia_modelo") == "discrepa_del_mercado":
                flagged.add(u["unit_id"])
    rest = [u["unit_id"] for u in units if u["unit_id"] not in flagged]
    n_rest = max(AUDIT_SAMPLE_MIN, int(AUDIT_SAMPLE_FRACTION * len(rest) + 0.9999))
    must, groups = set(flagged), {}
    for u in units:
        groups.setdefault(u["grupo"], []).append(u["unit_id"])
    for g, ids in groups.items():
        if not set(ids) & must:
            must.add(sorted(ids)[0])
    extra = [i for i in rest if i not in must]
    take = max(0, min(len(rest), n_rest) - len([i for i in must if i in set(rest)]))
    must |= set(extra[:take])
    return sorted(must & {u["unit_id"] for u in units}), sorted(flagged)


def review_gate(units, reports, run=None, pilot_ids=None):
    """Estado de la revisión: COMPLETA solo si los cuatro roles cubren TODAS las unidades esperadas sin errores y el auditor cumple la muestra mínima."""
    por_agente = {r: (validate_report(r, rep, units, run) if rep is not None else None) for r, rep in reports.items() if r in ROLES}
    inc = []
    for r in ROLES:
        v = por_agente.get(r)
        if v is None:
            inc.append({"tipo": "informe_ausente", "rol": r})
        elif not (v["valido"] if r == "auditor" else v["completo"]):      # el auditor solo debe cubrir la muestra mínima (se comprueba abajo), no todas las unidades
            inc.append({"tipo": "informe_incompleto_o_invalido", "rol": r, "faltantes": len(v["faltantes"]), "errores": len(v["errores"]), "duplicadas": len(v["duplicadas"]), "no_esperadas": len(v["no_esperadas"])})
    must, flagged = audit_sample_required(units, {r: reports.get(r) for r in ROLES if r != "auditor"})
    aud = reports.get("auditor")
    done = {u.get("unit_id") for u in (aud or {}).get("unidades", [])} if isinstance(aud, dict) else set()
    miss_sample = [i for i in must if i not in done]
    if aud is not None and miss_sample:
        inc.append({"tipo": "muestra_del_auditor_insuficiente", "faltantes": len(miss_sample), "ejemplos": miss_sample[:3]})
    ejecutado = any(v is not None for v in por_agente.values())
    estado = "NO_EJECUTADA" if not ejecutado else ("COMPLETA" if not inc else "INCOMPLETA")
    n_obj = sum(len(u.get(OBJECTION_FIELD) or []) for u in (aud or {}).get("unidades", [])) if isinstance(aud, dict) and isinstance(aud.get("unidades"), list) else 0
    return {"estado": estado, "unidades_esperadas": len(units), "por_agente": por_agente, "incidencias": inc, "objeciones_a_agentes": n_obj, "muestra_auditor": {"requeridas": len(must), "marcadas_por_otros": len(flagged), "regla": AUDIT_SAMPLE_TEXT}}


def consolidate(units, reports):
    """Veredictos por unidad y conflictos entre agentes. Las excepciones por entry_id se aplican con `entry_verdict`."""
    out = {}
    idx = {r: {u["unit_id"]: u for u in (rep or {}).get("unidades", [])} for r, rep in reports.items() if r in ROLES}
    for u in units:
        uid = u["unit_id"]
        c = {"unit_id": uid, "partido": u["partido"], "grupo": u["grupo"], "roles": {r: idx.get(r, {}).get(uid) for r in ROLES}, "conflictos": []}
        d, q, v, a = (c["roles"][r] for r in ("deportivo", "cuantitativo", "verificador", "auditor"))
        if d and a and d["solidez"] == "ALTA" and a["objecion"] != "ninguna" and a["severidad"] == "alta":
            c["conflictos"].append("deportivo_ALTA_vs_objecion_grave_del_auditor")
        if d and q and d["solidez"] == "ALTA" and q["consistencia_modelo"] == "discrepa_del_mercado":
            c["conflictos"].append("deportivo_ALTA_vs_modelo_discrepa_del_mercado")
        if v and v["discrepancias"] != ["ninguna"]:
            c["conflictos"].append("verificador_reporta_discrepancias")
        if a and a["recomendacion"] in ("descartar_de_rankings", "verificar_manualmente"):
            c["conflictos"].append(f"auditor_{a['recomendacion']}")
        c["objeciones"] = list((a or {}).get(OBJECTION_FIELD) or [])
        for ag in sorted({o["agente"] for o in c["objeciones"]}):
            c["conflictos"].append(f"auditor_objeta_a_{ag}")
        out[uid] = c
    return out


def entry_verdict(consolidated_unit, role, entry_id):
    """Veredicto de un rol para una entrada: su excepción si existe; si no, el de la unidad."""
    r = (consolidated_unit["roles"] or {}).get(role)
    if not r:
        return None
    for ex in r.get("excepciones", []):
        if ex["entry_id"] == entry_id:
            return ex[EXCEPTION_FIELD[role]]
    return r[EXCEPTION_FIELD[role]]


# ── archivos del run ──
def agent_dir(run):
    return os.path.join(run, "agentes")


def load_reports(run):
    d = agent_dir(run)
    out = {}
    for r in ROLES:
        p = os.path.join(d, f"informe_{r}.json")
        out[r] = common.read_json(p) if os.path.exists(p) else None
    return out


def load_gate(run):
    p = os.path.join(agent_dir(run), "validacion.json")
    return common.read_json(p) if os.path.exists(p) else None


# ── lotes y vista compacta (Fase 7): el paquete completo de un partido pesa ~270 KB; los agentes leen esta vista, el contrato no cambia ──
RES_CODE = {"encontrado": "E", "consultado_no_encontrado": "N", "fuente_no_ofrece": "O", "no_verificable": "V", "pendiente": "P"}


def batch_units(units, k, n):
    """Unidades del lote k de n (1-indexado): los partidos, ordenados por id, se reparten en n bloques contiguos; una unidad nunca se parte entre lotes."""
    if not (1 <= k <= n):
        raise ValueError("lote fuera de rango")
    ms = sorted({u["match_id"] for u in units})
    size = -(-len(ms) // n)
    mine = set(ms[(k - 1) * size: k * size])
    return [u for u in units if u["match_id"] in mine]


PRICE_CODE = {"real_verificada": "R", "otra_fuente": "A", "no_verificable": "V", "sin_precio": "-", "no_consultado": "?"}


def digest_text(units):
    """Vista compacta: por unidad, las firmas (datos/estimador/validación/investigación) que comparten sus líneas se definen UNA vez (S1, S2…) y cada línea solo trae id, firma, precio y p_modelo."""
    L = ["# Vista compacta del paquete (mismos hechos que paquete.json; el contrato de salida es el de contrato_<rol>.md)",
         "Línea: `id | firma | precio | p`. Precio: letra+cuota; R real_verificada (casa/usuario), A otra_fuente (agregador: referencia, NO ejecutable), V no_verificable, `-` sin precio. `p` = probabilidad del modelo propio (`-` si no hay estimador).",
         "Investigación por canal: E encontrado · N consultado_no_encontrado · O la fuente no lo ofrece · V no verificable · P pendiente.", ""]
    for u in units:
        c = u.get("contexto") or {}
        arb = (c.get("arbitro") or {}).get("designado")
        al = (c.get("alineaciones") or {}).get("estado")
        sigs, rows = {}, []
        for e in u["entradas"]:
            inv = ",".join(f"{k[:10]}={RES_CODE.get(v, v)}" for k, v in e["investigacion"].items())
            sg = (e["datos"], e["estimador"], e["validacion"], inv)
            sigs.setdefault(sg, f"S{len(sigs) + 1}")
            pr = e["precio"]
            price = PRICE_CODE.get(pr["estado"], pr["estado"]) + (str(pr["cuota"]) if pr["cuota"] else "")
            rows.append(f"- {e['id']} | {sigs[sg]} | {price} | {'-' if e['p_modelo'] is None else round(e['p_modelo'], 3)}")
        L += [f"## {u['unit_id']} · {u['partido']} · {u['grupo']} · {u.get('hora_utc')} · liga {u.get('liga')} · árbitro {arb or 's/d'} · alineaciones {al or 's/d'}"]
        L += [f"  {name}: datos {sg[0]} · estimador {sg[1]} · validación {sg[2]} · inv {sg[3]}" for sg, name in sigs.items()] + rows + [""]
    return "\n".join(L) + "\n"


def merge_parts(role, parts):
    """Une informes parciales del mismo rol; rechaza cabeceras distintas y unidades repetidas."""
    if not parts:
        raise ValueError("no hay partes")
    head = {k: parts[0].get(k) for k in ("agente", "version_contrato", "run")}
    out, seen, lim = [], set(), []
    for pt in parts:
        if {k: pt.get(k) for k in head} != head or head["agente"] != role:
            raise ValueError("las partes tienen cabeceras distintas o de otro rol")
        for u in pt.get("unidades", []):
            if u.get("unit_id") in seen:
                raise ValueError(f"unidad repetida entre partes: {u.get('unit_id')}")
            seen.add(u.get("unit_id"))
            out.append(u)
        lim += [x for x in pt.get("limitaciones", []) if x not in lim]
    return dict(head, unidades=sorted(out, key=lambda u: u["unit_id"]), limitaciones=lim)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("packages")
    p.add_argument("--run", required=True)
    p.add_argument("--matches")
    p.add_argument("--only", help="ids de partido separados por comas (piloto)")
    p.add_argument("--capture")
    p.add_argument("--capture-ids")
    v = sub.add_parser("validate")
    v.add_argument("--run", required=True)
    v.add_argument("--role", required=True, choices=ROLES)
    v.add_argument("--file", required=True)
    v.add_argument("--batch", help="k/n: valida solo las unidades de ese lote")
    dg = sub.add_parser("digest")
    dg.add_argument("--run", required=True)
    dg.add_argument("--batch", required=True, help="k/n")
    mg = sub.add_parser("merge")
    mg.add_argument("--run", required=True)
    mg.add_argument("--role", required=True, choices=ROLES)
    g = sub.add_parser("gate")
    g.add_argument("--run", required=True)
    sub.add_parser("contract")
    a = ap.parse_args(argv)
    if a.cmd == "contract":
        for r in ROLES:
            print(contract_text(r))
        return 0
    d = agent_dir(a.run)
    if a.cmd == "packages":
        ids = list(json.load(open(a.matches, encoding="utf-8")).values()) if a.matches and os.path.exists(a.matches) else None
        if a.only:
            ids = a.only.split(",")
        units, s = build_units(a.run, ids, capture=(a.capture, a.capture_ids) if a.capture else None)
        os.makedirs(d, exist_ok=True)
        common.write_json_atomic(os.path.join(d, "paquete.json"), {"version_contrato": CONTRACT_VERSION, "run": a.run, "grupos": GROUPS, "unidades": units,
                                                                  "cobertura": {"investigacion": s["investigacion"]["estado"], "analitica": s["analitica"]["estado"], "precios": s["precios"]["estado"]}})
        for r in ROLES:
            with open(os.path.join(d, f"contrato_{r}.md"), "w", encoding="utf-8") as f:
                f.write(contract_text(r))
        print(f"{len(units)} unidades ({len({u['match_id'] for u in units})} partidos × grupos) -> {d}/paquete.json")
        return 0
    pack = common.read_json(os.path.join(d, "paquete.json"))
    if a.cmd == "digest":
        k, n = (int(x) for x in a.batch.split("/"))
        bu = batch_units(pack["unidades"], k, n)
        path = os.path.join(d, f"lote_{k}_de_{n}.md")
        with open(path, "w", encoding="utf-8") as f:
            f.write(digest_text(bu))
        print(f"{path}: {len(bu)} unidades de {len({u['match_id'] for u in bu})} partidos")
        return 0
    if a.cmd == "merge":
        files = sorted(glob.glob(os.path.join(d, f"informe_{a.role}.part*.json")))
        merged = merge_parts(a.role, [common.read_json(f) for f in files])
        common.write_json_atomic(os.path.join(d, f"informe_{a.role}.json"), merged)
        print(f"{a.role}: {len(files)} partes -> {len(merged['unidades'])} unidades")
        return 0
    if a.cmd == "validate":
        us = pack["unidades"]
        if a.batch:
            us = batch_units(us, *(int(x) for x in a.batch.split("/")))
        res = validate_report(a.role, common.read_json(a.file), us, pack["run"])
        print(json.dumps({k: (v if k != "errores" else v[:25]) for k, v in res.items()}, ensure_ascii=False, indent=1))
        return 0 if res["valido"] else 1
    reports = load_reports(a.run)
    gate = review_gate(pack["unidades"], reports, pack["run"])
    common.write_json_atomic(os.path.join(d, "validacion.json"), {k: v for k, v in gate.items() if k != "por_agente"} | {"partidos_ids": sorted({u["match_id"] for u in pack["unidades"]}), "por_agente": None} | {"por_agente": {r: (None if v is None else {k: x for k, x in v.items() if k != "errores"} | {"n_errores": len(v["errores"])}) for r, v in gate["por_agente"].items()}})
    common.write_json_atomic(os.path.join(d, "revision_consolidada.json"), consolidate(pack["unidades"], reports))
    print(f"revisión de agentes: {gate['estado']} · {len(gate['incidencias'])} incidencias · unidades esperadas {gate['unidades_esperadas']}")
    for i in gate["incidencias"]:
        print(" -", i)
    return 0 if gate["estado"] == "COMPLETA" else 3


if __name__ == "__main__":
    sys.exit(main())
