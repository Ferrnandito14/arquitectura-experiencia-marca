import json, os, tempfile, unittest
import helpers
from helpers import common


class Robots(unittest.TestCase):
    def test_fotmob_api_wildcard_disallow(self):
        rules = common.parse_robots("User-agent: *\nAllow: /\nDisallow: /api/*\nDisallow: /auth/*\n")
        self.assertFalse(common.robots_allows(rules, "/api/data/matches?date=1"))
        self.assertTrue(common.robots_allows(rules, "/matches?date=20261013"))

    def test_betexplorer_query_patterns(self):
        rules = common.parse_robots("User-agent: *\nDisallow: /*?year=\nDisallow: /*?month=\nAllow: /reviews/wp-admin/admin-ajax.php\n")
        self.assertFalse(common.robots_allows(rules, "/next/soccer/?year=2026&month=10&day=13"))
        self.assertTrue(common.robots_allows(rules, "/next/soccer/"))

    def test_longest_match_and_allow_wins_tie(self):
        rules = common.parse_robots("User-agent: *\nDisallow: /a\nAllow: /a/b\n")
        self.assertTrue(common.robots_allows(rules, "/a/b/c"))
        self.assertFalse(common.robots_allows(rules, "/a/x"))
        tie = common.parse_robots("User-agent: *\nDisallow: /p\nAllow: /p\n")
        self.assertTrue(common.robots_allows(tie, "/p"))

    def test_dollar_anchor_and_empty_disallow(self):
        self.assertFalse(common.robots_allows(common.parse_robots("User-agent: *\nDisallow: /*.pdf$\n"), "/x.pdf"))
        self.assertTrue(common.robots_allows(common.parse_robots("User-agent: *\nDisallow: /*.pdf$\n"), "/x.pdfx"))
        self.assertTrue(common.robots_allows(common.parse_robots("User-agent: *\nDisallow:\n"), "/cualquier/cosa"))

    def test_disallow_all(self):
        self.assertFalse(common.robots_allows(common.parse_robots("User-agent: *\nDisallow: /\n"), "/x"))

    def test_specific_agent_group_overrides_star(self):
        t = "User-agent: *\nDisallow: /\n\nUser-agent: football-picks-system\nAllow: /\n"
        self.assertTrue(common.robots_allows(common.parse_robots(t), "/x"))


class FakeNet:
    def __init__(self, script):
        self.script, self.calls, self.headers = list(script), [], []

    def __call__(self, url, headers, timeout):
        self.calls.append(url)
        self.headers.append(headers)
        r = self.script.pop(0) if self.script else (200, {}, b"ok")
        if isinstance(r, Exception):
            raise r
        return r


def client(net, tmp, **kw):
    sleeps = []
    c = common.Client(tmp, os.path.join(tmp, "log.jsonl"), policy=helpers.POLICY, opener=net, sleep=sleeps.append,
                      clock=iter(range(0, 10**6, 100)).__next__, min_interval=0, **kw)
    return c, sleeps


class ClientTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()

    def test_excluded_host_never_touches_network(self):
        net = FakeNet([])
        c, _ = client(net, self.tmp)
        with self.assertRaises(common.PolicyError) as cm:
            c.fetch("https://www.fotmob.com/api/data/matches?date=1")
        self.assertIn("EXCLUIDA", str(cm.exception))
        self.assertEqual(net.calls, [])

    def test_unreviewed_host_denied_by_default(self):
        net = FakeNet([])
        c, _ = client(net, self.tmp)
        with self.assertRaises(common.PolicyError):
            c.fetch("https://www.ejemplo-desconocido.com/")
        self.assertEqual(net.calls, [])

    def test_honest_user_agent_and_cache(self):
        net = FakeNet([(200, {}, b"User-agent: *\nAllow: /\n"), (200, {}, b"hola")])
        c, _ = client(net, self.tmp)
        r1 = c.fetch("https://www.football-data.co.uk/fixtures.csv")
        r2 = c.fetch("https://www.football-data.co.uk/fixtures.csv")
        self.assertEqual((r1.text, r1.from_cache, r2.from_cache), ("hola", False, True))
        self.assertEqual(len(net.calls), 2)       # robots + 1 sola descarga (la 2.ª sale de caché)
        self.assertTrue(all(h["User-Agent"] == "football-picks-system/0.1" for h in net.headers))
        self.assertTrue(all("Cookie" not in h and "Authorization" not in h for h in net.headers))

    def test_robots_denied_path(self):
        net = FakeNet([(200, {}, b"User-agent: *\nDisallow: /fixtures\n")])
        c, _ = client(net, self.tmp)
        with self.assertRaises(common.PolicyError):
            c.fetch("https://www.football-data.co.uk/fixtures.csv")
        self.assertEqual(len(net.calls), 1)

    def test_robots_unreadable_is_not_permission(self):
        net = FakeNet([OSError("boom")])
        c, _ = client(net, self.tmp)
        with self.assertRaises(common.PolicyError):
            c.fetch("https://www.football-data.co.uk/fixtures.csv")

    def test_retry_after_respected_and_limited_retries(self):
        net = FakeNet([(200, {}, b""), (429, {"Retry-After": "7"}, b""), (429, {"Retry-After": "7"}, b""), (200, {}, b"fin")])
        c, sleeps = client(net, self.tmp)
        self.assertEqual(c.fetch("https://www.football-data.co.uk/a.csv").text, "fin")
        self.assertEqual(sleeps.count(7.0), 2)

    def test_gives_up_after_max_retries(self):
        net = FakeNet([(200, {}, b"")] + [(503, {}, b"")] * 10)
        c, _ = client(net, self.tmp, max_retries=2)
        with self.assertRaises(common.FetchError):
            c.fetch("https://www.football-data.co.uk/a.csv")
        self.assertEqual(len(net.calls), 1 + 3)   # robots + (1 intento + 2 reintentos)

    def test_exponential_backoff_on_network_errors(self):
        net = FakeNet([(200, {}, b""), OSError("x"), OSError("y"), (200, {}, b"ok")])
        c, sleeps = client(net, self.tmp, backoff=1.0)
        self.assertEqual(c.fetch("https://www.football-data.co.uk/a.csv").text, "ok")
        self.assertEqual([s for s in sleeps if s], [1.0, 2.0])

    def test_antibot_challenge_is_not_evaded(self):
        net = FakeNet([(200, {}, b""), (403, {}, b"<title>Just a moment...</title>")])
        c, _ = client(net, self.tmp)
        with self.assertRaises(common.FetchError) as cm:
            c.fetch("https://www.football-data.co.uk/a.csv")
        self.assertEqual(cm.exception.kind, "blocked")
        self.assertEqual(len(net.calls), 2)       # sin reintentos ni cambios de identidad

    def test_http_404_no_retry(self):
        net = FakeNet([(200, {}, b""), (404, {}, b"")])
        c, _ = client(net, self.tmp)
        with self.assertRaises(common.FetchError):
            c.fetch("https://www.football-data.co.uk/zz.csv")
        self.assertEqual(len(net.calls), 2)

    def test_log_has_no_sensitive_headers(self):
        net = FakeNet([(200, {"Set-Cookie": "a=b"}, b"x"), (200, {"Set-Cookie": "a=b"}, b"x")])
        c, _ = client(net, self.tmp)
        c.fetch("https://www.football-data.co.uk/a.csv")
        with open(os.path.join(self.tmp, "log.jsonl")) as f:
            log = f.read().lower()
        self.assertNotIn("cookie", log)
        self.assertNotIn("authorization", log)


class AtomicAndTime(unittest.TestCase):
    def test_atomic_write_survives_failure(self):
        d = tempfile.mkdtemp()
        p = os.path.join(d, "x.json")
        common.write_json_atomic(p, {"a": 1})
        class Bad:
            pass
        with self.assertRaises(TypeError):
            common.write_json_atomic(p, {"a": Bad()})
        with open(p) as f:
            self.assertEqual(json.load(f), {"a": 1})
        self.assertEqual([f for f in os.listdir(d) if f.startswith(".tmp-")], [])

    def test_caracas_window(self):
        s, e = common.window_for_local_date("2026-10-13", "America/Caracas")
        self.assertEqual((s.isoformat(), e.isoformat()), ("2026-10-13T04:00:00+00:00", "2026-10-14T04:00:00+00:00"))

    def test_bst_and_gmt_by_date(self):
        from datetime import datetime
        self.assertEqual(common.source_dt_to_utc(datetime(2026, 10, 13, 20, 0), "Europe/London").hour, 19)   # BST
        self.assertEqual(common.source_dt_to_utc(datetime(2026, 10, 30, 20, 0), "Europe/London").hour, 20)   # GMT
        self.assertEqual(common.source_dt_to_utc(datetime(2026, 10, 13, 20, 0), "America/New_York").hour, 0)  # EDT
        self.assertEqual(common.source_dt_to_utc(datetime(2026, 11, 2, 20, 0), "America/New_York").hour, 1)   # EST

    def test_utc_to_local(self):
        self.assertEqual(common.utc_to_local(helpers.utc("2026-10-13T00:00:00Z")).strftime("%Y-%m-%d %H:%M"), "2026-10-12 20:00")

    def test_norm_name(self):
        self.assertEqual(common.norm_name("São Paulo FC"), "sao paulo")
        self.assertEqual(common.norm_name("  Club Brugge KV "), "brugge kv")

    def test_days_to_query_covers_neighbours(self):
        self.assertEqual([d.isoformat() for d in common.days_to_query("2026-10-13")], ["2026-10-12", "2026-10-13", "2026-10-14"])


if __name__ == "__main__":
    unittest.main()


class Limits(unittest.TestCase):
    def test_per_provider_interval_and_download_cap(self):
        import copy
        pol = common.Policy(data=copy.deepcopy(helpers.POLICY.data))
        pol.data["providers"]["football-data"]["limits"] = {"min_interval": 3.0, "max_files_per_run": 2}
        tmp = tempfile.mkdtemp()
        net = FakeNet([(200, {}, b"")] + [(200, {}, b"x")] * 5)
        ticks = iter(range(0, 10**6, 1))           # el reloj avanza 1 s por consulta
        sleeps = []
        c = common.Client(tmp, None, policy=pol, opener=net, sleep=sleeps.append, clock=lambda: float(next(ticks)), min_interval=0)
        c.fetch("https://www.football-data.co.uk/a.csv")
        c.fetch("https://www.football-data.co.uk/b.csv")
        self.assertTrue(any(s >= 1.0 for s in sleeps))            # se esperó para respetar los 3 s
        with self.assertRaises(common.PolicyError) as cm:
            c.fetch("https://www.football-data.co.uk/c.csv")
        self.assertIn("tope", str(cm.exception))
        c.fetch("https://www.football-data.co.uk/a.csv")          # desde caché: no cuenta como descarga
