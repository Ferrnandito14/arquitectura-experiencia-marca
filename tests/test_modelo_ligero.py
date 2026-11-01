import importlib.util
import os
import sys
import unittest

D = os.path.join(os.path.dirname(__file__), "..", ".claude", "skills", "seleccion-final-picks", "scripts")
sys.path.insert(0, D)
spec = importlib.util.spec_from_file_location("modelo_ligero", os.path.join(D, "modelo_ligero.py"))
ml = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ml)


class ModeloLigero(unittest.TestCase):
    def test_probabilidades_coherentes(self):
        lh, la = 1.6, 1.1
        pl, pv, sin_emp = ml.p_leg("dc_local", None, lh, la), ml.p_leg("dc_visita", None, lh, la), ml.p_leg("sin_empate", None, lh, la)
        self.assertGreater(pl, pv)
        self.assertAlmostEqual(pl + pv - 1.0, 1.0 - sin_emp, places=6)   # 1X + X2 = 1 + P(empate)
        self.assertAlmostEqual(ml.p_leg("over", 2.5, lh, la) + ml.p_leg("under", 2.5, lh, la), 1.0, places=9)

    def test_lambdas_promedian_ataque_y_defensa(self):
        L = {"resumen": {"gf_medio": 2.0, "gc_medio": 1.0}}
        V = {"resumen": {"gf_medio": 1.0, "gc_medio": 3.0}}
        self.assertEqual(ml.lambdas(L, V), ((2.0 + 3.0) / 2, (1.0 + 1.0) / 2))

    def test_over_crece_con_mas_goles_esperados(self):
        self.assertGreater(ml.p_leg("over", 2.5, 2.0, 1.5), ml.p_leg("over", 2.5, 1.0, 0.8))

    def test_tipo_desconocido(self):
        self.assertIsNone(ml.p_leg("otro", None, 1.0, 1.0))


if __name__ == "__main__":
    unittest.main()
