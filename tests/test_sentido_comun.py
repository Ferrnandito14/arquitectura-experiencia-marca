import importlib.util
import os
import unittest

RUTA = os.path.join(os.path.dirname(__file__), "..", ".claude", "skills", "seleccion-final-picks", "scripts", "sentido_comun.py")
spec = importlib.util.spec_from_file_location("sentido_comun", RUTA)
sc = importlib.util.module_from_spec(spec)
spec.loader.exec_module(sc)


def e(eid, cuota, linea=None, direccion=None, pmod=None, pm=None):
    return {"id": eid, "linea": linea, "direccion": direccion, "p_modelo": pmod,
            "precio": {"cuota": cuota, "p_mercado": ({"p": pm} if pm is not None else None)}}


def u(*entradas):
    return {"unit_id": "m-1|g", "match_id": "m-1", "entradas": list(entradas)}


def reglas(unidad):
    return sorted({b["regla"] for b in sc.revisar_unidad(unidad)})


class SentidoComun(unittest.TestCase):
    def test_handicap_imposible(self):
        un = u(e("resultado.ah.home.-2.5", 1.03, -2.5, "home"), e("resultado.ah.away.+2.5", 1.02, 2.5, "away"))
        self.assertEqual(reglas(un), ["par_imposible"])

    def test_handicap_normal_no_marca(self):
        un = u(e("resultado.ah.home.-1.5", 1.85, -1.5, "home"), e("resultado.ah.away.+1.5", 1.93, 1.5, "away"))
        self.assertEqual(reglas(un), [])

    def test_totales_normales_y_planos(self):
        self.assertEqual(reglas(u(e("goles.total.over.2.5", 1.9, 2.5), e("goles.total.under.2.5", 1.95, 2.5))), [])
        self.assertEqual(reglas(u(e("shots.total.over.27.5", 1.833, 27.5), e("shots.total.under.27.5", 1.833, 27.5))), ["cuota_plana"])

    def test_btts_y_dnb(self):
        self.assertEqual(reglas(u(e("goles.btts.yes", 1.03), e("goles.btts.no", 1.03))), ["par_imposible"])
        self.assertEqual(reglas(u(e("resultado.dnb.home", 1.5), e("resultado.dnb.away", 2.6))), [])

    def test_1x2_imposible(self):
        un = u(e("resultado.1x2.home", 1.5), e("resultado.1x2.draw", 2.0), e("resultado.1x2.away", 2.0))
        self.assertEqual(reglas(un), ["par_imposible"])
        ok = u(e("resultado.1x2.home", 2.0), e("resultado.1x2.draw", 3.4), e("resultado.1x2.away", 3.8))
        self.assertEqual(reglas(ok), [])

    def test_cuota_repetida_en_escalera(self):
        un = u(e("sot.total.over.8.5", 2.1, 8.5), e("sot.total.over.9.5", 2.1, 9.5), e("sot.total.over.10.5", 3.0, 10.5))
        self.assertEqual(reglas(un), ["cuota_repetida"])

    def test_escalera_no_monotona(self):
        un = u(e("goles.total.over.2.5", 2.4, 2.5), e("goles.total.over.3.5", 1.9, 3.5))
        self.assertIn("escalera_no_monotona", reglas(un))
        ok = u(e("goles.total.over.2.5", 1.9, 2.5), e("goles.total.over.3.5", 3.4, 3.5))
        self.assertEqual(reglas(ok), [])

    def test_brecha_extrema(self):
        self.assertIn("brecha_extrema", reglas(u(e("goles.total.over.2.5", 1.9, 2.5, pmod=0.95, pm=0.50 - 0.1))))
        self.assertEqual(reglas(u(e("goles.total.over.2.5", 1.9, 2.5, pmod=0.60, pm=0.45))), [])

    def test_partido_no_programado(self):
        paq = {"run": "r", "unidades": [u(e("goles.total.over.2.5", 1.9, 2.5))]}
        inv = {"matches": [{"match_id": "m-1", "event_status": "APLAZADO"}]}
        self.assertEqual(sc.revisar(paq, inv)["resumen"], {"partido_no_programado": 1})
        inv2 = {"matches": [{"match_id": "m-1", "event_status": "PROGRAMADO"}]}
        self.assertEqual(sc.revisar(paq, inv2)["resumen"], {})

    def test_entradas_sin_cuota_no_fallan(self):
        self.assertEqual(reglas(u(e("goles.total.over.2.5", None, 2.5), e("goles.total.under.2.5", None, 2.5))), [])


if __name__ == "__main__":
    unittest.main()
