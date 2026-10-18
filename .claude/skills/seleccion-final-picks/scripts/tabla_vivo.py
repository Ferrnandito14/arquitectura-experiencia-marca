#!/usr/bin/env python3
"""Tabla compacta EN VIVO de los tickets abiertos (lee seguimiento/vivo_estado.json que escribe vivo.py; no consulta la API). Una línea por ticket con el estado de cada pata:
✅ acertada · ❌ fallada · 🟢 en juego cumpliendo · 🔴 en juego perdiendo · ⏳ pendiente (hora Caracas). Sale con código 3 cuando no queda ningún ticket abierto.
Uso:  tabla_vivo.py --run runs/2026-10-17"""
import argparse
import json
import os
import sys
from datetime import datetime, timedelta, timezone

CARACAS = timezone(timedelta(hours=-4))


def corto(p):
    a, b = (p.split(" – ") + [""])[:2]
    return f"{a.strip()[:6]}–{b.strip()[:6]}"


def icono(est, det):
    if est == "ACERTADA":
        return "✅"
    if est == "FALLADA":
        return "❌"
    if est in ("MEDIA_GANADA", "MEDIA_PERDIDA", "ANULADA"):
        return "➖"
    if est == "EN_JUEGO":
        d = det.lower()
        return "🔴" if ("perdiendo" in d or "falta" in d or "va perdida" in d or "ya superó" in d) else "🟢"
    return "⏳"


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", required=True)
    a = ap.parse_args(argv)
    sp = os.path.join(a.run, "seguimiento")
    spec = json.load(open(os.path.join(sp, "tickets_abiertos.json"), encoding="utf-8"))
    st = json.load(open(os.path.join(sp, "vivo_estado.json"), encoding="utf-8"))
    inv = {m["match_id"]: m for m in json.load(open(os.path.join(a.run, "inventory.json"), encoding="utf-8"))["matches"]}
    now = datetime.now(CARACAS).strftime("%H:%M")
    lines, cerrados, abiertos = [f"📊 {now} (Caracas)"], [], 0
    for t in spec["tickets"]:
        ts = (st["legs"].get("T|" + t["id"]) or ["ABIERTO"])[0]
        if ts != "ABIERTO":
            cerrados.append(f"{t['id']} {'perdido' if ts == 'PERDIDO' else ts.lower()}")
            continue
        abiertos += 1
        partes = []
        for l in t["patas"]:
            es, det = st["legs"].get(f"{t['id']}|{l['apif']}|{l['mercado']}", ["PENDIENTE", ""])
            ic = icono(es, det)
            sn = st["snap"].get(l["apif"]) or {}
            extra = ""
            if es == "EN_JUEGO" and sn:
                extra = f" {sn.get('h')}-{sn.get('a')} {str(sn.get('min') or '')}'"
            elif es == "PENDIENTE":
                h = (inv.get(l["mid"]) or {}).get("normalized_datetime_utc")
                if h:
                    extra = " " + (datetime.fromisoformat(h.replace("Z", "+00:00")).astimezone(CARACAS)).strftime("%H:%M")
            partes.append(f"{ic}{corto(l['partido'])}{extra}")
        lines.append(f"{t['id']} ({t['monto']}): " + " | ".join(partes))
    if cerrados:
        lines.append("cerrados: " + ", ".join(cerrados))
    print("\n".join(lines), flush=True)
    return 0 if abiertos else 3


if __name__ == "__main__":
    sys.exit(main())
