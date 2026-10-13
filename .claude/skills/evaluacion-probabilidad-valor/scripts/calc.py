#!/usr/bin/env python3
"""Calculos deterministas para picks de futbol.

Uso:
  calc.py implied C                 prob. de equilibrio bruta = 1/C           (C > 1)
  calc.py novig C1 C2 [C3 ...]      cuotas de TODOS los resultados del mismo mercado y misma casa (>=2, cada C > 1)
  calc.py ev P C                    EV teorico por unidad = P*C - 1           (0 <= P <= 1, C > 1)
  calc.py combo C1 C2 [...]         multiplicador (>=2 cuotas, cada C > 1). Solo equivale a un ticket real
                                    si TODAS las cuotas son de la misma casa y el ticket existe alli.
  calc.py joint P1 P2 [...]         producto de probabilidades (>=2, cada 0 <= P <= 1). Solo es la
                                    probabilidad conjunta si los eventos son independientes.
  calc.py freq K N                  frecuencia observada K/N (enteros, N > 0, 0 <= K <= N) + Wilson 95%

Errores de uso o de entrada: mensaje en stderr y codigo de salida 2. Exito: 0.
Un resultado matematico NO demuestra que un pick tenga valor: P debe estar justificada aparte.
"""
import math
import re
import sys

USAGE = __doc__.split("\n\n")[1] if "\n\n" in __doc__ else __doc__
_INT = re.compile(r"^[0-9]+$")


class InputError(Exception):
    pass


def num(text, name):
    if "_" in text or text.strip() != text or not text:
        raise InputError(f"{name}: '{text}' no es un numero valido")
    try:
        x = float(text)
    except ValueError:
        raise InputError(f"{name}: '{text}' no es un numero")
    if not math.isfinite(x):
        raise InputError(f"{name}: '{text}' no es un numero finito")
    return x


def odds(text, name="cuota"):
    x = num(text, name)
    if x <= 1.0:
        raise InputError(f"{name}: la cuota decimal debe ser > 1 (recibido {text})")
    return x


def prob(text, name="probabilidad"):
    x = num(text, name)
    if not 0.0 <= x <= 1.0:
        raise InputError(f"{name}: la probabilidad debe estar en [0, 1] (recibido {text})")
    return x


def count(text, name):
    if not _INT.match(text):
        raise InputError(f"{name}: debe ser un entero no negativo (recibido '{text}')")
    return int(text)


def need(args, lo, hi, cmd):
    if len(args) < lo or (hi is not None and len(args) > hi):
        rango = f"{lo}" if lo == hi else (f"al menos {lo}" if hi is None else f"{lo} a {hi}")
        raise InputError(f"'{cmd}' requiere {rango} argumento(s); recibidos {len(args)}")


def finite(x, what):
    if not math.isfinite(x):
        raise InputError(f"{what}: resultado fuera de rango numerico")
    return x


def wilson(k, n, z=1.96):
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return max(0.0, c - h), min(1.0, c + h)


# --- API importable (usada por level1.py; la CLI de abajo sólo valida y formatea) ---
def implied_prob(c):
    """Probabilidad de equilibrio bruta = 1/cuota decimal (c > 1)."""
    return 1 / c


def novig_probs(cuotas):
    """(overround, [prob sin margen proporcional]) para todas las selecciones de un mismo mercado y casa."""
    s = sum(1 / o for o in cuotas)
    return s, [(1 / o) / s for o in cuotas]


def ev_unit(p, c):
    """EV teórico por unidad = p*c - 1. Sólo es válido si p es defendible."""
    return p * c - 1


def combo_odds(cuotas):
    m = 1.0
    for o in cuotas:
        m *= o
    return m


def joint_prob(probs):
    """Producto: sólo es la probabilidad conjunta bajo independencia."""
    p = 1.0
    for x in probs:
        p *= x
    return p


def run(argv):
    if not argv:
        raise InputError("falta el comando")
    cmd, a = argv[0], argv[1:]
    out = []
    if cmd == "implied":
        need(a, 1, 1, cmd)
        c = odds(a[0])
        out.append(f"prob_equilibrio_bruta={implied_prob(c):.4f}")
    elif cmd == "novig":
        need(a, 2, None, cmd)
        v = [odds(x, f"cuota {i+1}") for i, x in enumerate(a)]
        s, nv = novig_probs(v)
        out.append(f"overround={s:.4f} margen={s-1:.4f}")
        for o, q in zip(v, nv):
            out.append(f"cuota={o:g} bruta={implied_prob(o):.4f} sin_margen_proporcional={q:.4f}")
        out.append("nota: metodo proporcional (aproximacion); exige todas las selecciones del mismo mercado y casa")
    elif cmd == "ev":
        need(a, 2, 2, cmd)
        p, c = prob(a[0]), odds(a[1])
        fair = f"{1/p:.3f}" if p > 0 else "n/a"
        out.append(f"EV_por_unidad={ev_unit(p, c):+.4f} cuota_justa={fair}")
        out.append("nota: valido solo si P es una estimacion defendible; 0 o 1 absolutos exigen justificacion extraordinaria")
    elif cmd == "combo":
        need(a, 2, None, cmd)
        m = finite(combo_odds([odds(x, f"cuota {i+1}") for i, x in enumerate(a)]), "multiplicador")
        out.append(f"multiplicador={m:.4f} prob_equilibrio={1/m:.4f}")
        out.append("nota: ticket real solo si todas las cuotas son de la misma casa y la combinacion existe alli")
    elif cmd == "joint":
        need(a, 2, None, cmd)
        p = joint_prob([prob(x, f"probabilidad {i+1}") for i, x in enumerate(a)])
        out.append(f"prob_conjunta_si_independientes={p:.4f}")
        out.append("nota: el producto exige independencia; con correlacion (mismo partido/equipo/arbitro) no es valido")
    elif cmd == "freq":
        need(a, 2, 2, cmd)
        k, n = count(a[0], "K"), count(a[1], "N")
        if n <= 0:
            raise InputError("N debe ser > 0")
        if k > n:
            raise InputError(f"K ({k}) no puede ser mayor que N ({n})")
        lo, hi = wilson(k, n)
        out.append(f"frecuencia={k}/{n}={k/n:.3f} Wilson95%=[{lo:.3f},{hi:.3f}]")
        out.append("nota: frecuencia observada, NO probabilidad")
    else:
        raise InputError(f"comando desconocido: '{cmd}'")
    return out


def main(argv):
    if argv and argv[0] in ("-h", "--help"):
        print(__doc__)
        return 0
    try:
        lines = run(argv)
    except InputError as e:
        print(f"error: {e}\n\n{USAGE}", file=sys.stderr)
        return 2
    print("\n".join(lines))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
