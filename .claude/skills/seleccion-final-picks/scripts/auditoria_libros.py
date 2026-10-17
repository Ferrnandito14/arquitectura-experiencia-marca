#!/usr/bin/env python3
"""Auditoría de un libro `ligas-XX-oct-*.xlsx` y, opcionalmente, de su comparativo de resultados. Solo LEE: no modifica ningún archivo entregado.
Lista inconsistencias con severidad (ALTA / MEDIA / BAJA / INFO): textos desactualizados o contradictorios en el Léeme, filas duplicadas, horas que no coinciden con el inventario,
diferencias entre las hojas Catálogo, ligas, rankings y combinadas, reglas de los rankings incumplidas, combinadas mal sumadas, partidos sin probabilidad del modelo, y en el comparativo:
partido en juego sin aviso PROVISIONAL, patas SIN DATO por motivo (cuáles podían resolverse), conflictos de córners falsos y combinadas cuyo estado no sale de sus patas.
Uso:  auditoria_libros.py --book dist/ligas-16-oct-v2.xlsx [--run runs/2026-10-16] [--comparativo dist/comparativo-ligas-16-oct-resultados.xlsx] [--json salida.json] [--md salida.md]"""
import argparse
import json
import os
import re
import sys
from collections import Counter, defaultdict
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

CCS = ZoneInfo("America/Caracas")
MAX_LEG_ODDS = 2.10
MAX_GAP_PP = 15.0
SEV = {"ALTA": 0, "MEDIA": 1, "BAJA": 2, "INFO": 3}
# frases del Léeme que quedaron obsoletas o se contradicen con otra parte del mismo libro / con el comparativo
STALE_PHRASES = [
    (r"no tienen precio en ninguna fuente", "MEDIA", "El Léeme dice que córners, tarjetas, goles por equipo, 1.ª parte y remates no tienen precio en ninguna fuente, pero más abajo dice que TheStatsAPI los cotiza (y la hoja «Precio por casa» los trae)."),
    (r"no se asume A=1, R=2", "MEDIA", "El Léeme dice que no se asume A=1/R=2 para las tarjetas, pero el catálogo, los rankings y el comparativo SÍ liquidan con A=1/R=2 (regla confirmada por la persona usuaria el 13-oct)."),
    (r"tu casa/captura", "BAJA", "El Léeme define «real» como «tu casa/captura»: el diseño exige que ninguna casa concreta sea requisito; los precios de captura son una capa opcional de contraste."),
]


def _norm(v):
    return "" if v is None else str(v).strip()


def _num(v):
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


def leer_libro(path):
    """{hoja: [dict por fila]} y {hoja: [líneas]} para las hojas de una sola columna (Léeme)."""
    import openpyxl
    wb = openpyxl.load_workbook(path, read_only=True, data_only=True)
    sheets, notes = {}, {}
    for ws in wb:
        rows = list(ws.iter_rows(values_only=True))
        if not rows:
            sheets[ws.title], notes[ws.title] = [], []
            continue
        h = list(rows[0])
        notes[ws.title] = [_norm(r[0]) for r in rows if r and r[0] is not None]
        sheets[ws.title] = [dict(zip(h, r)) for r in rows[1:] if any(c is not None for c in r)]
    return sheets, notes, wb.sheetnames


def hojas_de_liga(names):
    """Las hojas entre «Leyenda» y «Ranking seguridad» son las de cada liga."""
    if "Leyenda" in names and "Ranking seguridad" in names:
        return names[names.index("Leyenda") + 1:names.index("Ranking seguridad")]
    return []


class Informe:
    def __init__(self):
        self.items = []

    def add(self, id_, sev, hoja, detalle, n=None, ejemplos=None):
        self.items.append({"id": id_, "severidad": sev, "hoja": hoja, "detalle": detalle, "n": n, "ejemplos": (ejemplos or [])[:5]})

    def ordenado(self):
        return sorted(self.items, key=lambda x: (SEV[x["severidad"]], x["id"]))


# ── auditoría del libro ──
def auditar_libro(path, run=None, informe=None):
    inf = informe or Informe()
    sheets, notes, names = leer_libro(path)
    stem = os.path.splitext(os.path.basename(path))[0]
    leeme = notes.get("Léeme", [])
    arch = next((re.sub(r"^ARCHIVO:\s*", "", t) for t in leeme if t.startswith("ARCHIVO:")), None)
    if arch is None:
        inf.add("B01", "MEDIA", "Léeme", "El Léeme no declara el nombre del archivo (línea «ARCHIVO:»).")
    elif os.path.splitext(arch)[0] != stem:
        inf.add("B01", "MEDIA", "Léeme", f"El Léeme dice «{arch}» pero el archivo se llama «{os.path.basename(path)}»: el texto no se actualizó al versionar.", 1)
    texto = "\n".join(leeme)
    for pat, sev, det in STALE_PHRASES:
        if re.search(pat, texto):
            inf.add("B02", sev, "Léeme", det, 1)
    cat = sheets.get("Catálogo completo", [])
    ligas = hojas_de_liga(names)

    # duplicados
    def dups(rows, key):
        c = Counter(key(r) for r in rows)
        return [k for k, v in c.items() if v > 1]
    d = dups(cat, lambda r: (r.get("Partido"), r.get("Entrada")))
    if d:
        inf.add("B03", "ALTA", "Catálogo completo", "Filas duplicadas (partido, entrada).", len(d), d)
    for nm in ligas:
        d = dups([r for r in sheets[nm] if r.get("Selección")], lambda r: (r.get("Partido"), r.get("Mercado"), r.get("Selección")))
        if d:
            inf.add("B03", "ALTA", nm, "Filas duplicadas (partido, mercado, selección).", len(d), d)
    for nm in ("Ranking seguridad", "Ranking atractivo-cuota"):
        d = dups(sheets.get(nm, []), lambda r: (r.get("Partido"), r.get("Selección")))
        if d:
            inf.add("B03", "ALTA", nm, "La misma pata sale dos veces en el ranking.", len(d), d)

    # horas contra el inventario
    if run and os.path.exists(os.path.join(run, "inventory.json")):
        inv = json.load(open(os.path.join(run, "inventory.json"), encoding="utf-8"))["matches"]
        por_nombre = {f"{m['home_team']} – {m['away_team']}": m for m in inv}
        malas = Counter()
        for nm in ligas + ["Catálogo completo", "Ranking seguridad", "Ranking atractivo-cuota", "Top por liga", "Resumen por partido", "Combinadas"]:
            for r in sheets.get(nm, []):
                m = por_nombre.get(r.get("Partido"))
                if not m or not r.get("Hora Caracas"):
                    continue
                t = datetime.fromisoformat(m["normalized_datetime_utc"].replace("Z", "+00:00")).astimezone(CCS)
                if _norm(r["Hora Caracas"]).lower() != t.strftime("%d-%b %H:%M").lower():
                    malas[(nm, r["Partido"], _norm(r["Hora Caracas"]), t.strftime("%d-%b %H:%M"))] += 1
        if malas:
            inf.add("B04", "ALTA", "varias", "Hora de Caracas distinta de la del inventario (UTC−4).", sum(malas.values()), list(malas)[:5])
        else:
            inf.add("B04", "INFO", "varias", "Todas las horas coinciden con el inventario (UTC−4).")
        # cada partido en una sola hoja de liga y día de Caracas
        en = defaultdict(set)
        for nm in ligas:
            for r in sheets[nm]:
                en[r.get("Partido")].add(nm)
        multi = {k: sorted(v) for k, v in en.items() if len(v) > 1}
        if multi:
            inf.add("B04b", "MEDIA", "ligas", "Un partido aparece en más de una hoja de liga.", len(multi), list(multi.items()))
        sin_hoja = sorted({r["Partido"] for r in cat} - set(en))
        if sin_hoja:
            inf.add("B04c", "MEDIA", "ligas", "Partidos del catálogo sin hoja de liga.", len(sin_hoja), sin_hoja)

    # consistencia entre catálogo, ligas, rankings y combinadas
    catk = {(r["Partido"], r["Etiqueta"]): r for r in cat}

    def comparar(nm, rows, ksel, cuota_col, p_col):
        dif, sin = Counter(), []
        for r in rows:
            if not r.get(ksel):
                continue
            c = catk.get((r.get("Partido"), r[ksel]))
            if c is None:
                sin.append((r.get("Partido"), r[ksel]))
                continue
            for lab, col_h, col_c in (("cuota", cuota_col, "Cuota"), ("P modelo", p_col, "P modelo %"), ("tipo de precio", "Tipo de precio", "Tipo de precio"), ("agentes", "Agentes", "Agentes")):
                if col_h in r and _norm(r.get(col_h)) != _norm(c.get(col_c)):
                    a, b = _num(r.get(col_h)), _num(c.get(col_c))
                    if a is None or b is None or abs(a - b) > 1e-6:
                        dif[lab] += 1
        if sin:
            inf.add("B05", "ALTA", nm, "Filas sin su pata en el Catálogo completo.", len(sin), sin)
        if dif:
            inf.add("B05", "ALTA", nm, "Valores distintos a los del Catálogo completo: " + ", ".join(f"{k} {v}" for k, v in dif.items()), sum(dif.values()))
    for nm in ligas:
        comparar(nm, sheets[nm], "Selección", "Cuota", "P modelo %")
    for nm in ("Ranking seguridad", "Ranking atractivo-cuota", "Top por liga"):
        comparar(nm, sheets.get(nm, []), "Selección", "Cuota", "P modelo %")
    comparar("Combinadas", [r for r in sheets.get("Combinadas", []) if r.get("Selección")], "Selección", "Cuota de la pata", "P modelo de la pata %")

    # reglas declaradas de los rankings y composición por partido
    for nm in ("Ranking seguridad", "Ranking atractivo-cuota"):
        rows = sheets.get(nm, [])
        viol = Counter()
        for r in rows:
            o, brecha = _num(r.get("Cuota")), _num(r.get("Brecha vs 1/cuota (pp)"))
            ag = _norm(r.get("Agentes"))
            if o is None or o > MAX_LEG_ODDS:
                viol["cuota > 2.10 o sin cuota"] += 1
            if o is not None and o < 1.10:
                viol["cuota < 1.10"] += 1
            if brecha is not None and abs(brecha) >= MAX_GAP_PP:
                viol["|brecha| ≥ 15 pp"] += 1
            if ag.startswith(("rechazada", "degradada")):
                viol["rechazada/degradada"] += 1
        if viol:
            inf.add("B06", "ALTA", nm, "Filas que incumplen las reglas que declara el Léeme: " + ", ".join(f"{k} {v}" for k, v in viol.items()), sum(viol.values()))
        por = Counter(r.get("Partido") for r in rows)
        if rows:
            inf.add("B06b", "MEDIA" if max(por.values()) > 2 else "INFO", nm, f"{len(rows)} filas de {len(por)} partidos distintos; máx. {max(por.values())} patas del mismo partido (las patas de un partido no son independientes).", len(por), por.most_common(3))
    # combinadas
    combos = defaultdict(list)
    for r in sheets.get("Combinadas", []):
        if r.get("Opción") is not None:
            combos[(r["Objetivo"], r["Opción"])].append(r)
    malas = []
    for k, rows in combos.items():
        prod = 1.0
        for r in rows:
            prod *= _num(r.get("Cuota de la pata")) or 1.0
        tot = _num(rows[0].get("Cuota total"))
        if tot is not None and abs(prod - tot) / tot > 0.01:
            malas.append((k, round(prod, 3), tot))
        if len({r.get("Partido") for r in rows}) != len(rows):
            malas.append((k, "dos patas del mismo partido"))
        if any((_num(r.get("Cuota de la pata")) or 0) > MAX_LEG_ODDS for r in rows):
            malas.append((k, "pata con cuota > 2.10"))
    if malas:
        inf.add("B07", "ALTA", "Combinadas", "Combinadas cuyo multiplicador o composición no cuadra.", len(malas), malas)
    # partidos sin probabilidad del modelo
    sinp = [r.get("Partido") for nm in ligas for r in sheets[nm] if "sin probabilidad del modelo" in _norm(r.get("Mercado"))]
    if sinp:
        inf.add("B08", "MEDIA", "ligas", "Partidos sin ninguna probabilidad del modelo (muestra insuficiente): sus hojas de liga traen solo una nota.", len(sinp), sinp)
    # cifras del Léeme vs hojas
    m = re.search(r"Cifras: (\d+) unidades, (\d+) partidos, (\d+) filas", texto)
    if m and cat:
        if int(m.group(3)) != len(cat) or int(m.group(2)) != len({r["Partido"] for r in cat}):
            inf.add("B09", "MEDIA", "Léeme", f"Cifras del Léeme ({m.group(2)} partidos, {m.group(3)} filas) distintas de las del Catálogo ({len({r['Partido'] for r in cat})} partidos, {len(cat)} filas).", 1)
    m = re.search(r"\((\d+) patas liquidadas de (\d+) run\(s\): ([^;)]*)", texto)
    if m:
        inf.add("B09b", "INFO", "Léeme", f"La frase «Lo que dicen los datos hasta hoy» usa solo {m.group(2)} run(s) ({m.group(3).strip()}): refleja el registro al generar el libro, no incluye el día del propio libro ni los posteriores.", 1)
    # hojas con mercados repetidos
    if "Mercados extra" in sheets and "Mercados adicionales" in sheets:
        inf.add("B10", "INFO", "Mercados extra / Mercados adicionales", "Dos hojas con nombres casi iguales: «Mercados extra» (mercados del catálogo sin precio de casa) y «Mercados adicionales» (mercados que el catálogo no tiene). Aclarar en la Leyenda.", 1)
    return inf


# ── auditoría del comparativo ──
def auditar_comparativo(path, book_path=None, informe=None):
    import comparativo_resultados as cmp
    inf = informe or Informe()
    sheets, notes, names = leer_libro(path)
    leeme = notes.get("Léeme", [])
    texto = "\n".join(leeme)
    res = sheets.get("Resultados", [])
    sin_final = [r for r in res if _norm(r.get("Estado del resultado")) != "FINALIZADO"]
    if sin_final and "PROVISIONAL" not in texto:
        inf.add("C01", "ALTA", "Léeme", f"{len(sin_final)} partido(s) sin resultado final ({', '.join(_norm(r.get('Partido')) for r in sin_final)}) y el Léeme no avisa que el archivo es PROVISIONAL.", len(sin_final), [(r.get("Partido"), r.get("Estado del resultado")) for r in sin_final])
    elif sin_final:
        inf.add("C01", "INFO", "Léeme", "Hay partidos sin resultado final y el archivo está rotulado PROVISIONAL.", len(sin_final))
    if book_path:
        stem = os.path.basename(book_path)
        if stem not in texto:
            inf.add("C02", "MEDIA", "Léeme", f"El Léeme no cita el libro evaluado «{stem}».", 1)
    cat = sheets.get("Catálogo evaluado", [])
    sd = [r for r in cat if _norm(r.get("Resultado de la pata")) == cmp.NODATA]
    motivos = Counter(re.sub(r"\d+", "#", _norm(r.get("Dato que decide"))) for r in sd)
    if sd:
        resolv = [(m, n) for m, n in motivos.items() if "cero total" in m or "córners #–#" in m or "dato inválido" in m.lower()]
        inf.add("C03", "INFO", "Catálogo evaluado", f"{len(sd)} patas SIN DATO de {len(cat)}; motivos: " + "; ".join(f"{m} ({n})" for m, n in motivos.most_common(6)), len(sd))
        if resolv:
            inf.add("C03b", "ALTA", "Catálogo evaluado", "Patas SIN DATO que se podían resolver (regla anterior a la corrección del 17-oct: un equipo con 0 córners no es dato dudoso).", sum(n for _, n in resolv), resolv)
    fuentes = [_norm(r.get("Fuente del dato (lecturas que confirman)")) for r in cat]
    conf = sum(1 for f in fuentes if "CONFLICTO" in f and "córners" not in f.lower() and "bloques" in f)
    spur = sum(1 for f in fuentes if "CONFLICTO entre bloques" in f)
    if spur:
        inf.add("C04", "MEDIA", "Catálogo evaluado", "El texto de procedencia marca «CONFLICTO entre bloques» en córners cuando solo se comparaba el bloque del partido con el de la 1.ª parte (siempre menor): falso conflicto.", spur)
    # combinadas coherentes con sus patas
    combos = defaultdict(list)
    for r in sheets.get("Combinadas", []):
        if r.get("Opción") is not None:
            combos[(r["Objetivo"], r["Opción"])].append(r)
    malas = []
    for k, rows in combos.items():
        est, _ = cmp.combo_status([_norm(r.get("Resultado de la pata")) for r in rows], [_num(r.get("Cuota de la pata")) or 1.0 for r in rows])
        if est != _norm(rows[0].get("Resultado de la combinada")):
            malas.append((k, est, _norm(rows[0].get("Resultado de la combinada"))))
    if malas:
        inf.add("C05", "ALTA", "Combinadas", "Estado de la combinada distinto del que sale de sus patas.", len(malas), malas)
    # resumen: suma de ganadas+perdidas+anuladas+sin dato = filas del catálogo evaluado
    cuenta = Counter(_norm(r.get("Resultado de la pata")).split(" ")[0] for r in cat)
    inf.add("C06", "INFO", "Catálogo evaluado", "Reparto de resultados: " + ", ".join(f"{k} {v}" for k, v in cuenta.most_common()), len(cat))
    if "Reglas de liquidación" not in names:
        inf.add("C07", "MEDIA", "(falta hoja)", "El comparativo no incluye la hoja «Reglas de liquidación»: no se ve qué reglas se aplicaron ni cuáles están sin confirmar.", 1)
    return inf


def render_md(inf, titulo):
    L = [f"# {titulo}", ""]
    c = Counter(x["severidad"] for x in inf.items)
    L += ["Resumen: " + ", ".join(f"{k} {c.get(k, 0)}" for k in SEV), "", "| Id | Severidad | Hoja | Hallazgo | n |", "|---|---|---|---|---|"]
    for x in inf.ordenado():
        L.append(f"| {x['id']} | {x['severidad']} | {x['hoja']} | {x['detalle'].replace('|', '/')} | {x['n'] if x['n'] is not None else ''} |")
    return "\n".join(L) + "\n"


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--book", required=True)
    ap.add_argument("--run")
    ap.add_argument("--comparativo")
    ap.add_argument("--json")
    ap.add_argument("--md")
    a = ap.parse_args(argv)
    inf = Informe()
    auditar_libro(a.book, a.run, inf)
    if a.comparativo:
        auditar_comparativo(a.comparativo, a.book, inf)
    md = render_md(inf, f"Auditoría de {os.path.basename(a.book)}" + (f" y {os.path.basename(a.comparativo)}" if a.comparativo else ""))
    print(md)
    if a.json:
        with open(a.json, "w", encoding="utf-8") as fh:
            json.dump(inf.ordenado(), fh, ensure_ascii=False, indent=1)
    if a.md:
        with open(a.md, "w", encoding="utf-8") as fh:
            fh.write(md)
    return 0


if __name__ == "__main__":
    sys.exit(main())
