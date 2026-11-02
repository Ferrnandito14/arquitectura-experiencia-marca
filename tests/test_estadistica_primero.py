import json
import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".claude", "skills", "seleccion-final-picks", "scripts"))
import estadistica_primero as ep  # noqa: E402

MATCH = {"id": "mt_x", "utc_date": "2026-11-02T18:00:00.000Z", "home_team": {"id": "tm_h", "name": "Local"}, "away_team": {"id": "tm_a", "name": "Visita"}}


def _lista(d, tid, partidos):
    filas = []
    for i, (local, gf, gc, corners, amar, rojas) in enumerate(partidos):
        mid = f"{tid}_{i}"
        h, a = (tid, "rival") if local else ("rival", tid)
        gh, ga = (gf, gc) if local else (gc, gf)
        filas.append({"id": mid, "fecha": "2026-10-01", "h": h, "a": a, "hn": "x", "an": "y", "gh": gh, "ga": ga, "comp": "c"})
        ch, ca = (corners[0], corners[1]) if local else (corners[1], corners[0])
        json.dump({"ok": True, "corners": [ch, ca], "amarillas": [amar, 0], "rojas": [rojas, 0]}, open(os.path.join(d, f"stats_{mid}.json"), "w"))
    json.dump(filas, open(os.path.join(d, f"lista_{tid}.json"), "w"))


class EstadisticaPrimero(unittest.TestCase):
    def test_probabilidad_sale_del_historial_y_no_del_mercado(self):
        with tempfile.TemporaryDirectory() as d:
            # Local: 8 partidos, 6 con +2.5 goles; Visita: 8 partidos, 4 con +2.5
            _lista(d, "tm_h", [(True, 2, 1, (5, 3), 2, 0)] * 6 + [(False, 0, 1, (4, 4), 1, 0)] * 2)
            _lista(d, "tm_a", [(True, 2, 1, (6, 2), 3, 0)] * 4 + [(False, 0, 0, (3, 2), 1, 1)] * 4)
            patas = {p["seleccion"]: p for p in ep.patas_deportivas(MATCH, d)}
            self.assertAlmostEqual(patas["Más de 2.5 goles"]["p_dep"], (6 / 8 + 4 / 8) / 2, places=3)
            self.assertAlmostEqual(patas["Menos de 2.5 goles"]["p_dep"], 1 - (6 / 8 + 4 / 8) / 2, places=3)
            for p in patas.values():
                self.assertNotIn("cuota", p)
                self.assertNotIn("p", p)   # nada del mercado

    def test_muestra_insuficiente_no_genera_patas(self):
        with tempfile.TemporaryDirectory() as d:
            _lista(d, "tm_h", [(True, 1, 0, (5, 3), 1, 0)] * 7)
            _lista(d, "tm_a", [(True, 1, 0, (5, 3), 1, 0)] * 8)
            self.assertEqual(ep.patas_deportivas(MATCH, d), [])

    def test_corners_y_tarjetas_usan_puntos_de_la_casa(self):
        with tempfile.TemporaryDirectory() as d:
            _lista(d, "tm_h", [(True, 1, 0, (6, 4), 2, 1)] * 8)   # puntos = 2 + 2*1 = 4 para el local; rival 0 -> total 4
            _lista(d, "tm_a", [(True, 1, 0, (6, 4), 2, 1)] * 8)
            patas = {p["seleccion"]: p for p in ep.patas_deportivas(MATCH, d)}
            self.assertAlmostEqual(patas["Más de 3.5 tarjetas"]["p_dep"], 1.0, places=3)
            self.assertAlmostEqual(patas["Más de 4.5 tarjetas"]["p_dep"], 0.0, places=3)
            self.assertAlmostEqual(patas["Más de 9.5 córners"]["p_dep"], 1.0, places=3)


if __name__ == "__main__":
    unittest.main()
