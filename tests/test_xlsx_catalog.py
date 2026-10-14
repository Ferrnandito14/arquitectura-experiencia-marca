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
        for n in ("Léeme", "Cobertura", "Catálogo completo", "Rankings por grupo", "Ranking general", "Combinadas", "Sin precio", "Agentes", "Resumen por partido"):
            self.assertIn(n, self.wb.sheetnames)

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
