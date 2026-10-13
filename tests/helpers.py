"""Utilidades de prueba (offline). Los datos son FICTICIOS: EJEMPLO — NO REAL."""
import os
import sys
from datetime import datetime, timezone

SCRIPTS = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", ".claude", "skills", "seleccion-final-picks", "scripts"))
sys.path.insert(0, SCRIPTS)
import common  # noqa: E402

POLICY = common.Policy(data={"providers": {
    "football-data": {"hosts": ["football-data.co.uk"], "status": "condicional", "reliability": "estructurada", "independence_group": "fd",
                      "reason": "x", "evidence": ["e"], "limits": {"min_interval": 0}},
    "apwin": {"hosts": ["apwin.com"], "status": "condicional", "reliability": "agregada", "independence_group": "apwin",
              "reason": "x", "evidence": ["e"]},
    "fotmob": {"hosts": ["fotmob.com"], "status": "excluida", "reason": "ToS prohíbe scraping", "evidence": ["https://x/tos"]},
}})


def raw(source, home, away, comp, dt, tz="UTC", conf=True, epoch=None, status=None, mid=None, country="", **extra):
    r = {"source": source, "source_match_id": mid or f"{home}-{away}", "home": home, "away": away, "competition": comp, "country": country,
         "category_hint": None, "original_datetime": dt, "source_timezone": tz, "tz_confirmed": conf, "event_status_raw": status, "url": "fixture://x"}
    if epoch is not None:
        r["utc_epoch"] = epoch
    r.update(extra)
    return r


def epoch(iso):
    return int(datetime.fromisoformat(iso.replace("Z", "+00:00")).timestamp())


def utc(iso):
    return datetime.fromisoformat(iso.replace("Z", "+00:00")).astimezone(timezone.utc)
