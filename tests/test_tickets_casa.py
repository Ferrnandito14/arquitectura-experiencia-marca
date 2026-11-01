import importlib.util
import os
import sys
import unittest

D = os.path.join(os.path.dirname(__file__), "..", ".claude", "skills", "seleccion-final-picks", "scripts")
sys.path.insert(0, D)
spec = importlib.util.spec_from_file_location("tickets_casa", os.path.join(D, "tickets_casa.py"))
tc = importlib.util.module_from_spec(spec)
spec.loader.exec_module(tc)


def pata(i, cuota=1.4, p=0.7):
    return {"match_id": f"m{i}", "partido": f"P{i}", "seleccion": f"S{i}", "cuota": cuota, "p": p}


class TicketsCasa(unittest.TestCase):
    def test_filtros(self):
        patas = [pata(1), pata(2), pata(3), pata(4), pata(5)]
        casa = {"1": {"disponible": True, "cuota": 1.38}, "2": {"disponible": False}, "3": {"disponible": True, "cuota": 1.5},
                "4": {"disponible": True, "cuota": 1.3}, "5": {"disponible": True, "cuota": 1.45}}
        aud = {"m3|S3": {"recomendacion": "descartar", "severidad": "alta"}, "m4|S4": {"recomendacion": "degradar", "severidad": "alta"}, "m5|S5": {"recomendacion": "mantener", "severidad": "baja"}}
        modelo = {"m1|S1": {"discrepa": True, "dif": -0.2}, "m5|S5": {"discrepa": True, "dif": +0.2, "p_modelo": 0.9}}
        ok, fuera = tc.filtrar(patas, casa, aud, modelo)
        self.assertEqual([q["seleccion"] for q in ok], ["S5"])         # modelo por encima del mercado no excluye
        self.assertEqual(len(fuera), 4)
        self.assertEqual(ok[0]["cuota"], 1.45)
        self.assertEqual(ok[0]["cuota_ref"], 1.4)

    def test_usa_cuota_de_la_casa_en_valor(self):
        ok, _ = tc.filtrar([pata(1, 1.4, 0.7)], {"1": {"disponible": True, "cuota": 1.5}}, {}, {})
        self.assertAlmostEqual(ok[0]["valor"], 0.7 * 1.5)


if __name__ == "__main__":
    unittest.main()
