#!/usr/bin/env python3
"""Nivel 1: evaluación individual estandarizada de TODO partido confirmado y elegible.

Uso:  level1.py --run runs/2026-10-13 [--limit N]
Lee inventory.json; escribe state.json (cola reanudable, escritura atómica), matrix.json y matrix.csv.
Sólo usa proveedores permitidos (common.Policy). Si ninguna fuente permitida cubre un partido, éste se marca
NO_EVALUABLE_TRAS_INTENTOS con motivo y evidencia: NO se omite y NO se rellena con datos inventados.
Las frecuencias k/n y Wilson son ESTADÍSTICA DESCRIPTIVA, no probabilidades predictivas.
La matemática viene de calc.py (importada, no reimplementada).
"""
import argparse
import csv
import importlib.util
import io
import os
import sys
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import adapters  # noqa: E402
import common  # noqa: E402

_CALC = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "evaluacion-probabilidad-valor", "scripts", "calc.py")
_spec = importlib.util.spec_from_file_location("calc", os.path.normpath(_CALC))
calc = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(calc)

MAX_ATTEMPTS = 3
HISTORY_N = 10
FAMILIES = {
    "resultado": ["1x2", "doble_oportunidad", "empate_no_valido", "handicap"],
    "goles": ["over_1_5", "over_2_5", "over_3_5", "btts", "goles_por_equipo", "rangos_goles", "primera_parte"],
    "corners": ["total", "por_equipo", "handicap", "mas_corners"],
    "tarjetas": ["total", "por_equipo", "handicap", "mas_tarjetas", "arbitro"],
    "otros": ["tiros", "tiros_a_puerta", "fueras_de_juego"],
}
ALL_MARKETS = [f"{fam}.{m}" for fam, ms in FAMILIES.items() for m in ms]


class ProviderUnavailable(Exception):
    pass


# ----------------------------------------------------------------------------- proveedor de histórico permitido
class FootballDataHistory:
    """CSV de temporada de Football-Data (mmz4281/<temporada>/<div>.csv). Cubre goles, córners, tarjetas, tiros, árbitro."""
    name = "football-data"

    def __init__(self, client, season_code):
        self.client, self.season, self._cache, self.files = client, season_code, {}, 0

    def _rows(self, div):
        if div not in self._cache:
            try:
                r = self.client.fetch(f"{adapters.FD_BASE}/mmz4281/{self.season}/{div}.csv")
            except (common.PolicyError, common.FetchError) as e:
                raise ProviderUnavailable(f"football-data {div}: {e}")
            self.files += 1
            self._cache[div] = list(csv.DictReader(io.StringIO(r.text.lstrip("﻿"))))
        return self._cache[div]

    def covers(self, match):
        return bool(match.get("extra", {}).get("div"))

    def team_history(self, match, team, before_iso):
        rows = []
        for x in self._rows(match["extra"]["div"]):
            if team not in (x.get("HomeTeam"), x.get("AwayTeam")) or not x.get("FTHG"):
                continue
            try:
                d = datetime.strptime(x["Date"], "%d/%m/%Y")
            except ValueError:
                d = datetime.strptime(x["Date"], "%d/%m/%y")
            if d.strftime("%Y-%m-%d") >= before_iso:
                continue
            rows.append((d, x))
        rows.sort(key=lambda t: t[0])
        out = []
        for d, x in rows[-HISTORY_N:]:
            home = x["HomeTeam"] == team
            gi = lambda k: int(x[k]) if x.get(k, "").strip() != "" else None
            out.append({"date": d.strftime("%Y-%m-%d"), "competition": match.get("competition"), "venue": "local" if home else "visitante",
                        "opponent": x["AwayTeam"] if home else x["HomeTeam"], "gf": gi("FTHG") if home else gi("FTAG"),
                        "ga": gi("FTAG") if home else gi("FTHG"), "ht_goals": (gi("HTHG"), gi("HTAG")),
                        "corners": (gi("HC"), gi("AC")), "yellow": (gi("HY"), gi("AY")), "red": (gi("HR"), gi("AR")),
                        "shots": (gi("HS"), gi("AS")), "sot": (gi("HST"), gi("AST")), "fouls": (gi("HF"), gi("AF")),
                        "referee": x.get("Referee") or None})
        return out


# ----------------------------------------------------------------------------- cálculo descriptivo
def freq_block(k, n, label):
    if n <= 0:
        return None
    lo, hi = calc.wilson(k, n)
    return {"label": label, "k": k, "n": n, "freq": round(k / n, 3), "wilson95": [round(lo, 3), round(hi, 3)],
            "tipo": "estadistica_descriptiva_no_probabilidad"}


def _count(hist, pred):
    vals = [pred(h) for h in hist]
    vals = [v for v in vals if v is not None]
    return sum(1 for v in vals if v), len(vals)


def stat_blocks(hh, ha):
    """Bloques por mercado a partir de los últimos partidos de local (hh) y visitante (ha). Cada uno usa SU muestra y la etiqueta."""
    out = {}
    tot = lambda h: (h["gf"] + h["ga"]) if h["gf"] is not None and h["ga"] is not None else None
    for line in (1.5, 2.5, 3.5):
        out[f"goles.over_{str(line).replace('.', '_')}"] = [
            freq_block(*_count(hh, lambda h, l=line: None if tot(h) is None else tot(h) > l), f"local últimos {len(hh)}: total>{line}"),
            freq_block(*_count(ha, lambda h, l=line: None if tot(h) is None else tot(h) > l), f"visitante últimos {len(ha)}: total>{line}")]
    btts = lambda h: None if h["gf"] is None else (h["gf"] > 0 and h["ga"] > 0)
    out["goles.btts"] = [freq_block(*_count(hh, btts), f"local últimos {len(hh)}: ambos anotan"),
                         freq_block(*_count(ha, btts), f"visitante últimos {len(ha)}: ambos anotan")]
    out["goles.goles_por_equipo"] = [freq_block(*_count(hh, lambda h: None if h["gf"] is None else h["gf"] >= 1), f"local anota ≥1 (últimos {len(hh)})"),
                                     freq_block(*_count(ha, lambda h: None if h["gf"] is None else h["gf"] >= 1), f"visitante anota ≥1 (últimos {len(ha)})")]
    ctot = lambda h: None if None in h["corners"] else h["corners"][0] + h["corners"][1]
    for line in (8.5, 9.5, 10.5):
        out.setdefault("corners.total", []).extend([
            freq_block(*_count(hh, lambda h, l=line: None if ctot(h) is None else ctot(h) > l), f"local últimos {len(hh)}: córners totales>{line}"),
            freq_block(*_count(ha, lambda h, l=line: None if ctot(h) is None else ctot(h) > l), f"visitante últimos {len(ha)}: córners totales>{line}")])
    cards = lambda h: None if None in h["yellow"] or None in h["red"] else sum(h["yellow"]) + sum(h["red"])
    for line in (3.5, 4.5, 5.5):
        out.setdefault("tarjetas.total", []).extend([
            freq_block(*_count(hh, lambda h, l=line: None if cards(h) is None else cards(h) > l), f"local últimos {len(hh)}: tarjetas (A+R)>{line}"),
            freq_block(*_count(ha, lambda h, l=line: None if cards(h) is None else cards(h) > l), f"visitante últimos {len(ha)}: tarjetas (A+R)>{line}")])
    win = lambda h: None if h["gf"] is None else h["gf"] > h["ga"]
    out["resultado.1x2"] = [freq_block(*_count(hh, win), f"local gana (últimos {len(hh)}, todos los rivales)"),
                            freq_block(*_count(ha, lambda h: None if h["gf"] is None else h["gf"] > h["ga"]), f"visitante gana (últimos {len(ha)})")]
    shots = lambda h: None if None in h["shots"] else h["shots"][0] + h["shots"][1]
    out["otros.tiros"] = [freq_block(*_count(hh, lambda h: None if shots(h) is None else shots(h) > 0), f"local: dato de tiros presente en {len(hh)} partidos")]
    return {k: [b for b in v if b] for k, v in out.items()}


def odds_info(match):
    o = (match.get("extra") or {}).get("odds") or {}
    res = {}
    try:
        if all(k in o for k in ("B365H", "B365D", "B365A")):
            cs = [float(o["B365H"]), float(o["B365D"]), float(o["B365A"])]
            ov, nv = calc.novig_probs(cs)
            res["resultado.1x2"] = {"casa": "bet365 (vía football-data)", "cuotas": cs, "overround": round(ov, 4),
                                    "prob_equilibrio_bruta": [round(calc.implied_prob(c), 4) for c in cs], "sin_margen_proporcional": [round(x, 4) for x in nv]}
        if "B365>2.5" in o and "B365<2.5" in o:
            cs = [float(o["B365>2.5"]), float(o["B365<2.5"])]
            ov, nv = calc.novig_probs(cs)
            res["goles.over_2_5"] = {"casa": "bet365 (vía football-data)", "cuotas": cs, "overround": round(ov, 4),
                                     "prob_equilibrio_bruta": [round(calc.implied_prob(c), 4) for c in cs], "sin_margen_proporcional": [round(x, 4) for x in nv]}
    except ValueError:
        pass
    return res


# ----------------------------------------------------------------------------- evaluación por partido
def evaluate_match(match, provider, policy, now_iso):
    attempts = []
    for name, p in policy.data["providers"].items():
        if p["status"] == "excluida":
            attempts.append({"provider": name, "resultado": "no consultada: excluida por política", "motivo": p["reason"][:160]})
    form, blocks, note = {}, {}, None
    data_attempted = False          # ¿se hizo alguna consulta real de datos para ESTE partido?
    if provider is not None and provider.covers(match):
        data_attempted = True
        try:
            before = (match["normalized_datetime_local"] or now_iso)[:10]
            form["local"] = provider.team_history(match, match["home_team"], before)
            form["visitante"] = provider.team_history(match, match["away_team"], before)
            attempts.append({"provider": provider.name, "resultado": f"consultada: {len(form['local'])}+{len(form['visitante'])} partidos previos"})
            if form["local"] and form["visitante"]:
                blocks = stat_blocks(form["local"], form["visitante"])
            note = f"últimos ≤{HISTORY_N} partidos por equipo de la liga {match['extra'].get('div')}, temporada en curso: NO es una muestra de temporada completa"
        except ProviderUnavailable as e:
            attempts.append({"provider": provider.name, "resultado": f"acceso fallido: {e}"})
    else:
        attempts.append({"provider": getattr(provider, "name", "football-data"), "resultado": "sin cobertura de esta liga/competición"})
    prices = odds_info(match)
    markets = {}
    for key in ALL_MARKETS:
        have_stats = key in blocks and blocks[key]
        have_price = key in prices
        stats_status = "SUFICIENTES" if have_stats and min(b["n"] for b in blocks[key]) >= 8 else ("PARCIALES" if have_stats else "INSUFICIENTES")
        if key == "resultado.1x2" and not have_price and not have_stats:
            stats_status = "INSUFICIENTES"
        if have_stats or have_price:
            ev = "PARCIAL"        # nunca EVALUABLE aquí: falta contraste de rivales, bajas y 2.ª cotización (Nivel 2)
            reason = None if have_stats else "hay cuota pero no estadísticas"
            if have_stats and not have_price:
                reason = "estadísticas descriptivas sin cuota verificada"
        elif not data_attempted:
            ev = "NOT_CHECKED"       # nadie examinó este mercado: no implica que no exista ni que la estadística sea 0
            reason = ("no investigado: ninguna fuente permitida cubre esta competición (sin ficha ni feed abierto); "
                      "no implica que el mercado no exista ni que la estadística sea 0")
        elif not (form.get("local") and form.get("visitante")):
            ev = "NO_EVALUABLE"
            reason = "intento de consulta fallido o sin histórico: ver attempts"
        else:
            ev = "NO_EVALUABLE"
            reason = "la fuente permitida abierta no incluye este mercado/estadística"
        markets[key] = {
            "market_availability_status": "VERIFICADO_DISPONIBLE_EN_UNA_CASA" if have_price else "NOT_CHECKED",
            "statistics_availability_status": stats_status,
            "price_verification_status": "PRECIO_NO_CONFIRMADO" + (" (una sola casa vía agregador)" if have_price else ""),
            "evaluation_status": ev, "not_evaluable_reason": reason,
            "sources_checked": [a["provider"] for a in attempts if a["resultado"].startswith(("consultada", "acceso fallido"))],
            "sources_not_consulted": [a["provider"] for a in attempts if a["resultado"].startswith(("no consultada", "sin cobertura"))],
            "last_updated": now_iso,
            "stats": blocks.get(key, []), "price": prices.get(key)}
    n_ok = sum(1 for m in markets.values() if m["evaluation_status"] in ("EVALUABLE", "PARCIAL"))
    return {"match_id": match["match_id"], "attempts": attempts, "data_attempted": data_attempted, "form": form, "sample_note": note,
            "markets": markets, "evaluated_markets_ok": n_ok,
            "sports_analysis_status": "COMPLETADO" if (form.get("local") and form.get("visitante")) else "NO_EVALUABLE_TRAS_INTENTOS",
            "market_analysis_status": "COMPLETADO" if n_ok else "NO_EVALUABLE_TRAS_INTENTOS"}


# ----------------------------------------------------------------------------- cola reanudable
def load_state(run):
    return common.read_json(os.path.join(run, "state.json"), {"matches": {}})


def save_state(run, st):
    common.write_json_atomic(os.path.join(run, "state.json"), st)


def init_state(st, inv):
    for m in inv["matches"]:
        if m["match_id"] not in st["matches"]:
            st["matches"][m["match_id"]] = {"status": "PENDIENTE" if m["analysis_required"] else "NO_REQUIERE_ANALISIS",
                                            "attempts": 0, "disposition": m["disposition"]}
    return st


def process(run, provider, policy, limit=None, evaluator=evaluate_match, now=None):
    inv = common.read_json(os.path.join(run, "inventory.json"))
    st = init_state(load_state(run), inv)
    matrix = common.read_json(os.path.join(run, "matrix.json"), {"matches": {}})
    now_iso = (now or datetime.now(timezone.utc)).strftime("%Y-%m-%dT%H:%M:%SZ")
    save_state(run, st)
    done = 0
    for m in inv["matches"]:
        s = st["matches"][m["match_id"]]
        if s["status"] in ("COMPLETADO", "NO_EVALUABLE_TRAS_INTENTOS", "NO_REQUIERE_ANALISIS", "ERROR_REQUIERE_INTERVENCION"):
            continue
        if limit is not None and done >= limit:
            break
        s["status"], s["attempts"] = "EN_CURSO", s["attempts"] + 1
        save_state(run, st)
        try:
            ev = evaluator(m, provider, policy, now_iso)
            matrix["matches"][m["match_id"]] = ev
            s["status"] = "COMPLETADO" if ev["sports_analysis_status"] == "COMPLETADO" else "NO_EVALUABLE_TRAS_INTENTOS"
            if s["status"] == "NO_EVALUABLE_TRAS_INTENTOS":
                s["reason"] = "ninguna fuente permitida aporta histórico para este partido"
                s["evidence"] = ev["attempts"]
            m["sports_analysis_status"], m["market_analysis_status"] = ev["sports_analysis_status"], ev["market_analysis_status"]
        except Exception as e:      # error recuperable hasta MAX_ATTEMPTS
            s["status"] = "ERROR_RECUPERABLE" if s["attempts"] < MAX_ATTEMPTS else "ERROR_REQUIERE_INTERVENCION"
            s["last_error"] = f"{type(e).__name__}: {e}"
        save_state(run, st)
        common.write_json_atomic(os.path.join(run, "matrix.json"), matrix)
        done += 1
    common.write_json_atomic(os.path.join(run, "inventory.json"), inv)
    write_csv(run, inv, matrix)
    return st, matrix


def write_csv(run, inv, matrix):
    path = os.path.join(run, "matrix.csv")
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["match_id", "home", "away", "competition", "utc", "calendario", "elegibilidad", "analisis_deportivo", "mercado", "evaluation_status", "disponibilidad", "estadisticas", "precio", "motivo"])
        for m in inv["matches"]:
            ev = matrix["matches"].get(m["match_id"])
            if not ev:
                w.writerow([m["match_id"], m["home_team"], m["away_team"], m["competition"], m["normalized_datetime_utc"], m["calendar_verification_status"],
                            m["prematch_eligibility"], m["sports_analysis_status"], "", "", "", "", "", m["disposition"]])
                continue
            for k, mk in ev["markets"].items():
                w.writerow([m["match_id"], m["home_team"], m["away_team"], m["competition"], m["normalized_datetime_utc"], m["calendar_verification_status"],
                            m["prematch_eligibility"], m["sports_analysis_status"], k, mk["evaluation_status"], mk["market_availability_status"],
                            mk["statistics_availability_status"], mk["price_verification_status"], mk["not_evaluable_reason"] or ""])


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--run", required=True)
    ap.add_argument("--limit", type=int)
    a = ap.parse_args(argv)
    inv = common.read_json(os.path.join(a.run, "inventory.json"))
    if not inv:
        print("error: falta inventory.json (ejecuta inventory.py primero)", file=sys.stderr)
        return 2
    policy = common.Policy()
    client = common.Client(os.path.join(a.run, "cache"), os.path.join(a.run, "sources", "consultas.jsonl"), policy=policy,
                           min_interval=policy.data["providers"]["football-data"]["limits"]["min_interval"])
    d = datetime.fromisoformat(inv["meta"]["date"])
    season = f"{(d.year if d.month >= 7 else d.year - 1) % 100:02d}{(d.year + (1 if d.month >= 7 else 0)) % 100:02d}"
    st, _ = process(a.run, FootballDataHistory(client, season), policy, a.limit)
    from collections import Counter
    print("estado de la cola:", dict(Counter(s["status"] for s in st["matches"].values())))
    return 0


if __name__ == "__main__":
    sys.exit(main())
