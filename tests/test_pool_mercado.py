import importlib.util
import os
import unittest

RUTA = os.path.join(os.path.dirname(__file__), "..", ".claude", "skills", "seleccion-final-picks", "scripts", "pool_mercado.py")
spec = importlib.util.spec_from_file_location("pool_mercado", RUTA)
pm = importlib.util.module_from_spec(spec)
spec.loader.exec_module(pm)


def ls(x):
    return {"opening": str(x), "last_seen": str(x)}


def libro(nombre, h, d, a, o25, u25, y=None, n=None, dc=None):
    mk = {"match_odds": {"home": ls(h), "draw": ls(d), "away": ls(a)}, "total_goals": {"2.5": {"over": ls(o25), "under": ls(u25)}}}
    if y:
        mk["btts"] = {"yes": ls(y), "no": ls(n)}
    if dc:
        mk["double_chance"] = {"home_draw": ls(dc[0]), "home_away": ls(dc[1]), "draw_away": ls(dc[2])}
    return {"bookmaker": nombre, "markets": mk}


MATCH = {"id": "mt_1", "utc_date": "2026-11-01T18:00:00.000Z", "home_team": {"name": "Alfa"}, "away_team": {"name": "Beta"}, "status": "scheduled"}


class PoolMercado(unittest.TestCase):
    def test_probabilidades_sin_margen_y_mediana(self):
        odds = {"data": {"bookmakers": [libro("A", 2.0, 3.4, 3.8, 1.9, 1.95), libro("B", 2.05, 3.3, 3.7, 1.95, 1.9), libro("C", 2.0, 3.5, 3.9, 1.9, 1.95)]}}
        patas, band = pm.patas_de_partido(MATCH, odds)
        por = {(p["mercado"], p["seleccion"]): p for p in patas}
        self.assertAlmostEqual(por[("1x2", "Gana Alfa")]["cuota"], 2.0)
        self.assertAlmostEqual(por[("1x2", "Gana Alfa")]["p"], 0.4708, places=2)
        o = por[("goles", "Más de 2.5 goles")]; u = por[("goles", "Menos de 2.5 goles")]
        self.assertAlmostEqual(o["p"] + u["p"], 1.0, places=3)
        self.assertEqual(o["n_casas"], 3)
        self.assertEqual(band, [])

    def test_menos_de_tres_casas_no_genera_pata(self):
        odds = {"data": {"bookmakers": [libro("A", 2.0, 3.4, 3.8, 1.9, 1.95), libro("B", 2.05, 3.3, 3.7, 1.95, 1.9)]}}
        self.assertEqual(pm.patas_de_partido(MATCH, odds)[0], [])

    def test_par_imposible_se_descarta_y_se_avisa(self):
        malo = libro("X", 2.0, 3.4, 3.8, 1.03, 1.02)
        odds = {"data": {"bookmakers": [libro("A", 2.0, 3.4, 3.8, 1.9, 1.95), libro("B", 2.05, 3.3, 3.7, 1.95, 1.9), libro("C", 2.0, 3.5, 3.9, 1.9, 1.95), malo]}}
        patas, band = pm.patas_de_partido(MATCH, odds)
        o = [p for p in patas if p["seleccion"] == "Más de 2.5 goles"][0]
        self.assertEqual(o["n_casas"], 3)
        self.assertTrue(any("X" in b and "2.5" in b for b in band))

    def test_doble_oportunidad_usa_p_de_1x2(self):
        odds = {"data": {"bookmakers": [libro(n, 2.0, 3.4, 3.8, 1.9, 1.95, dc=(1.25, 1.3, 1.8)) for n in "ABC"]}}
        patas, _ = pm.patas_de_partido(MATCH, odds)
        dc = [p for p in patas if p["seleccion"] == "Alfa o empate"][0]
        self.assertAlmostEqual(dc["cuota"], 1.25)
        self.assertGreater(dc["p"], 0.7)

    def test_buscar_respeta_rangos_y_un_partido_por_pata(self):
        patas = []
        for i, (c, p) in enumerate([(1.5, 0.64), (1.6, 0.6), (1.7, 0.56), (1.3, 0.74), (1.4, 0.69)]):
            patas.append({"match_id": f"m{i}", "partido": f"P{i}", "seleccion": "s", "cuota": c, "p": p, "valor": c * p})
        patas.append({"match_id": "m0", "partido": "P0", "seleccion": "t", "cuota": 1.5, "p": 0.66, "valor": 0.99})
        res = pm.buscar(patas, 1.2, 2.1, 3.9, 4.5, 3, 5, 5)
        self.assertTrue(res)
        for r in res:
            self.assertGreaterEqual(r["cuota_base"], 3.9); self.assertLessEqual(r["cuota_base"], 4.5)
            ms = [p["match_id"] for p in r["patas"]]
            self.assertEqual(len(ms), len(set(ms)))
        self.assertEqual(res, sorted(res, key=lambda r: -r["p_ganar"]))

    def test_excluye_equipos_juveniles_y_femenino(self):
        for n in ("Barca Women", "Ajax U21", "Real Madrid II", "Boca Reserves"):
            self.assertTrue(pm.EXCLUIR_EQUIPO.search(n), n)
        self.assertFalse(pm.EXCLUIR_EQUIPO.search("Aston Villa"))


if __name__ == "__main__":
    unittest.main()


class ReglasDeConcentracion(unittest.TestCase):
    def _patas(self):
        out = []
        for i, (sel, c, p) in enumerate([("Más de 2.5 goles", 1.8, 0.52), ("Más de 2.5 goles", 1.75, 0.55), ("A o empate", 1.3, 0.75), ("B o empate", 1.3, 0.75), ("C o D (sin empate)", 1.3, 0.75), ("E o F (sin empate)", 1.3, 0.75)]):
            out.append({"match_id": f"m{i}", "partido": f"P{i}", "seleccion": sel, "cuota": c, "p": p, "valor": c * p})
        return out

    def test_un_solo_over_por_ticket(self):
        res = pm.buscar(self._patas(), 1.2, 2.1, 3.0, 5.0, 3, 4, 50, max_overs=1)
        self.assertTrue(res)
        for r in res:
            self.assertLessEqual(sum(1 for p in r["patas"] if p["seleccion"].startswith("Más de")), 1)

    def test_sin_limite_aparecen_dos_overs(self):
        res = pm.buscar(self._patas(), 1.2, 2.1, 3.0, 5.0, 3, 4, 50)
        self.assertTrue(any(sum(1 for p in r["patas"] if p["seleccion"].startswith("Más de")) == 2 for r in res))

    def test_ninguna_pata_en_mas_de_max_rep_tickets(self):
        res = pm.buscar(self._patas(), 1.2, 2.1, 3.0, 5.0, 3, 4, 200, max_overs=1)
        elegidos = pm.diversificar(res, 3, 6, max_rep=2)
        cuenta = {}
        for t in elegidos:
            for p in t["patas"]:
                cuenta[p["match_id"]] = cuenta.get(p["match_id"], 0) + 1
        self.assertTrue(cuenta and max(cuenta.values()) <= 2)
