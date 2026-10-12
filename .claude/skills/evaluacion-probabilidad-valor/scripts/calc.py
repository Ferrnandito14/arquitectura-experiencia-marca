#!/usr/bin/env python3
"""Calculos deterministas para picks. Uso:
  calc.py implied 1.85
  calc.py novig 1.85 2.05 [3.4]        # cuotas de TODOS los resultados del mismo mercado, misma casa
  calc.py ev 0.58 1.85                 # probabilidad estimada, cuota
  calc.py combo 1.12 1.10 1.25         # multiplicador (solo si las cuotas son de la misma casa)
  calc.py joint 0.8 0.75               # prob. conjunta SOLO si los eventos son independientes
  calc.py freq 9 10                    # frecuencia observada k/n + intervalo Wilson 95%
"""
import sys, math

def wilson(k, n, z=1.96):
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return max(0, c - h), min(1, c + h)

def main(a):
    if len(a) < 2: print(__doc__); return 1
    cmd, v = a[0], [float(x) for x in a[1:]]
    if cmd == "implied":
        print(f"prob_equilibrio_bruta={1/v[0]:.4f}")
    elif cmd == "novig":
        s = sum(1/o for o in v)
        print(f"overround={s:.4f} margen={s-1:.4f}")
        for o in v: print(f"cuota={o} bruta={1/o:.4f} sin_margen_proporcional={(1/o)/s:.4f}")
    elif cmd == "ev":
        p, o = v; print(f"EV_por_unidad={p*o-1:+.4f} cuota_justa={1/p:.3f} (valida solo si p es defendible)")
    elif cmd == "combo":
        m = 1.0
        for o in v: m *= o
        print(f"multiplicador={m:.4f} prob_equilibrio={1/m:.4f}")
    elif cmd == "joint":
        p = 1.0
        for x in v: p *= x
        print(f"prob_conjunta_si_independientes={p:.4f} (con correlacion positiva real suele ser mayor; con negativa, menor)")
    elif cmd == "freq":
        k, n = int(v[0]), int(v[1]); lo, hi = wilson(k, n)
        print(f"frecuencia={k}/{n}={k/n:.3f} Wilson95%=[{lo:.3f},{hi:.3f}] (frecuencia observada, NO probabilidad)")
    else: print(__doc__); return 1
if __name__ == "__main__": sys.exit(main(sys.argv[1:]) or 0)
