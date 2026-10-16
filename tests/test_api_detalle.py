"""api_detalle: precio por casa, movimiento de cuotas y mercados adicionales de TheStatsAPI. Datos FICTICIOS: EJEMPLO — NO REAL."""
import math
import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".claude", "skills", "seleccion-final-picks", "scripts"))
import api_detalle as ad  # noqa: E402

TREE = {"total_goals": {"2.5": {"over": {"opening": "1.80", "last_seen": "1.60"}, "under": {"opening": "2.00", "last_seen": "2.30"}}},
        "asian_handicap": {"home": {"-0.25": {"opening": "1.90", "last_seen": "2.00"}}, "away": {"+0.25": {"opening": "1.95", "last_seen": "1.85"}}},
        "correct_score": {"1-0": {"opening": "7.0", "last_seen": "8.0"}},
        "double_chance": {"home_draw": {"opening": "1.30", "last_seen": "1.28"}}}
TM = {"home": "A", "away": "B", "books": {"Bet365": TREE, "Pinnacle": {"total_goals": {"2.5": {"over": {"opening": "1.70", "last_seen": "1.64"}, "under": {"opening": "2.10", "last_seen": "2.26"}}}}}}


class Aplanado(unittest.TestCase):
    def test_hojas_y_descripcion(self):
        hojas = {tuple(p): (o, l) for p, o, l in ad.walk(TREE["total_goals"])}
        self.assertEqual(hojas[("2.5", "over")], (1.8, 1.6))
        self.assertEqual(ad.describe("total_goals", ["2.5", "over"])[1:3], ("2.5", "Más de 2.5"))
        self.assertEqual(ad.describe("asian_handicap", ["away", "+0.25"])[2], "Visitante +0.25")
        self.assertEqual(ad.describe("total_goals_btts", ["2.5", "over_yes"])[2], "Más de 2.5 y ambos anotan sí")
        self.assertEqual(ad.describe("double_chance", ["home_draw"])[2], "Local o empate (1X)")

    def test_resumen_por_casa_y_movimiento(self):
        sel = ad.selections(TM)[("total_goals", ("2.5", "over"))]
        r = ad.resumen(sel)
        self.assertEqual((r["n"], r["apertura"], r["ultimo"], r["min"], r["max"]), (2, 1.75, 1.62, 1.6, 1.64))
        self.assertEqual(r["delta_pct"], round((1.62 / 1.75 - 1) * 100, 1))
        self.assertEqual(r["mejor"], "Pinnacle")

    def test_clave_de_apifootball_solo_donde_publica(self):
        self.assertEqual(ad.apif_key("total_goals", ["2.5", "over"]), ("goles.over_2_5", 0))
        self.assertEqual(ad.apif_key("total_goals", ["2.5", "under"]), ("goles.over_2_5", 1))
        self.assertEqual(ad.apif_key("asian_handicap", ["home", "-0.5"]), ("resultado.handicap-0.5", 0))
        self.assertEqual(ad.apif_key("asian_handicap", ["away", "+0.5"]), ("resultado.handicap-0.5", 1))
        self.assertIsNone(ad.apif_key("asian_handicap", ["home", "-0.25"]))      # cuartos de línea: apifootball no los publica
        self.assertIsNone(ad.apif_key("correct_score", ["1-0"]))


class ModeloAdicional(unittest.TestCase):
    LH, LA, SH = 1.5, 1.1, 0.45

    def test_distribuciones_suman_uno(self):
        h = sum(ad.p_additional("second_half_result", [k], self.LH, self.LA, self.SH) for k in ("home", "draw", "away"))
        self.assertAlmostEqual(h, 1, places=3)
        ft = sum(ad.p_additional("first_team_to_score", [k], self.LH, self.LA, self.SH) for k in ("home", "away", "none"))
        self.assertAlmostEqual(ft, 1, places=6)
        y = ad.p_additional("btts_first_half", ["yes"], self.LH, self.LA, self.SH) + ad.p_additional("btts_first_half", ["no"], self.LH, self.LA, self.SH)
        self.assertAlmostEqual(y, 1, places=6)
        o = sum(ad.p_additional("total_goals_btts", ["2.5", k], self.LH, self.LA, self.SH) for k in ("over_yes", "over_no", "under_yes", "under_no"))
        self.assertAlmostEqual(o, 1, places=3)

    def test_cuarto_de_linea_y_ev_exacto(self):
        outs = ad.p_additional("asian_handicap", ["home", "-0.25"], self.LH, self.LA, self.SH)
        self.assertAlmostEqual(sum(outs.values()), 1, places=3)
        self.assertIn("half_loss", outs)
        # sin pushes ni medias: EV = p·(o−1) − (1−p)
        self.assertAlmostEqual(ad.ah_ev(2.0, {"win": 0.5, "lose": 0.5}), 0.0)
        self.assertAlmostEqual(ad.ah_ev(2.0, {"win": 0.4, "half_win": 0.2, "half_loss": 0.1, "lose": 0.3}), 0.4 + 0.1 - 0.05 - 0.3)

    def test_sin_modelo_para_penales(self):
        self.assertIsNone(ad.p_additional("a_penalty_in_match", ["yes"], self.LH, self.LA, self.SH))
        self.assertIsNone(ad.p_additional("second_half_result", ["home"], self.LH, self.LA, None))      # sin fracción de 1.ª parte medida no hay mercados de mitad


class Liquidacion(unittest.TestCase):
    R = {"h": 2, "a": 1, "h1": 0, "a1": 1, "primer_gol": "away"}

    def test_mercados_adicionales(self):
        s = lambda key, r=None: ad.settle_additional(key, r or self.R)[0]
        self.assertEqual(s("correct_score|2-1"), "GANADA")
        self.assertEqual(s("correct_score|1-0"), "PERDIDA")
        self.assertEqual(s("second_half_result|home"), "GANADA")                 # 2.ª parte 2–0
        self.assertEqual(s("btts_first_half|no"), "GANADA")
        self.assertEqual(s("btts_second_half|yes"), "PERDIDA")
        self.assertEqual(s("half_time_double_chance|draw_away"), "GANADA")       # descanso 0–1
        self.assertEqual(s("total_goals_btts|2.5|over_yes"), "GANADA")
        self.assertEqual(s("first_team_to_score|away"), "GANADA")
        self.assertEqual(s("first_team_to_score|none", {"h": 0, "a": 0}), "GANADA")
        self.assertEqual(s("asian_handicap|home|-0.25"), "GANADA")
        self.assertEqual(s("asian_handicap|home|-1.25"), "PERDIDA (½)")           # 2–1: pierde −1 (devuelve) y −1.5 (pierde) → media perdida
        self.assertEqual(s("to_score_a_penalty|home"), "SIN DATO")
        self.assertEqual(s("second_half_result|home", {"h": 2, "a": 1}), "SIN DATO")               # sin descanso no se inventa


if __name__ == "__main__":
    unittest.main()
