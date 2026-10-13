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
        self.assertEqual(inventory.detect_category("Sevilla Atletico", "Real B", "Segunda"), "men")
        self.assertEqual(inventory.detect_category("Real Madrid U19", "X U19", "Youth League"), "youth")
        self.assertEqual(inventory.detect_category("Bayern II", "X", "Regionalliga"), "reserve")

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
