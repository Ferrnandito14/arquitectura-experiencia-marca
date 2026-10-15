"""Fase 4: modelos propios ampliados (leg_model, count_model), backtest walk-forward / vs mercado y decisión de validación. Datos FICTICIOS: EJEMPLO — NO REAL."""
import datetime as dt
import json
import os
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

import helpers  # noqa: F401  (añade scripts/ al path)
import backtest_modelo as bt
import count_model as cm
import leg_model as lm
import market_catalog as mc
import market_coverage as cov

REPO = os.path.normpath(os.path.join(os.path.dirname(__file__), ".."))


def goal_rows(n=10):
    return [{"gf": 2, "ga": 1, "venue": "local" if i % 2 == 0 else "visitante", "ht_goals": (1, 0)} for i in range(n)]


class LegModelAmpliado(unittest.TestCase):
    def setUp(self):
        rows = goal_rows()
        self.mu, self.adv = lm.league_means([rows])
        self.share = lm.half_share(rows, rows)
        self.p = lm.model_probs(rows, rows, self.mu, self.adv, share=self.share)

    def test_coherencia_de_resultados_y_derivados(self):
        p = self.p
        self.assertAlmostEqual(p["p1"] + p["px"] + p["p2"], 1.0, places=3)
        self.assertAlmostEqual(p["12"], p["p1"] + p["p2"], places=9)
        self.assertAlmostEqual(p["dnb_home"] + p["dnb_away"], 1.0, places=9)
        self.assertAlmostEqual(p["ht_p1"] + p["ht_px"] + p["ht_p2"], 1.0, places=3)

    def test_hándicaps_de_media_linea_son_complementarios(self):
        for L in lm.HANDICAP_HALF:
            self.assertAlmostEqual(self.p[f"ah_home_{L:+.1f}"] + self.p[f"ah_away_{-L:+.1f}"], 1.0, places=3)

    def test_goles_por_equipo_son_monotonos_y_coinciden_con_el_total(self):
        self.assertGreater(self.p["home_over_0.5"], self.p["home_over_1.5"])
        self.assertGreater(self.p["home_over_1.5"], self.p["home_over_2.5"])
        self.assertGreater(self.p["over_0.5"], max(self.p["home_over_0.5"], self.p["away_over_0.5"]) - 1e-9)       # el total supera a cada equipo por separado

    def test_primera_parte_solo_si_se_mide_la_fraccion(self):
        rows = goal_rows()
        self.assertNotIn("ht_over_0.5", lm.model_probs(rows, rows, self.mu, self.adv))
        self.assertIsNone(lm.half_share([], []))
        self.assertAlmostEqual(self.share, 1 / 3, places=6)                                                        # 1 gol en la 1.ª parte de 3 finales
        self.assertTrue(0 < self.share < 1)

    def test_no_usa_cuotas(self):
        import inspect
        names = set(lm.model_probs.__code__.co_names) | set(lm.model_probs.__code__.co_varnames)
        self.assertFalse([n for n in names if any(x in n.lower() for x in ("odds", "cuota", "novig", "price"))])
        self.assertNotIn("odds", inspect.signature(lm.model_probs).parameters)


class CountModel(unittest.TestCase):
    def rows(self, own, opp, n=10):
        return [{"venue": "local" if i % 2 else "visitante", "own": own, "opp": opp} for i in range(n)]

    def stats(self):
        return count_stats

    def test_cola_monotona_y_binomial_negativa_con_mas_cola_que_poisson(self):
        a = [cm.p_over(10, None, L) for L in (7.5, 9.5, 11.5, 13.5)]
        self.assertEqual(a, sorted(a, reverse=True))
        self.assertGreater(cm.p_over(10, 3.0, 17.5), cm.p_over(10, None, 17.5))                    # sobredispersión: cola derecha más pesada
        self.assertAlmostEqual(cm.p_over(0, None, 0.5), 0.0)

    def test_dispersion_por_momentos(self):
        self.assertIsNone(cm.dispersion([5] * 30))                                               # sin varianza extra: Poisson
        self.assertIsNone(cm.dispersion([1, 2, 3]))                                              # pocos datos
        r = cm.dispersion([0, 10] * 20)
        self.assertTrue(r is not None and r > 0)

    def test_estadisticas_de_liga_exigen_muestra(self):
        self.assertIsNone(cm.league_stats([(5, 4)] * 10))
        st = cm.league_stats([(6, 4), (5, 5), (7, 3)] * 10)
        self.assertEqual(st["n"], 30)
        self.assertAlmostEqual(st["mu"], 5.0, places=6)
        self.assertGreater(st["adv"], 1.0)

    def test_encogimiento_hacia_la_media_de_liga(self):
        att, dfn = cm.strengths(self.rows(12, 3), 5.0, k=8)
        self.assertTrue(1.0 < att < 12 / 5.0)                                                    # entre 1 y la fuerza bruta
        self.assertTrue(dfn < 1.0)
        self.assertEqual(cm.strengths([], 5.0), (1.0, 1.0))

    def test_arbitro_estricto_sube_las_tarjetas_esperadas(self):
        st = cm.league_stats([(2, 2), (3, 2), (2, 3)] * 10)
        base = cm.model_probs("cards", self.rows(2, 2), self.rows(2, 2), st, [3.5], [])
        estricto = cm.model_probs("cards", self.rows(2, 2), self.rows(2, 2), st, [3.5], [], ref_factor=cm.referee_factor(7.0, 20, 4.6))
        self.assertGreater(estricto["cards_total_over_3.5"], base["cards_total_over_3.5"])
        self.assertEqual(cm.referee_factor(None, 0, 4.6), 1.0)

    def test_sin_estadisticas_de_liga_no_hay_modelo(self):
        self.assertEqual(cm.model_probs("corners", self.rows(5, 5), self.rows(5, 5), None, [9.5], []), {})

    def test_claves_que_el_catalogo_espera(self):
        st = {"mu": 5.0, "adv": 1.1, "r_total": None, "r_team": None, "n": 100}
        keys = set(cm.model_probs("corners", self.rows(5, 4), self.rows(5, 4), st, cm.CORNER_TOTAL, cm.CORNER_TEAM))
        keys |= set(cm.model_probs("cards", self.rows(2, 2), self.rows(2, 2), st, cm.CARD_TOTAL, cm.CARD_TEAM))
        probe = cov._probe_model_keys()
        for e in mc.CATALOG:
            if e["model"] in ("count:corners", "count:cards"):
                self.assertIn(cov.model_key(e, probe), keys | probe, e["id"])


class WalkForward(unittest.TestCase):
    def liga(self, n_days=40, per_day=3):
        rows, base = [], dt.date(2026, 3, 1)
        teams = [f"T{i}" for i in range(8)]
        k = 0
        for d in range(n_days):
            for j in range(per_day):
                h, a = teams[(d + j) % 8], teams[(d + j + 3) % 8]
                rows.append({"id": str(k), "fecha": (base + dt.timedelta(days=d)).isoformat(), "local": h, "visitante": a, "gl": (k * 7) % 4, "gv": (k * 5) % 3,
                             "tarjetas": [1 + k % 3, 1 + (k * 2) % 3], "corners": [4 + k % 4, 3 + k % 3], "arbitro": f"R{k % 3}"})
                k += 1
        return rows

    def test_ningun_partido_se_predice_con_informacion_de_su_mismo_dia_ni_posterior(self):
        rows = self.liga()
        objetivo = rows[-1]
        mismo_dia_extremo = dict(rows[-2], id="x", local=objetivo["local"], visitante="T7", gl=9, gv=0, fecha=objetivo["fecha"])
        p1 = [p for p in bt.walk_forward({"1": rows}) if p["partido"] == objetivo["id"]]
        p2 = [p for p in bt.walk_forward({"1": rows + [mismo_dia_extremo]}) if p["partido"] == objetivo["id"]]
        self.assertTrue(p1)
        self.assertEqual([(x["mercado"], x["p"], x["p_base"]) for x in p1], [(x["mercado"], x["p"], x["p_base"]) for x in p2])
        # y un partido FUTURO tampoco influye
        futuro = dict(rows[0], id="f", fecha="2027-01-01", gl=9, gv=9)
        p3 = [p for p in bt.walk_forward({"1": rows + [futuro]}) if p["partido"] == objetivo["id"]]
        self.assertEqual([x["p"] for x in p1], [x["p"] for x in p3])

    def test_exige_partidos_previos_minimos(self):
        rows = self.liga(n_days=3)
        self.assertEqual(bt.walk_forward({"1": rows}), [])

    def test_familias_y_resultados_coherentes(self):
        preds = bt.walk_forward({"1": self.liga()})
        fams = {p["familia"] for p in preds}
        self.assertTrue({"goals_total", "btts", "1x2", "dc", "team_goals", "corners_total", "cards_total"} <= fams)
        for p in preds:
            self.assertTrue(0 <= p["p"] <= 1 and 0 < p["p_base"] < 1 and p["y"] in (0, 1))
        r = {p["mercado"]: p["y"] for p in preds if p["partido"] == preds[-1]["partido"] and p["familia"] == "1x2"}
        self.assertEqual(sum(r.values()), 1)                                                     # exactamente un resultado 1X2

    def test_resumen_con_ic_y_calibracion(self):
        wf = bt.summarize_walk_forward(bt.walk_forward({"1": self.liga()}), dict(bt.POLICY, bootstrap=100))
        g = wf["goals_total"]
        self.assertLessEqual(g["skill_ic"][0], g["skill"])
        self.assertGreaterEqual(g["skill_ic"][1], g["skill"])
        self.assertEqual(sum(b["n"] for b in g["calibracion"]), g["predicciones"])
        self.assertIn(g["vs_tasa_base"], ("supera", "no_supera", "no_concluyente"))
        self.assertEqual(g["vs_tasa_base"], "no_concluyente")                                    # con pocos partidos jamás «supera»


class Decision(unittest.TestCase):
    def wf(self, fam, estado, n=500):
        return {fam: {"partidos": n, "vs_tasa_base": estado}}

    def test_suficiente_solo_si_supera_la_tasa_base_y_no_es_peor_que_el_mercado(self):
        v = bt.decide_validation(self.wf("goals_total", "supera"), {"goals_total": {"vs_mercado": "no_peor", "partidos": 250}})
        self.assertEqual((v["nivel"], v["familias"]["goals_total"]["nivel"]), ("suficiente", "suficiente"))
        v = bt.decide_validation(self.wf("goals_total", "supera"), {"goals_total": {"vs_mercado": "no_concluyente", "partidos": 90}})
        self.assertEqual(v["familias"]["goals_total"]["nivel"], "parcial")
        v = bt.decide_validation(self.wf("goals_total", "supera"), {"goals_total": {"vs_mercado": "peor", "partidos": 300}})
        self.assertEqual(v["nivel"], "parcial")
        v = bt.decide_validation(self.wf("goals_total", "no_concluyente"), {"goals_total": {"vs_mercado": "no_peor", "partidos": 300}})
        self.assertEqual(v["nivel"], "insuficiente")

    def test_familias_sin_cuotas_historicas_nunca_pasan_de_parcial(self):
        v = bt.decide_validation(self.wf("cards_total", "supera"), {})
        self.assertEqual(v["familias"]["cards_total"]["nivel"], "parcial")
        self.assertEqual(v["familias"]["cards_total"]["vs_mercado"], "no_evaluable_sin_cuotas_historicas")
        self.assertEqual(v["nivel"], "parcial")

    def test_global_suficiente_exige_todas_las_familias(self):
        wf = dict(self.wf("goals_total", "supera"), **self.wf("btts", "no_concluyente"))
        vm = {"goals_total": {"vs_mercado": "no_peor", "partidos": 300}, "btts": {"vs_mercado": "no_peor", "partidos": 300}}
        self.assertEqual(bt.decide_validation(wf, vm)["nivel"], "parcial")

    def test_politica_declarada_en_el_resultado(self):
        v = bt.decide_validation({}, {})
        self.assertEqual(v["reglas"]["n_min_walk_forward"], bt.POLICY["n_min_walk_forward"])
        self.assertIn("política", v["reglas"]["nota"])

    def test_bootstrap_es_determinista_y_el_ic_contiene_el_punto(self):
        cl = [(0.2, 0.25, 1)] * 30 + [(0.3, 0.25, 1)] * 20
        a = bt.skill_ci(cl, 200, 0.95, 7)
        b = bt.skill_ci(cl, 200, 0.95, 7)
        self.assertEqual(a, b)
        self.assertTrue(a[1] <= a[0] <= a[2])
        d = bt.bootstrap_diff(cl, 200, 0.95, 7)
        self.assertTrue(d[1] <= d[0] <= d[2])
        self.assertIsNone(bt.skill_ci([], 10, 0.95, 1))


class FakeProvider:
    """Imita ApifootballOddsProvider: consultas con su instante y filas de casa con odd_date."""
    def __init__(self, ts, rows):
        self.queries = [{"ts": ts, "from": "2026-10-13", "to": "2026-10-14", "match_id": None, "url": "u", "cache": "c", "filas": len(rows)}]
        self.rows = {(str(r["match_id"]), r["odd_bookmakers"]): r for r in rows}

    def _cover(self, match):
        return self.queries[0]


def odds(mid, book, date, o1="2.0", ox="3.4", o2="3.6", over="1.9", under="1.95"):
    return {"match_id": mid, "odd_bookmakers": book, "odd_date": date, "odd_1": o1, "odd_x": ox, "odd_2": o2, "o+2.5": over, "u+2.5": under, "o+1.5": "1.3", "u+1.5": "3.5", "o+3.5": "3.2", "u+3.5": "1.3",
            "bts_yes": "1.8", "bts_no": "1.95", "odd_1x": "1.3", "odd_12": "1.3", "odd_x2": "1.7"}


class VsMercado(unittest.TestCase):
    def setUp(self):
        r = lambda v: {"gf": 2, "ga": 1, "venue": v, "misma_competicion": True}
        self.mx = {f"m{i}": {"form": {"local": [r("local")] * 8, "visitante": [r("visitante")] * 8}} for i in range(4)}
        self.inv = [{"match_id": f"m{i}", "competition": "Liga", "source_match_ids": {"apifootball": str(100 + i)}, "normalized_datetime_utc": "2026-10-13T20:00:00Z"} for i in range(4)]
        self.results = {str(100 + i): (2, 1) for i in range(4)}

    def rows(self, i, date="2026-10-13 12:00:00"):
        return [odds(str(100 + i), b, date) for b in ("A", "B", "C")]

    def test_solo_entran_partidos_con_precios_previos_al_inicio_y_se_cuentan_los_excluidos(self):
        rows = self.rows(0) + self.rows(1, "2026-10-13 21:00:00") + self.rows(2)
        prov = FakeProvider("2026-10-13T02:00:00Z", rows)
        recs, info = bt.build_market_records(self.inv[:3], self.mx, prov, self.results)
        usados = {r["partido"] for r in recs}
        self.assertEqual(usados, {"m0", "m2"})                                                  # m1: todas las filas son POSTERIORES al inicio
        self.assertEqual(info["excluidos"]["sin_filas_de_casa_previas_al_inicio"], 1)
        self.assertEqual(info["partidos_usados"], 2)

    def test_consulta_de_cuotas_posterior_al_inicio_excluye_al_partido(self):
        prov = FakeProvider("2026-10-13T20:30:00Z", self.rows(0))
        recs, info = bt.build_market_records(self.inv[:1], self.mx, prov, self.results)
        self.assertEqual(recs, [])
        self.assertEqual(info["excluidos"]["consulta_de_cuotas_posterior_al_inicio"], 1)

    def test_sin_resultado_final_o_sin_historial_no_entra(self):
        prov = FakeProvider("2026-10-13T02:00:00Z", self.rows(0))
        recs, info = bt.build_market_records(self.inv[:1], self.mx, prov, {})
        self.assertEqual((recs, info["excluidos"]["sin_resultado_final"]), ([], 1))
        mx = {"m0": {"form": {"local": [], "visitante": []}}}
        recs, info = bt.build_market_records(self.inv[:1], mx, prov, self.results)
        self.assertEqual(info["excluidos"]["sin_historial"], 1)

    def test_registros_tienen_probabilidad_de_mercado_sin_margen_y_resultado(self):
        prov = FakeProvider("2026-10-13T02:00:00Z", self.rows(0))
        recs, _ = bt.build_market_records(self.inv[:1], self.mx, prov, self.results)
        r = next(x for x in recs if x["mercado"] == "1" and x["familia"] == "1x2")
        q = [1 / 2.0, 1 / 3.4, 1 / 3.6]
        self.assertAlmostEqual(r["p_mercado"], q[0] / sum(q), places=3)
        self.assertEqual(r["y"], 1)
        self.assertEqual(next(x for x in recs if x["mercado"] == "over_2.5")["y"], 1)            # 2+1 = 3 goles
        self.assertEqual(next(x for x in recs if x["mercado"] == "over_3.5")["y"], 0)

    def test_evaluacion_con_pocos_partidos_es_no_concluyente_y_la_mezcla_se_informa(self):
        prov = FakeProvider("2026-10-13T02:00:00Z", self.rows(0) + self.rows(2))
        recs, _ = bt.build_market_records(self.inv[:3], self.mx, prov, self.results)
        ev = bt.evaluate_vs_market(recs, dict(bt.POLICY, bootstrap=100))
        self.assertEqual(ev["goals_total"]["vs_mercado"], "no_concluyente")
        self.assertEqual(set(ev["goals_total"]["mezclas_brier"]), {"w=0", "w=0.25", "w=0.5", "w=0.75", "w=1"})


class ValidacionEnLaCobertura(unittest.TestCase):
    def entry(self, eid):
        return mc.BY_ID[eid]

    def test_el_archivo_actual_deja_todo_sin_validar(self):
        self.assertIn(cov.MODEL_VALIDATION["nivel"], ("insuficiente", "parcial"))
        for eid in ("goles.total.over.2.5", "corners.total.over.9.5", "resultado.1x2.home"):
            self.assertFalse(cov.model_validated(self.entry(eid)), eid)

    def test_la_validacion_es_por_familia_y_el_resto_sigue_sin_validar(self):
        fams = {"goals_total": {"nivel": "suficiente"}, "corners_total": {"nivel": "parcial"}}
        with mock.patch.dict(cov.MODEL_VALIDATION, {"nivel": "parcial", "familias": fams}):
            self.assertTrue(cov.model_validated(self.entry("goles.total.over.2.5")))
            self.assertFalse(cov.model_validated(self.entry("corners.total.over.9.5")))          # parcial: nunca habilita
            self.assertFalse(cov.model_validated(self.entry("resultado.dnb.home")))              # sin familia probada
            self.assertEqual(cov.validation_level(self.entry("resultado.dnb.home")), "no_evaluada")
            self.assertEqual(cov.validation_level(self.entry("corners.total.over.9.5")), "parcial")

    def test_global_suficiente_habilita_como_antes(self):
        with mock.patch.dict(cov.MODEL_VALIDATION, {"nivel": "suficiente"}):
            self.assertTrue(cov.model_validated(self.entry("goles.total.over.2.5")))

    def test_carga_desde_archivo_y_nunca_sube_a_mano(self):
        d = tempfile.mkdtemp()
        p = os.path.join(d, "v.json")
        with open(p, "w", encoding="utf-8") as f:
            json.dump({"nivel": "suficiente", "familias": {"btts": {"nivel": "suficiente"}}, "motivo": "x", "referencia": "r", "blend_weight": 0.3}, f)
        saved = dict(cov.MODEL_VALIDATION)
        try:
            cov.load_model_validation(p)
            self.assertEqual((cov.MODEL_VALIDATION["nivel"], cov.MODEL_VALIDATION["blend_weight"]), ("suficiente", 0.3))
        finally:
            cov.MODEL_VALIDATION.clear()
            cov.MODEL_VALIDATION.update(saved)
        self.assertNotEqual(cov.MODEL_VALIDATION["nivel"], "suficiente")


class DatasetSinPonderacionArbitraria(unittest.TestCase):
    def test_p_central_es_la_del_mercado_mientras_el_modelo_no_este_validado(self):
        import test_market_catalog as T
        d = tempfile.mkdtemp()
        case = T.RutasProtegidas()
        case._ligas_dir(d)
        r = case._exec("build_dataset.py", "--run", d)
        self.assertEqual(r.returncode, 0, r.stderr)
        with open(os.path.join(d, "ligas", "dataset.json"), encoding="utf-8") as f:
            ds = json.load(f)
        for m in ds:
            for l in m["patas"]:
                self.assertEqual(l["p_central"], l["p_mercado"])
                self.assertIn("modelo no validado", l["p_central_metodo"])
                self.assertIsNotNone(l["p_modelo"])                                              # el modelo se muestra aparte


if __name__ == "__main__":
    unittest.main()
