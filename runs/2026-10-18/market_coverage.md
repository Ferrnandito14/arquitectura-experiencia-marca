# Cobertura de mercados — tres controles

> INVESTIGACIÓN CERTIFICADA (solo exhaustividad de la investigación; no es una aprobación para apostar) · analítica: CON_LIMITACIONES · precios: SIN_PRECIOS_REALES · revisión de agentes: NO_EJECUTADA · preparación para apostar: NO APTA (0 filas aptas)

Partidos autorizados: 55 · entradas del catálogo (mercado × selección × línea × alcance, GENERALES, no por partido): 326 · canales: datos_deportivos, apifootball (agregador), football-data (fixtures, Bet365), thestatsapi (agregador) · combinaciones requeridas = partidos × entradas × canales = 71720 · filas (partido × entrada) = 17930

## A. Investigación — INVESTIGACION_COMPLETA

- sin incidencias

| Canal | Requeridas | Encontrado | Consultado, no encontrado | La fuente no lo ofrece | No verificable | Pendiente | Cobertura (informativa) |
|---|---|---|---|---|---|---|---|
| datos_deportivos | 17930 | 16825 | 1105 | 0 | 0 | 0 | 1.0 |
| apifootball (agregador) | 17930 | 1928 | 1042 | 14960 | 0 | 0 | 1.0 |
| football-data (fixtures, Bet365) | 17930 | 120 | 0 | 17810 | 0 | 0 | 1.0 |
| thestatsapi (agregador) | 17930 | 5189 | 10463 | 2278 | 0 | 0 | 1.0 |

## B. Analítica — CON_LIMITACIONES (modelo: validación parcial)

- sin_estimador_propio: 183 ['goles.total_entero.over.1', 'goles.total_entero.over.2', 'goles.total_entero.over.3', 'goles.total_entero.over.4']
- sin_extractor_de_estadistica: 35 ['goles.total_entero.over.1', 'goles.total_entero.over.2', 'goles.total_entero.over.3', 'goles.total_entero.over.4']
- datos_insuficientes: 1050 {'tiros': 1050}
- modelo_sin_validacion_suficiente: 7865 
- liga_con_registro_incompleto_de_tarjetas: 16 ['120', '152', '168', '175', '207', '244', '253', '279', '302', '307', '322', '333', '337', '344', '44', '99']
- liga_con_registro_incompleto_de_corners: 15 ['120', '152', '168', '175', '207', '244', '253', '279', '302', '322', '333', '337', '344', '44', '99']
- arbitro_no_designado: 7 ['m-7e3010d323c6', 'm-a0f48a732882', 'm-e73c8cb408c4']
- arbitro_designado_sin_partidos_en_la_muestra: 9 ['m-5ccd9c52e282', 'm-0624efc59c6b', 'm-dc0f4abd4c36']
- alineaciones_no_publicadas: 55 ['m-5ccd9c52e282', 'm-7d20d2d79be2', 'm-8d88d2ba62b0']

Datos: {'suficientes': 14379, 'parciales': 576, 'insuficientes': 1050, 'sin_datos': 0, 'sin_extractor': 1925} · Estimador: {'calculable': 7739, 'datos_insuficientes': 126, 'no_implementado': 10065}

## C. Precios — SIN_PRECIOS_REALES (límite individual 2.1)

- sin_precios_reales_verificados: 17930 

Por estado: {'real_verificada': 0, 'otra_fuente': 5415, 'no_verificable': 75, 'sin_precio': 12440, 'no_consultado': 0} · filas con precio que cumple los requisitos de precio: 0

## D. Preparación para apostar — NINGUNA_FILA_APTA (independiente de la certificación)

- filas aptas: 0 de 17930 · modelo: validación parcial
- requisitos incumplidos (filas): investigacion_resuelta: 0, precio_real_verificado: 17930, cuota_dentro_del_limite: 14945, datos_suficientes: 3551, estimador_propio_disponible: 10191, modelo_validado: 17930, revision_agentes_completa: 17930
- estado independiente de investigacion_certificada: con el modelo sin validar no hay filas aptas aunque la investigación esté certificada
