import importlib.util
import os
import unittest

RUTA = os.path.join(os.path.dirname(__file__), "..", ".claude", "skills", "seleccion-final-picks", "scripts", "cuantitativo_regla.py")
spec = importlib.util.spec_from_file_location("cuantitativo_regla", RUTA)
cr = importlib.util.module_from_spec(spec)
spec.loader.exec_module(cr)


def linea(eid, pmod, cuota=None, pm=None, estimador="calculable", validacion="no_evaluada"):
    precio = {"cuota": cuota, "p_mercado": ({"p": pm} if pm is not None else None)}
    return {"id": eid, "p_modelo": pmod, "estimador": estimador, "precio": precio, "validacion": validacion}


def unidad(*lineas, uid="m-1|goles"):
    return {"unit_id": uid, "entradas": list(lineas)}


class ReglaCuantitativo(unittest.TestCase):
    def test_umbral_15pp(self):
        self.assertEqual(cr.clasificar_linea(linea("goles.total.over.2.5", 0.60, 1.9, 0.44))[0], "discrepa_del_mercado")
        self.assertEqual(cr.clasificar_linea(linea("goles.total.over.2.5", 0.55, 1.9, 0.44))[0], "coherente")

    def test_sin_p_mercado_usa_1_sobre_cuota_en_linea_simple(self):
        self.assertEqual(cr.clasificar_linea(linea("goles.total.over.2.5", 0.40, 2.0))[0], "coherente")
        self.assertEqual(cr.clasificar_linea(linea("goles.total.over.2.5", 0.70, 2.0))[0], "discrepa_del_mercado")

    def test_lineas_enteras_y_europeo_no_usan_1_sobre_cuota(self):
        for eid in ("goles.total_entero.over.3", "resultado.ah_entero.home.-1", "resultado.eh.home.-1"):
            self.assertEqual(cr.clasificar_linea(linea(eid, 0.70, 2.0))[0], "sin_precio_para_contrastar")
            self.assertEqual(cr.clasificar_linea(linea(eid, 0.70, 2.0, 0.40))[0], "discrepa_del_mercado")

    def test_cuota_plana_no_informa(self):
        self.assertEqual(cr.clasificar_linea(linea("shots.total.over.27.5", 0.30, 1.833, 0.5))[0], "sin_precio_para_contrastar")

    def test_sin_estimador_y_datos_insuficientes(self):
        self.assertEqual(cr.clasificar_linea(linea("otros.fueras_de_juego.over.3.5", None, estimador="no_implementado"))[0], "sin_estimador")
        self.assertEqual(cr.clasificar_linea(linea("corners.total.over.9.5", None, estimador="datos_insuficientes"))[0], "datos_insuficientes")

    def test_unidad_discrepa_con_un_cuarto_de_lineas(self):
        u = unidad(linea("a", 0.70, 2.0, 0.40), linea("b", 0.50, 2.0, 0.50 - 0.01), linea("c", 0.50, 2.0, 0.49), linea("d", 0.50, 2.0, 0.49))
        v, cats, brechas, exc = cr.veredicto_unidad(u)
        self.assertEqual(v, "discrepa_del_mercado")
        self.assertEqual([e["entry_id"] for e in exc], ["b", "c", "d"])

    def test_unidad_coherente_con_menos_de_un_cuarto(self):
        lineas = [linea("a", 0.70, 2.0, 0.40)] + [linea(f"x{i}", 0.50, 2.0, 0.49) for i in range(5)]
        self.assertEqual(cr.veredicto_unidad(unidad(*lineas))[0], "coherente")

    def test_unidad_sin_nada_contrastable(self):
        self.assertEqual(cr.veredicto_unidad(unidad(linea("a", 0.5, None)))[0], "sin_precio_para_contrastar")
        self.assertEqual(cr.veredicto_unidad(unidad(linea("a", None, estimador="datos_insuficientes")))[0], "datos_insuficientes")
        self.assertEqual(cr.veredicto_unidad(unidad(linea("a", None, estimador="no_implementado")))[0], "sin_estimador")

    def test_entrada_cumple_contrato(self):
        e = cr.entrada_unidad(unidad(linea("a", 0.70, 2.0, 0.40, validacion="parcial")))
        self.assertEqual(set(e), {"unit_id", "consistencia_modelo", "riesgo_correlacion", "validacion_aplicable", "nota", "excepciones", "evidencia"})
        self.assertEqual(e["validacion_aplicable"], "parcial")
        self.assertLessEqual(len(e["nota"]), 200)
        self.assertTrue(e["evidencia"][0].startswith("paquete:"))

    def test_nunca_afirma_validado(self):
        e = cr.entrada_unidad(unidad(linea("a", 0.5, 2.0, 0.5 - 0.02, validacion="validado")))
        self.assertNotEqual(e["validacion_aplicable"], "validado")


if __name__ == "__main__":
    unittest.main()
