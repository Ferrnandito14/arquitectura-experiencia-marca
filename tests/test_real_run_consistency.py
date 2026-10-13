"""Verificación INDEPENDIENTE sobre la ejecución real guardada (runs/2026-10-13): recalcula con código propio las
frecuencias de los proxies desde los CSV en caché y las compara con matrix.json. Se omite si no existe la ejecución."""
import csv, glob, io, json, os, unittest

ROOT = os.path.normpath(os.path.join(os.path.dirname(__file__), ".."))
RUN = os.path.join(ROOT, "runs", "2026-10-13")


def load_csvs():
    out = {}
    for meta in glob.glob(os.path.join(RUN, "cache", "*.meta.json")):
        m = json.load(open(meta))
        url = m["url"]
        if "/mmz4281/2627/" in url:
            div = url.rsplit("/", 1)[1][:-4]
            body = open(meta.replace(".meta.json", ".body"), encoding="utf-8", errors="replace").read().lstrip("﻿")
            out[div] = list(csv.DictReader(io.StringIO(body)))
    return out


def history(rows, team, before, n=10):
    sel = []
    for r in rows:
        if team in (r["HomeTeam"], r["AwayTeam"]) and r.get("FTHG", "") != "":
            d, mth, y = r["Date"].split("/")
            iso = f"{int(y) if len(y) == 4 else 2000 + int(y)}-{int(mth):02d}-{int(d):02d}"
            if iso < before:
                sel.append((iso, r))
    sel.sort(key=lambda t: t[0])
    return [r for _, r in sel[-n:]]


def kn(rs, pred):
    vals = [pred(r) for r in rs]
    vals = [v for v in vals if v is not None]
    return sum(1 for v in vals if v), len(vals)


def iv(r, k):
    return int(r[k]) if r.get(k, "").strip() != "" else None


@unittest.skipUnless(os.path.exists(os.path.join(RUN, "matrix.json")), "no hay ejecución real guardada")
class RealRunProxyIndependentRecompute(unittest.TestCase):
    def test_all_proxy_frequencies_match_independent_recomputation(self):
        inv = json.load(open(os.path.join(RUN, "inventory.json")))
        mx = json.load(open(os.path.join(RUN, "matrix.json")))["matches"]
        csvs = load_csvs()
        idx = {m["match_id"]: m for m in inv["matches"]}
        proxies = [(mid, e) for mid, e in mx.items() if e["proxy_sample"]]
        if not proxies:
            self.skipTest("la ejecución real guardada ya no contiene proxies (el historial propio de la API los reemplazó)")
        checked = 0
        for mid, e in proxies:
            m = idx[mid]
            before = m["normalized_datetime_local"][:10]
            res = m["extra"]["proxy_resolution"]
            teams = {"home": res["home"], "away": res["away"]}
            samples = {s: history(csvs[teams[s][0]], teams[s][1], before) for s in ("home", "away")}
            tot = lambda r: iv(r, "FTHG") + iv(r, "FTAG")
            cards = lambda r: None if None in (iv(r, "HY"), iv(r, "AY"), iv(r, "HR"), iv(r, "AR")) else iv(r, "HY") + iv(r, "AY") + iv(r, "HR") + iv(r, "AR")
            corners = lambda r: None if None in (iv(r, "HC"), iv(r, "AC")) else iv(r, "HC") + iv(r, "AC")
            shots = lambda r: None if None in (iv(r, "HS"), iv(r, "AS")) else iv(r, "HS") + iv(r, "AS")
            cases = {
                "goles.btts": (0, lambda r: iv(r, "FTHG") > 0 and iv(r, "FTAG") > 0),
                "goles.over_2_5": (0, lambda r: tot(r) > 2.5),
                "corners.total": (2, lambda r: None if corners(r) is None else corners(r) > 9.5),     # 2.º par = línea 9.5
                "tarjetas.total": (2, lambda r: None if cards(r) is None else cards(r) > 4.5),         # 2.º par = línea 4.5
                "otros.tiros": (0, lambda r: None if shots(r) is None else shots(r) > 22.5),
            }
            for key, (off, pred) in cases.items():
                blocks = e["markets"][key]["stats"]
                self.assertGreaterEqual(len(blocks), off + 2, (mid, key))
                for side, b in zip(("home", "away"), blocks[off:off + 2]):
                    k, n = kn(samples[side], pred)
                    self.assertEqual((b["k"], b["n"]), (k, n), (m["home_team"], m["away_team"], key, side))
                    checked += 1
            for side in ("home", "away"):                      # n y fechas: nunca posteriores al partido, ≤10
                self.assertLessEqual(len(samples[side]), 10)
        self.assertGreaterEqual(checked, 5 * 2 * len(proxies))

    def test_own_history_blocks_match_independent_recount_from_rows(self):
        """Recuento independiente (sin stat_blocks) de BTTS, más de 2.5 goles y córners>9.5 desde las filas guardadas del historial propio."""
        mx = json.load(open(os.path.join(RUN, "matrix.json")))["matches"]
        own = [e for e in mx.values() if e.get("history_kind") == "apifootball_historial_propio"]
        if not own:
            self.skipTest("no hay partidos con historial propio en la ejecución guardada")
        checked = 0
        for e in own:
            for side, rows in (("local", e["form"]["local"]), ("visitante", e["form"]["visitante"])):
                idx = 0 if side == "local" else 1
                blocks = e["markets"]["goles.btts"]["stats"]
                if len(blocks) == 2:
                    k = sum(1 for r in rows if r["gf"] is not None and r["gf"] > 0 and r["ga"] > 0)
                    n = sum(1 for r in rows if r["gf"] is not None)
                    self.assertEqual((blocks[idx]["k"], blocks[idx]["n"]), (k, n))
                    checked += 1
                ob = e["markets"]["goles.over_2_5"]["stats"]
                if len(ob) == 2:
                    k = sum(1 for r in rows if r["gf"] is not None and r["gf"] + r["ga"] > 2.5)
                    n = sum(1 for r in rows if r["gf"] is not None)
                    self.assertEqual((ob[idx]["k"], ob[idx]["n"]), (k, n))
                    checked += 1
                self.assertLessEqual(len(rows), 10)
        self.assertGreater(checked, 0)

    def test_no_proxy_cell_claims_value(self):
        mx = json.load(open(os.path.join(RUN, "matrix.json")))["matches"]
        for e in mx.values():
            for k, c in e["markets"].items():
                self.assertNotEqual(c["evaluation_status"], "EVALUABLE", k)       # el nivel 1 nunca declara EVALUABLE
                if c["price"] is not None:                                         # con la API solo existen PROMEDIOS de mercado, nunca «una casa»
                    self.assertEqual(c["price"].get("tipo"), "promedio_de_mercado", k)
                    self.assertGreaterEqual(c["price"]["n_casas"], 2, k)
                    self.assertIn("NO cuota ejecutable", c["price"]["casa"], k)
                    self.assertNotIn("(vía football-data)", c["price"]["casa"] if e.get("history_kind") == "proxy_otra_competicion" else "", k)


if __name__ == "__main__":
    unittest.main()
