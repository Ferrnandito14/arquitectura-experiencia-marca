import json, os, tempfile, unittest
import helpers
import common, coverage_report, level1
from test_level1 import match, make_run, FakeProvider
from datetime import datetime, timezone

NOW = datetime(2026, 10, 12, 23, 45, tzinfo=timezone.utc)


def prep(matches, provider=None, process=True):
    tmp = tempfile.mkdtemp()
    make_run(tmp, matches)
    if process:
        level1.process(tmp, provider or FakeProvider(), helpers.POLICY, now=NOW)
    else:
        st = level1.init_state({"matches": {}}, common.read_json(os.path.join(tmp, "inventory.json")))
        level1.save_state(tmp, st)
    return tmp


class Gate(unittest.TestCase):
    def test_gate_FAILS_when_confirmed_eligible_match_has_no_basic_evaluation(self):
        tmp = prep([match(1), match(2)], process=False)
        r = coverage_report.compute(tmp)
        self.assertEqual(r["exit_code"], 3)
        self.assertIn("BLOQUEADO", r["verdict"])
        self.assertEqual(r["pending"], 2)
        self.assertEqual(coverage_report.main(["--run", tmp]), 3)

    def test_gate_blocks_even_if_one_of_many_is_pending(self):
        tmp = prep([match(i) for i in range(1, 5)])
        st = common.read_json(os.path.join(tmp, "state.json"))
        st["matches"]["m-3"]["status"] = "PENDIENTE"
        common.write_json_atomic(os.path.join(tmp, "state.json"), st)
        r = coverage_report.compute(tmp)
        self.assertEqual((r["exit_code"], r["pending"], r["pending_ids"]), (3, 1, ["m-3"]))

    def test_no_evaluable_without_reason_or_evidence_counts_as_pending_and_problem(self):
        tmp = prep([match(1, div=None)], FakeProvider(covered=False))
        st = common.read_json(os.path.join(tmp, "state.json"))
        del st["matches"]["m-1"]["evidence"]
        common.write_json_atomic(os.path.join(tmp, "state.json"), st)
        r = coverage_report.compute(tmp)
        self.assertEqual(r["exit_code"], 3)
        self.assertTrue(r["problems"] and "sin motivo o sin evidencia" in r["problems"][0][1])

    def test_no_evaluable_with_reason_and_evidence_is_processed_but_restricted(self):
        tmp = prep([match(1, div=None)], FakeProvider(covered=False))
        r = coverage_report.compute(tmp)
        self.assertEqual((r["processed"], r["pending"], r["evaluated_sufficiently"]), (1, 0, 0))
        self.assertEqual(r["exit_code"], 4)
        self.assertIn("RANKING PROVISIONAL RESTRINGIDO", r["verdict"])

    def test_error_states_block(self):
        tmp = prep([match(1)], process=False)
        st = common.read_json(os.path.join(tmp, "state.json"))
        st["matches"]["m-1"].update(status="ERROR_REQUIERE_INTERVENCION", last_error="x")
        common.write_json_atomic(os.path.join(tmp, "state.json"), st)
        r = coverage_report.compute(tmp)
        self.assertEqual(r["exit_code"], 3)
        self.assertTrue(r["problems"])

    def test_processed_without_data_attempt_is_reported_and_markets_not_overstated(self):
        tmp = prep([match(1, div=None), match(2, div=None)], FakeProvider(covered=False))
        r = coverage_report.compute(tmp)
        self.assertEqual((r["processed"], r["processed_without_any_data_attempt"]), (2, 2))
        self.assertEqual((r["markets_examined"], r["markets_not_checked"]), (0, 2 * len(level1.ALL_MARKETS)))
        self.assertEqual(r["coverage_markets_pct"], 0.0)       # antes se mostraba 100 %: nadie examinó esos mercados
        self.assertEqual(r["exit_code"], 4)

    def test_inventory_state_mismatch_blocks_and_orphans_flagged(self):
        tmp = prep([match(1)])
        inv = common.read_json(os.path.join(tmp, "inventory.json"))
        inv["matches"][0]["sports_analysis_status"] = "PENDIENTE"          # inventario regenerado sin conservar el avance
        common.write_json_atomic(os.path.join(tmp, "inventory.json"), inv)
        r = coverage_report.compute(tmp)
        self.assertEqual(r["exit_code"], 3)
        self.assertTrue(any("inventario dice PENDIENTE" in b for _, b in r["problems"]))
        st = common.read_json(os.path.join(tmp, "state.json"))
        st["matches"]["m-fantasma"] = {"status": "COMPLETADO", "attempts": 1}
        common.write_json_atomic(os.path.join(tmp, "state.json"), st)
        self.assertTrue(any("huérfano" in b for _, b in coverage_report.compute(tmp)["problems"]))

    def test_empty_universe_is_never_a_definitive_ranking(self):
        tmp = prep([match(1, required=False)])
        r = coverage_report.compute(tmp)
        self.assertEqual(r["exit_code"], 4)
        self.assertEqual(r["required_confirmed_eligible"], 0)

    def test_systemic_family_limitation_prevents_definitive(self):
        # histórico completo, pero ninguna cuota ni estadística de fueras de juego en NINGÚN partido => familia 'otros' parcial por tiros; tarjetas ok...
        tmp = prep([match(i) for i in range(1, 4)])
        r = coverage_report.compute(tmp)
        self.assertEqual(r["pending"], 0)
        self.assertEqual(r["evaluated_sufficiently"], 3)
        # Level 1 nunca marca EVALUABLE (falta Nivel 2): hay mercados NO_EVALUABLES sistémicos => no es 'definitivo' sin nota
        self.assertGreater(r["markets_not_evaluable"], 0)

    def test_definitive_only_when_complete_and_no_systemic_gap(self):
        tmp = prep([match(1)])
        r = coverage_report.compute(tmp)
        r2 = dict(r)
        self.assertIn(r["exit_code"], (0, 4))     # 0 sólo si ninguna familia queda sin mercados evaluables
        fam_ok = r["systemic_families_without_any_evaluable"]
        self.assertEqual(r["exit_code"] == 0, not fam_ok and r["evaluated_sufficiently"] == r["required_confirmed_eligible"])


class Denominators(unittest.TestCase):
    def test_percentages_and_denominators(self):
        ms = [match(1), match(2), match(3), match(4, required=False)]
        ms[0]["event_status"] = "FINALIZADO"
        tmp = prep(ms)
        r = coverage_report.compute(tmp)
        self.assertEqual(r["unique_matches"], 4)
        self.assertEqual(r["required_confirmed_eligible"], 3)
        self.assertEqual((r["processed"], r["coverage_matches_den"], r["coverage_matches_pct"]), (3, 3, 100.0))
        self.assertEqual(r["markets_denominator"], 3 * len(level1.ALL_MARKETS))
        self.assertEqual(r["markets_examined"] + r["markets_not_checked"], r["markets_denominator"])
        self.assertEqual(r["confirmed"], 3)
        self.assertEqual(r["not_confirmed"], 1)
        self.assertEqual(r["started_or_finished"], 1)

    def test_not_checked_markets_are_not_counted_as_examined(self):
        tmp = prep([match(1)])
        mx = common.read_json(os.path.join(tmp, "matrix.json"))
        mx["matches"]["m-1"]["markets"]["corners.handicap"]["evaluation_status"] = "NOT_CHECKED"
        common.write_json_atomic(os.path.join(tmp, "matrix.json"), mx)
        r = coverage_report.compute(tmp)
        self.assertEqual(r["markets_not_checked"], 1)
        self.assertEqual(r["markets_examined"], len(level1.ALL_MARKETS) - 1)

    def test_report_text_has_verdict_and_writes_files(self):
        tmp = prep([match(1)])
        coverage_report.main(["--run", tmp])
        for f in ("coverage.json", "coverage_report.md"):
            self.assertTrue(os.path.exists(os.path.join(tmp, f)))
        with open(os.path.join(tmp, "coverage_report.md"), encoding="utf-8") as fh:
            self.assertIn("Veredicto de la puerta de cobertura", fh.read())


if __name__ == "__main__":
    unittest.main()
