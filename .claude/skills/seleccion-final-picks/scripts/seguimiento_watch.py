#!/usr/bin/env python3
"""Vigilancia en vivo: repite seguimiento.run cada N s y emite UNA línea por cambio (marcador, estado de pata, estado de ticket).
Uso: seguimiento_watch.py --run runs/2026-10-13 [--every 60] [--minutes 28]. Termina solo al agotar el tiempo."""
import argparse
import re
import datetime
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import adapters  # noqa: E402
import common  # noqa: E402
import seguimiento as sg  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", default="runs/2026-10-13")
    ap.add_argument("--every", type=int, default=60)
    ap.add_argument("--minutes", type=int, default=720)
    a = ap.parse_args()
    key = adapters.apif_key()
    if not key:
        print("ERROR sin clave", flush=True)
        return 2
    client = common.Client(os.path.join(a.run, "cache"), os.path.join(a.run, "sources", "consultas.jsonl"), policy=common.Policy(), min_interval=2.0, ttl=20)

    def fetch(mid):
        d = adapters.apif_call(client, key, action="get_events", match_id=mid, timezone="UTC")
        return d[0] if isinstance(d, list) and d else None
    prev, end = {}, time.time() + a.minutes * 60
    while time.time() < end:
        try:
            res = sg.run(a.run, fetch)
            sg.write_all(a.run, res)
            for t in res:
                cur = {"T": t["estado"]}
                for l in t["patas"]:
                    cur[l["partido"] + "|" + l["mercado"]] = (l["estado"], re.sub(r" \((\d+\+?\d*|Half Time)\)", "", l["detalle"]))
                for k, v in cur.items():
                    if prev.get(t["id"], {}).get(k) != v and (prev or v not in ("PENDIENTE",) and v[0] not in ("PENDIENTE",) if k != "T" else True):
                        if k == "T":
                            if t["id"] in prev:
                                print(f"TICKET {t['id']} {t['nombre']}: {v}", flush=True)
                        else:
                            print(f"[{t['id']}] {k.split('|')[0]} ({k.split('|')[1]}) -> {v[0]}: {v[1]}", flush=True)
                prev[t["id"]] = cur
            live = {}
            for t in res:
                for l in t["patas"]:
                    m = re.match(r"^(\d+-\d+) \(([^)]+)\)", l["detalle"])
                    if m:
                        live[l["partido"].split(" – ")[0][:14]] = f"{m.group(1)} ({m.group(2)}')" if m.group(2).isdigit() else f"{m.group(1)} ({m.group(2)})"
            if live:
                print("PULSO " + datetime.datetime.utcnow().strftime("%H:%MZ") + " | " + " | ".join(f"{k} {v}" for k, v in live.items()), flush=True)
            if all(l["estado"] in ("ACERTADA", "FALLADA", "ANULADA") for t in res for l in t["patas"]):
                print("FIN: todas las patas decididas", flush=True)
                return 0
        except Exception as e:  # noqa: BLE001
            print(f"aviso: fallo transitorio {type(e).__name__}", flush=True)
        time.sleep(a.every)
    return 0


if __name__ == "__main__":
    sys.exit(main())
