"""Fase 6: rankings y combinadas desde el catálogo completo, con tope de 2.10 por pata, riesgo, exposición y estado de agentes. Datos FICTICIOS: EJEMPLO — NO REAL."""
import copy
import os
import re
import subprocess
import sys
import unittest

import helpers  # noqa: F401  (añade scripts/ al path)
import agent_review as ar
import catalog_rankings as cr
import market_catalog as mc
import market_coverage as cov

REPO = os.path.normpath(os.path.join(os.path.dirname(__file__), ".."))
OVER = [e["id"] for e in mc.CATALOG if e["market"] == "goles" and e["direction"] == "over"][:3]
UNDER = [e["id"] for e in mc.CATALOG if e["market"] == "goles" and e["direction"] == "under"][:3]


def entrada(eid, odds=None, p=0.7, estado="real_verificada", datos="suficientes"):
    return {"id": eid, "linea": None, "direccion": mc.BY_ID[eid]["direction"], "alcance": "match", "investigacion": {"datos_deportivos": "encontrado", "agregador": "encontrado"},
            "precio": {"estado": estado if odds else "sin_precio", "cuota": odds, "fuente": "casa X" if odds else None, "tipo": "casa" if odds else None, "cumple_limite_2_10": None},
            "datos": datos, "estimador": "calculable" if p is not None else "no_implementado", "validacion": "insuficiente", "p_modelo": p}


def unit(i, entries, liga="L1", hora="2026-10-14T20:00:00Z", grupo="goles"):
    cnt = lambda f: {k: sum(1 for x in entries if f(x) == k) for k in sorted({f(x) for x in entries})}
    resumen = {"entradas": len(entries), "precio": cnt(lambda x: x["precio"]["estado"]), "datos": cnt(lambda x: x["datos"]), "estimador": cnt(lambda x: x["estimador"]),
               "validacion": cnt(lambda x: x["validacion"] or "sin_estimador"), "investigacion": {"resuelta": len(entries)}}
    return {"unit_id": ar.unit_id(f"m{i}", grupo), "match_id": f"m{i}", "partido": f"A{i} – B{i}", "grupo": grupo, "hora_utc": hora, "liga": liga, "contexto": {}, "entradas": entries, "resumen": resumen}


def legs_of(units, status=None):
    return cr.legs_from_units(units, status)


class Patas(unittest.TestCase):
    def test_exclusiones_por_estimador_precio_limite_y_brecha(self):
        e = [entrada(OVER[0], None, 0.7), entrada(OVER[1], 1.8, None), entrada(OVER[2], 2.5, 0.6), entrada(UNDER[0], 1.5, 0.9), entrada(UNDER[1], 1.5, 0.6)]
        L = {l["entry_id"]: l for l in legs_of([unit(1, e)])}
        self.assertIn("sin_precio", L[OVER[0]]["motivos_exclusion"])
        self.assertIn("sin_estimador_propio", L[OVER[1]]["motivos_exclusion"])
        self.assertIn(f"cuota_sobre_{cr.MAX_LEG_ODDS}", L[OVER[2]]["motivos_exclusion"])
        self.assertIn("brecha_modelo_vs_precio", L[UNDER[0]]["motivos_exclusion"])          # 0.90 − 1/1.5 = 0.23
        self.assertEqual(L[UNDER[1]]["motivos_exclusion"], [])
        neg = {l["entry_id"]: l for l in legs_of([unit(2, [entrada(UNDER[2], 1.5, 0.40)])])}          # 0.40 − 1/1.5 = −0.27: el modelo da la pata por perdedora
        self.assertIn("brecha_modelo_vs_precio", neg[UNDER[2]]["motivos_exclusion"])
        self.assertEqual(L[OVER[0]]["limite_2_10"], "sin_precio_justa_ok")                    # 1/0.7 = 1.43 ≤ 2.10
        self.assertEqual(L[OVER[2]]["limite_2_10"], "excede")

    def test_la_etiqueta_nombra_a_los_equipos(self):
        eid = next(e["id"] for e in mc.CATALOG if "{home}" in e["label"])
        l = legs_of([unit(1, [entrada(eid, 1.5, 0.6)])])[0]
        self.assertNotIn("{", l["etiqueta"])
        self.assertIn("A1", l["etiqueta"])

    def test_sin_precio_con_cuota_justa_sobre_el_limite_se_marca(self):
        self.assertEqual({l["entry_id"]: l for l in legs_of([unit(1, [entrada(OVER[0], None, 0.30)])])}[OVER[0]]["limite_2_10"], "sin_precio_justa_excede")

    def test_precio_de_agregador_es_referencia_y_nunca_ejecutable(self):
        l = legs_of([unit(1, [entrada(OVER[0], 1.6, 0.66, estado="otra_fuente")])])[0]
        self.assertEqual(l["precio_tipo"], "referencia")
        r = cr.combo_readiness([l], certified=True)
        self.assertIn("precio_real_verificado", r["incumplidos"])
        self.assertEqual(r["estado"], "NO_APTA")


class Riesgo(unittest.TestCase):
    def setUp(self):
        self.us = [unit(i, [entrada(OVER[0], 1.5, 0.7), entrada(UNDER[1], 1.5, 0.7)], liga=f"L{i % 2}", hora=f"2026-10-14T{10 + 3 * i:02d}:00:00Z") for i in range(6)]
        self.legs = legs_of(self.us)

    def pick(self, entry, ms):
        return [l for l in self.legs if l["entry_id"] == entry and l["match_id"] in ms]

    def test_misma_direccion_liga_y_partido(self):
        self.assertIn("mas_de_2_over", cr.risk_violations(self.pick(OVER[0], {"m0", "m1", "m2"})))
        self.assertEqual(cr.risk_violations(self.pick(OVER[0], {"m0", "m1"}) + self.pick(UNDER[1], {"m2"})), [])
        self.assertIn("dos_patas_del_mismo_partido", cr.risk_violations([l for l in self.legs if l["match_id"] == "m0"]))
        self.assertIn("demasiadas_de_la_misma_liga", cr.risk_violations(self.pick(OVER[0], {"m0", "m2"}) + self.pick(UNDER[1], {"m4"})))

    def test_ventana_horaria(self):
        us = [unit(i, [entrada(OVER[0] if i % 2 else UNDER[1], 1.5, 0.7)], liga=f"L{i}", hora="2026-10-14T20:30:00Z") for i in range(5)]
        self.assertIn("demasiadas_en_la_misma_ventana_horaria", cr.risk_violations(legs_of(us)[:4]))


class Combinadas(unittest.TestCase):
    def setUp(self):
        self.us = [unit(i, [entrada(OVER[0], 1.5, 0.70 - 0.01 * i), entrada(UNDER[1], 1.45, 0.72 - 0.01 * i)], liga=f"L{i}", hora=f"2026-10-14T{8 + 2 * i:02d}:00:00Z") for i in range(8)]
        self.legs = legs_of(self.us)

    def test_cada_pata_cumple_limite_y_una_por_partido_y_rango(self):
        out = cr.build_combos(self.legs, targets=(("x2", 2.0, 2.4, 3),))
        cs = out["x2"]["combinadas"]
        self.assertTrue(cs)
        for c in cs:
            self.assertTrue(2.0 <= c["cuota_total"] <= 2.4)
            self.assertTrue(all(p["cuota"] <= cr.MAX_LEG_ODDS for p in c["patas"]))
            ms = [p["leg_id"].split("|")[0] for p in c["patas"]]
            self.assertEqual(len(ms), len(set(ms)))
            self.assertEqual(c["preparacion_para_apostar"]["estado"], "NO_APTA")        # modelo sin validar
            self.assertEqual(c["estado_agentes"], "SIN_REVISION")

    def test_exposicion_no_repite_patas_ni_partidos_mas_de_lo_permitido(self):
        out = cr.build_combos(self.legs, targets=(("x2", 2.0, 2.4, 2), ("x3", 2.9, 3.6, 3)), policy=dict(cr.POLICY, top_por_objetivo=6))
        legs, ms = {}, {}
        for b in out.values():
            for c in b["combinadas"]:
                for p in c["patas"]:
                    legs[p["leg_id"]] = legs.get(p["leg_id"], 0) + 1
                    ms[p["leg_id"].split("|")[0]] = ms.get(p["leg_id"].split("|")[0], 0) + 1
        self.assertLessEqual(max(legs.values()), cr.POLICY["max_reuso_pata"])
        self.assertLessEqual(max(ms.values()), cr.POLICY["max_reuso_partido"])

    def test_sin_patas_con_precio_no_hay_combinadas_y_se_avisa(self):
        us = [unit(i, [entrada(OVER[0], None, 0.7)]) for i in range(5)]
        out = cr.build_combos(legs_of(us), targets=(("x2", 2.0, 2.4, 3),))
        self.assertEqual(out["x2"]["combinadas"], [])
        self.assertIsNotNone(out["x2"]["aviso"])

    def test_ninguna_combinada_es_apta_con_modelo_sin_validar_aunque_todo_lo_demas_cumpla(self):
        l = legs_of([unit(1, [entrada(OVER[0], 1.5, 0.7)])])[0]
        l["agentes"] = "aprobada"
        r = cr.combo_readiness([l], certified=True)
        self.assertEqual(r["incumplidos"], ["modelo_validado"])


class Agentes(unittest.TestCase):
    def reports(self, us, **over):
        out = {}
        for role in ar.ROLES:
            rep = {"agente": role, "version_contrato": 1, "run": "r", "limitaciones": [], "unidades": []}
            for u in us:
                r = {"unit_id": u["unit_id"], "nota": "", "excepciones": [], "evidencia": [f"paquete:{u['unit_id']}"]}
                if role == "deportivo":
                    r.update(solidez="MEDIA", factor_principal="forma", direccion_favorable="sin_sesgo", escenario_perdida="partido_cerrado")
                elif role == "cuantitativo":
                    r.update(consistencia_modelo="coherente", riesgo_correlacion="ninguno", validacion_aplicable="no_validado")
                elif role == "verificador":
                    r.update(disponibilidad="verificada_en_fuente", precio="referencia_agregador", discrepancias=["ninguna"], fuentes_consultadas=["paquete"])
                else:
                    r.update(objecion="ninguna", severidad="baja", recomendacion="mantener")
                r.update(over.get(role, {}))
                rep["unidades"].append(r)
            out[role] = rep
        return out

    def test_estado_por_pata_sin_revision_aprobada_y_rechazada(self):
        us = [unit(1, [entrada(OVER[0], 1.5, 0.7, estado="otra_fuente")]), unit(2, [entrada(OVER[0], 1.5, 0.7, estado="otra_fuente")])]
        # solo se revisa m1; además el deportivo la rebaja → degradada
        solo = self.reports(us[:1], deportivo={"solidez": "BAJA"})      # BAJA = degradada (fuera de combinadas, visible en rankings)
        st = cr.agent_status(us, solo)
        self.assertTrue(st[(us[0]["unit_id"], OVER[0])].startswith("degradada:deportivo:BAJA"))
        self.assertEqual(st[(us[1]["unit_id"], OVER[0])], "sin_revision")
        ok = cr.agent_status(us, self.reports(us[:1]))
        self.assertEqual(ok[(us[0]["unit_id"], OVER[0])], "aprobada")
        legs = legs_of(us, st)
        self.assertEqual([l["match_id"] for l in cr.eligible(legs)], ["m2"])             # la rechazada no entra; la sin revisión sí, rotulada

    def test_combinada_aprobada_solo_si_todas_las_patas_estan_aprobadas(self):
        us = [unit(i, [entrada(OVER[0], 1.5, 0.7)], liga=f"L{i}", hora=f"2026-10-14T{8 + 3 * i:02d}:00:00Z") for i in range(3)]
        legs = legs_of(us, cr.agent_status(us, self.reports(us[:2])))
        c = cr.build_combos(legs, targets=(("x2", 2.2, 2.3, 2),))["x2"]["combinadas"]
        self.assertTrue(c)
        self.assertEqual(c[0]["estado_agentes"], "APROBADA")          # las dos aprobadas van primero
        self.assertTrue(all(p["agentes"] == "aprobada" for p in c[0]["patas"]))

    def test_objecion_abierta_del_auditor_quita_la_aprobacion(self):
        us = [unit(1, [entrada(OVER[0], 1.5, 0.7), entrada(OVER[1], 1.5, 0.7)])]
        reps = self.reports(us)
        reps["auditor"]["unidades"][0][ar.OBJECTION_FIELD] = [{"entry_id": OVER[0], "agente": "cuantitativo", "campo": "consistencia_modelo", "problema": "dato_citado_incorrecto"}]
        st = cr.agent_status(us, reps)
        self.assertEqual(st[(us[0]["unit_id"], OVER[0])], "objetada:cuantitativo")
        self.assertEqual(st[(us[0]["unit_id"], OVER[1])], "aprobada")
        legs = legs_of(us, st)
        self.assertEqual(cr.combo_readiness([l for l in legs if l["entry_id"] == OVER[0]], True)["requisitos"]["revision_agentes_completa"], False)
        c = cr._combo_record("x", [l for l in legs if l["entry_id"] == OVER[0]], True)
        self.assertEqual(c["estado_agentes"], "OBJETADA")

    def test_degradada_sale_de_combinadas_pero_sigue_en_rankings_y_rechazada_sale_de_ambos(self):
        us = [unit(1, [entrada(OVER[0], None, 0.80), entrada(OVER[1], 1.6, 0.66)])]
        st = {(us[0]["unit_id"], OVER[0]): "degradada:deportivo:BAJA", (us[0]["unit_id"], OVER[1]): "rechazada:verificador:no_verificable"}
        legs = legs_of(us, st)
        self.assertEqual(cr.eligible(legs), [])
        ids = [x["leg_id"].split("|")[1] for x in cr.build_rankings(legs)["por_grupo"]["goles"]["mas_probables"]]
        self.assertEqual(ids, [OVER[0]])

    def test_mercado_no_ofrecido_por_la_api_no_se_oculta_de_los_rankings(self):
        us = [unit(1, [entrada(OVER[0], None, 0.80)])]
        reps = self.reports(us, verificador={"disponibilidad": "no_ofrecida", "precio": "sin_precio"})
        self.assertEqual(cr.agent_status(us, reps)[(us[0]["unit_id"], OVER[0])], "aprobada")

    def test_informe_con_errores_no_aprueba_nada(self):
        us = [unit(1, [entrada(OVER[0], 1.5, 0.7)])]
        reps = self.reports(us)
        reps["cuantitativo"]["unidades"][0]["consistencia_modelo"] = "quizás"
        self.assertEqual(cr.agent_status(us, reps)[(us[0]["unit_id"], OVER[0])], "sin_revision")


class Rankings(unittest.TestCase):
    def test_rankings_por_grupo_incluyen_sin_precio_con_cuota_minima_justa(self):
        us = [unit(1, [entrada(OVER[0], None, 0.80), entrada(OVER[1], 1.6, 0.66), entrada(UNDER[0], None, 0.30)])]
        r = cr.build_rankings(legs_of(us))
        g = r["por_grupo"]["goles"]
        ids = [x["leg_id"].split("|")[1] for x in g["mas_probables"]]
        self.assertEqual(ids, [OVER[0], OVER[1]])                     # 0.30 → cuota justa 3.3 > 2.10: no entra
        self.assertEqual(g["mas_probables"][0]["cuota_minima_justa"], 1.25)
        self.assertIsNone(g["mas_probables"][0]["cuota"])
        self.assertEqual([x["leg_id"].split("|")[1] for x in g["mayor_ev_teorico_con_precio"]], [OVER[1]])


class Ruta(unittest.TestCase):
    def test_la_ruta_esta_registrada_y_contiene_su_control(self):
        f = ".claude/skills/seleccion-final-picks/scripts/catalog_rankings.py"
        self.assertIn(f, cov.GENERATION_ROUTES)
        with open(os.path.join(REPO, f), encoding="utf-8") as fh:
            self.assertIn(cov.GENERATION_ROUTES[f]["marker"], fh.read())

    def test_no_nombra_casas_ni_usa_credenciales(self):
        with open(os.path.join(REPO, ".claude", "skills", "seleccion-final-picks", "scripts", "catalog_rankings.py"), encoding="utf-8") as fh:
            txt = fh.read().lower()
        for w in ("triunfobet", "bet365", "apikey", "api_key"):
            self.assertNotIn(w, txt)


if __name__ == "__main__":
    unittest.main()

class Multiplicador(unittest.TestCase):
    def setUp(self):
        self.us = [unit(i, [entrada(OVER[0], 1.5, 0.70), entrada(UNDER[1], 1.4, 0.72)], liga="L1" if i < 2 else f"L{i}", hora=f"2026-10-14T{8 + (0 if i < 2 else 3 * i):02d}:00:00Z") for i in range(5)]
        self.legs = legs_of(self.us)

    def test_cada_combinada_muestra_producto_aporte_y_nota_de_correlacion(self):
        combo = [l for l in self.legs if l["entry_id"] == OVER[0]][:2]          # dos overs de la misma liga y a la misma hora
        c = cr._combo_record("x", combo, True)
        self.assertEqual(c["multiplicador"], "1.5 × 1.5 = 2.25")
        self.assertAlmostEqual(c["cuota_total"], 2.25)
        self.assertAlmostEqual(sum(p["aporte_log_pct"] for p in c["patas"]), 100, delta=0.2)
        self.assertAlmostEqual(c["p_conjunta_independiente"], 0.49, places=3)
        self.assertIn("overs", c["nota_correlacion"])
        self.assertIn("misma liga", c["nota_correlacion"])
        solo = cr._combo_record("x", [self.legs[0], [l for l in self.legs if l["match_id"] == "m4" and l["entry_id"] == UNDER[1]][0]], True)
        self.assertIsNone(solo["nota_correlacion"])

    def test_entre_alternativas_comparables_se_reparte_por_grupo_y_liga(self):
        us = [unit(i, [entrada(OVER[0], 1.5, 0.70), entrada(UNDER[1], 1.5, 0.70)], liga=f"L{i}", hora=f"2026-10-14T{8 + 3 * i:02d}:00:00Z", grupo="goles" if i % 2 else "córners") for i in range(6)]
        legs = cr.legs_from_units(us)
        out = cr.build_combos(legs, False, targets=(("x2.25", 2.2, 2.3, 2),), policy=dict(cr.POLICY, top_por_objetivo=3, max_reuso_partido=1))
        usados = [(p["grupo"], p["partido"]) for c in out["x2.25"]["combinadas"] for p in c["patas"]]
        self.assertEqual(len(usados), len(set(p for _, p in usados)))           # sin repetir partido
        self.assertEqual({g for g, _ in usados}, {"goles", "córners"})          # ambas familias representadas

