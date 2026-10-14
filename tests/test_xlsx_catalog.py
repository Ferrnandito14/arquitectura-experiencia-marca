"""Fase 7: libro v2 desde el catálogo completo. Datos FICTICIOS: EJEMPLO — NO REAL."""
import hashlib
import os
import tempfile
import unittest

import helpers  # noqa: F401  (añade scripts/ al path)
import agent_review as ar
import build_xlsx_catalog as bx
import catalog_rankings as cr
import market_coverage as cov
from test_catalog_rankings import OVER, UNDER, entrada, unit

REPO = os.path.normpath(os.path.join(os.path.dirname(__file__), ".."))


def summary(ids, certified=True, modo="enforce", revision="COMPLETA"):
    inc = [{"tipo": "x", "cantidad": 1}]
    return {"modo": modo, "partidos_ids": ids, "investigacion_certificada": certified, "investigacion": {"estado": "INVESTIGACION_COMPLETA" if certified else "INVESTIGACION_INCOMPLETA", "incidencias": []},
            "analitica": {"estado": "CON_LIMITACIONES", "incidencias": inc}, "precios": {"estado": "PRECIOS_REALES_PARCIALES", "incidencias": []},
            "revision_agentes": {"estado": revision, "incidencias": 0, "unidades_esperadas": 9}, "preparacion_para_apostar": {"estado": "NINGUNA_FILA_APTA", "filas_aptas": 0, "filas": 4, "requisitos_incumplidos": {"modelo_validado": 4}},
            "aviso": "", "contexto_partidos": {}}


class Nombre(unittest.TestCase):
    ids = ["m0", "m1"]

    def test_definitivo_solo_con_todo(self):
        f, why = bx.workbook_name("ligas-v2", summary(self.ids), self.ids, {"estado": "COMPLETA", "partidos_ids": self.ids})
        self.assertEqual((f, why), ("ligas-v2.xlsx", []))

    def test_cada_carencia_lo_deja_provisional(self):
        ok = {"estado": "COMPLETA", "partidos_ids": self.ids}
        casos = [(summary(self.ids, certified=False), ok, "catalog"), (summary(self.ids, modo="omitida"), ok, "catalog"), (summary(self.ids), {"estado": "INCOMPLETA", "partidos_ids": self.ids}, "catalog"),
                 (summary(self.ids), {"estado": "COMPLETA", "partidos_ids": ["m0"]}, "catalog"), (summary(self.ids), None, "catalog"), (summary(self.ids), ok, "capture_legs_only")]
        for s, rv, scope in casos:
            f, why = bx.workbook_name("ligas-v2", s, self.ids, rv, scope)
            self.assertEqual(f, "ligas-v2-PROVISIONAL.xlsx")
            self.assertTrue(why)


class Libro(unittest.TestCase):
    def setUp(self):
        self.us = [unit(i, [entrada(OVER[0], 1.5, 0.7), entrada(UNDER[1], None, 0.65), entrada(OVER[2], 1.4, None)], liga=f"L{i}", hora=f"2026-10-14T{16 + i}:30:00Z") for i in range(3)]
        self.ids = [u["match_id"] for u in self.us]
        self.legs = cr.legs_from_units(self.us)
        self.wb = bx.make_workbook(self.us, summary(self.ids), self.legs, cr.build_rankings(self.legs), cr.build_combos(self.legs, True, targets=(("x2", 2.0, 2.4, 3),)),
                                   ar.consolidate(self.us, {}), {"m0": {"home": {"nivel": "alto"}, "away": {"nivel": "bajo"}}}, "ligas-v2.xlsx", [])

    def test_hojas_esperadas(self):
        for n in ("Léeme", "Ranking seguridad", "Ranking atractivo-cuota", "Top por liga", "Combinadas", "Mercados extra", "Resumen por partido", "Cobertura", "Catálogo completo", "Sin precio", "Agentes"):
            self.assertIn(n, self.wb.sheetnames)
        self.assertEqual(self.wb.sheetnames[:3], ["Léeme", "Leyenda", "Liga L0"])          # formato clásico: Léeme, leyenda y luego una hoja por liga

    def test_una_hoja_por_liga_con_todos_los_mercados_visibles_de_sus_partidos(self):
        for i in range(3):
            w = self.wb[f"Liga L{i}"]
            partidos = {w.cell(r, 2).value for r in range(2, w.max_row + 1)}
            self.assertEqual(partidos, {f"A{i} – B{i}"})
            self.assertEqual(w.max_row - 1, 2)                              # solo las entradas con estimador (la de p=None queda en el catálogo completo)
        self.assertEqual(self.wb["Liga L0"].cell(1, 3).value, "Mercado")

    def test_rankings_solo_con_precio_dentro_del_limite(self):
        w = self.wb["Ranking seguridad"]
        for r in range(2, w.max_row + 1):
            self.assertIsNotNone(w.cell(r, 7).value)                        # cuota de alguna fuente
            self.assertLessEqual(w.cell(r, 7).value, 2.10)
            self.assertGreaterEqual(w.cell(r, 7).value, bx.RANK_MIN_ODDS)

    def test_las_combinadas_traen_los_rangos_clasicos_y_los_objetivos_estandar(self):
        us = [unit(i, [entrada(OVER[0], 1.4, 0.7), entrada(UNDER[1], 1.3, 0.7)], liga=f"L{i}", hora=f"2026-10-14T{8 + 3 * i:02d}:00:00Z") for i in range(6)]
        legs = cr.legs_from_units(us)
        combos = cr.build_combos(legs, True, targets=bx.CLASSIC_TARGETS + cr.DEFAULT_TARGETS)
        self.assertEqual(list(combos), ["×1.5–1.8", "×2–2.6", "×3–3.8", "x1.2", "x3", "x4"])

    def test_el_catalogo_trae_una_fila_por_pata_con_hora_de_caracas(self):
        w = self.wb["Catálogo completo"]
        self.assertEqual(w.max_row - 1, len(self.legs))
        self.assertEqual(w.cell(2, 2).value, "14-Oct 12:30")          # 16:30Z = 12:30 en Caracas (UTC−4)

    def test_ningun_precio_de_agregador_se_marca_ejecutable_y_nada_es_apto(self):
        us = [unit(1, [entrada(OVER[0], 1.5, 0.7, estado="otra_fuente")])]
        legs = cr.legs_from_units(us)
        wb = bx.make_workbook(us, summary(["m1"]), legs, cr.build_rankings(legs), cr.build_combos(legs, True, targets=(("x1.5", 1.4, 1.6, 1),)), ar.consolidate(us, {}), {}, "f.xlsx", [])
        tipos = {wb["Catálogo completo"].cell(r, 9).value for r in range(2, wb["Catálogo completo"].max_row + 1)}
        self.assertEqual(tipos, {"referencia"})
        for r in range(2, wb["Combinadas"].max_row + 1):
            self.assertNotEqual(wb["Combinadas"].cell(r, 9).value, "APTA")

    def test_sin_precio_trae_columna_para_completar_y_solo_entradas_con_cuota_justa_dentro_del_limite(self):
        w = self.wb["Sin precio"]
        self.assertEqual(w.cell(1, 7).value, "Cuota de tu casa (completar)")
        self.assertEqual(w.max_row - 1, 3)                               # la entrada sin precio de cada partido
        self.assertTrue(all(w.cell(r, 7).value is None for r in range(2, w.max_row + 1)))

    def test_leeme_aclara_certificacion_modelo_y_horas(self):
        txt = " ".join(str(c.value) for c in self.wb["Léeme"]["A"])
        for frag in ("≠ aprobación para apostar", "NO está validado", "Caracas"):
            self.assertIn(frag, txt)

    def test_la_leyenda_cubre_cada_resultado_de_investigacion_y_cada_estado_de_agentes(self):
        txt = " ".join(str(c.value) for row in self.wb["Leyenda"].iter_rows() for c in row)
        for v in ("encontrado", "consultado_no_encontrado", "fuente_no_ofrece", "no_verificable", "pendiente", "aprobada", "objetada", "degradada", "rechazada", "sin_revision", "ejecutable", "referencia", "Alerta"):
            self.assertIn(v, txt)
        inv = self.wb["Catálogo completo"].cell(2, 20).value
        self.assertIn("datos_deportivos=encontrado", inv)             # palabras, no letras

    def test_alerta_marca_desacuerdo_y_ev_alto(self):
        l = cr.legs_from_units([unit(1, [entrada(OVER[0], 2.0, 0.80)])])[0]          # EV +60 %, brecha +30 pp
        a = bx.alerta(l)
        self.assertIn("desacuerdo", a)
        self.assertIn("EV alto", a)
        ok = cr.legs_from_units([unit(1, [entrada(OVER[0], 1.5, 0.66)])])[0]
        self.assertIsNone(bx.alerta(ok))

    def test_mercados_extra_y_sin_precio_dicen_sin_cuota_en_fuente_y_no_cuota_minima(self):
        us = [unit(1, [entrada(OVER[0], 1.5, 0.70), entrada(OVER[1], None, 0.75)], grupo="córners")]
        legs = cr.legs_from_units(us)
        wb = bx.make_workbook(us, summary(["m1"]), legs, cr.build_rankings(legs), {}, ar.consolidate(us, {}), {}, "f.xlsx", [])
        for n in ("Mercados extra", "Sin precio"):
            hdr = [c.value for c in wb[n][1]]
            self.assertIn("Cuota fuente", hdr, n)
            self.assertNotIn("Cuota mínima justa", hdr, n)
            self.assertIn("Cuota de tu casa (completar)", hdr, n)
        vals = [c.value for row in wb["Mercados extra"].iter_rows(min_row=2) for c in row]
        self.assertIn("sin cuota en fuente", vals)
        self.assertIn(1.5, vals)                                          # la fila con cuota de fuente muestra la cuota
        self.assertEqual({c.value for c in wb["Sin precio"]["F"][1:]}, {"sin cuota en fuente"})

    def test_la_hoja_de_combinadas_trae_multiplicador_aporte_y_correlacion(self):
        us = [unit(i, [entrada(OVER[0], 1.5, 0.70)], liga="L1", hora="2026-10-14T20:00:00Z") for i in range(3)]
        legs = cr.legs_from_units(us)
        combos = cr.build_combos(legs, True, targets=(("x2.25", 2.2, 2.3, 2),), policy=dict(cr.POLICY, max_misma_ventana=3))
        wb = bx.make_workbook(us, summary(["m0", "m1", "m2"]), legs, cr.build_rankings(legs), combos, ar.consolidate(us, {}), {}, "f.xlsx", [])
        hdr = [c.value for c in wb["Combinadas"][1]]
        for h in ("Multiplicador (producto de las cuotas)", "Aporte de la pata al multiplicador %", "P gana si fueran independientes %", "Nota de correlación"):
            self.assertIn(h, hdr)
        txt = " ".join(str(c.value) for row in wb["Léeme"].iter_rows() for c in row)
        self.assertIn("1.50 × 1.60 × 1.40 = 3.36", txt)
        self.assertIn("sin cuota en fuente", txt)
        self.assertIn("TheStatsAPI", txt)

    def test_el_script_no_puede_nombrar_el_libro_original_y_la_ruta_esta_registrada(self):
        f = ".claude/skills/seleccion-final-picks/scripts/build_xlsx_catalog.py"
        self.assertIn(f, cov.GENERATION_ROUTES)
        with open(os.path.join(REPO, f), encoding="utf-8") as fh:
            txt = fh.read()
        self.assertIn(cov.GENERATION_ROUTES[f]["marker"], txt)
        self.assertIn("nunca puede llamarse como el original", txt)

    def test_guardar_el_libro_no_toca_el_original(self):
        orig = os.path.join(REPO, "dist", "ligas-14-oct.xlsx")
        h = lambda: hashlib.sha256(open(orig, "rb").read()).hexdigest() if os.path.exists(orig) else None
        before = h()
        self.wb.save(os.path.join(tempfile.mkdtemp(), "ligas-v2.xlsx"))
        self.assertEqual(before, h())


if __name__ == "__main__":
    unittest.main()
