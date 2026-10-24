#!/usr/bin/env python3
"""Genera diapositivas (PNG) y reels (MP4) de @hamster.2511058 a partir de un JSON.

Uso: python3 generar.py lote.json carpeta_salida
Formato del JSON: {"piezas": [{"id": "dia1-a", "tipo": "carrusel" | "reel", "diapositivas": [
  {"kicker": "...", "grande": "...", "pequeno": "...", "tamano": 110, "hamster": 300, "sello": ["FALSO", "#C0392B"], "pie": "desliza →"}]}]}
Las diapositivas de un reel salen en 1080x1920 y se unen en un MP4 con fundidos.
"""
import html, json, pathlib, subprocess, sys
from PIL import Image

CHROME = '/opt/pw-browsers/chromium-1194/chrome-linux/chrome'
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
CSS = '''*{box-sizing:border-box;margin:0}
body{width:1080px;height:%(h)spx;background:#FFF4E0;font-family:'Inter',sans-serif;color:#3B2A20;position:relative;overflow:hidden}
.wrap{position:absolute;inset:90px 90px 170px 90px;display:flex;flex-direction:column;justify-content:center}
.kicker{font-size:34px;font-weight:700;letter-spacing:.14em;text-transform:uppercase;color:#C8671B;margin-bottom:36px}
.big{font-size:%(size)spx;font-weight:800;line-height:1.08;letter-spacing:-.02em}
.small{font-size:50px;font-weight:500;line-height:1.35;margin-top:44px;color:#5A4437}
.foot{position:absolute;left:90px;right:90px;bottom:%(foot)spx;display:flex;justify-content:space-between;font-size:30px;font-weight:600;color:#7A6455}
.stamp{display:inline-block;align-self:flex-start;border:10px solid %(stamp)s;color:%(stamp)s;font-size:96px;font-weight:900;letter-spacing:.06em;padding:6px 36px;transform:rotate(-6deg);border-radius:14px;margin-bottom:56px}
.ham{position:absolute;right:50px;bottom:%(ham_b)spx}'''

def diapositiva(ruta, d, alto):
    sello = d.get('sello')
    cuerpo = ''
    if sello: cuerpo += f'<div class="stamp">{html.escape(sello[0])}</div>'
    if d.get('kicker'): cuerpo += f'<div class="kicker">{html.escape(d["kicker"])}</div>'
    cuerpo += f'<div class="big">{d["grande"]}</div>'
    if d.get('pequeno'): cuerpo += f'<div class="small">{d["pequeno"]}</div>'
    ham = f'<div class="ham">{HAMSTER.format(w=d["hamster"])}</div>' if d.get('hamster') else ''
    css = CSS % dict(h=alto, size=d.get('tamano', 100), stamp=(sello[1] if sello else '#000'), foot=60 if alto == 1350 else 120, ham_b=110 if alto == 1350 else 200)
    pagina = f'<!doctype html><html><head><meta charset="utf-8"><style>{css}</style></head><body><div class="wrap">{cuerpo}</div>{ham}<div class="foot"><span>hamsterverified</span><span>{html.escape(d.get("pie", ""))}</span></div></body></html>'
    f = ruta.with_suffix('.html'); f.write_text(pagina, encoding='utf-8')
    subprocess.run([CHROME, '--headless', '--no-sandbox', '--disable-gpu', '--hide-scrollbars', f'--screenshot={ruta}', f'--window-size=1080,{alto + 150}', f'file://{f.resolve()}'], check=True, capture_output=True)
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
            reel(pngs, salida / f'{pieza["id"]}.mp4')
            for p in pngs: p.unlink()
        print(pieza['id'], 'ok')

if __name__ == '__main__':
    main()
