import json
import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".claude", "skills", "seleccion-final-picks", "scripts"))
import mercados_extra as me  # noqa: E402


def _odds(markets, n_casas=3):
    return {"data": {"match_id": "mt_x", "bookmakers": [{"bookmaker": f"B{i}", "markets": markets} for i in range(n_casas)]}}


MATCH = {"id": "mt_x", "utc_date": "2026-11-02T15:00:00.000Z", "home_team": {"name": "Local"}, "away_team": {"name": "Visita"}}


class Guardia(unittest.TestCase):
    def test_mercado_desconocido_se_detecta(self):
        with tempfile.TemporaryDirectory() as d:
            json.dump(_odds({"match_odds": {}, "mercado_nuevo_raro": {}}), open(os.path.join(d, "mt_x.json"), "w"))
            conteo, desc = me.auditar(d)
            self.assertEqual(desc, ["mercado_nuevo_raro"])

    def test_todos_los_conocidos_clasificados(self):
        for k in list(me.EXTRAIDOS) + list(me.EXCLUIDOS):
            self.assertIn(me.clasificar(k), ("extraido", "excluido"))
        for k in me.EXCLUIDOS:
            self.assertTrue(me.EXCLUIDOS[k])   # todo excluido lleva motivo

    def test_datos_reales_si_existen_sin_desconocidos(self):
        d = os.path.join(os.path.dirname(__file__), "..", "runs", "2026-11-02", "thestatsapi", "odds")
        if os.path.isdir(d):
            self.assertEqual(me.auditar(d)[1], [])


class Extraccion(unittest.TestCase):
    def test_handicap_solo_lineas_medias(self):
        ah = {"home": {"-1.5": {"last_seen": "2.50"}, "-1": {"last_seen": "2.10"}, "-0.25": {"last_seen": "1.90"}},
              "away": {"+1.5": {"last_seen": "1.50"}, "+1": {"last_seen": "1.75"}, "+0.25": {"last_seen": "1.95"}}}
        patas = me.patas_extra(MATCH, _odds({"asian_handicap": ah}))
        sel = {p["seleccion"] for p in patas}
        self.assertEqual(sel, {"Hándicap Local -1.5", "Hándicap Visita +1.5"})
        p = {x["seleccion"]: x for x in patas}
        self.assertAlmostEqual(p["Hándicap Local -1.5"]["p"] + p["Hándicap Visita +1.5"]["p"], 1.0, places=3)

    def test_corners_con_dos_casas_y_goles_equipo(self):
        c = {"9.5": {"over": {"last_seen": "1.90"}, "under": {"last_seen": "1.90"}}, "10": {"over": {"last_seen": "2.0"}, "under": {"last_seen": "1.8"}}}
        patas = me.patas_extra(MATCH, _odds({"match_corners": c}, n_casas=2))
        self.assertEqual({p["seleccion"] for p in patas}, {"Más de 9.5 córners", "Menos de 9.5 córners"})
        tt = {"home": {"1.5": {"over": {"last_seen": "2.0"}, "under": {"last_seen": "1.8"}}}}
        self.assertEqual(len(me.patas_extra(MATCH, _odds({"team_total_goals": tt}, n_casas=2))), 2)
        self.assertEqual(me.patas_extra(MATCH, _odds({"total_cards": {"3.5": {"over": {"last_seen": "1.9"}, "under": {"last_seen": "1.9"}}}}, n_casas=1)), [])

    def test_primera_parte(self):
        fh = {"home": {"last_seen": "3.0"}, "draw": {"last_seen": "2.2"}, "away": {"last_seen": "3.8"}}
        patas = me.patas_extra(MATCH, _odds({"first_half_result": fh}))
        self.assertEqual({p["seleccion"] for p in patas}, {"1.ª parte: gana Local", "1.ª parte: empate", "1.ª parte: gana Visita"})


if __name__ == "__main__":
    unittest.main()
