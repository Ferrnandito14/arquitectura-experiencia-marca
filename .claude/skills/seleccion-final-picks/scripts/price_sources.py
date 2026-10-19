#!/usr/bin/env python3
"""Capa de PRECIOS independiente de cualquier casa (Fase 1). Una estructura común y proveedores OPCIONALES.

Reglas:
- Los precios nunca definen qué partidos ni qué mercados se investigan (eso es `market_catalog.py`) ni las probabilidades del modelo.
- Un proveedor que falla (sin credenciales, caído, sin datos) NO detiene nada: `collect_prices` aísla el error y lo registra.
- Ninguna casa concreta es una dependencia: cualquier casa es, como máximo, un proveedor opcional más y solo aparece como valor del campo `bookmaker`.
- Un precio ESTIMADO por el modelo nunca cuenta como precio real (`is_real_price`).

Registro de precio (dict): match_id, entry_id, odds, source, source_type, bookmaker, observed_utc, verified, n_books, note.
source_type: «casa» (precio de una casa concreta) · «usuario» (comunicado por la persona usuaria: captura o CSV) · «agregador» (promedio de varias casas, no ejecutable)
             · «estimacion_modelo» (nunca real).
"""
import csv
import hashlib
import json
import os
import re
import statistics
from urllib.parse import parse_qs, urlparse

SOURCE_TYPES = ("casa", "usuario", "agregador", "estimacion_modelo")


def make_record(match_id, entry_id, odds, source, source_type, bookmaker=None, observed_utc=None, verified=False, n_books=None, note=None, min_books=None, **extra):
    if source_type not in SOURCE_TYPES:
        raise ValueError(f"source_type inválido: {source_type}")
    odds = float(odds)
    if odds <= 1.0:
        raise ValueError("una cuota decimal debe ser > 1.0")
    rec = {"match_id": match_id, "entry_id": entry_id, "odds": odds, "source": source, "source_type": source_type, "bookmaker": bookmaker,
           "observed_utc": observed_utc, "verified": bool(verified), "n_books": n_books, "note": note, "min_books": min_books}
    rec.update({k: v for k, v in extra.items() if v is not None})          # campos opcionales (p. ej. probabilidad del mercado sin margen)
    return rec


def demargin(odds):
    """Probabilidades SIN margen de un grupo de resultados mutuamente excluyentes de UNA casa (normalización proporcional: 1/cuota ÷ suma de 1/cuota). None si falta alguna cuota."""
    if not odds or any(o is None or o <= 1.0 for o in odds):
        return None
    inv = [1 / o for o in odds]
    t = sum(inv)
    return [x / t for x in inv]


def is_whole_line(line):
    """Líneas enteras (con devolución si el total es exacto): la probabilidad de ganar no se obtiene normalizando el par, así que no se calcula P de mercado."""
    try:
        return float(line) == int(float(line))
    except (TypeError, ValueError):
        return False


def is_real_price(rec):
    """Precio real = de una casa concreta o comunicado por la persona usuaria, y verificado. Un agregador o una estimación del modelo NO lo son."""
    return rec["source_type"] in ("casa", "usuario") and rec["verified"] is True


class PriceProvider:
    """Interfaz mínima. `supports` dice si la fuente PUEDE publicar ese mercado (y por qué no); `prices` devuelve los registros hallados."""
    name = "base"
    source_type = "agregador"

    def supports(self, entry):
        return True, None

    vocabulary = "sin descripción"            # qué mercados publica esta fuente (evidencia de «la fuente no ofrece»)

    def consulted(self, match):
        """(¿consta que esta fuente se consultó para este partido?, evidencia). Sin constancia => la investigación de ese precio está PENDIENTE (no «no encontrada»)."""
        return False, None

    # Opcional: `covers(match) -> (bool, evidencia)` para fuentes que solo cubren ciertos partidos/competiciones (si no cubre, la combinación queda «fuente_no_ofrece» para esa fuente).

    def prices(self, match, entry):
        return []


# Evidencia (observada en caché el 14-oct: 27 respuestas de get_odds) de lo que la API de cuotas publica y de lo que no.
API_ODDS_VOCABULARY = ("odd_1/odd_x/odd_2, odd_1x/odd_12/odd_x2, ah-4.5…ah+4.5 (_1/_2; incluye enteros y cuartos), o+/u+0.5…5.5 (incluye enteros), bts_yes/bts_no. "
                       "NO publica córners, tarjetas, goles por equipo ni 1.ª parte.")


class MatrixAggregatorProvider(PriceProvider):
    vocabulary = API_ODDS_VOCABULARY
    """Promedios de agregador ya guardados en matrix.json (`api_prices`). Reutiliza el mapeo de `adapters._ODDS_PAIRS` y `tickets._price`."""
    name = "apifootball (agregador)"
    source_type = "agregador"

    def __init__(self, ev_by_id, min_books=3):
        import adapters
        import tickets
        self.ev, self.min_books, self._pairs, self._price = ev_by_id, min_books, adapters._ODDS_PAIRS, tickets._price

    def consulted(self, match):
        """Evidencia de consulta: `level1.py` anota en `attempts` que apifootball fue consultada (historial + cuotas por día) para este partido. Si el historial vino de otra
        fuente (p. ej. football-data), las cuotas de apifootball NO se pidieron: la consulta de precio consta como no realizada."""
        ev = self.ev.get(match["match_id"]) or {}
        for a in ev.get("attempts") or []:
            if a.get("provider") == "apifootball" and str(a.get("resultado", "")).startswith("consultada"):
                return True, {"fuente": "apifootball get_odds (por día)", "referencia": f"matrix.json:{match['match_id']}:attempts", "detalle": a["resultado"]}
        return False, None

    def supports(self, entry):
        if entry["price_key"] is None:
            return False, "la_fuente_no_publica_este_mercado"
        if entry["price_key"] not in self._pairs:
            return False, "la_api_lo_entrega_pero_el_adaptador_no_lo_mapea" if entry.get("price_via_api") else "la_fuente_no_publica_este_mercado"
        return True, None

    def prices(self, match, entry):
        ev = self.ev.get(match["match_id"]) or {}
        if not entry["price_key"] or not ev.get("api_prices"):
            return []
        pr = self._price(ev, entry["price_key"], entry["price_idx"])
        if not pr:
            return []
        return [make_record(match["match_id"], entry["id"], pr["cuota_media"], self.name, "agregador", bookmaker="media", verified=False, n_books=pr.get("n_casas"),
                            note="promedio de mercado vía agregador: referencia, no cuota ejecutable")]


class ManualCsvProvider(PriceProvider):
    """CSV/JSON con precios comunicados por la persona usuaria (home,away,seleccion,cuota[,casa]). Cubre cualquier mercado del catálogo por etiqueta."""
    source_type = "usuario"

    def __init__(self, path):
        import common
        self.name = f"usuario:{os.path.basename(path)}"
        self.path = path
        with open(path, encoding="utf-8-sig") as fh:
            rows = list(csv.DictReader(fh)) if path.endswith(".csv") else json.load(fh)
        self.idx = {(common.norm_name(r["home"]), common.norm_name(r["away"]), r["seleccion"].strip().lower()): r for r in rows if str(r.get("cuota", "")).strip()}
        self._norm = common.norm_name

    def supports(self, entry):
        return True, None

    def consulted(self, match):
        return True, {"fuente": self.name, "referencia": self.path, "detalle": "archivo de precios de la persona usuaria"}

    def prices(self, match, entry):
        import market_catalog
        lab = market_catalog.entry_label(entry, match["home_team"], match["away_team"]).strip().lower()
        r = self.idx.get((self._norm(match["home_team"]), self._norm(match["away_team"]), lab))
        if not r:
            return []
        return [make_record(match["match_id"], entry["id"], r["cuota"], self.name, "usuario", bookmaker=(r.get("casa") or None), verified=True, note="comunicado por la persona usuaria")]


class ApifootballOddsProvider(PriceProvider):
    """Promedios de agregador calculados DIRECTAMENTE de las respuestas crudas de `get_odds` que quedaron en la caché del run (con la consulta registrada en
    `sources/consultas.jsonl`): no depende de lo que `matrix.json` guardara en su día, así que usa todas las líneas que la API publica (hándicaps enteros, totales enteros…).
    Evidencia de consulta = la consulta registrada cuya ventana (from/to) o match_id cubre el partido; sin ella la combinación queda pendiente."""
    name = "apifootball (agregador)"
    source_type = "agregador"
    vocabulary = API_ODDS_VOCABULARY

    def __init__(self, run):
        import adapters
        import common
        self.run, self.queries, rows = run, [], {}
        log = os.path.join(run, "sources", "consultas.jsonl")
        first_ts = {}
        if os.path.exists(log):
            with open(log, encoding="utf-8") as fh:
                for line in fh:
                    try:
                        j = json.loads(line)
                    except ValueError:
                        continue
                    url = j.get("url", "")
                    if "action=get_odds" in url and j.get("status") == 200:
                        first_ts.setdefault(url, j.get("ts"))
        for url, ts in first_ts.items():
            base = os.path.join(run, "cache", hashlib.sha256(common.redact_url(url).encode()).hexdigest())
            path = base + ".body"                                          # common.Client guarda el cuerpo en <sha256>.body y los metadatos en <sha256>.meta.json
            if not os.path.exists(path):
                continue
            try:
                with open(base + ".meta.json", encoding="utf-8") as fh:
                    import datetime as _dt
                    cache_ts = _dt.datetime.fromtimestamp(json.load(fh)["fetched_epoch"], _dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
            except (OSError, ValueError, KeyError):
                cache_ts = None
            try:
                with open(path, encoding="utf-8") as fh:
                    body = json.load(fh)
            except ValueError:
                continue
            if not isinstance(body, list):
                continue
            qs = parse_qs(urlparse(url).query)
            self.queries.append({"url": url, "ts": ts, "cache_utc": cache_ts, "cache": os.path.relpath(path, run), "from": (qs.get("from") or [None])[0], "to": (qs.get("to") or [None])[0],
                                 "match_id": (qs.get("match_id") or [None])[0], "filas": len(body)})
            for r in body:                                                 # misma casa y partido en varias consultas: se conserva la fila más reciente
                k = (str(r.get("match_id")), r.get("odd_bookmakers"))
                if k not in rows or str(r.get("odd_date", "")) > str(rows[k].get("odd_date", "")):
                    rows[k] = r
        self.rows = rows                                                   # {(match_id, casa): fila cruda más reciente}: el backtest filtra por odd_date < inicio del partido
        self.last_odd = {}
        for (mid, _), r in rows.items():
            self.last_odd[mid] = max(self.last_odd.get(mid, ""), str(r.get("odd_date", "")))
        self.avg = adapters.apif_odds_average(list(rows.values()), min_books=1)
        self._pairs = adapters._ODDS_PAIRS

    def _cover(self, match):
        mid = (match.get("source_match_ids") or {}).get("apifootball")
        day = str(match.get("normalized_datetime_utc", ""))[:10]
        for q in self.queries:
            if q["match_id"] and mid and q["match_id"] == mid:
                return q
        for q in self.queries:
            if q["from"] and q["to"] and q["from"] <= day <= q["to"]:
                return q
        return None

    def supports(self, entry):
        if entry["price_key"] is None:
            return False, "la_fuente_no_publica_este_mercado"
        if entry["price_key"] not in self._pairs:
            return False, "la_api_lo_entrega_pero_el_adaptador_no_lo_mapea" if entry.get("price_via_api") else "la_fuente_no_publica_este_mercado"
        return True, None

    def consulted(self, match):
        q = self._cover(match)
        if q is None:
            return False, None
        mid = (match.get("source_match_ids") or {}).get("apifootball")
        evid = {"fuente": "apifootball get_odds", "consulta": q["url"], "referencia": f"sources/consultas.jsonl + {q['cache']}", "consultado_utc": q["ts"], "filas_en_la_respuesta": q["filas"]}
        if not mid:
            evid["detalle"] = "el partido no tiene id en apifootball (no figura en su calendario): la respuesta de cuotas no puede contenerlo"
        return True, evid

    def prices(self, match, entry):
        mid = (match.get("source_match_ids") or {}).get("apifootball")
        pr = ((self.avg.get(mid) or {}).get(entry["price_key"])) if mid and entry["price_key"] else None
        if not pr or self._cover(match) is None:
            return []
        i = entry["price_idx"]
        # MEDIANA entre casas (no la media): una casa con precios atípicos (p. ej. Betfair en hándicap, 1.02–1.10) no debe inflar la referencia (observación del auditor, piloto de la Fase 5)
        grupo = pr.get("cuotas_medianas") or pr["cuotas_medias"]
        odds = grupo[i]
        spread = pr.get("minmax", [[None, None]] * (i + 1))[i]
        pm = None
        if entry["price_key"] != "resultado.doble_oportunidad" and not is_whole_line(entry.get("line")) and not str(entry["id"]).startswith(("goles.total_entero", "resultado.ah_entero")):
            dm = demargin(list(grupo))                       # P del mercado sin margen: normaliza el grupo de medianas (1X2, par más/menos, par de hándicap, ambos anotan)
            pm = None if dm is None else round(dm[i], 4)
        return [make_record(match["match_id"], entry["id"], odds, self.name, "agregador", bookmaker="mediana", observed_utc=self.last_odd.get(mid) or None,
                            verified=False, n_books=pr["n_casas"], note=f"mediana de mercado vía agregador ({pr['n_casas']} casas, rango {spread[0]}–{spread[1]}): referencia, no cuota ejecutable",
                            p_mercado_sin_margen=pm, p_mercado_n=pr["n_casas"] if pm is not None else None)]


class FootballDataOddsProvider(PriceProvider):
    """Precios de UNA casa (Bet365) publicados en los fixtures de football-data (`inventory.extra.odds`): 1X2 y más/menos de 2.5. Solo cubre las competiciones que esa fuente lista;
    para el resto de partidos la combinación queda «fuente_no_ofrece». Es el dato de un tercero: no se marca verificado."""
    name = "football-data (fixtures, Bet365)"
    source_type = "casa"
    vocabulary = "football-data fixtures: B365H/B365D/B365A (1X2) y B365>2.5/B365<2.5; sin hándicaps, córners, tarjetas, goles por equipo ni 1.ª parte"
    MAP = {"resultado.1x2.home": "B365H", "resultado.1x2.draw": "B365D", "resultado.1x2.away": "B365A", "goles.total.over.2.5": "B365>2.5", "goles.total.under.2.5": "B365<2.5"}

    def __init__(self, inv_by_id):
        self.inv = inv_by_id

    def _odds(self, match):
        m = self.inv.get(match["match_id"]) or match
        return ((m.get("extra") or {}).get("odds") or {}) if "football-data" in (m.get("source_names") or []) else {}

    def covers(self, match):
        if self._odds(match):
            return True, None
        m = self.inv.get(match["match_id"]) or match
        return False, {"fuente": self.name, "referencia": f"inventory.json:{match['match_id']}:source_names", "detalle": f"fuentes del partido: {m.get('source_names')}; no figura en los fixtures de football-data"}

    def supports(self, entry):
        return (True, None) if entry["id"] in self.MAP else (False, "la_fuente_no_publica_este_mercado")

    def consulted(self, match):
        ok, _ = self.covers(match)
        return (True, {"fuente": self.name, "referencia": f"inventory.json:{match['match_id']}:extra.odds", "detalle": "fixtures de football-data consultados por inventory.py"}) if ok else (False, None)

    def prices(self, match, entry):
        col = self.MAP.get(entry["id"])
        v = self._odds(match).get(col) if col else None
        try:
            return [make_record(match["match_id"], entry["id"], float(v), self.name, "casa", bookmaker="Bet365", verified=False, n_books=1, note="precio de un tercero (football-data); no verificado como ejecutable")]
        except (TypeError, ValueError):
            return []


class UserCaptureProvider(PriceProvider):
    """Precios que la persona usuaria comunicó con capturas (formato `partidos_usuario.json`: [liga, local, visitante, hora, [1,X,2], línea, [más, menos]]) + `ids.json` {local|visitante: match_id}.
    Consultado el archivo, cualquier combinación que no aparezca queda «consultado_no_encontrado». Es un precio comunicado y verificable por la persona usuaria; no nombra ninguna casa."""
    source_type = "usuario"
    vocabulary = "capturas de la persona usuaria: 1X2 y una línea de goles por partido"

    def __init__(self, partidos_path, ids_path):
        self.name = f"usuario:{os.path.basename(partidos_path)}"
        self.path = partidos_path
        with open(partidos_path, encoding="utf-8") as fh:
            raw = json.load(fh)
        with open(ids_path, encoding="utf-8") as fh:
            ids = json.load(fh)
        self.nota = raw.get("fuente", "capturas de la persona usuaria")
        self.capturado_utc = raw.get("capturado_utc")                 # opcional: hora UTC en que la persona usuaria tomó la captura (sin ella, la antigüedad de la cuota queda «sin hora de captura»)
        self.idx = {}
        for _liga, h, a, _hora, o1x2, line, ou in raw["partidos"]:
            mid = ids.get(f"{h}|{a}")
            if mid and line is not None and o1x2:          # una lista de partidos sin cuotas (selección automática de ligas) no es una captura de precios
                self.idx[mid] = {"1x2": o1x2, "line": float(line), "ou": ou}

    def consulted(self, match):
        if not self.idx:
            return False, None
        return True, {"fuente": self.name, "referencia": self.path, "detalle": "archivo de capturas de la persona usuaria"}

    def prices(self, match, entry):
        r = self.idx.get(match["match_id"])
        if not r:
            return []
        odds = None
        if entry["id"].startswith("resultado.1x2."):
            odds = r["1x2"][{"home": 0, "draw": 1, "away": 2}[entry["direction"]]]
        elif entry["market"] == "goles" and entry["scope"] == "match" and entry["direction"] in ("over", "under") and entry["id"].startswith("goles.total.") and entry["line"] == r["line"]:
            odds = r["ou"][0 if entry["direction"] == "over" else 1]
        return [make_record(match["match_id"], entry["id"], odds, self.name, "usuario", observed_utc=self.capturado_utc, verified=True, note=f"comunicado por la persona usuaria: {self.nota}")] if odds else []


def collect_prices(providers, matches, entries):
    """Recoge los precios de TODOS los proveedores aislando los fallos: devuelve ({(match_id, entry_id): [registros]}, [errores])."""
    out, errors = {}, []
    for prov in providers:
        try:
            for m in matches:
                for e in entries:
                    ok, _ = prov.supports(e)
                    if not ok:
                        continue
                    for rec in prov.prices(m, e):
                        out.setdefault((m["match_id"], e["id"]), []).append(rec)
        except Exception as exc:                 # un proveedor roto no detiene el catálogo ni los cálculos deportivos
            errors.append({"provider": getattr(prov, "name", str(prov)), "error": f"{type(exc).__name__}: {exc}"})
    return out, errors



# ── TheStatsAPI: cuotas pre-partido de varias casas (córners, tarjetas, goles por equipo, 1.ª parte, hándicap europeo, remates y también los mercados clásicos) ──
TSA_VOCABULARY = ("match_odds, double_chance, draw_no_bet, btts, total_goals (con enteros y cuartos), asian_handicap (con enteros y cuartos), handicap_result (europeo), first_half_result, first_half_total_goals, "
                  "team_total_goals, match_corners, team_corners, total_cards, match_shots, team_shots, match_shots_on_target, team_shots_on_target. Un mercado aparece solo si esa casa lo cotiza. NO publica fueras de juego ni tarjetas por equipo.")
_TSA_DC = {"1x": "home_draw", "12": "home_away", "x2": "draw_away"}


def tsa_lookup(entry):
    """Entrada del catálogo -> (mercado TSA, lado|None, línea|None, selección) con coincidencia EXACTA de línea y selección; None si la fuente no publica ese mercado."""
    i = entry["id"]
    m = re.fullmatch(r"corners\.total\.(over|under)\.([\d.]+)", i)
    if m:
        return "match_corners", None, m[2], m[1]
    m = re.fullmatch(r"corners\.equipo\.(home|away)\.(over|under)\.([\d.]+)", i)
    if m:
        return "team_corners", m[1], m[3], m[2]
    m = re.fullmatch(r"cards_pts\.total\.(over|under)\.([\d.]+)", i)
    if m:
        return "total_cards", None, m[2], m[1]
    m = re.fullmatch(r"goles\.equipo\.(home|away)\.(over|under)\.([\d.]+)", i)
    if m:
        return "team_total_goals", m[1], m[3], m[2]
    m = re.fullmatch(r"goles\.total(?:_entero)?\.(over|under)\.([\d.]+)", i)
    if m:
        return "total_goals", None, m[2], m[1]
    m = re.fullmatch(r"goles\.btts\.(yes|no)", i)
    if m:
        return "btts", None, None, m[1]
    m = re.fullmatch(r"primera_parte\.1x2\.(home|draw|away)", i)
    if m:
        return "first_half_result", None, None, m[1]
    m = re.fullmatch(r"primera_parte\.total\.(over|under)\.([\d.]+)", i)
    if m:
        return "first_half_total_goals", None, m[2], m[1]
    m = re.fullmatch(r"resultado\.1x2\.(home|draw|away)", i)
    if m:
        return "match_odds", None, None, m[1]
    m = re.fullmatch(r"resultado\.dc\.(1x|12|x2)", i)
    if m:
        return "double_chance", None, None, _TSA_DC[m[1]]
    m = re.fullmatch(r"resultado\.dnb\.(home|away)", i)
    if m:
        return "draw_no_bet", None, None, m[1]
    m = re.fullmatch(r"resultado\.ah(?:_entero)?\.(home|away)\.([+-][\d.]+)", i)
    if m:
        return "asian_handicap", m[1], m[2], None
    m = re.fullmatch(r"resultado\.eh\.(home|draw|away)\.([+-]\d+)", i)
    if m:
        return "handicap_result", None, m[2], m[1]
    m = re.fullmatch(r"sot\.total\.(over|under)\.([\d.]+)", i)
    if m:
        return "match_shots_on_target", None, m[2], m[1]
    m = re.fullmatch(r"sot\.equipo\.(home|away)\.(over|under)\.([\d.]+)", i)
    if m:
        return "team_shots_on_target", m[1], m[3], m[2]
    m = re.fullmatch(r"shots\.total\.(over|under)\.([\d.]+)", i)
    if m:
        return "match_shots", None, m[2], m[1]
    m = re.fullmatch(r"shots\.equipo\.(home|away)\.(over|under)\.([\d.]+)", i)
    if m:
        return "team_shots", m[1], m[3], m[2]
    return None


def _tsa_leaf(markets, mk, side, line, sel):
    v = markets.get(mk)
    if not isinstance(v, dict):
        return None
    if mk == "asian_handicap":
        v = (v.get(side) or {}).get(line)
    elif mk in ("team_corners", "team_total_goals", "team_shots", "team_shots_on_target"):
        v = ((v.get(side) or {}).get(line) or {}).get(sel)
    elif line is not None:
        v = (v.get(line) or {}).get(sel)
    else:
        v = v.get(sel)
    try:
        x = float((v or {}).get("last_seen"))
    except (TypeError, ValueError):
        return None
    return x if x > 1.0 else None


def _flip(tag):
    """'+1.5' <-> '-1.5'; '+0.0' <-> '+0.0' (el hándicap del lado contrario)."""
    f = float(tag)
    if f == 0:
        return tag
    return ("-" if f > 0 else "+") + tag.lstrip("+-")


def _tsa_overround(markets, mk, side, line, sel):
    """Suma de probabilidades implícitas del grupo de resultados mutuamente excluyentes al que pertenece la selección en ESA casa, o None si el grupo no está completo o no es comprobable."""
    if mk in ("total_goals", "match_corners", "total_cards", "first_half_total_goals", "match_shots", "match_shots_on_target", "team_corners", "team_total_goals", "team_shots", "team_shots_on_target"):
        other = "under" if sel == "over" else "over"
        a, b = _tsa_leaf(markets, mk, side, line, sel), _tsa_leaf(markets, mk, side, line, other)
        return None if not (a and b) else 1 / a + 1 / b
    if mk in ("btts", "draw_no_bet"):
        keys = ("yes", "no") if mk == "btts" else ("home", "away")
        vals = [_tsa_leaf(markets, mk, None, None, k) for k in keys]
        return None if not all(vals) else sum(1 / v for v in vals)
    if mk in ("match_odds", "first_half_result"):
        vals = [_tsa_leaf(markets, mk, None, None, k) for k in ("home", "draw", "away")]
        return None if not all(vals) else sum(1 / v for v in vals)
    if mk == "handicap_result":
        vals = [_tsa_leaf(markets, mk, None, line, k) for k in ("home", "draw", "away")]
        return None if not all(vals) else sum(1 / v for v in vals)
    if mk == "asian_handicap":
        a = _tsa_leaf(markets, mk, side, line, None)
        b = _tsa_leaf(markets, mk, "away" if side == "home" else "home", _flip(line), None)
        return None if not (a and b) else 1 / a + 1 / b
    return None          # double_chance: no hay un grupo de dos o tres salidas comprobable


OVERROUND_RANGE = {"2": (0.97, 1.15), "3": (0.97, 1.20)}      # un par/trío de una casa fuera de este rango es un precio roto (p. ej. 1.01/10.5 en hándicap), no una cuota real


class TheStatsApiOddsProvider(PriceProvider):
    """Mediana entre casas del último precio visto (tipo «agregador»: referencia, nunca ejecutable). Lee lo que dejó `tsa_fetch.py` (<run>/thestatsapi). Con una sola casa en la línea el precio se acepta pero lo marca `n_books`."""
    name = "thestatsapi (agregador)"
    vocabulary = TSA_VOCABULARY

    def __init__(self, run):
        self.run, self.map, self.bodies, self.unmatched = run, {}, {}, {}
        base = os.path.join(run, "thestatsapi")
        mp = os.path.join(base, "map.json")
        if os.path.exists(mp):
            with open(mp, encoding="utf-8") as fh:
                d = json.load(fh)
            self.map, self.unmatched = d.get("partidos", {}), d.get("sin_emparejar", {})
            self.generated = d.get("generado_utc")
            for mid, e in self.map.items():
                path = os.path.join(base, "odds", f"{e['tsa_id']}.json")
                if os.path.exists(path):
                    with open(path, encoding="utf-8") as fh:
                        w = json.load(fh)
                    self.bodies[mid] = {"fetched_utc": w.get("fetched_utc"), "books": (w.get("response") or {}).get("data", {}).get("bookmakers", []), "tsa_id": e["tsa_id"]}

    def covers(self, match):
        mid = match["match_id"]
        if mid in self.bodies:
            return True, None
        why = (self.unmatched.get(mid) or {}).get("motivo") or ("el partido no tiene cuotas en la fuente" if mid in self.map else "partido no emparejado con la fuente")
        return False, {"fuente": self.name, "referencia": "thestatsapi/map.json", "detalle": why}

    def supports(self, entry):
        if tsa_lookup(entry) is None:
            return False, "la_fuente_no_publica_este_mercado"
        return True, None

    def consulted(self, match):
        b = self.bodies.get(match["match_id"])
        if not b:
            return False, None
        return True, {"fuente": "thestatsapi /football/matches/{id}/odds", "referencia": f"thestatsapi/odds/{b['tsa_id']}.json", "consultado_utc": b["fetched_utc"], "casas_en_la_respuesta": len(b["books"])}

    def prices(self, match, entry):
        b = self.bodies.get(match["match_id"])
        look = tsa_lookup(entry)
        if not b or look is None:
            return []
        mk, side, line, sel = look
        got, dropped, pbooks = [], [], []
        whole = is_whole_line(line) if (line is not None and mk != "handicap_result") else False
        for bk in b["books"]:
            mkts = bk.get("markets") or {}
            x = _tsa_leaf(mkts, mk, side, line, sel)
            if not x:
                continue
            ov = _tsa_overround(mkts, mk, side, line, sel)
            if ov is not None:
                lo, hi = OVERROUND_RANGE["3" if mk in ("match_odds", "first_half_result", "handicap_result") else "2"]
                if not lo <= ov <= hi:
                    dropped.append(bk["bookmaker"])
                    continue
                if not whole:
                    pbooks.append((bk["bookmaker"], (1 / x) / ov))        # P sin margen de ESA casa: la normalización se hace casa por casa y luego se toma la mediana
            got.append((bk["bookmaker"], x))
        if not got:
            return []
        xs = [x for _, x in got]
        pm = round(statistics.median(p for _, p in pbooks), 4) if pbooks else None
        pp = next((round(p, 4) for n, p in pbooks if n == "Pinnacle"), None)
        extra = f"; descartado por precios incoherentes de su par/trío: {', '.join(dropped)}" if dropped else ""
        return [make_record(match["match_id"], entry["id"], statistics.median(xs), self.name, "agregador", bookmaker="mediana", observed_utc=b["fetched_utc"], verified=False, n_books=len(xs), min_books=1,
                            note=f"mediana de {len(xs)} casa(s) ({', '.join(n for n, _ in got)}), rango {min(xs)}–{max(xs)}{extra}; último precio visto: referencia, no cuota ejecutable",
                            p_mercado_sin_margen=pm, p_mercado_n=len(pbooks) if pm is not None else None, p_pinnacle_sin_margen=pp)]
