import os, sys, unittest
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".claude", "skills", "seleccion-final-picks", "scripts"))
import leg_model as L  # noqa: E402


class LegModel(unittest.TestCase):
    ROWS = [{"gf": 2, "ga": 1, "venue": "local"}] * 5 + [{"gf": 1, "ga": 1, "venue": "visitante"}] * 5

    def test_probabilidades_coherentes(self):
        mu, adv = L.league_means([self.ROWS])
        p = L.model_probs(self.ROWS, self.ROWS, mu, adv)
        self.assertAlmostEqual(p["p1"] + p["px"] + p["p2"], 1.0, places=3)
        self.assertGreater(p["over_1.5"], p["over_2.5"])
        self.assertGreater(p["over_2.5"], p["over_3.5"])

    def test_equipo_goleador_sube_over(self):
        mu = 1.4
        fuerte = [{"gf": 4, "ga": 2, "venue": "local"}] * 10
        debil = [{"gf": 0, "ga": 1, "venue": "local"}] * 10
        a = L.model_probs(fuerte, fuerte, mu, 1.2)["over_2.5"]
        b = L.model_probs(debil, debil, mu, 1.2)["over_2.5"]
        self.assertGreater(a, b)

    def test_sin_datos_no_inventa(self):
        self.assertEqual(L.strengths([], 1.4), (1.0, 1.0))


if __name__ == "__main__":
    unittest.main()
