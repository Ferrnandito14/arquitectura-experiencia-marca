"""Módulos añadidos tras la auditoría del 13-oct: muestras de liga, riesgo de rotación y calibración. Datos FICTICIOS: EJEMPLO — NO REAL."""
import os, sys, unittest
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".claude", "skills", "seleccion-final-picks", "scripts"))
import calibracion  # noqa: E402
import league_sample  # noqa: E402
import rotation_risk as rr  # noqa: E402


def row(i, gl, gv, tar=(2, 3), cor=(5, 4), ref="Árbitro X"):
    return {"id": str(i), "fecha": "2026-09-01", "local": "A", "visitante": "B" if i % 2 else "C", "gl": gl, "gv": gv, "tarjetas": list(tar) if tar else None, "corners": list(cor) if cor else None, "arbitro": ref}


class LeagueSample(unittest.TestCase):
    def test_summary_has_league_team_and_referee_blocks(self):
        rows = [row(i, 2, 1) for i in range(8)]
        r = league_sample.summarize(rows, min_ref=6)
        self.assertEqual(r["n_partidos"], 8)
        self.assertEqual(r["liga"]["goles"]["media"], 3.0)
        self.assertEqual(r["liga"]["goles"]["mas_2.5"], 1.0)
        self.assertIn("A", r["equipos"])
        self.assertIn("Árbitro X", r["arbitros"])

    def test_missing_cards_are_excluded_not_zero(self):
        rows = [row(i, 1, 1, tar=None) for i in range(6)] + [row(10, 1, 1, tar=(3, 3))]
        r = league_sample.summarize(rows)
        self.assertEqual(r["liga"]["tarjetas"]["n"], 1)

    def test_referee_with_few_matches_is_hidden(self):
        rows = [row(i, 1, 0, ref="R1") for i in range(3)]
        self.assertEqual(league_sample.summarize(rows, min_ref=6)["arbitros"], {})


class Rotation(unittest.TestCase):
    def test_overlap_and_levels(self):
        prev = [set("abcdefghijk"), set("abcdefghijl"), set("abcdefghijm"), set("abcdefghijn")]
        self.assertEqual(rr.overlap_with_habitual(set("abcdefghijk"), prev), 10)
        self.assertEqual(rr.real_risk(set("abcdefghijk"), prev)["nivel"], "bajo")
        self.assertEqual(rr.real_risk(set("abcdexyzuvw"), prev)["nivel"], "alto")        # 5/11 habituales (Bayern 13-oct)

    def test_change_rate(self):
        self.assertEqual(rr.change_rate([set("abc"), set("abd"), set("abd")]), 0.5)
        self.assertIsNone(rr.change_rate([set("abc")]))

    def test_prior_risk_and_penalty(self):
        r = rr.prior_risk(rest_days=3, euro_or_cup_soon=True, change_rate_prev=4.5)
        self.assertEqual(r["nivel"], "alto")
        self.assertEqual(rr.prior_risk(7, False, 1.0)["nivel"], "bajo")
        self.assertEqual(rr.penalty_for_leg("alto", "under", False), "veto")
        self.assertEqual(rr.penalty_for_leg("medio", None, True), "rebajar")
        self.assertIsNone(rr.penalty_for_leg("bajo", "under", False))


class Calibracion(unittest.TestCase):
    def test_brier_roi_and_min_n_rule(self):
        rows = [{"origen": "sistema", "mercado": "total U4.5", "cuota": 1.25, "p_mercado_sin_margen_aprox": 0.75, "resultado": "FALLADA"},
                {"origen": "sistema", "mercado": "total O1.5", "cuota": 1.25, "p_mercado_sin_margen_aprox": 0.75, "resultado": "ACERTADA"},
                {"origen": "sistema", "mercado": "hándicap Brugge +2.5", "cuota": 1.55, "p_mercado_sin_margen_aprox": 0.65, "resultado": "ACERTADA"}]
        r = calibracion.evaluate(rows)
        self.assertEqual(r["n"], 3)
        self.assertEqual(r["aciertos_reales"], 2)
        self.assertAlmostEqual(r["aciertos_esperados"], 2.15, places=2)
        self.assertTrue(all(g["accion"].startswith("sin base") for g in r["grupos"].values()))      # n<30: no se concluye
        self.assertEqual(r["grupos"]["direccion:under"]["aciertos"], 0)

    def test_freeze_rule_needs_n30_and_negative_roi(self):
        rows = [{"origen": "sistema", "mercado": "total U2.5", "cuota": 1.5, "p_mercado_sin_margen_aprox": 0.6, "resultado": "FALLADA" if i % 3 else "ACERTADA"} for i in range(30)]
        g = calibracion.evaluate(rows)["grupos"]["direccion:under"]
        self.assertEqual(g["n"], 30)
        self.assertEqual(g["accion"], "CONGELAR tipo")

    def test_pending_results_are_ignored(self):
        self.assertEqual(calibracion.evaluate([{"mercado": "total U2.5", "cuota": 1.5, "p_mercado_sin_margen_aprox": 0.6, "resultado": "EN_JUEGO"}])["n"], 0)


if __name__ == "__main__":
    unittest.main()


class Snapshots(unittest.TestCase):
    def test_snapshot_lines_are_appended_with_declared_probabilities(self):
        import json, tempfile, tickets
        tk = {"cuota_combinada_media": 1.25, "cuota_combinada_conservadora": 1.2, "p_mercado_conjunta": 0.8, "p_central_conjunta": 0.78, "ev_mercado": -0.11, "ev_central": -0.12,
              "max_brecha_muestra_mercado": 0.2, "etiqueta_riesgo": "BAJO RIESGO (EV<0)", "direcciones": {"under": 1, "over": 0},
              "items": [{"patas": [{"partido": "A – B", "seleccion": "Menos de 4.5 goles", "cuota_media": 1.25, "cuota_tipo": "promedio_de_mercado", "prob_implicita_sin_margen": 0.8, "frec": [1.0, 0.9], "n": [10, 10], "inicio_utc": "2026-10-13T18:45:00Z"}]}]}
        out = {"targets": [{"name": "seguridad", "tickets": [tk]}], "patas_vetadas": [{"partido": "X – Y"}]}
        with tempfile.TemporaryDirectory() as d:
            self.assertEqual(tickets.write_snapshots(d, out, "2026-10-13T16:00:00Z"), 1)
            self.assertEqual(tickets.write_snapshots(d, out, "2026-10-13T17:00:00Z"), 1)
            lines = open(os.path.join(d, "snapshots.jsonl"), encoding="utf-8").read().strip().splitlines()
            self.assertEqual(len(lines), 2)                      # se añade, no se sobrescribe
            r = json.loads(lines[0])
            self.assertEqual(r["p_mercado"], 0.8)
            self.assertEqual(r["n_vetos_vigentes"], 1)
            self.assertEqual(r["patas"][0]["seleccion"], "Menos de 4.5 goles")
