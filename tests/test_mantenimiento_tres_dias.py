"""Mantenimiento 14–16 oct: análisis fuera de muestra, CSV acumulativo, día de Caracas, tope por partido, independencia de la casa y auditor de libros. Datos FICTICIOS: EJEMPLO — NO REAL."""
import csv
import json
import os
import random
import tempfile
import unittest

import helpers  # noqa: F401  (añade scripts/ al path)
import acumulado as acu
import analisis_tres_dias as an
import auditoria_libros as aud
import catalog_rankings as cr
import comparativo_resultados as cmp
import price_sources as ps
from test_catalog_rankings import OVER, UNDER, entrada, unit

RUNS = an.RUNS


def fila(run, mid, i, p, y, grupo="goles", cuota=1.5, agentes="degradada:deportivo:BAJA"):
    return {"run": run, "dia": run[-10:], "dia_caracas": run[-10:], "leg_id": f"{mid}|e{i}", "entry_id": f"e{i}", "partido_id": mid, "partido": f"A{mid} – B{mid}", "grupo": grupo, "p": p, "cuota": cuota,
            "precio_tipo": "referencia", "agentes": agentes, "elegible": False, "res": "GANADA" if y else "PERDIDA", "y": 1 if y else 0, "hora_utc": run[-10:] + "T20:00:00Z", "observado_utc": None, "liga": "L"}


def sintetico(n_por_dia, sobreconfianza, seed=3):
    """3 días; la verdad es p_real y el modelo la declara con `sobreconfianza` (p_decl = p_real + sobreconfianza)."""
    rnd = random.Random(seed)
    rows = []
    for r in RUNS:
        for k in range(n_por_dia):
            real = rnd.uniform(0.5, 0.95)
            decl = min(0.99, real + sobreconfianza)
            rows.append(fila(r, f"{r[-2:]}{k // 2}", k, round(decl, 4), 1 if rnd.random() < real else 0, grupo=rnd.choice(["goles", "córners"])))
    return rows


class Recalibracion(unittest.TestCase):
    def test_isotonica_es_monotona_y_acotada(self):
        rnd = random.Random(1)
        p = [rnd.random() for _ in range(300)]
        y = [1 if rnd.random() < x else 0 for x in p]
        m = an.fit_iso(p, y)
        out = an.pred_iso(m, sorted(p))
        self.assertTrue(all(b >= a - 1e-12 for a, b in zip(out, out[1:])))
        self.assertTrue(0.01 <= out.min() and out.max() <= 0.99)

    def test_un_modelo_ya_calibrado_no_se_publica(self):
        res = an.recalib(sintetico(400, 0.0))
        self.assertFalse(res["publicar_alguno"])

    def test_una_sobreconfianza_grande_se_corrige_y_se_publica_solo_si_mejora_fuera_de_muestra(self):
        res = an.recalib(sintetico(900, 0.12))
        self.assertTrue(res["publicar"]["platt_global"] or res["publicar"]["isotonica_global"])
        e = res["agregado_fuera_de_muestra"]
        self.assertLess(e["platt_global"]["brier"], e["sin_ajuste"]["brier"])
        self.assertLess(e["platt_global"]["ece"], e["sin_ajuste"]["ece"])

    def test_el_ajuste_nunca_se_entrena_con_el_dia_que_evalua(self):
        rows = [r for r in sintetico(120, 0.1) if r["p"] >= 0.5]
        # el fold «14+15 → 16» se entrena solo con 14 y 15: si cambiamos los resultados del 16 las probabilidades ajustadas del 16 no se mueven
        tr = [r for r in rows if r["run"] != RUNS[2]]
        te = [r for r in rows if r["run"] == RUNS[2]]
        a = an.metodos(tr, [r["p"] for r in te], [r["grupo"] for r in te])
        for r in te:
            r["y"] = 1 - r["y"]
        b = an.metodos(tr, [r["p"] for r in te], [r["grupo"] for r in te])
        for k in a:
            self.assertTrue((a[k] == b[k]).all(), k)

    def test_solo_cuentan_ganadas_y_perdidas_de_los_tres_dias(self):
        with tempfile.TemporaryDirectory() as d:
            p = os.path.join(d, "l.jsonl")
            rows = [fila(RUNS[0], "m1", 1, 0.7, 1), fila(RUNS[0], "m1", 2, 0.7, 0), dict(fila(RUNS[0], "m1", 3, 0.7, 1), res="ANULADA"), dict(fila("runs/2026-10-17", "m9", 1, 0.7, 1))]
            open(p, "w").write("".join(json.dumps(r) + "\n" for r in rows))
            self.assertEqual(len(an.cargar(p)), 2)


class AgentesYPrecio(unittest.TestCase):
    def test_diferencia_no_distinguible_de_cero_se_avisa(self):
        rnd = random.Random(5)
        rows = []
        for i in range(120):
            etiqueta = "aprobada" if i % 2 else "degradada:deportivo:BAJA"
            rows.append(fila(RUNS[i % 3], f"m{i // 3}", i, 0.7, 1 if rnd.random() < 0.7 else 0, agentes=etiqueta))
        for r in rows:
            r["y"] = 1 if r["res"] == "GANADA" else 0
        out = an.agentes(rows)
        d = out["todas las patas con P≥50 %"]["diferencias"]["aprobada − degradada"]
        self.assertFalse(d["distinguible_de_cero"])
        self.assertTrue(d["ic95_pp"][0] < 0 < d["ic95_pp"][1])

    def test_clase_de_agentes(self):
        self.assertEqual(an.clase_agentes("rechazada:verificador:x"), "rechazada")
        self.assertEqual(an.clase_agentes("aprobada"), "aprobada")
        self.assertEqual(an.clase_agentes("???"), "otra")

    def test_discrepancia_de_10pp_separa_modelo_alto_y_bajo(self):
        rows = []
        for i in range(60):
            r = fila(RUNS[0], f"m{i}", i, 0.8, 1 if i % 2 else 0)
            r["y"] = 1 if r["res"] == "GANADA" else 0
            r["p_mercado"] = 0.6 if i < 30 else 0.95
            rows.append(r)
        out = an.precio(rows)["discrepancia_mayor_10pp"]
        self.assertEqual(out["n"], 60)
        self.assertEqual(out["modelo_mayor_que_mercado"]["n"], 30)
        self.assertEqual(out["modelo_menor_que_mercado"]["n"], 30)


class PreciosSinMargen(unittest.TestCase):
    def test_demargin_normaliza_y_suma_uno(self):
        p = ps.demargin([1.80, 2.10])
        self.assertAlmostEqual(sum(p), 1.0)
        self.assertAlmostEqual(p[0], (1 / 1.8) / (1 / 1.8 + 1 / 2.1))
        self.assertIsNone(ps.demargin([1.8, None]))
        self.assertIsNone(ps.demargin([1.8, 1.0]))

    def test_lineas_enteras_no_tienen_p_de_mercado(self):
        self.assertTrue(ps.is_whole_line(2.0))
        self.assertFalse(ps.is_whole_line(2.5))
        self.assertFalse(ps.is_whole_line(2.25))


class Rankings(unittest.TestCase):
    def test_tope_de_patas_por_partido_y_composicion(self):
        legs = [{"match_id": "a"}, {"match_id": "a"}, {"match_id": "a"}, {"match_id": "b"}, {"match_id": "a"}, {"match_id": "c"}]
        out = cr.limitar_por_partido(legs, 2)
        self.assertEqual([l["match_id"] for l in out], ["a", "a", "b", "c"])
        c = cr.composicion(out)
        self.assertEqual((c["filas"], c["partidos_distintos"], c["max_por_partido"]), (4, 3, 2))
        self.assertEqual(cr.MAX_RANK_POR_PARTIDO, 2)

    def test_p_del_modelo_y_rankings_no_dependen_de_la_captura_del_usuario(self):
        base = [unit(1, [entrada(OVER[0], 1.6, 0.72, estado="otra_fuente"), entrada(UNDER[0], 1.5, 0.66, estado="otra_fuente")]),
                unit(2, [entrada(OVER[1], 1.7, 0.70, estado="otra_fuente")])]
        con = [unit(1, [entrada(OVER[0], 1.6, 0.72, estado="real_verificada"), entrada(UNDER[0], 1.5, 0.66, estado="real_verificada")]),
               unit(2, [entrada(OVER[1], 1.7, 0.70, estado="real_verificada")])]
        a, b = cr.legs_from_units(base), cr.legs_from_units(con)
        self.assertEqual([(l["entry_id"], l["p_modelo"], l["cuota"]) for l in a], [(l["entry_id"], l["p_modelo"], l["cuota"]) for l in b])
        ra, rb = cr.build_rankings(a), cr.build_rankings(b)
        self.assertEqual(json.dumps(ra, sort_keys=True, default=str).count("entry_id"), json.dumps(rb, sort_keys=True, default=str).count("entry_id"))


class RegistroYDia(unittest.TestCase):
    def test_dia_de_caracas_resta_cuatro_horas(self):
        self.assertEqual(cmp.dia_caracas("2026-10-17T01:00:00Z"), "2026-10-16")
        self.assertEqual(cmp.dia_caracas("2026-10-17T04:00:00Z"), "2026-10-17")
        self.assertEqual(cmp.dia_caracas("2026-10-16T23:59:00Z"), "2026-10-16")

    def test_csv_una_fila_por_pata_con_las_columnas_acordadas(self):
        rows = [fila(RUNS[0], "m1", 1, 0.7, 1), fila(RUNS[0], "m1", 2, 0.4, 0), dict(fila(RUNS[1], "m2", 1, 0.6, 1), p_mercado=0.55, cuota_usuario=1.7, agentes="aprobada")]
        with tempfile.TemporaryDirectory() as d:
            out = os.path.join(d, "h.csv")
            self.assertEqual(acu.exportar_csv(rows, out, {(RUNS[0], "m1"): 3}), 3)
            got = list(csv.DictReader(open(out, encoding="utf-8")))
        self.assertEqual(list(got[0]), acu.CSV_COLUMNAS)
        self.assertEqual(len(got), 3)
        self.assertEqual(len({(g["run"], g["partido_id"], g["entry_id"]) for g in got}), 3)
        self.assertEqual([g["acierto"] for g in got], ["1", "0", "1"])
        self.assertEqual(got[0]["goles_reales_partido"], "3")
        self.assertEqual(got[2]["clase_agentes"], "aprobada")
        self.assertEqual(got[2]["cuota_usuario"], "1.7")
        self.assertEqual(got[0]["p_mercado"], "")

    def test_el_csv_real_coincide_con_el_registro(self):
        root = os.path.normpath(os.path.join(os.path.dirname(__file__), ".."))
        led, csvp = os.path.join(root, "data", "ledger_patas.jsonl"), os.path.join(root, "data", "historial_patas.csv")
        if not (os.path.exists(led) and os.path.exists(csvp)):
            self.skipTest("sin registro real")
        self.assertEqual(sum(1 for _ in open(csvp, encoding="utf-8")) - 1, len(acu.leer(led)))


class AuditorDeLibros(unittest.TestCase):
    def libro(self, d, nombre, arch, partido_hora="14-Oct 20:00", extra_filas=()):
        import openpyxl
        wb = openpyxl.Workbook()
        wb.active.title = "Léeme"
        wb["Léeme"].append(["ARCHIVO: " + arch])
        wb.create_sheet("Leyenda").append(["x"])
        ws = wb.create_sheet("Liga 1")
        ws.append(["Hora Caracas", "Partido", "Mercado", "Selección", "Cuota"])
        for f in [(partido_hora, "A – B", "Goles", "Más de 2.5", 1.8), *extra_filas]:
            ws.append(list(f))
        wb.create_sheet("Ranking seguridad").append(["Partido", "Selección"])
        wb.create_sheet("Ranking atractivo-cuota").append(["Partido", "Selección"])
        wb.create_sheet("Catálogo completo").append(["Partido", "Entrada", "Etiqueta"])
        p = os.path.join(d, nombre)
        wb.save(p)
        return p

    def ids(self, inf):
        return {x["id"] for x in inf.items}

    def test_texto_desactualizado_y_duplicados(self):
        with tempfile.TemporaryDirectory() as d:
            p = self.libro(d, "ligas-16-oct-v2_1.xlsx", "ligas-16-oct-v2.xlsx", extra_filas=[("14-Oct 20:00", "A – B", "Goles", "Más de 2.5", 1.8)])
            inf = aud.Informe()
            aud.auditar_libro(p, informe=inf)
            self.assertIn("B01", self.ids(inf))
            self.assertIn("B03", self.ids(inf))

    def test_libro_coherente_no_marca_el_nombre(self):
        with tempfile.TemporaryDirectory() as d:
            p = self.libro(d, "ligas-16-oct-v3.xlsx", "ligas-16-oct-v3.xlsx")
            inf = aud.Informe()
            aud.auditar_libro(p, informe=inf)
            self.assertNotIn("B01", self.ids(inf))
            self.assertNotIn("B03", self.ids(inf))


if __name__ == "__main__":
    unittest.main()
