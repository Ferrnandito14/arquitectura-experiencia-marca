#!/usr/bin/env python3
"""Re-revisión parcial de unidades: valida un informe PARCIAL (solo las unidades re-revisadas) superpuesto al informe fusionado del rol, y lo fusiona.
Uso:  patch_review.py validate --run R --role X --patch parche.json --units unidades.json   ·   patch_review.py merge --run R --role X --patch p1.json [p2.json …]"""
import argparse, json, os, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import agent_review as ar


def _units(run):
    ids = json.load(open(os.path.join(run, "ligas", "ids.json")))
    return ar.build_units(run, list(ids.values()))[0]


def _overlay(base, patches):
    new = {u["unit_id"]: u for p in patches for u in p.get("unidades", [])}
    out = dict(base)
    out["unidades"] = [new.get(u["unit_id"], u) for u in base["unidades"]] + [u for k, u in new.items() if k not in {x["unit_id"] for x in base["unidades"]}]
    return out, set(new)


def main():
    a = argparse.ArgumentParser()
    a.add_argument("cmd", choices=("validate", "merge"))
    a.add_argument("--run", required=True)
    a.add_argument("--role", required=True)
    a.add_argument("--patch", nargs="+", required=True)
    a.add_argument("--units")
    a = a.parse_args()
    base = json.load(open(os.path.join(a.run, "agentes", f"informe_{a.role}.json")))
    patches = [json.load(open(p)) for p in a.patch]
    merged, touched = _overlay(base, patches)
    units = _units(a.run)
    v = ar.validate_report(a.role, merged, units, a.run)
    want = set(json.load(open(a.units))) if a.units else touched
    errs = [e for e in v["errores"] if (e.get("unit_id") if isinstance(e, dict) else None) in want]
    print(json.dumps({"unidades_parche": len(touched), "esperadas_sin_cubrir": sorted(want - touched)[:5], "errores_en_parche": errs[:10], "n_errores_parche": len(errs),
                      "valido_global": v["valido"], "completo_global": v["completo"]}, ensure_ascii=False, indent=1))
    if a.cmd == "merge":
        if errs or want - touched:
            sys.exit("parche inválido o incompleto: no se fusiona")
        json.dump(merged, open(os.path.join(a.run, "agentes", f"informe_{a.role}.json"), "w"), ensure_ascii=False, indent=1)
        print("fusionado")


if __name__ == "__main__":
    main()
