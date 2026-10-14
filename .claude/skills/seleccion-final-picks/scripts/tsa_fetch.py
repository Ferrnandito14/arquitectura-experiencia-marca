#!/usr/bin/env python3
"""Descarga de cuotas pre-partido de TheStatsAPI para los partidos de un run (segunda fuente de cuotas, OPCIONAL e independiente de cualquier casa).

- Autenticación: `Authorization: Bearer <clave>`. La clave sale de THESTATSAPI_KEY / THESTATSAPI_KEY_FILE / --key-file y NUNCA se imprime, registra ni guarda (los registros llevan solo la URL sin credenciales).
- Política: el host debe figurar en `sources_policy.json` (estado condicional); ritmo mínimo entre peticiones y respeto de `Retry-After`; un 401/403 detiene todo.
- Emparejamiento de partidos EXACTO: misma hora de inicio (±60 min) y, a la vez, los equipos locales y los visitantes comparten palabras de su nombre; si hay más de un candidato o ninguno, el partido NO se empareja (queda registrado con el motivo).
- Salida: `<run>/thestatsapi/map.json` y `<run>/thestatsapi/odds/<id>.json` (respuesta cruda + hora de consulta), solo lo necesario para la ejecución."""
import argparse
import json
import os
import re
import sys
import time
import unicodedata
import urllib.error
import urllib.request
from datetime import datetime, timedelta, timezone

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common  # noqa: E402

BASE = "https://api.thestatsapi.com/api"
HOST = "api.thestatsapi.com"
UA = "football-picks-system/0.1"
STOPWORDS = {"fc", "cf", "sc", "ac", "afc", "club", "de", "the", "cd", "ca", "real", "city", "united", "utd", "sk", "fk", "fa"}


def api_key(key_file=None):
    k = os.environ.get("THESTATSAPI_KEY")
    path = key_file or os.environ.get("THESTATSAPI_KEY_FILE")
    if not k and path and os.path.exists(path):
        with open(path, encoding="utf-8") as fh:
            k = fh.read().strip()
    return k


def _tokens(name):
    """Palabras del nombre sin términos genéricos, más sus INICIALES cuando hay ≥ 3 palabras (PSG = Paris Saint-Germain, QPR = Queens Park Rangers)."""
    s = unicodedata.normalize("NFKD", str(name or "")).encode("ascii", "ignore").decode().lower()
    words = re.sub(r"[^a-z0-9 ]", " ", s).split()
    out = {t for t in words if t not in STOPWORDS}
    if len(words) >= 3:
        out.add("".join(w[0] for w in words))
    return out


def _t(iso):
    return datetime.fromisoformat(iso.replace("Z", "+00:00")).astimezone(timezone.utc)


def pair_match(match, tsa_rows, tolerance_min=60):
    """(fila de TheStatsAPI | None, motivo). Exige hora ±tolerancia Y coincidencia de palabras en local y en visitante (nunca solo en uno)."""
    t0 = _t(match["normalized_datetime_utc"])
    h, a = _tokens(match["home_team"]), _tokens(match["away_team"])
    good = []
    for r in tsa_rows:
        try:
            dt = abs((_t(r["utc_date"]) - t0).total_seconds()) / 60
        except (KeyError, ValueError):
            continue
        if dt > tolerance_min:
            continue
        rh, ra = _tokens(r["home_team"]["name"]), _tokens(r["away_team"]["name"])
        if (h & rh) and (a & ra):
            good.append(r)
    if len(good) == 1:
        return good[0], None
    return None, ("ningún partido con la misma hora y ambos equipos" if not good else f"{len(good)} candidatos: emparejamiento ambiguo")


class Fetcher:
    def __init__(self, key, policy=None, min_interval=2.3, sleep=time.sleep, opener=None):
        self.key, self.policy, self.min_interval, self.sleep = key, policy or common.Policy(), min_interval, sleep
        self.opener = opener or urllib.request.urlopen
        self.last = 0.0
        self.log_path = None
        self.calls = 0

    def get(self, path):
        name, p = self.policy.lookup(HOST)
        if not p or p.get("status") not in ("permitida", "condicional"):
            raise common.PolicyError(f"{HOST} no está permitido por sources_policy.json")
        wait = self.min_interval - (time.monotonic() - self.last)
        if wait > 0:
            self.sleep(wait)
        req = urllib.request.Request(BASE + path, headers={"Authorization": "Bearer " + self.key, "User-Agent": UA, "Accept": "application/json"})
        for attempt in range(3):
            try:
                r = self.opener(req, timeout=40)
                code, body = r.status, r.read().decode("utf-8")
            except urllib.error.HTTPError as e:
                code, body = e.code, e.read().decode("utf-8", "replace")
                if code == 429 and attempt < 2:
                    self.sleep(int(e.headers.get("Retry-After") or 20))
                    continue
            self.last = time.monotonic()
            self.calls += 1
            if self.log_path:
                with open(self.log_path, "a", encoding="utf-8") as fh:
                    fh.write(json.dumps({"provider": "thestatsapi", "status": code, "ts": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"), "url": BASE + path}) + "\n")
            return code, body
        return 429, body


def run(run_dir, match_ids, fetcher, now=None):
    inv = {m["match_id"]: m for m in common.read_json(os.path.join(run_dir, "inventory.json"))["matches"]}
    ms = [inv[i] for i in match_ids]
    times = [_t(m["normalized_datetime_utc"]) for m in ms]
    d0, d1 = (min(times) - timedelta(days=1)).strftime("%Y-%m-%d"), (max(times) + timedelta(days=1)).strftime("%Y-%m-%d")
    rows, page = [], 1
    while True:
        code, body = fetcher.get(f"/football/matches?date_from={d0}&date_to={d1}&per_page=100&sort=utc_date&page={page}")
        if code in (401, 403):
            raise SystemExit(f"TheStatsAPI rechazó la clave ({code}): {json.loads(body).get('error', {}).get('message') if body else ''}")
        if code != 200:
            raise SystemExit(f"error {code} al listar partidos")
        d = json.loads(body)
        rows += d["data"]
        if page >= (d.get("meta") or {}).get("total_pages", 1):
            break
        page += 1
    out_dir = os.path.join(run_dir, "thestatsapi")
    os.makedirs(os.path.join(out_dir, "odds"), exist_ok=True)
    mapping, unmatched = {}, {}
    for m in ms:
        r, why = pair_match(m, rows)
        if r is None:
            unmatched[m["match_id"]] = {"partido": f"{m['home_team']} – {m['away_team']}", "motivo": why}
            continue
        entry = {"tsa_id": r["id"], "home": r["home_team"]["name"], "away": r["away_team"]["name"], "utc_date": r["utc_date"], "odds_available": bool(r.get("odds_available")), "status": r.get("status")}
        if r.get("odds_available") and r.get("status") == "scheduled":
            code, body = fetcher.get(f"/football/matches/{r['id']}/odds")
            entry["odds_http"] = code
            if code == 200:
                with open(os.path.join(out_dir, "odds", f"{r['id']}.json"), "w", encoding="utf-8") as fh:
                    json.dump({"fetched_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"), "tsa_match_id": r["id"], "response": json.loads(body)}, fh, ensure_ascii=False)
        mapping[m["match_id"]] = entry
    common.write_json_atomic(os.path.join(out_dir, "map.json"), {"generado_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"), "partidos": mapping, "sin_emparejar": unmatched})
    return mapping, unmatched


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--run", required=True)
    ap.add_argument("--ids", required=True, help="JSON {«local|visitante»: match_id}: los valores definen los partidos")
    ap.add_argument("--key-file")
    ap.add_argument("--min-interval", type=float, default=2.3)
    a = ap.parse_args(argv)
    key = api_key(a.key_file)
    if not key:
        print("error: sin clave (THESTATSAPI_KEY / THESTATSAPI_KEY_FILE / --key-file)", file=sys.stderr)
        return 2
    f = Fetcher(key, min_interval=a.min_interval)
    f.log_path = os.path.join(a.run, "sources", "consultas.jsonl")
    mapping, unmatched = run(a.run, sorted(set(common.read_json(a.ids).values())), f)
    print(f"{len(mapping)} partidos emparejados, {len(unmatched)} sin emparejar, {f.calls} consultas")
    for mid, u in unmatched.items():
        print(" -", u["partido"], "·", u["motivo"])
    return 0


if __name__ == "__main__":
    sys.exit(main())
