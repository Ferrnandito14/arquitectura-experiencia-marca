#!/usr/bin/env python3
"""Informe del rol cuantitativo generado por REGLA FIJA (sin agente ni tokens).

Para cada unidad del paquete compara `p_modelo` de cada línea con la probabilidad de mercado SIN margen
(`precio.p_mercado.p`); si la línea no la trae y es una línea simple, con 1/cuota. En líneas enteras y hándicap
europeo `p_modelo` es P(gana | sin devolución) y 1/cuota incluye la devolución: solo se contrasta contra la P de
mercado sin margen. Cuotas planas (p_mercado 0.50) no informan. No calcula EV ni afirma validación.

Uso:  cuantitativo_regla.py --run runs/2026-10-26 [--batch k/N] [--out RUTA]
Salida: JSON del contrato del cuantitativo; se valida con `agent_review.py validate --role cuantitativo`."""
import argparse
import json
import os
import sys

UMBRAL_PP = 0.15          # «discrepa_del_mercado» solo con brecha >= 15 pp
FRACCION_UNIDAD = 0.25    # la unidad discrepa si >= 25 % de sus líneas contrastables discrepan
GRUPOS_ENTEROS = ("goles.total_entero", "resultado.ah_entero", "resultado.eh")


def _prefijo(entry_id):
    return ".".join(entry_id.split(".")[:2])


def comparador(entry):
    """P de mercado a usar para la línea, o None si no hay con qué contrastar."""
    precio = entry.get("precio") or {}
    pm = precio.get("p_mercado")
    p = pm.get("p") if isinstance(pm, dict) else pm
    if p is not None:
        if abs(p - 0.5) < 1e-9:      # par plano: no informa
            return None
        return float(p)
    if _prefijo(entry["id"]) in GRUPOS_ENTEROS:
        return None
    cuota = precio.get("cuota")
    return 1.0 / cuota if cuota else None


def clasificar_linea(entry, umbral=UMBRAL_PP):
    if entry.get("estimador") == "no_implementado":
        return "sin_estimador", None
    pmod = entry.get("p_modelo")
    if pmod is None:
        return "datos_insuficientes", None
    ref = comparador(entry)
    if ref is None:
        return "sin_precio_para_contrastar", None
    brecha = pmod - ref
    return ("discrepa_del_mercado" if abs(brecha) >= umbral else "coherente"), brecha


def veredicto_unidad(unidad, umbral=UMBRAL_PP, fraccion=FRACCION_UNIDAD):
    cats = {}
    brechas = {}
    for e in unidad["entradas"]:
        c, b = clasificar_linea(e, umbral)
        cats[e["id"]] = c
        if b is not None:
            brechas[e["id"]] = b
    valores = list(cats.values())
    contrastables = [v for v in valores if v in ("coherente", "discrepa_del_mercado")]
    if contrastables:
        n_disc = sum(1 for v in contrastables if v == "discrepa_del_mercado")
        v = "discrepa_del_mercado" if n_disc / len(contrastables) >= fraccion else "coherente"
    elif "sin_precio_para_contrastar" in valores:
        v = "sin_precio_para_contrastar"
    elif "datos_insuficientes" in valores:
        v = "datos_insuficientes"
    else:
        v = "sin_estimador"
    excepciones = [{"entry_id": i, "consistencia_modelo": c} for i, c in cats.items() if c != v]
    return v, cats, brechas, excepciones


def entrada_unidad(unidad, umbral=UMBRAL_PP, fraccion=FRACCION_UNIDAD):
    v, cats, brechas, excepciones = veredicto_unidad(unidad, umbral, fraccion)
    cuenta = {}
    for c in cats.values():
        cuenta[c] = cuenta.get(c, 0) + 1
    maxb = max((abs(b) for b in brechas.values()), default=None)
    partes = [f"{n} {c}" for c, n in sorted(cuenta.items(), key=lambda kv: -kv[1])]
    nota = "Regla fija: " + "; ".join(partes)
    if maxb is not None:
        nota += f"; brecha máx {maxb * 100:.1f} pp"
    validaciones = {(e.get("validacion") or "") for e in unidad["entradas"]}
    return {
        "unit_id": unidad["unit_id"],
        "consistencia_modelo": v,
        "riesgo_correlacion": "mismo_partido",
        "validacion_aplicable": "parcial" if "parcial" in validaciones else "no_validado",
        "nota": nota[:200],
        "excepciones": excepciones,
        "evidencia": [f"paquete:{unidad['unit_id']}"],
    }


def construir(paquete, ids_unidades=None):
    unidades = [u for u in paquete["unidades"] if ids_unidades is None or u["unit_id"] in ids_unidades]
    return {
        "agente": "cuantitativo",
        "version_contrato": 1,
        "run": paquete.get("run"),
        "unidades": [entrada_unidad(u) for u in unidades],
        "limitaciones": [
            "Informe generado por regla fija (cuantitativo_regla.py), sin juicio de agente.",
            f"Umbral de discrepancia {UMBRAL_PP * 100:.0f} pp; la unidad discrepa si >= {FRACCION_UNIDAD * 100:.0f} % de sus líneas contrastables discrepan.",
            "Modelo sin validar suficientemente: las brechas indican desacuerdo con el mercado, no ventaja.",
            "Líneas enteras y hándicap europeo se contrastan solo contra la P de mercado sin margen.",
        ],
    }


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--run", required=True)
    ap.add_argument("--batch", help="k/N: solo las unidades de ese lote (por partido, en el orden del paquete)")
    ap.add_argument("--out")
    a = ap.parse_args(argv)
    ruta = os.path.join(a.run, "agentes", "paquete.json")
    paquete = json.load(open(ruta, encoding="utf-8"))
    ids = None
    if a.batch:
        k, n = (int(x) for x in a.batch.split("/"))
        partidos = []
        for u in paquete["unidades"]:
            if u["match_id"] not in partidos:
                partidos.append(u["match_id"])
        tam = -(-len(partidos) // n)
        sel = set(partidos[(k - 1) * tam:k * tam])
        ids = {u["unit_id"] for u in paquete["unidades"] if u["match_id"] in sel}
    informe = construir(paquete, ids)
    out = a.out or os.path.join(a.run, "agentes", "informe_cuantitativo.json")
    with open(out, "w", encoding="utf-8") as fh:
        json.dump(informe, fh, ensure_ascii=False, indent=1)
    print(f"{len(informe['unidades'])} unidades -> {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
