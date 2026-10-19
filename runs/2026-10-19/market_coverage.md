# Cobertura de mercados — tres controles

> INVESTIGACIÓN CERTIFICADA (solo exhaustividad de la investigación; no es una aprobación para apostar) · analítica: CON_LIMITACIONES · precios: SIN_PRECIOS_REALES · revisión de agentes: NO_EJECUTADA · preparación para apostar: NO APTA (0 filas aptas)

Partidos autorizados: 40 · entradas del catálogo (mercado × selección × línea × alcance, GENERALES, no por partido): 326 · canales: datos_deportivos, apifootball (agregador), football-data (fixtures, Bet365), thestatsapi (agregador) · combinaciones requeridas = partidos × entradas × canales = 52160 · filas (partido × entrada) = 13040

## A. Investigación — INVESTIGACION_COMPLETA

- sin incidencias

| Canal | Requeridas | Encontrado | Consultado, no encontrado | La fuente no lo ofrece | No verificable | Pendiente | Cobertura (informativa) |
|---|---|---|---|---|---|---|---|
| datos_deportivos | 13040 | 11962 | 1078 | 0 | 0 | 0 | 1.0 |
| apifootball (agregador) | 13040 | 1322 | 838 | 10880 | 0 | 0 | 1.0 |
| football-data (fixtures, Bet365) | 13040 | 35 | 0 | 13005 | 0 | 0 | 1.0 |
| thestatsapi (agregador) | 13040 | 3098 | 7136 | 2806 | 0 | 0 | 1.0 |

## B. Analítica — CON_LIMITACIONES (modelo: validación parcial)

- sin_estimador_propio: 183 ['goles.total_entero.over.1', 'goles.total_entero.over.2', 'goles.total_entero.over.3', 'goles.total_entero.over.4']
- sin_extractor_de_estadistica: 35 ['goles.total_entero.over.1', 'goles.total_entero.over.2', 'goles.total_entero.over.3', 'goles.total_entero.over.4']
- datos_insuficientes: 1038 {'corners': 138, 'tiros': 900}
- modelo_sin_validacion_suficiente: 5720 
- liga_con_registro_incompleto_de_tarjetas: 25 ['120', '135', '140', '141', '152', '164', '192', '195', '200', '202', '207', '259', '263', '266', '272', '278', '302', '307', '319', '322', '333', '344', '44', '75', '99']
- liga_con_registro_incompleto_de_corners: 20 ['120', '135', '140', '152', '192', '195', '202', '207', '259', '263', '266', '272', '302', '319', '322', '333', '344', '44', '75', '99']
- arbitro_no_designado: 17 ['m-af7a1528a242', 'm-d4b241f14ab9', 'm-fc4d4b26a6d3']
- arbitro_designado_sin_partidos_en_la_muestra: 1 ['m-00f954192010']
- alineaciones_no_publicadas: 40 ['m-af7a1528a242', 'm-d4b241f14ab9', 'm-fc4d4b26a6d3']

Datos: {'suficientes': 10110, 'parciales': 492, 'insuficientes': 1038, 'sin_datos': 0, 'sin_extractor': 1400} · Estimador: {'calculable': 5540, 'datos_insuficientes': 180, 'no_implementado': 7320}

## C. Precios — SIN_PRECIOS_REALES (límite individual 2.1)

- sin_precios_reales_verificados: 13040 

Por estado: {'real_verificada': 0, 'otra_fuente': 3313, 'no_verificable': 108, 'sin_precio': 9619, 'no_consultado': 0} · filas con precio que cumple los requisitos de precio: 0

## D. Preparación para apostar — NINGUNA_FILA_APTA (independiente de la certificación)

- filas aptas: 0 de 13040 · modelo: validación parcial
- requisitos incumplidos (filas): investigacion_resuelta: 0, precio_real_verificado: 13040, cuota_dentro_del_limite: 11233, datos_suficientes: 2930, estimador_propio_disponible: 7500, modelo_validado: 13040, revision_agentes_completa: 13040
- estado independiente de investigacion_certificada: con el modelo sin validar no hay filas aptas aunque la investigación esté certificada
