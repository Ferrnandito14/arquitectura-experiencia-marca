#!/usr/bin/env python3
"""Revisión antes de publicar: vista previa del enlace, ícono y color de barra en las seis demos.

Idempotente (marcadores <!-- cabecera:inicio --> / <!-- cabecera:fin -->). Aplica a demos-web/<slug>/
y demos-web/publicar/<slug>/. Uso: python reserva/cabecera.py
"""
import html, pathlib, re, urllib.parse

RAIZ = pathlib.Path(__file__).resolve().parent.parent
INI, FIN = '<!-- cabecera:inicio -->', '<!-- cabecera:fin -->'

# slug: (iniciales del ícono, fondo, letra, descripción ahora que se reserva o pide en la web)
NEGOCIOS = {
    'barberia-hermanos-mora': ('HM', '#24160F', '#C29A55', 'Barbería clásica en Los Palos Grandes, Caracas. Corte, barba y buena música en un local impecable. Reserva tu hora en línea.'),
    'tonsor-barber-club': ('T', '#1C3FA0', '#FFFFFF', 'Barbería para caballeros con café y tienda de productos en Los Palos Grandes, Caracas. Reserva tu hora en línea.'),
    'bravos-barber-caracas': ('B', '#0A0A0A', '#C9A24A', 'Barber studio en Centro Plaza, Los Palos Grandes, Caracas. Dinos cómo quieres tu corte y reserva tu hora en línea.'),
    'odontologia-gran-caracas': ('OG', '#1F55B8', '#FFFFFF', 'Clínica odontológica en Centro Perú, Torre A, piso 7, Caracas. Solicita tu cita en línea.'),
    'la-flor-de-altamira': ('LF', '#1C48A0', '#D9A92B', 'Cachitos, tortas, pizzas, charcutería y jugos en Altamira, Caracas. Haz tu pedido en línea y pásalo a buscar.'),
    'restaurant-el-barquero': ('EB', '#13294B', '#E3B23C', 'Restaurant El Barquero, la embajada de los mares en Caracas. Cocina de mar, vinos, música y baile en Altamira. Reserva tu mesa en línea.'),
    'cakevanas': ('C', '#8E5BB3', '#FFFFFF', 'Tartas vascas cremosas y café de especialidad en Chacao, Caracas. Haz tu pedido en línea para retirar o con delivery.'),
    'voila-beauty-room': ('V', '#F8F3EC', '#A98550', 'Spa de belleza y estética en Los Palos Grandes, Caracas: cejas, pestañas, uñas, estilismo, faciales y corporales. Reserva tu cita en línea.'),
}


def icono(letras, fondo, letra):
    tam = 34 if len(letras) == 1 else 26
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64"><rect width="64" height="64" rx="14" fill="{fondo}"/>'
           f'<text x="32" y="{32 + tam * 0.36:.0f}" font-family="Georgia,serif" font-size="{tam}" font-weight="700" fill="{letra}" text-anchor="middle">{letras}</text></svg>')
    return 'data:image/svg+xml,' + urllib.parse.quote(svg)


def aplicar(ruta, letras, fondo, letra, desc):
    t = ruta.read_text(encoding='utf-8')
    t = re.sub(r'\n?' + re.escape(INI) + r'.*?' + re.escape(FIN), '', t, flags=re.S)
    titulo = html.unescape(re.search(r'<title>(.*?)</title>', t).group(1))
    t = re.sub(r'<meta name="description" content="[^"]*">', f'<meta name="description" content="{html.escape(desc)}">', t, count=1)
    bloque = '\n'.join([
        INI,
        f'<meta property="og:title" content="{html.escape(titulo)}">',
        f'<meta property="og:description" content="{html.escape(desc)}">',
        '<meta property="og:type" content="website">',
        '<meta property="og:locale" content="es_VE">',
        f'<meta name="theme-color" content="{fondo}">',
        f'<link rel="icon" href="{icono(letras, fondo, letra)}">',
        '<link rel="preconnect" href="https://fonts.googleapis.com">',
        '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>',
        FIN,
    ])
    t = re.sub(r'(<meta name="description" content="[^"]*">)', lambda m: m.group(1) + '\n' + bloque, t, count=1)
    with open(ruta, 'w', encoding='utf-8', newline='') as f:
        f.write(t)


for slug, datos in NEGOCIOS.items():
    for ruta in (RAIZ / slug / 'index.html', RAIZ / 'publicar' / slug / 'index.html'):
        if ruta.exists():
            aplicar(ruta, *datos)
            print('ok', ruta.relative_to(RAIZ))
