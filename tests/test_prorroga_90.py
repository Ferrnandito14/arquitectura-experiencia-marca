"""Liquidación a 90' cuando el partido ya está en prórroga (copa) aunque el feed no marque «Finished» (caso real: Mafra–Santa Clara, Taça de Portugal, 18-oct)."""
import unittest

import helpers  # noqa: F401  (añade scripts/ al path)
import seguimiento as sg


def ev(h, a, ex_h="", ex_a="", status="118"):
    return {"match_status": status, "match_hometeam_score": str(h), "match_awayteam_score": str(a), "match_hometeam_extra_score": ex_h, "match_awayteam_extra_score": ex_a,
            "match_hometeam_penalty_score": "", "match_awayteam_penalty_score": "", "match_hometeam_ft_score": "", "match_awayteam_ft_score": ""}


class ProrrogaA90(unittest.TestCase):
    def test_1x2_visitante_empate_a_90_es_fallada(self):
        leg = {"mercado": "1x2", "lado": "away", "cuota": 1.54}
        self.assertEqual(sg.eval_leg(leg, ev(3, 2, "1", "0"))[0], "FALLADA")     # 2-2 a 90', gol de prórroga de Mafra

    def test_total_over_se_liquida_con_goles_de_90(self):
        leg = {"mercado": "total", "op": "over", "linea": 2.5, "cuota": 1.5}
        self.assertEqual(sg.eval_leg(leg, ev(2, 2, "0", "0"))[0], "ACERTADA")    # 4 goles a 90'
        self.assertEqual(sg.eval_leg(leg, ev(2, 1, "1", "0"))[0], "FALLADA")     # 2-1 a 90': el gol de prórroga no cuenta

    def test_sin_prorroga_sigue_en_juego(self):
        leg = {"mercado": "1x2", "lado": "away", "cuota": 1.54}
        self.assertEqual(sg.eval_leg(leg, ev(1, 2, status="70"))[0], "EN_JUEGO")


if __name__ == "__main__":
    unittest.main()
