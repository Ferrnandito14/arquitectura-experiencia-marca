# Cobertura de mercados — tres controles

> INVESTIGACIÓN CERTIFICADA (solo exhaustividad de la investigación; no es una aprobación para apostar) · analítica: CON_LIMITACIONES · precios: SIN_PRECIOS_REALES · revisión de agentes: NO_EJECUTADA · preparación para apostar: NO APTA (0 filas aptas)

Partidos autorizados: 58 · entradas del catálogo (mercado × selección × línea × alcance, GENERALES, no por partido): 326 · canales: datos_deportivos, apifootball (agregador), football-data (fixtures, Bet365), thestatsapi (agregador) · combinaciones requeridas = partidos × entradas × canales = 75632 · filas (partido × entrada) = 18908

## A. Investigación — INVESTIGACION_COMPLETA

- sin incidencias

| Canal | Requeridas | Encontrado | Consultado, no encontrado | La fuente no lo ofrece | No verificable | Pendiente | Cobertura (informativa) |
|---|---|---|---|---|---|---|---|
| datos_deportivos | 18908 | 14716 | 4192 | 0 | 0 | 0 | 1.0 |
| apifootball (agregador) | 18908 | 1790 | 1342 | 15776 | 0 | 0 | 1.0 |
| football-data (fixtures, Bet365) | 18908 | 0 | 0 | 18908 | 0 | 0 | 1.0 |
| thestatsapi (agregador) | 18908 | 4183 | 8158 | 6567 | 0 | 0 | 1.0 |

## B. Analítica — CON_LIMITACIONES (modelo: validación parcial)

- sin_estimador_propio: 1 ['otros.fueras_de_juego.total']
- sin_extractor_de_estadistica: 35 ['goles.total_entero.over.1', 'goles.total_entero.over.2', 'goles.total_entero.over.3', 'goles.total_entero.over.4']
- datos_insuficientes: 4961 {'resultado': 21, 'goles': 32, 'corners': 138, 'tarjetas': 420, 'tiros': 4350}
- modelo_sin_validacion_suficiente: 18850 
- liga_con_registro_incompleto_de_tarjetas: 13 ['120', '141', '194', '209', '212', '235', '277', '3', '330', '346', '475', '8092', '8105']
- liga_con_registro_incompleto_de_corners: 11 ['120', '194', '209', '212', '235', '277', '330', '346', '475', '8092', '8105']
- arbitro_no_designado: 47 ['m-18851448cf85', 'm-05e1b9d8b71c', 'm-000983169e80']
- arbitro_designado_sin_partidos_en_la_muestra: 1 ['m-5253ab17ca20']
- alineaciones_no_publicadas: 58 ['m-18851448cf85', 'm-05e1b9d8b71c', 'm-000983169e80']

Datos: {'suficientes': 10654, 'parciales': 1263, 'insuficientes': 4961, 'sin_datos': 0, 'sin_extractor': 2030} · Estimador: {'calculable': 12524, 'datos_insuficientes': 6326, 'no_implementado': 58}

## C. Precios — SIN_PRECIOS_REALES (límite individual 2.1)

- sin_precios_reales_verificados: 18908 

Por estado: {'real_verificada': 0, 'otra_fuente': 4523, 'no_verificable': 118, 'sin_precio': 14267, 'no_consultado': 0} · filas con precio que cumple los requisitos de precio: 0

## D. Preparación para apostar — NINGUNA_FILA_APTA (independiente de la certificación)

- filas aptas: 0 de 18908 · modelo: validación parcial
- requisitos incumplidos (filas): investigacion_resuelta: 0, precio_real_verificado: 18908, cuota_dentro_del_limite: 16440, datos_suficientes: 8254, estimador_propio_disponible: 6384, modelo_validado: 18908, revision_agentes_completa: 18908
- estado independiente de investigacion_certificada: con el modelo sin validar no hay filas aptas aunque la investigación esté certificada
