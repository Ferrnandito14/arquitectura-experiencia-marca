import os, sys, tempfile, unittest
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".claude", "skills", "seleccion-final-picks", "scripts"))
import memoria_equipos as me


def mk(i, utc, h, a, gh, ga, status="finished"):
    return {"id": i, "status": status, "utc_date": utc + ":00.000Z", "home_team": {"id": "t" + h, "name": h},
            "away_team": {"id": "t" + a, "name": a}, "score": {"regulation": {"home": gh, "away": ga}}}


class T(unittest.TestCase):
    def test_fusion_sin_duplicados_y_solo_terminados(self):
        d = {}
        n, c = me.fusionar(d, [mk("1", "2026-10-01T10:00", "A", "B", 2, 1), mk("2", "2026-10-02T10:00", "A", "C", 0, 0, "scheduled")])
        self.assertEqual((n, c, len(d)), (1, 0, 1))
        n, c = me.fusionar(d, [mk("1", "2026-10-01T10:00", "A", "B", 2, 1)])
        self.assertEqual((n, c, len(d)), (0, 0, 1))
        n, c = me.fusionar(d, [mk("1", "2026-10-01T10:00", "A", "B", 3, 1)])
        self.assertEqual((n, c), (0, 1))

    def test_resumen_y_antes(self):
        d = {}
        me.fusionar(d, [mk("1", "2026-10-01T10:00", "A", "B", 2, 1), mk("2", "2026-10-08T10:00", "C", "A", 0, 0), mk("3", "2026-10-15T10:00", "A", "D", 4, 0)])
        r = me.resumen(d, "a", 8)
        self.assertEqual(r["n"], 3)
        self.assertEqual(r["frecuencias"]["o35"], 1)
        self.assertEqual(r["frecuencias"]["gana"], 2)
        self.assertEqual(me.resumen(d, "A", 8, antes="2026-10-10T00:00")["n"], 2)

    def test_guardar_cargar_y_rango(self):
        with tempfile.TemporaryDirectory() as t:
            p = os.path.join(t, "x", "p.jsonl")
            d = {}
            me.fusionar(d, [mk("1", "2026-10-10T10:00", "A", "B", 1, 1)])
            me.guardar(d, p)
            self.assertEqual(me.cargar(p), d)
            self.assertEqual(me.rango_nuevo(d, "2026-10-20"), ("2026-10-08", "2026-10-20"))


if __name__ == "__main__":
    unittest.main()


class TStats(unittest.TestCase):
    def test_stats_append_y_ultimo_gana(self):
        with tempfile.TemporaryDirectory() as t:
            p = os.path.join(t, "s.jsonl")
            me.anotar_stats("m1", {"ok": False}, p)
            me.anotar_stats("m1", {"ok": True, "corners": [5, 3], "amarillas": [1, 2], "rojas": [0, 0]}, p)
            me.anotar_stats("m2", {"ok": False}, p)
            d = me.cargar_stats(p)
            self.assertTrue(d["m1"]["ok"])
            self.assertEqual(d["m1"]["corners"], [5, 3])
            self.assertFalse(d["m2"]["ok"])

    def test_partidos_por_id(self):
        d = {}
        me.fusionar(d, [mk("1", "2026-10-01T10:00", "A", "B", 2, 1), mk("2", "2026-10-08T10:00", "C", "A", 0, 0)])
        xs = me.partidos_por_id(d, "tA", 8)
        self.assertEqual([r["id"] for r in xs], ["2", "1"])
        self.assertEqual(len(me.partidos_por_id(d, "tA", 1)), 1)
