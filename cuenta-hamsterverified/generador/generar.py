#!/usr/bin/env python3
"""Genera diapositivas (PNG) y reels (MP4) de @hamster.2511058 a partir de un JSON.

Uso: python3 generar.py lote.json carpeta_salida
Formato del JSON: {"piezas": [{"id": "dia1-a", "tipo": "carrusel" | "reel", "diapositivas": [
  {"kicker": "...", "grande": "...", "pequeno": "...", "tamano": 110, "hamster": 300, "sello": ["FALSO", "#C0392B"], "pie": "desliza →",
  "pregunta": "texto de la serie El hámster responde", "conteo": "auto"}]}]}
Las diapositivas de un reel salen en 1080x1920 y se unen en un MP4 con fundidos.
"""
import html, json, os, pathlib, re, shutil, subprocess, sys
from PIL import Image
sys.path.insert(0, str(pathlib.Path(__file__).parent))
import audio_reel

def buscar_chrome():
    # HAMSTER_CHROME manda; luego los lugares habituales (nube, Windows, Linux).
    candidatos = [os.environ.get('HAMSTER_CHROME'),
        '/opt/pw-browsers/chromium-1194/chrome-linux/chrome',
        r'C:\Program Files\Google\Chrome\Application\chrome.exe',
        r'C:\Program Files (x86)\Google\Chrome\Application\chrome.exe',
        r'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe']
    for c in candidatos:
        if c and pathlib.Path(c).exists(): return c
    for nombre in ('google-chrome', 'chromium', 'chromium-browser', 'chrome'):
        if shutil.which(nombre): return shutil.which(nombre)
    sys.exit('No encuentro Chrome. Define HAMSTER_CHROME con la ruta del ejecutable.')

CHROME = buscar_chrome()
HAMSTER = '''<svg viewBox="0 0 400 400" xmlns="http://www.w3.org/2000/svg" width="{w}" height="{w}">
<ellipse cx="200" cy="360" rx="120" ry="14" fill="#3B2A20" opacity=".12"/>
<circle cx="112" cy="118" r="44" fill="#E3A862"/><circle cx="112" cy="118" r="26" fill="#F4B9B0"/>
<circle cx="288" cy="118" r="44" fill="#E3A862"/><circle cx="288" cy="118" r="26" fill="#F4B9B0"/>
<ellipse cx="200" cy="228" rx="150" ry="128" fill="#EDB873"/>
<ellipse cx="200" cy="268" rx="104" ry="84" fill="#FFF1D6"/>
<circle cx="140" cy="212" r="12" fill="#2B1D16"/><circle cx="260" cy="212" r="12" fill="#2B1D16"/>
<circle cx="144" cy="208" r="4" fill="#fff"/><circle cx="264" cy="208" r="4" fill="#fff"/>
<ellipse cx="102" cy="250" rx="26" ry="18" fill="#F4A9A0" opacity=".75"/>
<ellipse cx="298" cy="250" rx="26" ry="18" fill="#F4A9A0" opacity=".75"/>
<ellipse cx="200" cy="238" rx="13" ry="9" fill="#C2675F"/>
<path d="M200 247 v14 M178 266 q22 14 44 0" stroke="#2B1D16" stroke-width="5" fill="none" stroke-linecap="round"/>
<g transform="translate(292 296)"><circle r="40" fill="#1D9BF0"/><path d="M-18 2 l12 13 l25 -28" stroke="#fff" stroke-width="10" fill="none" stroke-linecap="round" stroke-linejoin="round"/></g>
</svg>'''
# Colores (contraste sobre el papel, WCAG): tinta 14.9, texto 8.3, kicker 5.0, pie 6.5.
# Zona segura de reels: Instagram tapa unos 250 px arriba y 380 px abajo (1080x1920).
CSS = '''@import url('https://fonts.googleapis.com/css2?family=Inter:wght@500;700;800;900&display=swap');
:root{--papel:#FFF4E0;--tinta:#2B1D16;--texto:#5A4437;--kicker:#A9500E;--pie:#6B5444}
*{box-sizing:border-box;margin:0}
body{width:1080px;height:%(h)spx;background:var(--papel);font-family:'Inter','Segoe UI',Arial,sans-serif;color:var(--tinta);position:relative;overflow:hidden}
.wrap{position:absolute;inset:%(top)spx 90px %(bottom)spx 90px;display:flex;flex-direction:column;justify-content:center}
.kicker{font-size:44px;font-weight:700;line-height:1.2;color:var(--kicker);margin-bottom:30px}
.big{font-size:%(size)spx;font-weight:800;line-height:1.06;letter-spacing:-.025em;text-wrap:balance}
.small{font-size:54px;font-weight:500;line-height:1.3;margin-top:44px;color:var(--texto);max-width:880px}
.foot{position:absolute;left:90px;right:90px;bottom:%(foot)spx;display:flex;justify-content:space-between;font-size:34px;font-weight:700;color:var(--pie)}
.stamp{display:inline-block;align-self:flex-start;border:10px solid %(stamp)s;color:%(stamp)s;font-size:96px;font-weight:900;letter-spacing:.06em;padding:6px 36px;transform:rotate(-6deg);border-radius:14px;margin-bottom:76px}
.ham{position:absolute;right:50px;bottom:%(ham_b)spx}
.qtag{font-size:34px;font-weight:700;color:var(--pie);margin-bottom:14px}
.q{align-self:flex-start;background:#fff;border:4px solid #E8D5B5;border-radius:40px 40px 40px 10px;padding:30px 42px;font-size:50px;font-weight:600;line-height:1.25;color:var(--texto);max-width:840px;margin-bottom:56px}
.count{align-self:flex-start;background:var(--tinta);color:var(--papel);border-radius:999px;padding:8px 32px;font-size:40px;font-weight:800;margin-bottom:36px}'''

def tamano_auto(texto, reel=False):
    n = len(re.sub(r'<[^>]+>', '', texto))
    for limite, px in ((22, 140), (36, 120), (55, 104), (80, 88)):
        if n <= limite: return round(px * (1.15 if reel else 1))
    return round(74 * (1.15 if reel else 1))

def diapositiva(ruta, d, alto):
    sello = d.get('sello')
    cuerpo = ''
    if sello: cuerpo += f'<div class="stamp">{html.escape(sello[0])}</div>'
    if d.get('pregunta'): cuerpo += f'<div class="qtag">Pregunta común</div><div class="q">{html.escape(d["pregunta"])}</div>'
    if d.get('conteo'):
        # "auto" cuenta las palabras reales del titular para que la etiqueta nunca mienta.
        n = len(re.sub(r'<[^>]+>', ' ', d['grande']).split())
        cuerpo += f'<div class="count">{n} palabras</div>' if d['conteo'] == 'auto' else f'<div class="count">{html.escape(d["conteo"])}</div>'
    if d.get('kicker'): cuerpo += f'<div class="kicker">{html.escape(d["kicker"])}</div>'
    cuerpo += f'<div class="big">{d["grande"]}</div>'
    if d.get('pequeno'): cuerpo += f'<div class="small">{d["pequeno"]}</div>'
    ham = f'<div class="ham">{HAMSTER.format(w=d["hamster"])}</div>' if d.get('hamster') else ''
    reel_ = alto == 1920
    css = CSS % dict(h=alto, size=d.get('tamano') or tamano_auto(d['grande'], reel_), stamp=(sello[1] if sello else '#000'),
                     top=250 if reel_ else 90, bottom=500 if reel_ else 170, foot=400 if reel_ else 60, ham_b=430 if reel_ else 110)
    pagina = f'<!doctype html><html><head><meta charset="utf-8"><style>{css}</style></head><body><div class="wrap">{cuerpo}</div>{ham}<div class="foot"><span>hamsterverified</span><span>{html.escape(d.get("pie", ""))}</span></div></body></html>'
    f = ruta.with_suffix('.html'); f.write_text(pagina, encoding='utf-8')
    subprocess.run([CHROME, '--headless', '--no-sandbox', '--disable-gpu', '--hide-scrollbars', '--virtual-time-budget=6000', f'--screenshot={ruta}', f'--window-size=1080,{alto + 150}', f'file://{f.resolve()}'], check=True, capture_output=True)
    Image.open(ruta).convert('RGB').crop((0, 0, 1080, alto)).save(ruta)
    f.unlink()

def reel(pngs, destino, seg=3.0, fundido=0.5):
    entradas, filtros, prev = [], [], '0:v'
    for i, p in enumerate(pngs):
        entradas += ['-loop', '1', '-t', str(seg), '-i', str(p)]
    for i in range(1, len(pngs)):
        sal = f'v{i}'
        filtros.append(f'[{prev}][{i}:v]xfade=transition=fade:duration={fundido}:offset={i * (seg - fundido):.2f}[{sal}]')
        prev = sal
    total = len(pngs) * seg - (len(pngs) - 1) * fundido
    cmd = ['ffmpeg', '-y', *entradas, '-f', 'lavfi', '-t', f'{total:.2f}', '-i', 'anullsrc=r=44100:cl=stereo']
    if filtros: cmd += ['-filter_complex', ';'.join(filtros), '-map', f'[{prev}]']
    else: cmd += ['-map', '0:v']
    cmd += ['-map', f'{len(pngs)}:a', '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-r', '30', '-c:a', 'aac', '-shortest', str(destino)]
    subprocess.run(cmd, check=True, capture_output=True)

def main():
    lote = json.loads(pathlib.Path(sys.argv[1]).read_text(encoding='utf-8'))
    salida = pathlib.Path(sys.argv[2]); salida.mkdir(parents=True, exist_ok=True)
    for pieza in lote['piezas']:
        es_reel = pieza['tipo'] == 'reel'
        pngs = []
        for n, d in enumerate(pieza['diapositivas'], 1):
            ruta = salida / f'{pieza["id"]}-{n}.png'
            diapositiva(ruta, d, 1920 if es_reel else 1350)
            pngs.append(ruta)
        if es_reel:
            if os.environ.get('HAMSTER_SIN_VOZ') != '1' and audio_reel.disponible():
                audio_reel.reel_con_audio(pngs, pieza['diapositivas'], pieza['id'], salida / f'{pieza["id"]}.mp4')
            else:
                reel(pngs, salida / f'{pieza["id"]}.mp4')
            for p in pngs: p.unlink()
        print(pieza['id'], 'ok')

if __name__ == '__main__':
    main()
