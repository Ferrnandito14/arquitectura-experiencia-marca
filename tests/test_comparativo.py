"""Comparativo contra resultados reales: liquidación de las entradas del catálogo. Datos FICTICIOS: EJEMPLO — NO REAL."""
import unittest

import helpers  # noqa: F401  (añade scripts/ al path)
import comparativo_resultados as cmp
import market_catalog as mc

E = {e["id"]: e for e in mc.CATALOG}


def r(h, a, h1=0, a1=0, corners=(5, 4), tarjetas=(1, 2), estado="Finished", **kw):
    return dict({"estado": estado, "h": h, "a": a, "h1": h1, "a1": a1, "corners": corners, "tarjetas": tarjetas, "remates": (10, 9), "a_puerta": (4, 3), "fueras": (2, 1)}, **kw)


class Liquidacion(unittest.TestCase):
    def s(self, eid, res):
        return cmp.settle_entry(E[eid], res)[0]

    def test_resultado_doble_oportunidad_y_empate_no_valido(self):
        self.assertEqual(self.s("resultado.1x2.home", r(2, 1)), cmp.WIN)
        self.assertEqual(self.s("resultado.dc.x2", r(2, 1)), cmp.LOSE)
        self.assertEqual(self.s("resultado.dc.12", r(1, 1)), cmp.LOSE)
        self.assertEqual(self.s("resultado.dnb.home", r(1, 1)), cmp.VOID)

    def test_totales_lineas_enteras_btts_y_goles_por_equipo(self):
        self.assertEqual(self.s("goles.total.over.2.5", r(2, 1)), cmp.WIN)
        self.assertEqual(self.s("goles.total.under.3.5", r(3, 3)), cmp.LOSE)
        self.assertEqual(self.s("goles.total_entero.over.3", r(2, 1)), cmp.VOID)
        self.assertEqual(self.s("goles.btts.yes", r(1, 0)), cmp.LOSE)
        self.assertEqual(self.s("goles.equipo.away.over.0.5", r(1, 0)), cmp.LOSE)

    def test_primera_parte_usa_el_descanso(self):
        self.assertEqual(self.s("primera_parte.total.over.0.5", r(3, 0, 1, 0)), cmp.WIN)
        self.assertEqual(self.s("primera_parte.1x2.draw", r(2, 0, 0, 0)), cmp.WIN)

    def test_handicap_asiatico_y_europeo(self):
        self.assertEqual(self.s("resultado.ah.away.+2.5", r(3, 0)), cmp.LOSE)
        self.assertEqual(self.s("resultado.ah.away.+2.5", r(2, 0)), cmp.WIN)
        self.assertEqual(self.s("resultado.ah_entero.home.-2", r(2, 0)), cmp.VOID)
        self.assertEqual(self.s("resultado.eh.draw.-2", r(2, 0)), cmp.WIN)

    def test_corners_tarjetas_y_sin_dato(self):
        self.assertEqual(self.s("corners.total.over.8.5", r(1, 0, corners=(5, 4))), cmp.WIN)
        self.assertEqual(self.s("corners.equipo.away.over.2.5", r(1, 0, corners=(5, 4))), cmp.WIN)
        self.assertEqual(self.s("cards_pts.total.over.2.5", r(1, 0, tarjetas=(1, 2))), cmp.WIN)
        self.assertEqual(self.s("cards_pts.total.over.2.5", r(1, 0, tarjetas=None)), cmp.NODATA)       # la fuente no trae tarjetas: no se inventa
        self.assertEqual(self.s("corners.total.over.8.5", r(1, 0, corners=(10, 0))), cmp.NODATA)       # un cero total de córners es dato dudoso
        self.assertEqual(self.s("goles.total.over.0.5", r(0, 0, estado="Not Started")), cmp.NODATA)

    def test_prorroga_y_penales_no_cuentan_y_el_beneficio_se_calcula_a_la_cuota_del_libro(self):
        self.assertEqual(cmp.parse_result({"match_status": "After Pen.", "match_hometeam_score": "5", "match_awayteam_score": "4", "match_hometeam_ft_score": "1", "match_awayteam_ft_score": "1"})["h"], 1)
        self.assertAlmostEqual(cmp.payoff(cmp.WIN, 1.5), 0.5)
        self.assertEqual(cmp.payoff(cmp.LOSE, 1.5), -1.0)
        self.assertEqual(cmp.payoff(cmp.VOID, 1.5), 0.0)

    def test_el_comparativo_no_puede_llamarse_como_un_libro_original(self):
        with self.assertRaises(SystemExit):
            cmp.main(["--run", "x", "--book", "y", "--out", "dist/ligas-14-oct-v2.xlsx"])


if __name__ == "__main__":
    unittest.main()
