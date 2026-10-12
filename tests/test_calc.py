"""Pruebas de calc.py (unittest, ejecuta el script como proceso real)."""
import math
import re
import subprocess
import sys
import unittest
from pathlib import Path

CALC = Path(__file__).resolve().parent.parent / ".claude/skills/evaluacion-probabilidad-valor/scripts/calc.py"


def run(*args):
    p = subprocess.run([sys.executable, str(CALC), *map(str, args)], capture_output=True, text=True, timeout=20)
    return p.returncode, p.stdout, p.stderr


def grab(text, key):
    m = re.search(rf"{re.escape(key)}=\[?(-?[0-9.+]+)(?:,(-?[0-9.]+))?", text)
    return tuple(float(g) for g in m.groups() if g) if m else None


class Valid(unittest.TestCase):
    def ok(self, *a):
        rc, out, err = run(*a)
        self.assertEqual(rc, 0, err)
        self.assertNotIn("Traceback", err + out)
        return out

    def test_implied(self):
        self.assertAlmostEqual(grab(self.ok("implied", "2.0"), "prob_equilibrio_bruta")[0], 0.5)
        self.assertAlmostEqual(grab(self.ok("implied", "1.25"), "prob_equilibrio_bruta")[0], 0.8)

    def test_novig_no_margin(self):
        out = self.ok("novig", "2.0", "2.0")
        self.assertAlmostEqual(grab(out, "margen")[0], 0.0)
        self.assertEqual([float(x) for x in re.findall(r"sin_margen_proporcional=([0-9.]+)", out)], [0.5, 0.5])

    def test_novig_margin_and_sum(self):
        out = self.ok("novig", "1.85", "2.05")
        vals = [float(x) for x in re.findall(r"sin_margen_proporcional=([0-9.]+)", out)]
        self.assertAlmostEqual(sum(vals), 1.0, places=3)
        self.assertAlmostEqual(grab(out, "margen")[0], 1 / 1.85 + 1 / 2.05 - 1, places=4)

    def test_ev(self):
        self.assertAlmostEqual(grab(self.ok("ev", "0.5", "2.0"), "EV_por_unidad")[0], 0.0)
        self.assertAlmostEqual(grab(self.ok("ev", "0.58", "1.85"), "EV_por_unidad")[0], 0.58 * 1.85 - 1, places=4)

    def test_ev_boundaries(self):
        self.assertAlmostEqual(grab(self.ok("ev", "0", "2.0"), "EV_por_unidad")[0], -1.0)
        self.assertIn("cuota_justa=n/a", self.ok("ev", "0", "2.0"))
        self.assertAlmostEqual(grab(self.ok("ev", "1", "2.0"), "EV_por_unidad")[0], 1.0)

    def test_combo(self):
        self.assertAlmostEqual(grab(self.ok("combo", "1.12", "1.12"), "multiplicador")[0], 1.2544)
        self.assertAlmostEqual(grab(self.ok("combo", "1.1", "1.2", "1.5"), "multiplicador")[0], 1.98)

    def test_joint(self):
        self.assertAlmostEqual(grab(self.ok("joint", "0.8", "0.75"), "prob_conjunta_si_independientes")[0], 0.6)
        self.assertIn("independencia", self.ok("joint", "0.8", "0.75"))

    def test_joint_boundaries(self):
        self.assertAlmostEqual(grab(self.ok("joint", "0", "1"), "prob_conjunta_si_independientes")[0], 0.0)
        self.assertAlmostEqual(grab(self.ok("joint", "1", "1"), "prob_conjunta_si_independientes")[0], 1.0)

    def test_freq_symmetric(self):
        lo, hi = grab(self.ok("freq", "5", "10"), "Wilson95%")
        self.assertAlmostEqual(0.5 - lo, hi - 0.5, places=3)

    def test_freq_limits(self):
        for k, n in (("10", "10"), ("0", "10"), ("0", "1"), ("1", "1")):
            lo, hi = grab(self.ok("freq", k, n), "Wilson95%")
            self.assertTrue(0.0 <= lo <= int(k) / int(n) <= hi <= 1.0, (k, n, lo, hi))
        self.assertAlmostEqual(grab(self.ok("freq", "9", "10"), "Wilson95%")[0], 0.596, places=3)

    def test_warnings_present(self):
        self.assertIn("misma casa", self.ok("combo", "1.5", "1.5"))
        self.assertIn("NO probabilidad", self.ok("freq", "1", "2"))


class Invalid(unittest.TestCase):
    def bad(self, *a):
        rc, out, err = run(*a)
        self.assertEqual(rc, 2, f"{a}: rc={rc} out={out} err={err}")
        self.assertNotIn("Traceback", err + out, a)
        self.assertTrue(err.startswith("error:"), a)
        self.assertEqual(out, "", a)

    def test_user_listed_cases(self):
        self.bad("freq", "11", "10")
        self.bad("freq", "0", "0")
        self.bad("implied", "0")

    def test_bad_odds(self):
        for c in ("1", "1.0", "0.5", "-2", "abc", "nan", "inf", "-inf", "1e999", "", "1_5", " 2"):
            self.bad("implied", c)
        self.bad("novig", "2.0", "1.0")
        self.bad("combo", "1.5", "0.9")
        self.bad("ev", "0.5", "1")

    def test_bad_probabilities(self):
        for p in ("-0.1", "1.1", "2", "nan", "inf", "x"):
            self.bad("ev", p, "2.0")
            self.bad("joint", p, "0.5")

    def test_bad_counts(self):
        for k, n in (("-1", "10"), ("1.5", "10"), ("5", "10.0"), ("a", "10"), ("5", "-3"), ("nan", "10"), ("1", "0")):
            self.bad("freq", k, n)

    def test_arg_counts(self):
        self.bad()
        self.bad("implied")
        self.bad("implied", "2", "3")
        self.bad("novig", "2.0")
        self.bad("combo", "1.5")
        self.bad("joint", "0.5")
        self.bad("ev", "0.5")
        self.bad("ev", "0.5", "2", "3")
        self.bad("freq", "1")
        self.bad("freq", "1", "2", "3")

    def test_unknown_command(self):
        self.bad("foo", "1")

    def test_overflow_combo(self):
        self.bad("combo", "1e200", "1e200")

    def test_help_ok(self):
        rc, out, _ = run("--help")
        self.assertEqual(rc, 0)
        self.assertIn("implied", out)


if __name__ == "__main__":
    unittest.main(verbosity=2)
