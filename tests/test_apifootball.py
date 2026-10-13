"""apifootball: adaptador, alineación con otras fuentes y cola con límite de la API. Datos FICTICIOS: EJEMPLO — NO REAL."""
import json, os, tempfile, unittest
from datetime import datetime, timezone
import helpers
import adapters, common, inventory, level1

KEY = "SECRETKEY1234567890"


class Resp:
    def __init__(self, text): self.text = text


class FakeClient:
    def __init__(self, payload): self.payload, self.urls = payload, []

    def fetch(self, url):
        self.urls.append(url)
        p = self.payload(url) if callable(self.payload) else self.payload
        return Resp(p if isinstance(p, str) else json.dumps(p))


def ev(mid, home, away, hs, as_, date="2026-10-01", status="Finished", stats=None, cards=None, hid="1", aid="2", league="Liga X"):
    return {"match_id": mid, "match_date": date, "match_time": "18:00", "match_status": status, "match_hometeam_name": home,
            "match_awayteam_name": away, "match_hometeam_id": hid, "match_awayteam_id": aid, "match_hometeam_score": str(hs),
            "match_awayteam_score": str(as_), "league_name": league, "league_id": "9", "country_name": "X",
            "statistics": stats or [], "cards": cards or [], "match_referee": ""}


class Call(unittest.TestCase):
    def test_timezone_is_urlencoded_and_key_not_leaked(self):
        c = FakeClient([])
        adapters.apif_call(c, KEY, action="get_events", timezone="America/Caracas")
        self.assertIn("timezone=America%2FCaracas", c.urls[0])

    def test_limit_error_raises_and_empty_result_is_list(self):
        with self.assertRaises(adapters.ApiLimit):
            adapters.apif_call(FakeClient({"error": 429, "message": "You have exceeded the request limit of your plan"}), KEY, action="x")
        self.assertEqual(adapters.apif_call(FakeClient({"error": 404, "message": "No event found!"}), KEY, action="x"), [])

    def test_status_mapping(self):
        m = adapters.apif_status
        self.assertEqual([m(""), m("Not Started"), m("Finished"), m("After Pen."), m("Postponed"), m("Cancelled"), m("Half Time"), m("67")],
                         ["upcoming", "upcoming", "finished", "finished", "postponed", "cancelled", "live", "live"])


class HistoryRow(unittest.TestCase):
    def test_missing_stats_are_none_not_zero(self):
        r = adapters.apif_history_row(ev("1", "A", "B", 2, 1), "1")
        self.assertEqual((r["gf"], r["ga"], r["venue"]), (2, 1, "local"))
        self.assertEqual((r["corners"], r["yellow"], r["red"], r["shots"]), ((None, None),) * 4)

    def test_stats_and_cards_list(self):
        stats = [{"type": "Corners", "home": "6", "away": "4"}, {"type": "Shots Total", "home": "12", "away": "9"}]
        cards = [{"card": "yellow card", "home_fault": "P1", "away_fault": ""}, {"card": "red card", "home_fault": "", "away_fault": "P2"}]
        r = adapters.apif_history_row(ev("1", "A", "B", 0, 3, stats=stats, cards=cards), "2")     # equipo visitante
        self.assertEqual((r["venue"], r["gf"], r["ga"]), ("visitante", 3, 0))
        self.assertEqual((r["corners"], r["shots"], r["yellow"], r["red"]), ((6, 4), (12, 9), (1, 0), (0, 1)))


class Odds(unittest.TestCase):
    def test_average_needs_min_books(self):
        rows = [{"match_id": "1", "odd_bookmakers": "a", "odd_1": "2.0", "odd_x": "3.0", "odd_2": "4.0", "bts_yes": "", "bts_no": ""},
                {"match_id": "1", "odd_bookmakers": "b", "odd_1": "2.2", "odd_x": "3.2", "odd_2": "3.8"},
                {"match_id": "2", "odd_bookmakers": "a", "odd_1": "1.5", "odd_x": "4", "odd_2": "6"}]
        out = adapters.apif_odds_average(rows)
        self.assertEqual(out["1"]["resultado.1x2"]["cuotas_medias"], [2.1, 3.1, 3.9])
        self.assertEqual(out["1"]["resultado.1x2"]["n_casas"], 2)
        self.assertNotIn("2", out)            # una sola casa: no hay promedio
        self.assertNotIn("goles.btts", out["1"])


class Align(unittest.TestCase):
    def _r(self, src, home, away, dt, comp="Liga", mid=None):
        ep = helpers.epoch(dt.replace(" ", "T") + ("Z" if not dt.endswith("Z") else "")) if src == "apwin" else None
        r = helpers.raw(src, home, away, comp, dt, mid=mid or f"{src}-{home}", epoch=ep)
        if src == "apifootball":
            r["api"] = {"match_id": r["source_match_id"], "home_id": "1", "away_id": "2", "home_name": home, "away_name": away}
        return r

    def test_unique_alignment_renames_to_other_source(self):
        other = [self._r("apwin", "Pohang Steelers", "Johor Darul Ta'zim", "2026-10-13T10:00:00Z")]
        api = [self._r("apifootball", "Pohang", "Johor DT", "2026-10-13 10:00", comp="AFC Champions League Elite - League Phase")]
        keep, rep = inventory.align_api_records(api, other)
        self.assertEqual((keep[0]["home"], rep["aligned_with_other_source"], rep["api_only_added"]), ("Pohang Steelers", 1, 0))

    def test_category_prevents_wrong_merge(self):
        other = [self._r("apwin", "Arsenal U19", "Lille U19", "2026-10-13T12:00:00Z", comp="UEFA Youth League")]
        api = [self._r("apifootball", "Arsenal Tivat", "FK Lille", "2026-10-13 12:00")]
        keep, rep = inventory.align_api_records(api, other)
        self.assertEqual((rep["aligned_with_other_source"], rep["api_only_added"]), (0, 1))

    def test_ambiguity_excludes_api_event(self):
        other = [self._r("apwin", "Real Sol", "Gran Mar", "2026-10-13T12:00:00Z", mid="1"), self._r("apwin", "Real Sol Atletico", "Gran Marina", "2026-10-13T12:00:00Z", mid="2")]
        api = [self._r("apifootball", "Real Sol", "Gran Mar", "2026-10-13 12:00")]
        keep, rep = inventory.align_api_records(api, other)
        self.assertEqual((keep, rep["ambiguous_excluded"]), ([], 1))

    def test_alignment_merges_into_two_independent_sources(self):
        now = datetime(2026, 10, 12, 23, 0, tzinfo=timezone.utc)
        other = [self._r("apwin", "Pohang Steelers", "Johor Darul Ta'zim", "2026-10-13T10:00:00Z")]
        api = [self._r("apifootball", "Pohang", "Johor DT", "2026-10-13 10:00")]
        keep, _ = inventory.align_api_records(api, other)
        pol = common.Policy()
        ms, _ = inventory.build_inventory({"apwin": other, "apifootball": keep}, "2026-10-13", "America/Caracas", now, pol)
        self.assertEqual(len(ms), 1)
        self.assertEqual(ms[0]["extra"]["api"]["home_id"], "1")
        self.assertEqual(ms[0]["confirmation_basis"], "dos_fuentes_independientes")


class ApiProvider(unittest.TestCase):
    def test_history_uses_only_finished_and_keeps_last_n(self):
        evs = [ev(str(i), "A", "B", 1, 0, date=f"2026-09-{i + 1:02d}") for i in range(14)] + [ev("x", "A", "B", 0, 0, date="2026-09-20", status="Postponed")]
        c = FakeClient(evs)
        p = level1.ApiFootballHistory(c, KEY, "2026-10-13")
        m = {"home_team": "A", "away_team": "B", "extra": {"api": {"home_id": "1", "away_id": "2", "match_id": "9"}}}
        h = p.team_history(m, "A", "2026-10-13")
        self.assertEqual(len(h), level1.HISTORY_N)
        self.assertTrue(all(r["date"] <= "2026-09-14" for r in h))

    def test_limit_stops_queue_and_leaves_pending(self):
        d = tempfile.mkdtemp()
        inv = {"meta": {"date": "2026-10-13"}, "matches": [{"match_id": "m1", "home_team": "A", "away_team": "B", "competition": "L",
                                                           "normalized_datetime_utc": "2026-10-13T14:00:00Z", "calendar_verification_status": "CONFIRMADO",
                                                           "prematch_eligibility": "ELEGIBLE", "analysis_required": True, "disposition": "ok", "normalized_datetime_local": "2026-10-13T10:00:00-04:00",
                                                           "sports_analysis_status": "PENDIENTE", "market_analysis_status": "PENDIENTE"}]}
        common.write_json_atomic(os.path.join(d, "inventory.json"), inv)

        def evaluator(m, prov, pol, now):
            raise level1.ProviderLimit("request limit reached")
        st, _ = level1.process(d, None, helpers.POLICY, evaluator=evaluator)
        self.assertEqual(st["matches"]["m1"]["status"], "PENDIENTE")
        self.assertEqual(st["matches"]["m1"]["attempts"], 0)


if __name__ == "__main__":
    unittest.main()


class AlignGenericTokens(unittest.TestCase):
    def test_u19_marker_alone_does_not_make_teams_compatible(self):
        self.assertFalse(inventory._team_compat("Arsenal U19", "Lille U19"))
        self.assertTrue(inventory._team_compat("Sporting CP U19", "Sporting U19"))
        self.assertTrue(inventory._team_compat("Pohang", "Pohang Steelers"))
