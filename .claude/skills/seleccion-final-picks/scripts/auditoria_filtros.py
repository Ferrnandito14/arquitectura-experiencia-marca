#!/usr/bin/env python3
"""¿Los filtros del sistema (revisión de agentes, elegibilidad) separan patas ganadoras de perdedoras MÁS ALLÁ de lo que ya dice la probabilidad?

Lee el registro acumulado `data/ledger_patas.jsonl` (lo alimenta `comparativo_resultados.py --ledger …` día a día). Para cada filtro compara las patas que conserva con las que descarta
usando el EXCESO de acierto = frecuencia real − probabilidad media del modelo (así no se premia a un filtro solo por quedarse con patas más probables).
Un filtro es útil si el exceso de las patas que conserva supera al de las que descarta con un IC 95 % (bootstrap de partidos) que excluye 0. Con pocos días el resultado es «no concluyente».
Solo patas del lado que el modelo favorece (P ≥ 50 %) y cuota ≤ 2.10 (las que el sistema podría mostrar); las anuladas no cuentan.
Uso: auditoria_filtros.py [--ledger data/ledger_patas.jsonl] [--doc docs/AUDITORIA-filtros.md]"""
import argparse
import json
import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common  # noqa: E402

BOOT, SEED, MIN_N = 1000, 7, 100


def load(path):
    out = []
    with open(path, encoding="utf-8") as fh:
        for ln in fh:
            d = json.loads(ln)
            if d["res"].startswith("GANADA"):
                d["y"] = 1
            elif d["res"].startswith("PERDIDA"):
                d["y"] = 0
            else:
                continue
            if d["p"] >= 0.5 and d["cuota"] <= 2.10:
                out.append(d)
    return out


def excess(rows):
    return sum(r["y"] - r["p"] for r in rows) / len(rows) if rows else None


def diff_ci(keep, drop):
    """IC 95 % de exceso(conserva) − exceso(descarta) remuestreando partidos."""
    by = {}
    for r in keep:
        by.setdefault((r["run"], r["partido_id"]), [[], []])[0].append(r)
    for r in drop:
        by.setdefault((r["run"], r["partido_id"]), [[], []])[1].append(r)
    keys = list(by)
    rnd = random.Random(SEED)
    out = []
    for _ in range(BOOT):
        k, d = [], []
        for _i in range(len(keys)):
            g = by[keys[rnd.randrange(len(keys))]]
            k += g[0]
            d += g[1]
        if k and d:
            out.append(excess(k) - excess(d))
    out.sort()
    return (out[int(0.025 * len(out))], out[int(0.975 * len(out))]) if len(out) > 50 else (None, None)


def filters():
    st = lambda r: (r["agentes"] or "").split(":")[0]
    return [("Estado de agentes: aprobada (frente al resto)", lambda r: st(r) == "aprobada"),
            ("Agentes: no rechazada ni degradada (frente a rechazadas y degradadas)", lambda r: st(r) not in ("rechazada", "degradada")),
            ("Agentes: no degradada por el deportivo (BAJA)", lambda r: not (r["agentes"] or "").startswith("degradada")),
            ("Agentes: no rechazada", lambda r: st(r) != "rechazada"),
            ("Elegible para combinadas", lambda r: bool(r["elegible"])),
            ("Precio real o de referencia con casas (frente a sin precio verificable)", lambda r: r["precio_tipo"] in ("ejecutable", "referencia"))]


def report(rows):
    out = []
    for name, f in filters():
        keep, drop = [r for r in rows if f(r)], [r for r in rows if not f(r)]
        rec = {"filtro": name, "n_conserva": len(keep), "n_descarta": len(drop)}
        if len(keep) >= MIN_N and len(drop) >= MIN_N:
            lo, hi = diff_ci(keep, drop)
            rec.update({"acierto_conserva": round(sum(r["y"] for r in keep) / len(keep) * 100, 1), "acierto_descarta": round(sum(r["y"] for r in drop) / len(drop) * 100, 1),
                        "exceso_conserva_pp": round(excess(keep) * 100, 2), "exceso_descarta_pp": round(excess(drop) * 100, 2), "dif_pp_ic95": None if lo is None else [round(lo * 100, 2), round(hi * 100, 2)]})
            rec["veredicto"] = ("útil (separa)" if lo is not None and lo > 0 else "contraproducente (descarta patas mejores)" if hi is not None and hi < 0 else "no concluyente")
        else:
            rec["veredicto"] = "muestra insuficiente"
        out.append(rec)
    return out


def render(res, n, dias):
    L = ["# Auditoría de los filtros del sistema", "", f"Patas liquidadas (lado favorecido por el modelo, cuota ≤ 2.10): **{n}** en {len(dias)} día(s): {', '.join(sorted(dias))}.", "",
         "Exceso = frecuencia real − probabilidad media del modelo (en puntos porcentuales). Un filtro es útil si lo que CONSERVA tiene más exceso que lo que DESCARTA con IC 95 % que excluye 0.", "",
         "| Filtro | Conserva (n) | Descarta (n) | Acierto conserva | Acierto descarta | Exceso conserva | Exceso descarta | Dif. [IC 95 %] | Veredicto |", "|---|---|---|---|---|---|---|---|---|"]
    for r in res:
        L.append(f"| {r['filtro']} | {r['n_conserva']} | {r['n_descarta']} | {r.get('acierto_conserva', '—')} | {r.get('acierto_descarta', '—')} | {r.get('exceso_conserva_pp', '—')} | {r.get('exceso_descarta_pp', '—')} | {r.get('dif_pp_ic95', '—')} | {r['veredicto']} |")
    L += ["", "Lectura: «no concluyente» significa que con estos días no se puede afirmar que el filtro ayude ni que estorbe; el registro sigue creciendo (cada día liquidado se añade con `comparativo_resultados.py --ledger`)."]
    return "\n".join(L) + "\n"


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--ledger", default="data/ledger_patas.jsonl")
    ap.add_argument("--doc")
    a = ap.parse_args(argv)
    rows = load(a.ledger)
    res = report(rows)
    if a.doc:
        with open(a.doc, "w", encoding="utf-8") as f:
            f.write(render(res, len(rows), {r["dia"] for r in rows}))
    for r in res:
        print(r)
    return 0


if __name__ == "__main__":
    sys.exit(main())
