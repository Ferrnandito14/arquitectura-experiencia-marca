import json, os, sys, tempfile, unittest
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".claude", "skills", "seleccion-final-picks", "scripts"))
import contraste_poisson as cp
import lista_ancha as la


def partido(i, utc, h, a, gh, ga):
    return {"id": i, "utc": utc, "h_id": h, "h": h, "a_id": a, "a": a, "gh": gh, "ga": ga}


class T(unittest.TestCase):
    def _mem(self):
        d = {}
        n = 0
        for rival in ("r1", "r2", "r3", "r4", "r5", "r6", "r7", "r8"):
            n += 1; d[f"a{n}"] = partido(f"a{n}", f"2026-10-{n:02d}T10:00", "L", rival, 2, 1)   # L local marca 2 y recibe 1
            n += 1; d[f"a{n}"] = partido(f"a{n}", f"2026-10-{n:02d}T11:00", rival, "V", 1, 2)   # V visita marca 2 y recibe 1
        return d

    def test_contraste_basico(self):
        r = cp.contraste(self._mem(), "L", "V", 15)
        self.assertAlmostEqual(r["lambda_local"], 1.5, places=2)
        self.assertAlmostEqual(r["lambda_total"], 3.0, places=2)
        self.assertAlmostEqual(r["menos"]["4.5"] + r["mas"]["4.5"], 1.0, places=3)
        self.assertGreater(r["menos"]["4.5"], 0.8)

    def test_muestra_insuficiente(self):
        d = {"x": partido("x", "2026-10-01T10:00", "L", "V", 1, 0)}
        self.assertIn("error", cp.contraste(d, "L", "V", 15))

    def test_lista_ancha_filtra(self):
        with tempfile.TemporaryDirectory() as t:
            os.makedirs(os.path.join(t, "pool"))
            json.dump({"patas": [{"match_id": "m1", "seleccion": "A", "cuota": 1.3, "p": 0.7, "n_casas": 3},
                                 {"match_id": "m1", "seleccion": "B", "cuota": 1.1, "p": 0.9, "n_casas": 3}], "banderas": []}, open(os.path.join(t, "pool", "patas.json"), "w"))
            json.dump([{"match_id": "m1", "seleccion": "A", "p_suav": 0.7, "hora_caracas": "05-11 10:00", "partido": "X"},
                       {"match_id": "m1", "seleccion": "B", "p_suav": 0.9, "hora_caracas": "05-11 10:00", "partido": "X"},
                       {"match_id": "m2", "seleccion": "C", "p_suav": 0.9, "hora_caracas": "05-11 11:00", "partido": "Y"}], open(os.path.join(t, "pool", "est_patas.json"), "w"))
            out, n = la.construir(t)
            self.assertEqual([z["seleccion"] for z in out], ["A"])  # B cuota<1.20, C sin precio
            self.assertEqual(n, 3)


if __name__ == "__main__":
    unittest.main()
