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
