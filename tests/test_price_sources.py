"""Fase 2: proveedores de precio (caché cruda de apifootball, football-data, capturas del usuario), líneas completas del adaptador y plantilla de precios.
Datos FICTICIOS: EJEMPLO — NO REAL."""
import csv
import hashlib
import json
import os
import tempfile
import unittest

import helpers  # noqa: F401  (añade scripts/ al path)
import adapters
import common
import market_catalog as mc
import market_coverage as cov
import price_sources as ps


def _dump(path, obj):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f)


def odds_row(mid, book, **kw):
    r = {"match_id": mid, "odd_bookmakers": book, "odd_date": "2026-10-13 21:00:00", "odd_1": "2.0", "odd_x": "3.4", "odd_2": "3.6", "odd_1x": "1.3", "odd_12": "1.3", "odd_x2": "1.7",
         "o+2.5": "1.9", "u+2.5": "1.95", "o+2": "1.5", "u+2": "2.6", "ah-1_1": "2.9", "ah-1_2": "1.4", "ah0_1": "1.6", "ah0_2": "2.2", "bts_yes": "1.8", "bts_no": "1.9"}
    r.update(kw)
    return r


def make_run(rows_by_query, now="2026-10-13T22:59:32Z"):
    """Run temporal con `sources/consultas.jsonl` y el cuerpo en caché (<sha256 de la URL redactada>.body) como los deja common.Client."""
    run = tempfile.mkdtemp()
    os.makedirs(os.path.join(run, "sources"))
    os.makedirs(os.path.join(run, "cache"))
    with open(os.path.join(run, "sources", "consultas.jsonl"), "w", encoding="utf-8") as log:
        for qs, rows in rows_by_query:
            url = f"https://apiv3.apifootball.com/?action=get_odds&{qs}&APIkey=***"
            base = os.path.join(run, "cache", hashlib.sha256(common.redact_url(url).encode()).hexdigest())
            if rows is not None:
                _dump(base + ".body", rows)
                _dump(base + ".meta.json", {"url": url, "status": 200, "fetched_epoch": 1760396372})
            log.write(json.dumps({"provider": "apifootball", "status": 200, "ts": now, "url": url}) + "\n")
    return run


def match(mid="m1", apif="100", day="2026-10-14", names=("football-data",), odds=None, home="Alfa", away="Beta"):
    return {"match_id": mid, "home_team": home, "away_team": away, "normalized_datetime_utc": f"{day}T18:00:00Z", "source_match_ids": {"apifootball": apif} if apif else {},
            "source_names": list(names), "extra": {"odds": odds or {}}}


def ent(eid):
    return mc.BY_ID[eid]


class LineasDelAdaptador(unittest.TestCase):
    def test_hándicaps_y_totales_completos(self):
        keys = adapters._ODDS_PAIRS
        for t in ("-4.5", "-4", "-1", "0", "+1", "+2", "+4.5"):
            self.assertIn("resultado.handicap" + t, keys, t)
        for t in ("0_5", "1", "2", "3", "4", "5", "5_5"):
            self.assertIn("goles.over_" + t, keys, t)
        self.assertEqual(keys["resultado.handicap0"], ("ah0_1", "ah0_2"))
        self.assertEqual(keys["goles.over_2"], ("o+2", "u+2"))
        self.assertEqual((adapters.line_tag(2.5), adapters.line_tag(2), adapters.line_tag(-1, True), adapters.line_tag(0, True), adapters.line_tag(1.5, True)), ("2.5", "2", "-1", "0", "+1.5"))

    def test_todo_mercado_que_la_api_entrega_segun_el_catalogo_esta_mapeado(self):
        faltan = [e["id"] for e in mc.CATALOG if e["price_via_api"] and e["price_key"] not in adapters._ODDS_PAIRS]
        self.assertEqual(faltan, [], "entradas que la API entrega pero el adaptador no mapea")
        self.assertFalse([e["id"] for e in mc.CATALOG if not e["price_via_api"] and e["price_key"]], "price_key declarado para un mercado que la API no publica")


class Mediana(unittest.TestCase):
    def test_una_casa_atipica_no_infla_la_referencia_del_agregador(self):
        rows = [odds_row("100", b, **{"ah-1.5_1": v, "ah-1.5_2": "1.3"}) for b, v in (("A", "2.9"), ("B", "3.0"), ("C", "3.1"), ("D", "1.02"))]      # D = precio absurdo de una casa
        run = make_run([("from=2026-10-14&to=2026-10-15", rows)])
        p = ps.ApifootballOddsProvider(run)
        r = p.prices(match(), ent("resultado.ah.home.-1.5"))[0]
        self.assertAlmostEqual(r["odds"], 2.95, places=2)                   # mediana de 1.02, 2.9, 3.0, 3.1; la media sería 2.505
        self.assertIn("mediana", r["note"])


class ApifootballCache(unittest.TestCase):
    def test_promedia_por_casa_con_lineas_enteras_y_deja_evidencia_de_la_consulta(self):
        rows = [odds_row("100", "A"), odds_row("100", "B", **{"ah-1_1": "3.1"}), odds_row("100", "C", **{"ah-1_1": "3.0"})]
        run = make_run([("from=2026-10-14&to=2026-10-15", rows)])
        p = ps.ApifootballOddsProvider(run)
        m = match()
        ok, evid = p.consulted(m)
        self.assertTrue(ok)
        self.assertIn("get_odds", evid["consulta"])
        self.assertNotIn("APIkey=sec", evid["consulta"])
        self.assertEqual(evid["filas_en_la_respuesta"], 3)
        self.assertEqual(evid["consultado_utc"], "2025-10-13T23:19:32Z" if False else evid["consultado_utc"])
        rec = p.prices(m, ent("resultado.ah_entero.home.-1"))[0]
        self.assertEqual(rec["n_books"], 3)
        self.assertAlmostEqual(rec["odds"], round((2.9 + 3.1 + 3.0) / 3, 3), places=2)
        self.assertEqual(rec["source_type"], "agregador")
        self.assertFalse(ps.is_real_price(rec))
        tot = p.prices(m, ent("goles.total_entero.over.2"))[0]
        self.assertEqual(tot["n_books"], 3)

    def test_sin_id_o_fuera_de_la_ventana(self):
        run = make_run([("from=2026-10-14&to=2026-10-15", [odds_row("100", "A")])])
        p = ps.ApifootballOddsProvider(run)
        sin_id = match(apif=None)
        ok, evid = p.consulted(sin_id)
        self.assertTrue(ok)
        self.assertIn("no tiene id en apifootball", evid["detalle"])
        self.assertEqual(p.prices(sin_id, ent("resultado.1x2.home")), [])                         # consultada la ventana, el partido no figura
        self.assertFalse(p.consulted(match(day="2026-10-20"))[0])                                  # ninguna consulta cubre ese día => pendiente

    def test_consulta_por_match_id_y_respuesta_que_no_lo_contiene(self):
        run = make_run([("match_id=100", [odds_row("100", "A")])])
        p = ps.ApifootballOddsProvider(run)
        self.assertTrue(p.consulted(match(apif="100", day="2026-12-01"))[0])                        # la consulta por id cubre ese partido sin importar la fecha
        self.assertFalse(p.consulted(match(apif="999"))[0])

    def test_misma_casa_en_dos_consultas_conserva_la_fila_mas_reciente(self):
        viejo = odds_row("100", "A", odd_date="2026-10-13 10:00:00", odd_1="2.0")
        nuevo = odds_row("100", "A", odd_date="2026-10-13 20:00:00", odd_1="2.4")
        run = make_run([("from=2026-10-14&to=2026-10-15", [viejo]), ("match_id=100", [nuevo])])
        p = ps.ApifootballOddsProvider(run)
        self.assertEqual(p.prices(match(), ent("resultado.1x2.home"))[0]["odds"], 2.4)
        self.assertEqual(p.prices(match(), ent("resultado.1x2.home"))[0]["n_books"], 1)

    def test_sin_cuerpo_en_cache_no_hay_constancia(self):
        run = make_run([("from=2026-10-14&to=2026-10-15", None)])                                    # la consulta consta en el log pero no se conserva la respuesta
        p = ps.ApifootballOddsProvider(run)
        self.assertEqual(p.queries, [])
        self.assertFalse(p.consulted(match())[0])


class FootballData(unittest.TestCase):
    def test_cubre_solo_partidos_de_football_data(self):
        p = ps.FootballDataOddsProvider({})
        m = match(odds={"B365H": "2.4", "B365D": "3.6", "B365A": "2.57", "B365>2.5": "1.5", "B365<2.5": "2.63"})
        self.assertTrue(p.covers(m)[0])
        rec = p.prices(m, ent("resultado.1x2.home"))[0]
        self.assertEqual((rec["odds"], rec["bookmaker"], rec["source_type"], rec["verified"]), (2.4, "Bet365", "casa", False))
        self.assertFalse(ps.is_real_price(rec))                                                      # dato de un tercero: no se marca verificado
        self.assertEqual(p.prices(m, ent("goles.total.under.2.5"))[0]["odds"], 2.63)
        mls = match(names=("apifootball",), odds={})
        cubre, evid = p.covers(mls)
        self.assertFalse(cubre)
        self.assertIn("no figura en los fixtures", evid["detalle"])

    def test_en_la_cobertura_resuelve_fuente_no_ofrece_para_lo_que_no_cubre(self):
        p = ps.FootballDataOddsProvider({})
        rows, _ = cov.build_records([match(names=("apifootball",))], {"m1": None}, [p])
        self.assertTrue(all(c["resultado"] == "fuente_no_ofrece" for r in rows for c in r["investigacion"]["canales"][1:]))
        rows, _ = cov.build_records([match(odds={"B365H": "2.4"})], {"m1": None}, [p])
        r = {x["entry_id"]: x["investigacion"]["canales"][1] for x in rows}
        self.assertEqual(r["resultado.1x2.home"]["resultado"], "encontrado")
        self.assertEqual(r["resultado.1x2.draw"]["resultado"], "consultado_no_encontrado")          # columna ausente en el fixture
        self.assertEqual(r["corners.total.over.9.5"]["resultado"], "fuente_no_ofrece")


class CapturasDelUsuario(unittest.TestCase):
    def _files(self):
        d = tempfile.mkdtemp()
        _dump(os.path.join(d, "partidos.json"), {"fuente": "capturas de prueba", "partidos": [["Liga", "Alfa", "Beta", "14:00", [2.0, 3.4, 3.6], 2.5, [1.9, 1.95]]]})
        _dump(os.path.join(d, "ids.json"), {"Alfa|Beta": "m1"})
        return os.path.join(d, "partidos.json"), os.path.join(d, "ids.json")

    def test_precios_comunicados_son_reales_y_solo_los_de_la_captura(self):
        p = ps.UserCaptureProvider(*self._files())
        m = match()
        rec = p.prices(m, ent("resultado.1x2.away"))[0]
        self.assertEqual((rec["odds"], rec["source_type"], rec["verified"]), (3.6, "usuario", True))
        self.assertTrue(ps.is_real_price(rec))
        self.assertEqual(p.prices(m, ent("goles.total.over.2.5"))[0]["odds"], 1.9)
        self.assertEqual(p.prices(m, ent("goles.total.under.2.5"))[0]["odds"], 1.95)
        self.assertEqual(p.prices(m, ent("goles.total.over.1.5")), [])                               # otra línea: no aparece en la captura
        self.assertEqual(p.prices(m, ent("corners.total.over.9.5")), [])
        self.assertEqual(p.prices(match(mid="otro"), ent("resultado.1x2.home")), [])

    def test_en_la_cobertura_lo_ausente_es_consultado_no_encontrado_no_fuente_no_ofrece(self):
        p = ps.UserCaptureProvider(*self._files())
        rows, _ = cov.build_records([match()], {"m1": None}, [p])
        by = {r["entry_id"]: r for r in rows}
        self.assertEqual(by["resultado.1x2.home"]["precio"]["estado"], "real_verificada")
        self.assertEqual(by["resultado.1x2.home"]["precio"]["cumple_limite"], True)                  # 2.0 ≤ 2.10
        self.assertEqual(by["resultado.1x2.away"]["precio"]["cumple_limite"], False)                 # 3.6 > 2.10
        self.assertEqual(by["corners.total.over.9.5"]["investigacion"]["canales"][1]["resultado"], "consultado_no_encontrado")
        self.assertNotIn("triunfo", json.dumps(by["resultado.1x2.home"]).lower())


class PlantillaDePrecios(unittest.TestCase):
    def test_solo_mercados_pedidos_sin_precio_real_y_se_puede_rellenar_y_cargar(self):
        ev = {"history_kind": "apifootball_misma_competicion", "attempts": [{"provider": "apifootball", "resultado": "consultada: 8+8"}],
              "form": {"local": [{"gf": 1, "ga": 0, "venue": "local", "date": "2026-09-01", "ht_goals": (1, 0), "corners": (5, 4), "cards_pts": (2, 3), "sot": (3, 2), "shots": (9, 8)}] * 8,
                       "visitante": [{"gf": 0, "ga": 1, "venue": "visitante", "date": "2026-09-01", "ht_goals": (0, 1), "corners": (4, 5), "cards_pts": (3, 2), "sot": (2, 3), "shots": (8, 9)}] * 8}}
        m = match()
        rows, _ = cov.build_records([m], {"m1": ev}, [])
        d = tempfile.mkdtemp()
        path = os.path.join(d, "plantilla.csv")
        n = cov.write_price_template(rows, [m], path)
        with open(path, encoding="utf-8") as f:
            data = list(csv.DictReader(f))
        self.assertEqual(n, len(data))
        self.assertTrue({r["mercado"] for r in data} <= {"córners", "tarjetas", "goles por equipo"})
        self.assertTrue(all(r["cuota"] == "" for r in data))
        self.assertNotIn("goles", {r["mercado"] for r in data} - {"goles por equipo"})
        data[0]["cuota"], data[0]["casa"] = "1.85", "CasaX"
        with open(path, "w", encoding="utf-8", newline="") as f:
            w = csv.DictWriter(f, fieldnames=list(data[0].keys()))
            w.writeheader()
            w.writerows(data)
        rows2, _ = cov.build_records([m], {"m1": ev}, [ps.ManualCsvProvider(path)])
        self.assertEqual(sum(1 for r in rows2 if r["precio"]["estado"] == "real_verificada"), 1)
        n2 = cov.write_price_template(rows2, [m], os.path.join(d, "p2.csv"))
        self.assertEqual(n2, n - 1)                                                                   # lo ya comunicado sale de la plantilla


class IntegracionDeLaCobertura(unittest.TestCase):
    def _run_completo(self):
        rows = [odds_row("100", "A"), odds_row("100", "B")]
        run = make_run([("from=2026-10-14&to=2026-10-15", rows)])
        ev = {"history_kind": "apifootball_misma_competicion", "attempts": [{"provider": "apifootball", "resultado": "consultada: 8+8"}],
              "form": {"local": [{"gf": 2, "ga": 1, "venue": "local", "date": "2026-09-01", "ht_goals": (1, 0), "corners": (5, 4), "cards_pts": (2, 3), "sot": (3, 2), "shots": (9, 8)}] * 8,
                       "visitante": [{"gf": 1, "ga": 2, "venue": "visitante", "date": "2026-09-01", "ht_goals": (0, 1), "corners": (4, 5), "cards_pts": (3, 2), "sot": (2, 3), "shots": (8, 9)}] * 8}}
        m = dict(match(), analysis_required=True, disposition="elegible para evaluación", competition="Liga")
        _dump(os.path.join(run, "inventory.json"), {"matches": [m]})
        _dump(os.path.join(run, "matrix.json"), {"matches": {"m1": ev}})
        return run

    def test_con_los_adaptadores_la_investigacion_se_certifica_pero_nada_es_apto_para_apostar(self):
        run = self._run_completo()
        s = cov.run_coverage(run, write=False)
        self.assertEqual(s["investigacion"]["estado"], "INVESTIGACION_COMPLETA", s["investigacion"]["incidencias"])
        self.assertTrue(s["investigacion_certificada"])
        self.assertEqual(s["preparacion_para_apostar"]["filas_aptas"], 0)                            # sin modelo validado
        canales = s["investigacion"]["canales"]
        self.assertEqual(canales[0], cov.CANAL_DATOS)
        self.assertIn("apifootball (agregador)", canales)
        self.assertIn("football-data (fixtures, Bet365)", canales)
        self.assertEqual(s["investigacion"]["por_canal"]["apifootball (agregador)"]["pendiente"], 0)

    def test_sin_consulta_de_cuotas_en_cache_se_usa_el_registro_de_level1_y_sin_ninguno_queda_pendiente(self):
        run = self._run_completo()
        os.remove(os.path.join(run, "sources", "consultas.jsonl"))                                    # sin consulta registrada en caché: respaldo = `attempts` de matrix.json
        s = cov.run_coverage(run, write=False)
        self.assertEqual(s["investigacion"]["estado"], "INVESTIGACION_COMPLETA")
        with open(os.path.join(run, "matrix.json"), encoding="utf-8") as f:
            mx = json.load(f)
        mx["matches"]["m1"]["attempts"] = []                                                           # y sin constancia alguna de consulta (ni de cuotas ni de historial)
        _dump(os.path.join(run, "matrix.json"), mx)
        s, rows = cov.run_coverage(run, write=False, return_rows=True)
        self.assertEqual(s["investigacion"]["estado"], "INVESTIGACION_INCOMPLETA")
        self.assertFalse(s["investigacion_certificada"])

    def test_la_captura_aporta_precios_reales_y_el_limite_se_aplica(self):
        run = self._run_completo()
        d = tempfile.mkdtemp()
        _dump(os.path.join(d, "p.json"), {"fuente": "capturas de prueba", "partidos": [["Liga", "Alfa", "Beta", "14:00", [1.8, 3.4, 4.6], 2.5, [1.9, 1.95]]]})
        _dump(os.path.join(d, "i.json"), {"Alfa|Beta": "m1"})
        s = cov.run_coverage(run, write=False, capture=(os.path.join(d, "p.json"), os.path.join(d, "i.json")))
        self.assertEqual(s["precios"]["por_estado"]["real_verificada"], 5)
        self.assertEqual(s["precios"]["filas_con_precio_que_cumple_requisitos"], 3)                  # 1.8, 1.9 y 1.95 cumplen; 3.4 y 4.6 superan 2.10
        self.assertEqual(s["preparacion_para_apostar"]["estado"], "NINGUNA_FILA_APTA")

    def test_el_resumen_no_arrastra_filas_ni_claves(self):
        run = self._run_completo()
        s = cov.run_coverage(run, write=False)
        self.assertNotIn("_rows", s)
        self.assertNotIn("APIkey=sec", json.dumps(s))
        self.assertLess(len(json.dumps(s)), 200000)                                                  # el resumen es compacto aunque haya miles de filas


if __name__ == "__main__":
    unittest.main()
