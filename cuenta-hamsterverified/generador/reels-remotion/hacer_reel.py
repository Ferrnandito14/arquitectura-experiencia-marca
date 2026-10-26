#!/usr/bin/env python3
"""Reel de la serie "El hámster responde": guion JSON -> MP4 con voz, música y animación.

Uso: python hacer_reel.py guiones/mi-guion.json salida.mp4

Formato del guion (los campos con valor por defecto son opcionales):
  {"id": "d3-responde-postergar",
   "pregunta": "¿Cómo dejo de postergar?",
   "titular": "Empieza dos minutos.",
   "destacar": ["dos"],
   "consejo": "Casi siempre, seguir cuesta menos que empezar.",
   "puente": "Te lo explico en una línea.",
   "cierre": "Palabra de hámster.",
   "sello": null,
   "serie": "El hámster responde"}

La pregunta tiene que ser una duda frecuente y genérica (REGLAS.md): nunca se atribuye a una persona.
Necesita Node y Python con numpy. La voz por defecto es "Microsoft Pablo" (solo Windows).
Para usar Piper (Windows o Linux): HAMSTER_VOZ=piper:ruta/a/voz.onnx y, si piper-tts está en otra
Python, HAMSTER_PIPER_PYTHON=ruta/a/python.
"""
import hashlib, json, os, pathlib, shutil, subprocess, sys, wave
import numpy as np

AQUI = pathlib.Path(__file__).resolve().parent
SR = 44100
PAUSAS = [0.35, 0.3, 0.45, 0.45, 0.5, 0.9]  # antes de la primera frase, entre frases y al final
PREDETERMINADOS = {'serie': 'El hámster responde', 'puente': 'Te lo explico en una línea.', 'cierre': 'Palabra de hámster.', 'sello': None, 'destacar': []}


def npx(*args):
    return subprocess.run(['npx', 'remotion', *args], cwd=AQUI, check=True, shell=(sys.platform == 'win32'), capture_output=True, text=True)


def leer_wav(ruta):
    with wave.open(str(ruta)) as w:
        sr, ch = w.getframerate(), w.getnchannels()
        a = np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16).astype(np.float32) / 32768
    if ch > 1:
        a = a.reshape(-1, ch).mean(1)
    idx = np.where(np.abs(a) > 0.02)[0]
    a = a[max(0, idx[0] - int(0.03 * sr)):idx[-1] + int(0.08 * sr)]
    t = np.linspace(0, len(a) / sr, int(len(a) / sr * SR), endpoint=False)
    return np.interp(t, np.arange(len(a)) / sr, a)


def guardar_wav(ruta, x):
    y = (np.clip(x, -1, 1) * 32767).astype(np.int16)
    with wave.open(str(ruta), 'wb') as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes(y.tobytes())


def narrar(frases, carpeta):
    """Graba cada frase en carpeta/l0.wav, l1.wav, ... con la voz elegida en HAMSTER_VOZ."""
    voz = os.environ.get('HAMSTER_VOZ', 'pablo')
    if voz.startswith('piper:'):
        modelo = voz[len('piper:'):]
        python = os.environ.get('HAMSTER_PIPER_PYTHON', sys.executable)
        ritmo = os.environ.get('HAMSTER_PIPER_RITMO', '0.85')  # menos de 1 = más rápido, para acercarse a Pablo
        for i, frase in enumerate(frases):
            subprocess.run([python, '-m', 'piper', '-m', modelo, '-f', str(carpeta / f'l{i}.wav'), '--length-scale', ritmo, '--sentence-silence', '0'],
                           input=frase, text=True, encoding='utf-8', check=True, capture_output=True)
        return
    (carpeta / 'lineas.txt').write_text('\n'.join(frases) + '\n', encoding='utf-8')
    subprocess.run(['powershell', '-NoProfile', '-ExecutionPolicy', 'Bypass', '-File', str(AQUI / 'voz' / 'narrar.ps1'), '-Lineas', str(carpeta / 'lineas.txt'), '-Salida', str(carpeta)], check=True, capture_output=True)


def musica(duracion, semilla):
    """Música original: acordes suaves, bajo, bombo y shaker. La tonalidad cambia según el guion."""
    rng = np.random.default_rng(semilla)
    sube = 2 ** (int(rng.integers(0, 5)) / 12)  # transpone hasta 4 semitonos
    beat = 60 / 96; n = int(duracion * SR); t = np.arange(n) / SR; m = np.zeros(n)
    acordes = [[261.63, 329.63, 392.0], [220.0, 261.63, 329.63], [174.61, 220.0, 261.63], [196.0, 246.94, 293.66]]
    bajos = [130.81, 110.0, 87.31, 98.0]
    compas = 4 * beat
    for k in range(int(duracion / compas) + 1):
        s, e = int(k * compas * SR), min(n, int((k + 1) * compas * SR))
        if s >= n:
            break
        tt = np.arange(e - s) / SR; env = np.minimum(1, tt / 0.3) * np.minimum(1, (compas - tt) / 0.3)
        for f in acordes[k % 4]:
            m[s:e] += 0.09 * env * (np.sin(2 * np.pi * f * sube * tt) + 0.3 * np.sin(4 * np.pi * f * sube * tt))
        m[s:e] += 0.16 * env * np.sin(2 * np.pi * bajos[k % 4] * sube * tt)
    for k in range(int(duracion / (beat / 2))):
        s, L = int(k * beat / 2 * SR), int(0.05 * SR)
        if s + L >= n:
            break
        m[s:s + L] += 0.03 * (1.0 if k % 2 else 0.6) * rng.standard_normal(L) * np.exp(-np.arange(L) / (0.012 * SR))
    for k in range(int(duracion / beat)):
        s, L = int(k * beat * SR), int(0.18 * SR)
        if s + L >= n:
            break
        tt = np.arange(L) / SR; f = 55 + 60 * np.exp(-tt * 30)
        m[s:s + L] += 0.22 * np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-tt * 14)
    m *= np.minimum(1, np.minimum(t / 1.0, (duracion - t) / 1.5))
    return m / np.max(np.abs(m)) * 0.8


def main():
    guion_ruta, salida = pathlib.Path(sys.argv[1]).resolve(), pathlib.Path(sys.argv[2]).resolve()
    g = {**PREDETERMINADOS, **json.loads(guion_ruta.read_text(encoding='utf-8'))}
    for campo in ('pregunta', 'titular', 'consejo'):
        if not g.get(campo):
            sys.exit(f'Falta "{campo}" en el guion.')
    if not (AQUI / 'node_modules').exists():
        subprocess.run(['npm', 'install', '--no-audit', '--no-fund', '--ignore-scripts'], cwd=AQUI, check=True, shell=(sys.platform == 'win32'))

    trabajo = AQUI / 'trabajo'; publico = AQUI / 'public'
    shutil.rmtree(trabajo, ignore_errors=True); trabajo.mkdir(); publico.mkdir(exist_ok=True)

    # 1. Voz: una grabación por frase
    frases = [g['pregunta'], g['puente'], g['titular'], g['consejo'], g['cierre']]
    narrar(frases, trabajo)

    # 2. Unir frases con pausas y calcular cuándo empieza y termina cada una
    partes, tiempos, pos = [np.zeros(int(PAUSAS[0] * SR))], [], PAUSAS[0]
    for i in range(len(frases)):
        a = leer_wav(trabajo / f'l{i}.wav')
        tiempos.append({'inicio': round(pos, 2), 'fin': round(pos + len(a) / SR, 2)})
        partes += [a, np.zeros(int(PAUSAS[i + 1] * SR))]
        pos += len(a) / SR + PAUSAS[i + 1]
    voz = np.concatenate(partes); duracion = len(voz) / SR
    guardar_wav(trabajo / 'voz-original.wav', voz / np.max(np.abs(voz)) * 0.9)
    # Tono un poco más agudo para el hámster, sin cambiar la velocidad
    npx('ffmpeg', '-y', '-loglevel', 'error', '-i', str(trabajo / 'voz-original.wav'), '-af', 'asetrate=44100*1.12,aresample=44100,atempo=0.8929', str(publico / 'voz.wav'))

    # 3. Música original, distinta tonalidad según el guion
    semilla = int(hashlib.sha1(g.get('id', g['pregunta']).encode()).hexdigest()[:8], 16)
    guardar_wav(publico / 'musica.wav', musica(duracion, semilla))

    # 4. Render con Remotion
    props = {k: g[k] for k in ('serie', 'pregunta', 'puente', 'titular', 'destacar', 'consejo', 'cierre', 'sello')}
    props.update({'tiempos': {'duracion': round(duracion, 2), 'frases': tiempos}, 'voz': 'voz.wav', 'musica': 'musica.wav'})
    (trabajo / 'props.json').write_text(json.dumps(props, ensure_ascii=False), encoding='utf-8')
    salida.parent.mkdir(parents=True, exist_ok=True)
    npx('render', 'src/index.ts', 'HamsterResponde', str(trabajo / 'render.mp4'), f'--props={trabajo / "props.json"}', '--log=error')
    # moov al principio para que el video arranque rápido en la web
    npx('ffmpeg', '-y', '-loglevel', 'error', '-i', str(trabajo / 'render.mp4'), '-c', 'copy', '-movflags', '+faststart', str(salida))
    print(f'{g.get("id", "reel")}: {salida} ({duracion:.1f} s)')


if __name__ == '__main__':
    main()
