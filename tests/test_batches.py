import json, os, tempfile, unittest
import helpers
import batches, common
from test_level1 import match


def inv_of(n, comps=("Liga A", "Liga B")):
    ms = []
    for i in range(n):
        m = match(i)
        m["competition"] = comps[i % len(comps)]
        ms.append(m)
    ms.append(dict(match(900, required=False), discrepancies=[{"kind": "hora"}]))
    return {"matches": ms}


def results_for(b, agent, drop=None, dup=None, pend=None, summary_only=False):
    out = []
    for bt in b["batches"]:
        if agent not in bt["agents"]:
            continue
        ids = list(bt["match_ids"])
        rows = [{"match_id": i, "review_status": "REVISADO", "corrections": []} for i in ids if i != drop]
        if dup:
            rows.append({"match_id": dup, "review_status": "REVISADO"})
        if pend:
            rows = [dict(r, review_status="PENDIENTE") if r["match_id"] == pend else r for r in rows]
        out.append({"agent": agent, "batch_id": bt["batch_id"], "rows": rows[:1] if summary_only else rows})
    return out


class Batches(unittest.TestCase):
    def setUp(self):
        self.inv = inv_of(40)
        self.b = batches.make_batches(self.inv, {"matches": {}}, max_chars=2000)

    def test_every_required_match_in_exactly_one_batch_size_from_volume(self):
        ids = [i for bt in self.b["batches"] for i in bt["match_ids"]]
        req = [m["match_id"] for m in self.inv["matches"] if m["analysis_required"]]
        self.assertEqual(sorted(ids), sorted(req))
        self.assertEqual(len(ids), len(set(ids)))
        self.assertGreater(len(self.b["batches"]), 2)        # no 3-4 lotes fijos: depende del volumen

    def test_bigger_budget_gives_fewer_batches(self):
        big = batches.make_batches(self.inv, {"matches": {}}, max_chars=10**7)
        self.assertLess(len(big["batches"]), len(self.b["batches"]))

    def test_discrepancy_batch_has_no_sampling(self):
        d = self.b["discrepancy_batch"]
        self.assertIn("m-900", d["match_ids"])
        self.assertIn("NINGUNO", d["sampling"])

    def full(self):
        r = results_for(self.b, "analista-deportivo") + results_for(self.b, "analista-cuantitativo")
        r.append({"agent": "verificador-mercados", "batch_id": "disc", "rows": [{"match_id": i, "review_status": "REVISADO"} for i in self.b["discrepancy_batch"]["match_ids"]]})
        return r

    def test_complete_reconciliation_ok(self):
        rep = batches.check_results(self.b, self.full())
        self.assertTrue(rep["ok"], rep)
        self.assertEqual(rep["per_agent"]["analista-deportivo"]["asignadas"], rep["per_agent"]["analista-deportivo"]["revisadas"])

    def test_missing_row_detected(self):
        victim = self.b["batches"][0]["match_ids"][0]
        r = results_for(self.b, "analista-deportivo", drop=victim) + results_for(self.b, "analista-cuantitativo")
        rep = batches.check_results(self.b, r)
        self.assertFalse(rep["ok"])
        self.assertTrue(any(victim in v for v in rep["missing"].values()))

    def test_duplicate_row_detected(self):
        dup = self.b["batches"][0]["match_ids"][0]
        rep = batches.check_results(self.b, results_for(self.b, "analista-deportivo", dup=dup))
        self.assertTrue(rep["duplicates"])

    def test_unknown_match_and_unassigned_batch_detected(self):
        r = results_for(self.b, "analista-deportivo")
        r[0]["rows"].append({"match_id": "m-fantasma", "review_status": "REVISADO"})
        r.append({"agent": "analista-deportivo", "batch_id": "b99", "rows": []})
        rep = batches.check_results(self.b, r)
        self.assertGreaterEqual(len(rep["unknown"]), 2)

    def test_pending_row_stays_explicitly_pending(self):
        victim = self.b["batches"][0]["match_ids"][1]
        r = self.full()
        for res in r:
            for row in res["rows"]:
                if row["match_id"] == victim and res["agent"] == "analista-cuantitativo":
                    row["review_status"] = "PENDIENTE"
        rep = batches.check_results(self.b, r)
        self.assertFalse(rep["ok"])
        self.assertEqual(rep["pending_rows"][0]["match_id"], victim)

    def test_competition_summary_is_not_evidence(self):
        r = results_for(self.b, "analista-deportivo", summary_only=True) + results_for(self.b, "analista-cuantitativo")
        rep = batches.check_results(self.b, r)
        self.assertFalse(rep["ok"])
        self.assertTrue(rep["missing"])

    def test_corrections_are_recorded(self):
        r = self.full()
        r[0]["rows"][0]["corrections"] = ["muestra mezclaba competiciones"]
        rep = batches.check_results(self.b, r)
        self.assertEqual(rep["corrections"][0]["corrections"], ["muestra mezclaba competiciones"])

    def test_cli_make_and_check_exit_codes(self):
        tmp = tempfile.mkdtemp()
        common.write_json_atomic(os.path.join(tmp, "inventory.json"), self.inv)
        self.assertEqual(batches.main(["make", "--run", tmp, "--max-chars", "2000"]), 0)
        res = os.path.join(tmp, "res.json")
        bb = common.read_json(os.path.join(tmp, "batches.json"))
        with open(res, "w") as fh:
            json.dump(results_for(bb, "analista-deportivo"), fh)
        self.assertEqual(batches.main(["check", "--run", tmp, "--results", res]), 3)   # faltan los otros agentes


if __name__ == "__main__":
    unittest.main()
