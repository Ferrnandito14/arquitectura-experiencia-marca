import importlib.util
import os
import sys
import unittest

D = os.path.join(os.path.dirname(__file__), "..", ".claude", "skills", "seleccion-final-picks", "scripts")
sys.path.insert(0, D)
spec = importlib.util.spec_from_file_location("justificacion_patas", os.path.join(D, "justificacion_patas.py"))
jp = importlib.util.module_from_spec(spec)
spec.loader.exec_module(jp)


def eq(nombre, tid, G, E, P, local=None, visita=None, gf=1.5, gc=1.0, totales=(3, 1, 4, 2, 3, 2, 1, 4)):
    n = G + E + P
    lado = {"n": n // 2, "G": G // 2, "E": E // 2, "P": P // 2}
    ultimos = [{"total_goles": g, "fecha": "2026-10-2%d" % (i % 9)} for i, g in enumerate(totales)]
    return {"equipo": nombre, "team_id": tid, "ultimos": ultimos, "bajas": {"lesiones_activas": 1, "sanciones_activas": 0},
            "proximos": [{"utc": "2026-11-01T12:00", "rival": "X"}, {"utc": "2026-11-04T12:00", "rival": "Y"}],
            "resumen": {"n": n, "G": G, "E": E, "P": P, "gf_medio": gf, "gc_medio": gc, "sin_perder": (G + E) / n, "por_lado": {"local": local or lado, "visita": visita or lado}}}


class Justificacion(unittest.TestCase):
    def test_clasificar(self):
        self.assertEqual(jp.clasificar("Lazio o empate", "Lazio", "Cagliari"), ("dc_local", None))
        self.assertEqual(jp.clasificar("Cagliari o empate", "Lazio", "Cagliari"), ("dc_visita", None))
        self.assertEqual(jp.clasificar("Lazio o Cagliari (sin empate)", "Lazio", "Cagliari"), ("sin_empate", None))
        self.assertEqual(jp.clasificar("Más de 2.5 goles", "A", "B"), ("over", 2.5))
        self.assertEqual(jp.clasificar("Menos de 7.5 goles", "A", "B"), ("under", 7.5))

    def test_dc_favorito_respaldado(self):
        fila = {"local": eq("Lazio", "l", 7, 1, 0), "visitante": eq("Cagliari", "v", 2, 2, 4)}
        tabla = {"l": {"team": {"name": "Lazio"}, "position": 1, "points": 25, "matches_played": 9, "goal_difference": 15},
                 "v": {"team": {"name": "Cagliari"}, "position": 12, "points": 10, "matches_played": 9, "goal_difference": -4}}
        h2h = {"n": 4, "sin_perder_local": 1.0, "sin_perder_visita": 0.0, "empates": 1, "goles_medios": 2.0}
        ls = jp.evaluar("dc_local", None, fila, tabla, h2h)
        self.assertGreater(sum(1 for x in ls if x["m"] == "+"), sum(1 for x in ls if x["m"] == "−"))
        self.assertTrue(jp.lectura(ls).startswith("El dossier respalda"))

    def test_dc_equipo_irregular_se_debilita(self):
        fila = {"local": eq("A", "l", 1, 2, 5), "visitante": eq("B", "v", 6, 1, 1)}
        ls = jp.evaluar("dc_local", None, fila, {}, None)
        self.assertTrue(jp.lectura(ls).startswith("El dossier la debilita"))

    def test_sin_empate_penaliza_equipos_empatadores(self):
        fila = {"local": eq("A", "l", 2, 5, 1), "visitante": eq("B", "v", 3, 4, 1)}
        ls = jp.evaluar("sin_empate", None, fila, {}, {"n": 4, "empates": 2, "goles_medios": 1.5})
        self.assertGreaterEqual(sum(1 for x in ls if x["m"] == "−"), 3)

    def test_over_under_usa_tasa_y_media(self):
        fila = {"local": eq("A", "l", 4, 2, 2, gf=2.0, gc=1.5), "visitante": eq("B", "v", 3, 3, 2, gf=1.8, gc=1.4)}
        over = jp.evaluar("over", 2.5, fila, {}, {"n": 3, "goles_medios": 3.3})
        under = jp.evaluar("under", 2.5, fila, {}, {"n": 3, "goles_medios": 3.3})
        self.assertGreater(sum(1 for x in over if x["m"] == "+"), sum(1 for x in under if x["m"] == "+"))

    def test_h2h_orientado_al_local_actual(self):
        def p(h, a, gh, ga, fecha="2026-02-21T18:00:00Z"):
            return {"status": "finished", "utc_date": fecha, "home_team": {"id": h, "name": h}, "away_team": {"id": a, "name": a}, "score": {"home": gh, "away": ga}}
        r = jp.h2h_de([p("c", "l", 0, 3), p("l", "c", 2, 0), p("l", "c", 1, 1), p("x", "y", 5, 5)], "l", "c")
        self.assertEqual((r["n"], r["G_local"], r["E"], r["G_visita"]), (3, 2, 1, 0))
        self.assertAlmostEqual(r["goles_medios"], (3 + 2 + 2) / 3, places=2)
        self.assertEqual(jp.h2h_de([], "l", "c"), {"n": 0})

    def test_registro_por_tipo_y_cuota(self):
        led = [{"entry_id": "resultado.dc.1x", "res": "GANADA", "cuota": 1.10, "dia": "d1"}] * 8 + [{"entry_id": "resultado.dc.1x", "res": "PERDIDA", "cuota": 1.11, "dia": "d2"}] * 2 + [{"entry_id": "resultado.dc.1x", "res": "GANADA", "cuota": 2.0, "dia": "d3"}]
        r = jp.registro(led, "A o empate", "dc_local", None, 1.1, "A")
        self.assertEqual((r["n"], r["acierto"]), (10, 80.0))
        self.assertEqual(jp.registro(led, "x", "otro", None, 1.1, "A"), None)

    def test_contexto_marca_poco_descanso(self):
        fila = {"local": eq("A", "l", 4, 2, 2), "visitante": eq("B", "v", 4, 2, 2)}
        fila["local"]["ultimos"][0]["fecha"] = "2026-10-30"
        ls = jp.contexto_lineas(fila, "2026-11-01T12:00:00Z")
        self.assertEqual(ls[0]["m"], "−")


if __name__ == "__main__":
    unittest.main()
