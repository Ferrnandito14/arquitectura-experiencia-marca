"""Catálogo de mercados, capa de precios independiente y puerta de completitud (Fase 1). Datos FICTICIOS: EJEMPLO — NO REAL."""
import csv
import json
import os
import re
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

import helpers  # noqa: F401  (añade scripts/ al path)
import market_catalog as mc
import market_coverage as cov
import price_sources as ps
import tickets


def _dump(d, name, obj):
    with open(os.path.join(d, name), "w", encoding="utf-8") as f:
        json.dump(obj, f)


def _load(d, name, text=False):
    with open(os.path.join(d, name), encoding="utf-8") as f:
        return f.read() if text else json.load(f)


def row(i, venue="local", gf=2, ga=1):
    return {"gf": gf, "ga": ga, "venue": venue, "date": f"2026-09-{i + 1:02d}", "ht_goals": (1, 0), "corners": (6, 4), "yellow": (2, 1), "red": (0, 0), "cards_pts": (2, 3),
            "shots": (14, 10), "sot": (6, 4), "fouls": (10, 12), "referee": None}


def ev(n=8, kind="apifootball_misma_competicion", prices=None, attempts=None):
    return {"attempts": attempts if attempts is not None else [{"provider": "apifootball", "resultado": "consultada: 8+8 partidos previos"}], "history_kind": kind, "form": {"local": [row(i, "local") for i in range(n)], "visitante": [row(i, "visitante", 1, 2) for i in range(n)]}, "markets": {}, "api_prices": prices or {}}


def match(i):
    return {"match_id": f"m{i}", "home_team": f"Alfa{i}", "away_team": f"Beta{i}", "competition": "Liga", "normalized_datetime_utc": "2026-10-14T18:00:00Z"}


class Catalogo(unittest.TestCase):
    def test_ids_unicos_y_familias(self):
        ids = [e["id"] for e in mc.CATALOG]
        self.assertEqual(len(ids), len(set(ids)))
        self.assertTrue({e["family"] for e in mc.CATALOG} <= set(mc.FAMILIES))

    def test_contiene_las_familias_exigidas(self):
        ids = {e["id"] for e in mc.CATALOG}
        for need in ("resultado.1x2.home", "resultado.1x2.draw", "resultado.1x2.away", "resultado.dc.1x", "resultado.dc.x2", "resultado.dc.12", "resultado.dnb.home",
                     "resultado.ah.home.-1.5", "resultado.ah_entero.home.-1", "resultado.eh.home.-1", "primera_parte.1x2.home", "goles.total.over.0.5", "goles.total.under.4.5",
                     "goles.equipo.home.over.0.5", "goles.equipo.away.over.0.5", "goles.btts.yes", "corners.total.over.9.5", "corners.equipo.home.over.4.5",
                     "cards_pts.total.under.4.5", "cards_pts.equipo.away.over.1.5", "primera_parte.total.over.0.5"):
            self.assertIn(need, ids, need)

    def test_las_lineas_de_stat_markets_no_se_duplican_en_tickets(self):
        self.assertIs(tickets.STAT_MARKETS, mc.STAT_MARKETS)

    def test_el_catalogo_y_tickets_atoms_coinciden_en_etiquetas(self):
        names = ("Alfa", "Beta")
        atom_labels = {a[3] for a in tickets.atoms(ev(), names, extended=True)}
        cat_labels = {mc.entry_label(e, *names) for e in mc.CATALOG if e["stats"] in ("atoms", "extended")}
        self.assertEqual(cat_labels - atom_labels, set(), "entradas del catálogo con estadística declarada pero sin átomo")
        self.assertEqual(atom_labels - cat_labels, set(), "átomos de tickets que el catálogo no declara (catálogo incompleto)")

    def test_atoms_por_defecto_no_cambian_los_tickets(self):
        base = {a[3] for a in tickets.atoms(ev(), ("Alfa", "Beta"))}
        self.assertFalse(any(l.startswith("1.ª parte") or "goles" in l and l.startswith("Alfa:") for l in base))


class GolesPorEquipoYPrimeraParte(unittest.TestCase):
    def test_goles_por_equipo_usan_el_valor_propio_y_lo_que_concede_el_rival(self):
        legs = {a[3]: a for a in tickets.atoms(ev(), ("Alfa", "Beta"), extended=True)}
        ph, pa = legs["Alfa: más de 1.5 goles"][4], legs["Alfa: más de 1.5 goles"][5]
        self.assertTrue(ph(row(0, "local", 2, 0)))            # Alfa en casa marca 2
        self.assertFalse(ph(row(0, "local", 1, 0)))
        self.assertTrue(pa(row(0, "visitante", 0, 2)))         # Beta (fuera) concede 2 a Alfa

    def test_primera_parte_orienta_el_descanso_por_sede(self):
        legs = {a[3]: a for a in tickets.atoms(ev(), ("Alfa", "Beta"), extended=True)}
        r = row(0, "local"); r["ht_goals"] = (1, 0)           # el local ganaba al descanso
        self.assertTrue(legs["1.ª parte: local gana"][4](r))
        r2 = row(0, "visitante"); r2["ht_goals"] = (1, 0)     # el local del partido ganaba: para el equipo visitante de la fila es una derrota
        self.assertTrue(legs["1.ª parte: local gana"][5](r2))
        self.assertIsNone(legs["1.ª parte: empate"][4]({**row(0), "ht_goals": (None, None)}))


REPO = os.path.normpath(os.path.join(os.path.dirname(__file__), ".."))
PY = sys.executable


class FakeProvider(ps.PriceProvider):
    """Proveedor ficticio configurable: qué mercados dice ofrecer, si consta su consulta y qué precios devuelve."""
    def __init__(self, name="fake", offers=True, consulted=True, records=None):
        self.name, self._offers, self._consulted, self._records = name, offers, consulted, records or {}

    def supports(self, entry):
        return (True, None) if self._offers else (False, "la_fuente_no_publica_este_mercado")

    def consulted(self, match):
        return (True, {"fuente": self.name, "referencia": "fixture://consulta", "detalle": "ok"}) if self._consulted else (False, None)

    def prices(self, match, entry):
        r = self._records.get(entry["id"])
        return [ps.make_record(match["match_id"], entry["id"], r[0], self.name, r[1], verified=r[2], n_books=5)] if r else []


def _read(path):
    with open(path, encoding="utf-8") as f:
        return f.read()


def by_entry(rows, eid):
    return next(r for r in rows if r["entry_id"] == eid)


class A_Investigacion(unittest.TestCase):
    def test_las_combinaciones_requeridas_se_generan_desde_partidos_catalogo_y_canales(self):
        req = cov.required_combinations(["m1", "m2"], mc.CATALOG, [cov.CANAL_DATOS, "fake"])
        self.assertEqual(len(req), 2 * len(mc.CATALOG) * 2)

    def test_completa_aunque_no_haya_estimador_ni_precio_ni_modelo(self):
        """Investigación ≠ estimador ≠ precio: todos los mercados (incluso DNB, sin estimador) quedan resueltos con evidencia y la analítica y los precios muestran sus limitaciones."""
        fake = FakeProvider()
        rows, errs = cov.build_records([match(1)], {"m1": ev()}, [fake])
        # los mercados cuyo campo de datos no existe (fueras de juego) quedan «consultado_no_encontrado» en datos: resuelto con evidencia
        s = cov.summarize(rows, ["m1"], errs, channels=[cov.CANAL_DATOS, "fake"])
        self.assertEqual(s["investigacion"]["estado"], "INVESTIGACION_COMPLETA", s["investigacion"]["incidencias"])
        self.assertTrue(s["certificado_investigacion"])
        self.assertEqual(s["analitica"]["estado"], "CON_LIMITACIONES")
        self.assertEqual(s["precios"]["estado"], "SIN_PRECIOS_REALES")
        self.assertEqual(by_entry(rows, "resultado.ah_entero.home.-1")["analitica"]["estimador"], "no_implementado")      # sin estimador, pero investigado
        self.assertEqual(by_entry(rows, "otros.fueras_de_juego.total")["investigacion"]["canales"][0]["resultado"], "consultado_no_encontrado")
        self.assertNotIn("probabilidad", json.dumps(by_entry(rows, "resultado.ah_entero.home.-1")))       # nunca se inventa una probabilidad

    def test_una_sola_combinacion_pendiente_basta_para_declararla_incompleta_sin_umbral(self):
        rows, errs = cov.build_records([match(i) for i in range(1, 6)], {f"m{i}": ev() for i in range(1, 6)}, [FakeProvider()])
        rows[0]["investigacion"]["canales"][0]["resultado"] = "pendiente"           # 1 de >1500 combinaciones: 99.9 % resuelto
        s = cov.summarize(rows, [f"m{i}" for i in range(1, 6)], errs, channels=[cov.CANAL_DATOS, "fake"])
        self.assertEqual(s["investigacion"]["estado"], "INVESTIGACION_INCOMPLETA")
        self.assertGreater(s["investigacion"]["por_canal"][cov.CANAL_DATOS]["cobertura_informativa"], 0.99)       # el % es solo informativo
        self.assertFalse(s["certificado_investigacion"])

    def test_faltan_registros_partidos_ajenos_duplicados_y_resultados_sin_evidencia(self):
        rows, errs = cov.build_records([match(1), match(2)], {"m1": ev(), "m2": ev()}, [FakeProvider()])
        ch = [cov.CANAL_DATOS, "fake"]
        kinds = lambda rs, auth: {i["tipo"] for i in cov.investigation_gate(rs, auth, channels=ch)["incidencias"]}
        self.assertIn("combinacion_requerida_sin_registro", kinds(rows[:-1], ["m1", "m2"]))
        self.assertIn("partido_no_autorizado", kinds(rows, ["m1"]))
        self.assertIn("registro_duplicado", kinds(rows + [json.loads(json.dumps(rows[0]))], ["m1", "m2"]))
        bad = json.loads(json.dumps(rows))
        bad[0]["investigacion"]["canales"][0]["evidencia"] = None
        self.assertIn("resuelto_sin_evidencia", kinds(bad, ["m1", "m2"]))
        bad[1]["investigacion"]["canales"][0]["resultado"] = "inventado"
        self.assertIn("resultado_desconocido", kinds(bad, ["m1", "m2"]))

    def test_fuente_no_ofrece_resuelve_solo_esa_fuente(self):
        no_ofrece, ofrece_sin_consulta = FakeProvider("A", offers=False), FakeProvider("B", consulted=False)
        rows, _ = cov.build_records([match(1)], {"m1": ev()}, [no_ofrece, ofrece_sin_consulta])
        canales = {c["canal"]: c for c in by_entry(rows, "corners.total.over.9.5")["investigacion"]["canales"]}
        self.assertEqual(canales["A"]["resultado"], "fuente_no_ofrece")          # resuelto respecto de A…
        self.assertEqual(canales["B"]["resultado"], "pendiente")                  # …pero no prueba nada sobre B
        s = cov.summarize(rows, ["m1"], channels=[cov.CANAL_DATOS, "A", "B"])
        self.assertEqual(s["investigacion"]["estado"], "INVESTIGACION_INCOMPLETA")

    def test_el_adaptador_que_no_mapea_una_linea_que_la_api_entrega_es_pendiente_no_no_ofrece(self):
        sin_mapear = dict(next(e for e in mc.CATALOG if e["id"] == "resultado.ah_entero.home.-1"), id="x.sin_mapear", price_key="resultado.handicap-9", price_via_api=True)
        agg = ps.MatrixAggregatorProvider({"m1": ev()})
        rows, _ = cov.build_records([match(1)], {"m1": ev()}, [agg], catalog=[sin_mapear])
        c = rows[0]["investigacion"]["canales"][1]
        self.assertEqual(c["resultado"], "pendiente")
        self.assertIn("adaptador", c["nota"])
        rows, _ = cov.build_records([match(1)], {"m1": ev()}, [agg])
        self.assertEqual(by_entry(rows, "corners.total.over.9.5")["investigacion"]["canales"][1]["resultado"], "fuente_no_ofrece")
        self.assertEqual(by_entry(rows, "resultado.ah_entero.home.-1")["investigacion"]["canales"][1]["resultado"], "consultado_no_encontrado")      # ahora el adaptador mapea los hándicaps enteros

    def test_sin_constancia_de_consulta_de_cuotas_es_pendiente_y_con_constancia_sin_precio_es_no_encontrado(self):
        solo_fd = ev(attempts=[{"provider": "football-data", "resultado": "consultada: 9+9 partidos previos"}])      # el historial vino de otra fuente: las cuotas de apifootball NO se pidieron
        agg = ps.MatrixAggregatorProvider({"m1": solo_fd, "m2": ev()})
        rows, _ = cov.build_records([match(1), match(2)], {"m1": solo_fd, "m2": ev()}, [agg])
        g = lambda mid: next(r for r in rows if r["match_id"] == mid and r["entry_id"] == "goles.total.over.2.5")["investigacion"]["canales"][1]
        self.assertEqual(g("m1")["resultado"], "pendiente")
        self.assertEqual(g("m2")["resultado"], "consultado_no_encontrado")

    def test_proveedor_roto_deja_sus_combinaciones_pendientes_y_no_detiene_lo_demas(self):
        class Roto(FakeProvider):
            def prices(self, match, entry):
                raise RuntimeError("sin credenciales")
        rows, errs = cov.build_records([match(1)], {"m1": ev()}, [Roto("roto")])
        self.assertEqual(errs[0]["provider"], "roto")
        self.assertEqual(by_entry(rows, "goles.total.over.2.5")["investigacion"]["canales"][1]["resultado"], "pendiente")
        self.assertEqual(by_entry(rows, "goles.total.over.2.5")["investigacion"]["canales"][0]["resultado"], "encontrado")       # datos deportivos intactos

    def test_partido_sin_historial_es_pendiente_y_historial_ajeno_no_verificable(self):
        rows, _ = cov.build_records([match(1), match(2)], {"m1": None, "m2": ev(kind="proxy_otra_competicion")}, [])
        r1 = next(r for r in rows if r["match_id"] == "m1")["investigacion"]["canales"][0]
        r2 = next(r for r in rows if r["match_id"] == "m2")["investigacion"]["canales"][0]
        self.assertEqual((r1["resultado"], r2["resultado"]), ("pendiente", "no_verificable"))

    def test_que_representan_las_cifras(self):
        """entradas = catálogo general; filas = partidos × entradas; combinaciones requeridas = filas × canales; calculable = entradas con estimador × partidos."""
        rows, errs = cov.build_records([match(1), match(2)], {"m1": ev(), "m2": ev()}, [FakeProvider()])
        s = cov.summarize(rows, ["m1", "m2"], errs, channels=[cov.CANAL_DATOS, "fake"])
        self.assertEqual((s["entradas_catalogo"], s["filas"]), (len(mc.CATALOG), 2 * len(mc.CATALOG)))
        self.assertEqual(s["investigacion"]["combinaciones_requeridas"], s["filas"] * 2)
        con_estimador = sum(1 for e in mc.CATALOG if cov.model_key(e, cov._probe_model_keys()))
        self.assertEqual(s["analitica"]["estimador"]["calculable"], 2 * con_estimador)


class B_Analitica(unittest.TestCase):
    def test_datos_estimador_y_validacion_son_independientes(self):
        thin = ev()
        for r in thin["form"]["local"] + thin["form"]["visitante"]:
            r["corners"] = (None, None)
        rows, _ = cov.build_records([match(1)], {"m1": thin}, [])
        r = by_entry(rows, "corners.total.over.9.5")
        self.assertEqual(r["investigacion"]["canales"][0]["resultado"], "consultado_no_encontrado")     # investigado: el campo no existe
        self.assertEqual(r["analitica"]["datos"], "insuficientes")
        self.assertEqual(r["analitica"]["estimador"], "datos_insuficientes")                         # hay estimador de córners pero faltan los datos
        self.assertEqual(by_entry(rows, "sot.total.over.8.5")["analitica"]["estimador"], "no_implementado")
        g = by_entry(rows, "goles.total.over.2.5")
        self.assertEqual((g["analitica"]["estimador"], g["analitica"]["validacion"]), ("calculable", "insuficiente"))     # hay estimador pero el modelo NO está validado

    def test_el_modelo_solo_declara_lo_que_calcula(self):
        rows, _ = cov.build_records([match(1)], {"m1": ev()}, [])
        est = {r["entry_id"]: r["analitica"]["estimador"] for r in rows}
        self.assertEqual(est["resultado.1x2.home"], "calculable")
        self.assertEqual(est["resultado.dc.12"], "calculable")
        self.assertEqual(est["goles.equipo.home.over.0.5"], "calculable")
        self.assertEqual(est["corners.total.over.9.5"], "calculable")
        self.assertEqual(est["cards_pts.equipo.away.over.1.5"], "calculable")
        self.assertEqual(est["primera_parte.total.over.0.5"], "calculable")
        for eid in ("resultado.ah_entero.home.-1", "resultado.eh.home.-1", "sot.total.over.8.5", "shots.total.over.24.5", "otros.fueras_de_juego.total", "goles.total_entero.over.2"):
            self.assertEqual(est[eid], "no_implementado", eid)


class C_Precios(unittest.TestCase):
    def test_que_es_precio_real(self):
        mk = lambda t, v: ps.make_record("m", "e", 1.8, "s", t, verified=v)
        self.assertTrue(ps.is_real_price(mk("casa", True)))
        self.assertTrue(ps.is_real_price(mk("usuario", True)))
        self.assertFalse(ps.is_real_price(mk("casa", False)))
        self.assertFalse(ps.is_real_price(mk("agregador", True)))
        self.assertFalse(ps.is_real_price(mk("estimacion_modelo", True)))
        with self.assertRaises(ValueError):
            ps.make_record("m", "e", 1.0, "s", "casa")

    def test_limite_individual_y_aptitud(self):
        prov = FakeProvider(records={"goles.total.over.2.5": (1.95, "casa", True), "goles.total.over.3.5": (2.60, "casa", True), "goles.total.over.1.5": (1.30, "agregador", True)})
        rows, _ = cov.build_records([match(1)], {"m1": ev()}, [prov])
        ok, alto, agg = (by_entry(rows, f"goles.total.over.{x}")["precio"] for x in ("2.5", "3.5", "1.5"))
        self.assertEqual((ok["estado"], ok["cumple_limite"], ok["cumple_requisitos_de_precio"]), ("real_verificada", True, True))
        self.assertEqual((alto["estado"], alto["cumple_limite"], alto["cumple_requisitos_de_precio"]), ("real_verificada", False, False))          # 2.60 > 2.10
        self.assertFalse(agg["cumple_requisitos_de_precio"])                                                                                         # un agregador nunca cumple
        rep = cov.pricing_report(rows)
        self.assertEqual(rep["filas_con_precio_que_cumple_requisitos"], 1)
        self.assertTrue(any(i["tipo"].startswith("precio_real_sobre") for i in rep["incidencias"]))

    def test_precio_ausente_no_es_investigacion_incompleta(self):
        rows, errs = cov.build_records([match(1)], {"m1": ev()}, [FakeProvider()])        # el proveedor consultó y no tiene precios
        s = cov.summarize(rows, ["m1"], errs, channels=[cov.CANAL_DATOS, "fake"])
        self.assertEqual(s["precios"]["estado"], "SIN_PRECIOS_REALES")
        self.assertEqual(s["investigacion"]["estado"], "INVESTIGACION_COMPLETA")

    def test_precio_comunicado_por_el_usuario_es_real(self):
        d = tempfile.mkdtemp()
        p = os.path.join(d, "precios.csv")
        with open(p, "w", encoding="utf-8", newline="") as f:
            w = csv.writer(f)
            w.writerow(["home", "away", "seleccion", "cuota", "casa"])
            w.writerow(["Alfa1", "Beta1", "Más de 9.5 córners", "1.85", "CasaX"])
        rows, _ = cov.build_records([match(1)], {"m1": ev()}, [ps.ManualCsvProvider(p)])
        r = by_entry(rows, "corners.total.over.9.5")
        self.assertEqual(r["precio"]["estado"], "real_verificada")
        self.assertEqual(r["precio"]["registro"]["bookmaker"], "CasaX")
        self.assertEqual(r["investigacion"]["canales"][1]["resultado"], "encontrado")
        self.assertEqual(by_entry(rows, "corners.total.under.9.5")["investigacion"]["canales"][1]["resultado"], "consultado_no_encontrado")


class IndependenciaDeCasas(unittest.TestCase):
    def test_ningun_script_depende_de_una_casa_concreta(self):
        d = os.path.join(REPO, ".claude", "skills", "seleccion-final-picks", "scripts")
        for f in os.listdir(d):
            if f.endswith(".py"):
                txt = _read(os.path.join(d, f)).lower()
                self.assertNotIn("triunfobet", txt, f)
                self.assertNotIn("triunfo", txt, f)

    def test_catalogo_e_investigacion_deportiva_funcionan_sin_credenciales_ni_precios(self):
        with mock.patch.dict(os.environ, {}, clear=True):
            rows, errs = cov.build_records([match(1)], {"m1": ev()}, [])
            s = cov.summarize(rows, ["m1"], errs, channels=[cov.CANAL_DATOS])
        self.assertEqual(len(rows), len(mc.CATALOG))                              # los mercados siguen todos en el catálogo
        self.assertEqual(s["investigacion"]["estado"], "INVESTIGACION_COMPLETA")  # la investigación deportiva no necesita precios
        self.assertEqual(s["precios"]["por_estado"]["no_consultado"], len(mc.CATALOG))
        self.assertEqual(s["analitica"]["estimador"]["calculable"] > 0, True)       # el modelo calcula lo que puede sin cuotas


class SkipCoverage(unittest.TestCase):
    def _run(self, *flags):
        d = tempfile.mkdtemp()
        _dump(d, "inventory.json", {"matches": [dict(match(1), analysis_required=True, disposition="elegible para evaluación")]})
        _dump(d, "matrix.json", {"matches": {"m1": ev()}})
        with mock.patch("sys.stdout"):
            tickets.main(["--run", d, "--target", "s:1.2:1.3:2:0.3", *flags])
        return d

    def test_skip_queda_registrado_y_nunca_certifica(self):
        d = self._run("--skip-coverage")
        out = _load(d, "tickets.json")
        self.assertEqual(out["cobertura_mercados"]["modo"], "omitida")
        self.assertFalse(out["certificado"])
        self.assertFalse(out["cobertura_mercados"]["certificado_investigacion"])
        md = _load(d, "tickets.md", text=True)
        self.assertIn("NO VALIDADO", md)
        self.assertIn("OMITIDA", md)
        self.assertFalse(os.path.exists(os.path.join(d, "market_coverage.json")))           # no se ejecutó ni se escribió ningún control

    def test_certified_exige_modo_enforce_e_investigacion_completa(self):
        rows, errs = cov.build_records([match(1)], {"m1": ev()}, [FakeProvider()])
        s = cov.summarize(rows, ["m1"], errs, channels=[cov.CANAL_DATOS, "fake"])
        self.assertTrue(cov.certified(s))
        self.assertEqual(s["investigacion_certificada"], s["certificado_investigacion"])        # alias antiguo con el mismo valor
        self.assertFalse(cov.certified(dict(s, modo="omitida")))                  # ni siquiera con la investigación completa
        self.assertFalse(cov.certified(dict(s, modo="error")))
        self.assertFalse(cov.certified(cov.omitted_summary()))
        inc = dict(s, investigacion=dict(s["investigacion"], estado="INVESTIGACION_INCOMPLETA"))
        self.assertFalse(cov.certified(inc))


class RutasProtegidas(unittest.TestCase):
    """Los controles se EJECUTAN en las rutas reales y su resultado se respeta antes de producir la salida."""
    def test_pipeline_principal_ejecuta_los_controles_y_rotula_cada_ranking(self):
        d = tempfile.mkdtemp()
        _dump(d, "inventory.json", {"matches": [dict(match(1), analysis_required=True, disposition="elegible para evaluación")]})
        _dump(d, "matrix.json", {"matches": {"m1": ev(attempts=[])}})              # historial sin constancia de consulta externa => investigación pendiente
        with mock.patch("sys.stdout"):
            tickets.main(["--run", d, "--target", "s:1.2:1.3:2:0.3"])
        out = _load(d, "tickets.json")
        self.assertEqual(out["cobertura_mercados"]["modo"], "enforce")
        self.assertFalse(out["certificado"])
        self.assertEqual(out["cobertura_mercados"]["investigacion"]["estado"], "INVESTIGACION_INCOMPLETA")     # el agregador aún no mapea los hándicaps enteros
        self.assertTrue(os.path.exists(os.path.join(d, "market_coverage.json")))                               # la puerta se ejecutó y dejó evidencia
        md = _load(d, "tickets.md", text=True)
        self.assertIn("INVESTIGACIÓN NO CERTIFICADA COMO EXHAUSTIVA", md)
        for h in re.findall(r"^## (?:Perfil|Top de picks).*$", md, flags=re.M):
            i = md.index(h)
            self.assertIn("NO CERTIFICADA COMO EXHAUSTIVA", md[i:i + len(h) + 400], h)                                          # advertencia junto a cada ranking

    def _ligas_dir(self, d):
        os.makedirs(os.path.join(d, "ligas"))
        m = dict(match(1), analysis_required=True, disposition="elegible para evaluación", source_match_ids={"apifootball": "1"}, competition="Liga")
        _dump(d, "inventory.json", {"matches": [m]})
        _dump(d, "matrix.json", {"matches": {"m1": dict(ev(attempts=[]), **{"form": {"local": [dict(row(i, "local"), misma_competicion=True) for i in range(8)], "visitante": [dict(row(i, "visitante", 1, 2), misma_competicion=True) for i in range(8)]}})}})
        _dump(d, "rotation.json", {})
        _dump(os.path.join(d, "ligas"), "partidos_usuario.json", {"partidos": [["Liga", "Alfa1", "Beta1", "14:00", [2.0, 3.4, 3.6], 2.5, [1.9, 1.9]]]})
        _dump(os.path.join(d, "ligas"), "ids.json", {"Alfa1|Beta1": "m1"})

    def _exec(self, script, *args):
        return subprocess.run([PY, os.path.join(REPO, "runs", "2026-10-14", "ligas", script), *args], cwd=REPO, capture_output=True, text=True, timeout=120)

    def test_flujo_paralelo_ejecuta_los_controles_y_el_libro_sale_provisional(self):
        d = tempfile.mkdtemp()
        self._ligas_dir(d)
        r = self._exec("build_dataset.py", "--run", d)
        self.assertEqual(r.returncode, 0, r.stderr)
        meta = _load(os.path.join(d, "ligas"), "dataset_meta.json")
        self.assertFalse(meta["certificado_investigacion"])
        self.assertTrue(os.path.exists(os.path.join(d, "ligas", "market_coverage.json")))                       # el control se ejecutó dentro de build_dataset
        out = os.path.join(d, "out")
        r = self._exec("build_xlsx.py", "--ligas-dir", os.path.join(d, "ligas"), "--out-dir", out)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(os.listdir(out), ["ligas-14-oct-PROVISIONAL.xlsx"])                                    # NUNCA el nombre definitivo
        from openpyxl import load_workbook
        wb = load_workbook(os.path.join(out, "ligas-14-oct-PROVISIONAL.xlsx"))
        self.assertTrue(any("NO CERTIFICADO COMO EXHAUSTIVO" in str(c.value) for row in wb["Léeme"].iter_rows() for c in row))
        self.assertIn("Cobertura (3 controles)", wb.sheetnames)

    def test_libro_sin_controles_ejecutados_o_con_resultado_obsoleto_no_es_definitivo(self):
        d = tempfile.mkdtemp()
        self._ligas_dir(d)
        self.assertEqual(self._exec("build_dataset.py", "--run", d).returncode, 0)
        lg = os.path.join(d, "ligas")
        _dump(lg, "dataset_meta.json", dict(_load(lg, "dataset_meta.json"), partidos_ids=["m-otro"]))              # cobertura de OTRO conjunto de partidos
        out = os.path.join(d, "out2")
        self.assertEqual(self._exec("build_xlsx.py", "--ligas-dir", lg, "--out-dir", out).returncode, 0)
        self.assertEqual(os.listdir(out), ["ligas-14-oct-PROVISIONAL.xlsx"])
        os.remove(os.path.join(lg, "market_coverage.json"))                                                       # sin constancia de ejecución
        out3 = os.path.join(d, "out3")
        self.assertEqual(self._exec("build_xlsx.py", "--ligas-dir", lg, "--out-dir", out3).returncode, 0)
        self.assertEqual(os.listdir(out3), ["ligas-14-oct-PROVISIONAL.xlsx"])

    def test_el_libro_definitivo_solo_se_escribe_si_los_controles_certifican_y_coinciden(self):
        d = tempfile.mkdtemp()
        self._ligas_dir(d)
        self.assertEqual(self._exec("build_dataset.py", "--run", d).returncode, 0)
        lg = os.path.join(d, "ligas")
        rows, errs = cov.build_records([match(1)], {"m1": ev()}, [FakeProvider()])
        good = cov.summarize(rows, ["m1"], errs, channels=[cov.CANAL_DATOS, "fake"])               # investigación completa sintética
        self.assertTrue(good["certificado_investigacion"])
        _dump(lg, "market_coverage.json", good)
        _dump(lg, "dataset_meta.json", {"partidos_ids": ["m1"], "certificado_investigacion": True})
        out0 = os.path.join(d, "out0")                                                              # contenido parcial (solo patas de la captura): nunca definitivo
        self.assertEqual(self._exec("build_xlsx.py", "--ligas-dir", lg, "--out-dir", out0).returncode, 0)
        self.assertEqual(os.listdir(out0), ["ligas-14-oct-PROVISIONAL.xlsx"])
        out = os.path.join(d, "out4")
        self.assertEqual(self._exec("build_xlsx.py", "--ligas-dir", lg, "--out-dir", out, "--content-scope", "catalog").returncode, 0)
        self.assertEqual(os.listdir(out), ["ligas-14-oct.xlsx"])
        _dump(lg, "market_coverage.json", dict(good, modo="omitida"))                               # el mismo resultado pero omitido: no basta
        out5 = os.path.join(d, "out5")
        self.assertEqual(self._exec("build_xlsx.py", "--ligas-dir", lg, "--out-dir", out5, "--content-scope", "catalog").returncode, 0)
        self.assertEqual(os.listdir(out5), ["ligas-14-oct-PROVISIONAL.xlsx"])

    def test_otros_puntos_de_entrada_no_generan_rankings_ni_combinadas_definitivas(self):
        """Inspección: solo tickets.py (rankings/tickets), custom_check.py (valida el ticket de la persona usuaria) y los scripts de ligas producen candidatos; el resto no."""
        d = os.path.join(REPO, ".claude", "skills", "seleccion-final-picks", "scripts")
        generan = {f for f in os.listdir(d) if f.endswith(".py") and re.search(r"def (top_picks|search|_ranking_general)\b", _read(os.path.join(d, f)))}
        self.assertEqual(generan, {"tickets.py"})
        for f in ("tickets.py",):
            self.assertIn("market_coverage.run_coverage", _read(os.path.join(d, f)))
        self.assertIn("MC.run_coverage", _read(os.path.join(REPO, "runs", "2026-10-14", "ligas", "build_dataset.py")))
        self.assertIn("_certification()", _read(os.path.join(REPO, "runs", "2026-10-14", "ligas", "build_xlsx.py")))


class CertificacionNoEsAprobacion(unittest.TestCase):
    """`investigacion_certificada` = exhaustividad de la investigación; la preparación para apostar es un estado independiente."""
    def _complete(self, prov):
        rows, errs = cov.build_records([match(1)], {"m1": ev()}, [prov])
        return rows, cov.summarize(rows, ["m1"], errs, channels=[cov.CANAL_DATOS, "fake"])

    def test_investigacion_certificada_sin_que_nada_este_apto_para_apostar(self):
        rows, s = self._complete(FakeProvider())                       # investigación completa, sin ningún precio real
        self.assertTrue(s["investigacion_certificada"])
        self.assertEqual(s["certificado_investigacion"], True)         # alias de compatibilidad
        self.assertEqual(s["preparacion_para_apostar"]["estado"], "NINGUNA_FILA_APTA")
        self.assertEqual(s["preparacion_para_apostar"]["filas_aptas"], 0)
        self.assertIn("NO es una aprobación", cov.SEMANTICS["investigacion_certificada"].replace("NO aprueba apostar", "NO es una aprobación"))
        self.assertIn("no es una aprobación para apostar", s["aviso"])
        self.assertIn("preparación para apostar: NO APTA", s["aviso"])

    def test_con_precio_real_dentro_del_limite_y_datos_suficientes_el_modelo_no_validado_impide_apto(self):
        prov = FakeProvider(records={"goles.total.over.1.5": (1.55, "casa", True)})
        rows, errs = cov.build_records([match(1)], {"m1": ev()}, [prov], revision_ok=True)            # revisión de agentes completa (requisito aparte)
        s = cov.summarize(rows, ["m1"], errs, channels=[cov.CANAL_DATOS, "fake"])
        r = by_entry(rows, "goles.total.over.1.5")
        req = r["preparacion_para_apostar"]["requisitos"]
        self.assertTrue(all(req[k] for k in req if k != "modelo_validado"), req)       # todo lo demás se cumple…
        self.assertFalse(req["modelo_validado"])                                         # …pero el modelo no está validado
        self.assertEqual(r["preparacion_para_apostar"]["estado"], "NO_APTA")
        self.assertEqual(r["preparacion_para_apostar"]["incumplidos"], ["modelo_validado"])
        self.assertTrue(s["investigacion_certificada"])                                  # investigación certificada ≠ apta

    def test_solo_es_apta_si_se_cumplen_todos_los_requisitos_incluida_la_validacion(self):
        prov = FakeProvider(records={"goles.total.over.1.5": (1.55, "casa", True), "goles.total.over.2.5": (2.60, "casa", True), "goles.total.over.3.5": (1.60, "agregador", True)})
        with mock.patch.dict(cov.MODEL_VALIDATION, {"nivel": "suficiente"}):                # hipótesis: modelo validado en el futuro
            rows, _ = cov.build_records([match(1)], {"m1": ev()}, [prov], revision_ok=True)
            apta, alto, agg = (by_entry(rows, f"goles.total.over.{x}")["preparacion_para_apostar"] for x in ("1.5", "2.5", "3.5"))
            sin_revision, _ = cov.build_records([match(1)], {"m1": ev()}, [prov])
        self.assertEqual(apta["estado"], "APTA")
        self.assertEqual(by_entry(sin_revision, "goles.total.over.1.5")["preparacion_para_apostar"]["incumplidos"], ["revision_agentes_completa"])       # sin revisión de agentes completa, nunca
        self.assertEqual(alto["incumplidos"], ["cuota_dentro_del_limite"])                 # 2.60 > 2.10
        self.assertIn("precio_real_verificado", agg["incumplidos"])                          # un agregador no es precio real

    def test_investigacion_completa_no_basta_ni_siquiera_con_precio_si_los_datos_son_insuficientes(self):
        thin = ev(n=3)
        prov = FakeProvider(records={"goles.total.over.1.5": (1.55, "casa", True)})
        rows, _ = cov.build_records([match(1)], {"m1": thin}, [prov])
        self.assertIn("datos_suficientes", by_entry(rows, "goles.total.over.1.5")["preparacion_para_apostar"]["incumplidos"])

    def _ticket(self, tipo="manual_usuario", cuota=1.5, n=(8, 8)):
        return {"items": [{"patas": [{"cuota_tipo": tipo, "cuota_media": cuota, "n": list(n), "p_central": 0.7, "apoyo_conservador": 0.7}]}]}

    def test_borrador_con_precio_real_cuota_ok_y_datos_suficientes_sigue_no_apto_con_el_modelo_sin_validar(self):
        r = cov.ticket_readiness(self._ticket(), investigacion_certificada=True, revision_ok=True)
        self.assertEqual(r["incumplidos"], ["modelo_validado"])
        self.assertEqual(r["estado"], "NO_APTA")
        with mock.patch.dict(cov.MODEL_VALIDATION, {"nivel": "suficiente"}):
            self.assertEqual(cov.ticket_readiness(self._ticket(), True, True)["estado"], "APTA")
            self.assertIn("precio_real_verificado", cov.ticket_readiness(self._ticket("promedio_de_mercado"), True, True)["incumplidos"])
            self.assertIn("cuota_dentro_del_limite", cov.ticket_readiness(self._ticket(cuota=2.5), True, True)["incumplidos"])
            self.assertIn("investigacion_resuelta", cov.ticket_readiness(self._ticket(), False, True)["incumplidos"])         # la certificación es necesaria pero no suficiente
            self.assertEqual(cov.ticket_readiness(self._ticket(), True, False)["incumplidos"], ["revision_agentes_completa"])

    def test_tickets_json_expone_el_campo_inequivoco_el_alias_y_la_preparacion_por_borrador(self):
        import test_tickets as TT
        d = tempfile.mkdtemp()
        pr = lambda: {"goles.over_5_5": TT.avg([4.0, 1.12]), "resultado.doble_oportunidad": TT.avg([1.15, 1.22, 3.0]), "goles.over_2_5": TT.avg([1.5, 2.4])}
        _dump(d, "inventory.json", {"matches": [dict(TT.mm(i), analysis_required=True, disposition="elegible para evaluación") for i in range(10)]})
        _dump(d, "matrix.json", {"matches": {f"m{i}": dict(TT.ev(prices=pr()), attempts=[{"provider": "apifootball", "resultado": "consultada: 8+8"}]) for i in range(10)}})
        old, tickets.MAX_GAP = tickets.MAX_GAP, 1.0
        try:
            with mock.patch("sys.stdout"):
                tickets.main(["--run", d, "--target", "seg:1.20:1.28:2:0.5"])
        finally:
            tickets.MAX_GAP = old
        out = _load(d, "tickets.json")
        tks = [tk for t in out["targets"] for tk in t["tickets"]]
        self.assertTrue(tks)
        self.assertIn("investigacion_certificada", out)
        self.assertEqual(out["certificado"], out["investigacion_certificada"])               # alias antiguo
        self.assertIn("NO es una aprobación", out["certificado_significa"])
        self.assertTrue(all("preparacion_para_apostar" in tk and tk["preparacion_para_apostar"]["estado"] == "NO_APTA" for tk in tks))
        self.assertEqual(out["preparacion_para_apostar"]["aptos"], 0)
        md = _load(d, "tickets.md", text=True)
        self.assertIn("Preparación para apostar (estado independiente de la certificación)", md)
        with open(os.path.join(d, "candidatos_estadisticos.csv"), encoding="utf-8") as f:
            hdr = f.readline().strip().split(",")
        self.assertEqual(hdr[-2:], ["investigacion_certificada", "preparacion_para_apostar"])

    def test_certificacion_con_investigacion_completa_en_tickets_no_cambia_la_preparacion(self):
        """Un resumen con investigación completa certifica el campo pero los borradores siguen NO_APTA."""
        rows, s = self._complete(FakeProvider())
        self.assertTrue(s["investigacion_certificada"])
        self.assertEqual(cov.ticket_readiness(self._ticket(), s["investigacion_certificada"])["estado"], "NO_APTA")


class DatosDeportivosSignificado(unittest.TestCase):
    """«datos_deportivos» = consulta externa REGISTRADA + campo presente en el historial local; no es suficiencia ni consulta del mercado concreto."""
    def _canal(self, e, eid="goles.total.over.2.5"):
        rows, _ = cov.build_records([match(1)], {"m1": e}, [])
        return by_entry(rows, eid)["investigacion"]["canales"][0]

    def test_con_consulta_externa_registrada_y_campo_es_encontrado_con_evidencia_de_ambas(self):
        c = self._canal(ev())
        self.assertEqual(c["resultado"], "encontrado")
        self.assertEqual(c["evidencia"]["tipo_verificacion"], "consulta_externa_registrada + campo_en_historial_local")
        self.assertEqual(c["evidencia"]["consulta_externa"]["proveedor"], "apifootball")
        self.assertEqual(c["evidencia"]["filas_con_el_campo"], [8, 8])

    def test_filas_en_un_archivo_local_sin_constancia_de_consulta_no_cuentan_como_investigacion(self):
        c = self._canal(ev(attempts=[]))                                      # hay filas y campo, pero no consta de dónde salieron
        self.assertEqual(c["resultado"], "pendiente")
        self.assertIn("solo archivo local", c["nota"])
        otro = self._canal(ev(attempts=[{"provider": "football-data", "resultado": "consultada: 9+9"}]))     # consulta de OTRA fuente que la del historial
        self.assertEqual(otro["resultado"], "pendiente")

    def test_consulta_registrada_pero_campo_ausente_es_consultado_no_encontrado(self):
        c = self._canal(ev(), "otros.fueras_de_juego.total")
        self.assertEqual(c["resultado"], "consultado_no_encontrado")
        self.assertEqual(c["evidencia"]["filas_con_el_campo"], [0, 0])

    def test_encontrado_no_implica_datos_suficientes(self):
        rows, _ = cov.build_records([match(1)], {"m1": ev(n=2)}, [])
        r = by_entry(rows, "goles.total.over.2.5")
        self.assertEqual(r["investigacion"]["canales"][0]["resultado"], "encontrado")      # el campo existe…
        self.assertEqual(r["analitica"]["datos"], "insuficientes")                          # …pero no bastan para analizar el mercado

    def test_indicadores_por_canal_distinguen_consulta_externa_campo_local_y_pendientes(self):
        rows, errs = cov.build_records([match(1), match(2)], {"m1": ev(), "m2": ev(attempts=[])}, [])
        pc = cov.investigation_gate(rows, ["m1", "m2"], channels=[cov.CANAL_DATOS])["por_canal"][cov.CANAL_DATOS]
        n = len(mc.CATALOG)
        self.assertEqual(pc["con_consulta_externa_registrada"], n)             # solo m1 tiene constancia de consulta externa
        self.assertEqual(pc["sin_constancia_de_consulta_externa"], n)
        self.assertEqual(pc["campo_presente_en_historial_local"] + pc["campo_ausente_en_historial_local"], n)
        self.assertIn("NO significa estadística suficiente", pc["semantica"])


class RutasDeGeneracion(unittest.TestCase):
    """Inventario de rutas que generan rankings, candidatos, combinadas o libros: cada una ejecuta la cobertura o declara que no la evalúa; una ruta nueva sin registrar rompe la prueba."""
    PAT = re.compile(r"\.xlsx|\.pptx|tickets\.md|candidatos_|top_picks|_ranking|ranking|combinad|user_tickets_eval|PROVISIONAL", re.I)

    def _scripts(self):
        import glob
        files = glob.glob(os.path.join(REPO, ".claude", "skills", "seleccion-final-picks", "scripts", "*.py")) + glob.glob(os.path.join(REPO, "runs", "*", "ligas", "*.py")) + glob.glob(os.path.join(REPO, "data", "*.py"))
        return {os.path.relpath(f, REPO): _read(f) for f in files}

    def test_toda_ruta_que_menciona_rankings_o_libros_esta_registrada(self):
        sin_registrar = [f for f, t in self._scripts().items() if self.PAT.search(t) and f not in cov.GENERATION_ROUTES and f not in cov.NON_GENERATING]
        self.assertEqual(sin_registrar, [], "ruta nueva que menciona rankings/combinadas/libros sin registrar en market_coverage.GENERATION_ROUTES / NON_GENERATING")

    def test_cada_ruta_registrada_contiene_realmente_su_control(self):
        scripts = self._scripts()
        for f, info in cov.GENERATION_ROUTES.items():
            self.assertIn(f, scripts, f)
            self.assertIn(info["marker"], scripts[f], f"{f}: falta el control «{info['marker']}»")
        for f in cov.NON_GENERATING:
            self.assertIn(f, scripts, f)

    def test_build_dataset_se_registra_aunque_no_mencione_rankings(self):
        self.assertIn("runs/2026-10-14/ligas/build_dataset.py", cov.GENERATION_ROUTES)

    def test_las_salidas_que_los_scripts_escriben_pasan_por_rutas_registradas(self):
        """Todo script que escribe un .md/.json/.csv/.xlsx de resultados (no de datos de entrada) está en el registro o en la lista de no generadores / no resultado."""
        escritores = {f for f, t in self._scripts().items() if re.search(r"tickets\.json|tickets\.md|candidatos_estadisticos|manual_odds_plantilla|\.save\(|user_tickets_eval", t)}
        no_resultado = set()      # sin excepciones: los que escriben resultados deben estar en el registro
        self.assertEqual({f for f in escritores if f not in cov.GENERATION_ROUTES and f not in cov.NON_GENERATING and f not in no_resultado}, set())

    def test_custom_check_declara_que_no_evalua_cobertura_ni_preparacion(self):
        d = tempfile.mkdtemp()
        inv = {"matches": [dict(match(1), analysis_required=True, disposition="elegible para evaluación")]}
        _dump(d, "inventory.json", inv)
        mxm = ev(prices={"goles.over_2_5": {"cuotas_medias": [1.9, 1.95], "n_casas": 5, "minmax": [[1.8, 2.0], [1.9, 2.0]], "casas": ["a"]}})
        _dump(d, "matrix.json", {"matches": {"m1": mxm}})
        spec = os.path.join(d, "spec.json")
        _dump(d, "spec.json", [{"nombre": "mío", "patas": [{"partido": "Alfa1 – Beta1", "tipo": "total_goles", "operador": "over", "linea": 1.5}]}])
        r = subprocess.run([PY, os.path.join(REPO, ".claude", "skills", "seleccion-final-picks", "scripts", "custom_check.py"), "--run", d, "--spec", spec], capture_output=True, text=True, cwd=REPO, timeout=120)
        self.assertEqual(r.returncode, 0, r.stderr)
        res = _load(d, "user_tickets_eval.json")
        self.assertTrue(all(x["investigacion_certificada"] is False and x["preparacion_para_apostar"] == "NO_EVALUADA" for x in res))
        self.assertIn("NO CERTIFICADO COMO EXHAUSTIVO", _load(d, "user_tickets_eval.md", text=True))

    def test_el_veredicto_de_nivel_1_ya_no_dice_ranking_definitivo_permitido(self):
        txt = _read(os.path.join(REPO, ".claude", "skills", "seleccion-final-picks", "scripts", "coverage_report.py"))
        self.assertNotIn("ranking definitivo permitido, sujeto", txt)
        self.assertIn("NO certifica la investigación de mercados", txt)

    def test_ninguna_ruta_certifica_con_cobertura_omitida_incompleta_o_ausente(self):
        """Sintetiza los tres escenarios en tickets.py (omitida / incompleta / error al calcular) y exige investigacion_certificada = False en JSON, snapshots y encabezado."""
        for flags in (["--skip-coverage"], []):
            d = tempfile.mkdtemp()
            _dump(d, "inventory.json", {"matches": [dict(match(1), analysis_required=True, disposition="elegible para evaluación")]})
            _dump(d, "matrix.json", {"matches": {"m1": ev(attempts=[])}})
            with mock.patch("sys.stdout"):
                tickets.main(["--run", d, "--target", "s:1.2:1.3:2:0.3", *flags])
            out = _load(d, "tickets.json")
            self.assertIs(out["investigacion_certificada"], False, flags)
            self.assertIs(out["certificado"], False, flags)
        d = tempfile.mkdtemp()
        _dump(d, "inventory.json", {"matches": [dict(match(1), analysis_required=True, disposition="elegible para evaluación")]})
        _dump(d, "matrix.json", {"matches": {"m1": ev()}})
        with mock.patch("market_coverage.run_coverage", side_effect=RuntimeError("falla")), mock.patch("sys.stdout"):
            tickets.main(["--run", d, "--target", "s:1.2:1.3:2:0.3"])
        out = _load(d, "tickets.json")
        self.assertIs(out["investigacion_certificada"], False)
        self.assertEqual(out["cobertura_mercados"]["modo"], "error")
        self.assertIn("NO VALIDADO", _load(d, "tickets.md", text=True))


if __name__ == "__main__":
    unittest.main()
