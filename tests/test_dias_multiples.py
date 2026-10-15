"""Flujo por día (15–17 oct): clasificación de categoría, emparejamiento captura↔inventario y vínculo manual con la API. Datos FICTICIOS: EJEMPLO — NO REAL."""
import json
import os
import tempfile
import unittest

import helpers  # noqa: F401  (añade scripts/ al path)
import adapters
import common
import inventory as inv
import link_api
import resolve_ids


def write(path, obj):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(obj, fh)


def match(mid, home, away, utc, cat="men", **kw):
    m = {"match_id": mid, "home_team": home, "away_team": away, "competition": "liga ejemplo", "normalized_datetime_utc": utc, "gender_or_category": cat, "analysis_required": True,
         "source_match_ids": {"apwin": "1"}, "source_names": ["apwin"], "verification_sources": ["apwin"], "extra": {"api": None}}
    m.update(kw)
    return m


class Categoria(unittest.TestCase):
    def test_juniors_en_el_nombre_de_un_equipo_no_es_juvenil_y_los_romanos_de_primer_equipo_tampoco(self):
        self.assertEqual(inv.detect_category("Boca Juniors", "Talleres de Cordoba", "primera division"), "men")
        self.assertEqual(inv.detect_category("Argentinos Juniors", "Banfield", "Liga"), "men")
        self.assertEqual(inv.detect_category("Juan Pablo II", "Sport Boys", "Primera"), "men")
        self.assertEqual(inv.detect_category("Willem II", "Sparta", "Eredivisie"), "men")

    def test_lo_juvenil_de_verdad_sigue_siendo_juvenil(self):
        self.assertEqual(inv.detect_category("Ajax U19", "PSV U19", "Liga"), "youth")
        self.assertEqual(inv.detect_category("A", "B", "Liga Juniors"), "youth")


class Emparejamiento(unittest.TestCase):
    def setUp(self):
        self.run = tempfile.mkdtemp()
        write(os.path.join(self.run, "inventory.json"), {"meta": {"date": "2026-10-15", "tz": "America/Caracas"}, "matches": [
            match("m-1", "Olympique de Marseille", "Olympiakos Piraeus", "2026-10-15T19:00:00Z"),
            match("m-2", "Marseille", "Olympiacos", "2026-10-15T19:00:00Z", cat="youth"),          # categoría juvenil: no se empareja
            match("m-3", "Otro", "Equipo", "2026-10-15T19:00:00Z"),
            match("m-4", "Al Hazem", "Al Fateh", "2026-10-15T15:15:00Z")]})
        write(os.path.join(self.run, "ligas", "partidos_usuario.json"), {"partidos": [
            ["Europa League", "Marseille", "Olympiacos FC", "15:00", [2.3, 3.5, 2.9], 2.5, [1.72, 2.05]],
            ["Saudi", "Al Hazm FC", "Al Fateh SC", "11:15", [2.45, 3.66, 2.5], 2.5, [1.63, 2.12]],
            ["Nada", "Inventado", "Fantasma", "10:00", [2, 3, 4], 2.5, [1.9, 1.9]]]})

    def test_empareja_por_hora_y_nombres_y_deja_sin_resolver_lo_que_no_encuentra(self):
        resolve_ids.main(["--run", self.run])
        ids = json.load(open(os.path.join(self.run, "ligas", "ids.json")))
        self.assertEqual(ids["Marseille|Olympiacos FC"], "m-1")        # 15:00 Caracas = 19:00Z; el juvenil queda fuera
        self.assertEqual(ids["Al Hazm FC|Al Fateh SC"], "m-4")
        self.assertNotIn("Inventado|Fantasma", ids)
        miss = json.load(open(os.path.join(self.run, "ligas", "ids_sin_resolver.json")))
        self.assertEqual(len(miss), 1)

    def test_una_hora_distinta_no_empareja_aunque_el_nombre_coincida(self):
        d = json.load(open(os.path.join(self.run, "inventory.json")))
        d["matches"][0]["normalized_datetime_utc"] = "2026-10-15T23:30:00Z"
        write(os.path.join(self.run, "inventory.json"), d)
        resolve_ids.main(["--run", self.run])
        self.assertNotIn("Marseille|Olympiacos FC", json.load(open(os.path.join(self.run, "ligas", "ids.json"))))


class VinculoManual(unittest.TestCase):
    def setUp(self):
        self.run = tempfile.mkdtemp()
        write(os.path.join(self.run, "inventory.json"), {"meta": {}, "matches": [match("m-9", "ABB", "Real Potosí", "2026-10-16T19:00:00Z")]})
        write(os.path.join(self.run, "state.json"), {"matches": {"m-9": {"status": "NO_INVESTIGADO_SIN_FUENTE_PERMITIDA", "attempts": 2}}})
        self._k, self._c = adapters.apif_key, adapters.apif_call
        adapters.apif_key = lambda: "CLAVE-FICTICIA"

    def tearDown(self):
        adapters.apif_key, adapters.apif_call = self._k, self._c

    def _event(self, hora):
        return [{"match_id": "838243", "match_date": "2026-10-16", "match_time": hora, "match_hometeam_id": "1", "match_hometeam_name": "Academia del Balompie", "match_awayteam_id": "2",
                 "match_awayteam_name": "Real Potosi", "league_id": "69", "league_name": "Primera División", "match_referee": "", "match_status": ""}]

    def test_vincula_con_la_misma_hora_deja_constancia_y_reinicia_la_cola(self):
        adapters.apif_call = lambda *a, **k: self._event("19:00")
        self.assertEqual(link_api.main(["--run", self.run, "--match-id", "m-9", "--api-id", "838243"]), 0)
        m = json.load(open(os.path.join(self.run, "inventory.json")))["matches"][0]
        self.assertEqual(m["source_match_ids"]["apifootball"], "838243")
        self.assertEqual(m["extra"]["api"]["home_name"], "Academia del Balompie")
        self.assertIn("manual_link", m)
        st = json.load(open(os.path.join(self.run, "state.json")))["matches"]["m-9"]
        self.assertEqual((st["status"], st["attempts"]), ("PENDIENTE", 0))

    def test_hora_distinta_no_vincula(self):
        adapters.apif_call = lambda *a, **k: self._event("22:00")
        self.assertEqual(link_api.main(["--run", self.run, "--match-id", "m-9", "--api-id", "838243"]), 2)
        self.assertNotIn("manual_link", json.load(open(os.path.join(self.run, "inventory.json")))["matches"][0])


if __name__ == "__main__":
    unittest.main()
