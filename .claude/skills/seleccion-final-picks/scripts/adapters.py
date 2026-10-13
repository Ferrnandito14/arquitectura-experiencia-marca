#!/usr/bin/env python3
"""Adaptadores de calendario. Cada uno devuelve registros BRUTOS homogéneos:
  {source, source_match_id, home, away, competition, country, category_hint, original_datetime,
   source_timezone, tz_confirmed, event_status_raw, url, utc_epoch (opcional)}
No deciden identidad, estado ni elegibilidad: eso lo hace inventory.py.
Sólo se instancian para proveedores 'permitida'/'condicional' en sources_policy.json
(el Client lo impone: PolicyError si no)."""
import csv
import io
import json
import re
from datetime import datetime, timezone

FD_BASE = "https://www.football-data.co.uk"
APWIN_BASE = "https://www.apwin.com"

# Códigos de división de football-data -> (país, competición). Sólo los documentados en su web.
FD_DIV = {
    "E0": ("England", "Premier League"), "E1": ("England", "Championship"), "E2": ("England", "League One"),
    "E3": ("England", "League Two"), "EC": ("England", "National League"),
    "SC0": ("Scotland", "Premiership"), "SC1": ("Scotland", "Championship"), "SC2": ("Scotland", "League One"),
    "SC3": ("Scotland", "League Two"), "D1": ("Germany", "Bundesliga"), "D2": ("Germany", "2. Bundesliga"),
    "I1": ("Italy", "Serie A"), "I2": ("Italy", "Serie B"), "SP1": ("Spain", "La Liga"),
    "SP2": ("Spain", "La Liga 2"), "F1": ("France", "Ligue 1"), "F2": ("France", "Ligue 2"),
    "N1": ("Netherlands", "Eredivisie"), "B1": ("Belgium", "Pro League"), "P1": ("Portugal", "Primeira Liga"),
    "T1": ("Turkey", "Super Lig"), "G1": ("Greece", "Super League"),
}


def fd_fixtures(client):
    """Fixtures de Football-Data (CSV). Hora: se asume hora del Reino Unido (la web no la declara) -> tz_confirmed=False."""
    r = client.fetch(FD_BASE + "/fixtures.csv")
    rows = list(csv.DictReader(io.StringIO(r.text.lstrip("﻿"))))
    out = []
    for i, x in enumerate(rows):
        if not x.get("Date") or not x.get("HomeTeam"):
            continue
        country, comp = FD_DIV.get(x.get("Div", ""), ("", x.get("Div", "")))
        try:
            d = datetime.strptime(x["Date"], "%d/%m/%Y")
        except ValueError:
            d = datetime.strptime(x["Date"], "%d/%m/%y")
        hh, mm = (x.get("Time") or "").split(":") if x.get("Time") else (None, None)
        iso = d.strftime("%Y-%m-%d") + (f" {int(hh):02d}:{int(mm):02d}" if hh is not None else "")
        out.append({
            "source": "football-data", "source_match_id": f"{x.get('Div')}:{x['Date']}:{x['HomeTeam']}-{x['AwayTeam']}",
            "home": x["HomeTeam"], "away": x["AwayTeam"], "competition": comp, "country": country,
            "category_hint": None, "original_datetime": iso, "source_timezone": "Europe/London", "tz_confirmed": False,
            "event_status_raw": None, "url": FD_BASE + "/fixtures.csv", "div": x.get("Div"),
            "odds": {k: x[k] for k in ("B365H", "B365D", "B365A", "B365>2.5", "B365<2.5") if x.get(k)},
            "referee": x.get("Referee") or None,
        })
    return out


_APWIN_STATUS = {"upcoming": "PROGRAMADO", "live": "EN_JUEGO", "finished": "FINALIZADO", "postponed": "APLAZADO",
                 "cancelled": "CANCELADO", "canceled": "CANCELADO"}


def apwin_pagination(txt):
    """{'page','has_more','declared_total'} del bloque `"pagination":{...}` embebido, o None si no existe."""
    m = re.search(r'"pagination":\{"page":(\d+),"hasMore":(true|false),"total":(\d+)', txt)
    return {"page": int(m.group(1)), "has_more": m.group(2) == "true", "declared_total": int(m.group(3))} if m else None


def apwin_home(client, day_iso=None):
    return apwin_fetch(client, day_iso)[0]


def apwin_fetch(client, day_iso=None):
    """Portada de APWin (HTML público). Devuelve (registros, paginación). El HTML solo trae la PÁGINA 1 de una lista
    paginada que el cliente completa con llamadas que NO se usan: el universo es una cota inferior."""
    url = APWIN_BASE + "/" + (f"?date={day_iso}" if day_iso else "")
    r = client.fetch(url)
    txt = r.text.replace('\\"', '"')
    out = []
    ctx = sorted([(m.start(), m.group(1), "league") for m in re.finditer(r'"leagueSlug":"([^"]+)"', txt)]
                 + [(m.start(), m.group(1), "country") for m in re.finditer(r'"countrySlug":"([^"]+)"', txt)])
    dec = json.JSONDecoder()
    for m in re.finditer(r'\{"slug":"', txt):
        try:
            obj, _ = dec.raw_decode(txt, m.start())          # objeto JSON completo y balanceado: no cruza partidos
        except ValueError:
            continue
        if not all(k in obj for k in ("homeTeam", "awayTeam", "kickoffUnix", "id")):
            continue
        lg = [c[1] for c in ctx if c[0] < m.start() and c[2] == "league"]
        ct = [c[1] for c in ctx if c[0] < m.start() and c[2] == "country"]
        ep = int(obj["kickoffUnix"])
        out.append({
            "source": "apwin", "source_match_id": str(obj["id"]), "home": obj["homeTeam"], "away": obj["awayTeam"],
            "competition": (lg[-1] if lg else "").replace("-", " "), "country": (ct[-1] if ct else "").replace("-", " "),
            "category_hint": None, "original_datetime": str(ep), "source_timezone": "UTC", "tz_confirmed": True, "utc_epoch": ep,
            "event_status_raw": obj.get("status"), "url": url,
        })
    pag = apwin_pagination(txt)
    if pag:
        pag.update(url=url, loaded=len(out), day=day_iso)
    return out, pag


APWIN_API = APWIN_BASE + "/api/home/calendar"
APWIN_API_TZ = "America/New_York"      # misma zona y país con los que el HTML sirve la página 1
APWIN_API_COUNTRY = "US"
APWIN_MAX_PAGES_PER_DAY = 14


def apwin_api_records(payload, url):
    """Registros brutos de la respuesta JSON de /api/home/calendar (mismo esquema que el feed embebido)."""
    out = []
    for g in payload.get("groups") or []:
        for obj in g.get("matches") or []:
            if not all(k in obj for k in ("homeTeam", "awayTeam", "kickoffUnix", "id")):
                continue
            ep = int(obj["kickoffUnix"])
            out.append({
                "source": "apwin", "source_match_id": str(obj["id"]), "home": obj["homeTeam"], "away": obj["awayTeam"],
                "competition": (g.get("leagueSlug") or g.get("name") or "").replace("-", " "),
                "country": (g.get("countrySlug") or "").replace("-", " "),
                "category_hint": None, "original_datetime": str(ep), "source_timezone": "UTC", "tz_confirmed": True, "utc_epoch": ep,
                "event_status_raw": obj.get("status"), "url": url,
            })
    return out


def apwin_fetch_all(client, day_iso, max_pages=APWIN_MAX_PAGES_PER_DAY):
    """Página 1 (HTML) + páginas siguientes del JSON público `/api/home/calendar` que usa la propia web (misma
    zona/país que el HTML; robots.txt no lo veta; sin sesión). Se detiene en hasMore=false, respuesta no válida,
    página sin partidos nuevos o tope. Devuelve (registros_deduplicados, paginación) con loaded vs declared_total."""
    from urllib.parse import urlencode
    recs, pag = apwin_fetch(client, day_iso)
    if not pag:
        return recs, pag
    seen = {r["source_match_id"] for r in recs}
    pages, stop, page = 1, None, pag["page"]
    while pag["has_more"] and stop is None:
        if pages >= max_pages:
            stop = "tope de páginas"
            break
        page += 1
        url = APWIN_API + "?" + urlencode({"date": day_iso, "locale": "en", "timezone": APWIN_API_TZ,
                                           "country": APWIN_API_COUNTRY, "page": page})
        try:
            payload = json.loads(client.fetch(url).text)
            p = payload["pagination"]
            if not (isinstance(p["hasMore"], bool) and isinstance(p["total"], int) and isinstance(payload["groups"], list)):
                raise ValueError("estructura inesperada")
        except Exception as e:      # FetchError/PolicyError/JSON/estructura: no se inventa nada; se informa
            stop = f"error en página {page}: {type(e).__name__}"
            break
        new = [r for r in apwin_api_records(payload, url) if r["source_match_id"] not in seen]
        pages += 1
        pag["declared_total"] = p["total"]
        pag["has_more"] = p["hasMore"]
        if not new:
            stop = f"página {page} sin partidos nuevos"
            break
        seen.update(r["source_match_id"] for r in new)
        recs.extend(new)
    pag.update(loaded=len(recs), pages_fetched=pages, stop_reason=stop or "hasMore=false",
               complete=(not pag["has_more"]) and len(recs) >= pag["declared_total"])
    return recs, pag


def apwin_status(raw):
    return _APWIN_STATUS.get((raw or "").lower(), "DESCONOCIDO")


def manual_calendar(path):
    """Calendario aportado por la persona usuaria (JSON o CSV). Campos: home, away, competition, country,
    datetime_utc (ISO con Z) | datetime + timezone, status(opc.), source_label(opc.)."""
    out = []
    if path.endswith(".json"):
        rows = json.load(open(path, encoding="utf-8"))
    else:
        rows = list(csv.DictReader(open(path, encoding="utf-8-sig")))
    for i, x in enumerate(rows):
        if x.get("datetime_utc"):
            dt = datetime.fromisoformat(x["datetime_utc"].replace("Z", "+00:00"))
            orig, tz, conf, ep = x["datetime_utc"], "UTC", True, int(dt.timestamp())
        else:
            orig, tz, conf, ep = x.get("datetime"), x.get("timezone"), bool(x.get("timezone")), None
        out.append({"source": "usuario:" + (x.get("source_label") or "manual"), "source_match_id": str(x.get("id") or i),
                    "home": x["home"], "away": x["away"], "competition": x.get("competition", ""), "country": x.get("country", ""),
                    "category_hint": x.get("category"), "original_datetime": orig, "source_timezone": tz,
                    "tz_confirmed": conf, "utc_epoch": ep, "event_status_raw": x.get("status"), "url": path})
    return out


# ----------------------------------------------------------------------------- apifootball.com (API v3, clave propia)
import os  # noqa: E402
from urllib.parse import urlencode  # noqa: E402

APIF_BASE = "https://apiv3.apifootball.com/"
_APIF_LIMIT = re.compile(r"limit|exceed|quota|too many|suspend|expired|invalid|not authori|unauthori|subscription|plan", re.I)


class ApiLimit(Exception):
    """La API rechazó la petición por límite/clave/plan: se detiene la cola SIN marcar partidos como evaluados."""


def apif_key():
    """Clave desde el entorno: APIFOOTBALL_KEY, o el fichero apuntado por APIFOOTBALL_KEY_FILE. Nunca se imprime."""
    k = os.environ.get("APIFOOTBALL_KEY")
    if not k and os.environ.get("APIFOOTBALL_KEY_FILE"):
        try:
            k = open(os.environ["APIFOOTBALL_KEY_FILE"], encoding="utf-8").read()
        except OSError:
            k = None
    return (k or "").strip() or None


def apif_call(client, key, **params):
    """GET con la zona/valores correctamente codificados (urlencode: `America/Caracas` -> `America%2FCaracas`)."""
    url = APIF_BASE + "?" + urlencode({**params, "APIkey": key})
    try:
        r = client.fetch(url)
    except Exception as e:
        msg = str(e).replace(key, "***")
        if getattr(e, "status", None) in (401, 403, 429):
            raise ApiLimit(msg)
        raise type(e)(msg) if not isinstance(e, (OSError,)) else e
    try:
        d = json.loads(r.text)
    except ValueError:
        raise ApiLimit("respuesta no JSON de la API")
    if isinstance(d, dict) and "error" in d:
        text = f"{d.get('error')}: {d.get('message', '')}"
        if _APIF_LIMIT.search(text) and "no event" not in text.lower() and "no odds" not in text.lower():
            raise ApiLimit(text[:200])
        return []                     # p. ej. «No event found!»: lista vacía legítima
    return d


_APIF_STATUS_FIN = ("finished", "after pen", "after extra", "awarded", "walkover")


def apif_status(raw):
    """Normaliza el estado de apifootball al vocabulario del feed ya mapeado (upcoming/live/finished/postponed/cancelled)."""
    s = (raw or "").strip().lower()
    if s in ("", "not started"):
        return "upcoming"
    if s.startswith(_APIF_STATUS_FIN):
        return "finished"
    if "postpon" in s or "delayed" in s:
        return "postponed"
    if "cancel" in s or "abandon" in s or "suspend" in s:
        return "cancelled"
    return "live"          # «Half Time», minuto en juego, etc.


def apif_event_records(events, source_url_label="apiv3.apifootball.com get_events"):
    """Registros brutos de calendario (hora UTC pedida con timezone=UTC) + ids de la API en `api`."""
    out = []
    for e in events:
        if not e.get("match_date") or not e.get("match_time") or not e.get("match_hometeam_name"):
            continue
        out.append({
            "source": "apifootball", "source_match_id": str(e["match_id"]), "home": e["match_hometeam_name"], "away": e["match_awayteam_name"],
            "competition": e.get("league_name", ""), "country": e.get("country_name", ""), "category_hint": None,
            "original_datetime": f"{e['match_date']} {e['match_time']}", "source_timezone": "UTC", "tz_confirmed": True,
            "event_status_raw": apif_status(e.get("match_status")), "url": source_url_label,
            "api": {"match_id": str(e["match_id"]), "home_id": str(e.get("match_hometeam_id") or ""), "away_id": str(e.get("match_awayteam_id") or ""),
                    "league_id": str(e.get("league_id") or ""), "league_name": e.get("league_name"), "home_name": e["match_hometeam_name"],
                    "away_name": e["match_awayteam_name"], "referee": (e.get("match_referee") or None), "status_raw": e.get("match_status")},
        })
    return out


def apif_events(client, key, day_from, day_to):
    return apif_call(client, key, action="get_events", **{"from": day_from, "to": day_to}, timezone="UTC")


_ODDS_PAIRS = {"resultado.1x2": ("odd_1", "odd_x", "odd_2"), "resultado.doble_oportunidad": ("odd_1x", "odd_12", "odd_x2"),
               "goles.btts": ("bts_yes", "bts_no")}
for _l in ("0.5", "1.5", "2.5", "3.5", "4.5", "5.5"):
    _ODDS_PAIRS["goles.over_" + _l.replace(".", "_")] = ("o+" + _l, "u+" + _l)
for _l in ("-2.5", "-1.5", "-0.5", "+0.5", "+1.5", "+2.5"):          # hándicap asiático de media línea (sin devolución): local con _l, visitante con -_l
    _ODDS_PAIRS["resultado.handicap" + _l] = ("ah" + _l + "_1", "ah" + _l + "_2")


def apif_odds_average(rows, min_books=2):
    """{match_id: {mercado: {cuotas_medias, n_casas, minmax, casas}}}. Promedio simple por casa: referencia de mercado, NO cuota ejecutable."""
    by = {}
    for r in rows or []:
        by.setdefault(str(r.get("match_id")), []).append(r)
    out = {}
    for mid, rs in by.items():
        mk = {}
        for key, cols in _ODDS_PAIRS.items():
            vals = {c: [] for c in cols}
            books = []
            for r in rs:
                try:
                    v = [float(r[c]) for c in cols]
                except (KeyError, ValueError, TypeError):
                    continue
                if all(x > 1.0 for x in v):
                    for c, x in zip(cols, v):
                        vals[c].append(x)
                    books.append(r.get("odd_bookmakers"))
            if len(books) >= min_books:
                import statistics
                tuples = {tuple(vals[c][i] for c in cols) for i in range(len(books))}
                mk[key] = {"cuotas_medias": [round(sum(vals[c]) / len(vals[c]), 3) for c in cols],
                           "cuotas_medianas": [round(statistics.median(vals[c]), 3) for c in cols],     # robusta a una casa atípica
                           "n_casas": len(books), "n_precios_distintos": len(tuples),                     # casas que repiten el mismo precio no son independientes
                           "minmax": [[min(vals[c]), max(vals[c])] for c in cols], "casas": sorted(set(books))}
        if mk:
            out[mid] = mk
    return out


def _stat(e, name):
    for s in e.get("statistics") or []:
        if s.get("type") == name:
            try:
                return int(s["home"]), int(s["away"])
            except (ValueError, TypeError, KeyError):
                return None
    return None


def _cards_from_list(e):
    cl = e.get("cards") or []
    if not cl:
        return None
    y, r = [0, 0], [0, 0]
    for c in cl:
        kind = (c.get("card") or "").lower()
        side = 0 if c.get("home_fault") else (1 if c.get("away_fault") else None)
        if side is None:
            continue
        if "red" in kind:
            r[side] += 1
        elif "yellow" in kind:
            y[side] += 1
    return tuple(y), tuple(r)


def _played_ids(e):
    """Ids de jugadores que disputaron algún minuto, por lado (0 local, 1 visitante): titulares + los que entraron (también los sustituidos después).
    None para un lado si la API no trae alineación (entonces no se filtra)."""
    lu = e.get("lineup") or {}
    subs = e.get("substitutions") or {}
    out = [None, None]
    for i, side in enumerate(("home", "away")):
        starters = {p.get("player_key") for p in ((lu.get(side) or {}).get("starting_lineups") or []) if p.get("player_key")}
        if not starters:
            continue
        ids = set(starters)
        for sb in subs.get(side) or []:
            for pid in str(sb.get("substitution_player_id") or "").split("|"):
                if pid.strip():
                    ids.add(pid.strip())
        out[i] = ids
    return out


def _card_points(e):
    """Puntos de tarjetas por equipo (local, visitante) con la regla de la casa de la persona usuaria: amarilla = 1, roja = 2, máximo 3 por jugador
    (1 amarilla + 1 roja directa = 3; dos amarillas = expulsión = 2 puntos EN TOTAL, confirmado por la persona usuaria el 13-oct), solo jugadores (los eventos sin nombre de jugador son del cuerpo técnico y se
    ignoran) y solo 90' + descuento (la prórroga no cuenta; las del entretiempo sí). Sin lista de eventos o con 0 puntos en ambos equipos => None
    (dato faltante: un 0-0 de tarjetas es casi siempre un dato ausente y no se cuenta como 0). LIMITACIÓN: la API no marca si el jugador estaba en la
    cancha o en el banquillo; las tarjetas a suplentes con nombre se cuentan."""
    cl = e.get("cards") or []
    if not cl:
        return None
    played = _played_ids(e)
    per = {}
    for c in cl:
        side = 0 if c.get("home_fault") else (1 if c.get("away_fault") else None)
        if side is None:
            continue
        pid = c.get("home_player_id") if side == 0 else c.get("away_player_id")
        if played[side] is not None and pid and pid not in played[side]:
            continue        # regla de la casa: no cuentan las tarjetas a quien no disputó ningún minuto (suplente que no entró)
        t = str(c.get("time") or "").strip()
        if str(c.get("score_info_time") or "").lower().startswith("extra") or (t.isdigit() and int(t) > 90):
            continue
        name = c.get("home_fault") or c.get("away_fault")
        kind = (c.get("card") or "").lower()
        y_r = per.setdefault((side, name), [0, 0])
        if "red" in kind:
            y_r[1] += 1
        elif "yellow" in kind:
            y_r[0] += 1
    pts = [0, 0]
    for (side, _), (y, r) in per.items():
        # regla confirmada por la persona usuaria: la 2.ª amarilla cuenta 2 puntos EN TOTAL (no 3); amarilla + roja directa = 3; roja directa = 2
        p = 2 if y >= 2 else min(3, y + 2 * r)
        pts[side] += p
    return None if pts == [0, 0] else (pts[0], pts[1])


def apif_history_row(e, team_id):
    """Fila de historial (mismo formato que FootballDataHistory.team_history) desde un evento FINALIZADO de la API.
    Falta de estadística => None (nunca 0 inventado)."""
    home = str(e.get("match_hometeam_id")) == str(team_id)
    try:
        hs, as_ = int(e["match_hometeam_score"]), int(e["match_awayteam_score"])
    except (ValueError, TypeError, KeyError):
        return None
    gi = lambda t, i: (t[i] if t else None)
    yl = _stat(e, "Yellow Cards")
    cl = _cards_from_list(e)
    yellow = yl if yl else (cl[0] if cl else None)
    red = _stat(e, "Red Cards") or (cl[1] if cl else None)     # lista de tarjetas vacía => rojas desconocidas (None), no 0
    ht = (e.get("match_hometeam_halftime_score"), e.get("match_awayteam_halftime_score"))
    ht = tuple(int(x) if str(x).strip().isdigit() else None for x in ht)
    shots, sot, corners, fouls = _stat(e, "Shots Total"), _stat(e, "Shots On Goal"), _stat(e, "Corners"), _stat(e, "Fouls")
    cp = _card_points(e)
    stat_pts = (yellow[0] + 2 * red[0], yellow[1] + 2 * red[1]) if (yellow and red and None not in tuple(yellow) + tuple(red)) else None
    if cp is None and stat_pts and sum(stat_pts) > 0:
        cp = stat_pts                                                 # sin lista de eventos: puntos desde estadísticas agregadas (pueden incluir cuerpo técnico)
    elif cp is not None and stat_pts is not None and any(abs(cp[i] - stat_pts[i]) >= 2 for i in (0, 1)):
        cp = None                                                     # eventos y estadísticas del proveedor discrepan en ≥2 puntos: dato DEFECTUOSO, no se usa (auditor)
    return {"date": e["match_date"], "competition": e.get("league_name") or "?", "venue": "local" if home else "visitante",
            "cards_pts": (cp[0], cp[1]) if cp else (None, None),
            "opponent": e["match_awayteam_name"] if home else e["match_hometeam_name"],
            "gf": hs if home else as_, "ga": as_ if home else hs, "ht_goals": ht,
            "corners": (gi(corners, 0), gi(corners, 1)) if corners else (None, None),
            "yellow": (gi(yellow, 0), gi(yellow, 1)) if yellow else (None, None),
            "red": (gi(red, 0), gi(red, 1)) if red else (None, None),
            "shots": (gi(shots, 0), gi(shots, 1)) if shots else (None, None),
            "sot": (gi(sot, 0), gi(sot, 1)) if sot else (None, None),
            "fouls": (gi(fouls, 0), gi(fouls, 1)) if fouls else (None, None),
            "referee": e.get("match_referee") or None, "api_match_id": str(e.get("match_id"))}
