"""Reglas de liquidación del comparativo con casos que OCURRIERON entre el 14 y el 16-oct-2026 (fixture `fixtures/resultados_reales_14_16oct.json`: resultados reales de apifootball
tal como los guarda `parse_result`, y eventos crudos recortados). Los casos sintéticos (variaciones de un partido real) se rotulan «variante».
Cuando una regla es ambigua la prueba exige SIN DATO («regla no confirmada»), nunca una suposición."""
import copy
import json
import os
import unittest

import helpers  # noqa: F401  (añade scripts/ al path)
import adapters
import api_detalle as ad
import comparativo_resultados as cmp
import market_catalog as mc

E = {e["id"]: e for e in mc.CATALOG}
FX = json.load(open(os.path.join(os.path.dirname(__file__), "fixtures", "resultados_reales_14_16oct.json"), encoding="utf-8"))
RES, RAW = FX["resultados"], FX["eventos_crudos"]
W, L, V, N = cmp.WIN, cmp.LOSE, cmp.VOID, cmp.NODATA


def real(prefix):
    k = next(k for k in RES if prefix in k)
    return copy.deepcopy(RES[k])


def raw(prefix):
    k = next(k for k in RAW if prefix in k)
    return copy.deepcopy(RAW[k])


def s(eid, r):
    return cmp.settle_entry(E[eid], r)


class Totales(unittest.TestCase):
    def test_linea_entera_se_anula_si_el_total_la_iguala(self):
        r = real("Burnley – Wolves")             # 1–2: 3 goles
        self.assertEqual(s("goles.total_entero.over.3", r)[0], V)
        self.assertEqual(s("goles.total_entero.under.3", r)[0], V)
        self.assertEqual(s("goles.total_entero.over.2", r)[0], W)
        self.assertEqual(s("goles.total_entero.under.4", r)[0], W)

    def test_media_linea_no_tiene_devolucion(self):
        r = real("Burnley – Wolves")
        self.assertEqual(s("goles.total.over.2.5", r)[0], W)
        self.assertEqual(s("goles.total.under.2.5", r)[0], L)
        self.assertEqual(s("goles.total.under.3.5", r)[0], W)

    def test_ambos_anotan_y_goles_por_equipo(self):
        r = real("Frankfurt")                    # 1–0
        self.assertEqual(s("goles.btts.yes", r)[0], L)
        self.assertEqual(s("goles.btts.no", r)[0], W)
        self.assertEqual(s("goles.equipo.away.over.0.5", r)[0], L)
        self.assertEqual(s("goles.equipo.home.under.1.5", r)[0], W)

    def test_primera_parte_usa_el_descanso_real(self):
        r = real("Le Mans")                      # 0–3, descanso 0–0
        self.assertEqual(s("primera_parte.total.under.0.5", r)[0], W)
        self.assertEqual(s("primera_parte.1x2.draw", r)[0], W)
        self.assertEqual(s("goles.total.over.2.5", r)[0], W)


class EmpateNoValidoYResultado(unittest.TestCase):
    def test_empate_0_0_real(self):
        r = real("Sydney")                       # 0–0
        self.assertEqual(s("resultado.1x2.draw", r)[0], W)
        self.assertEqual(s("resultado.dnb.home", r)[0], V)
        self.assertEqual(s("resultado.dnb.away", r)[0], V)
        self.assertEqual(s("resultado.dc.1x", r)[0], W)
        self.assertEqual(s("resultado.dc.12", r)[0], L)

    def test_dnb_con_ganador(self):
        r = real("Le Mans")                      # 0–3 visitante
        self.assertEqual(s("resultado.dnb.away", r)[0], W)
        self.assertEqual(s("resultado.dnb.home", r)[0], L)


class HandicapAsiatico(unittest.TestCase):
    def setUp(self):
        self.r = real("Frosinone")               # 4–2: el local gana por 2

    def test_media_linea(self):
        self.assertEqual(s("resultado.ah.home.-1.5", self.r)[0], W)
        self.assertEqual(s("resultado.ah.home.-2.5", self.r)[0], L)
        self.assertEqual(s("resultado.ah.away.+1.5", self.r)[0], L)
        self.assertEqual(s("resultado.ah.away.+2.5", self.r)[0], W)

    def test_linea_entera_devuelve_si_empata_tras_el_handicap(self):
        self.assertEqual(s("resultado.ah_entero.home.-2", self.r)[0], V)
        self.assertEqual(s("resultado.ah_entero.away.+2", self.r)[0], V)
        self.assertEqual(s("resultado.ah_entero.home.-1", self.r)[0], W)
        self.assertEqual(s("resultado.ah_entero.away.+1", self.r)[0], L)

    def test_cuarto_de_linea_es_ganada_o_perdida_a_medias(self):
        k = lambda side, line: ad.settle_additional(f"asian_handicap|{side}|{line}", self.r)[0]
        self.assertEqual(k("home", "-1.75"), W + " (½)")      # -1.5 gana, -2 se anula
        self.assertEqual(k("home", "-2.25"), L + " (½)")      # -2 se anula, -2.5 pierde
        self.assertEqual(k("home", "-1.25"), W)               # -1 y -1.5 ganan
        self.assertEqual(k("away", "+1.75"), L + " (½)")      # +1.5 pierde, +2 se anula
        self.assertEqual(k("away", "+2.25"), W + " (½)")      # +2 se anula, +2.5 gana

    def test_beneficio_de_las_mitades(self):
        self.assertAlmostEqual(cmp.payoff(W + " (½)", 1.8), 0.4)
        self.assertAlmostEqual(cmp.payoff(L + " (½)", 1.8), -0.5)
        self.assertEqual(cmp.hit(W + " (½)"), 1)
        self.assertEqual(cmp.hit(V), None)


class HandicapEuropeo(unittest.TestCase):
    def test_tres_resultados_con_la_linea_sumada_al_local(self):
        r = real("Frosinone")                    # 4–2
        self.assertEqual(s("resultado.eh.home.-1", r)[0], W)     # 3–2 tras el hándicap
        self.assertEqual(s("resultado.eh.draw.-1", r)[0], L)
        self.assertEqual(s("resultado.eh.home.-2", r)[0], L)     # 2–2: empate tras el hándicap
        self.assertEqual(s("resultado.eh.draw.-2", r)[0], W)
        self.assertEqual(s("resultado.eh.away.-2", r)[0], L)
        self.assertEqual(s("resultado.eh.away.+1", r)[0], L)     # 5–2

    def test_handicap_positivo_al_local(self):
        r = real("Le Mans")                      # 0–3
        self.assertEqual(s("resultado.eh.draw.+2", r)[0], L)     # 2–3
        self.assertEqual(s("resultado.eh.away.+2", r)[0], W)
        self.assertEqual(s("resultado.eh.draw.+1", r)[0], L)
        self.assertEqual(s("resultado.eh.away.+1", r)[0], W)


class CornersPorEquipo(unittest.TestCase):
    def test_un_equipo_con_cero_corners_es_un_dato_valido(self):
        """Bug corregido el 17-oct: 5 partidos reales del 14 al 16-oct (bloques de la API coincidentes, 30–35 remates contra 4) tenían un equipo con 0 córners y todas sus líneas salían SIN DATO."""
        r = real("Fluminense")                   # córners 6–0
        self.assertEqual(r["corners"], [6, 0])
        self.assertEqual(s("corners.total.under.6.5", r)[0], W)
        self.assertEqual(s("corners.total.over.6.5", r)[0], L)
        self.assertEqual(s("corners.equipo.away.under.2.5", r)[0], W)
        self.assertEqual(s("corners.equipo.away.over.2.5", r)[0], L)
        self.assertEqual(s("corners.equipo.home.over.5.5", r)[0], W)
        r2 = real("Panathinaikos")               # 11–0
        self.assertEqual(s("corners.equipo.home.over.7.5", r2)[0], W)
        self.assertEqual(s("corners.equipo.away.under.2.5", r2)[0], W)

    def test_cero_a_cero_sigue_siendo_dato_dudoso(self):
        r = real("Fluminense")
        r["corners"] = [0, 0]
        res, why = s("corners.total.under.8.5", r)
        self.assertEqual(res, N)
        self.assertIn("0–0", why)

    def test_el_bloque_de_la_1_parte_siempre_es_menor_y_no_es_un_conflicto(self):
        """Antes se marcaba «CONFLICTO» en 104 de 107 partidos porque se comparaba el bloque del partido (11–0) con el de la 1.ª parte (5–0). Solo es conflicto si el del partido va POR DETRÁS del de la 1.ª parte."""
        pr = cmp.parse_result(raw("Panathinaikos"))
        self.assertEqual(pr["corners"], [11, 0])
        self.assertEqual(pr["procedencia"]["corners_bloques"], {"statistics": [11, 0], "statistics_1half": [5, 0]})
        self.assertFalse(pr["procedencia"]["corners_conflicto"])
        e = raw("Panathinaikos")
        e["statistics"] = [{"type": "Corners", "home": "3", "away": "0"}]          # variante: el bloque del partido va retrasado
        pr2 = cmp.parse_result(e)
        self.assertTrue(pr2["procedencia"]["corners_conflicto"])
        self.assertEqual(pr2["corners"], [5, 0])

    def test_el_bloque_retrasado_no_baja_los_corners(self):
        e = {"statistics": [{"type": "Corners", "home": "3", "away": "5"}], "statistics_1half": [{"type": "Corners", "home": "4", "away": "5"}]}
        self.assertEqual(cmp.sg._corner_pair(e), (4, 5))


class Tarjetas(unittest.TestCase):
    def card(self, minute, kind, who="Jugador", side="home", info="1st Half"):
        return {"time": str(minute), "home_fault": who if side == "home" else "", "away_fault": who if side == "away" else "", "card": kind, "home_player_id": "", "away_player_id": "", "score_info_time": info}

    def pts(self, cards):
        return adapters._card_points({"cards": cards})

    def test_regla_a1_r2(self):
        self.assertEqual(self.pts([self.card(10, "yellow card")]), (1, 0))
        self.assertEqual(self.pts([self.card(10, "red card")]), (2, 0))
        self.assertEqual(self.pts([self.card(10, "yellow card"), self.card(30, "red card")]), (3, 0))       # amarilla y luego roja directa: máx. 3 por jugador
        self.assertEqual(self.pts([self.card(10, "yellow card", side="away"), self.card(20, "yellow card", "Otro", "away")]), (0, 2))

    def test_segunda_amarilla_cuenta_2_en_total_confirmado_por_la_persona_usuaria(self):
        self.assertEqual(self.pts([self.card(10, "yellow card"), self.card(60, "yellow card"), self.card(60, "red card")]), (2, 0))

    def test_la_prorroga_no_cuenta_caso_real(self):
        e = raw("Santarem")                      # 5 amarillas, 2 en la prórroga (105+2 y 108)
        self.assertEqual(adapters._card_points(e), (0, 3))
        self.assertEqual(len(e["cards"]), 5)

    def test_amarilla_y_roja_en_el_mismo_minuto_es_ambiguo_caso_real_atlante(self):
        """Atlante – Pumas 16-oct, min 34: M. Herrera aparece con UNA amarilla y UNA roja en el mismo minuto. ¿Doble amarilla (2 puntos) o amarilla + roja directa (3)? La fuente no lo dice."""
        cards = [self.card(34, "yellow card", "M. Herrera"), self.card(34, "red card", "M. Herrera")]
        self.assertEqual(self.pts(cards), (3, 0))
        pts, alt, amb = adapters._card_points_variants({"cards": cards})
        self.assertEqual((pts, alt, amb), ([3, 0], [2, 0], 1))
        r = real("Fluminense")
        r["tarjetas"], r["tarjetas_alt"], r["tarjetas_ambiguas"] = [3, 0], [2, 0], 1
        res, why = s("cards_pts.equipo.home.over.2.5", r)           # 3 pts gana, 2 pts pierde → no se asume
        self.assertEqual(res, N)
        self.assertIn("regla no confirmada", why)
        self.assertEqual(s("cards_pts.equipo.home.over.1.5", r)[0], W)    # con 3 o con 2 puntos gana: se liquida
        self.assertEqual(s("cards_pts.equipo.home.under.3.5", r)[0], W)

    def test_total_de_tarjetas_real_mirassol(self):
        r = real("Mirassol")                     # 2 + 8 = 10 puntos
        self.assertEqual(s("cards_pts.total.over.9.5", r)[0], W)
        self.assertEqual(s("cards_pts.equipo.away.over.5.5", r)[0], W)
        self.assertEqual(s("cards_pts.equipo.home.over.2.5", r)[0], L)

    def test_sin_tarjetas_en_la_fuente_no_se_inventa(self):
        r = real("Boston River")
        self.assertIsNone(r["tarjetas"])
        self.assertEqual(s("cards_pts.total.over.1.5", r)[0], N)


class ProrrogaYPenales(unittest.TestCase):
    def test_la_tanda_de_penales_no_cuenta_como_goles_caso_real_boston_river(self):
        """Boston River – River Plate (14-oct): 0–0 a 90', tanda 4–3. La lista de goleadores trae los 7 penales de la tanda; antes el resultado salía DATO INVÁLIDO."""
        e = raw("Boston River")
        pr = cmp.parse_result(e)
        self.assertEqual((pr["h"], pr["a"]), (0, 0))
        self.assertEqual(pr["procedencia"]["goles_eventos"]["total"], [0, 0])
        self.assertIsNone(pr["primer_gol"])
        self.assertTrue(pr["marcador_90_directo"])
        self.assertEqual(cmp.result_status(pr), "FINALIZADO")
        self.assertEqual(s("goles.total.under.0.5", pr)[0], W)
        self.assertEqual(s("resultado.1x2.draw", pr)[0], W)

    def test_la_prorroga_no_cuenta_caso_real_santarem(self):
        e = raw("Santarem")                      # 2–2 a 90', gol en el 109'
        pr = cmp.parse_result(e)
        self.assertEqual((pr["h"], pr["a"]), (2, 2))
        self.assertEqual(pr["procedencia"]["goles_eventos"]["total"], [2, 2])
        self.assertEqual(cmp.result_status(pr), "FINALIZADO")
        self.assertEqual(s("goles.total.under.4.5", pr)[0], W)

    def test_sin_marcador_a_90_en_prorroga_es_regla_no_confirmada(self):
        e = raw("Santarem")
        e["match_hometeam_ft_score"] = e["match_awayteam_ft_score"] = ""
        pr = cmp.parse_result(e)
        self.assertFalse(pr["marcador_90_directo"])
        res, why = s("goles.total.under.4.5", pr)
        self.assertEqual(res, N)
        self.assertIn("regla no confirmada", why)
        self.assertEqual(s("primera_parte.total.under.0.5", pr)[0], W)      # el descanso no depende de la prórroga

    def test_corners_y_remates_en_prorroga_son_regla_no_confirmada(self):
        pr = cmp.parse_result(raw("Santarem"))
        pr["remates"], pr["a_puerta"] = [14, 9], [5, 3]                      # variante: con estadística de remates presente
        for eid in ("corners.total.over.8.5", "corners.equipo.away.over.3.5", "shots.total.over.14.5", "sot.total.over.5.5"):
            res, why = s(eid, pr)
            self.assertEqual(res, N, eid)
            self.assertIn("regla no confirmada", why)
        self.assertNotEqual(s("cards_pts.total.over.1.5", pr)[0], "")        # las tarjetas sí se separan por `score_info_time`


class EstadoDelPartido(unittest.TestCase):
    def test_en_juego_real_atlante(self):
        r = real("Atlante")
        self.assertEqual(r["estado"], "66")
        self.assertEqual(cmp.result_status(r), "EN JUEGO")
        res, why = s("goles.total.over.1.5", r)
        self.assertEqual(res, N)
        self.assertIn("excluido", why)

    def test_descanso_y_tiempo_de_descuento_son_en_juego(self):
        for st in ("Half Time", "45+", "90+", "34", "HT"):
            self.assertEqual(cmp.result_status({"estado": st}), "EN JUEGO", st)

    def test_aplazado_real_santa_fe(self):
        r = real("Santa Fe")
        self.assertEqual(cmp.result_status(r), "APLAZADO")
        self.assertEqual(s("resultado.1x2.home", r)[0], N)

    def test_cancelado_suspendido_y_sin_resultado(self):
        self.assertEqual(cmp.result_status({"estado": "Cancelled"}), "CANCELADO")
        self.assertEqual(cmp.result_status({"estado": "Abandoned"}), "SUSPENDIDO")
        self.assertEqual(cmp.result_status({"estado": "sin_resultado_en_la_api"}), "SIN RESULTADO")
        self.assertEqual(cmp.result_status({"estado": "Not Started"}), "SIN RESULTADO")

    def test_dato_invalido(self):
        base = {"estado": "Finished", "h": 2, "a": 1, "h1": 3, "a1": 0}
        self.assertEqual(cmp.result_status(base), "DATO INVÁLIDO")                      # descanso mayor que el final
        self.assertEqual(cmp.result_status({"estado": "Finished", "h": 20, "a": 0}), "DATO INVÁLIDO")
        self.assertEqual(cmp.result_status(dict(base, h1=1, a1=0)), "FINALIZADO")


class Combinadas(unittest.TestCase):
    def test_pierde_aunque_otra_pata_no_tenga_dato(self):
        self.assertEqual(cmp.combo_status([L, N, W], [1.5, 1.4, 1.3]), (L, None))

    def test_sin_dato_si_ninguna_perdio_pero_falta_una(self):
        self.assertEqual(cmp.combo_status([W, N], [1.5, 1.4]), (N, None))

    def test_patas_anuladas_valen_cuota_1(self):
        est, cuota = cmp.combo_status([W, V, W], [1.5, 1.4, 1.2])
        self.assertEqual(est, W)
        self.assertAlmostEqual(cuota, 1.8)

    def test_todas_anuladas_la_combinada_se_anula(self):
        self.assertEqual(cmp.combo_status([V, V], [1.5, 1.4]), (V, 1.0))


class TablaDeReglas(unittest.TestCase):
    def test_toda_familia_del_catalogo_tiene_regla_y_las_dudosas_estan_marcadas(self):
        prefijos = [r[0] for r in cmp.RULES]
        for e in mc.CATALOG:
            self.assertTrue(any(e["id"].startswith(p) for p in prefijos), e["id"])
        no_conf = [r[1] for r in cmp.RULES if "NO CONFIRMADA" in r[3]]
        for f in ("Fueras de juego", "Tarjetas (puntos)", "Córners (total y por equipo)"):
            self.assertIn(f, no_conf)


if __name__ == "__main__":
    unittest.main()
