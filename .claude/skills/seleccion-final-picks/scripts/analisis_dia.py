#!/usr/bin/env python3
"""Análisis del día en curso de un libro «ligas-XX-oct»: picks de los rankings ya liquidados (acertados/fallados), picks de partidos EN VIVO con su probabilidad de cumplirse
(condicionada a marcador, córners y tarjetas actuales y al tiempo que queda) y picks PENDIENTES ordenados de mejor a peor, con la P del modelo y una P ajustada al régimen del día
(factor de goles reales/esperados de los partidos ya terminados: EXPLORATORIO; el análisis fuera de muestra 14–16 oct mostró que este tipo de factor NO mejora, por eso se muestran ambas).
Probabilidad en vivo: goles ~ Poisson con las tasas del modelo propio (api_detalle.model_params) escaladas por el tiempo restante; córners/tarjetas ~ Poisson con la media implícita en la P del modelo
(se invierte P(más de L) = p). Es una APROXIMACIÓN: no ve rojas, lesiones ni cambios tácticos, y los minutos de la API pueden ir atrasados.
Salida: dist/analisis-<libro>-<HHMM>.xlsx (hojas Resumen, Terminados, En vivo, Pendientes, Tus tickets) y JSON en --out-json. No toca el registro oficial.
Uso:  analisis_dia.py --run runs/2026-10-17 --book dist/ligas-17-oct-v3.xlsx --cmp <comparativo provisional.xlsx> [--tickets runs/2026-10-17/seguimiento/tickets_abiertos.json] [--out ...]"""
import argparse
import json
import math
import os
import re
import sys
from collections import defaultdict
from datetime import datetime, timedelta, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import adapters  # noqa: E402
import api_detalle  # noqa: E402
import common  # noqa: E402
import leg_model  # noqa: E402
import live_prob  # noqa: E402
import seguimiento as sg  # noqa: E402

CARACAS = timezone(timedelta(hours=-4))
TOTAL_MIN = 95.0
MAXK = 14


def pois_pmf(lam, n=MAXK):
    p = [math.exp(-lam)]
    for k in range(1, n):
        p.append(p[-1] * lam / k)
    return p


def lambda_from_p(line, p, over=True):
    """Media de un Poisson tal que P(X > line) = p (over) o P(X < line) = p (under). Bisección; None si no existe."""
    f = (lambda lam: 1 - sum(pois_pmf(lam, 60)[:int(math.floor(line)) + 1])) if over else (lambda lam: sum(pois_pmf(lam, 60)[:int(math.ceil(line))]))
    lo, hi = 0.01, 40.0
    for _ in range(60):
        mid = (lo + hi) / 2
        v = f(mid)
        if (v < p) == over:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2


def parse_entry(eid):
    """('tipo', lado, op, linea) de un entry_id del catálogo."""
    s = eid.split(".")
    if s[0] == "goles" and s[1] == "total":
        return "goles_total", None, s[2], float(".".join(s[3:]))
    if s[0] == "goles" and s[1] == "equipo":
        return "goles_equipo", s[2], s[3], float(".".join(s[4:]))
    if s[0] == "goles" and s[1] == "btts":
        return "btts", None, s[2], None
    if s[0] == "resultado" and s[1] == "1x2":
        return "1x2", s[2], None, None
    if s[0] == "resultado" and s[1] == "dc":
        return "dc", s[2], None, None
    if s[0] == "resultado" and s[1] == "dnb":
        return "dnb", s[2], None, None
    if s[0] == "resultado" and s[1] == "ah":
        return "ah", s[2], None, float(".".join(s[3:]))
    if s[0] == "primera_parte" and s[1] == "total":
        return "pp_total", None, s[2], float(".".join(s[3:]))
    if s[0] == "primera_parte" and s[1] == "1x2":
        return "pp_1x2", s[2], None, None
    if s[0] == "corners" and s[1] == "total":
        return "corners_total", None, s[2], float(".".join(s[3:]))
    if s[0] == "corners" and s[1] == "equipo":
        return "corners_equipo", s[2], s[3], float(".".join(s[4:]))
    if s[0] == "cards_pts" and s[1] == "total":
        return "cards_total", None, s[2], float(".".join(s[3:]))
    return None


def goal_dist(lh, la, f, cur_h, cur_a):
    """{(h,a): prob} del marcador final dado el actual y la fracción de partido que queda."""
    ph, pa = pois_pmf(lh * f), pois_pmf(la * f)
    return {(cur_h + i, cur_a + j): ph[i] * pa[j] for i in range(MAXK) for j in range(MAXK)}


def prob_pick(eid, p_modelo, ctx):
    """P de que el pick se cumpla. ctx: dict con h, a, f (fracción que queda), lh, la, share, corners (h,a)|None, cards (h,a)|None, minute, h1, a1, fin1 (1.ª parte terminada)."""
    t = parse_entry(eid)
    if not t:
        return None
    kind, lado, op, line = t
    f = ctx["f"]
    if kind in ("goles_total", "goles_equipo", "btts", "1x2", "dc", "dnb", "ah"):
        if ctx.get("lh") is None:
            return None
        g = goal_dist(ctx["lh"], ctx["la"], f, ctx["h"], ctx["a"])
        tot = sum(g.values())
        if kind == "goles_total":
            return sum(p for (x, y), p in g.items() if ((x + y) > line) == (op == "over")) / tot
        if kind == "goles_equipo":
            return sum(p for (x, y), p in g.items() if (((x if lado == "home" else y) > line) == (op == "over"))) / tot
        if kind == "btts":
            yes = sum(p for (x, y), p in g.items() if x > 0 and y > 0) / tot
            return yes if op == "yes" else 1 - yes
        if kind == "1x2":
            return sum(p for (x, y), p in g.items() if (x > y if lado == "home" else (y > x if lado == "away" else x == y))) / tot
        if kind == "dc":
            return sum(p for (x, y), p in g.items() if ((x >= y) if lado == "1x" else ((y >= x) if lado == "x2" else x != y))) / tot
        if kind == "dnb":
            w = sum(p for (x, y), p in g.items() if (x > y if lado == "home" else y > x))
            d = sum(p for (x, y), p in g.items() if x == y)
            return w / (tot - d) if tot - d > 0 else None
        if kind == "ah":
            pw = 0.0
            for (x, y), p in g.items():
                r = sg.settle_handicap_quarter(x, y, lado, line)
                pw += p * {"win": 1, "half_win": 0.5, "void": 0, "half_loss": 0, "lose": 0}[r]
            return pw / tot
    if kind in ("pp_total", "pp_1x2"):
        if ctx.get("lh") is None:
            return None
        share = ctx.get("share") or 0.45
        if ctx["fin1"]:
            x, y = ctx["h1"], ctx["a1"]
            if kind == "pp_total":
                return 1.0 if ((x + y) > line) == (op == "over") else 0.0
            return 1.0 if (x > y if lado == "home" else (y > x if lado == "away" else x == y)) else 0.0
        f1 = max(0.0, (45.0 - ctx["minute"])) / 45.0
        ph, pa = pois_pmf(ctx["lh"] * share * f1), pois_pmf(ctx["la"] * share * f1)
        g = {(ctx["h1"] + i, ctx["a1"] + j): ph[i] * pa[j] for i in range(MAXK) for j in range(MAXK)}
        tot = sum(g.values())
        if kind == "pp_total":
            return sum(p for (x, y), p in g.items() if ((x + y) > line) == (op == "over")) / tot
        return sum(p for (x, y), p in g.items() if (x > y if lado == "home" else (y > x if lado == "away" else x == y))) / tot
    if kind in ("corners_total", "corners_equipo", "cards_total"):
        cur = ctx["cards"] if kind == "cards_total" else ctx["corners"]
        if cur is None or p_modelo is None:
            return None
        lam = lambda_from_p(line, p_modelo, over=(op == "over"))
        have = (cur[0] + cur[1]) if kind != "corners_equipo" else (cur[0] if lado == "home" else cur[1])
        add = pois_pmf(lam * f, 80)            # los conteos (córners/tarjetas) tienen medias altas: la cola no cabe en MAXK términos
        return sum(add[k] for k in range(80) if ((have + k) > line) == (op == "over"))
    return None


def minute_num(e):
    return live_prob.minute_of(e)


def goals_first_half(e):
    h1 = a1 = 0
    for g in (e.get("goalscorer") or []):
        if sg._is_pen_shootout(g) if hasattr(sg, "_is_pen_shootout") else False:
            continue
        t = str(g.get("time") or "")
        m = re.match(r"(\d+)(?:\+(\d+))?", t)
        if not m:
            continue
        base, extra = int(m.group(1)), int(m.group(2) or 0)
        if base <= 45:
            if g.get("home_scorer"):
                h1 += 1
            if g.get("away_scorer"):
                a1 += 1
    return h1, a1


def leer_hoja(wb, nombre):
    rows = list(wb[nombre].iter_rows(values_only=True))
    h = list(rows[0])
    return [dict(zip(h, r)) for r in rows[1:] if any(c is not None for c in r)]


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--run", required=True)
    ap.add_argument("--book", required=True)
    ap.add_argument("--cmp", required=True, help="comparativo provisional ya generado con --refresh")
    ap.add_argument("--tickets")
    ap.add_argument("--out")
    ap.add_argument("--out-json")
    a = ap.parse_args(argv)
    import openpyxl
    now = datetime.now(CARACAS)
    book = openpyxl.load_workbook(a.book, read_only=True, data_only=True)
    cmp_ = openpyxl.load_workbook(a.cmp, read_only=True, data_only=True)
    cat = {(r["Partido"], r["Etiqueta"]): r for r in leer_hoja(book, "Catálogo completo")}
    inv = {f"{m['home_team']} – {m['away_team']}": m for m in common.read_json(os.path.join(a.run, "inventory.json"))["matches"]}
    res = common.read_json(os.path.join(a.run, "resultados", "resultados.json"), {})

    # picks de los rankings (sin repetir) con el resultado del comparativo
    picks = {}
    for sh in ("Ranking seguridad", "Ranking atractivo-cuota", "Top por liga"):
        for r in leer_hoja(cmp_, sh):
            k = (r["Partido"], r["Selección"])
            pk = picks.setdefault(k, {"partido": r["Partido"], "seleccion": r["Selección"], "mercado": r["Mercado"], "hora": r["Hora Caracas"], "liga": r["Liga"], "cuota": r["Cuota"], "p": r["P modelo %"],
                                      "agentes": r["Agentes"], "resultado": r["Resultado del pick"], "marcador": r["Resultado del partido"], "en": set()})
            pk["en"].add(sh if sh != "Top por liga" else "Top " + str(r.get("Ranking")))
    for k, pk in picks.items():
        c = cat.get(k)
        pk["entry"] = c["Entrada"] if c else None
    # estado de cada partido
    live = {}
    client = common.Client(os.path.join(a.run, "cache_vivo"), os.path.join(a.run, "sources", "consultas_vivo.jsonl"), policy=common.Policy(), min_interval=0.3, ttl=20)
    key = adapters.apif_key()
    estados = {}
    for pn in {p["partido"] for p in picks.values()} | set():
        m = inv.get(pn)
        r = res.get(m["match_id"]) if m else None
        est = (r or {}).get("estado") or ""
        estados[pn] = "terminado" if est == "Finished" else ("en vivo" if est not in ("", None) else "pendiente")
    # partidos de los tickets del usuario
    tk = common.read_json(a.tickets) if a.tickets else {"tickets": []}
    for t in tk["tickets"]:
        for l in t["patas"]:
            estados.setdefault(l["partido"], None)
    for pn in list(estados):
        m = inv.get(pn)
        if not m:
            continue
        r = res.get(m["match_id"]) or {}
        est = r.get("estado") or ""
        estados[pn] = "terminado" if est == "Finished" else ("en vivo" if est else "pendiente")

    # eventos en vivo
    for pn, st in estados.items():
        m = inv.get(pn)
        if st != "en vivo" or not m:
            continue
        aid = m["source_match_ids"]["apifootball"]
        try:
            e = adapters.apif_call(client, key, action="get_events", match_id=aid, timezone="UTC")[0]
        except Exception as err:     # noqa: BLE001
            print("aviso:", pn, type(err).__name__)
            continue
        h, aw = sg.score(e)
        mn = minute_num(e)
        cp = sg._corner_pair(e)
        cards = adapters._card_points(e)
        h1, a1 = goals_first_half(e)
        mp = api_detalle.model_params(a.run, m["match_id"])
        live[pn] = {"h": h or 0, "a": aw or 0, "minute": mn, "f": max(0.0, (TOTAL_MIN - mn)) / TOTAL_MIN, "corners": tuple(cp) if cp else None, "cards": tuple(cards) if cards else None,
                    "lh": mp[0] if mp else None, "la": mp[1] if mp else None, "share": mp[2] if mp else None, "h1": h1, "a1": a1, "fin1": mn > 45 or str(e.get("match_status", "")).lower().startswith("half"),
                    "estado_txt": str(e.get("match_status") or "")}

    # régimen del día: goles reales/esperados de los terminados con λ del modelo
    reales = esperados = 0.0
    n_reg = 0
    for pn, st in estados.items():
        m = inv.get(pn)
        if st != "terminado" or not m:
            continue
        r = res.get(m["match_id"])
        mp = api_detalle.model_params(a.run, m["match_id"])
        if not mp or r.get("h") is None or r.get("marcador_90_directo") is False:
            continue
        reales += r["h"] + r["a"]
        esperados += mp[0] + mp[1]
        n_reg += 1
    k_dia = reales / esperados if esperados else 1.0

    def ctx_base(pn, f=1.0, k=1.0):
        m = inv.get(pn)
        mp = api_detalle.model_params(a.run, m["match_id"]) if m else None
        return {"h": 0, "a": 0, "f": f, "lh": mp[0] * k if mp else None, "la": mp[1] * k if mp else None, "share": mp[2] if mp else None, "corners": (0, 0), "cards": (0, 0), "minute": 0.0, "h1": 0, "a1": 0, "fin1": False}

    out = {"terminados": [], "en_vivo": [], "pendientes": []}
    for pk in picks.values():
        pn = pk["partido"]
        st = estados.get(pn, "pendiente")
        pk["estado_partido"] = st
        p_mod = pk["p"] / 100 if pk["p"] is not None else None
        if st == "terminado":
            out["terminados"].append(pk)
        elif st == "en vivo" and pn in live:
            pr = prob_pick(pk["entry"], p_mod, live[pn]) if pk["entry"] else None
            pk["p_vivo"] = None if pr is None else round(pr * 100, 1)
            pk["marcador_vivo"] = f"{live[pn]['h']}-{live[pn]['a']} (min {live[pn]['minute']:.0f})"
            pk["corners_vivo"] = live[pn]["corners"]
            out["en_vivo"].append(pk)
        elif st == "en vivo":
            pk["p_vivo"] = None
            pk["marcador_vivo"] = "sin dato"
            out["en_vivo"].append(pk)
        else:
            pk["p_dia"] = None
            if pk["entry"]:
                c = ctx_base(pn, 1.0, k_dia)
                pr = prob_pick(pk["entry"], p_mod, c)
                if pr is not None and parse_entry(pk["entry"])[0] in ("goles_total", "goles_equipo", "btts", "1x2", "dc", "dnb", "ah", "pp_total", "pp_1x2"):
                    pk["p_dia"] = round(pr * 100, 1)
                else:
                    pk["p_dia"] = pk["p"]
            out["pendientes"].append(pk)
    for pk in out["pendientes"]:
        pk["orden"] = pk["p_dia"] if pk["p_dia"] is not None else pk["p"]
    out["pendientes"].sort(key=lambda x: -(x["orden"] or 0))

    # tus tickets
    tick = []
    for t in tk["tickets"]:
        legs = []
        for l in t["patas"]:
            legs.append({"partido": l["partido"], "estado_partido": estados.get(l["partido"]), "cuota": l["cuota"]})
        tick.append({"id": t["id"], "monto": t["monto"], "cuota_total": t["cuota_total"], "patas": legs})

    gan = [p for p in out["terminados"] if p["resultado"] == "GANADA"]
    per = [p for p in out["terminados"] if p["resultado"] == "PERDIDA"]
    resumen = {"hora_caracas": now.strftime("%H:%M"), "partidos_terminados": sum(1 for s in estados.values() if s == "terminado"), "partidos_en_vivo": sum(1 for s in estados.values() if s == "en vivo"),
               "partidos_pendientes": sum(1 for s in estados.values() if s == "pendiente"), "picks_en_rankings": len(picks), "ganadas": len(gan), "perdidas": len(per),
               "goles_reales_por_partido_terminados": round(reales / n_reg, 2) if n_reg else None, "goles_esperados_modelo": round(esperados / n_reg, 2) if n_reg else None, "k_dia": round(k_dia, 3), "partidos_para_k": n_reg}
    out["resumen"] = resumen
    out["tickets"] = tick
    if a.out_json:
        with open(a.out_json, "w", encoding="utf-8") as fh:
            json.dump(out, fh, ensure_ascii=False, indent=1, default=lambda o: sorted(o) if isinstance(o, set) else str(o))
    print(json.dumps(resumen, ensure_ascii=False))
    return out, picks, estados, live


if __name__ == "__main__":
    main()
