"""Agrega la reserva o pedido en línea (reserva.js) a cada demo y a su copia para publicar.

Uso: python aplicar.py   (desde demos-web/reserva). Es idempotente: si la página ya la tiene, la reemplaza.
"""
import json, pathlib, re

AQUI = pathlib.Path(__file__).resolve().parent
DEMOS = AQUI.parent
JS = (AQUI / 'reserva.js').read_text(encoding='utf-8')
EJEMPLO = 'Días y horas de ejemplo: el negocio define su agenda real.'
PRECIO = 'precio por confirmar'

NEGOCIOS = {
    'barberia-hermanos-mora': {
        'titulo': 'Reserva tu turno en línea', 'lead': 'Elige servicio, día y hora en un minuto, aunque el local esté cerrado.', 'boton': 'Reservar en línea',
        'config': {'palabra': 'reserva', 'textoConfirmar': 'Confirmar reserva', 'textoListo': 'Reserva lista',
                   'tema': {'fondo': '#FFFFFF', 'texto': '#24160F', 'suave': '#5E4A3C', 'acento': '#B3241E', 'sobreAcento': '#FFFFFF', 'borde': '#E3D6BE'},
                   'pasos': [{'id': 'servicio', 'tipo': 'opciones', 'titulo': '¿Qué servicio quieres?', 'corto': 'Servicio', 'columnas': 'dos', 'opciones': [{'txt': 'Corte con lavado', 'sub': PRECIO}, {'txt': 'Barba', 'sub': PRECIO}, {'txt': 'Corte y barba', 'sub': PRECIO}, {'txt': 'Masaje breve', 'sub': PRECIO}]},
                             {'id': 'dia', 'tipo': 'fecha', 'titulo': '¿Qué día?', 'corto': 'Día', 'dias': 6},
                             {'id': 'hora', 'tipo': 'hora', 'titulo': '¿A qué hora?', 'corto': 'Hora', 'desde': 9, 'hasta': 18, 'cada': 30, 'nota': EJEMPLO},
                             {'id': 'datos', 'tipo': 'datos', 'titulo': '¿A nombre de quién?', 'corto': 'Nombre'}]}},
    'tonsor-barber-club': {
        'titulo': 'Reserva en el club', 'lead': 'Elige servicio, día y hora. Te esperamos con un café.', 'boton': 'Reservar en línea',
        'config': {'palabra': 'reserva', 'textoConfirmar': 'Confirmar reserva', 'textoListo': 'Reserva lista',
                   'tema': {'fondo': '#FFFFFF', 'texto': '#16203A', 'suave': '#4B5568', 'acento': '#1C3FA0', 'sobreAcento': '#FFFFFF', 'borde': '#DAD5CA', 'radio': '8px'},
                   'pasos': [{'id': 'servicio', 'tipo': 'opciones', 'titulo': '¿Qué servicio quieres?', 'corto': 'Servicio', 'columnas': 'dos', 'opciones': [{'txt': 'Corte de cabello', 'sub': PRECIO}, {'txt': 'Barba', 'sub': PRECIO}, {'txt': 'Mascarilla facial', 'sub': PRECIO}, {'txt': 'Corte y barba', 'sub': PRECIO}]},
                             {'id': 'dia', 'tipo': 'fecha', 'titulo': '¿Qué día?', 'corto': 'Día', 'dias': 6},
                             {'id': 'hora', 'tipo': 'hora', 'titulo': '¿A qué hora?', 'corto': 'Hora', 'desde': 9, 'hasta': 19, 'cada': 30, 'nota': EJEMPLO},
                             {'id': 'datos', 'tipo': 'datos', 'titulo': '¿A nombre de quién?', 'corto': 'Nombre'}]}},
    'bravos-barber-caracas': {
        'titulo': 'Reserva en línea', 'lead': 'Servicio, día y hora. Sin esperas.', 'boton': 'Reservar en línea',
        'config': {'palabra': 'reserva', 'textoConfirmar': 'Confirmar reserva', 'textoListo': 'Reserva lista',
                   'tema': {'fondo': '#151515', 'texto': '#F4F6F7', 'suave': '#A9ADB2', 'acento': '#C9A24A', 'sobreAcento': '#0A0A0A', 'borde': '#333333', 'radio': '4px'},
                   'pasos': [{'id': 'servicio', 'tipo': 'opciones', 'titulo': '¿Qué servicio quieres?', 'corto': 'Servicio', 'columnas': 'dos', 'opciones': [{'txt': 'Corte', 'sub': PRECIO}, {'txt': 'Barba', 'sub': PRECIO}, {'txt': 'Corte y barba', 'sub': PRECIO}, {'txt': 'Corte para niños', 'sub': PRECIO}]},
                             {'id': 'dia', 'tipo': 'fecha', 'titulo': '¿Qué día?', 'corto': 'Día', 'dias': 6},
                             {'id': 'hora', 'tipo': 'hora', 'titulo': '¿A qué hora?', 'corto': 'Hora', 'desde': 9, 'hasta': 18, 'cada': 30, 'nota': EJEMPLO},
                             {'id': 'datos', 'tipo': 'datos', 'titulo': '¿A nombre de quién?', 'corto': 'Nombre'}]}},
    'odontologia-gran-caracas': {
        'titulo': 'Pide tu cita en línea', 'lead': 'Elige el motivo y el momento que te conviene. La clínica te confirma el horario exacto.', 'boton': 'Pedir cita en línea',
        'config': {'palabra': 'solicitud de cita', 'textoConfirmar': 'Enviar solicitud', 'textoListo': 'Solicitud de cita lista',
                   'tema': {'fondo': '#FFFFFF', 'texto': '#13213F', 'suave': '#4E5B74', 'acento': '#1F55B8', 'sobreAcento': '#FFFFFF', 'borde': '#DCE6F3', 'radio': '18px'},
                   'pasos': [{'id': 'motivo', 'tipo': 'opciones', 'titulo': '¿Cuál es el motivo?', 'corto': 'Motivo', 'columnas': 'dos', 'opciones': [{'txt': 'Consulta y diagnóstico'}, {'txt': 'Limpieza dental'}, {'txt': 'Restauraciones'}, {'txt': 'Endodoncia'}, {'txt': 'Ortodoncia'}, {'txt': 'Urgencia'}]},
                             {'id': 'primera', 'tipo': 'opciones', 'titulo': '¿Es tu primera visita?', 'corto': 'Primera visita', 'columnas': 'dos', 'opciones': [{'txt': 'Sí, es la primera'}, {'txt': 'Ya soy paciente'}]},
                             {'id': 'dia', 'tipo': 'fecha', 'titulo': '¿Qué día prefieres?', 'corto': 'Día', 'dias': 6, 'cerrados': [0]},
                             {'id': 'franja', 'tipo': 'opciones', 'titulo': '¿En qué momento del día?', 'corto': 'Momento', 'columnas': 'dos', 'opciones': [{'txt': 'Mañana'}, {'txt': 'Tarde', 'sub': 'hasta las 6 p. m.'}], 'nota': EJEMPLO},
                             {'id': 'datos', 'tipo': 'datos', 'titulo': '¿A nombre de quién?', 'corto': 'Nombre'}]}},
    'la-flor-de-altamira': {
        'titulo': 'Haz tu pedido para retirar', 'lead': 'Elige lo que quieres y a qué hora pasas. Lo tenemos listo.', 'boton': 'Pedir en línea',
        'config': {'palabra': 'pedido', 'textoConfirmar': 'Confirmar pedido', 'textoListo': 'Pedido listo',
                   'tema': {'fondo': '#FFFFFF', 'texto': '#1A2238', 'suave': '#525A6C', 'acento': '#1C48A0', 'sobreAcento': '#FFFFFF', 'borde': '#E3E8F2'},
                   'pasos': [{'id': 'productos', 'tipo': 'cantidades', 'titulo': '¿Qué vas a llevar?', 'corto': 'Pedido', 'opciones': [{'txt': 'Cachitos', 'sub': PRECIO}, {'txt': 'Pan de jamón', 'sub': PRECIO}, {'txt': 'Pizza', 'sub': PRECIO}, {'txt': 'Charcutería', 'sub': PRECIO}, {'txt': 'Jugos', 'sub': PRECIO}]},
                             {'id': 'dia', 'tipo': 'fecha', 'titulo': '¿Qué día lo retiras?', 'corto': 'Día', 'dias': 3},
                             {'id': 'hora', 'tipo': 'hora', 'titulo': '¿A qué hora pasas?', 'corto': 'Hora de retiro', 'desde': 8, 'hasta': 20, 'cada': 30, 'nota': EJEMPLO},
                             {'id': 'datos', 'tipo': 'datos', 'titulo': '¿A nombre de quién?', 'corto': 'Nombre'}]}},
    'restaurant-el-barquero': {
        'titulo': 'Reserva tu mesa en línea', 'lead': 'Cuántos son, qué día y a qué hora. Te esperamos con música.', 'boton': 'Reservar mesa en línea',
        'config': {'palabra': 'reserva', 'textoConfirmar': 'Confirmar reserva', 'textoListo': 'Reserva lista',
                   'tema': {'fondo': '#FFFFFF', 'texto': '#1B1A17', 'suave': '#5A5145', 'acento': '#13294B', 'sobreAcento': '#FFFFFF', 'borde': '#CDBB98', 'radio': '10px'},
                   'pasos': [{'id': 'personas', 'tipo': 'opciones', 'titulo': '¿Cuántas personas?', 'corto': 'Personas', 'columnas': 'tres', 'opciones': [{'txt': str(n)} for n in range(1, 9)] + [{'txt': '9 o más'}]},
                             {'id': 'dia', 'tipo': 'fecha', 'titulo': '¿Qué día?', 'corto': 'Día', 'dias': 6},
                             {'id': 'hora', 'tipo': 'hora', 'titulo': '¿A qué hora?', 'corto': 'Hora', 'desde': 12, 'hasta': 23, 'cada': 30, 'nota': EJEMPLO},
                             {'id': 'ocasion', 'tipo': 'opciones', 'titulo': '¿Alguna ocasión especial?', 'corto': 'Ocasión', 'columnas': 'dos', 'opcional': True, 'opciones': [{'txt': 'Sin ocasión especial'}, {'txt': 'Cumpleaños'}, {'txt': 'Reunión de trabajo'}, {'txt': 'Celebración familiar'}]},
                             {'id': 'datos', 'tipo': 'datos', 'titulo': '¿A nombre de quién?', 'corto': 'Nombre'}]}},
}

INICIO, FIN = '<!-- reserva-web:inicio -->', '<!-- reserva-web:fin -->'


def aplicar(ruta, n):
    s = ruta.read_text(encoding='utf-8')
    s = re.sub(re.escape(INICIO) + '.*?' + re.escape(FIN) + r'\n?', '', s, flags=re.S)
    s = re.sub(r'<a class="[^"]*" href="#reserva-web" data-reserva>[^<]*</a>\s*', '', s)
    cfg = dict(n['config'], demo=True)
    bloque = (f'{INICIO}\n<section aria-labelledby="reserva-t" style="padding:64px 0"><div class="wrap">'
              f'<h2 id="reserva-t">{n["titulo"]}</h2><p class="lead">{n["lead"]}</p><div id="reserva-web"></div></div></section>\n'
              f'<script>window.RESERVA = {json.dumps(cfg, ensure_ascii=False)};</script>\n<script>{JS}</script>\n{FIN}\n')
    m = re.search(r'aria-labelledby="(donde|visit)"', s)
    i = s.rfind('<section', 0, m.start())
    s = s[:i] + bloque + s[i:]
    # Botón principal en la portada, antes del botón de WhatsApp
    m = re.search(r'<a class="([^"]*)" id="(reservar|pedido|cita)"', s)
    s = s[:m.start()] + f'<a class="{m.group(1)}" href="#reserva-web" data-reserva>{n["boton"]}</a>\n        ' + s[m.start():]
    # El botón pequeño del menú también lleva a la reserva en línea
    s = re.sub(r'(<a class="[^"]*mini[^"]*" href=")#(reservar|pedido|cita)(")', r'\1#reserva-web\3', s)
    with open(ruta, 'w', encoding='utf-8', newline='') as fh:
        fh.write(s)


for nombre, n in NEGOCIOS.items():
    for ruta in (DEMOS / nombre / 'index.html', DEMOS / 'publicar' / nombre / 'index.html'):
        aplicar(ruta, n)
        print('ok', ruta.relative_to(DEMOS))
