#!/usr/bin/env python3
"""Utilidades compartidas por inventory.py, level1.py, batches.py y coverage_report.py.

Principios (ver docs/FUENTES-CONFORMIDAD.md):
  * Identidad honesta: User-Agent = UA. Nunca se falsifica un navegador ni se evaden CAPTCHA/Cloudflare.
  * Política de fuentes: sólo se consulta un host con estado 'permitida' o 'condicional' en sources_policy.json.
    Un host excluido (condiciones de uso / robots.txt) o no revisado lanza PolicyError.
  * robots.txt se respeta (con comodines * y $, regla de mayor especificidad; empate -> Allow).
  * Límite de ritmo por proveedor, reintentos acotados, backoff exponencial, Retry-After, caché en disco,
    registro de consultas SIN cabeceras sensibles.
Sólo biblioteca estándar.
"""
import hashlib
import json
import os
import re
import tempfile
import threading
import time
import unicodedata
import urllib.error
import urllib.parse
import urllib.request
from datetime import date, datetime, time as dtime, timedelta, timezone
from zoneinfo import ZoneInfo

UA = "football-picks-system/0.1"
POLICY_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sources_policy.json")
DEFAULT_TZ = "America/Caracas"


class PolicyError(Exception):
    """El host está excluido, no revisado, o robots.txt desautoriza la ruta."""


class FetchError(Exception):
    def __init__(self, msg, kind="error", status=None):
        super().__init__(msg)
        self.kind = kind          # network | timeout | http | blocked
        self.status = status


# ----------------------------------------------------------------------------- ficheros
def write_json_atomic(path, obj):
    d = os.path.dirname(os.path.abspath(path))
    os.makedirs(d, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=d, prefix=".tmp-", suffix=".json")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(obj, f, ensure_ascii=False, indent=2, sort_keys=True)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp, path)
    except BaseException:
        if os.path.exists(tmp):
            os.unlink(tmp)
        raise


def read_json(path, default=None):
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return default


def append_jsonl(path, obj):
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(obj, ensure_ascii=False, sort_keys=True) + "\n")


# ----------------------------------------------------------------------------- nombres
_SUFFIX = re.compile(r"\b(fc|cf|sc|ac|afc|cd|ud|sd|fk|sk|bk|if|ik|ssc|rc|as|us|club|de|the)\b")


def norm_name(s):
    """Minúsculas, sin acentos ni puntuación ni sufijos genéricos. NO decide identidad por sí solo."""
    s = unicodedata.normalize("NFKD", s or "")
    s = "".join(c for c in s if not unicodedata.combining(c)).lower()
    s = re.sub(r"[^a-z0-9 ]+", " ", s)
    s = _SUFFIX.sub(" ", s)
    return re.sub(r"\s+", " ", s).strip()


# ----------------------------------------------------------------------------- zonas horarias
def window_for_local_date(day, tz=DEFAULT_TZ):
    """[inicio, fin) UTC del día de calendario `day` (YYYY-MM-DD o date) en la zona `tz`."""
    if isinstance(day, str):
        day = date.fromisoformat(day)
    z = ZoneInfo(tz)
    start = datetime.combine(day, dtime(0, 0), tzinfo=z).astimezone(timezone.utc)
    end = datetime.combine(day + timedelta(days=1), dtime(0, 0), tzinfo=z).astimezone(timezone.utc)
    return start, end


def source_dt_to_utc(naive_local, source_tz):
    """Convierte una hora local naive de la fuente a UTC con zoneinfo (respeta DST de esa fecha)."""
    return naive_local.replace(tzinfo=ZoneInfo(source_tz)).astimezone(timezone.utc)


def utc_to_local(dt_utc, tz=DEFAULT_TZ):
    return dt_utc.astimezone(ZoneInfo(tz))


def days_to_query(day, tz=DEFAULT_TZ, spread=1):
    """Días de calendario (de la fuente) a consultar para cubrir la ventana local: día-1, día, día+1."""
    if isinstance(day, str):
        day = date.fromisoformat(day)
    return [day + timedelta(days=k) for k in range(-spread, spread + 1)]


# ----------------------------------------------------------------------------- robots.txt
def parse_robots(text, agent=UA):
    """Devuelve la lista [(allow:bool, patron)] del grupo que aplica a `agent` (o '*')."""
    groups, cur, seen_rule = [], None, False
    for raw in (text or "").splitlines():
        line = raw.split("#", 1)[0].strip()
        if not line or ":" not in line:
            continue
        k, v = (x.strip() for x in line.split(":", 1))
        k = k.lower()
        if k == "user-agent":
            if cur is None or seen_rule:
                cur = {"agents": [], "rules": []}
                groups.append(cur)
                seen_rule = False
            cur["agents"].append(v.lower())
        elif k in ("allow", "disallow") and cur is not None:
            seen_rule = True
            if v == "":
                continue    # 'Disallow:' vacío = permitir todo
            cur["rules"].append((k == "allow", v))
    name = agent.lower().split("/")[0]
    specific = [g for g in groups if any(a != "*" and a in name for a in g["agents"])]
    star = [g for g in groups if "*" in g["agents"]]
    chosen = specific or star
    return [r for g in chosen for r in g["rules"]]


def _rx(pattern):
    anchored = pattern.endswith("$")
    p = pattern[:-1] if anchored else pattern
    out = "".join(".*" if c == "*" else re.escape(c) for c in p)
    return re.compile("^" + out + ("$" if anchored else ""))


def robots_allows(rules, path_and_query):
    best_len, allowed = -1, True
    for allow, pat in rules:
        if _rx(pat).match(path_and_query):
            n = len(pat.rstrip("$"))
            if n > best_len or (n == best_len and allow):
                best_len, allowed = n, allow
    return allowed


# ----------------------------------------------------------------------------- política de fuentes
class Policy:
    def __init__(self, path=POLICY_PATH, data=None):
        self.data = data if data is not None else (read_json(path) or {"providers": {}})

    def lookup(self, host):
        host = host.lower()
        for name, p in self.data.get("providers", {}).items():
            for h in p.get("hosts", []):
                if host == h or host.endswith("." + h):
                    return name, p
        return None, None

    def check(self, host):
        name, p = self.lookup(host)
        if p is None:
            raise PolicyError(f"{host}: fuente no revisada (denegada por defecto)")
        if p["status"] == "excluida":
            raise PolicyError(f"{host}: EXCLUIDA ({p.get('reason', 'sin motivo')})")
        return name, p


# ----------------------------------------------------------------------------- cliente HTTP
_SECRET_QS = re.compile(r"(?i)([?&;](?:apikey|api_key|api-key|key|token|access_token)=)[^&#\s\"']+")


def redact_url(s):
    """Oculta valores de claves/tokens en query strings: nada sensible llega a logs, caché ni artefactos."""
    return _SECRET_QS.sub(lambda m: m.group(1) + "***", s) if isinstance(s, str) else s


class Response:
    def __init__(self, url, status, text, from_cache, headers=None):
        url = redact_url(url)
        self.url, self.status, self.text, self.from_cache, self.headers = url, status, text, from_cache, headers or {}


def _default_opener(url, headers, timeout):
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.status, dict(r.headers), r.read()
    except urllib.error.HTTPError as e:
        return e.code, dict(e.headers or {}), e.read() if hasattr(e, "read") else b""


_CHALLENGE = re.compile(r"just a moment|attention required|cf-browser-verification|captcha", re.I)


class Client:
    def __init__(self, cache_dir, log_path=None, policy=None, opener=None, sleep=time.sleep, clock=time.monotonic,
                 min_interval=1.5, max_retries=3, backoff=1.0, timeout=20, ttl=6 * 3600, honor_robots=True):
        self.cache_dir, self.log_path = cache_dir, log_path
        self.policy = policy or Policy()
        self.opener, self.sleep, self.clock = opener or _default_opener, sleep, clock
        self.min_interval, self.max_retries, self.backoff, self.timeout, self.ttl = min_interval, max_retries, backoff, timeout, ttl
        self.honor_robots = honor_robots
        self._last = {}
        self._robots = {}
        self._downloads = {}
        self._lock = threading.Lock()
        os.makedirs(cache_dir, exist_ok=True)

    # -- registro (sin cabeceras ni cookies)
    def _log(self, **kw):
        kw = {k: redact_url(v) for k, v in kw.items()}
        kw["ts"] = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        if self.log_path:
            append_jsonl(self.log_path, kw)

    def _key(self, url):
        return os.path.join(self.cache_dir, hashlib.sha256(redact_url(url).encode()).hexdigest())

    def _cached(self, url):
        base = self._key(url)
        meta = read_json(base + ".meta.json")
        if not meta or not os.path.exists(base + ".body"):
            return None
        if time.time() - meta["fetched_epoch"] > self.ttl or meta["status"] >= 500:
            return None
        with open(base + ".body", encoding="utf-8", errors="replace") as f:
            return Response(url, meta["status"], f.read(), True)

    def _limits(self, host):
        _, p = self.policy.lookup(host)
        return (p or {}).get("limits", {})

    def _pace(self, host):
        interval = max(self.min_interval, float(self._limits(host).get("min_interval", 0)))
        with self._lock:
            wait = self._last.get(host, -1e9) + interval - self.clock()
            if wait > 0:
                self.sleep(wait)
            self._last[host] = self.clock()

    def _robots_rules(self, host, scheme):
        if host not in self._robots:
            url = f"{scheme}://{host}/robots.txt"
            try:
                self._pace(host)
                st, hd, body = self.opener(url, {"User-Agent": UA}, self.timeout)
                text = body.decode("utf-8", "replace")
            except Exception as e:      # red caída: no se asume permiso
                raise PolicyError(f"{host}: no se pudo leer robots.txt ({type(e).__name__})")
            if st >= 500 or _CHALLENGE.search(text[:2000] or ""):
                raise PolicyError(f"{host}: robots.txt inaccesible/protegido (HTTP {st}); no se consulta")
            self._robots[host] = parse_robots(text) if st < 400 else []
            self._log(url=url, status=st, kind="robots")
        return self._robots[host]

    def fetch(self, url, force=False):
        u = urllib.parse.urlsplit(url)
        host = u.hostname or ""
        provider, _ = self.policy.check(host)             # PolicyError si excluida/no revisada
        if self.honor_robots:
            rules = self._robots_rules(host, u.scheme)
            pq = (u.path or "/") + (("?" + u.query) if u.query else "")
            if not robots_allows(rules, pq):
                self._log(url=url, provider=provider, kind="robots_denied")
                raise PolicyError(f"{host}: robots.txt desautoriza {pq}")
        if not force:
            c = self._cached(url)
            if c:
                self._log(url=url, provider=provider, status=c.status, from_cache=True)
                return c
        cap = self._limits(host)
        cap = cap.get("max_files_per_run") or cap.get("max_pages_per_run")
        if cap and self._downloads.get(provider, 0) >= cap:
            raise PolicyError(f"{host}: tope de {cap} descargas por ejecución alcanzado (límite de la política)")
        self._downloads[provider] = self._downloads.get(provider, 0) + 1
        last_err = None
        for attempt in range(self.max_retries + 1):
            self._pace(host)
            try:
                st, hd, body = self.opener(url, {"User-Agent": UA, "Accept": "*/*"}, self.timeout)
            except (urllib.error.URLError, TimeoutError, OSError) as e:
                last_err = FetchError(f"{host}: {type(e).__name__}: {e}", "timeout" if "timed out" in str(e) else "network")
                self._log(url=url, provider=provider, error=str(last_err), attempt=attempt)
                self.sleep(self.backoff * (2 ** attempt))
                continue
            text = body.decode("utf-8", "replace")
            self._log(url=url, provider=provider, status=st, attempt=attempt, bytes=len(body))
            if st in (403, 401) and _CHALLENGE.search(text[:3000]):
                raise FetchError(f"{host}: protección anti-bot (HTTP {st}); no se evade", "blocked", st)
            if st in (429, 503) or st >= 500:
                ra = hd.get("Retry-After") or hd.get("retry-after")
                try:
                    delay = float(ra) if ra is not None else self.backoff * (2 ** attempt)
                except ValueError:
                    delay = self.backoff * (2 ** attempt)
                last_err = FetchError(f"{host}: HTTP {st}", "http", st)
                if attempt < self.max_retries:
                    self.sleep(delay)
                continue
            if st >= 400:
                raise FetchError(f"{host}: HTTP {st}", "http", st)
            base = self._key(url)
            with open(base + ".body", "w", encoding="utf-8") as f:
                f.write(text)
            write_json_atomic(base + ".meta.json", {"url": redact_url(url), "status": st, "fetched_epoch": time.time()})
            return Response(url, st, text, False, {})
        raise last_err or FetchError(f"{host}: sin respuesta", "network")


# ----------------------------------------------------------------------------- discrepancias
def add_discrepancy(rec, kind, detail, sources=None):
    rec.setdefault("discrepancies", []).append({"kind": kind, "detail": detail, "sources": sources or []})
    return rec
