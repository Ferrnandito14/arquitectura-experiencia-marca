#!/usr/bin/env python3
"""Voz del hámster: Piper (voz neuronal es_MX-claude-high, Apache-2.0) con tono ajustado.

Uso: python3 hacer_voz.py "texto a decir" salida.wav
Requisitos: pip install piper-tts; ffmpeg en el PATH. El modelo (63 MB) se descarga solo la primera vez
a ~/.cache/hamsterverified-voz y no se sube al repo.
Ajuste elegido por la persona dueña el 2026-10-26: tono 1.14 y velocidad 1.02 (mezcla entre la voz natural y la de hámster).
"""
import os, pathlib, shutil, subprocess, sys, tempfile, urllib.request

TONO = float(os.environ.get('HAMSTER_TONO', '1.14'))
VELOCIDAD = float(os.environ.get('HAMSTER_VELOCIDAD', '1.02'))
BASE = 'https://huggingface.co/rhasspy/piper-voices/resolve/main/es/es_MX/claude/high/es_MX-claude-high'
CARPETA = pathlib.Path.home() / '.cache' / 'hamsterverified-voz'

def modelo():
    CARPETA.mkdir(parents=True, exist_ok=True)
    for ext in ('.onnx', '.onnx.json'):
        destino = CARPETA / f'es_MX-claude-high{ext}'
        if not destino.exists():
            print('Descargando', destino.name, '...', file=sys.stderr)
            urllib.request.urlretrieve(BASE + ext, destino)
    return CARPETA / 'es_MX-claude-high.onnx'

def tiene_filtro(nombre):
    salida = subprocess.run(['ffmpeg', '-hide_banner', '-filters'], capture_output=True, text=True).stdout
    return nombre in salida

def main():
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    texto, salida = sys.argv[1], pathlib.Path(sys.argv[2])
    if not shutil.which('ffmpeg'):
        sys.exit('Falta ffmpeg en el PATH.')
    with tempfile.TemporaryDirectory() as tmp:
        crudo = pathlib.Path(tmp) / 'crudo.wav'
        subprocess.run([sys.executable, '-m', 'piper', '-m', str(modelo()), '-f', str(crudo)], input=texto, text=True, check=True)
        if tiene_filtro('rubberband'):
            filtro = f'rubberband=pitch={TONO}:tempo={VELOCIDAD}'
        else:
            # Sin rubberband: cambia el tono y la velocidad a la vez (queda un poco más rápida).
            filtro = f'asetrate=22050*{TONO},aresample=22050,atempo={VELOCIDAD / TONO:.4f}' if TONO <= 1.0 else f'asetrate=22050*{TONO},aresample=22050'
        subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', str(crudo), '-af', filtro, str(salida)], check=True)
    print('Voz lista:', salida)

if __name__ == '__main__':
    main()
