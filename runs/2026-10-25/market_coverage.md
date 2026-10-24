# Cobertura de mercados — tres controles

> INVESTIGACIÓN CERTIFICADA (solo exhaustividad de la investigación; no es una aprobación para apostar) · analítica: CON_LIMITACIONES · precios: SIN_PRECIOS_REALES · revisión de agentes: NO_EJECUTADA · preparación para apostar: NO APTA (0 filas aptas)

Partidos autorizados: 45 · entradas del catálogo (mercado × selección × línea × alcance, GENERALES, no por partido): 326 · canales: datos_deportivos, apifootball (agregador), football-data (fixtures, Bet365), thestatsapi (agregador) · combinaciones requeridas = partidos × entradas × canales = 58680 · filas (partido × entrada) = 14670

## A. Investigación — INVESTIGACION_COMPLETA

- sin incidencias

| Canal | Requeridas | Encontrado | Consultado, no encontrado | La fuente no lo ofrece | No verificable | Pendiente | Cobertura (informativa) |
|---|---|---|---|---|---|---|---|
| datos_deportivos | 14670 | 13599 | 1071 | 0 | 0 | 0 | 1.0 |
| apifootball (agregador) | 14670 | 1496 | 934 | 12240 | 0 | 0 | 1.0 |
| football-data (fixtures, Bet365) | 14670 | 135 | 0 | 14535 | 0 | 0 | 1.0 |
| thestatsapi (agregador) | 14670 | 4747 | 7594 | 2329 | 0 | 0 | 1.0 |

## B. Analítica — CON_LIMITACIONES (modelo: validación parcial)

- sin_estimador_propio: 1 ['otros.fueras_de_juego.total']
- sin_extractor_de_estadistica: 35 ['goles.total_entero.over.1', 'goles.total_entero.over.2', 'goles.total_entero.over.3', 'goles.total_entero.over.4']
- datos_insuficientes: 1299 {'resultado': 3, 'goles': 6, 'corners': 138, 'tarjetas': 252, 'tiros': 900}
- modelo_sin_validacion_suficiente: 14625 
- liga_con_registro_incompleto_de_tarjetas: 10 ['120', '152', '168', '207', '209', '244', '266', '302', '346', '44']
- liga_con_registro_incompleto_de_corners: 10 ['120', '152', '168', '207', '209', '244', '266', '302', '346', '44']
- arbitro_no_designado: 15 ['m-2d99cfa814b2', 'm-3eb015afdafe', 'm-ddca5a9a3837']
- alineaciones_no_publicadas: 45 ['m-2d99cfa814b2', 'm-3eb015afdafe', 'm-ddca5a9a3837']

Datos: {'suficientes': 11614, 'parciales': 182, 'insuficientes': 1299, 'sin_datos': 0, 'sin_extractor': 1575} · Estimador: {'calculable': 13110, 'datos_insuficientes': 1515, 'no_implementado': 45}

## C. Precios — SIN_PRECIOS_REALES (límite individual 2.1)

- sin_precios_reales_verificados: 14670 

Por estado: {'real_verificada': 0, 'otra_fuente': 4919, 'no_verificable': 14, 'sin_precio': 9737, 'no_consultado': 0} · filas con precio que cumple los requisitos de precio: 0

## D. Preparación para apostar — NINGUNA_FILA_APTA (independiente de la certificación)

- filas aptas: 0 de 14670 · modelo: validación parcial
- requisitos incumplidos (filas): investigacion_resuelta: 0, precio_real_verificado: 14670, cuota_dentro_del_limite: 11956, datos_suficientes: 3056, estimador_propio_disponible: 1560, modelo_validado: 14670, revision_agentes_completa: 14670
- estado independiente de investigacion_certificada: con el modelo sin validar no hay filas aptas aunque la investigación esté certificada
