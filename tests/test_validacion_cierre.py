"""Recalibración fuera de tiempo, cuotas de cierre de TheStatsAPI y auditoría de filtros. Datos FICTICIOS: EJEMPLO — NO REAL."""
import json
import os
import random
import tempfile
import unittest

import numpy as np

import helpers  # noqa: F401  (añade scripts/ al path)
import auditoria_filtros as af
import model_calibration as mcal
import tsa_history as th


class Calibracion(unittest.TestCase):
    def test_grupos_de_las_claves_del_modelo(self):
        g = mcal.group_of_key
        self.assertEqual((g("over_2.5"), g("btts"), g("p1"), g("x2"), g("home_over_0.5"), g("corners_total_over_9.5"), g("cards_total_over_3.5")),
                         ("goals_total", "btts", "1x2", "dc", "team_goals", "corners_total", "cards_total"))
        self.assertIsNone(g("ah_home_-1.5"))
        self.assertIsNone(g("dnb_home"))

    def test_platt_recupera_una_sobreconfianza_conocida(self):
        rnd = np.random.default_rng(1)
        p = rnd.uniform(0.05, 0.95, 20000)
        y = (rnd.uniform(size=p.size) < mcal.sigmoid(0.6 * mcal.logit(p))).astype(int)      # el modelo exagera: la verdad es más moderada
        a, b = mcal.fit_platt(p, y)
        self.assertAlmostEqual(a, 0.6, delta=0.06)
        self.assertAlmostEqual(b, 0.0, delta=0.06)

    def _preds(self, a_true, n=20000, seed=3):
        rnd = random.Random(seed)
        out = []
        for i in range(n):
            p = rnd.uniform(0.1, 0.9)
            q = float(mcal.sigmoid(a_true * mcal.logit(p)))
            out.append({"fecha": f"2026-0{1 + i * 8 // n}-15", "partido": f"m{i}", "familia": "goals_total", "p": p, "y": int(rnd.random() < q)})
        return out

    def test_se_aplica_solo_si_mejora_fuera_de_tiempo(self):
        mal = mcal.fit_groups(self._preds(0.6))["goals_total"]
        self.assertTrue(mal["aplicar"])
        self.assertLess(mal["brier_test_calibrada"], mal["brier_test_bruta"])
        bien = mcal.fit_groups(self._preds(1.0))["goals_total"]
        self.assertFalse(bien["aplicar"])             # ya calibrado: no hay mejora concluyente, se deja igual

    def test_apply_respeta_el_archivo_y_no_toca_lo_que_no_esta_aplicado(self):
        d = tempfile.mkdtemp()
        path = os.path.join(d, "cal.json")
        json.dump({"grupos": {"goals_total": {"aplicar": True, "a": 0.5, "b": 0.0}, "btts": {"aplicar": False, "a": 0.5, "b": 0.0}}}, open(path, "w"))
        p, g, ok = mcal.apply("over_2.5", 0.9, path)
        self.assertTrue(ok)
        self.assertLess(p, 0.9)
        self.assertEqual(mcal.apply("btts", 0.9, path), (0.9, "btts", False))
        self.assertEqual(mcal.apply("ah_home_-1.5", 0.9, path), (0.9, None, False))
        self.assertEqual(mcal.apply("over_2.5", 0.9, os.path.join(d, "no_existe.json")), (0.9, "goals_total", False))


def respuesta(books):
    return {"data": {"bookmakers": [{"bookmaker": n, "markets": m} for n, m in books]}}


def leaf(o):
    return {"opening": str(o), "last_seen": str(o)}


class CierreTsa(unittest.TestCase):
    def test_probabilidades_sin_margen_mediana_entre_casas_y_filtro_de_margen_absurdo(self):
        m1 = {"match_odds": {"home": leaf(2.0), "draw": leaf(3.5), "away": leaf(4.0)}, "total_goals": {"2.5": {"over": leaf(1.9), "under": leaf(1.95)}}}
        m2 = {"match_odds": {"home": leaf(2.1), "draw": leaf(3.4), "away": leaf(3.8)}, "total_goals": {"2.5": {"over": leaf(1.85), "under": leaf(2.0)}}}
        m3 = {"total_goals": {"2.5": {"over": leaf(1.01), "under": leaf(1.01)}}}          # margen absurdo (suma > 1.25): se descarta
        ex = th.extract(respuesta([("A", m1), ("B", m2), ("C", m3)]))
        self.assertAlmostEqual(sum(ex["1x2"]["p"]), 1.0, places=3)
        self.assertEqual(ex["1x2"]["n"], 2)
        self.assertEqual(ex["goles"]["2.5"]["n"], 2)
        self.assertTrue(0.45 < ex["goles"]["2.5"]["p"] < 0.55)

    def test_emparejamiento_por_fecha_equipos_con_su_orientacion_y_marcador(self):
        sample = {"L": {"r1": {"id": "r1", "fecha": "2026-09-26", "local": "Rotherham", "visitante": "Crewe Alexandra", "gl": 2, "gv": 1}}}
        tsa = [{"id": "mt_1", "status": "finished", "odds_available": True, "utc_date": "2026-09-26T14:00:00Z", "home_team": {"name": "Rotherham United"}, "away_team": {"name": "Crewe Alexandra"},
                "score": {"regulation": {"home": 2, "away": 1}}}]
        ok, amb = th.pair_rows(sample, tsa)
        self.assertEqual(ok["r1"][1]["id"], "mt_1")
        tsa[0]["score"]["regulation"] = {"home": 1, "away": 1}          # otro partido con los mismos equipos (ida/vuelta): no se empareja
        self.assertEqual(th.pair_rows(sample, tsa)[0], {})
        tsa[0]["score"]["regulation"] = {"home": 2, "away": 1}
        tsa[0]["home_team"], tsa[0]["away_team"] = {"name": "Crewe Alexandra"}, {"name": "Rotherham United"}      # orientación invertida
        self.assertEqual(th.pair_rows(sample, tsa)[0], {})


class AuditoriaFiltros(unittest.TestCase):
    def fila(self, i, res, p=0.7, cuota=1.5, ag="aprobada", partido="m"):
        return {"run": "r", "dia": "2026-10-14", "leg_id": f"{partido}{i}|x", "partido_id": f"{partido}{i}", "grupo": "goles", "p": p, "cuota": cuota, "precio_tipo": "referencia", "agentes": ag, "elegible": True, "res": res}

    def test_solo_cuentan_las_patas_liquidadas_del_lado_favorecido_con_cuota_valida(self):
        d = tempfile.mkdtemp()
        path = os.path.join(d, "l.jsonl")
        rows = [self.fila(1, "GANADA"), self.fila(2, "PERDIDA"), self.fila(3, "ANULADA"), self.fila(4, "GANADA", p=0.4), self.fila(5, "GANADA", cuota=2.5), self.fila(6, "GANADA (½)")]
        open(path, "w").write("\n".join(json.dumps(r) for r in rows))
        out = af.load(path)
        self.assertEqual(sorted(r["leg_id"][:2] for r in out), ["m1", "m2", "m6"])

    def test_un_filtro_que_separa_se_detecta_y_con_poca_muestra_no_se_concluye(self):
        rnd = random.Random(5)
        rows = [self.fila(i, "GANADA" if rnd.random() < 0.9 else "PERDIDA", ag="aprobada") for i in range(300)] + [self.fila(1000 + i, "GANADA" if rnd.random() < 0.5 else "PERDIDA", ag="degradada:deportivo:BAJA") for i in range(300)]
        for r in rows:
            r["y"] = 1 if r["res"].startswith("GANADA") else 0
        res = {x["filtro"]: x for x in af.report(rows)}
        self.assertEqual(res["Agentes: no degradada por el deportivo (BAJA)"]["veredicto"], "útil (separa)")
        pocos = af.report(rows[:20])
        self.assertTrue(all(x["veredicto"] == "muestra insuficiente" for x in pocos))


if __name__ == "__main__":
    unittest.main()
