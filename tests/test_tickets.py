"""tickets.py: patas, ítems del mismo partido y búsqueda por multiplicador. Datos FICTICIOS: EJEMPLO — NO REAL."""
import os, unittest
import helpers
import tickets


def form(n, gf=2, ga=0, **kw):
    return [dict({"gf": gf, "ga": ga, "date": f"2026-09-{i + 1:02d}", "corners": (5, 4) if i % 2 else (7, 5), "yellow": (2, 2) if i % 2 else (3, 3), "red": (0, 0)}, **kw)
            for i in range(n)]


def avg(cuotas, n=5):
    return {"cuotas_medias": cuotas, "n_casas": n, "minmax": [[c, c] for c in cuotas], "casas": ["a"] * n}


def ev(kind="apifootball_historial_propio", fh=None, fa=None, prices=None):
    return {"history_kind": kind, "form": {"local": fh or form(8), "visitante": fa or form(8, 0, 2)}, "markets": {}, "api_prices": prices or {}}


def mm(i):
    return {"match_id": f"m{i}", "home_team": f"H{i}", "away_team": f"A{i}", "competition": "Liga", "normalized_datetime_utc": "2026-10-13T18:00:00Z",
            "selection_calendar_verification": "SUFICIENTE"}


class Legs(unittest.TestCase):
    def test_proxy_never_produces_legs(self):
        self.assertEqual(tickets.legs_for_match(mm(1), ev(kind="proxy_otra_competicion", prices={"resultado.1x2": avg([1.5, 4, 6])})), [])

    def test_all_market_families_evaluated(self):
        legs = tickets.legs_for_match(mm(1), ev())
        fams = {l["mercado"] for l in legs}
        self.assertTrue({"resultado", "doble oportunidad", "hándicap", "goles", "córners", "tarjetas"} <= fams, fams)
        self.assertTrue(any("5.5 goles" in l["seleccion"] for l in legs))

    def test_price_needs_min_books_and_range(self):
        legs = tickets.legs_for_match(mm(1), ev(prices={"resultado.1x2": avg([1.5, 4, 6], n=2)}))
        self.assertTrue(all(l["cuota_media"] is None for l in legs if l["mercado"] in ("resultado", "doble oportunidad", "goles", "hándicap")))
        legs = tickets.legs_for_match(mm(1), ev(prices={"resultado.1x2": avg([1.5, 4, 6])}))
        priced = {l["seleccion"] for l in legs if l["cuota_media"] is not None}
        self.assertIn("Local gana (1)", priced)
        self.assertNotIn("Visitante gana (2)", priced)         # 6.0 fuera del rango de cuotas útiles

    def test_small_sample_no_legs(self):
        self.assertEqual(tickets.legs_for_match(mm(1), ev(fh=form(3))), [])

    def test_missing_corner_stats_excluded_not_zero(self):
        f = form(8, corners=(None, None))
        legs = tickets.legs_for_match(mm(1), ev(fh=f, fa=f))
        self.assertFalse(any(l["mercado"] == "córners" for l in legs))

    def test_corners_cards_get_labelled_estimated_odds_with_breakeven(self):
        legs = tickets.legs_for_match(mm(1), ev())
        un = tickets.unpriced(legs, min_support=0.0)
        self.assertTrue(un)
        for u in un:
            self.assertEqual(u["cuota_tipo"], "estimada_por_modelo")
            self.assertGreaterEqual(u["cuota_media"], 1.03)
            self.assertEqual(u["n_casas"], 0)
            self.assertGreaterEqual(u["cuota_equilibrio_minima"], 1)

    def test_estimated_odds_never_enter_attractiveness_ranking(self):
        tp = tickets.top_picks(tickets.legs_for_match(mm(1), ev(prices={"resultado.doble_oportunidad": avg([1.45, 1.5, 3.0])})), top=20)
        self.assertTrue(all(p["cuota_tipo"] != "estimada_por_modelo" for p in tp["atractivo"]))

    def test_manual_odds_override(self):
        import tempfile
        legs = tickets.legs_for_match(mm(1), ev())
        d = tempfile.mkdtemp()
        p = os.path.join(d, "o.csv")
        with open(p, "w", encoding="utf-8") as f:
            f.write("home,away,seleccion,cuota\nH1,A1,Más de 9.5 córners,1.77\n")
        self.assertEqual(tickets.apply_manual_odds(legs, p), 1)
        l = [x for x in legs if x["seleccion"] == "Más de 9.5 córners"][0]
        self.assertEqual((l["cuota_media"], l["cuota_tipo"]), (1.77, "manual_usuario"))


class Search(unittest.TestCase):
    def _legs(self, specs, dc=(1.15, 1.2, 4.0)):
        out = []
        for i, (odds_u, odds_o) in enumerate(specs):
            e = ev(prices={"goles.over_5_5": avg([odds_o, odds_u]), "resultado.doble_oportunidad": avg(list(dc))})
            out += tickets.legs_for_match(mm(i), e)
        return out

    def test_safety_target_can_use_two_legs_of_same_match(self):
        legs = self._legs([(1.1, 8.0)])
        res, _ = tickets.search(legs, 1.20, 1.28, 2, 0.5, top=5)
        self.assertTrue(res)
        t = res[0]
        self.assertTrue(1.20 <= t["cuota_combinada_media"] <= 1.28)
        self.assertTrue(any(it["mismo_partido"] for it in t["items"]) or t["n_patas"] == 1)

    def test_same_match_pair_support_is_joint_not_product(self):
        legs = tickets.legs_for_match(mm(0), ev(fh=form(8, 3, 0), fa=form(8, 0, 3), prices={
            "resultado.doble_oportunidad": avg([1.15, 1.2, 4.0]), "goles.over_2_5": avg([1.4, 3.0])}))
        items = tickets._items(legs, 0.0)
        pairs = [i for i in items if i["mismo_partido"]]
        self.assertTrue(pairs)
        for p in pairs:
            self.assertLessEqual(p["apoyo"], min(l["apoyo_conservador"] for l in p["patas"]) + 1e-9)    # conjunto ≤ cada pata

    def test_wide_target_distinct_matches_in_range(self):
        legs = self._legs([(1.3, 4.0)] * 8, dc=(1.45, 1.5, 3.0))
        res, _ = tickets.search(legs, 4.0, 4.8, 6, 0.3, top=5)
        self.assertTrue(res)
        for t in res:
            self.assertTrue(4.0 <= t["cuota_combinada_media"] <= 4.8)
            ids = [it["match_id"] for it in t["items"]]
            self.assertEqual(len(ids), len(set(ids)))
            self.assertLessEqual(t["n_patas"], 6)

    def test_no_forced_ticket(self):
        legs = self._legs([(1.9, 1.9)])
        res, _ = tickets.search(legs, 9.0, 9.5, 2, 0.5)
        self.assertEqual(res, [])

    def test_uses_calc_not_own_math(self):
        with open(os.path.join(helpers.SCRIPTS, "tickets.py"), encoding="utf-8") as f:
            src = f.read()
        self.assertIn("calc.combo_odds", src)
        self.assertIn("calc.wilson", src)


if __name__ == "__main__":
    unittest.main()


class Disjoint(unittest.TestCase):
    def _all(self, n=10):
        out = []
        for i in range(n):
            out += tickets.legs_for_match(mm(i), ev(prices={"goles.over_5_5": avg([4.0, 1.12]), "resultado.doble_oportunidad": avg([1.15, 1.22, 3.0]),
                                                           "goles.over_2_5": avg([1.5, 2.4])}))
        return out

    def test_exclude_removes_matches_from_search(self):
        legs = self._all()
        a, _ = tickets.search(legs, 1.20, 1.28, 2, 0.5, top=1)
        used = {it["match_id"] for it in a[0]["items"]}
        b, _ = tickets.search(legs, 1.20, 1.28, 2, 0.5, top=5, exclude=used)
        for t in b:
            self.assertFalse(used & {it["match_id"] for it in t["items"]})

    def test_main_principals_share_no_match(self):
        import tempfile, json, common
        d = tempfile.mkdtemp()
        inv = {"matches": [dict(mm(i), analysis_required=True) for i in range(10)]}
        mx = {"matches": {f"m{i}": ev(prices={"goles.over_5_5": avg([4.0, 1.12]), "resultado.doble_oportunidad": avg([1.15, 1.22, 3.0]),
                                              "goles.over_2_5": avg([1.5, 2.4])}) for i in range(10)}}
        common.write_json_atomic(os.path.join(d, "inventory.json"), inv)
        common.write_json_atomic(os.path.join(d, "matrix.json"), mx)
        self.assertEqual(tickets.main(["--run", d, "--target", "seg:1.20:1.28:2:0.5", "--target", "amp:4.0:4.8:6:0.3"]), 0)
        out = json.load(open(os.path.join(d, "tickets.json")))
        self.assertTrue(out["sin_partidos_repetidos_entre_perfiles"])
        a = {it["match_id"] for t in out["targets"][0]["tickets"] for it in t["items"]}
        b = {it["match_id"] for t in out["targets"][1]["tickets"] for it in t["items"]}
        self.assertFalse(a & b)             # CUALQUIER borrador del primer perfil es disjunto de CUALQUIER borrador del segundo
        self.assertGreaterEqual(len(out["targets"][0]["tickets"]), 2)      # varios borradores para escoger

    def test_same_match_pair_has_justification_and_is_allowed_in_wide(self):
        legs = tickets.legs_for_match(mm(0), ev(fh=form(8, 3, 0), fa=form(8, 0, 3), prices={
            "resultado.doble_oportunidad": avg([1.45, 1.5, 3.0]), "goles.over_2_5": avg([1.5, 2.4])}))
        items = [i for i in tickets._items(legs, 0.3) if i["mismo_partido"]]
        self.assertTrue(items)
        self.assertTrue(all(i["justificacion"] and "Conjunto medido" in i["justificacion"] for i in items))


class TopPicks(unittest.TestCase):
    def _legs(self):
        out = []
        for i in range(6):
            out += tickets.legs_for_match(mm(i), ev(prices={"goles.over_5_5": avg([4.0, 1.12 + i * 0.05]), "resultado.doble_oportunidad": avg([1.3 + i * 0.1, 1.5, 3.0]),
                                                           "goles.over_2_5": avg([1.5, 2.4])}))
        return out

    def test_two_rankings_one_pick_per_match_and_sorted(self):
        tp = tickets.top_picks(self._legs(), top=5)
        for k in ("seguridad", "atractivo"):
            ids = [p["match_id"] for p in tp[k]]
            self.assertEqual(len(ids), len(set(ids)))
            self.assertLessEqual(len(ids), 5)
        sup = [p["apoyo_conservador"] for p in tp["seguridad"]]
        self.assertEqual(sup, sorted(sup, reverse=True))
        ev_ = [p["ev_descriptivo_conservador"] for p in tp["atractivo"]]
        self.assertEqual(ev_, sorted(ev_, reverse=True))
        self.assertTrue(all(p["ev_descriptivo_conservador"] > 0 and p["apoyo_conservador"] >= 0.55 for p in tp["atractivo"]))

    def test_render_has_both_tables_and_disclaimer(self):
        import tempfile, common
        d = tempfile.mkdtemp()
        inv = {"matches": [dict(mm(i), analysis_required=True) for i in range(6)]}
        mx = {"matches": {f"m{i}": ev(prices={"goles.over_5_5": avg([4.0, 1.12]), "resultado.doble_oportunidad": avg([1.45, 1.5, 3.0])}) for i in range(6)}}
        common.write_json_atomic(os.path.join(d, "inventory.json"), inv)
        common.write_json_atomic(os.path.join(d, "matrix.json"), mx)
        tickets.main(["--run", d])
        with open(os.path.join(d, "tickets.md"), encoding="utf-8") as f:
            md = f.read()
        self.assertIn("Top de picks por SEGURIDAD", md)
        self.assertIn("Top de picks por ATRACTIVO", md)
        self.assertIn("NO es valor esperado real", md)


class CalendarRequirement(unittest.TestCase):
    def test_single_source_calendar_excluded_from_tickets_but_flagged(self):
        m = dict(mm(0), selection_calendar_verification="REQUIERE_VERIFICACION_ADICIONAL")
        legs = tickets.legs_for_match(m, ev(prices={"resultado.doble_oportunidad": avg([1.15, 1.22, 3.0])}))
        self.assertTrue(legs and not any(l["calendario_2_fuentes"] for l in legs))
        res, _ = tickets.search(legs, 1.20, 1.28, 2, 0.5)
        self.assertEqual(res, [])                                        # exige dos fuentes
        res2, _ = tickets.search(legs, 1.20, 1.28, 2, 0.5, require_calendar=False)
        self.assertTrue(res2)

    def test_diversity_between_drafts(self):
        legs = []
        for i in range(8):
            legs += tickets.legs_for_match(mm(i), ev(prices={"resultado.doble_oportunidad": avg([1.3, 1.4, 3.0])}))
        res, _ = tickets.search(legs, 4.0, 4.8, 6, 0.3, top=4)
        sets = [{it["match_id"] for it in t["items"]} for t in res]
        for i in range(len(sets)):
            for j in range(i):
                self.assertLessEqual(len(sets[i] & sets[j]) / min(len(sets[i]), len(sets[j])), tickets.MAX_OVERLAP)


class PairFamilies(unittest.TestCase):
    def test_no_pair_inside_same_family(self):
        legs = tickets.legs_for_match(mm(0), ev(fh=form(8, 3, 0), fa=form(8, 0, 3), prices={
            "goles.over_1_5": avg([1.1, 6.0]), "goles.over_2_5": avg([1.5, 2.4]), "resultado.doble_oportunidad": avg([1.15, 1.22, 3.0])}))
        for it in tickets._items(legs, 0.0):
            if it["mismo_partido"]:
                a, b = it["patas"]
                self.assertNotEqual(tickets._family(a), tickets._family(b), (a["seleccion"], b["seleccion"]))
        pairs = [it for it in tickets._items(legs, 0.0) if it["mismo_partido"]]
        self.assertTrue(any({tickets._family(p) for p in it["patas"]} == {"resultado", "goles_total"} for it in pairs))


class Categories(unittest.TestCase):
    def test_youth_excluded_from_tickets_by_default(self):
        m = dict(mm(0), gender_or_category="u23")
        legs = tickets.legs_for_match(m, ev(prices={"resultado.doble_oportunidad": avg([1.15, 1.22, 3.0])}))
        self.assertTrue(legs and all(l["categoria"] == "u23" for l in legs))
        self.assertEqual(tickets.search(legs, 1.20, 1.28, 2, 0.5)[0], [])
        self.assertTrue(tickets.search(legs, 1.20, 1.28, 2, 0.5, exclude_categories=())[0])
