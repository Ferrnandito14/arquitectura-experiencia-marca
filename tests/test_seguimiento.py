import os, sys, unittest
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".claude", "skills", "seleccion-final-picks", "scripts"))
import seguimiento as s  # noqa: E402


def ev(h, a, st="Finished", ht=(None, None), cards=None):
    return {"match_hometeam_score": str(h), "match_awayteam_score": str(a), "match_status": st,
            "match_hometeam_halftime_score": "" if ht[0] is None else str(ht[0]), "match_awayteam_halftime_score": "" if ht[1] is None else str(ht[1]), "cards": cards or []}


class T(unittest.TestCase):
    def test_handicap_away_plus25(self):
        self.assertEqual(s.settle_handicap(3, 0, "away", 2.5), "lose")
        self.assertEqual(s.settle_handicap(2, 0, "away", 2.5), "win")
        self.assertEqual(s.settle_handicap(0, 2, "away", 2.5), "win")

    def test_totals(self):
        self.assertEqual(s.settle_total(4, "under", 4.5), "win")
        self.assertEqual(s.settle_total(5, "under", 4.5), "lose")
        self.assertEqual(s.settle_total(2, "over", 2.0), "void")

    def test_under_live_lost_early(self):
        leg = {"mercado": "total", "op": "under", "linea": 2.5}
        self.assertEqual(s.eval_leg(leg, ev(2, 1, "67"))[0], "EN_JUEGO")  # provisional (VAR)
        self.assertIn("PROVISIONAL", s.eval_leg(leg, ev(2, 1, "67"))[1])
        self.assertEqual(s.eval_leg(leg, ev(1, 1, "67"))[0], "EN_JUEGO")
        self.assertEqual(s.eval_leg(leg, ev(1, 1))[0], "ACERTADA")

    def test_over_live_won_early(self):
        leg = {"mercado": "total", "op": "over", "linea": 1.5}
        self.assertEqual(s.eval_leg(leg, ev(1, 1, "30"))[0], "EN_JUEGO")  # provisional (VAR)
        self.assertEqual(s.eval_leg(leg, ev(1, 1))[0], "ACERTADA")
        self.assertEqual(s.eval_leg(leg, ev(0, 1))[0], "FALLADA")

    def test_1x2_and_first_half(self):
        self.assertEqual(s.eval_leg({"mercado": "1x2", "lado": "home"}, ev(2, 0))[0], "ACERTADA")
        self.assertEqual(s.eval_leg({"mercado": "1x2", "lado": "away"}, ev(1, 1))[0], "FALLADA")
        leg = {"mercado": "1x2_1t", "lado": "away"}
        self.assertEqual(s.eval_leg(leg, ev(0, 3, "Finished", (1, 1)))[0], "FALLADA")
        self.assertEqual(s.eval_leg(leg, ev(0, 3, "Finished", (0, 1)))[0], "ACERTADA")
        self.assertEqual(s.eval_leg(leg, ev(0, 1, "30", (0, 1)))[0], "EN_JUEGO")

    def test_btts(self):
        self.assertEqual(s.eval_leg({"mercado": "btts"}, ev(1, 1, "50"))[0], "EN_JUEGO")
        self.assertEqual(s.eval_leg({"mercado": "btts"}, ev(1, 1))[0], "ACERTADA")
        self.assertEqual(s.eval_leg({"mercado": "btts"}, ev(2, 0))[0], "FALLADA")

    def test_cards_dc(self):
        c = [{"home_fault": "A", "card": "yellow card", "time": "10"}, {"away_fault": "B", "card": "red card", "time": "50"}]
        leg = {"mercado": "cards_dc", "min_puntos": 3, "lado": "home_or_draw"}
        self.assertEqual(s.eval_leg(leg, ev(1, 1, cards=c))[0], "ACERTADA")
        self.assertEqual(s.eval_leg(leg, ev(0, 1, cards=c))[0], "FALLADA")

    def test_ticket_lost_with_one_failed_leg(self):
        self.assertEqual(s.ticket_status([{"estado": "FALLADA"}, {"estado": "EN_JUEGO"}]), "PERDIDO")
        self.assertEqual(s.ticket_status([{"estado": "ACERTADA"}, {"estado": "PENDIENTE"}]), "ABIERTO")
        self.assertEqual(s.ticket_status([{"estado": "ACERTADA"}, {"estado": "ACERTADA"}]), "GANADO")

    def test_not_started_and_missing(self):
        self.assertEqual(s.eval_leg({"mercado": "btts"}, ev(0, 0, "")) [0], "PENDIENTE")
        self.assertEqual(s.eval_leg({"mercado": "btts"}, None)[0], "PENDIENTE")


if __name__ == "__main__":
    unittest.main()


class Liquidacion(unittest.TestCase):
    def test_quarter_line_handicap(self):
        # visitante +0.25: empate = media derrota? no: +0.25 = mitad en +0 (devolución en empate) y mitad en +0.5 (gana) → media victoria en el empate
        self.assertEqual(s.settle_handicap_quarter(1, 1, "away", 0.25), "half_win")
        self.assertEqual(s.settle_handicap_quarter(2, 1, "away", 0.25), "lose")
        self.assertEqual(s.settle_handicap_quarter(0, 1, "away", 0.25), "win")
        # visitante -0.25: empate = media derrota
        self.assertEqual(s.settle_handicap_quarter(1, 1, "away", -0.25), "half_loss")
        # líneas .5 y enteras no cambian
        self.assertEqual(s.settle_handicap_quarter(3, 0, "away", 2.5), "lose")
        self.assertEqual(s.settle_handicap_quarter(2, 0, "away", 2.0), "void")

    def test_score_at_90_ignores_extra_time(self):
        e = {"match_hometeam_score": "2", "match_awayteam_score": "1", "match_hometeam_ft_score": "1", "match_awayteam_ft_score": "1"}
        self.assertEqual(s.score90(e), (1, 1))
        self.assertEqual(s.score90({"match_hometeam_score": "2", "match_awayteam_score": "1"}), (2, 1))


class RegistroSoloFinalizado(unittest.TestCase):
    def test_log_only_written_when_match_finished(self):
        import json, tempfile
        with tempfile.TemporaryDirectory() as d:
            os.makedirs(os.path.join(d, "seguimiento"))
            spec = {"tickets": [{"id": "T", "nombre": "t", "monto": 1, "patas": [{"mid": "m", "apif": "1", "partido": "A – B", "mercado": "total", "op": "over", "linea": 1.5, "cuota": 1.3}]}]}
            with open(os.path.join(d, "seguimiento", "tickets_abiertos.json"), "w", encoding="utf-8") as f:
                json.dump(spec, f)
            live = lambda mid: ev(1, 1, "54")                 # 2 goles en juego: cumplida PROVISIONAL, no se registra
            s.write_all(d, s.run(d, live))
            reg = os.path.join(d, "seguimiento", "registro_resultados.jsonl")
            self.assertFalse(os.path.exists(reg) and open(reg).read().strip())
            fin = lambda mid: ev(1, 1)                        # finalizado
            s.write_all(d, s.run(d, fin))
            self.assertEqual(len(open(reg).read().strip().splitlines()), 1)
