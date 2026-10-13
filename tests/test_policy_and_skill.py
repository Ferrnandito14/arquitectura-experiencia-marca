"""Pruebas sobre la política de fuentes y las cláusulas obligatorias de las skills/agentes/documentos."""
import json, os, re, unittest
import helpers
import common

ROOT = os.path.normpath(os.path.join(os.path.dirname(__file__), ".."))
SK = os.path.join(ROOT, ".claude", "skills")
read = lambda *p: open(os.path.join(ROOT, *p), encoding="utf-8").read()


class PolicyFile(unittest.TestCase):
    def setUp(self):
        self.pol = common.Policy()

    def test_every_provider_has_reason_and_evidence(self):
        for n, p in self.pol.data["providers"].items():
            self.assertIn(p["status"], ("permitida", "condicional", "excluida"), n)
            self.assertTrue(p.get("reason") and p.get("evidence"), n)

    def test_known_excluded_hosts_are_denied(self):
        for host in ("www.fotmob.com", "www.betexplorer.com", "www.transfermarkt.com", "understat.com", "www.soccerstats.com"):
            with self.assertRaises(common.PolicyError, msg=host):
                self.pol.check(host)

    def test_conditional_hosts_have_limits_and_unknown_denied(self):
        self.pol.check("www.football-data.co.uk")
        self.pol.check("www.apwin.com")
        for n in ("football-data", "apwin"):
            self.assertIn("limits", self.pol.data["providers"][n])
        for host in ("www.flashscore.com", "www.sofascore.com", "www.oddsportal.com", "www.footystats.org", "fbref.com", "refsradar.com"):
            with self.assertRaises(common.PolicyError, msg=host):
                self.pol.check(host)

    def test_policy_documented_in_conformity_doc(self):
        doc = read("docs", "FUENTES-CONFORMIDAD.md")
        for n, p in self.pol.data["providers"].items():
            self.assertIn(p["hosts"][0].split(".")[0].lower(), doc.lower(), n)

    def test_honest_user_agent_constant(self):
        self.assertEqual(common.UA, "football-picks-system/0.1")
        src = "".join(open(os.path.join(helpers.SCRIPTS, f), encoding="utf-8").read() for f in os.listdir(helpers.SCRIPTS) if f.endswith(".py"))
        self.assertNotRegex(src, r"Mozilla/5\.0|Chrome/\d")          # ningún script falsifica un navegador


class OrchestratorClauses(unittest.TestCase):
    def setUp(self):
        self.s = read(".claude", "skills", "seleccion-final-picks", "SKILL.md")

    def test_mandatory_clauses_present(self):
        for clause in (
            "Todo partido confirmado y elegible dentro del alcance de la jornada recibe una evaluación individual (Nivel 1) ANTES de cualquier ranking definitivo",
            "No seleccionar un partido es válido; no investigarlo y afirmar que no ofrece oportunidades no lo es",
            "America/Caracas", "RANKING PROVISIONAL RESTRINGIDO", "Puerta de cobertura", "NO_EVALUABLE_TRAS_INTENTOS", "NOT_CHECKED ≠ NO_EVALUABLE",
            "inventory.py", "level1.py", "coverage_report.py", "batches.py", "sources_policy.json", "football-picks-system/0.1",
            "no falsificar navegador ni evadir CAPTCHA/Cloudflare", "SendMessage", "descriptivas, no probabilidades predictivas",
            "un resumen por competición no es evidencia", "Tercera comprobación", "decide SIEMPRE tú",
            "(1) ¿qué selección parece más probable? (2) ¿cuál tiene mejor relación probabilidad/cuota? (3) ¿cuál es la mejor alternativa global?",
            "PARCIAL_PROXY_OTRA_COMPETICION", "nunca `COMPLETADO`", "Proxy doméstico", "Universo truncado", "cota inferior", "team_aliases.json", "NO_INVESTIGADO_SIN_FUENTE_PERMITIDA", "los agentId sí",
        ):
            self.assertTrue(clause.lower() in self.s.lower(), clause)

    def test_ten_step_flow_and_no_fixed_candidate_limit(self):
        self.assertIn("Flujo (10 pasos)", self.s)
        self.assertNotRegex(self.s.lower(), r"(m[aá]ximo|solo|sólo) (4|cuatro|5|cinco|6|seis) candidatos")

    def test_does_not_claim_unverified_capabilities(self):
        self.assertIn("Agent Teams", self.s)
        self.assertRegex(self.s, r"NO activado ni necesario")


class ProtocolAndAgents(unittest.TestCase):
    def test_protocol_catalog_has_all_mandatory_sources(self):
        t = read(".claude", "skills", "protocolo-multifuente", "SKILL.md").lower()
        for url in ("flashscore.com", "soccerway.com", "worldfootball.net", "betexplorer.com", "fotmob.com", "sofascore.com", "apwin.com",
                    "laliga.com", "ligaportugal.pt", "afa.com.ar", "ligaprofesional.ar", "cbf.com.br", "soccerstats.com", "footystats.org",
                    "understat.com", "fbref.com", "football-data.co.uk", "oddalerts.com", "refsradar.com", "oddsportal.com", "oddschecker.com", "transfermarkt.com"):
            self.assertTrue(url in t, url)
        for st in ("consultada y útil", "consultada con datos insuficientes", "acceso parcial", "acceso fallido", "no consultada"):
            self.assertTrue(st in t, st)
        self.assertTrue("fuente | url o ficha | dato buscado | información obtenida | fecha de consulta | estado | discrepancias | alternativa consultada" in t)

    def test_agents_keep_minimal_tools_and_load(self):
        for n in ("verificador-mercados", "analista-deportivo", "analista-cuantitativo", "auditor-adversarial"):
            t = read(".claude", "agents", n + ".md")
            front = t.split("---")[1]
            self.assertIn("tools: Read, Grep, Glob, Bash, WebFetch, WebSearch, SendMessage", front)
            self.assertNotRegex(front, r"\b(Write|Edit)\b")
            self.assertIn("sources_policy.json", t)
            self.assertIn("Un resumen por competición NO sustituye las filas", t)

    def test_orchestrator_scripts_exist(self):
        for f in ("common.py", "adapters.py", "inventory.py", "level1.py", "coverage_report.py", "batches.py", "sources_policy.json"):
            self.assertTrue(os.path.exists(os.path.join(helpers.SCRIPTS, f)), f)


if __name__ == "__main__":
    unittest.main()
