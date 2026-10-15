"""Referencia ampliada para torneos continentales: guardia de identidad (club homónimo de otro país), ámbitos y H2H. Datos FICTICIOS: EJEMPLO — NO REAL."""
import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".claude", "skills", "seleccion-final-picks", "scripts"))
import contexto_continental as cc  # noqa: E402


def ev(date, league, country, h, a, hs, as_, hid="1", aid="2", status="Finished"):
    return {"match_date": date, "league_name": league, "country_name": country, "match_status": status, "match_hometeam_id": hid, "match_awayteam_id": aid,
            "match_hometeam_name": h, "match_awayteam_name": a, "match_hometeam_score": str(hs), "match_awayteam_score": str(as_)}


class Identidad(unittest.TestCase):
    def test_club_homonimo_de_otro_pais_y_amistosos_se_excluyen(self):
        evs = [ev("2026-05-01", "Liga Profesional Argentina - Clausura", "Argentina", "Estudiantes", "X", 1, 0) for _ in range(5)]
        evs += [ev("2026-05-02", "CONMEBOL Libertadores - Group Stage", "intl", "Estudiantes", "Y", 1, 1)]
        evs += [ev("2026-05-03", "Division di Honor - Relegation", "Aruba", "Estudiantes", "Z", 10, 0)] * 3
        evs += [ev("2026-05-04", "Club Friendlies - Club Friendly", "World", "Estudiantes", "W", 3, 3)]
        keep, excl, home = cc.identity_filter(evs)
        self.assertEqual((len(keep), excl, home), (6, 3, "argentina"))

    def test_competiciones_uefa_con_pais_europe_no_se_excluyen(self):
        evs = [ev("2026-05-01", "Primeira Liga", "Portugal", "Benfica", "X", 1, 0) for _ in range(5)]
        evs += [ev("2026-02-17", "UEFA Champions League - 1/16-finals", "Europe", "Benfica", "Real Madrid", 0, 1), ev("2026-07-23", "UEFA Europa League - Qualifying", "Europe", "St. Gallen", "Benfica", 1, 2)]
        keep, excl, home = cc.identity_filter(evs)
        self.assertEqual((len(keep), excl, home), (7, 0, "portugal"))
        self.assertEqual(cc.ambito("UEFA Europa League - Qualifying", "Europe"), "continental")

    def test_championship_no_es_continental(self):
        import rotation_risk
        for n in ("Championship", "Championship - Play-offs Final", "Championship - Semi-finals"):
            self.assertFalse(cc.is_continental(n), n)
            self.assertFalse(rotation_risk.decisive_phase(n), n)
        self.assertTrue(cc.is_continental("UEFA Champions League - League Phase"))
        self.assertTrue(rotation_risk.decisive_phase("UEFA Champions League - Semi-finals"))

    def test_sin_pais_domestico_claro_no_excluye_nada(self):
        keep, excl, home = cc.identity_filter([ev("2026-05-02", "CONMEBOL Libertadores", "intl", "A", "B", 1, 1)])
        self.assertEqual((len(keep), excl, home), (1, 0, None))


class Ambitos(unittest.TestCase):
    def test_ambito_por_competicion(self):
        self.assertEqual(cc.ambito("CONMEBOL Libertadores - Semi-finals", "intl"), "continental")
        self.assertEqual(cc.ambito("UEFA Europa League - League Phase", "eurocups"), "continental")
        self.assertEqual(cc.ambito("Copa Argentina - 1/8-finals", "Argentina"), "copa_nacional")
        self.assertEqual(cc.ambito("Serie A", "Brazil"), "liga")

    def test_resumen_descriptivo_con_n_y_sin_datos(self):
        s = cc.summarize([{"gf": 1, "ga": 0}, {"gf": 2, "ga": 2}, {"gf": 0, "ga": 0}, {"gf": None, "ga": 1}])
        self.assertEqual((s["n"], s["goles_por_partido"], s["pct_menos_2_5"], s["pct_ambos_anotan"]), (3, 1.67, 67, 33))
        self.assertEqual(cc.summarize([]), {"n": 0})


class H2H(unittest.TestCase):
    def test_h2h_solo_previos_finalizados_y_resumen(self):
        resp = {"firstTeam_VS_secondTeam": [ev("2026-05-21", "CONMEBOL Libertadores", "intl", "Flamengo", "Estudiantes", 1, 0), ev("2026-04-30", "CONMEBOL Libertadores", "intl", "Estudiantes", "Flamengo", 1, 1),
                                           ev("2026-10-15", "CONMEBOL Libertadores", "intl", "Estudiantes", "Flamengo", 0, 0, status="Not Started")]}
        r = cc.h2h_context(lambda **p: resp, 989, 542, "2026-10-15")
        self.assertEqual((r["n"], r["goles_por_partido"], r["pct_menos_2_5"]), (2, 1.5, 100))
        self.assertEqual(r["partidos"][0]["marcador"], "1-0")

    def test_no_toca_p_modelo(self):
        import inspect
        self.assertNotIn("p_modelo", inspect.getsource(cc).replace("NO entra en p_modelo", "").replace("no entra en p_modelo", "").replace("NO cambia `p_modelo`", ""))


if __name__ == "__main__":
    unittest.main()
