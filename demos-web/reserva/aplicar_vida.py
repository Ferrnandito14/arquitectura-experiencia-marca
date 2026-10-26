#!/usr/bin/env python3
"""Agrega las animaciones (vida.js) a cada demo y a su copia para publicar, con el carácter de cada marca.

Uso: python reserva/aplicar_vida.py. Idempotente (marcadores <!-- vida:inicio --> / <!-- vida:fin -->).
"""
import json, pathlib, re

AQUI = pathlib.Path(__file__).resolve().parent
DEMOS = AQUI.parent
JS = (AQUI / 'vida.js').read_text(encoding='utf-8')
INI, FIN = '<!-- vida:inicio -->', '<!-- vida:fin -->'

# firme: barberías (movimiento corto y decidido). suave: clínica y restaurante elegante. calido: panadería.
CARACTER = {
    'barberia-hermanos-mora': 'firme',
    'tonsor-barber-club': 'firme',
    'bravos-barber-caracas': 'firme',
    'odontologia-gran-caracas': 'suave',
    'la-flor-de-altamira': 'calido',
    'restaurant-el-barquero': 'suave',
    'cakevanas': 'calido',
    'voila-beauty-room': 'suave',
}


def aplicar(ruta, caracter):
    t = ruta.read_text(encoding='utf-8')
    t = re.sub(r'\n?' + re.escape(INI) + r'.*?' + re.escape(FIN), '', t, flags=re.S)
    bloque = f'{INI}\n<script>window.VIDA = {json.dumps({"caracter": caracter})};</script>\n<script>\n{JS}</script>\n{FIN}\n'
    t = t.replace('</body>', bloque + '</body>', 1)
    with open(ruta, 'w', encoding='utf-8', newline='') as f:
        f.write(t)


for slug, caracter in CARACTER.items():
    for ruta in (DEMOS / slug / 'index.html', DEMOS / 'publicar' / slug / 'index.html'):
        if ruta.exists():
            aplicar(ruta, caracter)
            print('ok', ruta.relative_to(DEMOS))
