"""Fase 3: muestras de liga, árbitro y alineaciones como contexto de la analítica (datos y limitaciones, nunca puertas). Datos FICTICIOS: EJEMPLO — NO REAL."""
import json
import os
import tempfile
import unittest
from unittest import mock

import helpers  # noqa: F401  (añade scripts/ al path)
import lineups_snapshot as ls
import market_coverage as cov


def _dump(path, obj):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f)


def _load(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def match(mid="m1", apif="100", league="7", comp="Liga", referee=None, kick="2026-10-14T18:00:00Z"):
    return {"match_id": mid, "home_team": f"Alfa{mid}", "away_team": f"Beta{mid}", "competition": comp, "normalized_datetime_utc": kick, "analysis_required": True,
            "disposition": "elegible para evaluación", "source_names": ["apifootball"], "source_match_ids": {"apifootball": apif} if apif else {},
            "extra": {"api": ({"league_id": league, "referee": referee} if league else None), "referee": None, "odds": None}}


def fila(i, tarjetas=(2, 3), corners=(5, 4), arbitro="Árbitro X"):
    return {"id": str(i), "fecha": "2026-09-01", "local": "A", "visitante": "B", "gl": 1, "gv": 1, "tarjetas": list(tarjetas) if tarjetas else None, "corners": list(corners) if corners else None, "arbitro": arbitro}


def ev():
    r = lambda v, gf, ga: {"gf": gf, "ga": ga, "venue": v, "date": "2026-09-01", "ht_goals": [1, 0], "corners": [5, 4], "cards_pts": [2, 3], "sot": [3, 2], "shots": [9, 8]}
    return {"history_kind": "apifootball_misma_competicion", "attempts": [{"provider": "apifootball", "resultado": "consultada: 8+8"}],
            "form": {"local": [r("local", 2, 1)] * 8, "visitante": [r("visitante", 1, 2)] * 8}}


def run_con_muestras(samples=None, snapshots=None, matches=None):
    run = tempfile.mkdtemp()
    ms = matches or [match()]
    _dump(os.path.join(run, "inventory.json"), {"matches": ms})
    _dump(os.path.join(run, "matrix.json"), {"matches": {m["match_id"]: ev() for m in ms}})
    for lid, filas in (samples or {}).items():
        _dump(os.path.join(run, "league_samples", f"{lid}.json"), {"league_id": lid, "filas": filas, "resumen": {}})
    for name, snap in (snapshots or {}).items():
        _dump(os.path.join(run, "lineups", name), snap)
    return run


class Contexto(unittest.TestCase):
    def test_muestra_de_liga_cuenta_partidos_con_cada_dato(self):
        filas = [fila(i) for i in range(10)] + [fila(10, tarjetas=None), fila(11, corners=None, arbitro=None)]
        run = run_con_muestras({"7": filas})
        c = cov.build_contexts(run, [match()], [match()])["m1"]
        self.assertEqual(c["muestra_liga"], {"ejecutada": True, "partidos": 12, "con_tarjetas": 11, "con_corners": 11, "con_arbitro": 11})
        self.assertEqual(c["liga_id"], "7")

    def test_sin_muestra_ejecutada_no_se_inventa_nada(self):
        run = run_con_muestras()
        c = cov.build_contexts(run, [match()], [match()])["m1"]
        self.assertEqual(c["muestra_liga"], {"ejecutada": False, "partidos": 0, "con_tarjetas": 0, "con_corners": 0, "con_arbitro": 0})
        self.assertIsNone(c["arbitro"]["partidos_en_muestra_liga"])

    def test_liga_inferida_de_otros_partidos_con_la_misma_competicion(self):
        sin_api = match("m2", apif=None, league=None, comp="Championship")
        con_api = match("m3", league="153", comp="championship")
        self.assertEqual(cov.league_of(sin_api, [sin_api, con_api]), "153")
        self.assertIsNone(cov.league_of(sin_api, [sin_api]))

    def test_arbitro_designado_y_sus_partidos_en_la_muestra(self):
        filas = [fila(i, arbitro="R. Pérez") for i in range(4)] + [fila(9, arbitro="Otro")]
        run = run_con_muestras({"7": filas})
        m = match(referee="R. Pérez")
        c = cov.build_contexts(run, [m], [m])["m1"]
        self.assertEqual(c["arbitro"], {"designado": "R. Pérez", "partidos_en_muestra_liga": 4})
        self.assertEqual(cov.build_contexts(run, [match()], [match()])["m1"]["arbitro"]["designado"], None)

    def test_alineaciones_toma_la_ultima_instantanea_sin_sobrescribir_las_anteriores(self):
        viejo = {"partidos": [{"match_id": "m1", "consulta": "realizada", "publicada": False, "consultado_utc": "2026-10-14T04:00:00Z", "bajas_registradas": 0}]}
        nuevo = {"partidos": [{"match_id": "m1", "consulta": "realizada", "publicada": True, "consultado_utc": "2026-10-14T17:00:00Z", "bajas_registradas": 2}]}
        run = run_con_muestras(snapshots={"snapshot_20261014T040000Z.json": viejo, "snapshot_20261014T170000Z.json": nuevo})
        self.assertEqual(cov.build_contexts(run, [match()], [match()])["m1"]["alineaciones"], {"estado": "publicada", "snapshot_utc": "2026-10-14T17:00:00Z", "bajas_registradas": 2})
        self.assertEqual(cov.build_contexts(run_con_muestras(), [match()], [match()])["m1"]["alineaciones"], {"estado": "sin_snapshot"})
        sin_id = {"partidos": [{"match_id": "m1", "consulta": "no_realizada", "consultado_utc": "x"}]}
        self.assertEqual(cov.build_contexts(run_con_muestras(snapshots={"s.json": sin_id}), [match()], [match()])["m1"]["alineaciones"]["estado"], "consulta_no_realizada")


class AnaliticaConContexto(unittest.TestCase):
    def _summary(self, run, matches=None):
        return cov.run_coverage(run, write=False)

    def test_incidencias_informativas_sin_umbrales(self):
        parcial = [fila(i) for i in range(40)] + [fila(100 + i, tarjetas=None) for i in range(60)]          # tarjetas en 40 de 100 partidos
        run = run_con_muestras({"7": parcial}, matches=[match("m1"), match("m2", league="8")])           # la liga 8 no tiene muestra
        s = self._summary(run)
        inc = {i["tipo"]: i for i in s["analitica"]["incidencias"]}
        self.assertEqual(inc["liga_con_registro_incompleto_de_tarjetas"]["por_liga"], {"7": "40/100"})
        self.assertNotIn("liga_con_registro_incompleto_de_corners", inc)
        self.assertEqual(inc["muestra_de_liga_no_ejecutada"]["cantidad"], 1)
        self.assertEqual(inc["arbitro_no_designado"]["cantidad"], 2)
        self.assertEqual(inc["alineaciones_no_publicadas"]["por_estado"], {"sin_snapshot": 2})

    def test_las_filas_de_corners_y_tarjetas_llevan_la_muestra_de_liga(self):
        run = run_con_muestras({"7": [fila(i) for i in range(5)] + [fila(9, tarjetas=None)]})
        s, rows = cov.run_coverage(run, write=False, return_rows=True)
        r = next(x for x in rows if x["entry_id"] == "cards_pts.total.over.4.5")
        self.assertEqual(r["analitica"]["muestra_liga"], {"campo": "tarjetas", "ejecutada": True, "partidos_liga": 6, "con_campo": 5})
        r2 = next(x for x in rows if x["entry_id"] == "goles.total.over.2.5")
        self.assertNotIn("muestra_liga", r2["analitica"])                                                # solo córners y tarjetas dependen de la muestra de liga

    def test_el_contexto_no_cambia_la_certificacion_ni_la_preparacion(self):
        """Alineaciones sin publicar, árbitro sin designar o liga sin muestra son limitaciones analíticas: no son puertas de la investigación."""
        con = cov.run_coverage(run_con_muestras({"7": [fila(i) for i in range(5)]}), write=False)
        sin = cov.run_coverage(run_con_muestras(), write=False)
        self.assertEqual(con["investigacion"]["estado"], sin["investigacion"]["estado"])
        self.assertEqual(con["preparacion_para_apostar"]["filas_aptas"], 0)
        self.assertEqual(sin["preparacion_para_apostar"]["filas_aptas"], 0)
        self.assertEqual(con["analitica"]["estado"], "CON_LIMITACIONES")


class InstantaneaDeAlineaciones(unittest.TestCase):
    NOW = "2026-10-14T16:30:00Z"

    def _call(self, publicada=True):
        def call(**p):
            side = {"starting_lineups": [{"player_key": str(i)} for i in range(11 if publicada else 0)], "substitutes": [], "missing_players": [{"x": 1}] if publicada else []}
            return {p["match_id"]: {"lineup": {"home": side, "away": side}}}
        return call

    def test_publicada_o_no_segun_lo_que_devuelve_la_api(self):
        import datetime as dt
        now = dt.datetime.fromisoformat(self.NOW.replace("Z", "+00:00"))
        r = ls.snapshot_match(match(), self._call(True), now)
        self.assertEqual((r["consulta"], r["publicada"], r["bajas_registradas"], r["minutos_hasta_inicio"]), ("realizada", True, 2, 90))
        r = ls.snapshot_match(match(), self._call(False), now)
        self.assertEqual((r["publicada"], r["bajas_registradas"]), (False, 0))
        r = ls.snapshot_match(match(apif=None), self._call(True), now)
        self.assertEqual(r["consulta"], "no_realizada")

    def _main(self, run, *args):
        with mock.patch("lineups_snapshot.adapters.apif_key", return_value="k"), mock.patch("lineups_snapshot.adapters.apif_call", side_effect=lambda client, key, **p: self._call(False)(**p)), \
                mock.patch("sys.stdout"):
            return ls.main(["--run", run, "--matches", "m1,m2", "--now-utc", self.NOW, *args])

    def test_ventana_t60_nueva_instantanea_por_ejecucion_y_nunca_se_sobrescribe(self):
        run = run_con_muestras(matches=[match("m1", kick="2026-10-14T17:30:00Z"), match("m2", kick="2026-10-15T17:30:00Z")])
        self.assertEqual(self._main(run, "--window-minutes", "90"), 0)
        snap = _load(os.path.join(run, "lineups", "snapshot_20261014T163000Z.json"))
        self.assertEqual([p["match_id"] for p in snap["partidos"]], ["m1"])                              # m2 empieza en 25 h: fuera de la ventana
        self.assertEqual(snap["partidos_fuera_de_ventana"], 1)
        self.assertEqual(self._main(run, "--window-minutes", "90"), 2)                                   # mismo instante: no sobrescribe
        self.assertEqual(len(os.listdir(os.path.join(run, "lineups"))), 1)


class SinFuentesDeCuotas(unittest.TestCase):
    def test_el_contexto_no_depende_de_precios_ni_credenciales(self):
        with mock.patch.dict(os.environ, {}, clear=True):
            s = cov.run_coverage(run_con_muestras({"7": [fila(1)]}), write=False, aggregator=False)
        self.assertIn("contexto_partidos", s)
        self.assertEqual(s["precios"]["estado"], "SIN_PRECIOS_REALES")


if __name__ == "__main__":
    unittest.main()
