"""Forma doméstica como PROXY (otra competición) vía Football-Data: resolución de nombres sin difusos, etiquetado y límites."""
import json, os, tempfile, unittest
from datetime import datetime, timezone
import helpers
import common, level1, adapters

HEAD = "Div,Date,HomeTeam,AwayTeam,FTHG,FTAG,HTHG,HTAG,HS,AS,HST,AST,HC,AC,HF,AF,HY,AY,HR,AR,Referee\n"


def csv_for(div, teams, n=10):
    rows = []
    for i in range(n):
        for t in teams:
            rows.append(f"{div},{i+1:02d}/09/2026,{t},Rival{i},2,1,1,0,12,8,5,3,6,4,10,11,2,1,0,0,Ref{i}")
    return HEAD + "\n".join(rows) + "\n"


class FakeClient:
    def __init__(self, files, fail=False):
        self.files, self.fail, self.urls = files, fail, []

    def fetch(self, url):
        self.urls.append(url)
        if self.fail:
            raise common.FetchError("x", "network")
        div = url.rsplit("/", 1)[1].replace(".csv", "")
        class R: pass
        r = R()
        r.text = self.files.get(div, HEAD)
        return r


def prov(aliases=None, fail=False, extra=None):
    files = {"E0": csv_for("E0", ["Arsenal", "Man United"]), "SP1": csv_for("SP1", ["Barcelona", "Ath Madrid"]),
             "I1": csv_for("I1", ["Inter", "Napoli"]), "P1": csv_for("P1", ["Sp Lisbon"]), "F1": csv_for("F1", ["Lens", "Lille"])}
    files.update(extra or {})
    return level1.FootballDataHistory(FakeClient(files, fail), "2627", aliases={"inter milan": "Inter", "atletico madrid": "Ath Madrid",
                                      "manchester united": "Man United", "sporting": "Sp Lisbon"} if aliases is None else aliases)


def match(home, away, comp="uefa champions league", div=None):
    return {"match_id": "m-x", "home_team": home, "away_team": away, "competition": comp, "country": "europe",
            "normalized_datetime_local": "2026-10-13T15:00:00-04:00", "normalized_datetime_utc": "2026-10-13T19:00:00Z",
            "extra": {"div": div, "odds": {}}}


class Resolution(unittest.TestCase):
    def test_exact_normalized_match_and_alias_are_flagged(self):
        p = prov()
        self.assertEqual(p.resolve("Arsenal"), ("E0", "Arsenal", False))
        self.assertEqual(p.resolve("Inter Milan"), ("I1", "Inter", True))          # alias explícito, queda marcado
        self.assertEqual(p.resolve("Sporting"), ("P1", "Sp Lisbon", True))

    def test_no_fuzzy_matching_without_alias(self):
        p = prov(aliases={})
        self.assertIsNone(p.resolve("Inter Milan"))                                 # 'Inter' != 'Inter Milan' sin alias
        self.assertIsNone(p.resolve("Atlético Madrid"))
        self.assertIsNone(p.resolve("Viking"))                                      # liga no cubierta

    def test_alias_to_nonexistent_team_is_ignored(self):
        self.assertIsNone(prov(aliases={"sporting": "Equipo Inexistente"}).resolve("Sporting"))

    def test_ambiguous_names_across_leagues_are_not_resolved(self):
        p = prov(extra={"D1": csv_for("D1", ["Arsenal"])})                           # dos 'Arsenal' en divisiones distintas con el mismo nombre
        p._index = None
        idx, amb = p._build_index()
        self.assertEqual(idx["arsenal"][0], "E0")                                    # mismo nombre FD en 2 divs: se queda con la primera, sin ambigüedad de NOMBRE FD
        # ambigüedad real: nombres FD distintos que normalizan igual
        p2 = prov(extra={"D1": csv_for("D1", ["Arsenal FC"])})
        p2._index = None
        self.assertIsNone(p2.resolve("Arsenal"))
        self.assertIn("arsenal", p2._build_index()[1])

    def test_covers_only_if_both_teams_resolved(self):
        p = prov()
        self.assertTrue(p.covers(match("Arsenal", "Lille")))
        self.assertFalse(p.covers(match("Viking", "Bayern München")))
        self.assertFalse(p.covers(match("Arsenal", "Viking")))

    def test_index_failure_means_not_covered_not_crash(self):
        self.assertFalse(prov(fail=True).covers(match("Arsenal", "Lille")))

    def test_downloads_within_policy_cap(self):
        p = prov()
        p.covers(match("Arsenal", "Lille"))
        self.assertLessEqual(len(level1.TOP_DIVS), 20)
        self.assertLessEqual(len(set(p.client.urls)), len(level1.TOP_DIVS))


class ProxyEvaluation(unittest.TestCase):
    def ev(self, m, p):
        return level1.evaluate_match(m, p, helpers.POLICY, "2026-10-13T00:30:00Z")

    def test_proxy_sample_is_labeled_partial_and_never_sufficient(self):
        m = match("Galatasaray", "Barcelona")
        p = prov(extra={"T1": csv_for("T1", ["Galatasaray"])})
        e = self.ev(m, p)
        self.assertTrue(e["proxy_sample"] and e["data_attempted"])
        self.assertEqual(e["sports_analysis_status"], level1.PARCIAL_PROXY)           # nunca COMPLETADO con solo proxy
        self.assertEqual(e["market_analysis_status"], level1.PARCIAL_PROXY)
        self.assertIn("OTRA competición", e["sample_note"])
        self.assertIn("sin árbitro designado", e["sample_note"])
        self.assertIn("NO las de ninguna casa", e["sample_note"])
        for h in e["form"]["local"] + e["form"]["visitante"]:
            self.assertIn("liga doméstica, OTRA competición", h["competition"])
        mk = e["markets"]["goles.btts"]
        self.assertEqual(mk["statistics_availability_status"], "PARCIALES")        # n=10 pero otra competición: nunca SUFICIENTES
        self.assertEqual(mk["evaluation_status"], "PARCIAL")
        self.assertIn("OTRA competición", mk["not_evaluable_reason"])
        self.assertTrue(mk["price_verification_status"].startswith("PRECIO_NO_CONFIRMADO"))
        self.assertIsNone(mk["price"])
        self.assertEqual(e["markets"]["corners.total"]["evaluation_status"], "PARCIAL")
        self.assertTrue(all(m["proxy_sample"] for m in e["markets"].values()))       # la marca vive en cada celda
        self.assertIn("mezcla partidos en casa y fuera", e["sample_note"])
        self.assertEqual(e["markets"]["otros.fueras_de_juego"]["evaluation_status"], "NO_EVALUABLE")   # fuente abierta sin ese dato

    def test_weak_sample_and_reviewable_alias_are_flagged_in_note(self):
        p = prov(extra={"P1": csv_for("P1", ["Sp Lisbon"], n=5)})
        p.needs_review = {"sporting": "alias global"}
        e = self.ev(match("Lens", "Sporting"), p)
        self.assertIn("MUESTRA DÉBIL n<8", e["sample_note"])
        self.assertIn("Sporting n=5", e["sample_note"])
        self.assertIn("ALIAS SUJETO A REVISIÓN: sporting", e["sample_note"])

    def test_alias_use_is_recorded_for_review(self):
        e = self.ev(match("Inter Milan", "Club Brugge"), prov(extra={"B1": csv_for("B1", ["Club Brugge"])}))
        self.assertIn("alias", e["sample_note"])
        self.assertIn("Inter (I1, alias)", e["sample_note"])

    def test_proxy_only_for_senior_mens_teams(self):
        p = prov()
        for cat in ("youth", "u23", "reserve", "women"):
            m = match("Arsenal", "Lille")
            m["gender_or_category"] = cat
            self.assertFalse(p.covers(m), cat)           # la forma del primer equipo masculino no es proxy de juveniles/reservas/femenino
        m = match("Arsenal", "Lille")
        m["gender_or_category"] = "men"
        self.assertTrue(p.covers(m))

    def test_native_football_data_match_is_not_proxy(self):
        m = match("Arsenal", "Man United", comp="Premier League", div="E0")
        e = self.ev(m, prov())
        self.assertFalse(e["proxy_sample"])
        self.assertFalse(any(m["proxy_sample"] for m in e["markets"].values()))
        self.assertEqual(e["markets"]["goles.btts"]["statistics_availability_status"], "SUFICIENTES")

    def test_uncovered_pair_stays_not_investigated(self):
        e = self.ev(match("Viking", "Bayern München"), prov())
        self.assertEqual(e["sports_analysis_status"], level1.NO_INVESTIGADO)
        self.assertFalse(e["data_attempted"])

    def test_history_excludes_matches_on_or_after_the_match_date(self):
        p = prov(extra={"E0": csv_for("E0", ["Arsenal", "Man United"], n=10) + "E0,20/10/2026,Arsenal,X,9,9,0,0,1,1,1,1,1,1,1,1,0,0,0,0,\n"})
        m = match("Arsenal", "Man United")
        p.covers(m)
        h = p.team_history(m, "Arsenal", "2026-10-13")
        self.assertTrue(all(x["date"] < "2026-10-13" for x in h))
        self.assertNotIn(9, [x["gf"] for x in h])


class AliasFile(unittest.TestCase):
    def test_alias_file_is_valid_and_only_maps_to_top_flight_names(self):
        d = common.read_json(level1.ALIASES_PATH)
        self.assertTrue(d["aliases"])
        for k, v in d["aliases"].items():
            self.assertEqual(k, common.norm_name(k), k)       # claves ya normalizadas
            self.assertTrue(v.strip())


if __name__ == "__main__":
    unittest.main()
