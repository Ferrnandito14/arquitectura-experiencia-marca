"""Voz del hámster y música tranquila para los reels (nube y Linux).

- Voz: Piper (es_MX-claude-high) con tono 1.14, vía voz/hacer_voz.py.
- Música: pad suave generado con código (acordes lentos y notas sueltas tipo campana). Original, sin derechos de terceros.
Cada diapositiva dura lo que dura su locución (mínimo 3 s). La música va unos 20 dB por debajo de la voz.
"""
import hashlib, html, math, pathlib, re, shutil, subprocess, sys, tempfile, wave
import numpy as np

AQUI = pathlib.Path(__file__).parent
FUNDIDO = 0.5
RETRASO_VOZ = 0.35   # la voz empieza un poco después de que aparece la diapositiva
COLA = 0.8           # silencio tras la locución antes de pasar a la siguiente
MIN_DIAPO = 3.0
SR = 44100

def disponible():
    if shutil.which('ffmpeg') is None: return False
    try:
        import piper  # noqa: F401
    except ImportError:
        return False
    return True

def texto_voz(d):
    """Lo que dice el hámster en una diapositiva. 'voz' manda; si no, se arma con los textos."""
    if 'voz' in d: return d['voz']
    partes = []
    if d.get('sello'): partes.append(d['sello'][0].capitalize() + '.')
    if d.get('pregunta'): partes.append(d['pregunta'])
    elif d.get('kicker'): partes.append(d['kicker'] + '.')
    for campo in ('grande', 'pequeno'):
        if d.get(campo): partes.append(d[campo])
    t = ' '.join(partes)
    t = re.sub(r'<[^>]+>', '', html.unescape(t)).replace('“', '').replace('”', '').replace('"', '')
    return re.sub(r'\s+', ' ', t).strip()

def duracion(wav):
    with wave.open(str(wav)) as w:
        return w.getnframes() / w.getframerate()

def hacer_voz(texto, destino):
    subprocess.run([sys.executable, str(AQUI / 'voz' / 'hacer_voz.py'), texto, str(destino)], check=True, capture_output=True)

def musica(id_pieza, segundos, destino):
    """Pad tranquilo en una tonalidad que depende del id (para que no suenen todos igual)."""
    semilla = int(hashlib.sha1(id_pieza.encode()).hexdigest(), 16)
    rng = np.random.default_rng(semilla % (2 ** 32))
    raiz = [48, 50, 53, 55, 57][semilla % 5]            # C3, D3, F3, G3, A3 (MIDI)
    acordes = [[0, 4, 7, 11], [9, 12, 16, 19], [5, 9, 12, 16], [7, 11, 14, 17]]  # I7M, vi7, IV7M, V6 (en semitonos)
    hz = lambda m: 440.0 * 2 ** ((m - 69) / 12)
    n = int((segundos + 1.5) * SR)
    t = np.arange(n) / SR
    mezcla = np.zeros(n)
    dur_acorde = 6.0
    for k in range(int(math.ceil((segundos + 1.5) / dur_acorde)) + 1):
        ini = k * dur_acorde
        acorde = acordes[(k + semilla) % len(acordes)]
        for i, grado in enumerate(acorde):
            f = hz(raiz + grado + (12 if i >= 2 else 0))
            for det in (-0.6, 0.0, 0.7):
                fase = rng.uniform(0, 2 * math.pi)
                nota = np.sin(2 * math.pi * (f + det) * t + fase)
                env = np.clip((t - ini) / 2.0, 0, 1) * np.clip((ini + dur_acorde + 2.0 - t) / 2.0, 0, 1)
                mezcla += 0.07 * nota * env
    escala = [0, 2, 4, 7, 9]                              # pentatónica mayor
    for tt in np.arange(2.0, segundos, 3.2):
        f = hz(raiz + 24 + int(rng.choice(escala)))
        env = np.exp(-1.6 * np.clip(t - tt, 0, None)) * (t >= tt)
        mezcla += 0.05 * np.sin(2 * math.pi * f * t) * env
    mezcla *= 0.6 + 0.4 * (np.sin(2 * math.pi * t / 9.0) * 0.5 + 0.5)   # respiración lenta
    mezcla = np.convolve(mezcla, np.ones(8) / 8, mode='same')            # suaviza agudos
    mezcla /= max(1e-6, np.abs(mezcla).max()) / 0.8
    pcm = (np.stack([mezcla, np.roll(mezcla, 220)], axis=1) * 32767).astype('<i2')
    with wave.open(str(destino), 'wb') as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes(pcm.tobytes())

def reel_con_audio(pngs, diapos, id_pieza, destino):
    with tempfile.TemporaryDirectory() as tmp:
        tmp = pathlib.Path(tmp)
        voces, durs = [], []
        for i, d in enumerate(diapos):
            texto = texto_voz(d)
            if texto:
                w = tmp / f'voz{i}.wav'
                hacer_voz(texto, w)
                voces.append(w)
                durs.append(max(MIN_DIAPO, RETRASO_VOZ + duracion(w) + COLA))
            else:
                voces.append(None); durs.append(MIN_DIAPO)
        n = len(pngs)
        inicios = [sum(durs[:i]) - i * FUNDIDO for i in range(n)]
        total = sum(durs) - (n - 1) * FUNDIDO
        entradas, filtros, prev = [], [], '0:v'
        for p, dd in zip(pngs, durs):
            entradas += ['-loop', '1', '-t', f'{dd:.3f}', '-i', str(p)]
        for i in range(1, n):
            filtros.append(f'[{prev}][{i}:v]xfade=transition=fade:duration={FUNDIDO}:offset={inicios[i]:.3f}[v{i}]'); prev = f'v{i}'
        mus = tmp / 'musica.wav'; musica(id_pieza, total, mus)
        entradas += ['-i', str(mus)]
        idx_mus = n
        etiquetas = []
        for i, w in enumerate(voces):
            if w is None: continue
            entradas += ['-i', str(w)]
            k = n + 1 + len(etiquetas)
            ms = int((inicios[i] + (FUNDIDO if i else 0) + RETRASO_VOZ) * 1000)
            filtros.append(f'[{k}:a]adelay={ms}|{ms}[a{len(etiquetas)}]'); etiquetas.append(f'[a{len(etiquetas)}]')
        filtros.append(f'[{idx_mus}:a]volume=0.10,afade=t=in:d=1.5,afade=t=out:st={max(0, total - 2.0):.2f}:d=2.0[m]')
        filtros.append(f'{"".join(etiquetas)}[m]amix=inputs={len(etiquetas) + 1}:normalize=0:duration=longest,loudnorm=I=-16:TP=-1.5:LRA=11,atrim=0:{total:.2f}[aud]')
        cmd = ['ffmpeg', '-y', *entradas, '-filter_complex', ';'.join(filtros), '-map', f'[{prev}]' if n > 1 else '0:v', '-map', '[aud]',
               '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-r', '30', '-c:a', 'aac', '-b:a', '160k', '-ar', '44100', '-t', f'{total:.2f}', str(destino)]
        subprocess.run(cmd, check=True, capture_output=True)
