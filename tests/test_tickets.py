"""tickets.py: patas, ítems del mismo partido y búsqueda por multiplicador. Datos FICTICIOS: EJEMPLO — NO REAL."""
import os, unittest
import helpers
import tickets


def form(n, gf=2, ga=0, **kw):
    return [dict({"gf": gf, "ga": ga, "date": f"2026-09-{i + 1:02d}", "corners": (5, 4) if i % 2 else (7, 5), "yellow": (2, 2) if i % 2 else (3, 3), "red": (0, 0)}, **kw)
            for i in range(n)]


def avg(cuotas, n=5):
    return {"cuotas_medias": cuotas, "n_casas": n, "minmax": [[c, c] for c in cuotas], "casas": ["a"] * n}


def ev(kind="apifootball_misma_competicion", fh=None, fa=None, prices=None):
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
            self.assertTrue(4.0 <= t["cuota_combinada_conservadora"] <= 4.8)       # el rango se juzga con la cuota conservadora (pares −5 %)
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
        legs = tickets.legs_for_match(m, ev(prices={"resultado.doble_oportunidad": avg([1.25, 1.5, 3.0])}))
        self.assertTrue(legs and all(l["categoria"] == "u23" for l in legs))
        self.assertEqual(tickets.search(legs, 1.20, 1.28, 2, 0.5)[0], [])
        self.assertTrue(tickets.search(legs, 1.20, 1.28, 2, 0.5, exclude_categories=())[0])


class StatMarkets(unittest.TestCase):
    def _row(self, venue, corners, sot, cards):
        r = {"gf": 1, "ga": 1, "venue": venue, "date": "2026-09-01", "corners": corners, "yellow": (None, None), "red": (None, None), "shots": (None, None), "sot": sot,
             "fouls": (None, None), "cards_pts": cards, "referee": None}
        return r

    def test_ladder_has_total_and_team_lines_for_every_stat_market(self):
        labels = [a[3] for a in tickets.atoms(ev(), ("Alfa", "Beta"))]
        for needle in ("Más de 9.5 córners", "Alfa: más de 4.5 córners", "Beta: menos de 5.5 córners", "Más de 4.5 tarjetas (A=1, R=2)",
                       "Alfa: menos de 2.5 tarjetas (A=1, R=2)", "Más de 8.5 remates a puerta", "Beta: más de 3.5 remates a puerta", "Más de 24.5 remates totales"):
            self.assertIn(needle, labels)

    def test_team_line_uses_own_value_for_the_team_and_conceded_for_the_rival(self):
        fh = [self._row("local", (8, 2), (5, 1), (1, 1)) for _ in range(8)]     # Alfa en casa: 8 córners propios
        fa = [self._row("visitante", (7, 3), (2, 6), (2, 2)) for _ in range(8)]  # Beta fuera: concede 7
        legs = {l["seleccion"]: l for l in tickets.legs_for_match(mm(0), ev(fh=fh, fa=fa))}
        l = legs[f"{mm(0)['home_team']}: más de 6.5 córners"]
        self.assertEqual(l["frec"], [1.0, 1.0])                                  # local propio 8>6.5 y lo que concede Beta 7>6.5
        self.assertEqual(l["mercado"], "córners")

    def test_cards_zero_zero_is_missing_not_zero(self):
        self.assertIsNone(tickets._cards_tuple({"cards_pts": (0, 0), "yellow": (None, None), "red": (None, None)}))
        self.assertEqual(tickets._cards_tuple({"cards_pts": (2, 3)}), (2, 3))
        self.assertEqual(tickets._cards_tuple({"yellow": (1, 2), "red": (1, 0)}), (3, 2))   # filas antiguas: 1 + 2×roja

    def test_stat_legs_are_estimated_priced_and_family_is_the_market(self):
        fh = [self._row("local", (8, 2), (5, 1), (3, 3)) for _ in range(10)]
        fa = [self._row("visitante", (7, 3), (2, 6), (3, 3)) for _ in range(10)]
        legs = tickets.legs_for_match(mm(0), ev(fh=fh, fa=fa))
        c = [l for l in legs if l["mercado"] == "remates a puerta"]
        self.assertTrue(c)
        self.assertTrue(all(l["cuota_tipo"] in (None, "estimada_por_modelo") for l in c))
        self.assertEqual(tickets._family(c[0]), "remates a puerta")


class CandidateSlots(unittest.TestCase):
    def test_estimated_legs_do_not_displace_real_priced_ones(self):
        mk = lambda mid, c, ap, tipo: {"match_id": mid, "cuota": c, "cuota_cons": c, "apoyo": ap, "mismo_partido": False,
                                       "patas": [{"match_id": mid, "partido": f"P{mid}", "seleccion": f"S{c}{tipo}", "mercado": "goles", "cuota_tipo": tipo, "cuota_media": c, "n_casas": 6 if tipo != "estimada_por_modelo" else 0,
                                                  "prob_implicita_sin_margen": 0.5, "apoyo_conservador": ap}]}
        items = [mk("a", 1.2 + i / 100, 0.7, "estimada_por_modelo") for i in range(8)] + [mk("a", 2.0, 0.5, "promedio_de_mercado")] + [mk("b", 2.1, 0.5, "promedio_de_mercado")]
        res, _ = tickets.search(None, 4.0, 4.5, 3, 0.1, top=2, items_override=items, buffer=0.0)
        self.assertTrue(res)                                       # 2.0 × 2.1 = 4.2 existe aunque «a» tenga 8 patas estimadas con más apoyo


class ExcludeOnlyForTickets(unittest.TestCase):
    def test_excluded_match_stays_in_tops_but_not_in_tickets(self):
        import tempfile, json, common
        d = tempfile.mkdtemp()
        inv = {"matches": [dict(mm(i), analysis_required=True) for i in range(3)]}
        mx = {"matches": {f"m{i}": ev(prices={"resultado.doble_oportunidad": avg([1.25, 1.5, 3.0], n=6), "goles.over_1_5": avg([1.25, 4.0], n=6)}) for i in range(3)}}
        common.write_json_atomic(os.path.join(d, "inventory.json"), inv)
        common.write_json_atomic(os.path.join(d, "matrix.json"), mx)
        name = f"{mm(0)['home_team']} – {mm(0)['away_team']}"
        self.assertEqual(tickets.main(["--run", d, "--target", "seg:1.20:1.28:2:0.3", "--exclude-match", name]), 0)
        out = json.load(open(os.path.join(d, "tickets.json")))
        in_tickets = {l["partido"] for r in out["targets"] for t in r["tickets"] for it in t["items"] for l in it["patas"]}
        in_tops = {p["partido"] for p in out["top_picks"]["seguridad"]}
        self.assertNotIn(name, in_tickets)
        self.assertIn(name, in_tops)


class StaleSample(unittest.TestCase):
    def test_recent_count_and_gate(self):
        old = [dict(r, date="2026-06-20") for r in form(10)]
        self.assertEqual(tickets._n_recent(old, "2026-10-13T17:00:00Z"), 0)
        recent = [dict(r, date="2026-10-01") for r in form(10)]
        self.assertEqual(tickets._n_recent(recent, "2026-10-13T17:00:00Z"), 10)
        legs = tickets.legs_for_match(mm(0), ev(fh=old, fa=recent, prices={"resultado.doble_oportunidad": avg([1.25, 1.5, 3.0], n=6)}))
        self.assertTrue(all(min(l["n_recientes"]) == 0 for l in legs))
        self.assertEqual([i for i in tickets._items(legs, 0.0, require_calendar=True)], [])   # muestra antigua: fuera de tickets


class TimeAndExclusions(unittest.TestCase):
    def test_after_utc_and_exclude_match(self):
        legs = tickets.legs_for_match(mm(0), ev(prices={"resultado.doble_oportunidad": avg([1.25, 1.5, 3.0], n=6)}))
        for l in legs:
            l["inicio_utc"] = "2026-10-13T17:00:00Z"
        kept, info = tickets.filter_legs_time_and_matches(legs, "2026-10-13T18:00:00Z", [])
        self.assertEqual(kept, [])
        self.assertEqual(info["partidos_descartados_por_hora"], 1)
        kept, _ = tickets.filter_legs_time_and_matches(legs, "2026-10-13T16:00:00Z", [])
        self.assertTrue(kept)
        kept, info = tickets.filter_legs_time_and_matches(legs, None, [legs[0]["partido"]])
        self.assertEqual(kept, [])
        self.assertEqual(info["partidos_excluidos_manualmente"], [legs[0]["partido"]])


class Replacements(unittest.TestCase):
    def test_replacement_keeps_range_info_and_skips_taken_matches(self):
        mk = lambda mid, c, ap: {"match_id": mid, "cuota": c, "cuota_cons": c, "apoyo": ap, "mismo_partido": False,
                                 "patas": [{"partido": f"P{mid}", "seleccion": "S", "cuota_tipo": "promedio_de_mercado", "cuota_media": c}]}
        tk = {"cuota_combinada_conservadora": 4.2, "items": [mk("a", 1.5, 0.6), mk("b", 2.8, 0.2)]}
        singles = [mk("c", 1.45, 0.65), mk("d", 1.55, 0.6), mk("e", 1.5, 0.7)]
        out = tickets._replacements([tk], singles, 4.0, 4.8, {"e"})
        alts = out[0]["alternativas"]
        self.assertEqual(alts[0]["partido"], "Pc")                               # «e» está tomado por otro ticket
        self.assertAlmostEqual(alts[0]["nuevo_multiplicador"], round(4.2 / 1.5 * 1.45, 3))
        self.assertTrue(alts[0]["en_rango"])


class AuditRules(unittest.TestCase):
    """Reglas añadidas tras la revisión por lotes y la auditoría adversarial."""

    def test_two_book_prices_do_not_enter_tickets(self):
        legs = tickets.legs_for_match(mm(0), ev(prices={"resultado.doble_oportunidad": avg([1.25, 1.5, 3.0], n=3)}))
        self.assertEqual(tickets.search(legs, 1.20, 1.28, 2, 0.5)[0], [])           # 3 casas: sirve para rankings, no para tickets
        legs = tickets.legs_for_match(mm(0), ev(prices={"resultado.doble_oportunidad": avg([1.25, 1.5, 3.0], n=4)}))
        self.assertTrue(tickets.search(legs, 1.20, 1.28, 2, 0.5)[0])

    def test_no_draw_legs_excluded_from_tickets(self):
        legs = tickets.legs_for_match(mm(0), ev(prices={"resultado.doble_oportunidad": avg([1.5, 1.25, 3.0])}))
        self.assertTrue(any(l["seleccion"].startswith("Gana alguno") and l["cuota_media"] for l in legs))
        for it in tickets._items(legs, 0.0, require_calendar=True):
            self.assertFalse(any(l["seleccion"].startswith("Gana alguno") for l in it["patas"]))

    def test_team_floor_hides_weak_team(self):
        s = tickets._support(form(10, 2, 0), form(10, 2, 0), lambda h: True, lambda h: h["gf"] > 5)   # un equipo 10/10, el otro 0/10 → promedio 0.36 ≥ 0 pero mínimo ≈ 0
        self.assertIsNone(s) if s is None else self.assertLess(s["apoyo_min_equipo"], tickets.TEAM_FLOOR)


class PairRange(unittest.TestCase):
    def test_pair_range_uses_conservative_odds_for_ceiling(self):
        a = {"match_id": "m0", "mismo_partido": True, "cuota": 1.285, "cuota_cons": 1.22}
        b = {"match_id": "m1", "mismo_partido": False, "cuota": 1.285, "cuota_cons": 1.285}
        self.assertEqual(tickets._hi_odds(a), 1.22)       # el par encaja bajo el techo 1.28 aunque su producto medio lo supere
        self.assertEqual(tickets._hi_odds(b), 1.285)      # una pata suelta se juzga por su cuota media


class PairRules(unittest.TestCase):
    def tearDown(self):
        tickets.PAIR_RULES["vetados"], tickets.PAIR_RULES["notas"] = {}, {}

    def _legs(self):
        return tickets.legs_for_match(mm(0), ev(prices={"goles.over_1_5": avg([1.25, 4.0], n=6), "resultado.doble_oportunidad": avg([1.25, 1.5, 3.0], n=6),
                                                        "goles.over_2_5": avg([1.6, 2.3], n=6)}))

    def test_vetoed_pair_not_generated_and_note_attached(self):
        legs = self._legs()
        pairs = [i for i in tickets._items(legs, 0.0, require_calendar=True) if i["mismo_partido"]]
        self.assertTrue(pairs)
        a, b = pairs[0]["patas"]
        tickets.PAIR_RULES["vetados"][tickets._pair_key(a["partido"], [b["seleccion"], a["seleccion"]])] = {"partido": a["partido"], "selecciones": [a["seleccion"], b["seleccion"]]}
        after = [i for i in tickets._items(legs, 0.0, require_calendar=True) if i["mismo_partido"]]
        self.assertTrue(all({x["seleccion"] for x in i["patas"]} != {a["seleccion"], b["seleccion"]} for i in after))
        tickets.PAIR_RULES["vetados"] = {}
        tickets.PAIR_RULES["notas"][tickets._pair_key(a["partido"], [a["seleccion"], b["seleccion"]])] = {"veredicto": "V", "condicion": "C"}
        noted = [i for i in tickets._items(legs, 0.0, require_calendar=True) if i["mismo_partido"] and {x["seleccion"] for x in i["patas"]} == {a["seleccion"], b["seleccion"]}]
        self.assertIn("Reevaluación de agentes: V", noted[0]["justificacion"])


class PairNoEstimated(unittest.TestCase):
    def test_pair_never_includes_estimated_leg(self):
        legs = tickets.legs_for_match(mm(0), ev(prices={"goles.over_1_5": avg([1.25, 4.0], n=6), "resultado.doble_oportunidad": avg([1.25, 1.5, 3.0], n=6)}))
        for it in tickets._items(legs, 0.0, require_calendar=True):
            if it["mismo_partido"]:
                self.assertFalse(any(l.get("cuota_tipo") == "estimada_por_modelo" for l in it["patas"]))


class QualityGates(unittest.TestCase):
    def _run_dir(self, corrections, kind):
        import tempfile, common
        d = tempfile.mkdtemp()
        inv = {"matches": [dict(mm(0), analysis_required=True, competition="UEFA Champions League")]}
        mx = {"matches": {"m0": ev(kind=kind, prices={"goles.over_1_5": avg([1.25, 4.0], n=6), "resultado.doble_oportunidad": avg([1.25, 1.5, 3.0], n=6)})}}
        common.write_json_atomic(os.path.join(d, "inventory.json"), inv)
        common.write_json_atomic(os.path.join(d, "matrix.json"), mx)
        os.makedirs(os.path.join(d, "reviews_raw", "batch"))
        common.write_json_atomic(os.path.join(d, "reviews_raw", "batch", "b01_analista-cuantitativo.json"),
                                 {"agent": "analista-cuantitativo", "batch_id": "b01", "rows": [{"match_id": "m0", "review_status": "REVISADO", "corrections": corrections, "note": ""}]})
        return d

    def test_hard_flaw_blocks_only_the_affected_market(self):
        d = self._run_dir(["Tarjetas 0/3: ceros sospechosos"], "apifootball_misma_competicion")
        legs = tickets.collect_legs(d)
        kept, gated = tickets.apply_quality_gate(legs, d)
        self.assertTrue(gated and all(g["familia"] == "tarjetas" for g in gated))
        self.assertTrue(any(l["mercado"] == "goles" for l in kept))
        self.assertFalse(any(l["mercado"] == "tarjetas" for l in kept))

    def test_flaw_without_market_blocks_whole_match(self):
        d = self._run_dir(["denominador mayor que n: dato defectuoso"], "apifootball_misma_competicion")
        kept, gated = tickets.apply_quality_gate(tickets.collect_legs(d), d)
        self.assertEqual(kept, [])
        self.assertEqual(gated[0]["familia"], "todo el partido")

    def test_mixed_history_leaves_main_tickets_and_goes_to_champions_variant(self):
        import json
        d = self._run_dir([], "apifootball_historial_propio")
        self.assertEqual(tickets.main(["--run", d, "--champions", "--target", "seg:1.20:1.28:1:0.5"]), 0)
        out = json.load(open(os.path.join(d, "tickets.json")))
        self.assertEqual(out["targets"][0]["tickets"], [])                      # principal: historial mixto no entra
        self.assertTrue(out["excluidas_por_historial_mixto"] > 0)
        self.assertTrue(any(r["tickets"] for r in out["targets"] if r["name"] == "seguridad_champions"))


class NoAllEstimated(unittest.TestCase):
    def test_ticket_needs_one_real_priced_leg(self):
        legs = [l for l in tickets.legs_for_match(mm(0), ev(prices={})) if l.get("cuota_tipo") == "estimada_por_modelo"]
        self.assertTrue(legs)
        res, _ = tickets.search(legs, 1.0, 9.0, 3, 0.0, require_calendar=False)
        self.assertEqual(res, [])


class Vetoes(unittest.TestCase):
    def test_vetoed_leg_removed_with_reason(self):
        import tempfile, json, common
        legs = tickets.legs_for_match(mm(0), ev(prices={"resultado.doble_oportunidad": avg([1.15, 1.22, 3.0])}))
        d = tempfile.mkdtemp()
        p = os.path.join(d, "vetoes.json")
        common.write_json_atomic(p, [{"partido": "H0 – A0", "seleccion": "Gana alguno, sin empate (12)", "motivo": "prueba"}])
        out, removed = tickets.apply_vetoes(legs, p)
        self.assertEqual(len(removed), 1)
        self.assertFalse(any(l["seleccion"] == "Gana alguno, sin empate (12)" for l in out))
        self.assertEqual(removed[0]["motivo"], "prueba")
