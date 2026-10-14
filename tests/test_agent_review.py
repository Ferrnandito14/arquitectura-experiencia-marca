"""Fase 5: contrato cerrado de revisión por agentes, validador de completitud, auditor con muestra mínima y requisito de preparación. Datos FICTICIOS: EJEMPLO — NO REAL."""
import copy
import json
import os
import subprocess
import sys
import tempfile
import unittest

import helpers  # noqa: F401  (añade scripts/ al path)
import agent_review as ar
import market_catalog as mc
import market_coverage as cov

REPO = os.path.normpath(os.path.join(os.path.dirname(__file__), ".."))
SCRIPT = os.path.join(REPO, ".claude", "skills", "seleccion-final-picks", "scripts", "agent_review.py")


def entrada(eid, precio="sin_precio", datos="suficientes", estimador="calculable", validacion="insuficiente", canales=None):
    return {"id": eid, "linea": None, "direccion": None, "alcance": "match", "investigacion": canales or {"datos_deportivos": "encontrado", "apifootball (agregador)": "consultado_no_encontrado"},
            "precio": {"estado": precio, "cuota": None, "fuente": None, "tipo": None, "cumple_limite_2_10": None}, "datos": datos, "estimador": estimador, "validacion": validacion, "p_modelo": 0.5}


def unidad(mid, grupo, **kw):
    es = [entrada(f"{grupo}.{i}", **kw) for i in range(2)]
    cnt = lambda f: {k: sum(1 for x in es if f(x) == k) for k in sorted({f(x) for x in es})}
    return {"unit_id": ar.unit_id(mid, grupo), "match_id": mid, "partido": f"A{mid} – B{mid}", "grupo": grupo, "entradas": es,
            "resumen": {"entradas": 2, "precio": cnt(lambda x: x["precio"]["estado"]), "datos": cnt(lambda x: x["datos"]), "estimador": cnt(lambda x: x["estimador"]),
                        "validacion": cnt(lambda x: x["validacion"] or "sin_estimador"), "investigacion": {"resuelta": 2}}}


GRUPOS = ["goles", "córners", "resultado"]


def units(n_matches=4, **kw):
    return [unidad(f"m{i}", g, **kw) for i in range(n_matches) for g in GRUPOS]


def valid_report(role, us, **over):
    out = []
    for u in us:
        r = {"unit_id": u["unit_id"], "nota": "ok", "excepciones": [], "evidencia": [f"paquete:{u['unit_id']}"]}
        if role == "deportivo":
            r.update(solidez="MEDIA", factor_principal="forma", direccion_favorable="sin_sesgo", escenario_perdida="partido_cerrado")
        elif role == "cuantitativo":
            r.update(consistencia_modelo="coherente", riesgo_correlacion="ninguno", validacion_aplicable="no_validado")
        elif role == "verificador":
            r.update(disponibilidad="no_encontrada", precio="sin_precio", discrepancias=["ninguna"], fuentes_consultadas=["paquete"])
        else:
            r.update(objecion="ninguna", severidad="baja", recomendacion="mantener")
        r.update(over)
        out.append(r)
    return {"agente": role, "version_contrato": 1, "run": "runs/x", "unidades": out, "limitaciones": []}


class Contrato(unittest.TestCase):
    def test_los_grupos_salen_del_catalogo_y_el_contrato_los_enumera(self):
        self.assertEqual(ar.GROUPS, sorted({e["market"] for e in mc.CATALOG}))
        for g in ("córners", "tarjetas", "goles por equipo", "hándicap", "doble oportunidad", "empate no válido", "1.ª parte goles"):
            self.assertIn(g, ar.GROUPS)
        for r in ar.ROLES:
            t = ar.contract_text(r)
            self.assertIn("NO vacía", t)
            for k in ar.ENUMS[r]:
                self.assertIn(f"`{k}`", t)

    def test_todos_los_informes_validos_son_completos(self):
        us = units()
        for r in ar.ROLES:
            v = ar.validate_report(r, valid_report(r, us), us, "runs/x")
            self.assertTrue(v["completo"], (r, v["errores"][:2]))
            self.assertEqual((v["esperadas"], v["recibidas"]), (12, 12))


class Validador(unittest.TestCase):
    def setUp(self):
        self.us = units()
        self.rep = valid_report("deportivo", self.us)

    def check(self, rep, role="deportivo"):
        return ar.validate_report(role, rep, self.us, "runs/x")

    def test_unidad_faltante_duplicada_o_no_esperada(self):
        rep = copy.deepcopy(self.rep)
        falta = rep["unidades"].pop()
        v = self.check(rep)
        self.assertEqual((v["completo"], v["faltantes"]), (False, [falta["unit_id"]]))
        rep["unidades"] += [copy.deepcopy(rep["unidades"][0])]
        self.assertTrue(self.check(rep)["duplicadas"])
        rep = copy.deepcopy(self.rep)
        rep["unidades"][0]["unit_id"] = "otro|goles"
        v = self.check(rep)
        self.assertEqual(v["no_esperadas"], ["otro|goles"])
        self.assertFalse(v["valido"])

    def test_texto_libre_campos_extra_y_enumeraciones(self):
        rep = copy.deepcopy(self.rep)
        rep["unidades"][0]["comentario_libre"] = "mi opinión"
        rep["unidades"][1]["solidez"] = "MUY_ALTA"
        rep["unidades"][2]["nota"] = "x" * (ar.NOTE_MAX + 1)
        rep["unidades"][3]["escenario_perdida"] = None
        motivos = {(e["unit_id"], e["campo"]) for e in self.check(rep)["errores"]}
        for i, campo in enumerate(("comentario_libre", "solidez", "nota", "escenario_perdida")):
            self.assertIn((self.us[i]["unit_id"], campo), motivos)

    def test_evidencia_obligatoria_y_con_prefijo_valido(self):
        rep = copy.deepcopy(self.rep)
        rep["unidades"][0]["evidencia"] = []
        rep["unidades"][1]["evidencia"] = ["me parece"]
        campos = [(e["unit_id"], e["campo"]) for e in self.check(rep)["errores"]]
        self.assertIn((self.us[0]["unit_id"], "evidencia"), campos)
        self.assertIn((self.us[1]["unit_id"], "evidencia"), campos)

    def test_excepciones_validas_sin_repetir_y_de_la_unidad(self):
        rep = copy.deepcopy(self.rep)
        eid = self.us[0]["entradas"][0]["id"]
        rep["unidades"][0]["excepciones"] = [{"entry_id": eid, "solidez": "BAJA"}]
        self.assertTrue(self.check(rep)["completo"])
        for malo in ([{"entry_id": "no.existe", "solidez": "BAJA"}], [{"entry_id": eid, "solidez": "ZZZ"}], [{"entry_id": eid, "solidez": "BAJA"}, {"entry_id": eid, "solidez": "ALTA"}], [{"entry_id": eid}]):
            rep["unidades"][0]["excepciones"] = malo
            self.assertFalse(self.check(rep)["completo"], malo)

    def test_cabecera_agente_version_y_run(self):
        for k, v in (("agente", "verificador"), ("version_contrato", 99), ("run", "otro")):
            rep = dict(self.rep, **{k: v})
            self.assertFalse(self.check(rep)["valido"], k)
        self.assertFalse(self.check("no es un objeto")["valido"])


class Coherencia(unittest.TestCase):
    def test_verificador_no_puede_afirmar_un_precio_real_que_el_paquete_no_tiene(self):
        us = units()
        v = ar.validate_report("verificador", valid_report("verificador", us, precio="real_verificado"), us, "runs/x")
        self.assertTrue(any(e["campo"] == "precio" for e in v["errores"]))
        con_real = units(precio="real_verificada")                                           # el fixture no declara el tipo de fuente: sin tipo «casa» no hay precio de casa
        self.assertFalse(ar.validate_report("verificador", valid_report("verificador", con_real, precio="real_verificado"), con_real, "runs/x")["completo"])
        for u in con_real:
            for e in u["entradas"]:
                e["precio"]["tipo"] = "usuario"
        self.assertTrue(ar.validate_report("verificador", valid_report("verificador", con_real, precio="comunicado_usuario"), con_real, "runs/x")["completo"])
        self.assertFalse(ar.validate_report("verificador", valid_report("verificador", con_real, precio="real_verificado"), con_real, "runs/x")["completo"])        # usuario ≠ casa
        for u in con_real:
            for e in u["entradas"]:
                e["precio"]["tipo"] = "casa"
        self.assertTrue(ar.validate_report("verificador", valid_report("verificador", con_real, precio="real_verificado"), con_real, "runs/x")["completo"])
        self.assertFalse(ar.validate_report("verificador", valid_report("verificador", us, precio="comunicado_usuario"), us, "runs/x")["completo"])

    def test_verificador_no_puede_decir_verificada_si_ningun_canal_de_precios_lo_encontro(self):
        us = units()
        v = ar.validate_report("verificador", valid_report("verificador", us, disponibilidad="verificada_en_fuente"), us, "runs/x")
        self.assertTrue(any(e["campo"] == "disponibilidad" for e in v["errores"]))
        con = units(canales={"datos_deportivos": "encontrado", "apifootball (agregador)": "encontrado"})
        self.assertTrue(ar.validate_report("verificador", valid_report("verificador", con, disponibilidad="verificada_en_fuente"), con, "runs/x")["completo"])

    def test_cuantitativo_no_inventa_estimador_ni_validacion(self):
        sin = units(estimador="no_implementado", validacion=None)
        v = ar.validate_report("cuantitativo", valid_report("cuantitativo", sin, consistencia_modelo="coherente"), sin, "runs/x")
        self.assertTrue(any(e["campo"] == "consistencia_modelo" for e in v["errores"]))
        self.assertTrue(ar.validate_report("cuantitativo", valid_report("cuantitativo", sin, consistencia_modelo="sin_estimador"), sin, "runs/x")["completo"])
        v = ar.validate_report("cuantitativo", valid_report("cuantitativo", sin, consistencia_modelo="sin_precio_para_contrastar"), sin, "runs/x")
        self.assertTrue(any(e["campo"] == "consistencia_modelo" for e in v["errores"]))                    # «sin precio para contrastar» exige estimador calculable
        con_est = units()
        self.assertTrue(ar.validate_report("cuantitativo", valid_report("cuantitativo", con_est, consistencia_modelo="sin_precio_para_contrastar"), con_est, "runs/x")["completo"])
        con = units()
        v = ar.validate_report("cuantitativo", valid_report("cuantitativo", con, consistencia_modelo="sin_estimador"), con, "runs/x")
        self.assertTrue(any(e["campo"] == "consistencia_modelo" for e in v["errores"]))
        v = ar.validate_report("cuantitativo", valid_report("cuantitativo", con, validacion_aplicable="validado"), con, "runs/x")
        self.assertTrue(any(e["campo"] == "validacion_aplicable" for e in v["errores"]))

    def test_deportivo_no_pone_solidez_alta_sin_datos(self):
        sin = units(datos="insuficientes")
        v = ar.validate_report("deportivo", valid_report("deportivo", sin, solidez="ALTA"), sin, "runs/x")
        self.assertTrue(any(e["campo"] == "solidez" for e in v["errores"]))
        self.assertTrue(ar.validate_report("deportivo", valid_report("deportivo", sin, solidez="NO_EVALUABLE"), sin, "runs/x")["completo"])


class AuditorYGate(unittest.TestCase):
    def setUp(self):
        self.us = units(n_matches=10)
        self.base = {r: valid_report(r, self.us) for r in ar.ROLES}

    def test_muestra_minima_estratificada_incluye_lo_marcado_por_otros(self):
        reps = copy.deepcopy(self.base)
        reps["deportivo"]["unidades"][4]["solidez"] = "BAJA"
        reps["verificador"]["unidades"][7]["discrepancias"] = ["precio_anomalo"]
        must, flagged = ar.audit_sample_required(self.us, {r: reps[r] for r in ("deportivo", "cuantitativo", "verificador")})
        self.assertEqual(set(flagged), {self.us[4]["unit_id"], self.us[7]["unit_id"]})
        self.assertTrue(set(flagged) <= set(must))
        self.assertGreaterEqual(len(must), ar.AUDIT_SAMPLE_MIN)
        self.assertEqual({u["grupo"] for u in self.us if u["unit_id"] in must}, set(GRUPOS))      # al menos una unidad de cada grupo
        self.assertEqual(must, ar.audit_sample_required(self.us, {r: reps[r] for r in ("deportivo", "cuantitativo", "verificador")})[0])          # determinista

    def test_gate_completa_incompleta_y_no_ejecutada(self):
        self.assertEqual(ar.review_gate(self.us, self.base, "runs/x")["estado"], "COMPLETA")
        self.assertEqual(ar.review_gate(self.us, {}, "runs/x")["estado"], "NO_EJECUTADA")
        falta = dict(self.base, verificador=None)
        g = ar.review_gate(self.us, falta, "runs/x")
        self.assertEqual(g["estado"], "INCOMPLETA")
        self.assertIn({"tipo": "informe_ausente", "rol": "verificador"}, g["incidencias"])

    def test_el_auditor_no_necesita_cubrir_todas_las_unidades_solo_la_muestra(self):
        must, _ = ar.audit_sample_required(self.us, {r: self.base[r] for r in ("deportivo", "cuantitativo", "verificador")})
        self.assertLess(len(must), len(self.us))                       # la muestra es menor que el total
        reps = copy.deepcopy(self.base)
        reps["auditor"]["unidades"] = [u for u in reps["auditor"]["unidades"] if u["unit_id"] in set(must)]
        self.assertEqual(ar.review_gate(self.us, reps, "runs/x")["estado"], "COMPLETA")
        reps["auditor"]["unidades"][0]["objecion"] = "inventada"       # pero un error de esquema sí la deja incompleta
        self.assertEqual(ar.review_gate(self.us, reps, "runs/x")["estado"], "INCOMPLETA")

    def test_el_auditor_con_muestra_insuficiente_deja_la_revision_incompleta(self):
        reps = copy.deepcopy(self.base)
        reps["deportivo"]["unidades"][2]["solidez"] = "BAJA"
        reps["auditor"]["unidades"] = [u for u in reps["auditor"]["unidades"] if u["unit_id"] != self.us[2]["unit_id"]]      # no revisó una unidad marcada
        g = ar.review_gate(self.us, reps, "runs/x")
        self.assertEqual(g["estado"], "INCOMPLETA")
        tipos = {i["tipo"] for i in g["incidencias"]}
        self.assertTrue({"informe_incompleto_o_invalido", "muestra_del_auditor_insuficiente"} & tipos)

    def test_un_error_de_esquema_en_cualquier_rol_deja_la_revision_incompleta(self):
        reps = copy.deepcopy(self.base)
        reps["cuantitativo"]["unidades"][0]["consistencia_modelo"] = "quizás"
        self.assertEqual(ar.review_gate(self.us, reps, "runs/x")["estado"], "INCOMPLETA")

    def _con_objecion(self, **ob):
        rep = copy.deepcopy(self.base["auditor"])
        rep["unidades"][0][ar.OBJECTION_FIELD] = [dict({"entry_id": self.us[0]["entradas"][0]["id"], "agente": "cuantitativo", "campo": "consistencia_modelo", "problema": "dato_citado_incorrecto"}, **ob)]
        return rep

    def test_objeciones_a_agentes_son_opcionales_y_cerradas(self):
        self.assertTrue(ar.validate_report("auditor", self.base["auditor"], self.us, "runs/x")["completo"])         # sin el campo sigue válido
        self.assertTrue(ar.validate_report("auditor", self._con_objecion(), self.us, "runs/x")["completo"])
        self.assertTrue(ar.validate_report("auditor", self._con_objecion(entry_id=None), self.us, "runs/x")["completo"])
        for malo in ({"agente": "auditor"}, {"agente": "inventado"}, {"campo": "solidez"}, {"problema": "texto libre"}, {"entry_id": "no-existe"}, {"entry_id": ["x"]}):
            self.assertFalse(ar.validate_report("auditor", self._con_objecion(**malo), self.us, "runs/x")["valido"], malo)
        dup = self._con_objecion()
        dup["unidades"][0][ar.OBJECTION_FIELD] *= 2
        self.assertFalse(ar.validate_report("auditor", dup, self.us, "runs/x")["valido"])
        extra = self._con_objecion()
        extra["unidades"][0][ar.OBJECTION_FIELD][0]["texto"] = "libre"
        self.assertFalse(ar.validate_report("auditor", extra, self.us, "runs/x")["valido"])
        otro = copy.deepcopy(self.base["deportivo"])
        otro["unidades"][0][ar.OBJECTION_FIELD] = []
        self.assertFalse(ar.validate_report("deportivo", otro, self.us, "runs/x")["valido"])             # solo el auditor lo tiene

    def test_objeciones_generan_conflicto_sin_cambiar_el_estado_del_gate(self):
        reps = dict(self.base, auditor=self._con_objecion())
        g = ar.review_gate(self.us, reps, "runs/x")
        self.assertEqual((g["estado"], g["objeciones_a_agentes"]), ("COMPLETA", 1))
        c = ar.consolidate(self.us, reps)[self.us[0]["unit_id"]]
        self.assertIn("auditor_objeta_a_cuantitativo", c["conflictos"])
        self.assertEqual(len(c["objeciones"]), 1)
        self.assertIn(ar.OBJECTION_FIELD, ar.contract_text("auditor"))
        self.assertNotIn(ar.OBJECTION_FIELD, ar.contract_text("deportivo"))

    def test_consolidacion_conflictos_y_excepciones_por_entrada(self):
        reps = copy.deepcopy(self.base)
        u0 = self.us[0]["unit_id"]
        reps["deportivo"]["unidades"][0].update(solidez="ALTA", excepciones=[{"entry_id": self.us[0]["entradas"][1]["id"], "solidez": "BAJA"}])
        reps["auditor"]["unidades"][0].update(objecion="muestra_debil", severidad="alta", recomendacion="degradar")
        reps["verificador"]["unidades"][0]["discrepancias"] = ["hora"]
        c = ar.consolidate(self.us, reps)[u0]
        self.assertIn("deportivo_ALTA_vs_objecion_grave_del_auditor", c["conflictos"])
        self.assertIn("verificador_reporta_discrepancias", c["conflictos"])
        self.assertEqual(ar.entry_verdict(c, "deportivo", self.us[0]["entradas"][0]["id"]), "ALTA")
        self.assertEqual(ar.entry_verdict(c, "deportivo", self.us[0]["entradas"][1]["id"]), "BAJA")        # la excepción gana


def _run(match_ids=("m1", "m2")):
    """Run temporal mínimo con historial propio (misma competición) y muestra de liga para construir paquetes."""
    import test_league_context as TL
    run = tempfile.mkdtemp()
    ms = [TL.match(mid, apif=str(100 + i)) for i, mid in enumerate(match_ids)]
    TL._dump(os.path.join(run, "inventory.json"), {"matches": ms})
    r = lambda v, gf, ga: {"gf": gf, "ga": ga, "venue": v, "date": "2026-09-01", "ht_goals": [1, 0], "corners": [5, 4], "cards_pts": [2, 3], "sot": [3, 2], "shots": [9, 8], "misma_competicion": True}
    ev = {"history_kind": "apifootball_misma_competicion", "attempts": [{"provider": "apifootball", "resultado": "consultada: 8+8"}],
          "form": {"local": [r("local", i % 3, 1) for i in range(8)], "visitante": [r("visitante", 1, i % 3) for i in range(8)]}}
    TL._dump(os.path.join(run, "matrix.json"), {"matches": {m["match_id"]: ev for m in ms}})
    filas = [TL.fila(i, tarjetas=(1 + i % 3, 2), corners=(4 + i % 4, 3 + i % 3)) | {"fecha": f"2026-08-{1 + i % 28:02d}"} for i in range(60)]
    TL._dump(os.path.join(run, "league_samples", "7.json"), {"league_id": "7", "filas": filas, "resumen": {}})
    return run


class LotesYMezcla(unittest.TestCase):
    def test_lotes_reparten_partidos_completos_sin_perder_unidades(self):
        us = units(n_matches=7)
        got = [ar.batch_units(us, k, 3) for k in (1, 2, 3)]
        self.assertEqual(sorted(u["unit_id"] for b in got for u in b), sorted(u["unit_id"] for u in us))
        self.assertEqual(len({u["match_id"] for u in got[0]}), 3)
        for b in got:
            self.assertEqual(len(b) % len(GRUPOS), 0)          # partidos completos
        with self.assertRaises(ValueError):
            ar.batch_units(us, 4, 3)

    def test_vista_compacta_trae_todas_las_lineas_y_es_mas_corta_que_el_paquete(self):
        us = units(n_matches=2)
        txt = ar.digest_text(us)
        for u in us:
            self.assertIn(u["unit_id"], txt)
            for e in u["entradas"]:
                self.assertIn(e["id"], txt)
        self.assertLess(len(txt), len(json.dumps(us)))

    def test_merge_une_partes_y_rechaza_repetidas_o_de_otro_rol(self):
        us = units(n_matches=4)
        full = valid_report("deportivo", us)
        a, b = dict(full, unidades=full["unidades"][:5]), dict(full, unidades=full["unidades"][5:])
        m = ar.merge_parts("deportivo", [b, a])
        self.assertEqual(len(m["unidades"]), len(us))
        self.assertTrue(ar.validate_report("deportivo", m, us, "runs/x")["completo"])
        with self.assertRaises(ValueError):
            ar.merge_parts("deportivo", [a, a])
        with self.assertRaises(ValueError):
            ar.merge_parts("auditor", [a])

    def test_validar_un_lote_solo_exige_sus_unidades(self):
        us = units(n_matches=4)
        bu = ar.batch_units(us, 1, 2)
        part = valid_report("deportivo", bu)
        self.assertTrue(ar.validate_report("deportivo", part, bu, "runs/x")["completo"])
        self.assertFalse(ar.validate_report("deportivo", part, us, "runs/x")["completo"])


class Paquetes(unittest.TestCase):
    def test_p_modelo_de_las_selecciones_complementarias_suma_uno(self):
        """Hallazgo del piloto: BTTS «sí» y «no» tenían la misma p_modelo. «no» y «menos» son el complemento."""
        run = _run()
        us, _ = ar.build_units(run)
        p = {e["id"]: e["p_modelo"] for u in us if u["match_id"] == "m1" for e in u["entradas"]}
        self.assertAlmostEqual(p["goles.btts.yes"] + p["goles.btts.no"], 1.0, places=3)
        self.assertAlmostEqual(p["goles.total.over.2.5"] + p["goles.total.under.2.5"], 1.0, places=3)
        self.assertAlmostEqual(p["goles.equipo.home.over.0.5"] + p["goles.equipo.home.under.0.5"], 1.0, places=3)
        self.assertAlmostEqual(p["resultado.1x2.home"] + p["resultado.1x2.draw"] + p["resultado.1x2.away"], 1.0, places=2)

    def test_paquete_con_todas_las_entradas_de_cada_grupo_y_hechos_deterministas(self):
        run = _run()
        us, s = ar.build_units(run)
        self.assertEqual(len(us), 2 * len(ar.GROUPS))                                         # una unidad por partido × grupo del catálogo
        por_grupo = {g: sum(1 for e in mc.CATALOG if e["market"] == g) for g in ar.GROUPS}
        for u in us:
            self.assertEqual(len(u["entradas"]), por_grupo[u["grupo"]])                          # TODAS las líneas del grupo
            self.assertEqual(u["resumen"]["entradas"], len(u["entradas"]))
        g = next(u for u in us if u["grupo"] == "goles" and u["match_id"] == "m1")
        self.assertTrue(any(e["p_modelo"] is not None for e in g["entradas"]))                   # el modelo propio aporta probabilidad
        cu = next(u for u in us if u["grupo"] == "córners")
        self.assertTrue(any(e["p_modelo"] is not None for e in cu["entradas"]))
        self.assertTrue(all(0 <= e["p_modelo"] <= 1 for u in us for e in u["entradas"] if e["p_modelo"] is not None))
        self.assertEqual(us[0]["contexto"]["muestra_liga"]["ejecutada"], True)

    def test_cli_paquetes_validate_y_gate(self):
        run = _run()
        run_cli = lambda *a: subprocess.run([sys.executable, SCRIPT, *a], capture_output=True, text=True, cwd=REPO, timeout=120)
        r = run_cli("packages", "--run", run, "--only", "m1")
        self.assertEqual(r.returncode, 0, r.stderr)
        with open(os.path.join(run, "agentes", "paquete.json"), encoding="utf-8") as f:
            pack = json.load(f)
        self.assertEqual({u["match_id"] for u in pack["unidades"]}, {"m1"})
        for role in ar.ROLES:
            self.assertTrue(os.path.exists(os.path.join(run, "agentes", f"contrato_{role}.md")))
        rep = valid_report("deportivo", pack["unidades"])
        rep["run"] = pack["run"]
        bad = os.path.join(run, "agentes", "informe_deportivo.json")
        with open(bad, "w", encoding="utf-8") as f:
            json.dump(rep, f)
        self.assertEqual(run_cli("validate", "--run", run, "--role", "deportivo", "--file", bad).returncode, 0)
        rep["unidades"][0]["solidez"] = "??"
        with open(bad, "w", encoding="utf-8") as f:
            json.dump(rep, f)
        self.assertEqual(run_cli("validate", "--run", run, "--role", "deportivo", "--file", bad).returncode, 1)
        g = run_cli("gate", "--run", run)
        self.assertEqual(g.returncode, 3)                                                       # 3 roles ausentes + uno inválido
        with open(os.path.join(run, "agentes", "validacion.json"), encoding="utf-8") as f:
            self.assertEqual(json.load(f)["estado"], "INCOMPLETA")


class EnLaCobertura(unittest.TestCase):
    def test_sin_revision_el_estado_es_no_ejecutada_y_ninguna_fila_es_apta(self):
        run = _run()
        s = cov.run_coverage(run, write=False)
        self.assertEqual(s["revision_agentes"]["estado"], "NO_EJECUTADA")
        self.assertIn("revisión de agentes: NO_EJECUTADA", s["aviso"])
        self.assertEqual(s["preparacion_para_apostar"]["requisitos_incumplidos"]["revision_agentes_completa"], s["filas"])

    def test_una_revision_completa_de_estos_partidos_cumple_el_requisito_pero_no_hace_apta_ninguna_fila(self):
        run = _run()
        us, _ = ar.build_units(run)
        os.makedirs(os.path.join(run, "agentes"))
        with open(os.path.join(run, "agentes", "validacion.json"), "w", encoding="utf-8") as f:
            json.dump({"estado": "COMPLETA", "partidos_ids": ["m1", "m2"], "incidencias": [], "unidades_esperadas": len(us)}, f)
        s = cov.run_coverage(run, write=False)
        self.assertEqual(s["revision_agentes"]["estado"], "COMPLETA")
        self.assertEqual(s["preparacion_para_apostar"]["requisitos_incumplidos"]["revision_agentes_completa"], 0)
        self.assertEqual(s["preparacion_para_apostar"]["filas_aptas"], 0)                       # el modelo sigue sin validar y no hay precios reales

    def test_una_revision_de_otro_conjunto_de_partidos_no_vale(self):
        run = _run()
        os.makedirs(os.path.join(run, "agentes"))
        with open(os.path.join(run, "agentes", "validacion.json"), "w", encoding="utf-8") as f:
            json.dump({"estado": "COMPLETA", "partidos_ids": ["m1"], "incidencias": [], "unidades_esperadas": 1}, f)
        s = cov.run_coverage(run, write=False)
        self.assertEqual(s["revision_agentes"]["estado"], "INCOMPLETA")
        self.assertEqual(s["preparacion_para_apostar"]["requisitos_incumplidos"]["revision_agentes_completa"], s["filas"])

    def test_la_revision_no_cambia_la_certificacion_de_la_investigacion(self):
        run = _run()
        a = cov.run_coverage(run, write=False)
        self.assertEqual(a["investigacion"]["estado"], cov.run_coverage(run, write=False)["investigacion"]["estado"])
        self.assertNotIn("revision_agentes", a["investigacion"])


if __name__ == "__main__":
    unittest.main()
