#!/usr/bin/env python3
"""Informe de cobertura con denominadores explícitos y PUERTA de cobertura.

Uso:  coverage_report.py --run runs/2026-10-13 [--json]
Códigos de salida:  0 = ranking definitivo permitido | 3 = BLOQUEADO (hay confirmados+elegibles sin evaluación básica
o estados inválidos) | 4 = RANKING PROVISIONAL RESTRINGIDO (limitación sistémica) | 2 = uso/entrada inválida.
'Procesado' no significa 'evaluado suficientemente': ambos se reportan por separado.
"""
import argparse
import os
import sys
from collections import Counter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common  # noqa: E402

PARCIAL_PROXY = "PARCIAL_PROXY_OTRA_COMPETICION"
PROCESSED_OK = ("COMPLETADO", PARCIAL_PROXY, "NO_EVALUABLE_TRAS_INTENTOS", "NO_INVESTIGADO_SIN_FUENTE_PERMITIDA")
NEEDS_REASON = ("NO_EVALUABLE_TRAS_INTENTOS", "NO_INVESTIGADO_SIN_FUENTE_PERMITIDA", PARCIAL_PROXY)


def _all_markets():
    import level1
    return level1.ALL_MARKETS, list(level1.FAMILIES)


def compute(run):
    inv = common.read_json(os.path.join(run, "inventory.json"))
    if not inv:
        raise FileNotFoundError("falta inventory.json")
    st = common.read_json(os.path.join(run, "state.json"), {"matches": {}})["matches"]
    mx = common.read_json(os.path.join(run, "matrix.json"), {"matches": {}})["matches"]
    ms = inv["matches"]
    comp = inv["meta"].get("source_completeness", [])
    truncated = [c for c in comp if c.get("has_more") or c.get("loaded", 0) < c.get("declared_total", 0)]
    ALL, FAMS = _all_markets()
    required = [m for m in ms if m["analysis_required"]]
    problems, pending, processed, sufficient, proxy_only = [], [], [], [], []
    for m in required:
        s = st.get(m["match_id"], {"status": "PENDIENTE"})
        stt = s["status"]
        if stt in PROCESSED_OK:
            if stt in NEEDS_REASON and not (s.get("reason") and s.get("evidence")):
                problems.append((m["match_id"], f"{stt} sin motivo o sin evidencia de intentos"))
                pending.append(m)
                continue
            processed.append(m)
            if stt == PARCIAL_PROXY or mx.get(m["match_id"], {}).get("proxy_sample"):
                proxy_only.append(m)              # solo forma doméstica de OTRA competición: PARCIAL, nunca «suficiente»
            elif stt == "COMPLETADO":
                sufficient.append(m)
        else:
            pending.append(m)
            if stt.startswith("ERROR"):
                problems.append((m["match_id"], stt + ": " + str(s.get("last_error", ""))))
    # consistencia inventario <-> estado <-> matriz (el informe debe concordar con lo persistido)
    inv_ids = {m["match_id"] for m in ms}
    for mid, s_ in st.items():
        if mid not in inv_ids:
            problems.append((mid, "estado huérfano: no existe en el inventario"))
    for mid in mx:
        if mid not in inv_ids:
            problems.append((mid, "matriz huérfana: no existe en el inventario"))
    for m in required:
        s_ = st.get(m["match_id"], {}).get("status")
        if s_ in PROCESSED_OK and m.get("sports_analysis_status") != s_:
            problems.append((m["match_id"], f"inventario dice {m.get('sports_analysis_status')} pero el estado persistido dice {s_}"))
        if s_ in PROCESSED_OK and m["match_id"] not in mx:
            problems.append((m["match_id"], "estado procesado sin fila en matrix.json"))
    # mercados
    examined = ok = nonev = notchk = 0
    examined_proxy = ok_proxy = examined_own = ok_own = 0
    fam_ok = Counter()
    for m in required:
        ev = mx.get(m["match_id"])
        if not ev:
            continue
        for k, mk in ev["markets"].items():
            if mk["evaluation_status"] == "NOT_CHECKED":
                notchk += 1
                continue
            examined += 1
            is_proxy = bool(mk.get("proxy_sample") or ev.get("proxy_sample"))
            own = ev.get("history_kind") in ("apifootball_historial_propio", "apifootball_misma_competicion")
            examined_proxy += is_proxy
            examined_own += own
            if mk["evaluation_status"] in ("EVALUABLE", "PARCIAL"):
                ok += 1
                ok_proxy += is_proxy
                ok_own += own
                if not is_proxy:
                    fam_ok[k.split(".")[0]] += 1           # un proxy de otra competición NO levanta una limitación sistémica
            else:
                nonev += 1
    kinds = Counter(mx.get(m["match_id"], {}).get("history_kind") for m in processed)
    no_data_attempt = [m["match_id"] for m in processed if not mx.get(m["match_id"], {}).get("data_attempted")]
    den_markets = len(required) * len(ALL)
    cal = Counter(m["calendar_verification_status"] for m in ms)
    started = sum(1 for m in ms if m["event_status"] in ("EN_JUEGO", "FINALIZADO") or "ya ha comenzado" in m["disposition"])
    not_elig = sum(1 for m in ms if m["prematch_eligibility"] == "NO_ELEGIBLE")
    pct = lambda a, b: round(100 * a / b, 1) if b else None
    systemic = [f for f in FAMS if required and fam_ok[f] == 0]
    trunc_note = ""
    if truncated:
        trunc_note = ("UNIVERSO TRUNCADO: " + "; ".join(f"{c['source']} {c.get('day')}: {c['loaded']} accesibles de {c['declared_total']} declarados" for c in truncated)
                      + " — los partidos contados son una cota inferior; nunca «la jornada completa»")
    if problems:
        verdict, code = "BLOQUEADO — inconsistencias de integridad entre inventario, estado y matriz (ver problemas)", 3
    elif required and pending:
        verdict, code = "BLOQUEADO — hay partidos confirmados y elegibles sin evaluación básica", 3
    elif not required:
        verdict, code = "RANKING PROVISIONAL RESTRINGIDO — no hay partidos confirmados y elegibles que evaluar", 4
    elif len(sufficient) < len(required) or systemic:
        verdict, code = ("RANKING PROVISIONAL RESTRINGIDO — limitación sistémica: "
                         + (f"familias sin ningún mercado evaluable {systemic}; " if systemic else "")
                         + f"{len(no_data_attempt)} partidos NO investigados (sin fuente permitida), {len(proxy_only)} solo con forma doméstica proxy (parcial) y {len(required) - len(sufficient) - len(no_data_attempt) - len(proxy_only)} con intento insuficiente"
                         + ("; " + trunc_note if trunc_note else "")), 4
    elif truncated:
        verdict, code = "RANKING PROVISIONAL RESTRINGIDO — " + trunc_note, 4
    else:
        verdict, code = "COBERTURA DE NIVEL 1 COMPLETA — ranking definitivo permitido, sujeto al Nivel 2", 0
    return {
        "raw_by_source": inv["meta"]["raw_counts"], "raw_duplicates_within_source": len(inv.get("raw_duplicates", [])),
        "unique_matches": len(ms), "calendar_status": dict(cal),
        "confirmed": cal["CONFIRMADO"], "not_confirmed": len(ms) - cal["CONFIRMADO"] - cal["DUPLICADO"],
        "started_or_finished": started, "not_eligible_prematch": not_elig,
        "required_confirmed_eligible": len(required), "processed": len(processed), "evaluated_sufficiently": len(sufficient), "proxy_only_partial": len(proxy_only),
        "required_single_source_calendar": sum(1 for m in required if len(m.get("source_names", [])) < 2),
        "required_selection_calendar_sufficient": sum(1 for m in required if m.get("selection_calendar_verification") == "SUFICIENTE"),
        "processed_without_any_data_attempt": len(no_data_attempt), "with_real_data_attempt": len(processed) - len(no_data_attempt),
        "pending": len(pending), "pending_ids": [m["match_id"] for m in pending],
        "coverage_matches_pct": pct(len(processed), len(required)), "coverage_matches_den": len(required),
        "history_kinds": {str(k): v for k, v in kinds.items()}, "markets_examined_own_history": examined_own, "markets_ok_own_history": ok_own,
        "markets_denominator": den_markets, "markets_examined": examined, "markets_not_checked": notchk, "markets_examined_from_other_competition_proxy": examined_proxy,
        "markets_evaluable_or_partial_same_competition": ok - ok_proxy,
        "markets_evaluable_or_partial": ok, "markets_not_evaluable": nonev,
        "coverage_markets_pct": pct(examined, den_markets),
        "candidates_detected": ok, "systemic_families_without_any_evaluable": systemic,
        "universe_truncated": bool(truncated), "truncation_detail": truncated, "truncation_note": trunc_note,
        "confirmed_with_sufficient_selection_check": sum(1 for m in ms if m.get("selection_calendar_verification") == "SUFICIENTE"),
        "problems": problems, "verdict": verdict, "exit_code": code}


def render(r):
    L = ["# Informe de cobertura", ""]
    L.append("| Métrica | Valor | Denominador / nota |\n|---|---|---|")
    L.append(f"| Registros brutos por fuente | {r['raw_by_source']} | duplicados dentro de fuente: {r['raw_duplicates_within_source']} |")
    L.append(f"| Partidos únicos | {r['unique_matches']} | tras deduplicar |")
    L.append(f"| Partidos con calendario CONFIRMADO (según fuente estructurada) | {r['confirmed']} | de {r['unique_matches']} únicos; con verificación SUFICIENTE para selección final: {r['confirmed_with_sufficient_selection_check']} |")
    L.append(f"| Partidos no confirmados | {r['not_confirmed']} | calendario: {r['calendar_status']} |")
    L.append(f"| Iniciados/finalizados | {r['started_or_finished']} | no elegibles prepartido (todas las causas): {r['not_eligible_prematch']} |")
    L.append(f"| Requieren evaluación (confirmados y elegibles) | {r['required_confirmed_eligible']} | base de la cobertura |")
    L.append(f"| Con disposición registrada (con motivo y evidencia) | {r['processed']} | de {r['coverage_matches_den']} = {r['coverage_matches_pct']}% — de ellos: {r['proxy_only_partial']} solo proxy parcial, {r['processed_without_any_data_attempt']} sin ninguna consulta de datos, {r['evaluated_sufficiently']} evaluados de verdad |")
    L.append(f"| Hora/calendario de los requeridos | {r['required_single_source_calendar']} de {r['required_confirmed_eligible']} con UNA sola fuente; "
             f"{r['required_selection_calendar_sufficient']} con verificación suficiente para selección final | «CONFIRMADO» significa sin discrepancias entre fuentes, no hora contrastada |")
    L.append(f"| Con al menos una consulta real de datos | {r['with_real_data_attempt']} | de {r['coverage_matches_den']} |")
    hk = r["history_kinds"]
    L.append(f"| Con histórico de la MISMA competición de los dos equipos (apifootball, sin amistosos) | {hk.get('apifootball_misma_competicion', 0)} | de {r['coverage_matches_den']}; ≤10 partidos recientes, mezcla casa/fuera, sin ajustar por rival |")
    L.append(f"| Con HISTORIAL PROPIO MIXTO (apifootball: copas/otras competiciones etiquetadas; al menos un equipo sin 6 partidos de la misma competición) | {hk.get('apifootball_historial_propio', 0)} | de {r['coverage_matches_den']}; muestra menos comparable |")
    L.append(f"| Con histórico de la MISMA liga (Football-Data) | {hk.get('football-data_misma_liga', 0)} | de {r['coverage_matches_den']} |")
    L.append(f"| Solo con forma doméstica PROXY (otra competición): evaluación PARCIAL | {r['proxy_only_partial']} | de {r['coverage_matches_den']}; no evalúa el partido |")
    L.append(f"| NO intentados (ningún adaptador de fuente permitida los cubre; no se comprobó si otra fuente permitida lo haría) | {r['processed_without_any_data_attempt']} | de {r['processed']} con disposición: «con disposición» no es «examinado» |")
    L.append(f"| Pendientes | {r['pending']} | {r['pending_ids'][:10]}{'…' if len(r['pending_ids']) > 10 else ''} |")
    L.append(f"| Mercados examinados | {r['markets_examined']} | de {r['markets_denominator']} = {r['coverage_markets_pct']}% (NOT_CHECKED: {r['markets_not_checked']}); "
             f"con historial propio del equipo: {r['markets_examined_own_history']}; solo proxy de OTRA competición: {r['markets_examined_from_other_competition_proxy']} |")
    L.append(f"| Mercados con estadística descriptiva o cuota media (PARCIAL/EVALUABLE) | {r['markets_evaluable_or_partial']} | con historial propio/misma liga: {r['markets_evaluable_or_partial_same_competition']}; el resto es proxy de otra competición |")
    L.append(f"| Mercados NO_EVALUABLE (huecos: en proxies, la fuente abierta no trae ese dato o no es comparable) | {r['markets_not_evaluable']} | familias sin ningún mercado evaluable con historial propio o de la misma liga: {r['systemic_families_without_any_evaluable']} |")
    if r["problems"]:
        L += ["", "Problemas de integridad:"] + [f"- {a}: {b}" for a, b in r["problems"]]
    L += ["", f"**Veredicto de la puerta de cobertura: {r['verdict']}**"]
    if r["universe_truncated"]:
        L += ["", f"**⚠ {r['truncation_note']}.** Nada de lo que sigue puede describirse como «la jornada completa»."]
    if r["exit_code"] == 4:
        L += ["", "**Qué NO se sostiene con este resultado:**",
              f"- Hay {r['markets_evaluable_or_partial']} mercados con estadística descriptiva PARCIAL (de partidos de otra competición cuando es proxy), pero ningún candidato evaluado, ninguna probabilidad, cuota ni EV para los {r['required_confirmed_eligible']} partidos requeridos.",
              f"- {r['markets_not_checked']} mercados están NOT_CHECKED (no investigados): eso no prueba que el mercado no exista ni que la estadística sea 0.",
              "- No se sostiene ninguna selección por valor ni «alta probabilidad»; cualquier orden entre partidos sería criterio cualitativo sin valor económico confirmado.",
              "- No hay histórico de la misma competición ajustado por rival, árbitro designado, bajas ni cuotas ejecutables de una casa concreta para estos partidos; el historial propio es descriptivo y el proxy doméstico no sustituye esos datos.",
              "- El calendario de cada partido proviene de una sola fuente: no basta para una selección final (`selection_calendar_verification`).",
              "- Para levantar la restricción faltan, según el caso: partidos sin cobertura de la API, bajas/alineaciones, cuotas ejecutables de la casa de la persona usuaria y contraste de Nivel 2."]
    return "\n".join(L)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--run", required=True)
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args(argv)
    try:
        r = compute(a.run)
    except FileNotFoundError as e:
        print(f"error: {e}", file=sys.stderr)
        return 2
    common.write_json_atomic(os.path.join(a.run, "coverage.json"), r)
    text = render(r)
    with open(os.path.join(a.run, "coverage_report.md"), "w", encoding="utf-8") as f:
        f.write(text + "\n")
    print(text)
    return r["exit_code"]


if __name__ == "__main__":
    sys.exit(main())
