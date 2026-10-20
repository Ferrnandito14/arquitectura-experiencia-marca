import unittest
import helpers  # noqa: F401  (añade scripts/ al path)
import leg_model as lm


class EstimadoresEnteros(unittest.TestCase):
    def setUp(self):
        self.g = lm.grid(1.6, 1.1)

    def test_total_entero_condicionado_a_no_devolucion(self):
        over = lm.p_whole_over(self.g, 3)
        push = sum(self.g[i][j] for i in range(lm.MAX_G + 1) for j in range(lm.MAX_G + 1) if i + j == 3)
        self.assertAlmostEqual(over, lm.p_over(self.g, 3) / (1 - push), places=6)
        self.assertTrue(0 < over < 1)

    def test_ah_entero_cero_es_dnb(self):
        h, d, a = lm.p_1x2(self.g)
        self.assertAlmostEqual(lm.p_ah_whole(self.g, "home", 0), h / (h + a), places=6)

    def test_handicap_europeo_suma_uno(self):
        for L in lm.EUROPEAN:
            self.assertAlmostEqual(sum(lm.p_eh(self.g, o, L) for o in ("home", "draw", "away")), 1.0, places=6)

    def test_model_probs_trae_las_claves_nuevas(self):
        rows = [{"gf": 1, "ga": 1, "venue": "local"}] * 8
        k = lm.model_probs(rows, rows, 1.3, 1.1).keys()
        for key in ("whole_over_3", "ahw_home_-1", "ahw_away_+2", "eh_draw_-1", "eh_home_+1"):
            self.assertIn(key, k)
