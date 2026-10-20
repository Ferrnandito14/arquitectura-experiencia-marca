# Cobertura de mercados — tres controles

> INVESTIGACIÓN CERTIFICADA (solo exhaustividad de la investigación; no es una aprobación para apostar) · analítica: CON_LIMITACIONES · precios: SIN_PRECIOS_REALES · revisión de agentes: NO_EJECUTADA · preparación para apostar: NO APTA (0 filas aptas)

Partidos autorizados: 58 · entradas del catálogo (mercado × selección × línea × alcance, GENERALES, no por partido): 326 · canales: datos_deportivos, apifootball (agregador), football-data (fixtures, Bet365), thestatsapi (agregador) · combinaciones requeridas = partidos × entradas × canales = 75632 · filas (partido × entrada) = 18908

## A. Investigación — INVESTIGACION_COMPLETA

- sin incidencias

| Canal | Requeridas | Encontrado | Consultado, no encontrado | La fuente no lo ofrece | No verificable | Pendiente | Cobertura (informativa) |
|---|---|---|---|---|---|---|---|
| datos_deportivos | 18908 | 17650 | 1258 | 0 | 0 | 0 | 1.0 |
| apifootball (agregador) | 18908 | 2024 | 1108 | 15776 | 0 | 0 | 1.0 |
| football-data (fixtures, Bet365) | 18908 | 0 | 0 | 18908 | 0 | 0 | 1.0 |
| thestatsapi (agregador) | 18908 | 4937 | 9511 | 4460 | 0 | 0 | 1.0 |

## B. Analítica — CON_LIMITACIONES (modelo: validación parcial)

- sin_estimador_propio: 183 ['goles.total_entero.over.1', 'goles.total_entero.over.2', 'goles.total_entero.over.3', 'goles.total_entero.over.4']
- sin_extractor_de_estadistica: 35 ['goles.total_entero.over.1', 'goles.total_entero.over.2', 'goles.total_entero.over.3', 'goles.total_entero.over.4']
- datos_insuficientes: 1200 {'tiros': 1200}
- modelo_sin_validacion_suficiente: 8294 
- liga_con_registro_incompleto_de_tarjetas: 14 ['120', '141', '145', '153', '154', '194', '235', '278', '282', '3', '305', '385', '517', '75']
- liga_con_registro_incompleto_de_corners: 8 ['120', '194', '235', '305', '385', '517', '75', '7981']
- arbitro_no_designado: 41 ['m-c666dbddc7fb', 'm-3470aeccdfcb', 'm-e2ceef3f62ee']
- arbitro_designado_sin_partidos_en_la_muestra: 4 ['m-a1bc7dfcb124', 'm-bd8ed8d3e54a', 'm-a7963c41237a']
- alineaciones_no_publicadas: 58 ['m-c666dbddc7fb', 'm-3470aeccdfcb', 'm-e2ceef3f62ee']

Datos: {'suficientes': 14972, 'parciales': 706, 'insuficientes': 1200, 'sin_datos': 0, 'sin_extractor': 2030} · Estimador: {'calculable': 8038, 'datos_insuficientes': 256, 'no_implementado': 10614}

## C. Precios — SIN_PRECIOS_REALES (límite individual 2.1)

- sin_precios_reales_verificados: 18908 

Por estado: {'real_verificada': 0, 'otra_fuente': 5317, 'no_verificable': 68, 'sin_precio': 13523, 'no_consultado': 0} · filas con precio que cumple los requisitos de precio: 0

## D. Preparación para apostar — NINGUNA_FILA_APTA (independiente de la certificación)

- filas aptas: 0 de 18908 · modelo: validación parcial
- requisitos incumplidos (filas): investigacion_resuelta: 0, precio_real_verificado: 18908, cuota_dentro_del_limite: 16018, datos_suficientes: 3936, estimador_propio_disponible: 10870, modelo_validado: 18908, revision_agentes_completa: 18908
- estado independiente de investigacion_certificada: con el modelo sin validar no hay filas aptas aunque la investigación esté certificada
