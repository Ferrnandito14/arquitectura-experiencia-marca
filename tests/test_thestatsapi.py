"""Segunda fuente de cuotas (TheStatsAPI): emparejamiento exacto, mapeo exacto de línea/selección, mediana entre casas, precios incoherentes descartados y la clave nunca registrada. Datos FICTICIOS: EJEMPLO — NO REAL."""
import json
import os
import tempfile
import unittest
import urllib.error

import helpers  # noqa: F401  (añade scripts/ al path)
import catalog_rankings as cr
import common
import market_catalog as mc
import market_coverage as cov
import price_sources as ps
import tsa_fetch as tf

KEY = "fapi_FICTICIA0123456789"


def L(o, c=None):
    return {"opening": c or o, "last_seen": o}


def book(name, **markets):
    return {"bookmaker": name, "markets": markets}


def run_dir(books, mid="m1", home="Alfa", away="Beta"):
    run = tempfile.mkdtemp()
    os.makedirs(os.path.join(run, "thestatsapi", "odds"))
    with open(os.path.join(run, "thestatsapi", "map.json"), "w", encoding="utf-8") as f:
        json.dump({"generado_utc": "2026-10-14T10:00:00Z", "partidos": {mid: {"tsa_id": "mt_1", "home": home, "away": away, "utc_date": "2026-10-14T18:00:00.000Z", "odds_available": True, "status": "scheduled"}}, "sin_emparejar": {"m2": {"partido": "X – Y", "motivo": "ningún partido con la misma hora y ambos equipos"}}}, f)
    with open(os.path.join(run, "thestatsapi", "odds", "mt_1.json"), "w", encoding="utf-8") as f:
        json.dump({"fetched_utc": "2026-10-14T10:05:00Z", "tsa_match_id": "mt_1", "response": {"data": {"match_id": "mt_1", "bookmakers": books}}}, f)
    return run


def match(mid="m1", home="Alfa", away="Beta", t="2026-10-14T18:00:00Z"):
    return {"match_id": mid, "home_team": home, "away_team": away, "normalized_datetime_utc": t}


class Mapeo(unittest.TestCase):
    def test_coincidencia_exacta_de_linea_y_seleccion(self):
        casos = {"corners.total.over.9.5": ("match_corners", None, "9.5", "over"), "corners.equipo.away.under.4.5": ("team_corners", "away", "4.5", "under"),
                 "cards_pts.total.over.3.5": ("total_cards", None, "3.5", "over"), "goles.equipo.home.over.0.5": ("team_total_goals", "home", "0.5", "over"),
                 "primera_parte.1x2.draw": ("first_half_result", None, None, "draw"), "primera_parte.total.under.1.5": ("first_half_total_goals", None, "1.5", "under"),
                 "resultado.eh.away.+1": ("handicap_result", None, "+1", "away"), "resultado.eh.draw.-1": ("handicap_result", None, "-1", "draw"),
                 "resultado.ah.home.-1.5": ("asian_handicap", "home", "-1.5", None), "resultado.ah_entero.away.+2": ("asian_handicap", "away", "+2", None),
                 "resultado.dnb.home": ("draw_no_bet", None, None, "home"), "resultado.dc.x2": ("double_chance", None, None, "draw_away"), "sot.equipo.home.over.4.5": ("team_shots_on_target", "home", "4.5", "over"),
                 "shots.total.under.26.5": ("match_shots", None, "26.5", "under"), "goles.total_entero.over.2": ("total_goals", None, "2", "over")}
        for eid, esperado in casos.items():
            self.assertEqual(ps.tsa_lookup(mc.BY_ID[eid]), esperado, eid)

    def test_lo_que_la_fuente_no_publica_no_se_mapea(self):
        for eid in ("otros.fueras_de_juego.total", "cards_pts.equipo.home.over.2.5"):
            self.assertIsNone(ps.tsa_lookup(mc.BY_ID[eid]), eid)

    def test_todo_id_mapeado_existe_en_el_catalogo_y_no_hay_dos_ids_con_la_misma_clave(self):
        claves = {}
        for e in mc.CATALOG:
            k = ps.tsa_lookup(e)
            if k:
                self.assertNotIn(k, claves, f"{e['id']} y {claves.get(k)} apuntan a la misma selección")
                claves[k] = e["id"]


class Proveedor(unittest.TestCase):
    def test_mediana_entre_casas_tipo_referencia_con_fuente_y_hora(self):
        mk = lambda o, u: {"match_corners": {"9.5": {"over": L(o), "under": L(u)}}}
        run = run_dir([book("Bet365", **mk("1.80", "2.00")), book("Pinnacle", **mk("1.90", "1.95")), book("BetMGM UK", **mk("2.10", "1.75"))])
        p = ps.TheStatsApiOddsProvider(run)
        r = p.prices(match(), mc.BY_ID["corners.total.over.9.5"])[0]
        self.assertEqual((r["odds"], r["n_books"], r["source_type"], r["verified"], r["observed_utc"]), (1.9, 3, "agregador", False, "2026-10-14T10:05:00Z"))
        self.assertFalse(ps.is_real_price(r))
        self.assertEqual(p.prices(match(), mc.BY_ID["corners.total.over.10.5"]), [])             # otra línea: nada, no se aproxima
        self.assertEqual(p.prices(match(), mc.BY_ID["cards_pts.total.over.3.5"]), [])

    def test_una_casa_con_par_incoherente_se_descarta(self):
        ok = {"total_goals": {"2.5": {"over": L("1.85"), "under": L("2.00")}}}
        roto = {"total_goals": {"2.5": {"over": L("1.02"), "under": L("10.5")}}}            # suma de probabilidades ≈ 1.07… pero invertido en el par: 0.98+0.095=1.08 → válido; usamos uno claramente roto
        roto = {"total_goals": {"2.5": {"over": L("1.01"), "under": L("1.01")}}}            # 1/1.01 + 1/1.01 ≈ 1.98: precio roto
        run = run_dir([book("A", **ok), book("B", **roto)])
        r = ps.TheStatsApiOddsProvider(run).prices(match(), mc.BY_ID["goles.total.over.2.5"])[0]
        self.assertEqual((r["odds"], r["n_books"]), (1.85, 1))
        self.assertIn("descartado", r["note"])

    def test_covers_distingue_partido_sin_emparejar(self):
        run = run_dir([book("A", btts={"yes": L("1.8"), "no": L("2.0")})])
        p = ps.TheStatsApiOddsProvider(run)
        self.assertTrue(p.covers(match())[0])
        ok, evid = p.covers(match("m2"))
        self.assertFalse(ok)
        self.assertIn("misma hora", evid["detalle"])

    def test_una_sola_casa_cuenta_como_otra_fuente_pero_con_sus_casas_visibles(self):
        run = run_dir([book("Bet365", match_corners={"9.5": {"over": L("1.85"), "under": L("1.95")}})])
        m = match()
        rows, _ = cov.build_records([m], {}, [ps.TheStatsApiOddsProvider(run)], catalog=[mc.BY_ID["corners.total.over.9.5"], mc.BY_ID["corners.total.over.10.5"]])
        a, b = rows
        self.assertEqual((a["precio"]["estado"], a["precio"]["registro"]["n_books"]), ("otra_fuente", 1))
        self.assertEqual(b["precio"]["estado"], "sin_precio")
        self.assertEqual([c["resultado"] for c in a["investigacion"]["canales"] if "thestatsapi" in c["canal"]], ["encontrado"])
        self.assertEqual([c["resultado"] for c in b["investigacion"]["canales"] if "thestatsapi" in c["canal"]], ["consultado_no_encontrado"])


class Emparejamiento(unittest.TestCase):
    rows = [{"id": "mt_1", "utc_date": "2026-10-14T18:00:00.000Z", "home_team": {"name": "Paris Saint-Germain"}, "away_team": {"name": "Manchester City"}},
            {"id": "mt_2", "utc_date": "2026-10-14T18:00:00.000Z", "home_team": {"name": "Manchester City"}, "away_team": {"name": "Paris Saint-Germain"}}]

    def test_exige_local_y_visitante_con_su_orientacion_y_acepta_siglas(self):
        r, why = tf.pair_match(match(home="PSG", away="Manchester City"), self.rows)
        self.assertEqual(r["id"], "mt_1")
        r, why = tf.pair_match(match(home="Manchester City", away="PSG"), self.rows)
        self.assertEqual(r["id"], "mt_2")

    def test_hora_distinta_o_ambiguedad_no_empareja(self):
        r, why = tf.pair_match(match(home="PSG", away="Manchester City", t="2026-10-14T21:00:00Z"), self.rows)
        self.assertIsNone(r)
        dup = self.rows + [dict(self.rows[0], id="mt_9")]
        r, why = tf.pair_match(match(home="PSG", away="Manchester City"), dup)
        self.assertIsNone(r)
        self.assertIn("ambiguo", why)
        r, why = tf.pair_match(match(home="Alfa", away="Beta"), self.rows)
        self.assertIsNone(r)


class Cliente(unittest.TestCase):
    class Resp:
        def __init__(self, status, body):
            self.status, self._b = status, body

        def read(self):
            return self._b.encode()

    def fetcher(self, script):
        calls = []

        def opener(req, timeout=0):
            calls.append(req)
            x = script.pop(0)
            if isinstance(x, tuple) and x[0] >= 400:
                raise urllib.error.HTTPError(req.full_url, x[0], "err", {"Retry-After": "1"}, __import__("io").BytesIO(x[1].encode()))
            return Cliente.Resp(*x)
        f = tf.Fetcher(KEY, min_interval=0, sleep=lambda s: None, opener=opener)
        f.log_path = os.path.join(tempfile.mkdtemp(), "consultas.jsonl")
        return f, calls

    def test_cabecera_bearer_user_agent_honesto_y_la_clave_no_llega_al_registro(self):
        f, calls = self.fetcher([(200, "{}")])
        f.get("/football/matches?date_from=2026-10-14")
        self.assertEqual(calls[0].get_header("Authorization"), "Bearer " + KEY)
        self.assertEqual(calls[0].get_header("User-agent"), "football-picks-system/0.1")
        with open(f.log_path, encoding="utf-8") as fh:
            log = fh.read()
        self.assertNotIn(KEY, log)
        self.assertNotIn("Bearer", log)
        self.assertIn('"provider": "thestatsapi"', log)

    def test_429_espera_y_reintenta(self):
        f, calls = self.fetcher([(429, "{}"), (200, "{}")])
        self.assertEqual(f.get("/x")[0], 200)
        self.assertEqual(len(calls), 2)

    def test_host_no_permitido_se_rechaza(self):
        f, _ = self.fetcher([(200, "{}")])
        f.policy = common.Policy(data={"providers": {}})
        with self.assertRaises(common.PolicyError):
            f.get("/x")

    def test_la_politica_registra_el_host_como_condicional_y_el_doc_lo_menciona(self):
        n, p = common.Policy().lookup("api.thestatsapi.com")
        self.assertEqual((n, p["status"]), ("thestatsapi", "condicional"))
        with open(os.path.join(helpers.SCRIPTS, "..", "..", "..", "..", "docs", "FUENTES-CONFORMIDAD.md"), encoding="utf-8") as fh:
            self.assertIn("thestatsapi", fh.read().lower())

    def test_ningun_script_contiene_una_clave_real(self):
        for fn in os.listdir(helpers.SCRIPTS):
            if fn.endswith(".py"):
                with open(os.path.join(helpers.SCRIPTS, fn), encoding="utf-8") as fh:
                    self.assertNotRegex(fh.read(), r"fapi_[A-Za-z0-9]{20,}", fn)


class EstadoDeAgentes(unittest.TestCase):
    def test_un_precio_nuevo_no_hereda_la_aprobacion_de_la_revision_anterior(self):
        from test_catalog_rankings import Agentes, OVER, unit, entrada
        a = Agentes()
        us = [unit(1, [entrada(OVER[0], 1.5, 0.7, estado="otra_fuente")])]
        reps = a.reports(us)
        e = us[0]["entradas"][0]["precio"]
        igual = {("m1", OVER[0]): (e["estado"], e["cuota"], e["fuente"])}
        self.assertEqual(cr.agent_status(us, reps, igual)[(us[0]["unit_id"], OVER[0])], "aprobada")
        movida = {("m1", OVER[0]): (e["estado"], 1.2, e["fuente"])}                      # la misma fuente con otra cuota: sigue aprobada
        self.assertEqual(cr.agent_status(us, reps, movida)[(us[0]["unit_id"], OVER[0])], "aprobada")
        legs = cr.legs_from_units(us, {}, movida)
        self.assertEqual(legs[0]["cuota_revisada"], 1.2)
        otro = {("m1", OVER[0]): ("sin_precio", None, None)}
        self.assertEqual(cr.agent_status(us, reps, otro)[(us[0]["unit_id"], OVER[0])], "precio_nuevo_sin_revisar")


if __name__ == "__main__":
    unittest.main()
