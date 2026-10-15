#!/usr/bin/env python3
"""Comparativo de un libro `ligas-<día>-oct-v2.xlsx` contra los RESULTADOS REALES: cómo le fue a cada pick (rankings, top por liga y combinadas) y a todo el catálogo con modelo y precio.

Uso:  comparativo_resultados.py --run runs/2026-10-14 --book dist/ligas-14-oct-v2.xlsx --out dist/comparativo-ligas-14-oct-resultados.xlsx [--refresh]
Pasos: (1) resultados finales de cada partido (apifootball get_events: marcador a 90', descanso, córners, tarjetas A=1/R=2, remates, fueras de juego) → `<run>/resultados/resultados.json`;
(2) liquidación de CADA entrada del catálogo con la regla de su mercado (líneas enteras = anulada; hándicap asiático y europeo; sin dato = «sin dato», nunca se inventa);
(3) los picks del libro (tal como se entregaron: misma cuota y mismo texto) se cruzan con el catálogo vivo del run por (partido, selección);
(4) libro de comparación: resumen de acierto, resultados, picks liquidados, combinadas con el resultado de cada pata y el catálogo evaluado (calibración del modelo, filtros de los agentes).
Todo en hora de Caracas. Es una muestra de UN día: sirve para ver el orden de magnitud, no demuestra ventaja ni la descarta (el modelo sigue sin validar)."""
import argparse
import json
import math
import os
import sys
from collections import defaultdict
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import adapters  # noqa: E402
import agent_review as ar  # noqa: E402
import catalog_rankings as cr  # noqa: E402
import common  # noqa: E402
import market_catalog as mc  # noqa: E402
import seguimiento as sg  # noqa: E402

CCS = ZoneInfo("America/Caracas")
WIN, LOSE, VOID, NODATA = "GANADA", "PERDIDA", "ANULADA", "SIN DATO"
FINAL_STATES = ("Finished", "After ET", "After Pen.")       # a 90' + descuento: la prórroga y los penales no cuentan (ver seguimiento.score90)


# ── (1) resultados ──
def _int(v):
    try:
        return int(v)
    except (TypeError, ValueError):
        return None


def parse_result(e):
    """Hechos liquidables de un evento de apifootball (None donde la fuente no los trae: nunca 0 inventado)."""
    h, a = sg.score90(e)
    cards = adapters._card_points(e)
    return {"estado": e.get("match_status") or "", "h": h, "a": a, "h1": _int(e.get("match_hometeam_halftime_score")), "a1": _int(e.get("match_awayteam_halftime_score")),
            "corners": adapters._stat(e, "Corners"), "tarjetas": list(cards) if cards else None, "remates": adapters._stat(e, "Shots Total"),
            "a_puerta": adapters._stat(e, "Shots On Goal"), "fueras": adapters._stat(e, "Offsides"), "arbitro": (e.get("match_referee") or "").strip() or None,
            "local": e.get("match_hometeam_name"), "visitante": e.get("match_awayteam_name"), "fecha": e.get("match_date"), "hora": e.get("match_time")}


def find_api_event(client, key, m):
    """Partido de apifootball de un registro del inventario sin id de la API: mismo día UTC, misma hora (±30 min) y nombres de AMBOS equipos parecidos (no se adivina con uno solo)."""
    import resolve_ids
    day = m["normalized_datetime_utc"][:10]
    t0 = datetime.fromisoformat(m["normalized_datetime_utc"].replace("Z", "+00:00"))
    best = None
    for e in adapters.apif_call(client, key, action="get_events", **{"from": day, "to": day, "timezone": "UTC"}) or []:
        try:
            t = datetime.strptime(f"{e['match_date']} {e['match_time']}", "%Y-%m-%d %H:%M").replace(tzinfo=timezone.utc)
        except (KeyError, ValueError):
            continue
        if abs((t - t0).total_seconds()) > 1800:
            continue
        sc = resolve_ids.sim(m["home_team"], e.get("match_hometeam_name", "")) + resolve_ids.sim(m["away_team"], e.get("match_awayteam_name", ""))
        if sc >= 1.4 and (best is None or sc > best[0]):
            best = (sc, e)
    return best[1] if best else None


def fetch_results(run, refresh=False):
    path = os.path.join(run, "resultados", "resultados.json")
    cur = common.read_json(path, {}) or {}
    inv = {m["match_id"]: m for m in common.read_json(os.path.join(run, "inventory.json"))["matches"]}
    ids = sorted(set(common.read_json(os.path.join(run, "ligas", "ids.json")).values()))
    key = adapters.apif_key()
    if not key:
        raise SystemExit("error: sin clave de apifootball")
    client = common.Client(os.path.join(run, "cache"), os.path.join(run, "sources", "consultas.jsonl"), policy=common.Policy(), min_interval=1.0, ttl=60)
    for mid in ids:
        if mid in cur and cur[mid].get("estado") in FINAL_STATES and not refresh:
            continue
        aid = (inv[mid].get("source_match_ids") or {}).get("apifootball")
        if aid:
            ev = adapters.apif_call(client, key, action="get_events", match_id=aid, timezone="UTC")
            ev = ev if isinstance(ev, list) and ev and isinstance(ev[0], dict) else None
            how = "id del inventario"
        else:
            e0 = find_api_event(client, key, inv[mid])
            ev, aid, how = ([e0], e0["match_id"], "búsqueda por día, hora y nombres de ambos equipos") if e0 else (None, None, None)
        cur[mid] = parse_result(ev[0]) if ev else {"estado": "sin_resultado_en_la_api"}
        cur[mid]["api_match_id"] = aid
        cur[mid]["vinculo"] = how
        cur[mid]["consultado_utc"] = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    common.write_json_atomic(path, cur)
    return cur


# ── (2) liquidación de entradas del catálogo ──
def _cmp(total, line, op):
    if total == line:
        return VOID
    return WIN if ((total > line) == (op == "over")) else LOSE


def _ah(h, a, side, line):
    r = sg.settle_handicap_quarter(h, a, side, line)
    return {"win": WIN, "lose": LOSE, "void": VOID, "half_win": WIN + " (½)", "half_loss": LOSE + " (½)"}[r]


def settle_entry(e, r):
    """(resultado, dato_usado). Regla por mercado; sin dato → (SIN DATO, motivo). 'half' solo en hándicaps de cuarto de línea."""
    if r.get("estado") not in FINAL_STATES or r.get("h") is None or r.get("a") is None:
        return NODATA, "partido sin resultado final"
    h, a, h1, a1 = r["h"], r["a"], r.get("h1"), r.get("a1")
    eid, d, line = e["id"], e["direction"], e.get("line")
    mk = e["market"]
    sel = lambda cond: WIN if cond else LOSE
    if eid.startswith("resultado.1x2."):
        return sel({"home": h > a, "draw": h == a, "away": h < a}[d]), f"{h}–{a}"
    if eid.startswith("resultado.dc."):
        return sel({"1x": h >= a, "12": h != a, "x2": h <= a}[d]), f"{h}–{a}"
    if eid.startswith("resultado.dnb."):
        return (VOID if h == a else sel((h > a) == (d == "home"))), f"{h}–{a}"
    if eid.startswith(("resultado.ah.", "resultado.ah_entero.")):
        return _ah(h, a, d, float(line)), f"{h}–{a}"
    if eid.startswith("resultado.eh."):
        hh = h + float(line)
        return sel({"home": hh > a, "draw": hh == a, "away": hh < a}[d]), f"{h}–{a} (hándicap {line:+g} al local)"
    if eid.startswith("primera_parte.1x2."):
        if h1 is None or a1 is None:
            return NODATA, "sin marcador al descanso"
        return sel({"home": h1 > a1, "draw": h1 == a1, "away": h1 < a1}[d]), f"descanso {h1}–{a1}"
    if eid.startswith("primera_parte.total."):
        if h1 is None or a1 is None:
            return NODATA, "sin marcador al descanso"
        return _cmp(h1 + a1, float(line), d), f"goles 1.ª parte {h1 + a1}"
    if eid.startswith(("goles.total.", "goles.total_entero.")):
        return _cmp(h + a, float(line), d), f"goles {h + a}"
    if eid.startswith("goles.btts."):
        return sel((h > 0 and a > 0) == (d == "yes")), f"{h}–{a}"
    if eid.startswith("goles.equipo."):
        return _cmp(h if e["scope"] == "home" else a, float(line), d), f"goles del equipo {h if e['scope'] == 'home' else a}"
    stat = {"corners": ("corners", "córners"), "cards_pts": ("tarjetas", "tarjetas (A=1, R=2)"), "sot": ("a_puerta", "remates a puerta"), "shots": ("remates", "remates"), "otros": ("fueras", "fueras de juego")}
    for pre, (k, name) in stat.items():
        if eid.startswith(pre + "."):
            v = r.get(k)
            if not v:
                return NODATA, f"la fuente no trae {name} de este partido"
            if pre == "corners" and 0 in v:
                return NODATA, f"córners {v[0]}–{v[1]}: un cero total es dato dudoso de la fuente"
            tot = v[0] + v[1] if e["scope"] == "match" else (v[0] if e["scope"] == "home" else v[1])
            if pre == "otros":
                return NODATA, "fueras de juego sin línea"
            return _cmp(tot, float(line), d), f"{name} {tot}"
    return NODATA, "mercado sin regla de liquidación"


def payoff(res, odds):
    """Beneficio por 1 unidad apostada (teórico, a la cuota del libro)."""
    if res.startswith(WIN):
        return (odds - 1) * (0.5 if "½" in res else 1)
    if res.startswith(LOSE):
        return -0.5 if "½" in res else -1.0
    return 0.0 if res == VOID else None


def hit(res):
    return 1 if res.startswith(WIN) else (0 if res.startswith(LOSE) else None)


# ── (3) picks del libro ──
def read_book(path):
    import openpyxl
    wb = openpyxl.load_workbook(path, read_only=True, data_only=True)
    out = {}
    for name in ("Ranking seguridad", "Ranking atractivo-cuota", "Top por liga", "Combinadas"):
        rows = list(wb[name].iter_rows(values_only=True))
        out[name] = [dict(zip(rows[0], r)) for r in rows[1:] if any(c is not None for c in r)]
    return out


def match_leg(legs_by_key, partido, seleccion):
    return legs_by_key.get((partido, seleccion))


def hhmm(utc_iso):
    return datetime.fromisoformat(utc_iso.replace("Z", "+00:00")).astimezone(CCS).strftime("%d-%b %H:%M")


# ── (4) libro ──
def append_ledger(path, run, legs, inv):
    """Registro acumulado de patas liquidadas (una línea por run+pata) para auditar los filtros con más días: probabilidad del modelo, cuota, estado de agentes y resultado."""
    have = set()
    if os.path.exists(path):
        with open(path, encoding="utf-8") as fh:
            for ln in fh:
                try:
                    d = json.loads(ln)
                    have.add((d["run"], d["leg_id"]))
                except (ValueError, KeyError):
                    pass
    n = 0
    with open(path, "a", encoding="utf-8") as fh:
        for l in legs:
            if l.get("p_modelo") is None or l.get("cuota") is None or l["res"] == NODATA or (run, l["leg_id"]) in have:
                continue
            fh.write(json.dumps({"run": run, "dia": inv[l["match_id"]]["normalized_datetime_utc"][:10], "leg_id": l["leg_id"], "partido_id": l["match_id"], "grupo": l["grupo"], "p": l["p_modelo"], "cuota": l["cuota"],
                                 "precio_tipo": l["precio_tipo"], "agentes": l["agentes"], "elegible": not l["motivos_exclusion"], "res": l["res"]}, ensure_ascii=False) + "\n")
            n += 1
    return n


def build(run, book_path, out_path, refresh=False, ledger=None):
    from openpyxl import Workbook
    from openpyxl.styles import Alignment, Font, PatternFill
    from openpyxl.utils import get_column_letter

    results = fetch_results(run, refresh)
    ids_map = common.read_json(os.path.join(run, "ligas", "ids.json"))
    ids = sorted(set(ids_map.values()))
    cap = (os.path.join(run, "ligas", "partidos_usuario.json"), os.path.join(run, "ligas", "ids.json"))
    units, summary = ar.build_units(run, ids, cap)
    reports = ar.load_reports(run)
    rev = cr.reviewed_prices(run)
    pack = common.read_json(os.path.join(run, "agentes", "paquete.json"), None)
    legs = cr.legs_from_units(units, cr.agent_status(units, reports, rev, (pack or {}).get("unidades") or None), rev)
    ent = {e["id"]: e for e in mc.CATALOG}
    inv = {m["match_id"]: m for m in common.read_json(os.path.join(run, "inventory.json"))["matches"]}
    liga_de = {}
    for u in units:
        liga_de[u["match_id"]] = u.get("liga")
    cap_json = common.read_json(cap[0])
    liga_cap = {}
    for liga, h, a, *_ in cap_json["partidos"]:
        mid = ids_map.get(f"{h}|{a}")
        if mid:
            liga_cap[mid] = liga

    # liquidar todo el catálogo con modelo y precio
    for l in legs:
        eid = l["leg_id"].split("|", 1)[1]
        l["entry_id"] = eid
        l["res"], l["dato"] = settle_entry(ent[eid], results.get(l["match_id"], {}))
    by_key = {(l["partido"], l["etiqueta"]): l for l in legs}
    by_key_nm = {}
    for l in legs:
        by_key_nm.setdefault((l["partido"], l["etiqueta"]), l)

    book = read_book(book_path)
    miss = []

    def settle_row(row, partido_col="Partido", sel_col="Selección", odds_col="Cuota"):
        l = by_key.get((row[partido_col], row[sel_col]))
        if not l:
            miss.append((row[partido_col], row[sel_col]))
            return None
        odds = row.get(odds_col)
        return l, l["res"], l["dato"], odds

    wb = Workbook()
    H = PatternFill("solid", fgColor="1F3864")
    GREEN, RED, GREY, AMBER = (PatternFill("solid", fgColor=c) for c in ("C6EFCE", "FFC7CE", "E7E6E6", "FFEB9C"))

    def sheet(title, headers, rows, widths=None, color_col=None, freeze="A2"):
        ws = wb.create_sheet(title[:31])
        ws.append(headers)
        for c in ws[1]:
            c.font, c.fill, c.alignment = Font(bold=True, color="FFFFFF"), H, Alignment(wrap_text=True, vertical="center")
        for r in rows:
            ws.append(r)
        ws.freeze_panes = freeze
        for i, hd in enumerate(headers, 1):
            w = (widths or {}).get(hd) or min(48, max(10, len(str(hd)) + 2))
            ws.column_dimensions[get_column_letter(i)].width = w
        if color_col:
            ci = headers.index(color_col) + 1
            for row in ws.iter_rows(min_row=2, min_col=ci, max_col=ci):
                for c in row:
                    v = str(c.value or "")
                    c.fill = GREEN if v.startswith(WIN) else RED if v.startswith(LOSE) else AMBER if v == VOID else GREY if v in (NODATA, "SIN DATO") else c.fill
        ws.auto_filter.ref = ws.dimensions
        return ws

    # resultados por partido
    res_rows = []
    for mid in ids:
        r, m = results.get(mid, {}), inv[mid]
        t = hhmm(m["normalized_datetime_utc"])
        if r.get("estado") in FINAL_STATES:
            marcador = f"{r['h']}–{r['a']}" + (" (prórroga/penales después)" if r.get("estado") != "Finished" else "")
            ht = f"{r['h1']}–{r['a1']}" if r.get("h1") is not None and r.get("a1") is not None else None
        else:
            marcador, ht = r.get("estado") or "sin resultado", None
        res_rows.append([t, liga_cap.get(mid) or m.get("competition"), f"{m['home_team']} – {m['away_team']}", marcador, ht,
                         f"{r['corners'][0]}–{r['corners'][1]} ({sum(r['corners'])})" if r.get("corners") else "sin dato",
                         f"{r['tarjetas'][0]}–{r['tarjetas'][1]} ({sum(r['tarjetas'])})" if r.get("tarjetas") else "sin dato",
                         f"{r['a_puerta'][0]}–{r['a_puerta'][1]}" if r.get("a_puerta") else "sin dato", f"{r['remates'][0]}–{r['remates'][1]}" if r.get("remates") else "sin dato",
                         r.get("arbitro"), r.get("estado")])
    # orden cronológico real
    order = {mid: inv[mid]["normalized_datetime_utc"] for mid in ids}
    res_rows = [x for _, x in sorted(zip([order[mid] for mid in ids], res_rows), key=lambda t: t[0])]

    # picks de cada hoja
    def pick_rows(name):
        rows = []
        for row in book[name]:
            s = settle_row(row)
            if not s:
                continue
            l, res, dato, odds = s
            pf = payoff(res, odds) if odds else None
            rows.append((row, l, res, dato, odds, pf))
        return rows

    picks = {n: pick_rows(n) for n in ("Ranking seguridad", "Ranking atractivo-cuota", "Top por liga")}
    base_hdr = ["Hora Caracas", "Liga", "Partido", "Mercado", "Selección", "Cuota", "Tipo de precio", "P modelo %", "Agentes", "Resultado del partido", "Dato que decide", "Resultado del pick", "Beneficio por 1 u (teórico)"]

    def fmt_row(row, l, res, dato, odds, pf, extra=None):
        r = results.get(l["match_id"], {})
        marcador = f"{r['h']}–{r['a']}" if r.get("h") is not None else r.get("estado")
        return ([row.get("Hora Caracas") or hhmm(inv[l["match_id"]]["normalized_datetime_utc"]), row.get("Liga") or liga_cap.get(l["match_id"]), row["Partido"], row.get("Mercado") or l["grupo"], row["Selección"], odds,
                 row.get("Tipo de precio"), row.get("P modelo %"), row.get("Agentes") or l.get("agentes"), marcador, dato, res, None if pf is None else round(pf, 2)])

    pick_sheets = {}
    for n in ("Ranking seguridad", "Ranking atractivo-cuota"):
        pick_sheets[n] = [([row.get("#")] + fmt_row(row, l, res, dato, odds, pf)) for row, l, res, dato, odds, pf in picks[n]]
    top_rows = [[row.get("Ranking")] + fmt_row(row, l, res, dato, odds, pf) for row, l, res, dato, odds, pf in picks["Top por liga"]]

    # combinadas
    combos = defaultdict(list)
    for row in book["Combinadas"]:
        if row.get("Opción") is None:
            continue
        combos[(row["Objetivo"], row["Opción"])].append(row)
    comb_rows, comb_summary = [], []
    for (obj, opt), rows in combos.items():
        legs_res, tot_odds_eff, any_lose, any_nodata = [], 1.0, False, False
        for row in rows:
            l = by_key.get((row["Partido"], row["Selección"]))
            if not l:
                miss.append((row["Partido"], row["Selección"]))
                continue
            res, dato = l["res"], l["dato"]
            legs_res.append((row, l, res, dato))
            if res.startswith(LOSE):
                any_lose = True
            elif res == NODATA:
                any_nodata = True
            elif res.startswith(WIN):
                tot_odds_eff *= row["Cuota de la pata"]
        estado = LOSE if any_lose else (NODATA if any_nodata else WIN)
        head = rows[0]
        n_w = sum(1 for _, _, r_, _ in legs_res if r_.startswith(WIN))
        pf = None if estado == NODATA else ((tot_odds_eff - 1) if estado == WIN else -1.0)
        comb_summary.append((obj, opt, head["Cuota total"], head.get("P gana si fueran independientes %"), head.get("Estado agentes"), head.get("Tipo de cuota"), len(legs_res), n_w, estado, pf))
        for row, l, res, dato in legs_res:
            r = results.get(l["match_id"], {})
            comb_rows.append([obj, opt, head["Cuota total"], estado, None if pf is None else round(pf, 2), row["Hora Caracas"], row["Partido"], row["Selección"], row["Cuota de la pata"],
                              f"{r['h']}–{r['a']}" if r.get("h") is not None else r.get("estado"), dato, res])

    # catálogo evaluado (todas las patas con modelo y precio)
    cat_rows, evald = [], []
    for l in legs:
        if l["p_modelo"] is None or l["cuota"] is None:
            continue
        h_ = hit(l["res"])
        cat_rows.append([hhmm(inv[l["match_id"]]["normalized_datetime_utc"]), liga_cap.get(l["match_id"]), l["partido"], l["grupo"], l["etiqueta"], l["cuota"], l["precio_tipo"], round(l["p_modelo"] * 100, 1),
                         round(100 / l["cuota"], 1), l["agentes"], "sí" if not l["motivos_exclusion"] else "no", l["dato"], l["res"]])
        if l["res"] not in (NODATA,):
            evald.append(l)

    # resúmenes
    def agg(items):
        """items: [(res, odds, p)] → n, ganadas, perdidas, anuladas, % acierto, ROI, p media, 1/cuota media"""
        g = sum(1 for r_, *_ in items if r_.startswith(WIN))
        pdd = sum(1 for r_, *_ in items if r_.startswith(LOSE))
        v = sum(1 for r_, *_ in items if r_ == VOID)
        sd = sum(1 for r_, *_ in items if r_ == NODATA)
        liq = [(r_, o, p) for r_, o, p in items if r_ != NODATA]
        pfs = [payoff(r_, o) for r_, o, _ in liq if o]
        roi = (sum(pfs) / len(pfs)) if pfs else None
        pm = [p for r_, o, p in liq if p is not None and (r_.startswith(WIN) or r_.startswith(LOSE))]
        im = [1 / o for r_, o, p in liq if o and (r_.startswith(WIN) or r_.startswith(LOSE))]
        acc = g / (g + pdd) if (g + pdd) else None
        return [len(items), g, pdd, v, sd, None if acc is None else round(acc * 100, 1), None if roi is None else round(roi * 100, 1),
                None if not pm else round(sum(pm) / len(pm) * 100, 1), None if not im else round(sum(im) / len(im) * 100, 1)]

    def items_from(prows):
        return [(res, odds, (row.get("P modelo %") / 100) if row.get("P modelo %") is not None else None) for row, l, res, dato, odds, pf in prows]

    sum_hdr = ["Conjunto", "Picks", "Ganados", "Perdidos", "Anulados", "Sin dato", "% acierto (ganados / liquidados)", "ROI teórico % (1 u por pick, a la cuota del libro)", "P modelo media %", "Prob. implícita media (1/cuota) %"]
    sum_rows = []
    for n in ("Ranking seguridad", "Ranking atractivo-cuota"):
        sum_rows.append([n] + agg(items_from(picks[n])))
    top_seg = [x for x in picks["Top por liga"] if x[0].get("Ranking") == "Seguridad"]
    top_atr = [x for x in picks["Top por liga"] if x[0].get("Ranking") != "Seguridad"]
    sum_rows.append(["Top por liga — seguridad"] + agg(items_from(top_seg)))
    sum_rows.append(["Top por liga — atractivo-cuota"] + agg(items_from(top_atr)))
    uniq = {}
    for n in picks:
        for row, l, res, dato, odds, pf in picks[n]:
            uniq[(l["leg_id"])] = (res, odds, (row.get("P modelo %") / 100) if row.get("P modelo %") is not None else None)
    sum_rows.append(["Todos los picks de los rankings (sin repetir)"] + agg(list(uniq.values())))

    # combinadas
    comb_hdr = ["Objetivo", "Combinadas", "Ganadas", "Perdidas", "Sin dato", "% acierto", "Beneficio total por 1 u por combinada (teórico)", "P gana media según el libro %", "Patas ganadas / patas"]
    by_obj = defaultdict(list)
    for s_ in comb_summary:
        by_obj[s_[0]].append(s_)
    comb_sum_rows = []
    for obj, lst in by_obj.items():
        g = sum(1 for x in lst if x[8] == WIN)
        pdd = sum(1 for x in lst if x[8] == LOSE)
        sd = sum(1 for x in lst if x[8] == NODATA)
        pfs = [x[9] for x in lst if x[9] is not None]
        pm = [x[3] for x in lst if x[3] is not None]
        comb_sum_rows.append([obj, len(lst), g, pdd, sd, round(g / (g + pdd) * 100, 1) if g + pdd else None, round(sum(pfs), 2) if pfs else None, round(sum(pm) / len(pm), 1) if pm else None,
                              f"{sum(x[7] for x in lst)} / {sum(x[6] for x in lst)}"])
    gg = sum(1 for x in comb_summary if x[8] == WIN)
    pp = sum(1 for x in comb_summary if x[8] == LOSE)
    comb_sum_rows.append(["TODAS", len(comb_summary), gg, pp, sum(1 for x in comb_summary if x[8] == NODATA), round(gg / (gg + pp) * 100, 1) if gg + pp else None,
                          round(sum(x[9] for x in comb_summary if x[9] is not None), 2), None, f"{sum(x[7] for x in comb_summary)} / {sum(x[6] for x in comb_summary)}"])

    # catálogo: por estado de agentes, por familia, por banda de cuota, calibración por banda de p
    def band(x, edges):
        for lo, hi in edges:
            if lo <= x < hi:
                return f"{lo:g}–{hi:g}" if hi < 99 else f"≥ {lo:g}"
    cat_items = [(l["res"], l["cuota"], l["p_modelo"], l) for l in evald]
    # el catálogo trae AMBOS lados de cada línea (más y menos): la tasa global es ~50 % por construcción. Las tablas por filtro usan solo el lado que el modelo favorece (P ≥ 50 %) con cuota ≤ 2.10
    pick_items = [x for x in cat_items if x[2] >= 0.5 and x[1] <= 2.10]

    def table(keyf, title, order=None, items=None):
        grp = defaultdict(list)
        for res, o, p, l in (items if items is not None else pick_items):
            k = keyf(l)
            if k is not None:
                grp[k].append((res, o, p))
        keys = order or sorted(grp)
        return [[f"{title}: {k}"] + agg(grp[k]) for k in keys if k in grp]

    def agente_k(l):
        a = l["agentes"] or ""
        return a.split(":")[0]

    t_ag = table(agente_k, "Estado de agentes", ["aprobada", "objetada", "degradada", "rechazada", "sin_revision", "precio_nuevo_sin_revisar"])
    t_el = table(lambda l: "elegible para combinadas" if not l["motivos_exclusion"] else "no elegible", "Elegibilidad", ["elegible para combinadas", "no elegible"])
    t_gr = table(lambda l: l["grupo"], "Mercado")
    t_bc = table(lambda l: band(l["cuota"], [(1.0, 1.25), (1.25, 1.4), (1.4, 1.6), (1.6, 1.8), (1.8, 2.11)]), "Banda de cuota", ["1–1.25", "1.25–1.4", "1.4–1.6", "1.6–1.8", "1.8–2.11"])
    t_pm = table(lambda l: band(l["p_modelo"] * 100, [(0, 30), (30, 45), (45, 55), (55, 65), (65, 75), (75, 85), (85, 101)]), "P del modelo (%), todas las patas (ambos lados)", ["0–30", "30–45", "45–55", "55–65", "65–75", "75–85", "85–101"], cat_items)
    t_pr = table(lambda l: l["precio_tipo"], "Tipo de precio")
    t_lg = table(lambda l: liga_cap.get(l["match_id"]), "Liga")

    # hoja Léeme
    ws0 = wb.active
    ws0.title = "Léeme"
    n_fin = sum(1 for mid in ids if results.get(mid, {}).get("estado") in FINAL_STATES)
    lines = [
        ("Comparativo de ligas-14-oct-v2.xlsx contra los resultados reales (hora de Caracas)", True),
        (f"Partidos: {len(ids)} del 14-oct; con resultado final: {n_fin}. Resultados y estadísticas: apifootball (marcador a 90', descanso, córners, tarjetas con A=1/R=2, remates).", False),
        ("Qué se evalúa: (1) los picks del libro tal como se entregaron — Ranking seguridad, Ranking atractivo-cuota, Top por liga y Combinadas — con su cuota de referencia; (2) TODAS las patas del catálogo con modelo y precio, para medir calibración y el efecto de los filtros de los agentes.", False),
        ("Liquidación: totales de línea entera y empate no válido = ANULADA (beneficio 0); hándicap asiático de cuarto de línea = mitad ganada/perdida; hándicap europeo aplica la línea al local; 1.ª parte = marcador al descanso. Si la fuente no trae el dato (p. ej. tarjetas de una copa) o trae un cero dudoso de córners (un equipo con 0 córners en todo el partido) queda SIN DATO y no cuenta como acierto ni fallo.", False),
        ("Beneficio/ROI teórico: se apuesta 1 unidad por pick a la cuota que mostraba el libro (referencia de agregador salvo las marcadas «ejecutable»). Las combinadas ganan solo si TODAS sus patas ganan (una pata anulada cuenta con cuota 1). No incluye margen de tu casa ni cuotas que se movieron.", False),
        ("Cómo leer el acierto: % acierto = ganados / (ganados + perdidos). Compáralo con la P media del modelo y con la probabilidad implícita 1/cuota: un modelo bien calibrado acierta cerca de su P media; el mercado, cerca de 1/cuota.", False),
        ("Advertencia de muestra: es UN día y pocas patas por tabla. Sirve para ver el orden de magnitud y detectar fallos de método; NO valida ni descarta el modelo (sigue sin validar) y no es una promesa de resultados futuros.", False),
        ("El libro original no se modifica. Las patas que no se pudieron cruzar con el catálogo del run se listan al final de esta hoja.", False)]
    for t, b in lines:
        ws0.append([t])
        ws0.cell(ws0.max_row, 1).font = Font(bold=b, size=13 if b else 11)
        ws0.cell(ws0.max_row, 1).alignment = Alignment(wrap_text=True, vertical="top")
    if miss:
        ws0.append([f"Sin cruce con el catálogo ({len(miss)}): " + "; ".join(f"{a} / {b}" for a, b in miss[:20])])
    ws0.column_dimensions["A"].width = 150

    sheet("Resumen de acierto", sum_hdr, sum_rows, {"Conjunto": 46})
    ws = wb["Resumen de acierto"]
    ws.append([])
    ws.append(["COMBINADAS"] + [None] * 9)
    ws.append(comb_hdr)
    for r_ in comb_sum_rows:
        ws.append(r_)
    ws.append([])
    ws.append(["CATÁLOGO COMPLETO CON MODELO Y PRECIO (patas liquidables)"] + [None] * 9)
    ws.append(["Las tablas «P del modelo» usan todas las patas (más y menos de cada línea, por eso la tasa global ronda el 50 %); el resto usa solo el lado que el modelo favorece (P ≥ 50 %) con cuota ≤ 2.10."] + [None] * 9)
    ws.append(sum_hdr)
    ws.append(["Todas las patas con modelo y precio (ambos lados)"] + agg([(res, o, p) for res, o, p, _ in cat_items]))
    ws.append(["Lado favorecido por el modelo, cuota ≤ 2.10"] + agg([(res, o, p) for res, o, p, _ in pick_items]))
    for tbl in (t_el, t_ag, t_pm, t_bc, t_gr, t_pr, t_lg):
        for r_ in tbl:
            ws.append(r_)
    for row in ws.iter_rows():
        if row[0].value in ("COMBINADAS", "CATÁLOGO COMPLETO CON MODELO Y PRECIO (patas liquidables)"):
            row[0].font = Font(bold=True, size=12)
    sheet("Resultados", ["Hora Caracas", "Liga", "Partido", "Marcador (90')", "Descanso", "Córners (total)", "Tarjetas A=1/R=2 (total)", "Remates a puerta", "Remates", "Árbitro", "Estado"], res_rows, {"Partido": 42, "Liga": 28})
    sheet("Ranking seguridad", ["#"] + base_hdr, pick_sheets["Ranking seguridad"], {"Partido": 40, "Selección": 34, "Dato que decide": 30}, "Resultado del pick")
    sheet("Ranking atractivo-cuota", ["#"] + base_hdr, pick_sheets["Ranking atractivo-cuota"], {"Partido": 40, "Selección": 34, "Dato que decide": 30}, "Resultado del pick")
    sheet("Top por liga", ["Ranking"] + base_hdr, top_rows, {"Partido": 40, "Selección": 34, "Dato que decide": 30}, "Resultado del pick")
    sheet("Combinadas", ["Objetivo", "Opción", "Cuota total", "Resultado de la combinada", "Beneficio por 1 u (teórico)", "Hora Caracas", "Partido", "Selección", "Cuota de la pata", "Resultado del partido", "Dato que decide", "Resultado de la pata"],
          comb_rows, {"Partido": 40, "Selección": 34, "Dato que decide": 30, "Resultado de la combinada": 16}, "Resultado de la pata")
    ws = wb["Combinadas"]
    ci = 4
    for row in ws.iter_rows(min_row=2, min_col=ci, max_col=ci):
        for c in row:
            v = str(c.value or "")
            c.fill = GREEN if v.startswith(WIN) else RED if v.startswith(LOSE) else GREY
    sheet("Catálogo evaluado", ["Hora Caracas", "Liga", "Partido", "Mercado", "Selección", "Cuota", "Tipo de precio", "P modelo %", "1/cuota %", "Agentes", "Elegible para combinadas", "Dato que decide", "Resultado de la pata"],
          cat_rows, {"Partido": 40, "Selección": 36, "Dato que decide": 30}, "Resultado de la pata")
    wb.save(out_path)
    n_led = append_ledger(ledger, run, legs, inv) if ledger else 0
    return {"ledger_agregadas": n_led, "partidos": len(ids), "finalizados": n_fin, "sin_cruce": miss, "resumen": sum_rows, "combinadas": comb_sum_rows, "catalogo": [["Todas"] + agg([(res, o, p) for res, o, p, _ in cat_items]), ["Lado favorecido"] + agg([(res, o, p) for res, o, p, _ in pick_items])], "por_agentes": t_ag, "por_p": t_pm, "elegibles": t_el, "por_grupo": t_gr}


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--run", required=True)
    ap.add_argument("--book", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--refresh", action="store_true")
    ap.add_argument("--ledger", help="añade las patas liquidadas a este registro acumulado (p. ej. data/ledger_patas.jsonl) para auditar los filtros")
    a = ap.parse_args(argv)
    if os.path.basename(a.out) in ("ligas-14-oct.xlsx", "ligas-14-oct-v2.xlsx"):
        raise SystemExit("el comparativo nunca puede llamarse como un libro original")
    info = build(a.run, a.book, a.out, a.refresh, a.ledger)
    print(json.dumps({k: v for k, v in info.items() if k in ("partidos", "finalizados", "sin_cruce", "ledger_agregadas")}, ensure_ascii=False))
    for k in ("resumen", "combinadas", "catalogo", "por_agentes", "por_p", "elegibles"):
        print(k)
        for r in info[k]:
            print("  ", r)
    return 0


if __name__ == "__main__":
    sys.exit(main())
