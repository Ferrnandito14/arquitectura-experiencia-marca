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
from datetime import datetime, timedelta, timezone

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import adapters  # noqa: E402
import common  # noqa: E402

_CALC = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "evaluacion-probabilidad-valor", "scripts", "calc.py")
_spec = importlib.util.spec_from_file_location("calc", os.path.normpath(_CALC))
calc = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(calc)

MAX_ATTEMPTS = 3
# Ninguna fuente permitida cubre el partido: NO hubo consulta real de datos. Distinto de NO_EVALUABLE_TRAS_INTENTOS (que exige intentos).
NO_INVESTIGADO = "NO_INVESTIGADO_SIN_FUENTE_PERMITIDA"
# Solo hay forma de OTRA competición (proxy doméstico): análisis PARCIAL, nunca COMPLETADO.
PARCIAL_PROXY = "PARCIAL_PROXY_OTRA_COMPETICION"
HISTORY_N = 10
MIN_SAME_COMP = 6      # mínimo de partidos de la misma competición para preferirlos al historial mixto
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
TOP_DIVS = ["E0", "SP1", "D1", "I1", "F1", "N1", "B1", "T1", "P1", "SC0", "G1"]
ALIASES_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "team_aliases.json")


class FootballDataHistory:
    """CSV de temporada de Football-Data (mmz4281/<temporada>/<div>.csv). Cubre goles, córners, tarjetas, tiros, árbitro.
    Dos usos: (1) partidos cuyo calendario viene de Football-Data (misma competición); (2) PROXY: equipos de un partido de
    OTRA competición (p. ej. Champions League) que juegan en una liga doméstica cubierta -> su forma doméstica se usa
    SIEMPRE etiquetada como «liga doméstica, otra competición» y nunca como evidencia del partido."""
    name = "football-data"

    def __init__(self, client, season_code, aliases=None):
        self.client, self.season, self._cache, self.files = client, season_code, {}, 0
        raw_aliases = aliases if aliases is not None else common.read_json(ALIASES_PATH, {}).get("aliases", {})
        self._aliases = {common.norm_name(k): v for k, v in raw_aliases.items()}      # claves normalizadas siempre
        self._index = None
        self._resolved = {}
        self.needs_review = {common.norm_name(k): v for k, v in common.read_json(ALIASES_PATH, {}).get("needs_review", {}).items()}

    def _rows(self, div):
        if div not in self._cache:
            try:
                r = self.client.fetch(f"{adapters.FD_BASE}/mmz4281/{self.season}/{div}.csv")
            except (common.PolicyError, common.FetchError) as e:
                raise ProviderUnavailable(f"football-data {div}: {e}")
            self.files += 1
            self._cache[div] = list(csv.DictReader(io.StringIO(r.text.lstrip("\ufeff"))))
        return self._cache[div]

    def _build_index(self):
        if self._index is None:
            idx, amb = {}, set()
            for div in TOP_DIVS:
                for x in self._rows(div):
                    for t in (x.get("HomeTeam"), x.get("AwayTeam")):
                        if not t:
                            continue
                        k = common.norm_name(t)
                        if k in idx and idx[k][1] != t:
                            amb.add(k)
                        idx.setdefault(k, (div, t))
            self._index = ({k: v for k, v in idx.items() if k not in amb}, amb)
        return self._index

    def resolve(self, team):
        """(div, nombre_FD, alias_usado) o None. Solo coincidencia exacta normalizada o alias explícito; nunca difusa."""
        if team in self._resolved:
            return self._resolved[team]
        idx, amb = self._build_index()
        k = common.norm_name(team)
        out = None
        if k in idx:
            out = (idx[k][0], idx[k][1], False)
        elif k in self._aliases and common.norm_name(self._aliases[k]) in idx:
            d, t = idx[common.norm_name(self._aliases[k])]
            out = (d, t, True)
        self._resolved[team] = out
        return out

    def covers(self, match):
        if match.get("extra", {}).get("div"):
            return True
        if match.get("gender_or_category", "men") != "men":
            return False        # juveniles/sub-23/reservas/femenino: la forma del primer equipo masculino NO es proxy válido
        try:
            h, a = self.resolve(match["home_team"]), self.resolve(match["away_team"])
        except ProviderUnavailable:
            return False
        if h and a:
            match.setdefault("extra", {})["proxy_resolution"] = {"home": h, "away": a}
            return True
        return False

    def is_proxy(self, match):
        return not match.get("extra", {}).get("div")

    def team_history(self, match, team, before_iso):
        if match.get("extra", {}).get("div"):
            div, fd_name, label = match["extra"]["div"], team, match.get("competition")
        else:
            side = "home" if team == match["home_team"] else "away"
            div, fd_name, _ = match["extra"]["proxy_resolution"][side]
            comp = adapters.FD_DIV.get(div, ("", div))
            label = f"{comp[1]} ({comp[0]}) — liga doméstica, OTRA competición"
        rows = []
        for x in self._rows(div):
            if fd_name not in (x.get("HomeTeam"), x.get("AwayTeam")) or not x.get("FTHG"):
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
            home = x["HomeTeam"] == fd_name
            gi = lambda k: int(x[k]) if x.get(k, "").strip() != "" else None
            out.append({"date": d.strftime("%Y-%m-%d"), "competition": label, "venue": "local" if home else "visitante",
                        "opponent": x["AwayTeam"] if home else x["HomeTeam"], "gf": gi("FTHG") if home else gi("FTAG"),
                        "ga": gi("FTAG") if home else gi("FTHG"), "ht_goals": (gi("HTHG"), gi("HTAG")),
                        "corners": (gi("HC"), gi("AC")), "yellow": (gi("HY"), gi("AY")), "red": (gi("HR"), gi("AR")),
                        "shots": (gi("HS"), gi("AS")), "sot": (gi("HST"), gi("AST")), "fouls": (gi("HF"), gi("AF")),
                        "referee": x.get("Referee") or None, "fd_team": fd_name})
        return out


class ProviderLimit(Exception):
    """La API de pago/prueba rechazó por límite o clave: la cola se detiene sin marcar partidos como evaluados."""


class ApiFootballHistory:
    """Historial PROPIO de cada equipo (todas sus competiciones, etiquetadas) desde apifootball `get_events?team_id=`: una petición
    por equipo devuelve sus partidos finalizados con estadísticas en línea. NO es histórico de la misma competición: es la forma
    reciente del equipo (mezcla casa/fuera y competiciones), sin ajustar por rival. Faltas de estadística => None, nunca 0."""
    name = "apifootball"
    needs_review = {}
    LOOKBACK_DAYS = 180

    def __init__(self, client, key, today_iso):
        self.client, self.key, self.today = client, key, today_iso
        self._teams, self.requests, self._odds = {}, 0, {}
        self.limit_hit = None

    def covers(self, match):
        a = (match.get("extra") or {}).get("api") or {}
        return bool(a.get("home_id") and a.get("away_id")) and not self.limit_hit

    def is_proxy(self, match):
        return False

    def _events(self, team_id, before_iso):
        k = (team_id, before_iso)
        if k not in self._teams:
            d_to = (datetime.fromisoformat(before_iso) - timedelta(days=1)).date().isoformat()
            d_from = (datetime.fromisoformat(before_iso) - timedelta(days=self.LOOKBACK_DAYS)).date().isoformat()
            try:
                self._teams[k] = adapters.apif_call(self.client, self.key, action="get_events", team_id=team_id,
                                                    **{"from": d_from, "to": d_to}, timezone="UTC")
                self.requests += 1
            except adapters.ApiLimit as e:
                self.limit_hit = str(e)
                raise ProviderLimit(str(e))
            except common.PolicyError as e:
                if "tope de" in str(e):          # tope por ejecución de la política: la cola se detiene y se reanuda en otra ejecución
                    self.limit_hit = str(e)
                    raise ProviderLimit(str(e))
                raise ProviderUnavailable(f"apifootball team {team_id}: {e}")
            except common.FetchError as e:
                raise ProviderUnavailable(f"apifootball team {team_id}: {e}")
        return self._teams[k]

    def team_history(self, match, team, before_iso):
        a = match["extra"]["api"]
        tid = a["home_id"] if team == match["home_team"] else a["away_id"]
        rows = []
        for e in self._events(tid, before_iso):
            if (e.get("match_status") or "").lower() not in ("finished", "after pen.", "after extra time"):
                continue
            if "friendl" in (e.get("league_name") or "").lower():
                continue                                   # los amistosos (rotaciones, rivales dispares) no entran en ninguna muestra
            r = adapters.apif_history_row(e, tid)
            if r:
                rows.append(r)
        rows.sort(key=lambda r: r["date"])
        base = lambda x: common.norm_name((x or "").split(" - ")[0])
        comp = base(a.get("league_name"))
        same = [r for r in rows if comp and base(r["competition"]) == comp]
        if len(same) >= MIN_SAME_COMP:                     # preferir partidos de la MISMA competición (sin eliminatorias/copas contra rivales dispares)
            use = same[-HISTORY_N:]
            for r in use:
                r["misma_competicion"] = True
            return use
        use = rows[-HISTORY_N:]
        for r in use:
            r["misma_competicion"] = False
        return use

    def load_odds(self, day_from, day_to):
        try:
            rows = adapters.apif_call(self.client, self.key, action="get_odds", **{"from": day_from, "to": day_to})
            self.requests += 1
        except adapters.ApiLimit as e:
            self.limit_hit = str(e)
            raise ProviderLimit(str(e))
        self._odds = adapters.apif_odds_average(rows)
        return len(self._odds)

    def odds_for(self, match):
        mid = ((match.get("extra") or {}).get("api") or {}).get("match_id")
        return self._odds.get(mid, {})


class CompositeProvider:
    """Prefiere el historial propio de la API; si no cubre el partido, la forma doméstica proxy de Football-Data (etiquetada)."""

    def __init__(self, api, fd):
        self.api, self.fd, self._chosen, self.name = api, fd, {}, "football-data"

    @property
    def needs_review(self):
        return getattr(self.fd, "needs_review", {})

    def covers(self, match):
        for p in (self.api, self.fd):
            if p is not None and p.covers(match):
                self._chosen[match["match_id"]] = p
                self.name = p.name
                return True
        return False

    def is_proxy(self, match):
        return self._chosen[match["match_id"]].is_proxy(match)

    def team_history(self, match, team, before_iso):
        return self._chosen[match["match_id"]].team_history(match, team, before_iso)

    def odds_for(self, match):
        return self.api.odds_for(match) if self.api else {}


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
            freq_block(*_count(hh, lambda h, l=line: None if tot(h) is None else tot(h) > l), f"equipo local (casa+fuera) últimos {len(hh)}: total>{line}"),
            freq_block(*_count(ha, lambda h, l=line: None if tot(h) is None else tot(h) > l), f"equipo visitante (casa+fuera) últimos {len(ha)}: total>{line}")]
    btts = lambda h: None if h["gf"] is None else (h["gf"] > 0 and h["ga"] > 0)
    out["goles.btts"] = [freq_block(*_count(hh, btts), f"equipo local (casa+fuera) últimos {len(hh)}: ambos anotan"),
                         freq_block(*_count(ha, btts), f"equipo visitante (casa+fuera) últimos {len(ha)}: ambos anotan")]
    out["goles.goles_por_equipo"] = [freq_block(*_count(hh, lambda h: None if h["gf"] is None else h["gf"] >= 1), f"local anota ≥1 (últimos {len(hh)})"),
                                     freq_block(*_count(ha, lambda h: None if h["gf"] is None else h["gf"] >= 1), f"visitante anota ≥1 (últimos {len(ha)})")]
    ctot = lambda h: None if None in h["corners"] else h["corners"][0] + h["corners"][1]
    for line in (8.5, 9.5, 10.5):
        out.setdefault("corners.total", []).extend([
            freq_block(*_count(hh, lambda h, l=line: None if ctot(h) is None else ctot(h) > l), f"equipo local (casa+fuera) últimos {len(hh)}: córners totales>{line}"),
            freq_block(*_count(ha, lambda h, l=line: None if ctot(h) is None else ctot(h) > l), f"equipo visitante (casa+fuera) últimos {len(ha)}: córners totales>{line}")])
    cards = lambda h: None if None in h["yellow"] or None in h["red"] else sum(h["yellow"]) + sum(h["red"])
    for line in (3.5, 4.5, 5.5):
        out.setdefault("tarjetas.total", []).extend([
            freq_block(*_count(hh, lambda h, l=line: None if cards(h) is None else cards(h) > l), f"equipo local (casa+fuera) últimos {len(hh)}: tarjetas (A+R)>{line}"),
            freq_block(*_count(ha, lambda h, l=line: None if cards(h) is None else cards(h) > l), f"equipo visitante (casa+fuera) últimos {len(ha)}: tarjetas (A+R)>{line}")])
    win = lambda h: None if h["gf"] is None else h["gf"] > h["ga"]
    out["resultado.1x2"] = [freq_block(*_count(hh, win), f"equipo local gana (últimos {len(hh)}, todos los rivales)"),
                            freq_block(*_count(ha, lambda h: None if h["gf"] is None else h["gf"] > h["ga"]), f"visitante gana (últimos {len(ha)})")]
    shots = lambda h: None if None in h["shots"] else h["shots"][0] + h["shots"][1]
    sot = lambda h: None if None in h["sot"] else h["sot"][0] + h["sot"][1]
    out["otros.tiros"] = [freq_block(*_count(hh, lambda h: None if shots(h) is None else shots(h) > 22.5), f"equipo local (casa+fuera) últimos {len(hh)}: tiros totales>22.5 (línea de referencia)"),
                          freq_block(*_count(ha, lambda h: None if shots(h) is None else shots(h) > 22.5), f"equipo visitante (casa+fuera) últimos {len(ha)}: tiros totales>22.5 (línea de referencia)")]
    out["otros.tiros_a_puerta"] = [freq_block(*_count(hh, lambda h: None if sot(h) is None else sot(h) > 8.5), f"equipo local (casa+fuera) últimos {len(hh)}: tiros a puerta totales>8.5 (línea de referencia)"),
                                   freq_block(*_count(ha, lambda h: None if sot(h) is None else sot(h) > 8.5), f"equipo visitante (casa+fuera) últimos {len(ha)}: tiros a puerta totales>8.5 (línea de referencia)")]
    return {k: [b for b in v if b] for k, v in out.items()}


def odds_info(match, provider=None):
    o = (match.get("extra") or {}).get("odds") or {}
    res = {}
    for key, v in (getattr(provider, "odds_for", lambda m: {})(match) or {}).items():
        try:
            ov, nv = calc.novig_probs(v["cuotas_medias"])
            res[key] = {"casa": f"PROMEDIO de {v['n_casas']} casas (agregador apifootball): referencia de mercado, NO cuota ejecutable",
                        "tipo": "promedio_de_mercado", "cuotas": v["cuotas_medias"], "minmax": v["minmax"], "n_casas": v["n_casas"],
                        "overround": round(ov, 4), "prob_equilibrio_bruta": [round(calc.implied_prob(c), 4) for c in v["cuotas_medias"]],
                        "sin_margen_proporcional": [round(x, 4) for x in nv]}
        except ValueError:
            continue
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
    form, blocks, note, proxy = {}, {}, None, False
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
            proxy = bool(getattr(provider, "is_proxy", lambda m: False)(match))
            if proxy:
                pr = match["extra"]["proxy_resolution"]
                weak = [f"{t} n={len(form[side])}" for side, t in (("local", match["home_team"]), ("visitante", match["away_team"])) if len(form[side]) < 8]
                review = [k for k, v in getattr(provider, "needs_review", {}).items()
                          if any(common.norm_name(match[t]) == k and pr[side][2] for t, side in (("home_team", "home"), ("away_team", "away")))]
                note = (f"PROXY: forma de liga DOMÉSTICA, OTRA competición, de ≤{HISTORY_N} partidos por equipo, temporada en curso; "
                        f"local→{pr['home'][1]} ({pr['home'][0]}{', alias' if pr['home'][2] else ''}), visitante→{pr['away'][1]} ({pr['away'][0]}{', alias' if pr['away'][2] else ''}). "
                        "NO es evidencia del partido (otra competición, rivales y contexto distintos), mezcla partidos en casa y fuera, y no es una muestra de temporada completa; "
                        "tarjetas = amarillas+rojas sin ponderar y sin árbitro designado; definición NO homogénea entre ligas (Football-Data: en Inglaterra y Escocia la amarilla inicial no cuenta cuando hay segunda amarilla y roja; en las ligas europeas sí); "
                        "líneas de córners/tarjetas/goles = referencias fijas, NO las de ninguna casa"
                        + (f"; MUESTRA DÉBIL n<8: {', '.join(weak)}" if weak else "")
                        + (f"; ALIAS SUJETO A REVISIÓN: {', '.join(review)}" if review else ""))
            elif getattr(provider, "name", "") == "apifootball":
                weak = [f"{t} n={len(form[side])}" for side, t in (("local", match["home_team"]), ("visitante", match["away_team"])) if len(form[side]) < 8]
                same = all(r.get("misma_competicion") for r in (form["local"] + form["visitante"]))
                note = (("MISMA COMPETICIÓN (apifootball, últimos ≤%d partidos finalizados de cada equipo en 180 días, sin amistosos): " % HISTORY_N) if same else
                        f"HISTORIAL PROPIO de cada equipo (apifootball, últimos ≤{HISTORY_N} partidos finalizados en 180 días, sin amistosos, MEZCLA competiciones — copas/eliminatorias/otras ligas —, "
                        "etiquetadas por partido); NO es histórico de la misma competición para al menos un equipo, ") + ("mezcla casa y fuera,"
                        " sin ajustar por rival ni por categoría del rival; "
                        "estadística faltante en un partido = excluido de la muestra (n menor), nunca 0; tarjetas A+R solo si hay datos de amarillas y rojas; "
                        "líneas de córners/tarjetas/goles/tiros = referencias fijas, NO las de ninguna casa; cuotas = promedio de mercado, no ejecutable"
                        + (f"; MUESTRA DÉBIL n<8: {', '.join(weak)}" if weak else ""))
            else:
                note = f"últimos ≤{HISTORY_N} partidos por equipo de la liga {match['extra'].get('div')}, temporada en curso: NO es una muestra de temporada completa"
        except ProviderUnavailable as e:
            attempts.append({"provider": provider.name, "resultado": f"acceso fallido: {e}"})
    else:
        attempts.append({"provider": getattr(provider, "name", "football-data"), "resultado": "sin cobertura de esta liga/competición"})
    prices = odds_info(match, provider)
    markets = {}
    for key in ALL_MARKETS:
        have_stats = key in blocks and blocks[key]
        if proxy and key.startswith("resultado."):
            have_stats = False      # equipos de ligas distintas, sin rivales comunes: su % de victorias no es comparable para el 1X2
        have_price = key in prices
        if have_stats:
            stats_status = "SUFICIENTES" if (min(b["n"] for b in blocks[key]) >= 8 and not proxy) else "PARCIALES"
        else:
            stats_status = "INSUFICIENTES" if data_attempted else "NOT_CHECKED"     # INSUFICIENTES = se buscó y no bastó
        if have_stats or have_price:
            ev = "PARCIAL"        # nunca EVALUABLE aquí: falta contraste de rivales, bajas y 2.ª cotización (Nivel 2)
            reason = None if have_stats else "hay cuota pero no estadísticas"
            if have_stats and not have_price:
                reason = "estadísticas descriptivas sin cuota verificada"
            if have_stats and proxy:
                reason = "estadística descriptiva de liga doméstica (OTRA competición): no evalúa el partido; sin cuota verificada"
        elif not data_attempted:
            ev = "NOT_CHECKED"       # nadie examinó este mercado: no implica que no exista ni que la estadística sea 0
            reason = ("no investigado: ningún adaptador de fuente permitida cubre esta competición (sin ficha ni feed abierto); "
                      "no implica que el mercado no exista ni que la estadística sea 0")
        elif proxy and key.startswith("resultado."):
            ev = "NO_EVALUABLE"
            reason = "forma doméstica de ligas distintas sin rivales comunes: no es comparable para resultado/hándicap; sin cuota"
        elif not (form.get("local") and form.get("visitante")):
            ev = "NO_EVALUABLE"
            reason = "intento de consulta fallido o sin histórico: ver attempts"
        else:
            ev = "NO_EVALUABLE"
            reason = "la fuente permitida abierta no incluye este mercado/estadística"
        markets[key] = {
            "market_availability_status": "VERIFICADO_DISPONIBLE_EN_UNA_CASA" if have_price else "NOT_CHECKED",
            "statistics_availability_status": stats_status,
            "price_verification_status": ("NOT_CHECKED" if not data_attempted and not have_price
                                          else "PRECIO_NO_CONFIRMADO" + ((" (promedio de mercado vía agregador, no ejecutable)" if prices[key].get("tipo") == "promedio_de_mercado"
                                                         else " (una sola casa vía agregador)") if have_price else "")),
            "evaluation_status": ev, "not_evaluable_reason": reason, "proxy_sample": proxy,
            "sources_checked": [a["provider"] for a in attempts if a["resultado"].startswith(("consultada", "acceso fallido"))],
            "sources_not_consulted": [a["provider"] for a in attempts if a["resultado"].startswith(("no consultada", "sin cobertura"))],
            "last_updated": now_iso,
            "stats": ([] if (proxy and key.startswith("resultado.")) else blocks.get(key, [])), "price": prices.get(key)}
    n_ok = sum(1 for m in markets.values() if m["evaluation_status"] in ("EVALUABLE", "PARCIAL"))
    if not data_attempted:
        kind = None
    elif proxy:
        kind = "proxy_otra_competicion"
    elif getattr(provider, "name", "") == "apifootball":
        rows = (form.get("local") or []) + (form.get("visitante") or [])
        kind = "apifootball_misma_competicion" if rows and all(r.get("misma_competicion") for r in rows) else "apifootball_historial_propio"
    else:
        kind = "football-data_misma_liga"
    api_prices = getattr(provider, "odds_for", lambda m: {})(match) if data_attempted else {}
    return {"match_id": match["match_id"], "attempts": attempts, "data_attempted": data_attempted, "proxy_sample": proxy, "history_kind": kind,
            "api_prices": api_prices, "form": form, "sample_note": note,
            "markets": markets, "evaluated_markets_ok": n_ok,
            "sports_analysis_status": (("COMPLETADO" if not proxy else PARCIAL_PROXY) if (form.get("local") and form.get("visitante"))
                                      else ("NO_EVALUABLE_TRAS_INTENTOS" if data_attempted else NO_INVESTIGADO)),
            "market_analysis_status": (("COMPLETADO" if not proxy else PARCIAL_PROXY) if n_ok else ("NO_EVALUABLE_TRAS_INTENTOS" if data_attempted else NO_INVESTIGADO))}


# ----------------------------------------------------------------------------- cola reanudable
def load_state(run):
    return common.read_json(os.path.join(run, "state.json"), {"matches": {}})


def save_state(run, st):
    common.write_json_atomic(os.path.join(run, "state.json"), st)


def init_state(st, inv):
    ids = {m["match_id"] for m in inv["matches"]}
    orphans = [mid for mid in st["matches"] if mid not in ids]
    if orphans:                                     # el inventario se regeneró y fusionó/renombró partidos: se retira el estado huérfano y se deja constancia
        st.setdefault("pruned_orphans", []).extend({"match_id": mid, "last_status": st["matches"][mid].get("status")} for mid in orphans)
        for mid in orphans:
            del st["matches"][mid]
    for m in inv["matches"]:
        if m["match_id"] not in st["matches"]:
            st["matches"][m["match_id"]] = {"status": "PENDIENTE" if m["analysis_required"] else "NO_REQUIERE_ANALISIS",
                                            "attempts": 0, "disposition": m["disposition"]}
    return st


def process(run, provider, policy, limit=None, evaluator=evaluate_match, now=None):
    inv = common.read_json(os.path.join(run, "inventory.json"))
    st = init_state(load_state(run), inv)
    matrix = common.read_json(os.path.join(run, "matrix.json"), {"matches": {}})
    matrix["matches"] = {k: v for k, v in matrix["matches"].items() if k in st["matches"]}
    now_iso = (now or datetime.now(timezone.utc)).strftime("%Y-%m-%dT%H:%M:%SZ")
    save_state(run, st)
    done = 0
    for m in inv["matches"]:
        s = st["matches"][m["match_id"]]
        if s["status"] in ("COMPLETADO", PARCIAL_PROXY, "NO_EVALUABLE_TRAS_INTENTOS", NO_INVESTIGADO, "NO_REQUIERE_ANALISIS", "ERROR_REQUIERE_INTERVENCION"):
            continue
        if limit is not None and done >= limit:
            break
        s["status"], s["attempts"] = "EN_CURSO", s["attempts"] + 1
        save_state(run, st)
        try:
            ev = evaluator(m, provider, policy, now_iso)
            matrix["matches"][m["match_id"]] = ev
            s["status"] = ev["sports_analysis_status"]
            if s["status"] == "NO_EVALUABLE_TRAS_INTENTOS":
                s["reason"] = "se intentó la consulta permitida y no aportó histórico suficiente"
                s["evidence"] = ev["attempts"]
            elif s["status"] == PARCIAL_PROXY:
                s["reason"] = "solo forma doméstica de OTRA competición (proxy descriptivo): no evalúa el partido"
                s["evidence"] = ev["attempts"]
            elif s["status"] == NO_INVESTIGADO:
                s["reason"] = ("no se intentó ninguna consulta de datos: ningún adaptador de fuente permitida implementado cubre esta competición "
                               "(fuentes excluidas por política o no revisadas; no se ha comprobado si las ligas extra de Football-Data cubrirían alguna)")
                s["evidence"] = ev["attempts"]
            m["sports_analysis_status"], m["market_analysis_status"] = ev["sports_analysis_status"], ev["market_analysis_status"]
        except ProviderLimit as e:  # límite/clave de la API: el partido sigue PENDIENTE y la cola se detiene (no se simula evaluación)
            s["status"], s["attempts"] = "PENDIENTE", s["attempts"] - 1
            s["last_error"] = f"detenido por límite de la API: {e}"
            save_state(run, st)
            common.write_json_atomic(os.path.join(run, "matrix.json"), matrix)
            print(f"AVISO: cola detenida por límite/clave de la API ({e}); quedan partidos PENDIENTES", file=sys.stderr)
            break
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
    ap.add_argument("--no-api", action="store_true", help="no usar apifootball aunque haya clave")
    ap.add_argument("--reset", default="", help="estados de la cola a volver a PENDIENTE (coma), p. ej. NO_INVESTIGADO_SIN_FUENTE_PERMITIDA,PARCIAL_PROXY_OTRA_COMPETICION")
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
    if a.reset:
        stq = load_state(a.run)
        wanted = {x.strip() for x in a.reset.split(",") if x.strip()}
        n = 0
        for rec in stq["matches"].values():
            if rec["status"] in wanted:
                rec["status"] = "PENDIENTE"
                n += 1
        save_state(a.run, stq)
        print(f"reiniciados a PENDIENTE: {n}")
    fd = FootballDataHistory(client, season)
    key = adapters.apif_key()
    prov = fd
    if key and not a.no_api:
        api_client = common.Client(os.path.join(a.run, "cache"), os.path.join(a.run, "sources", "consultas.jsonl"), policy=policy,
                                   min_interval=policy.data["providers"]["apifootball"]["limits"]["min_interval"], ttl=24 * 3600)
        api = ApiFootballHistory(api_client, key, inv["meta"]["date"])
        try:
            d0, d1 = inv["meta"]["window_utc"][0][:10], inv["meta"]["window_utc"][1][:10]
            n_odds = api.load_odds(d0, d1)
            print(f"cuotas medias de la API cargadas para {n_odds} partidos ({d0}..{d1})")
        except ProviderLimit as e:
            print(f"AVISO: no se pudieron cargar cuotas ({e})", file=sys.stderr)
        prov = CompositeProvider(api, fd)
    st, _ = process(a.run, prov, policy, a.limit)
    from collections import Counter
    print("estado de la cola:", dict(Counter(s["status"] for s in st["matches"].values())))
    return 0


if __name__ == "__main__":
    sys.exit(main())
