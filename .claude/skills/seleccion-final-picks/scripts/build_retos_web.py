#!/usr/bin/env python3
"""Genera el entregable WEB diario de los retos (×1,20 y ×4) como UNA página HTML autocontenida.

Uso:  build_retos_web.py --run runs/2026-11-01 --dia 2026-11-01 --saldo-x12 26704.02 --saldo-x4 834.35 --out dist/retos-del-dia.html
Lee lo mismo que build_retos_xlsx.py (pool/, agentes/, dossier/) y escribe la página; los datos van incrustados como JSON.
NO CERTIFICADO COMO EXHAUSTIVO: pool de mercado (3-5 casas); no evalúa la cobertura del catálogo ni la preparación para apostar."""
import argparse
import glob
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build_retos_xlsx as bx  # noqa: E402

DIAS = ["lunes", "martes", "miércoles", "jueves", "viernes", "sábado", "domingo"]
MESES = ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre"]


def pata_json(p, rev, just=None):
    k = p["match_id"] + "|" + p["seleccion"]
    r = rev.get(k, {})
    a, v, d = r.get("auditor") or {}, r.get("verificador") or {}, r.get("deportivo") or {}
    return {"hora": p["hora_caracas"][-5:], "partido": p["partido"], "competicion": v.get("competicion", ""), "seleccion": p["seleccion"],
            "cuota": p["cuota"], "p": round(p["p"] * 100, 1), "casas": p["n_casas"],
            "aud": a.get("recomendacion", ""), "sev": a.get("severidad", ""), "riesgo": a.get("riesgo_principal") or a.get("nota") or "",
            "dep": ([round(d["p_min"] * 100), round(d["p_max"] * 100)] if d.get("p_min") is not None else None), "sol": d.get("solidez", ""),
            "ver": "; ".join(v.get("alertas") or []), "just": (just or {}).get(k)}


def tickets_json(grupos, rev, just=None):
    out = []
    for etiqueta, lista in grupos.items():
        for i, t in enumerate(lista[:3], 1):
            out.append({"grupo": etiqueta, "opcion": i, "n": len(t["patas"]), "p": round(t["p_ganar"] * 100, 1), "cuota": t["cuota_base"], "patas": [pata_json(p, rev, just) for p in t["patas"]]})
    return out


def tickets_casa_json(run, rev, just):
    """Tickets ×4 con precios reales de la casa (tickets_casa.py) en el formato de la página; None si no existe."""
    ruta = os.path.join(run, "pool", "tickets_x4_casa.json")
    if not os.path.exists(ruta):
        return None
    d = json.load(open(ruta, encoding="utf-8"))
    aud = os.path.join(run, "agentes", "auditor_casa.json")
    notas = {(t["grupo"], t["opcion"]): t for t in json.load(open(aud, encoding="utf-8")).get("tickets", [])} if os.path.exists(aud) else {}
    out = []
    for g, lista in d["tickets"].items():
        for i, t in enumerate(lista[:3], 1):
            patas = []
            for p in t["patas"]:
                j = pata_json(p, rev, just)
                j["cuota"] = p["cuota"]; j["cuota_ref"] = p.get("cuota_ref"); j["cuenta_bono"] = p.get("cuenta_bono"); j["mercado_casa"] = p.get("mercado_casa", "")
                patas.append(j)
            n = notas.get((g, i), {})
            out.append({"grupo": f"{g}, precios reales de tu casa", "opcion": i, "n": len(patas), "p": round(t["p_ganar"] * 100, 1), "cuota": t["cuota_base"],
                        "bono": t["bono"], "validas": t["patas_validas_bono"], "ev_sin_bono": t["ev_sin_bono"], "ev": t["ev_casa"],
                        "auditor": n.get("recomendacion", ""), "auditor_nota": n.get("nota", ""), "patas": patas})
    return out


def horas_captura(run):
    ts = []
    for f in glob.glob(os.path.join(run, "thestatsapi", "odds", "*.json")):
        try:
            ts.append(json.load(open(f)).get("_consultado_utc"))
        except Exception:
            pass
    ts = sorted(x for x in ts if x)
    return (ts[0], ts[-1]) if ts else (None, None)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--run", required=True); ap.add_argument("--dia", required=True)
    ap.add_argument("--saldo-x12", type=float, required=True); ap.add_argument("--saldo-x4", type=float, required=True)
    ap.add_argument("--dia-plan", default="Día 1"); ap.add_argument("--nota-x12", default=""); ap.add_argument("--nota-x4", default=""); ap.add_argument("--out", default="dist/retos-del-dia.html")
    a = ap.parse_args(argv)
    from datetime import date
    d = date.fromisoformat(a.dia)
    rev = bx.revision(os.path.join(a.run, "agentes"))
    just = bx.leer(os.path.join(a.run, "pool", "justificaciones.json"), {})
    patas = bx.leer(os.path.join(a.run, "pool", "patas.json"))["patas"]
    aud = {k: v.get("auditor") for k, v in rev.items() if v.get("auditor")}
    revision = []
    for k, v in sorted(rev.items(), key=lambda kv: (kv[1].get("auditor") or {}).get("recomendacion", "z")):
        pata = next((p for p in patas if p["match_id"] + "|" + p["seleccion"] == k), None)
        if pata:
            revision.append(pata_json(pata, rev, just))
    c0, c1 = horas_captura(a.run)
    hist = bx.leer(os.path.join(a.run, "pool", "historial_perdidas.json"), [])
    casa = tickets_casa_json(a.run, rev, just)
    datos = {"fecha": f"{DIAS[d.weekday()]} {d.day} de {MESES[d.month - 1]}", "dia_plan": a.dia_plan, "captura": [c0, c1],
             "x12": {"nota": a.nota_x12, "saldo": a.saldo_x12, "tickets": tickets_json(bx.grupos(a.run, "x12"), rev, just)},
             "x4": {"nota": a.nota_x4, "saldo": a.saldo_x4, "bono": bx.BONO, "tickets": tickets_json(bx.grupos(a.run, "x4"), rev, just)},
             "revision": revision, "n_pool": len(patas), "historial": hist}
    if casa:
        datos["x4"]["tickets"] = casa
        datos["x4"]["casa"] = True
    html = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "retos_web_plantilla.html"), encoding="utf-8").read()
    html = html.replace("/*DATOS*/null", json.dumps(datos, ensure_ascii=False))
    os.makedirs(os.path.dirname(a.out) or ".", exist_ok=True)
    open(a.out, "w", encoding="utf-8").write(html)
    print(a.out, len(html) // 1024, "KB")
    return 0


if __name__ == "__main__":
    sys.exit(main())
