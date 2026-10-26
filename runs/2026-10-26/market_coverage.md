# Cobertura de mercados — tres controles

> INVESTIGACIÓN CERTIFICADA (solo exhaustividad de la investigación; no es una aprobación para apostar) · analítica: CON_LIMITACIONES · precios: SIN_PRECIOS_REALES · revisión de agentes: NO_EJECUTADA · preparación para apostar: NO APTA (0 filas aptas)

Partidos autorizados: 36 · entradas del catálogo (mercado × selección × línea × alcance, GENERALES, no por partido): 326 · canales: datos_deportivos, apifootball (agregador), football-data (fixtures, Bet365), thestatsapi (agregador) · combinaciones requeridas = partidos × entradas × canales = 46944 · filas (partido × entrada) = 11736

## A. Investigación — INVESTIGACION_COMPLETA

- sin incidencias

| Canal | Requeridas | Encontrado | Consultado, no encontrado | La fuente no lo ofrece | No verificable | Pendiente | Cobertura (informativa) |
|---|---|---|---|---|---|---|---|
| datos_deportivos | 11736 | 8400 | 3336 | 0 | 0 | 0 | 1.0 |
| apifootball (agregador) | 11736 | 884 | 1060 | 9792 | 0 | 0 | 1.0 |
| football-data (fixtures, Bet365) | 11736 | 0 | 0 | 11736 | 0 | 0 | 1.0 |
| thestatsapi (agregador) | 11736 | 2067 | 4856 | 4813 | 0 | 0 | 1.0 |

## B. Analítica — CON_LIMITACIONES (modelo: validación parcial)

- sin_estimador_propio: 1 ['otros.fueras_de_juego.total']
- sin_extractor_de_estadistica: 35 ['goles.total_entero.over.1', 'goles.total_entero.over.2', 'goles.total_entero.over.3', 'goles.total_entero.over.4']
- datos_insuficientes: 4498 {'tarjetas': 252, 'tiros': 4200, 'corners': 46}
- modelo_sin_validacion_suficiente: 11700 
- liga_con_registro_incompleto_de_tarjetas: 15 ['10', '111', '120', '130', '194', '208', '256', '277', '406', '41', '44', '69', '75', '8047', '99']
- liga_con_registro_incompleto_de_corners: 14 ['111', '120', '130', '194', '208', '256', '277', '406', '41', '44', '69', '75', '8047', '99']
- arbitro_no_designado: 26 ['m-730a6ac6b730', 'm-fd0946945ccf', 'm-1df54f8dc9a8']
- arbitro_designado_sin_partidos_en_la_muestra: 6 ['m-ecdc76cafa70', 'm-eedb1c0fbc1d', 'm-de725c56f218']
- alineaciones_no_publicadas: 36 ['m-730a6ac6b730', 'm-fd0946945ccf', 'm-1df54f8dc9a8']

Datos: {'suficientes': 5890, 'parciales': 88, 'insuficientes': 4498, 'sin_datos': 0, 'sin_extractor': 1260} · Estimador: {'calculable': 7114, 'datos_insuficientes': 4586, 'no_implementado': 36}

## C. Precios — SIN_PRECIOS_REALES (límite individual 2.1)

- sin_precios_reales_verificados: 11736 

Por estado: {'real_verificada': 0, 'otra_fuente': 2255, 'no_verificable': 106, 'sin_precio': 9375, 'no_consultado': 0} · filas con precio que cumple los requisitos de precio: 0

## D. Preparación para apostar — NINGUNA_FILA_APTA (independiente de la certificación)

- filas aptas: 0 de 11736 · modelo: validación parcial
- requisitos incumplidos (filas): investigacion_resuelta: 0, precio_real_verificado: 11736, cuota_dentro_del_limite: 10513, datos_suficientes: 5846, estimador_propio_disponible: 4622, modelo_validado: 11736, revision_agentes_completa: 11736
- estado independiente de investigacion_certificada: con el modelo sin validar no hay filas aptas aunque la investigación esté certificada
