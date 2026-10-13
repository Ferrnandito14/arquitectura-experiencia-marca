import ast, os, tempfile, unittest
from datetime import datetime, timezone
import helpers
import common, level1, inventory

NOW = datetime(2026, 10, 12, 23, 45, tzinfo=timezone.utc)


def hist(n, gf=2, ga=1, corners=(6, 5), yellow=(2, 2), red=(0, 0)):
    return [{"date": f"2026-09-{i+1:02d}", "competition": "Championship", "venue": "local", "opponent": f"R{i}", "gf": gf, "ga": ga,
             "ht_goals": (1, 0), "corners": corners, "yellow": yellow, "red": red, "shots": (10, 8), "sot": (4, 3), "fouls": (11, 12), "referee": "X"}
            for i in range(n)]


class FakeProvider:
    name = "football-data"

    def __init__(self, covered=True, fail=False, n=10):
        self.covered, self.fail, self.n, self.calls = covered, fail, n, 0

    def covers(self, m):
        return self.covered

    def team_history(self, m, team, before):
        self.calls += 1
        if self.fail:
            raise level1.ProviderUnavailable("caído")
        return hist(self.n)


def make_run(tmp, matches):
    inv = {"meta": {"date": "2026-10-13", "raw_counts": {"x": len(matches)}}, "matches": matches, "raw_duplicates": []}
    common.write_json_atomic(os.path.join(tmp, "inventory.json"), inv)
    return tmp


def match(i, required=True, odds=None, div="E1"):
    return {"match_id": f"m-{i}", "home_team": f"H{i}", "away_team": f"A{i}", "competition": "Championship", "country": "England",
            "normalized_datetime_utc": "2026-10-13T18:45:00Z", "normalized_datetime_local": "2026-10-13T14:45:00-04:00",
            "calendar_verification_status": "CONFIRMADO" if required else "NO_CONFIRMADO",
            "prematch_eligibility": "ELEGIBLE" if required else "PENDIENTE_DE_VERIFICAR", "event_status": "PROGRAMADO",
            "analysis_required": required, "disposition": "x", "sports_analysis_status": "PENDIENTE", "market_analysis_status": "PENDIENTE",
            "discrepancies": [], "extra": {"div": div, "odds": odds or {}}}


class MarketStates(unittest.TestCase):
    def ev(self, m, provider):
        return level1.evaluate_match(m, provider, helpers.POLICY, "2026-10-12T23:45:00Z")

    def test_stats_without_price_is_partial_and_price_unconfirmed(self):
        e = self.ev(match(1), FakeProvider())
        mk = e["markets"]["goles.btts"]
        self.assertEqual(mk["evaluation_status"], "PARCIAL")
        self.assertEqual(mk["statistics_availability_status"], "SUFICIENTES")
        self.assertTrue(mk["price_verification_status"].startswith("PRECIO_NO_CONFIRMADO"))
        self.assertEqual(mk["market_availability_status"], "NOT_CHECKED")       # no encontrar cuota != mercado inexistente
        self.assertIn("sin cuota", mk["not_evaluable_reason"])

    def test_price_present_market_available_but_still_unconfirmed(self):
        odds = {"B365H": "2.4", "B365D": "3.4", "B365A": "2.8", "B365>2.5": "1.9", "B365<2.5": "1.9"}
        e = self.ev(match(1, odds=odds), FakeProvider())
        p = e["markets"]["resultado.1x2"]
        self.assertEqual(p["market_availability_status"], "VERIFICADO_DISPONIBLE_EN_UNA_CASA")
        self.assertIn("una sola casa", p["price_verification_status"])
        self.assertAlmostEqual(sum(p["price"]["sin_margen_proporcional"]), 1.0, places=3)
        self.assertEqual(e["markets"]["goles.over_2_5"]["price"]["cuotas"], [1.9, 1.9])

    def test_uncovered_league_is_no_evaluable_with_evidence_not_omitted(self):
        e = self.ev(match(1, div=None), FakeProvider(covered=False))
        self.assertEqual(e["sports_analysis_status"], "NO_EVALUABLE_TRAS_INTENTOS")
        self.assertTrue(all(m["evaluation_status"] == "NO_EVALUABLE" for m in e["markets"].values()))
        provs = {a["provider"]: a["resultado"] for a in e["attempts"]}
        self.assertIn("fotmob", provs)
        self.assertIn("excluida", provs["fotmob"])          # evidencia: no consultada por política, NO "consultada"
        self.assertEqual(len(e["markets"]), len(level1.ALL_MARKETS))

    def test_unsupported_stat_in_covered_league_is_no_evaluable_with_reason(self):
        e = self.ev(match(1), FakeProvider())
        fj = e["markets"]["otros.fueras_de_juego"]
        self.assertEqual(fj["evaluation_status"], "NO_EVALUABLE")
        self.assertIn("no incluye", fj["not_evaluable_reason"])

    def test_small_sample_marks_partial_statistics(self):
        e = self.ev(match(1), FakeProvider(n=5))
        self.assertEqual(e["markets"]["goles.btts"]["statistics_availability_status"], "PARCIALES")

    def test_frequencies_use_calc_wilson_and_are_descriptive(self):
        b = level1.freq_block(7, 10, "x")
        lo, hi = level1.calc.wilson(7, 10)
        self.assertEqual((b["wilson95"][0], b["wilson95"][1]), (round(lo, 3), round(hi, 3)))
        self.assertEqual(b["tipo"], "estadistica_descriptiva_no_probabilidad")
        self.assertIsNone(level1.freq_block(0, 0, "vacio"))

    def test_sample_note_not_full_season(self):
        self.assertIn("NO es una muestra de temporada completa", self.ev(match(1), FakeProvider())["sample_note"])

    def test_does_not_reimplement_math(self):
        with open(level1.__file__, encoding="utf-8") as fh:
            src = fh.read()
        tree = ast.parse(src)
        defs = {n.name for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)}
        self.assertFalse({"wilson", "implied_prob", "novig_probs", "ev_unit"} & defs)
        self.assertNotIn("math.sqrt", src)
        self.assertNotIn("1 / c", src.replace("calc.implied_prob", ""))
        for needed in ("calc.wilson", "calc.novig_probs", "calc.implied_prob"):
            self.assertIn(needed, src)


class Queue(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()

    def test_only_required_matches_queued_others_have_disposition(self):
        make_run(self.tmp, [match(1), match(2, required=False)])
        st, mx = level1.process(self.tmp, FakeProvider(), helpers.POLICY, now=NOW)
        self.assertEqual(st["matches"]["m-2"]["status"], "NO_REQUIERE_ANALISIS")
        self.assertIn("m-1", mx["matches"])
        self.assertNotIn("m-2", mx["matches"])

    def test_resume_after_cut_does_not_repeat_completed_work(self):
        make_run(self.tmp, [match(i) for i in range(1, 6)])
        p = FakeProvider()
        level1.process(self.tmp, p, helpers.POLICY, limit=2, now=NOW)          # "corte" tras 2 partidos
        st = common.read_json(os.path.join(self.tmp, "state.json"))["matches"]
        self.assertEqual(sorted(v["status"] for v in st.values()).count("COMPLETADO"), 2)
        calls_after_first = p.calls
        st2, _ = level1.process(self.tmp, p, helpers.POLICY, now=NOW)
        self.assertEqual(p.calls - calls_after_first, 3 * 2)                    # sólo los 3 pendientes (2 equipos c/u)
        self.assertTrue(all(v["status"] == "COMPLETADO" for v in st2["matches"].values()))

    def test_interrupted_en_curso_is_reprocessed(self):
        make_run(self.tmp, [match(1)])
        common.write_json_atomic(os.path.join(self.tmp, "state.json"), {"matches": {"m-1": {"status": "EN_CURSO", "attempts": 1}}})
        st, mx = level1.process(self.tmp, FakeProvider(), helpers.POLICY, now=NOW)
        self.assertEqual(st["matches"]["m-1"]["status"], "COMPLETADO")
        self.assertEqual(st["matches"]["m-1"]["attempts"], 2)

    def test_recoverable_error_then_needs_intervention_after_max_attempts(self):
        make_run(self.tmp, [match(1)])
        def boom(*a, **k):
            raise RuntimeError("fallo")
        for i in range(level1.MAX_ATTEMPTS):
            st, _ = level1.process(self.tmp, FakeProvider(), helpers.POLICY, evaluator=boom, now=NOW)
            expected = "ERROR_RECUPERABLE" if i < level1.MAX_ATTEMPTS - 1 else "ERROR_REQUIERE_INTERVENCION"
            self.assertEqual(st["matches"]["m-1"]["status"], expected)
        self.assertIn("RuntimeError", st["matches"]["m-1"]["last_error"])

    def test_no_evaluable_records_reason_and_evidence(self):
        make_run(self.tmp, [match(1, div=None)])
        st, _ = level1.process(self.tmp, FakeProvider(covered=False), helpers.POLICY, now=NOW)
        s = st["matches"]["m-1"]
        self.assertEqual(s["status"], "NO_EVALUABLE_TRAS_INTENTOS")
        self.assertTrue(s["reason"] and s["evidence"])

    def test_provider_failure_does_not_mark_completed(self):
        make_run(self.tmp, [match(1)])
        st, _ = level1.process(self.tmp, FakeProvider(fail=True), helpers.POLICY, now=NOW)
        self.assertEqual(st["matches"]["m-1"]["status"], "NO_EVALUABLE_TRAS_INTENTOS")
        self.assertTrue(any("acceso fallido" in a["resultado"] for a in st["matches"]["m-1"]["evidence"]))

    def test_matrix_csv_written_with_every_market_row(self):
        make_run(self.tmp, [match(1)])
        level1.process(self.tmp, FakeProvider(), helpers.POLICY, now=NOW)
        with open(os.path.join(self.tmp, "matrix.csv"), encoding="utf-8") as fh:
            lines = fh.read().strip().splitlines()
        self.assertEqual(len(lines), 1 + len(level1.ALL_MARKETS))


if __name__ == "__main__":
    unittest.main()
