"""Comparativo v2: estado del resultado, procedencia, IC por partido, patas del usuario fuera del catálogo, versiones congeladas, registro acumulado y recorte en cuotas altas.
Datos FICTICIOS: EJEMPLO — NO REAL."""
import json
import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".claude", "skills", "seleccion-final-picks", "scripts"))
import acumulado as acu  # noqa: E402
import comparativo_resultados as cmp  # noqa: E402
import congelar_version as cv  # noqa: E402
import recalibrar_cuotas_altas as rc  # noqa: E402
import registrar_tickets as rt  # noqa: E402


class EstadoDelResultado(unittest.TestCase):
    def test_estados_no_finales_se_excluyen(self):
        self.assertEqual(cmp.result_status({"estado": "Finished", "h": 2, "a": 1, "h1": 1, "a1": 0}), "FINALIZADO")
        self.assertEqual(cmp.result_status({"estado": "Postponed", "h": None, "a": None}), "APLAZADO")
        self.assertEqual(cmp.result_status({"estado": "56", "h": 4, "a": 0}), "EN JUEGO")           # «56» era el minuto, no un marcador
        self.assertEqual(cmp.result_status({"estado": "Finished", "h": 56, "a": 4}), "DATO INVÁLIDO")
        self.assertEqual(cmp.result_status({"estado": "Finished", "h": 1, "a": 0, "h1": 2, "a1": 0}), "DATO INVÁLIDO")   # descanso mayor que el final
        self.assertEqual(cmp.result_status({"estado": "sin_resultado_en_la_api"}), "SIN RESULTADO")
        self.assertEqual(cmp.result_status({"estado": "Finished", "h": 0, "a": 0, "procedencia": {"goles_eventos": {"total": [2, 0], "descanso": [0, 0]}}}), "DATO INVÁLIDO")

    def test_settle_excluye_lo_no_final(self):
        import market_catalog as mc
        e = next(x for x in mc.CATALOG if x["id"] == "goles.total.over.2.5")
        for r in ({"estado": "Postponed"}, {"estado": "56", "h": 4, "a": 0}, {"estado": "Finished", "h": 56, "a": 4}):
            self.assertEqual(cmp.settle_entry(e, r)[0], cmp.NODATA)
        self.assertEqual(cmp.settle_entry(e, {"estado": "Finished", "h": 2, "a": 1})[0], cmp.WIN)


class Procedencia(unittest.TestCase):
    EV = {"goalscorer": [{"time": "18", "home_scorer": "", "away_scorer": "A"}, {"time": "45+2", "home_scorer": "B", "away_scorer": ""}, {"time": "90+7", "home_scorer": "", "away_scorer": "C"}, {"time": "103", "home_scorer": "D", "away_scorer": ""}]}

    def test_goles_desde_eventos_a_90_y_descanso(self):
        tot, ht = cmp.goals_from_events(self.EV)
        self.assertEqual((tot, ht), ([1, 2], [1, 1]))                 # el gol del 103' (prórroga) no cuenta

    def test_conflicto_de_bloques_de_corners(self):
        e = {"match_status": "Finished", "statistics": [{"type": "Corners", "home": "3", "away": "2"}], "statistics_1half": [{"type": "Corners", "home": "3", "away": "5"}]}
        r = cmp.parse_result(e)
        self.assertEqual(r["corners"], [3, 5])
        self.assertTrue(r["procedencia"]["corners_conflicto"])
        self.assertIn("CONFLICTO", cmp.provenance_text(r, "corners"))
        ok = cmp.parse_result({"match_status": "Finished", "statistics": [{"type": "Corners", "home": "3", "away": "2"}], "statistics_1half": [{"type": "Corners", "home": "3", "away": "2"}]})
        self.assertNotIn("CONFLICTO", cmp.provenance_text(ok, "corners"))


class IntervalosPorPartido(unittest.TestCase):
    def test_una_sola_agrupacion_no_da_intervalo_y_el_ic_es_mas_ancho_agrupando(self):
        self.assertEqual(acu.cluster_ci([("GANADA", 1.5, 0.7, "m1")] * 5), ("n/d", "n/d"))
        items = [("GANADA", 1.5, .7, f"m{i // 4}") for i in range(40)] + [("PERDIDA", 1.5, .7, f"m{10 + i // 4}") for i in range(40)]
        agrup = acu.cluster_ci(items)[0]
        indep = acu.cluster_ci([(r, o, p, i) for i, (r, o, p, _) in enumerate(items)])[0]
        ancho = lambda s: float(s.split("–")[1]) - float(s.split("–")[0])
        self.assertGreater(ancho(agrup), ancho(indep))              # correlación entre patas del mismo partido ⇒ más incertidumbre


class PatasDelUsuarioFueraDelCatalogo(unittest.TestCase):
    def test_ids_de_entradas(self):
        self.assertEqual(rt.entry_ids({"mercado": "1x2", "lado": "home"}), (["resultado.1x2.home"], None))
        self.assertEqual(rt.entry_ids({"mercado": "corners_equipo", "lado": "away", "op": "under", "linea": 4.5})[0], ["corners.equipo.away.under.4.5"])
        self.assertEqual(rt.entry_ids({"mercado": "handicap", "lado": "home", "linea": 1.5})[0], ["resultado.ah.home.+1.5"])
        ids, nota = rt.entry_ids({"mercado": "handicap", "lado": "home", "linea": 2.75})
        self.assertEqual(ids, ["resultado.ah.home.+2.5"])
        self.assertIn("cota inferior", nota)
        ids, nota = rt.entry_ids({"mercado": "combo", "subs": [{"tipo": "corners_equipo", "lado": "home", "op": "over", "linea": 3.5}, {"tipo": "handicap", "lado": "home", "linea": 1.5}]})
        self.assertEqual(ids, ["corners.equipo.home.over.3.5", "resultado.ah.home.+1.5"])
        self.assertIn("independencia", nota)
        self.assertIsNone(rt.entry_ids({"mercado": "combo", "subs": [{"tipo": "primer_gol", "lado": "home"}]})[0])

    def test_combina_p_como_producto(self):
        p, ag, el = rt.combine([{"p_modelo": 0.8, "agentes": "aprobada", "motivos_exclusion": []}, {"p_modelo": 0.5, "agentes": "degradada:x", "motivos_exclusion": ["degradada"]}])
        self.assertEqual((p, ag, el), (0.4, "aprobada;degradada:x", False))


class VersionesCongeladas(unittest.TestCase):
    def test_no_sobrescribe_y_es_idempotente(self):
        with tempfile.TemporaryDirectory() as d:
            libro, man = os.path.join(d, "libro.xlsx"), os.path.join(d, "m.jsonl")
            with open(libro, "wb") as f:
                f.write(b"v1")
            a, nueva = cv.freeze(libro, None, "x", man, os.path.join(d, "v"))
            b, nueva2 = cv.freeze(libro, None, "x", man, os.path.join(d, "v"))
            self.assertTrue(nueva)
            self.assertFalse(nueva2)
            self.assertEqual(a, b)
            with open(libro, "wb") as f:
                f.write(b"v2")
            c, nueva3 = cv.freeze(libro, None, "x", man, os.path.join(d, "v"))
            self.assertTrue(nueva3)
            self.assertNotEqual(a, c)
            with open(a, "rb") as fh:
                self.assertEqual(fh.read(), b"v1")                              # la versión anterior queda intacta
            self.assertEqual(cv.lookup(libro, man)["version"], 2)
            self.assertEqual(len(cv.read_manifest(man)), 2)


class RegistroAcumulado(unittest.TestCase):
    def test_append_ledger_completa_campos_sin_duplicar(self):
        with tempfile.TemporaryDirectory() as d:
            path = os.path.join(d, "l.jsonl")
            inv = {"m1": {"normalized_datetime_utc": "2026-10-15T19:00:00Z"}}
            leg = {"leg_id": "m1|x", "match_id": "m1", "grupo": "goles", "p_modelo": 0.7, "cuota": 1.5, "precio_tipo": "referencia", "agentes": "aprobada", "motivos_exclusion": [], "res": "GANADA", "observado_utc": "2026-10-15T10:00:00Z"}
            self.assertEqual(cmp.append_ledger(path, "runs/r", [leg], inv), 1)
            self.assertEqual(cmp.append_ledger(path, "runs/r", [leg], inv, {"liga": {"m1": "MLS"}, "legs": {"m1|x": {"rankings": ["Ranking seguridad"], "combinadas": 2, "usuario": ["G"]}}}), 0)
            rows = acu.leer(path)
            self.assertEqual(len(rows), 1)
            self.assertEqual((rows[0]["liga"], rows[0]["rankings"], rows[0]["usuario"]), ("MLS", ["Ranking seguridad"], ["G"]))
            self.assertEqual(acu.antiguedad(rows[0]), "6–24 h")

    def test_calibracion_y_metricas(self):
        rows = [{"p": 0.8, "res": "GANADA", "cuota": 1.3, "run": "r", "partido_id": f"m{i}"} for i in range(8)] + [{"p": 0.8, "res": "PERDIDA", "cuota": 1.3, "run": "r", "partido_id": f"n{i}"} for i in range(2)]
        c = acu.curva_calibracion(rows)
        self.assertEqual((c[0]["n"], c[0]["frecuencia"], c[0]["p_media"]), (10, 80.0, 80.0))
        self.assertEqual(acu.metricas(rows)["n"], 10)


class RecorteCuotasAltas(unittest.TestCase):
    def test_la_constante_de_la_banda_corrige_el_sesgo(self):
        def mk(run, n, win):
            return [{"run": run, "dia": "d", "partido_id": f"{run}{i}", "p": 0.62, "cuota": 1.9, "res": "GANADA" if i < win else "PERDIDA"} for i in range(n)]
        tr = mk("a", 60, 30)
        par = rc.fit_const(tr)
        self.assertAlmostEqual(par["c"], 0.5)
        te = mk("b", 60, 30)
        self.assertLess(rc.brier(te, [rc.apply("frecuencia de la banda", par, r) for r in te]), rc.brier(te, [r["p"] for r in te]))
        sh = rc.fit_shift(tr)
        self.assertAlmostEqual(sh["delta"], 0.12, places=2)


if __name__ == "__main__":
    unittest.main()
