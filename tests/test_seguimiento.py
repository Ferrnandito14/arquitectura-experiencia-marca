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




class CornersDosBloques(unittest.TestCase):
    """La API trae `statistics` (retrasado a veces) y `statistics_1half`; los córners no bajan: se toma el mayor. Datos FICTICIOS: EJEMPLO — NO REAL."""
    def test_toma_el_mayor_entre_bloques(self):
        e = {"statistics": [{"type": "Corners", "home": "3", "away": "0"}], "statistics_1half": [{"type": "Corners", "home": "5", "away": "0"}]}
        self.assertEqual(s._corner_pair(e), (5, 0))
        self.assertEqual(s._corners(e), 5)

    def test_un_solo_bloque_o_ninguno(self):
        self.assertEqual(s._corner_pair({"statistics": [{"type": "Corners", "home": "0", "away": "1"}]}), (0, 1))
        self.assertIsNone(s._corner_pair({"statistics": [{"type": "Fouls", "home": "1", "away": "1"}]}))

class RegistroTickets(unittest.TestCase):
    """registrar_tickets: etiqueta exacta del catálogo y consolidación idempotente. Datos FICTICIOS: EJEMPLO — NO REAL."""
    def test_etiquetas_exactas_y_sin_equivalente(self):
        import registrar_tickets as rt
        self.assertEqual(rt.catalog_label({"mercado": "total", "op": "over", "linea": 2.5}), "Más de 2.5 goles")
        self.assertEqual(rt.catalog_label({"mercado": "total_1t", "op": "over", "linea": 0.5}), "1.ª parte: más de 0.5 goles")
        self.assertEqual(rt.catalog_label({"mercado": "corners", "op": "over", "linea": 9.5}), "Más de 9.5 córners")
        self.assertIsNone(rt.catalog_label({"mercado": "combo"}))
        self.assertIsNone(rt.catalog_label({"mercado": "handicap", "linea": 2.75}))

    def test_consolida_y_es_idempotente(self):
        import json, tempfile, registrar_tickets as rt
        with tempfile.TemporaryDirectory() as d:
            os.makedirs(os.path.join(d, "runs", "2026-10-15", "seguimiento"))
            with open(os.path.join(d, "runs", "2026-10-15", "seguimiento", "registro_resultados.jsonl"), "w", encoding="utf-8") as f:
                f.write(json.dumps({"ticket": "G", "partido": "A – B", "mercado": "total", "cuota": 1.6, "resultado": "ACERTADA", "detalle": "1-0"}) + "\n")
            out = os.path.join(d, "reg.jsonl")
            for _ in range(2):
                rt.main(["--runs", os.path.join(d, "runs", "2026-10-15"), "--out", out])
            rows = [json.loads(x) for x in open(out, encoding="utf-8")]
            self.assertEqual(len(rows), 1)
            self.assertEqual((rows[0]["fecha"], rows[0]["p_implicita_con_margen"]), ("2026-10-15", 0.625))


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


class NuevosMercados(unittest.TestCase):
    def test_double_chance_and_goals_plus_cards(self):
        dc = {"mercado": "dc", "lado": "home_or_draw"}
        self.assertEqual(s.eval_leg(dc, ev(1, 1))[0], "ACERTADA")
        self.assertEqual(s.eval_leg(dc, ev(0, 1))[0], "FALLADA")
        self.assertEqual(s.eval_leg(dc, ev(0, 1, "60"))[0], "EN_JUEGO")
        gc = {"mercado": "goles_tarjetas", "min_goles": 2, "min_puntos": 4}
        cards = [{"home_fault": "A", "card": "yellow card", "time": "10"}] * 2 + [{"away_fault": "B", "card": "yellow card", "time": "20"}, {"away_fault": "C", "card": "red card", "time": "30"}]
        cards = [dict(c, home_fault=n) if "home_fault" in c else dict(c, away_fault=n) for c, n in zip(cards, ["P1", "P2", "Q1", "Q2"])]
        self.assertEqual(s.eval_leg(gc, ev(1, 1, cards=cards))[0], "ACERTADA")        # 2 goles y 1+1+1+2 = 5 puntos
        self.assertEqual(s.eval_leg(gc, ev(1, 0, cards=cards))[0], "FALLADA")         # un solo gol al final
        st, det = s.eval_leg(gc, ev(1, 1, "70", cards=cards))
        self.assertEqual(st, "EN_JUEGO")
        self.assertIn("PROVISIONAL", det)
