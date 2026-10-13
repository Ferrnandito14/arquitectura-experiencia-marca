import unittest
from datetime import datetime, timezone
import helpers
from helpers import raw, epoch
import inventory, adapters, common

NOW = datetime(2026, 10, 12, 23, 45, tzinfo=timezone.utc)      # 19:45 en Caracas
TZ = "America/Caracas"


def build(by_source, now=NOW):
    return inventory.build_inventory(by_source, "2026-10-13", TZ, now, helpers.POLICY)


def one(ms, home):
    return next(m for m in ms if m["home_team"] == home)


class Dedup(unittest.TestCase):
    def test_unique_count_not_sum_of_raw(self):
        a = [raw("football-data", f"Eq{i}", f"Rv{i}", "Championship", "2026-10-13 19:45", "Europe/London", False) for i in range(5)]
        b = [raw("apwin", f"Eq{i}", f"Rv{i}", "championship", None, "UTC", True, epoch=epoch(f"2026-10-13T18:45:00Z")) for i in range(3)]
        ms, dups = build({"football-data": a, "apwin": b})
        self.assertEqual(len(a) + len(b), 8)
        self.assertEqual(len(ms), 5)

    def test_same_names_different_incompatible_competition_not_merged(self):
        a = raw("football-data", "Racing", "Union", "Premier League", "2026-10-13 20:00", "UTC")
        b = raw("apwin", "Racing", "Union", "Copa Argentina", None, "UTC", epoch=epoch("2026-10-13T20:00:00Z"))
        ms, _ = build({"football-data": [a], "apwin": [b]})
        self.assertEqual(len(ms), 2)
        self.assertTrue(any(d["kind"] == "posible_duplicado_ambiguo" for m in ms for d in m["discrepancies"]))

    def test_women_reserve_youth_never_merged_with_men(self):
        men = raw("football-data", "Barcelona", "Madrid", "La Liga", "2026-10-13 20:00", "UTC")
        w = raw("apwin", "Barcelona Women", "Madrid Women", "Liga F", None, "UTC", epoch=epoch("2026-10-13T20:00:00Z"))
        ms, _ = build({"football-data": [men], "apwin": [w]})
        self.assertEqual(sorted(m["gender_or_category"] for m in ms), ["men", "women"])
        self.assertEqual(inventory.detect_category("Real Madrid U19", "X U19", "Youth League"), "youth")
        self.assertEqual(inventory.detect_category("Bayern München II", "X", "Regionalliga"), "reserve")

    def test_category_regressions_found_by_review(self):
        dc = inventory.detect_category
        self.assertEqual(dc("Novorizontino", "Ponte Preta", "Serie B"), "men")        # 'Serie B' es primera plantilla (falso positivo antiguo)
        self.assertEqual(dc("Genoa", "Sampdoria", "Serie B"), "men")
        self.assertEqual(dc("Utrecht", "Willem II", "Eredivisie"), "men")             # Willem II es primer equipo
        self.assertEqual(dc("Celta B", "Sociedad B", "La Liga 2"), "reserve")         # filiales (falso negativo antiguo)
        self.assertEqual(dc("Portimonense U23", "Academico Viseu U23", "Liga Revelação U23"), "u23")
        self.assertEqual(dc("Newcastle Jets FC", "Gamba Osaka", "AFC Champions League"), "men")

    def test_duplicate_within_same_source_marked_DUPLICADO(self):
        a = raw("apwin", "A", "B", "Liga", None, "UTC", epoch=epoch("2026-10-13T20:00:00Z"), mid="1")
        b = dict(a, source_match_id="2")
        ms, dups = build({"apwin": [a, b]})
        self.assertEqual(len(ms), 1)
        self.assertEqual(dups[0]["calendar_verification_status"], "DUPLICADO")
        self.assertEqual(dups[0]["duplicate_of"], "apwin:1")


class Statuses(unittest.TestCase):
    def test_two_independent_sources_confirm(self):
        a = raw("football-data", "A", "B", "Championship", "2026-10-13 19:45", "Europe/London", False)
        b = raw("apwin", "A", "B", "Championship", None, "UTC", epoch=epoch("2026-10-13T18:45:00Z"))
        m = build({"football-data": [a], "apwin": [b]})[0][0]
        self.assertEqual((m["calendar_verification_status"], m["confirmation_basis"]), ("CONFIRMADO", "dos_fuentes_independientes"))
        self.assertEqual(m["prematch_eligibility"], "ELEGIBLE")
        self.assertTrue(m["analysis_required"])

    def test_single_structured_source_confirms_but_single_aggregator_does_not(self):
        a = raw("football-data", "A", "B", "Championship", "2026-10-13 19:45", "Europe/London", False)
        b = raw("apwin", "C", "D", "Liga", None, "UTC", epoch=epoch("2026-10-13T18:45:00Z"))
        ms, _ = build({"football-data": [a], "apwin": [b]})
        self.assertEqual(one(ms, "A")["confirmation_basis"], "una_fuente_estructurada_fiable_sin_discrepancias")
        self.assertEqual(one(ms, "C")["calendar_verification_status"], "NO_CONFIRMADO")
        self.assertEqual(one(ms, "C")["prematch_eligibility"], "PENDIENTE_DE_VERIFICAR")
        self.assertFalse(one(ms, "C")["analysis_required"])

    def test_hour_discrepancy(self):
        a = raw("football-data", "A", "B", "Championship", "2026-10-13 20:45", "Europe/London", False)   # 19:45Z
        b = raw("apwin", "A", "B", "Championship", None, "UTC", epoch=epoch("2026-10-13T18:45:00Z"))
        m = build({"football-data": [a], "apwin": [b]})[0][0]
        self.assertEqual(m["calendar_verification_status"], "FECHA_DISCREPANTE")
        self.assertEqual(m["prematch_eligibility"], "PENDIENTE_DE_VERIFICAR")

    def test_missing_time_is_insufficient_information(self):
        a = raw("football-data", "A", "B", "Championship", "2026-10-13", "Europe/London", False)
        m = build({"football-data": [a]})[0][0]
        self.assertEqual(m["calendar_verification_status"], "INFORMACION_INSUFICIENTE")
        self.assertIsNone(m["normalized_datetime_utc"])

    def test_confirmed_AND_finished_are_independent_states(self):
        a = raw("apwin", "A", "B", "Liga", None, "UTC", epoch=epoch("2026-10-13T05:00:00Z"), status="finished", mid="1")
        b = raw("football-data", "A", "B", "Liga", "2026-10-13 06:00", "Europe/London", False)
        later = datetime(2026, 10, 13, 12, 0, tzinfo=timezone.utc)
        m = build({"apwin": [a], "football-data": [b]}, now=later)[0][0]
        self.assertEqual(m["calendar_verification_status"], "CONFIRMADO")
        self.assertEqual(m["event_status"], "FINALIZADO")
        self.assertEqual(m["prematch_eligibility"], "NO_ELEGIBLE")
        self.assertIn("ya ha comenzado", m["disposition"])
        self.assertFalse(m["analysis_required"])

    def test_postponed_and_cancelled_kept(self):
        a = raw("apwin", "A", "B", "Liga", None, "UTC", epoch=epoch("2026-10-13T20:00:00Z"), status="postponed")
        b = raw("football-data", "A", "B", "Liga", "2026-10-13 21:00", "Europe/London", False)
        m = build({"apwin": [a], "football-data": [b]})[0][0]
        self.assertEqual(m["event_status"], "APLAZADO")
        self.assertEqual(m["prematch_eligibility"], "NO_ELEGIBLE")

    def test_upcoming_but_past_time_is_discrepancy_not_eligible(self):
        a = raw("apwin", "A", "B", "Liga", None, "UTC", epoch=epoch("2026-10-13T05:00:00Z"), status="upcoming")
        later = datetime(2026, 10, 13, 12, 0, tzinfo=timezone.utc)
        m = build({"apwin": [a]}, now=later)[0][0]
        self.assertEqual(m["event_status"], "DESCONOCIDO")
        self.assertTrue(any(d["kind"] == "estado" for d in m["discrepancies"]))
        self.assertNotEqual(m["prematch_eligibility"], "ELEGIBLE")


class LocalDateBoundaries(unittest.TestCase):
    def elig(self, iso):
        a = raw("football-data", "A", "B", "Liga", None, "UTC", epoch=epoch(iso))
        b = raw("apwin", "A", "B", "Liga", None, "UTC", epoch=epoch(iso))
        return build({"football-data": [a], "apwin": [b]})[0][0]

    def test_bragantino_cruzeiro_is_not_on_local_13_oct(self):
        m = self.elig("2026-10-13T00:00:00Z")
        self.assertEqual(m["normalized_datetime_local"][:16], "2026-10-12T20:00")
        self.assertEqual(m["prematch_eligibility"], "NO_ELEGIBLE")
        self.assertIn("fuera de la fecha local", m["disposition"])

    def test_edges_inclusive_start_exclusive_end(self):
        self.assertEqual(self.elig("2026-10-13T03:59:00Z")["prematch_eligibility"], "NO_ELEGIBLE")
        self.assertEqual(self.elig("2026-10-13T04:00:00Z")["prematch_eligibility"], "ELEGIBLE")
        self.assertEqual(self.elig("2026-10-14T03:59:00Z")["prematch_eligibility"], "ELEGIBLE")
        self.assertEqual(self.elig("2026-10-14T04:00:00Z")["prematch_eligibility"], "NO_ELEGIBLE")

    def test_out_of_window_matches_stay_in_inventory(self):
        m = self.elig("2026-10-13T00:00:00Z")
        self.assertIsNotNone(m["match_id"])


class Adapters(unittest.TestCase):
    def test_footballdata_csv_parse_and_tz_flag(self):
        csv_text = "Div,Date,Time,HomeTeam,AwayTeam,Referee,B365H,B365D,B365A,B365>2.5,B365<2.5\nE1,13/10/2026,19:45,Millwall,Swansea,A Ref,2.4,3.4,2.8,1.9,1.9\n"
        class C:
            def fetch(self, url):
                class R: text = csv_text
                return R()
        r = adapters.fd_fixtures(C())
        self.assertEqual((r[0]["home"], r[0]["competition"], r[0]["source_timezone"], r[0]["tz_confirmed"]), ("Millwall", "Championship", "Europe/London", False))
        self.assertEqual(r[0]["odds"]["B365H"], "2.4")

    def test_apwin_embedded_json_parse(self):
        blob = ('{\\"countrySlug\\":\\"europe\\",\\"leagueSlug\\":\\"uefa-champions-league\\",\\"matches\\":[{\\"slug\\":\\"x\\",\\"code\\":\\"c\\",'
                '\\"status\\":\\"upcoming\\",\\"id\\":\\"7\\",\\"homeTeam\\":\\"Lens\\",\\"awayTeam\\":\\"Sporting\\",\\"kickoffUnix\\":1791909900,\\"time\\":\\"12:45\\"}]}')
        class C:
            def fetch(self, url):
                class R: text = blob
                return R()
        r = adapters.apwin_home(C())
        self.assertEqual((r[0]["home"], r[0]["competition"], r[0]["country"], r[0]["utc_epoch"]), ("Lens", "uefa champions league", "europe", 1791909900))
        self.assertEqual(adapters.apwin_status("upcoming"), "PROGRAMADO")


class Registry(unittest.TestCase):
    def test_excluded_providers_listed_as_not_consulted_with_reason(self):
        rows = inventory.source_registry(helpers.POLICY, [])
        fm = next(r for r in rows if r["Fuente"] == "fotmob")
        self.assertEqual(fm["Estado"], "No consultada")
        self.assertIn("EXCLUIDA", fm["Alternativa consultada"])
        self.assertEqual(set(fm), {"Fuente", "URL o ficha", "Dato buscado", "Información obtenida", "Fecha de consulta", "Estado", "Discrepancias", "Alternativa consultada"})


if __name__ == "__main__":
    unittest.main()


class SelectionVerification(unittest.TestCase):
    def test_single_structured_source_enters_universe_but_final_selection_needs_more(self):
        a = raw("football-data", "A", "B", "Championship", "2026-10-13 19:45", "Europe/London", False)
        m = build({"football-data": [a]})[0][0]
        self.assertEqual(m["calendar_verification_status"], "CONFIRMADO")
        self.assertTrue(m["analysis_required"])
        self.assertEqual(m["selection_calendar_verification"], "REQUIERE_VERIFICACION_ADICIONAL")

    def test_two_independent_sources_sufficient_for_selection(self):
        a = raw("football-data", "A", "B", "Championship", "2026-10-13 19:45", "Europe/London", False)
        b = raw("apwin", "A", "B", "Championship", None, "UTC", epoch=epoch("2026-10-13T18:45:00Z"))
        m = build({"football-data": [a], "apwin": [b]})[0][0]
        self.assertEqual(m["selection_calendar_verification"], "SUFICIENTE")


class ApwinDays(unittest.TestCase):
    def test_apwin_requested_for_three_days_within_page_cap(self):
        import copy, tempfile
        urls = []
        class C:
            def fetch(self, url):
                urls.append(url)
                class R: text = ""
                return R()
        for d in common.days_to_query("2026-10-13"):
            adapters.apwin_home(C(), d.isoformat())
        self.assertEqual([u.split("=")[-1] for u in urls], ["2026-10-12", "2026-10-13", "2026-10-14"])
        self.assertLessEqual(len(urls), helpers.POLICY.data["providers"]["apwin"].get("limits", {}).get("max_pages_per_run", 3))


class ApwinParserRegression(unittest.TestCase):
    def test_non_match_object_before_league_header_does_not_swallow_next_matches_league(self):
        # Fallo real: un objeto con slug+code que NO es partido, antes de la cabecera de liga, hacía que el regex perezoso
        # abarcara hasta el primer partido de la liga y le asignara competición vacía.
        noise = '{\\"slug\\":\\"noticia\\",\\"code\\":\\"n\\",\\"title\\":\\"x\\"}'
        league = ('{\\"countrySlug\\":\\"europe\\",\\"leagueSlug\\":\\"uefa-champions-league\\",\\"matches\\":['
                  '{\\"slug\\":\\"m2\\",\\"code\\":\\"c\\",\\"status\\":\\"upcoming\\",\\"id\\":\\"2\\",\\"homeTeam\\":\\"Sabah\\",'
                  '\\"awayTeam\\":\\"Slavia\\",\\"ext\\":{\\"b\\":2},\\"kickoffUnix\\":1791909900}]}')
        class C:
            def fetch(self, url):
                class R: text = noise + "xx" + league
                return R()
        r = adapters.apwin_home(C())
        self.assertEqual(len(r), 1)
        self.assertEqual(r[0]["competition"], "uefa champions league")
        self.assertEqual(r[0]["country"], "europe")
        self.assertEqual(r[0]["source_match_id"], "2")


class StableIds(unittest.TestCase):
    def test_match_id_does_not_depend_on_category_or_competition(self):
        a = raw("apwin", "Celta B", "Sociedad B", "Liga X", None, "UTC", epoch=epoch("2026-10-13T20:00:00Z"))
        b = dict(a, competition="Otro nombre de liga")
        ma = build({"apwin": [a]})[0][0]["match_id"]
        mb = build({"apwin": [b]})[0][0]["match_id"]
        self.assertEqual(ma, mb)
        self.assertEqual(inventory.match_id("a", "b", "2026-10-13"), inventory.match_id("a", "b", "2026-10-13"))

    def test_id_collision_gets_deterministic_suffix(self):
        a = raw("football-data", "Real", "Madrid", "Liga A", "2026-10-13 20:00", "UTC", mid="1")
        b = raw("apwin", "Real", "Madrid", "Copa Z", None, "UTC", epoch=epoch("2026-10-13T20:00:00Z"), mid="2")
        ms, _ = build({"football-data": [a], "apwin": [b]})
        ids = sorted(m["match_id"] for m in ms)
        self.assertEqual(len(ids), 2)
        self.assertEqual(ids[1], ids[0] + "-2")


class ConfirmationBasis(unittest.TestCase):
    def test_basis_discloses_open_discrepancies(self):
        a = raw("football-data", "A", "B", "Championship", "2026-10-13 06:00", "UTC", False, status="programado")
        later = datetime(2026, 10, 13, 12, 0, tzinfo=timezone.utc)
        ms, _ = inventory.build_inventory({"football-data": [a]}, "2026-10-13", TZ, later, helpers.POLICY,
                                          status_mappers={"football-data": lambda s: "PROGRAMADO"})
        m = ms[0]
        self.assertEqual(m["calendar_verification_status"], "CONFIRMADO")
        self.assertTrue(any(d["kind"] == "estado" for d in m["discrepancies"]))
        self.assertNotIn("sin_discrepancias", m["confirmation_basis"])
        self.assertIn("con_discrepancias_abiertas", m["confirmation_basis"])
        self.assertEqual(m["selection_calendar_verification"], "REQUIERE_VERIFICACION_ADICIONAL")


class PreserveProgressOnRegeneration(unittest.TestCase):
    def test_carry_over_keeps_progress_only_if_match_unchanged(self):
        a = raw("football-data", "A", "B", "Championship", "2026-10-13 19:45", "Europe/London", False)
        prev, _ = build({"football-data": [a]})
        prev[0]["sports_analysis_status"] = "NO_EVALUABLE_TRAS_INTENTOS"
        prev[0]["market_analysis_status"] = "COMPLETADO"
        same, _ = build({"football-data": [a]})
        inventory.carry_over_progress(same, prev)
        self.assertEqual((same[0]["sports_analysis_status"], same[0]["market_analysis_status"]), ("NO_EVALUABLE_TRAS_INTENTOS", "COMPLETADO"))
        moved = dict(a, original_datetime="2026-10-13 21:00")
        new, _ = build({"football-data": [moved]})
        inventory.carry_over_progress(new, prev)                    # la hora cambió: hay que reevaluar
        self.assertEqual(new[0]["sports_analysis_status"], "PENDIENTE")


if __name__ == "__main__":
    unittest.main()


class ApwinPagination(unittest.TestCase):
    BLOB = ('{\\"pagination\\":{\\"page\\":1,\\"hasMore\\":true,\\"total\\":166},\\"x\\":1}'
            '{\\"countrySlug\\":\\"europe\\",\\"leagueSlug\\":\\"uefa-champions-league\\",\\"matches\\":['
            '{\\"slug\\":\\"m\\",\\"code\\":\\"c\\",\\"status\\":\\"upcoming\\",\\"id\\":\\"1\\",\\"homeTeam\\":\\"A\\",\\"awayTeam\\":\\"B\\",\\"kickoffUnix\\":1791909900}]}')

    def test_pagination_parsed_and_loaded_counted(self):
        class C:
            def fetch(self, url):
                class R: text = ApwinPagination.BLOB
                return R()
        recs, pag = adapters.apwin_fetch(C(), "2026-10-13")
        self.assertEqual((len(recs), pag["loaded"], pag["declared_total"], pag["has_more"]), (1, 1, 166, True))
        self.assertEqual(pag["day"], "2026-10-13")
        self.assertEqual(len(adapters.apwin_home(C(), "2026-10-13")), 1)

    def test_no_pagination_block_returns_none(self):
        class C:
            def fetch(self, url):
                class R: text = "nada"
                return R()
        self.assertIsNone(adapters.apwin_fetch(C(), "2026-10-13")[1])


class ApwinFetchAll(unittest.TestCase):
    """Fixtures ficticios (EJEMPLO — NO REAL) de la paginación vía /api/home/calendar."""
    @staticmethod
    def _page(page, ids, has_more, total=5):
        import json
        ms = [{"id": str(i), "homeTeam": f"H{i}", "awayTeam": f"A{i}", "kickoffUnix": 1791909900 + i, "status": "upcoming"} for i in ids]
        return json.dumps({"groups": [{"leagueSlug": "liga-x", "countrySlug": "pais-x", "matches": ms}],
                           "pagination": {"page": page, "hasMore": has_more, "total": total, "totalLive": 0, "totalFinished": 0}})

    def _client(self, pages, first_has_more=True):
        urls = []
        first = ApwinPagination.BLOB.replace("true", "true" if first_has_more else "false").replace("166", "5")

        class C:
            def fetch(s, url):
                urls.append(url)
                class R: pass
                r = R()
                r.text = first if "/api/" not in url else pages[len(urls) - 2]
                return r
        return C(), urls

    def test_follows_pages_until_has_more_false_and_dedupes(self):
        c, urls = self._client([self._page(2, [1, 2, 3], True), self._page(3, [3, 4, 5], False)])
        recs, pag = adapters.apwin_fetch_all(c, "2026-10-13")
        self.assertEqual(len({r["source_match_id"] for r in recs}), len(recs))
        self.assertEqual((len(recs), pag["pages_fetched"], pag["complete"]), (5, 3, True))
        self.assertTrue(all("/api/home/calendar?" in u and "page=" in u for u in urls[1:]))
        self.assertIn("timezone=America%2FNew_York", urls[1])

    def test_page_cap_and_incomplete_flag(self):
        c, _ = self._client([self._page(2, [2], True), self._page(3, [3], True)])
        recs, pag = adapters.apwin_fetch_all(c, "2026-10-13", max_pages=2)
        self.assertEqual((pag["pages_fetched"], pag["complete"], pag["stop_reason"]), (2, False, "tope de páginas"))

    def test_bad_structure_stops_without_inventing(self):
        c, _ = self._client(['{"nope": 1}'])
        recs, pag = adapters.apwin_fetch_all(c, "2026-10-13")
        self.assertEqual(len(recs), 1)
        self.assertFalse(pag["complete"])
        self.assertIn("error en página 2", pag["stop_reason"])

    def test_no_more_pages_makes_no_api_call(self):
        c, urls = self._client([], first_has_more=False)
        recs, pag = adapters.apwin_fetch_all(c, "2026-10-13")
        self.assertEqual(len(urls), 1)
        self.assertEqual(pag["stop_reason"], "hasMore=false")


class CarryOverProxyResolution(unittest.TestCase):
    def test_proxy_resolution_survives_regeneration(self):
        old = [{"match_id": "m1", "normalized_datetime_utc": "2026-10-13T19:00:00Z", "sports_analysis_status": "PARCIAL_PROXY_OTRA_COMPETICION",
                "market_analysis_status": "PENDIENTE", "extra": {"proxy_resolution": {"home": ["SP1", "Ath Madrid"], "away": ["E0", "Man United"]}}}]
        new = [{"match_id": "m1", "normalized_datetime_utc": "2026-10-13T19:00:00Z", "sports_analysis_status": "PENDIENTE",
                "market_analysis_status": "PENDIENTE", "extra": {"div": None}}]
        inventory.carry_over_progress(new, old)
        self.assertEqual(new[0]["extra"]["proxy_resolution"]["home"][1], "Ath Madrid")
        self.assertEqual(new[0]["sports_analysis_status"], "PARCIAL_PROXY_OTRA_COMPETICION")
