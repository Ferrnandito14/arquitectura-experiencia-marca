#!/usr/bin/env python3
"""Seguimiento EN VIVO de tickets abiertos (pedido explícito de la persona usuaria, 15-oct): consulta cada `--every` s los partidos de `seguimiento/tickets_abiertos.json`,
detecta cambios (inicio, goles, tarjetas, córners, descanso, final) y el estado de cada pata/ticket, y emite una línea por evento (stdout) más un latido por ciclo.
Solo consulta partidos que empiezan en ≤ 15 min, están en juego o aún no se vieron terminados. Hora de Caracas. La clave nunca se imprime.
Uso:  vivo.py --run runs/2026-10-15 [--every 60] [--once]"""
import argparse
import datetime
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import adapters  # noqa: E402
import common  # noqa: E402
import seguimiento as sg  # noqa: E402

CARACAS = datetime.timezone(datetime.timedelta(hours=-4))


def hhmm(dt=None):
    return (dt or datetime.datetime.now(datetime.timezone.utc)).astimezone(CARACAS).strftime("%H:%M")


def snap(e):
    h, a = sg.score(e)
    pts = adapters._card_points(e) or (0, 0)
    cp = sg._corner_pair(e)
    return {"estado": sg.state(e), "min": e.get("match_status") or "", "h": h, "a": a, "tarj": list(pts), "corn": list(cp) if cp else None,
            "goles": [(g.get("time"), g.get("home_scorer") or g.get("away_scorer"), "L" if g.get("home_scorer") else "V") for g in (e.get("goalscorer") or [])]}


def diff(name, old, new, wants_corners):
    ev = []
    if old is None:
        if new["estado"] == "live":
            ev.append(f"▶ {name}: en juego ({new['min']}') {new['h']}-{new['a']}")
        return ev
    if old["estado"] != new["estado"]:
        ev.append({"live": f"▶ {name}: COMIENZA / en juego ({new['min']})", "finished": f"🏁 {name}: FINAL {new['h']}-{new['a']}"}.get(new["estado"], f"{name}: estado {new['estado']}"))
    z = lambda v: 0 if v is None else v            # sin marcador todavía = 0-0 (el inicio del partido no es un gol)
    if (z(old["h"]), z(old["a"])) != (z(new["h"]), z(new["a"])) and new["h"] is not None:
        last = new["goles"][-1] if new["goles"] else None
        extra = f" — {last[1]} ({last[0]}')" if last and last[1] else ""
        ev.append(f"⚽ {name}: GOL {z(old['h'])}-{z(old['a'])} → {new['h']}-{new['a']} (min {new['min']}){extra}" + (" [marcador bajó: gol anulado]" if (z(new["h"]) + z(new["a"])) < (z(old["h"]) + z(old["a"])) else ""))
    if sum(new["tarj"]) != sum(old["tarj"]):
        ev.append(f"🟨 {name}: tarjetas {sum(old['tarj'])} → {sum(new['tarj'])} pts (A=1,R=2) (min {new['min']})")
    if wants_corners and new["corn"] and new["corn"] != old.get("corn"):
        ev.append(f"⛳ {name}: córners {new['corn'][0]}-{new['corn'][1]} (total {sum(new['corn'])}) (min {new['min']})")
    om, nm = old["min"].lower(), new["min"].lower()
    if nm.startswith("half") and not om.startswith("half"):
        ev.append(f"⏸ {name}: DESCANSO {new['h']}-{new['a']}")
    return ev


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--run", required=True)
    ap.add_argument("--every", type=int, default=60)
    ap.add_argument("--once", action="store_true")
    a = ap.parse_args(argv)
    key = adapters.apif_key()
    if not key:
        print("error: sin clave de apifootball", file=sys.stderr)
        return 2
    spec = common.read_json(os.path.join(a.run, "seguimiento", "tickets_abiertos.json"))
    client = common.Client(os.path.join(a.run, "cache_vivo"), os.path.join(a.run, "sources", "consultas_vivo.jsonl"), policy=common.Policy(), min_interval=0.5, ttl=5)
    inv = {m["match_id"]: m for m in common.read_json(os.path.join(a.run, "inventory.json"))["matches"]}
    matches = {}
    for t in spec["tickets"]:
        for l in t["patas"]:
            matches.setdefault(l["apif"], {"partido": l["partido"].split(" (")[0], "corners": False, "inicio": (inv.get(l["mid"]) or {}).get("normalized_datetime_utc")})
            if l["mercado"] in ("corners", "corners_equipo") or (l["mercado"] == "combo" and any(s["tipo"].startswith("corners") for s in l["subs"])):
                matches[l["apif"]]["corners"] = True
    state_path = os.path.join(a.run, "seguimiento", "vivo_estado.json")
    prev = common.read_json(state_path, {"snap": {}, "legs": {}, "done": []}) or {"snap": {}, "legs": {}, "done": []}
    first = not prev["snap"]
    events = {}
    while True:
        evs, now = {}, datetime.datetime.now(datetime.timezone.utc)
        for aid, info in matches.items():
            if aid in prev["done"]:
                continue
            if info.get("inicio") and prev["snap"].get(aid) is None and now < datetime.datetime.fromisoformat(info["inicio"].replace("Z", "+00:00")) - datetime.timedelta(minutes=15):
                continue            # aún falta más de 15 min para el inicio: no se consulta (ahorra descargas)
            try:
                e = adapters.apif_call(client, key, action="get_events", match_id=aid, timezone="UTC")[0]
            except common.PolicyError as err:
                print(f"AVISO: tope de descargas del proceso ({err}); se reinicia el seguimiento", flush=True)
                return 3
            except Exception as err:        # error de red puntual: se reintenta en el siguiente ciclo
                print(f"aviso: {info['partido']}: {type(err).__name__}", flush=True)
                continue
            evs[aid] = e
            s = snap(e)
            for line in diff(info["partido"], prev["snap"].get(aid), s, info["corners"]):
                print(f"[{hhmm()}] {line}", flush=True)
            prev["snap"][aid] = s
            if s["estado"] == "finished":
                prev["done"].append(aid)
        # estado de patas y tickets
        beat = []
        for t in spec["tickets"]:
            legs = []
            for l in t["patas"]:
                e = evs.get(l["apif"])
                if e is None:
                    st, det = (l_prev := prev["legs"].get(f"{t['id']}|{l['apif']}|{l['mercado']}", ["PENDIENTE", "sin dato en este ciclo"]))
                else:
                    st, det = sg.eval_leg(l, e)
                key_ = f"{t['id']}|{l['apif']}|{l['mercado']}"
                old = prev["legs"].get(key_)
                if old and old[0] != st:
                    print(f"[{hhmm()}] 🎯 {t['id']} · {l['partido']}: {old[0]} → {st} — {det}", flush=True)
                prev["legs"][key_] = [st, det]
                legs.append({"estado": st, "detalle": det, "partido": l["partido"]})
            ts = sg.ticket_status(legs)
            tk = f"T|{t['id']}"
            if prev["legs"].get(tk) and prev["legs"][tk][0] != ts:
                print(f"[{hhmm()}] 🎫 TICKET {t['id']} ({t['nombre']}): {prev['legs'][tk][0]} → {ts}", flush=True)
            prev["legs"][tk] = [ts, ""]
            beat.append(f"{t['id']} {ts}: " + " | ".join(f"{x['partido'].split(' (')[0].split(' – ')[0][:11]} {x['estado'][:3]} {x['detalle'].split(': ', 1)[-1][:46]}" for x in legs))
        if first or not a.once:
            print(f"[{hhmm()}] ⏱ " + " ¦ ".join(beat), flush=True)
        first = False
        common.write_json_atomic(state_path, prev)
        if a.once or all(aid in prev["done"] for aid in matches):
            if not a.once:
                print(f"[{hhmm()}] ✅ todos los partidos terminaron; fin del seguimiento", flush=True)
            return 0
        time.sleep(a.every)


if __name__ == "__main__":
    sys.exit(main())
