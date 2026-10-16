#!/usr/bin/env python3
"""Congela una versión de un libro (xlsx) SIN sobrescribir: copia a `dist/versiones/<nombre>__<AAAAMMDD-HHMMSS>UTC.xlsx`, calcula su sha256 y añade una línea a `data/versiones_libros.jsonl`
con la hora (UTC y Caracas), el commit de git, el run y el hash de los informes de agentes del run en ese momento. Así se puede evaluar lo que se sabía cuando se decidió, aunque el libro
vivo (`dist/<nombre>.xlsx`) se regenere después con otros estados de agentes.
Uso:  congelar_version.py dist/ligas-15-oct-v2.xlsx --run runs/2026-10-15 [--nota "texto"] [--manifest data/versiones_libros.jsonl]
Una versión idéntica (mismo sha256) a la última congelada del mismo libro no se duplica."""
import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

CCS = ZoneInfo("America/Caracas")


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def _git(*args):
    try:
        return subprocess.run(["git", *args], capture_output=True, text=True, timeout=20).stdout.strip() or None
    except Exception:
        return None


def agent_hashes(run):
    """sha256 (prefijo) de los informes de agentes y del paquete del run: identifica los estados de agentes que alimentaron este libro."""
    out = {}
    d = os.path.join(run, "agentes") if run else None
    if d and os.path.isdir(d):
        for f in sorted(os.listdir(d)):
            if f.startswith("informe_") and f.endswith(".json") and ".part" not in f or f == "paquete.json":
                out[f] = sha256(os.path.join(d, f))[:16]
    return out


def read_manifest(path):
    rows = []
    if os.path.exists(path):
        with open(path, encoding="utf-8") as fh:
            for ln in fh:
                if ln.strip():
                    try:
                        rows.append(json.loads(ln))
                    except ValueError:
                        pass
    return rows


def freeze(book, run=None, nota=None, manifest="data/versiones_libros.jsonl", out_dir=None, now=None):
    """Devuelve (ruta de la versión congelada, True si es nueva). Nunca modifica ni borra versiones anteriores."""
    now = now or datetime.now(timezone.utc)
    book_hash = sha256(book)
    base = os.path.splitext(os.path.basename(book))[0]
    rows = [r for r in read_manifest(manifest) if r.get("libro") == base]
    if rows and rows[-1]["sha256"] == book_hash and os.path.exists(rows[-1]["archivo"]):
        return rows[-1]["archivo"], False
    out_dir = out_dir or os.path.join(os.path.dirname(book) or ".", "versiones")
    os.makedirs(out_dir, exist_ok=True)
    stamp = now.strftime("%Y%m%d-%H%M%S") + "UTC"
    dest = os.path.join(out_dir, f"{base}__{stamp}.xlsx")
    n = 1
    while os.path.exists(dest):                       # nunca se sobrescribe
        n += 1
        dest = os.path.join(out_dir, f"{base}__{stamp}-{n}.xlsx")
    shutil.copy2(book, dest)
    rec = {"libro": base, "archivo": dest, "sha256": book_hash, "creado_utc": now.strftime("%Y-%m-%dT%H:%M:%SZ"), "creado_caracas": now.astimezone(CCS).strftime("%Y-%m-%d %H:%M"),
           "run": run, "commit": _git("rev-parse", "--short", "HEAD"), "informes_agentes": agent_hashes(run), "nota": nota, "version": len(rows) + 1}
    os.makedirs(os.path.dirname(manifest) or ".", exist_ok=True)
    with open(manifest, "a", encoding="utf-8") as fh:
        fh.write(json.dumps(rec, ensure_ascii=False) + "\n")
    return dest, True


def lookup(book_path, manifest="data/versiones_libros.jsonl"):
    """Entrada del manifiesto cuyo hash coincide con el archivo dado (la versión que realmente se evalúa), o None."""
    h = sha256(book_path)
    for r in read_manifest(manifest):
        if r["sha256"] == h:
            return r
    return None


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("book")
    ap.add_argument("--run")
    ap.add_argument("--nota")
    ap.add_argument("--manifest", default="data/versiones_libros.jsonl")
    a = ap.parse_args(argv)
    dest, new = freeze(a.book, a.run, a.nota, a.manifest)
    print(("congelada: " if new else "sin cambios, ya congelada: ") + dest)
    return 0


if __name__ == "__main__":
    sys.exit(main())
