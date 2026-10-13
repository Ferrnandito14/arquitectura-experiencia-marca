#!/usr/bin/env python3
"""Vigila UN partido (apifootball match_id): imprime una línea cada N segundos con marcador, minuto, remates y córners, hora de Caracas. Termina al finalizar.
Uso: watch_match.py --run runs/2026-10-13 --match-id 853232 [--every 60]"""
import argparse
import datetime
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import adapters  # noqa: E402
import common  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", default="runs/2026-10-13")
    ap.add_argument("--match-id", required=True)
    ap.add_argument("--every", type=int, default=60)
    a = ap.parse_args()
    key = adapters.apif_key()
    client = common.Client(os.path.join(a.run, "cache"), os.path.join(a.run, "sources", "consultas.jsonl"), policy=common.Policy(), min_interval=2.0, ttl=20)
    tz = datetime.timezone(datetime.timedelta(hours=-4))
    while True:
        try:
            e = adapters.apif_call(client, key, action="get_events", match_id=a.match_id, timezone="UTC")[0]
            st = {}
            for s in e.get("statistics") or []:
                st.setdefault(s["type"], (s["home"], s["away"]))
            now = datetime.datetime.now(tz).strftime("%H:%M")
            sh = st.get("Shots Total", ("?", "?"))
            co = st.get("Corners", ("?", "?"))
            cards = len(e.get("cards") or [])
            print(f"PULSO {now} Caracas | {e['match_hometeam_name']} {e['match_hometeam_score']}-{e['match_awayteam_score']} {e['match_awayteam_name']} ({e.get('match_status') or 'no empezó'}) | remates {sh[0]}-{sh[1]} | córners {co[0]}-{co[1]} | tarjetas {cards}", flush=True)
            if adapters.apif_status(e.get("match_status")) == "finished":
                print("FIN DEL PARTIDO", flush=True)
                return 0
        except Exception as ex:  # noqa: BLE001
            print(f"aviso: fallo transitorio {type(ex).__name__}", flush=True)
        time.sleep(a.every)


if __name__ == "__main__":
    sys.exit(main())
