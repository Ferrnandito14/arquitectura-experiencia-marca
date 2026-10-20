#!/usr/bin/env python3
"""Vigila los tickets del 18-oct: imprime el estado completo (evento) cuando algo cambia (marcador, estado de una pata, o una P que se mueve >=10 pp) y un recordatorio cada 20 min si no pasó nada.
Estado persistente en state.json (hora de la última emisión y firma). Termina (exit 0) cuando no queda ticket abierto."""
import json, os, re, subprocess, sys, time
from datetime import datetime, timezone
ROOT = "/home/user/football-picks-system"
ST = os.path.dirname(os.path.abspath(__file__)) + "/state.json"
KEY = "/tmp/claude-0/-home-user/d56b1dd2-9e37-5240-9a83-4b470c476a77/scratchpad/probe/key.txt"
START = datetime(2026, 10, 19, 16, 15, tzinfo=timezone.utc)
env = dict(os.environ, APIFOOTBALL_KEY_FILE=KEY, PYTHONDONTWRITEBYTECODE="1")

def run():
    r = subprocess.run(["python3", ".claude/skills/seleccion-final-picks/scripts/estado_tickets.py", "--run", "runs/2026-10-19", "--book", "dist/ligas-19-oct-v3.xlsx"], cwd=ROOT, env=env, capture_output=True, text=True)
    return r.returncode, r.stdout

def parse(out):
    sig, ps = {}, {}
    cur = None
    for ln in out.splitlines():
        m = re.match(r"TICKET (\w+) .*probabilidad del ticket: ([\d.]+) %", ln)
        if m:
            cur = m.group(1); ps["T" + cur] = float(m.group(2)); continue
        if ln.startswith("   ") and "|" in ln and cur:
            parts = [x.strip() for x in ln.split("|")]
            tag = re.sub(r" min \d+", "", parts[3]) if len(parts) > 3 else ""
            tag = re.sub(r"\(sin estad.*\)", "", tag)
            sig[cur + "/" + parts[0] + "/" + parts[1]] = tag
            mp = re.match(r"([\d.]+) %", parts[2])
            if mp: ps[cur + "/" + parts[0] + "/" + parts[1]] = float(mp.group(1))
        if ln.startswith("Cerrados:"):
            sig["cerrados"] = ln
    return sig, ps

def load():
    try: return json.load(open(ST))
    except Exception: return {}

while datetime.now(timezone.utc) < START:
    time.sleep(30)
while True:
    rc, out = run()
    if rc == 3:
        print("FIN: ya no queda ningún ticket abierto\n" + out, flush=True); break
    if out.strip():
        sig, ps = parse(out)
        s = load(); now = time.time()
        if not s:
            kind = "INICIO"
        elif sig != s["sig"]:
            kind = "EVENTO"
        elif any(abs(ps.get(k, 0) - v) >= 10 for k, v in s["ps"].items() if k.startswith("T") or True):
            kind = "EVENTO"
        elif now - s["t"] >= 20 * 60:
            kind = "RECORDATORIO"
        else:
            kind = None
        if kind:
            print(f"[{kind}]\n{out}", flush=True)
            json.dump({"sig": sig, "ps": ps, "t": now}, open(ST, "w"))
    time.sleep(120)
