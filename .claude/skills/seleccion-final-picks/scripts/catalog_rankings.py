#!/usr/bin/env python3
"""Fase 6: rankings y combinadas construidos DESDE EL CATÁLOGO COMPLETO (partido × entrada), no desde una lista corta de patas.

Fuente única: `agent_review.build_units` (que ejecuta la cobertura de mercados: investigación, precio, datos, estimador propio `p_modelo`, validación) + los informes de los agentes si existen.
Nada de aquí es una recomendación: el modelo propio sigue SIN validar (data/model_validation.json), por eso cada salida lleva el estado de las tres dimensiones y la preparación para apostar.

Reglas (política declarada en POLICY; ninguna es un hecho estadístico):
- Cada pata de una combinada tiene precio comunicado por una fuente (real de la casa/usuario = «ejecutable»; agregador = «referencia», nunca ejecutable) y cuota ≤ MAX_LEG_ODDS (2.10).
  Una entrada SIN precio no entra en combinadas: en los rankings se muestra su «cuota mínima justa» (1/p_modelo) y si esa cuota ya supera 2.10 queda marcada.
- Riesgo: una pata por partido; máx. 2 patas over (o under) por combinada; máx. 2 de la misma liga; máx. 3 con inicio en la misma ventana horaria.
  La probabilidad conjunta es el producto de las p_modelo (independencia declarada, no validada), por eso los topes de arriba.
- Exposición entre combinadas mostradas: una misma pata en ≤ MAX_LEG_REUSE combinadas y un mismo partido en ≤ MAX_MATCH_REUSE.
- Brecha: una pata cuyo p_modelo supera a 1/cuota en ≥ 15 pp queda fuera (política heredada de la auditoría del 13-oct).
- Agentes: una pata que los agentes rechazan no entra; una combinada solo se marca APROBADA si TODAS sus patas tienen los cuatro informes válidos, sin rechazo ni objeción abierta del auditor (OBJETADA); si no, SIN_REVISION.
Cada combinada lleva su `preparacion_para_apostar` (los mismos siete requisitos que las filas)."""
import argparse
import itertools
import json
import math
import os
import sys
from collections import Counter
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import agent_review as ar  # noqa: E402
import common  # noqa: E402
import market_catalog as mc  # noqa: E402
import market_coverage as cov  # noqa: E402

MAX_LEG_ODDS = cov.MAX_LEG_ODDS
EV_ALERT = 0.10       # EV teórico ≥ +10 % con un modelo sin validar se rotula como probable ruido
MAX_GAP = 0.15      # política heredada de la auditoría del 13-oct: brecha modelo − precio ≥ 15 pp = descarte (efecto de escoger el máximo entre muchas entradas), no «salvedad»
POLICY = {"max_leg_odds": MAX_LEG_ODDS, "max_brecha_modelo_vs_precio": MAX_GAP, "max_over_o_under_por_combinada": 2, "max_misma_liga": 2, "max_misma_ventana": 3, "ventana_minutos": 120,
          "max_reuso_pata": 2, "ventana_calidad": 0.95, "max_reuso_partido": 3, "pool_por_banda": 6, "top_por_objetivo": 3, "top_ranking": 5,
          "independencia": "p_conjunta = producto de p_modelo (supuesto declarado, no validado)"}
# (nombre, cuota mínima, cuota máxima, máx. patas)
DEFAULT_TARGETS = (("x1.2", 1.20, 1.28, 2), ("x3", 2.80, 3.40, 4), ("x4", 4.00, 4.80, 5))
PRICE_OK = {"real_verificada": "ejecutable", "otra_fuente": "referencia"}
# «rechazada» = defecto de dato o de modelo señalado por los agentes: fuera de combinadas Y de rankings. «degradada» = solidez deportiva BAJA/NO_EVALUABLE: fuera de combinadas, pero visible (rotulada) en los rankings.
# «no_encontrada/no_ofrecida» del verificador describen la FUENTE DE PRECIOS (la API no publica córners/tarjetas): ya excluyen de combinadas por falta de precio y NO deben ocultar el mercado de los rankings.
AGENT_BAD = {"cuantitativo": ("defecto_del_modelo", "datos_insuficientes", "sin_estimador"), "verificador": ("no_verificable",)}
AGENT_SOFT = {"deportivo": ("BAJA", "NO_EVALUABLE")}
AUDITOR_BAD = ("descartar_de_rankings", "verificar_manualmente")
VERIFIER_BAD_DISCREPANCIES = ("precio_anomalo", "mercado_mal_etiquetado", "linea_distinta", "identidad_partido", "hora", "calendario")
AGENT_ORDER = {"APROBADA": 0, "SIN_REVISION": 1}


# ── revisión de agentes por entrada ──
def reviewed_prices(run):
    """{(match_id, entry_id): (estado, cuota, fuente)} del paquete CON EL QUE los agentes hicieron su revisión (agentes/paquete.json). Si el precio de una entrada cambió después, esa revisión ya no la cubre."""
    pack = common.read_json(os.path.join(run, "agentes", "paquete.json"), None)
    out = {}
    for u in (pack or {}).get("unidades", []):
        for e in u["entradas"]:
            pr = e["precio"]
            out[(u["match_id"], e["id"])] = (pr["estado"], pr["cuota"], pr["fuente"])
    return out


def agent_status(units, reports, reviewed=None):
    """{(unit_id, entry_id): 'aprobada' | 'sin_revision' | 'rechazada:<motivo>'}. Una unidad cuenta como revisada solo si los cuatro roles la cubren y su informe no tiene errores."""
    pk = {u["unit_id"]: u for u in units}
    valid = {}
    for r in ar.ROLES:
        rep = reports.get(r)
        valid[r] = {e["unit_id"] for e in (rep or {}).get("unidades", [])} if rep and not [x for x in ar.validate_report(r, rep, units)["errores"]] else set()
    cons = ar.consolidate(units, {r: reports.get(r) for r in ar.ROLES})
    out = {}
    for uid, u in pk.items():
        unit_reviewed = all(uid in valid[r] for r in ar.ROLES)
        c = cons[uid]
        for e in u["entradas"]:
            if not unit_reviewed:
                out[(uid, e["id"])] = "sin_revision"
                continue
            why = None
            for role, bad in AGENT_BAD.items():
                v = ar.entry_verdict(c, role, e["id"])
                if v in bad:
                    why = f"{role}:{v}"
                    break
            a, vr = c["roles"]["auditor"], c["roles"]["verificador"]
            soft = None
            for role, bad in AGENT_SOFT.items():
                v = ar.entry_verdict(c, role, e["id"])
                if v in bad:
                    soft = f"{role}:{v}"
            if not why and a["recomendacion"] in AUDITOR_BAD:
                why = f"auditor:{a['recomendacion']}"
            if not why and any(d in VERIFIER_BAD_DISCREPANCIES for d in vr["discrepancias"]):
                why = "verificador:discrepancia_de_la_unidad"
            obj = sorted({o["agente"] for o in c["objeciones"] if o["entry_id"] in (None, e["id"])})
            # una objeción abierta del auditor a otro agente (valor que contradice paquete/fuente) quita la aprobación aunque no rechace la pata
            st = f"rechazada:{why}" if why else (f"degradada:{soft}" if soft else (f"objetada:{','.join(obj)}" if obj else "aprobada"))
            if reviewed is not None and st in ("aprobada",) or (reviewed is not None and st.startswith("objetada")):
                pr = e["precio"]
                rv = reviewed.get((u["match_id"], e["id"]))
                # la aprobación cubre el MISMO tipo de precio y la MISMA fuente; una cuota que se mueve (refresco de precios) no la invalida, pero se avisa si cambió mucho (ver `cuota_revisada`)
                if rv is None or (rv[0], rv[2]) != (pr["estado"], pr["fuente"]):
                    st = "precio_nuevo_sin_revisar"          # los agentes revisaron otro tipo/fuente de precio (o ninguno) para esta entrada
            out[(uid, e["id"])] = st
    return out


# ── patas del catálogo ──
def _limite(odds, p):
    if odds is not None:
        return "cumple" if odds <= MAX_LEG_ODDS else "excede"
    if p is None:
        return "sin_precio_ni_estimador"
    return "sin_precio_justa_ok" if 1 / p <= MAX_LEG_ODDS else "sin_precio_justa_excede"


def legs_from_units(units, status=None, reviewed=None):
    """Una pata por (partido, entrada) del catálogo, con TODOS los hechos y los motivos que la excluyen de combinadas."""
    status = status or {}
    legs = []
    for u in units:
        teams = u["partido"].split(" – ")
        for e in u["entradas"]:
            pr = e["precio"]
            odds = pr["cuota"] if pr["estado"] in PRICE_OK and pr["cuota"] else None
            p = e["p_modelo"]
            st = status.get((u["unit_id"], e["id"]), "sin_revision")
            motivos = []
            if p is None:
                motivos.append("sin_estimador_propio")
            if odds is None:
                motivos.append("sin_precio")
            elif odds > MAX_LEG_ODDS:
                motivos.append(f"cuota_sobre_{MAX_LEG_ODDS}")
            gap = None if (p is None or odds is None) else round(p - 1 / odds, 3)      # contra 1/cuota (con margen de la fuente): subestima la brecha real frente al mercado sin margen
            if gap is not None and abs(gap) >= MAX_GAP:      # simétrico: un modelo MUY por debajo del precio (pata que su propio modelo da por perdedora) tampoco es candidato
                motivos.append("brecha_modelo_vs_precio")
            if st.startswith(("rechazada", "degradada")):
                motivos.append(st)
            legs.append({"leg_id": f"{u['match_id']}|{e['id']}", "match_id": u["match_id"], "partido": u["partido"], "equipos": teams, "grupo": u["grupo"], "entry_id": e["id"],
                         "etiqueta": mc.BY_ID[e["id"]]["label"].replace("{home}", teams[0]).replace("{away}", teams[-1]), "direccion": e["direccion"], "linea": e["linea"], "alcance": e["alcance"], "hora_utc": u.get("hora_utc"), "liga": u.get("liga"),
                         "cuota": odds, "precio_estado": pr["estado"], "precio_tipo": PRICE_OK.get(pr["estado"]), "fuente_precio": pr["fuente"], "observado_utc": pr.get("observado_utc"), "n_casas": pr.get("n_casas"), "limite_2_10": _limite(odds, p),
                         "p_modelo": p, "brecha_vs_precio": gap, "cuota_minima_justa": None if not p else round(1 / p, 3), "ev_teorico": None if (p is None or odds is None) else round(p * odds - 1, 3),
                         "cuota_revisada": ((reviewed or {}).get((u["match_id"], e["id"])) or (None, None, None))[1], "datos": e["datos"], "validacion": e["validacion"], "modelo_validado": cov.model_validated(mc.BY_ID[e["id"]]), "agentes": st, "motivos_exclusion": motivos})
    return legs


def eligible(legs):
    return [l for l in legs if not l["motivos_exclusion"]]


# ── riesgo de una combinada ──
def _minutes(a, b):
    try:
        return abs((datetime.fromisoformat(a.replace("Z", "+00:00")) - datetime.fromisoformat(b.replace("Z", "+00:00"))).total_seconds()) / 60
    except Exception:
        return None


def risk_violations(combo, policy=POLICY):
    """Motivos por los que un conjunto de patas rompe los topes de riesgo (lista vacía = pasa)."""
    v = []
    ms = [l["match_id"] for l in combo]
    if len(set(ms)) != len(ms):
        v.append("dos_patas_del_mismo_partido")
    for d in ("over", "under"):
        if sum(1 for l in combo if l["direccion"] == d) > policy["max_over_o_under_por_combinada"]:
            v.append(f"mas_de_{policy['max_over_o_under_por_combinada']}_{d}")
    ligas = [l["liga"] for l in combo if l["liga"]]
    if any(ligas.count(x) > policy["max_misma_liga"] for x in set(ligas)):
        v.append("demasiadas_de_la_misma_liga")
    for l in combo:
        near = [m for m in combo if l["hora_utc"] and m["hora_utc"] and (lambda d: d is not None and d <= policy["ventana_minutos"])(_minutes(l["hora_utc"], m["hora_utc"]))]
        if len(near) > policy["max_misma_ventana"]:
            v.append("demasiadas_en_la_misma_ventana_horaria")
            break
    return v


def combo_readiness(combo, certified):
    return cov._readiness({"investigacion_resuelta": bool(certified),
                           "precio_real_verificado": all(l["precio_tipo"] == "ejecutable" for l in combo),
                           "cuota_dentro_del_limite": all(l["cuota"] is not None and l["cuota"] <= MAX_LEG_ODDS for l in combo),
                           "datos_suficientes": all(l["datos"] == "suficientes" for l in combo),
                           "estimador_propio_disponible": all(l["p_modelo"] is not None for l in combo),
                           "modelo_validado": all(l["modelo_validado"] for l in combo),
                           "revision_agentes_completa": all(l["agentes"] == "aprobada" for l in combo)})


def correlation_notes(combo):
    """Avisos de dependencia entre patas (el producto de p las supone independientes): misma dirección de goles, misma liga o inicio cercano."""
    notes = []
    for d, txt in (("over", "overs"), ("under", "unders")):
        n = sum(1 for l in combo if l["direccion"] == d)
        if n >= 2:
            notes.append(f"{n} {txt}: comparten el régimen de goles del día (más dependientes de lo que supone el producto)")
    ligas = Counter(l["liga"] for l in combo if l["liga"])
    for lg, n in ligas.items():
        if n >= 2:
            notes.append(f"{n} patas de la misma liga ({lg}): misma competición, posible dependencia de árbitros/ritmo")
    for i, a in enumerate(combo):
        for b in combo[i + 1:]:
            m = _minutes(a["hora_utc"], b["hora_utc"]) if a["hora_utc"] and b["hora_utc"] else None
            if m is not None and m <= POLICY["ventana_minutos"]:
                notes.append(f"{a['partido']} y {b['partido']} empiezan con ≤ {POLICY['ventana_minutos']} min de diferencia (se resuelven a la vez)")
    return notes


def _combo_record(name, combo, certified):
    odds = 1.0
    p = 1.0
    for l in combo:
        odds *= l["cuota"]
        p *= l["p_modelo"]
    ln_total = math.log(odds)
    all_real = all(l["precio_tipo"] == "ejecutable" for l in combo)
    return {"objetivo": name, "patas": [dict({k: l[k] for k in ("leg_id", "partido", "grupo", "etiqueta", "cuota", "precio_tipo", "p_modelo", "cuota_minima_justa", "agentes", "hora_utc")},
                                            aporte_log_pct=round(100 * math.log(l["cuota"]) / ln_total, 1) if ln_total else None) for l in combo],
            "multiplicador": " × ".join(f"{l['cuota']:g}" for l in combo) + f" = {odds:.2f}", "nota_correlacion": "; ".join(correlation_notes(combo)) or None,
            "cuota_total": round(odds, 3), "p_conjunta_independiente": round(p, 4), "p_perdida": round(1 - p, 4), "ev_teorico": round(p * odds - 1, 3) if all_real else None,
            "alerta": "EV alto: probable desacuerdo del modelo (no validado) con el mercado, no ventaja" if (all_real and p * odds - 1 >= EV_ALERT) else None,
            "tipo_cuota": "ejecutable (precios reales)" if all_real else "REFERENCIA (alguna pata solo tiene precio de agregador: no ejecutable)",
            "estado_agentes": "APROBADA" if all(l["agentes"] == "aprobada" for l in combo) else ("OBJETADA" if any(l["agentes"].startswith("objetada") for l in combo) else "SIN_REVISION"),
            "preparacion_para_apostar": combo_readiness(combo, certified), "nota_p": "p_modelo del modelo propio NO VALIDADO; producto bajo independencia declarada"}


# ── combinadas con topes de exposición ──
def build_combos(legs, certified=False, targets=DEFAULT_TARGETS, policy=POLICY, budget=1_500_000):
    pool_all = eligible(legs)
    taken_leg, taken_match, out = {}, {}, {}
    used_grupo, used_liga = Counter(), Counter()
    for name, lo, hi, nmax in targets:
        floor = max(1.02, lo ** (1 / nmax))
        # pool ESTRATIFICADO por banda de cuota (top por p dentro de cada banda): ordenar solo por p llenaría el pool de patas casi seguras y baratas y dejaría fuera las de cuota media que un ×4 necesita
        cands = sorted([l for l in pool_all if l["cuota"] >= floor], key=lambda l: -l["p_modelo"])
        edges = (0.0, 1.25, 1.4, 1.6, 99.0)
        pool = []
        for lo_b, hi_b in zip(edges, edges[1:]):
            band = [l for l in cands if lo_b <= l["cuota"] < hi_b]
            # dentro de cada banda caben las mejores patas YA APROBADAS por los agentes y las mejores del resto: sin esto, las patas sin revisión (muy numerosas) desplazarían a las aprobadas
            pool += [l for l in band if l["agentes"] == "aprobada"][: policy["pool_por_banda"]] + [l for l in band if l["agentes"] != "aprobada"][: policy["pool_por_banda"]]
        cand, seen = [], 0
        for n in range(1, nmax + 1):
            for c in itertools.combinations(pool, n):
                seen += 1
                if seen > budget:
                    break
                od = 1.0
                for l in c:
                    od *= l["cuota"]
                if not lo <= od <= hi or risk_violations(c, policy):
                    continue
                p = 1.0
                for l in c:
                    p *= l["p_modelo"]
                cand.append((0 if all(l["agentes"] == "aprobada" for l in c) else 1, 0 if all(l["precio_tipo"] == "ejecutable" for l in c) else 1, -p, c))
        cand.sort(key=lambda t: t[:3])       # primero aprobadas por agentes, luego con precios ejecutables, luego mayor p_modelo
        cand = [(a, b, c) for a, _, b, c in cand]
        chosen, start = [], 0
        while len(chosen) < policy["top_por_objetivo"]:
            window, tier, p_first = [], None, None
            for i in range(start, len(cand)):
                if cand[i] is None:
                    continue
                tr, negp, c = cand[i]
                if any(taken_leg.get(l["leg_id"], 0) >= policy["max_reuso_pata"] or taken_match.get(l["match_id"], 0) >= policy["max_reuso_partido"] for l in c):
                    continue
                if tier is None:
                    tier, p_first = tr, -negp
                    start = i
                elif tr != tier or -negp < p_first * policy["ventana_calidad"]:
                    break
                window.append((i, c))
            if not window:
                break
            # entre alternativas de calidad comparable (misma aprobación y p ≥ 95 % de la mejor) se prefiere la que menos repite grupo de mercado y liga ya usados
            i, c = min(window, key=lambda t: (sum(used_grupo[l["grupo"]] + used_liga[l["liga"]] for l in t[1]), t[0]))
            for l in c:
                taken_leg[l["leg_id"]] = taken_leg.get(l["leg_id"], 0) + 1
                taken_match[l["match_id"]] = taken_match.get(l["match_id"], 0) + 1
                used_grupo[l["grupo"]] += 1
                used_liga[l["liga"]] += 1
            cand[i] = None                # ya elegida: no vuelve a entrar en la ventana
            chosen.append(_combo_record(name, c, certified))
        out[name] = {"rango_cuota": [lo, hi], "max_patas": nmax, "candidatas_evaluadas": seen, "pool": len(pool), "combinadas": chosen,
                     "aviso": None if chosen else "ninguna combinación del pool cumple rango, topes de riesgo y exposición"}
    return out


# ── rankings ──
def _row(l):
    return {k: l[k] for k in ("leg_id", "partido", "grupo", "etiqueta", "cuota", "precio_tipo", "limite_2_10", "p_modelo", "cuota_minima_justa", "brecha_vs_precio", "ev_teorico", "datos", "validacion", "agentes", "motivos_exclusion")}


def build_rankings(legs, top=POLICY["top_ranking"]):
    with_p = [l for l in legs if l["p_modelo"] is not None and not any(m.startswith("rechazada") for m in l["motivos_exclusion"])]
    groups = sorted({l["grupo"] for l in legs})
    por_grupo = {}
    for g in groups:
        gl = [l for l in with_p if l["grupo"] == g]
        # más probables con cuota mínima justa dentro del límite (p ≥ 1/2.10): las demás no pueden cumplir 2.10 ni siquiera a precio justo
        prob = sorted([l for l in gl if l["cuota_minima_justa"] <= MAX_LEG_ODDS], key=lambda l: -l["p_modelo"])[:top]
        ev = sorted([l for l in gl if l["ev_teorico"] is not None and l["limite_2_10"] == "cumple"], key=lambda l: -l["ev_teorico"])[:top]
        por_grupo[g] = {"entradas_con_estimador": len(gl), "mas_probables": [_row(l) for l in prob], "mayor_ev_teorico_con_precio": [_row(l) for l in ev]}
    return {"por_grupo": por_grupo,
            "general_mas_probables": [_row(l) for l in sorted([l for l in with_p if l["cuota_minima_justa"] <= MAX_LEG_ODDS], key=lambda l: -l["p_modelo"])[: top * 4]],
            "nota": "ordenados por probabilidad del modelo propio (NO validado) o por EV teórico con ese mismo p; el EV de mercado no es el veredicto. Sin precio: cuota mínima justa = 1/p."}


def summary(legs):
    from collections import Counter
    c = Counter(m for l in legs for m in (l["motivos_exclusion"] or ["elegible"]))
    return {"patas_catalogo": len(legs), "elegibles_para_combinadas": len(eligible(legs)), "por_motivo_de_exclusion": dict(sorted(c.items())),
            "por_precio": dict(Counter(l["precio_estado"] for l in legs)), "por_agentes": dict(Counter(l["agentes"].split(":")[0] for l in legs)), "con_estimador": sum(1 for l in legs if l["p_modelo"] is not None)}


def render_md(res):
    L = [f"# Rankings y combinadas desde el catálogo completo — {res['run']}", "", f"**ESTADO: {res['banner']}**", "",
         "Nada de esto es una recomendación: el modelo propio no está validado y las probabilidades son del modelo, no del mercado. Los precios «referencia» (agregador) no son ejecutables.", "",
         "## Resumen", "", json.dumps(res["resumen"], ensure_ascii=False, indent=1), "", "## Combinadas", ""]
    for name, b in res["combinadas"].items():
        L += [f"### {name} (cuota {b['rango_cuota'][0]}–{b['rango_cuota'][1]}, hasta {b['max_patas']} patas; evaluadas {b['candidatas_evaluadas']})", ""]
        if not b["combinadas"]:
            L += [f"_{b['aviso']}_", ""]
        for i, c in enumerate(b["combinadas"], 1):
            L += [f"**#{i}** cuota ×{c['cuota_total']} · P(modelo) {c['p_conjunta_independiente']:.1%} · P(pérdida) {c['p_perdida']:.1%} · agentes: {c['estado_agentes']} · apta: {c['preparacion_para_apostar']['estado']} (falta: {', '.join(c['preparacion_para_apostar']['incumplidos']) or '—'})",
                  f"_{c['tipo_cuota']}_"]
            L += [f"- {p['partido']} · {p['etiqueta']} @{p['cuota']} ({p['precio_tipo']}) · p={p['p_modelo']:.2f}" for p in c["patas"]] + [""]
    L += ["## Rankings por grupo de mercado", ""]
    for g, r in res["rankings"]["por_grupo"].items():
        L += [f"### {g} ({r['entradas_con_estimador']} entradas con estimador)", ""]
        for k, t in (("mas_probables", "Más probables (cuota mínima justa ≤ 2.10)"), ("mayor_ev_teorico_con_precio", "Mayor EV teórico con precio ≤ 2.10")):
            L.append(f"**{t}**")
            L += [f"- {x['partido']} · {x['etiqueta']} · p={x['p_modelo']:.2f} · mínima justa {x['cuota_minima_justa']} · cuota {x['cuota'] or '—'} ({x['precio_tipo'] or 'sin precio'})" for x in r[k]] or ["- (ninguna)"]
            L.append("")
    return "\n".join(L) + "\n"


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--run", required=True)
    ap.add_argument("--ids", help="JSON {«local|visitante»: match_id} (los valores definen los partidos); sin él, los partidos requeridos del run")
    ap.add_argument("--capture", nargs=2, metavar=("PARTIDOS_USUARIO", "IDS"))
    ap.add_argument("--out-dir")
    ap.add_argument("--targets", help="p. ej. x1.2:1.2:1.28:2,x3:2.8:3.4:4")
    a = ap.parse_args(argv)
    ids = sorted(set(common.read_json(a.ids).values())) if a.ids else None
    units, s = ar.build_units(a.run, ids, tuple(a.capture) if a.capture else None)
    reports = ar.load_reports(a.run)
    rev_prices = reviewed_prices(a.run)
    legs = legs_from_units(units, agent_status(units, reports, rev_prices), rev_prices)
    targets = tuple((n, float(lo), float(hi), int(k)) for n, lo, hi, k in (t.split(":") for t in a.targets.split(","))) if a.targets else DEFAULT_TARGETS
    res = {"run": a.run, "banner": cov.banner(s), "investigacion_certificada": s["investigacion_certificada"], "politica": POLICY, "resumen": summary(legs),
           "rankings": build_rankings(legs), "combinadas": build_combos(legs, s["investigacion_certificada"], targets)}
    out = a.out_dir or os.path.join(a.run, "rankings")
    os.makedirs(out, exist_ok=True)
    common.write_json_atomic(os.path.join(out, "ranking_catalogo.json"), res)
    with open(os.path.join(out, "ranking_catalogo.md"), "w", encoding="utf-8") as fh:
        fh.write(render_md(res))
    print(res["banner"])
    print(json.dumps(res["resumen"], ensure_ascii=False))
    for n, b in res["combinadas"].items():
        print(n, len(b["combinadas"]), "combinadas;", b["aviso"] or "")
    return 0


if __name__ == "__main__":
    sys.exit(main())
