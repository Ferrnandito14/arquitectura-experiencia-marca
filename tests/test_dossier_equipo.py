import importlib.util
import os
import sys
import unittest

D = os.path.join(os.path.dirname(__file__), "..", ".claude", "skills", "seleccion-final-picks", "scripts")
sys.path.insert(0, D)
spec = importlib.util.spec_from_file_location("dossier_equipo", os.path.join(D, "dossier_equipo.py"))
de = importlib.util.module_from_spec(spec)
spec.loader.exec_module(de)


def partido(h, a, gh, ga, status="finished", fecha="2026-10-20T18:00:00.000Z"):
    return {"id": "mt", "competition_id": "c", "utc_date": fecha, "status": status,
            "home_team": {"id": h, "name": "Local " + h}, "away_team": {"id": a, "name": "Visita " + a}, "score": {"home": gh, "away": ga}}


class Orientacion(unittest.TestCase):
    def test_victoria_de_visita_no_se_invierte(self):
        # la Lazio gana 3-0 en casa de la Juventus: marcador de la visita 0-3 en el partido, 3-0 para el equipo
        r = de.orientar(partido("juve", "lazio", 0, 3), "lazio")
        self.assertEqual((r["resultado"], r["gf"], r["gc"], r["lado"], r["marcador_equipo"]), ("G", 3, 0, "visita", "3-0"))

    def test_derrota_de_visita(self):
        r = de.orientar(partido("a", "b", 3, 1), "b")
        self.assertEqual((r["resultado"], r["marcador_equipo"], r["lado"]), ("P", "1-3", "visita"))

    def test_local_y_empate(self):
        self.assertEqual(de.orientar(partido("a", "b", 2, 0), "a")["resultado"], "G")
        self.assertEqual(de.orientar(partido("a", "b", 1, 1), "a")["resultado"], "E")

    def test_no_terminado_o_ajeno(self):
        self.assertIsNone(de.orientar(partido("a", "b", None, None, status="scheduled"), "a"))
        self.assertIsNone(de.orientar(partido("a", "b", 1, 0), "z"))

    def test_resumen(self):
        ps = [de.orientar(partido("a", "x", 3, 0), "a"), de.orientar(partido("y", "a", 2, 2), "a"), de.orientar(partido("z", "a", 3, 1), "a")]
        r = de.resumen(ps)
        self.assertEqual((r["n"], r["G"], r["E"], r["P"]), (3, 1, 1, 1))
        self.assertEqual(r["por_lado"]["visita"], {"n": 2, "G": 0, "E": 1, "P": 1})
        self.assertAlmostEqual(r["mas_2_5"], 1.0)
        self.assertEqual(de.resumen([]), {"n": 0})

    def test_bajas_solo_activas(self):
        b = de.bajas({"data": {"injuries": [{"status": "out", "reason": "knee", "expected_return": "2026-12-01T00:00:00Z", "active": True}, {"active": False}], "suspensions": []}})
        self.assertEqual((b["lesiones_activas"], b["sanciones_activas"]), (1, 0))


if __name__ == "__main__":
    unittest.main()
