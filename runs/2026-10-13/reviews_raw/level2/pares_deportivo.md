# Pares de dos patas del mismo partido: valoración deportiva (2026-10-13)

Alcance: solo ficheros locales del run (review_cards.json, tickets.json, inventory.json, reviews_raw/batch/*.json, y los informes level2 ya existentes). No se consultó ninguna fuente externa ni la API; por tanto no hay datos nuevos de alineaciones, bajas ni cuotas. Todas las cifras son de apifootball/APWin vía pipeline (una sola vía de datos, no independiente). Cuotas "promedio de mercado" de un agregador, no ejecutables. No se sabe la hora actual: Kyoto (10:00Z) y Birmingham (19:00Z) pueden estar ya jugados o en curso.

match_id: Birmingham-Preston m-adc7b810d3d6 (19:00Z); Bucaramanga-Águilas m-53aa260644d7 (23:30Z); Kyoto-Ratchaburi m-0c15b801051b (10:00Z).

## Registro de fuentes
| Fuente | Ficha | Dato buscado | Resultado | Estado |
|---|---|---|---|---|
| review_cards.json | 3 match_id | forma, k/n, cuotas medias | leído | Consultada y útil |
| tickets.json | targets[0].tickets[0] (Birmingham), targets[3].tickets[0] (Kyoto), top_picks, patas_vetadas | medición conjunta | leído; solo existe medición conjunta para A y E; B, C, D no están medidos como par | Consultada y útil (parcial para B/C/D) |
| inventory.json / matrix.csv | match_id | localizar partido; qué mercados tienen estadísticas | Bucaramanga: la DC figura "INSUFICIENTES" estadísticas en matrix.csv; no hay k/n de under 4.5 ni over 0.5 | Consultada con datos insuficientes |
| reviews_raw/batch/b06, b07 (cuant y dep) | corrections por match_id | correcciones previas | Kyoto: córners visitante 10/10 idénticos sospechosos y historial mixto; Birmingham: BTTS 15/20 vs 54% mercado; Bucaramanga: over 1.5 18/20 vs 70% mercado; sin correcciones deportivas relevantes | Consultada y útil |
| level2/deportivo.md, auditor.md, auditor_ronda2.md, cuantitativo.md, verificador.md | secciones de los 3 partidos | contexto: tabla, H2H, lesiones | Alineaciones [ND] en los tres; get_lineups de Kyoto vacío a las 04:00Z | Consultada y útil (de segunda mano) |

## Datos base (dato | fuente | n | estado)
- Birmingham forma DDDWDDLWDW (3V-6E-1D), GF/GA 1.4/1.2; Preston LLLLLWLLDL (1V-1E-8D), GF/GA 0.9/1.9; Championship, mezcla casa/fuera, n=10+10 | card | Confirmado en card, una sola vía.
- Birmingham #7, en casa 0V-4E-0D (7:7); Preston #24 (1-1-7, 8:16); Birmingham no ganó por 2+ en ninguno de 10; Preston perdió por 2+ en 3/10 (Wolves 1-3, Bristol 1-3, Everton 0-4 en Copa) y por 3+ en 1/10; H2H 6 duelos 2022-26 todos por 1 gol o menos | level2/deportivo.md | Una sola fuente (apifootball), H2H viejo en parte.
- Birmingham BTTS 8/10 y 7/10; over 3.5 3/10 y 4/10; over 2.5 6/10 y 7/10 | card.
- Mercado Birmingham: 1X2 1.589/4.081/5.228; DC 1X 1.145; under 4.5 1.144 (over 5.149); +2.5 Preston 1.125 (4 casas 1.11-1.18); implícitas sin margen: +2.5 0.812, U4.5 0.814 | card/tickets.
- Bucaramanga forma DDWDDWDWWW (5V-5E-0D contados en la cadena; la nota de b07 dep dice "6 victorias/4 empates": discrepancia, prevalece el recuento de la cadena de la card), GF/GA 1.9/1.0; Águilas DDDDLDLLWD (1V-5E-4D), GF/GA 1.2/1.5; Primera A Clausura, n=10+10, casa/fuera mezclados | card.
- Bucaramanga #4 en Clausura, 6-5-0 en 11, invicta; en casa 2-3-0 (9:5); últimos 5 en casa 1-1, 1-1, 2-2, 2-0, 3-1; Águilas #11, fuera 1-2-3 (6:10); H2H: Águilas ganó el último (2-1, abr-2026); 4 H2H con Buc local: 2V-1E-1D | level2/deportivo.md y auditor.md. Liga con ~34% de empates en Clausura (n=126).
- Mercado Bucaramanga: 1X2 1.979/3.202/3.756; 1X 1.234 (8 casas 1.16-1.27), 1X implícita sin margen ~0.754 (el 0.379 del pipeline es un bug ya señalado); under 4.5 1.067 (over 7.217; sin margen ~0.87 la under, bruta 0.94); over 1.5 1.33. No hay cuota de over 0.5 en el pipeline (@1.05 es comunicada, no verificada). No hay k/n de goles 5+ ni de 0-0 en la card.
- Kyoto: forma WWDLLLWWLL, GF/GA 0.9/1.1 (9 goles en 10, 0 goles en 4; incluye 4 partidos de Copa); Ratchaburi WLWWLWLDDW, GF/GA 2.3/1.3, historial Thai League + ASEAN + ACL (informes previos hablan de 2 amistosos 6-2 y 5-0 y goleadas 6-1/6-0 locales, y un 4-6 en ACL ante Shanghai Port). Over 3.5 1/10 y 3/10; BTTS 4/10 y 6/10 | card + level2.
- Mercado Kyoto: 1X2 1.382/4.626/7.05; +1.5 Ratchaburi 1.68 (sin margen 0.559); under 3.5 1.43 (0.647 sin margen); Kyoto -1.5 paga ~2.12 | tickets/auditor_ronda2.
- Medición conjunta Kyoto (pipeline): apoyo conservador conjunto 0.496 (frec. +1.5 0.9/1.0, U3.5 0.9/0.7).

## (A) Birmingham-Preston: Preston +2.5 @1.125 + menos de 4.5 @1.14 (x1.282; cons. x1.218)
1. Correlación: ninguna implica la otra, pero los fallos se solapan y eso favorece al par. 4-1, 5-0, 5-2 (victoria local por 3+ con 5+ goles) pierden ambas. Solo +2.5: 3-0, 4-0, 3-1 (diferencia 3 con menos de 5 goles). Solo U4.5: 3-2, 2-3, 3-3, 1-4 (Preston gana, 5 goles), 2-4. Correlación positiva moderada en la cola de goleada local; no es contradictoria. La medición conjunta del pipeline (local 1.0, visitante 1.0, n=10; cons. 0.722) es solo "10/10 en ambas", no contiene información de la cola.
2. Escenarios que pierden UNA: 3-0 o 4-0 (pierde +2.5, gana U4.5); 3-2 o 2-3 (pierde U4.5, gana +2.5). Si Birmingham (favorito 1.59, 3-5-1, GF 1.4) saca su partido más holgado del año, cae la +2.5; si Preston (GA 1.9, BTTS 7/10) entra en un intercambio de goles, cae la U4.5.
3. Muestra: n=10+10 en la misma competición, pero sin separar casa/fuera (Birmingham en casa solo 4 partidos, 0 victorias), sin ajustar por rival y con Copa mezclada en Preston (Everton 0-4). 10/10 en +2.5 para Birmingham y 9/10 para Preston es compatible con regresión a la media; el mercado pone ~19% de fallo por pata.
4. Precio: probabilidades de mercado ~0.81 y ~0.81 por pata; el multiplicador x1.282 exige 0.78 conjunta y el conservador x1.218 exige 0.82, que supera a cada pata por separado. La conjunta real de mercado está entre 0.63 (Fréchet inferior) y 0.81; con solape positivo de fallos probablemente 0.70-0.76 (estimación mía, no dato). Es decir, EV descriptivo ligeramente negativo en el rango bajo. Falta: cuota real del par (los operadores suelen recortar el producto en combinaciones del mismo partido, y puede que no lo permitan), alineaciones y bajas (ninguna consultada), +2.5 en solo 4 casas con rango 1.11-1.18.
Veredicto A: ACEPTABLE CON SALVEDADES. Es el mejor de los pares mismo partido en lo deportivo (Preston 24º, no gana desde hace meses, H2H siempre ajustado, Birmingham sin ganar por 2+ en 10), pero no hay colchón sobre el precio y el solape es menor de lo que parece. Condición: cuota del par >=1.25 en casa, y mirar alineaciones.

## (B) Bucaramanga-Águilas: 1X @1.25 + menos de 4.5 @1.06 (x1.325; cons. x1.259)
1. Correlación: casi independientes. 1X falla con victoria visitante; U4.5 falla con 5+ goles. Solape pequeño (un 2-3 o 1-4 pierde ambas). La U4.5 casi no es "protectora" del 1X.
2. Escenarios: 0-1, 1-2 (pierde 1X, gana U4.5); 3-2, 2-3 empate/victoria local con 5 goles (pierde U4.5, gana 1X); 3-3. Un 2-2 o 1-1 (muy frecuentes aquí: 5 empates en 11) los gana ambos.
3. Muestra: Primera A Clausura, n=10+10, 100% liga, pero casa/fuera mezclados. Para la U4.5 no hay k/n en el pipeline (solo over 3.5: 5/10 y 4/10, over 2.5: 5/10 y 4/10), por lo que la segunda pata no tiene respaldo estadístico verificado. Tarjetas aparte.
4. Precio: la 1X sola exige 0.80 frente a ~0.754 de mercado (EV negativo ya en la pata sola); la U4.5 a 1.06 exige 0.943 bruto contra ~0.87 sin margen. La segunda pata sube el multiplicador un 6% a cambio de sumar un riesgo de unos 6-13 puntos (según se use la cuota bruta o sin margen): intercambio desfavorable. Falta: k/n de partidos con 5+ goles, cuota real del par, alineaciones, calendario del cuadrangular (rotación).
Veredicto B: ACEPTABLE CON SALVEDADES (flojo, al borde de DESACONSEJADO). La 1X es lo más sólido del lote (invicta en 11, 5/5 sin perder en casa, visitante con 1 victoria en 10), pero la U4.5 solo existe para llegar al rango x1.25 y empeora la relación riesgo-premio. Si se quiere esta base, mejor una pata más defendible.

## (C) Bucaramanga: 1X @1.25 + más de 0.5 goles @1.05 (x1.312)
1. Correlación: el único fallo de O0.5 es el 0-0, que es un empate y por tanto está dentro de la 1X. Los fallos son excluyentes y se suman; no se refuerzan. El par solo pierde si Águilas gana o hay 0-0.
2. Escenarios: 0-0 (gana 1X, pierde O0.5); 0-1 o 1-2 (pierde 1X, O0.5 gana). Hay 5 empates en las últimas 10 de Bucaramanga y 5 del visitante: la fracción de 0-0 dentro de esos empates es el dato clave y no está en el pipeline (over 1.5 9/10 en ambos descarta como mucho 1 partido con 0-1/0-0 por equipo, es decir que los 0-0 son como máximo 1 por equipo en la muestra, no un número exacto).
3. Muestra: igual que B; el 0-0 es un evento raro (muestra n=10 no sirve para estimarlo). La O0.5 a 1.05 es cuota comunicada, no aparece en el pipeline; el over 1.5 de mercado 1.33 sugiere que 0-0 es un riesgo bajo pero no se puede derivar con exactitud de ahí.
4. Precio: la pata nueva paga un 5% por un riesgo de unos pocos puntos; cuando no hay dato de 0-0, el margen de seguridad no se puede comprobar. La 1X sigue siendo la que carga con casi todo el riesgo (~25% de fallo).
Veredicto C: ACEPTABLE CON SALVEDADES. Mejor que B (la segunda pata es más segura y no depende de una cola de goles), pero el multiplicador casi todo viene de la 1X, que ya es sub-fair. Falta: k/n de 0-0 en ambos equipos, cuota real de O0.5 y del par.

## (D) Birmingham-Preston: menos de 4.5 @1.14 + 1X @1.14 (x1.30)
1. Correlación: casi nula, leve positiva. La 1X (local o empate) y la U4.5 no se contradicen; la goleada visitante con 5+ goles es rarísima. No hay refuerzo real, y la medición conjunta del pipeline no existe para este par.
2. Escenarios: Preston gana 1-0, 2-1 (pierde 1X, gana U4.5); 3-2, 4-1 local (pierde U4.5, gana 1X); 2-3 pierde ambas.
3. Muestra: Birmingham no perdió en 4/4 en casa pero 0 victorias (0-4-0); forma DDDWDDLWDW con 1 derrota en 10. Preston 8 derrotas en 10 y GA 1.9, pero BTTS 7/10 (marca) y su desplazamiento reciente es el dato que falta separar. 1X ~0.82 por mercado (cuota 1.145 de card; sin margen 1/1.145 sería 0.87 bruto), U4.5 ~0.81.
4. Precio: x1.30 exige 0.77 conjunta; con p1X~0.82 y pU4.5~0.81 casi independientes, conjunta ~0.66-0.70, EV claramente negativo (peor que el par A, que tiene solape). Además, +2.5 Preston es un superconjunto de la 1X (gana con toda victoria, empate o derrota corta de Preston) y paga 1.125 frente a 1.14: la pata de resultado de D es estrictamente más arriesgada que la de A por casi el mismo precio.
Veredicto D: DESACONSEJADO frente a A (misma U4.5, pata de resultado más débil por el mismo precio).

## (E) Kyoto-Ratchaburi (Champions, historial mixto): Ratchaburi +1.5 @1.68 + menos de 3.5 @1.43 (x2.40)
1. Correlación: positiva pero parcial. Los partidos cerrados (0-0, 1-0, 1-1, 2-1) ganan ambas. Kyoto 2-0 o 3-0 solo pierde la +1.5; Ratchaburi 1-3 o 2-3 (o cualquier intercambio de 4+ goles) solo pierde la U3.5; Kyoto 4-1 o 4-0 pierde ambas. Ratchaburi es un equipo de goles (2.3 GF, 6-4 en ACL) y Kyoto no marca (9 en 10), así que el riesgo de U3.5 viene del visitante y el de +1.5 del local: se compensan poco.
2. Escenarios: 2-0 Kyoto (pierde +1.5); 1-3 o 2-3 (pierde U3.5, gana +1.5).
3. Muestra: historial propio mixto (Kyoto: 4 partidos de Copa; Ratchaburi: liga tailandesa, ASEAN, y según informes previos 2 amistosos y goleadas ante rivales débiles) con n=10+10; no es misma competición. Ya vetada la corrección de córners 10/10 como sospechosa. El pipeline marca +1.5 como única pata con EV descriptivo positivo, que el auditor señala como maldición del ganador (máximo de ~3000 patas), y el mercado paga -1.5 de Kyoto a 2.12 (~47% de 2+), por encima de lo que dice el historial. Alineaciones: ninguna (get_lineups vacío a las 04:00Z); Ratchaburi jugó 7 y 9 de octubre y viaja.
4. Precio: x2.40 exige 0.416 conjunta; independientes serían 0.559 x 0.647 = 0.36; con correlación positiva podría rozar 0.40-0.45, es decir cerca del precio justo, sin ventaja. Y ni por multiplicador ni por probabilidad (~40% de acierto) es una pieza de seguridad x1.2-1.28.
Veredicto E: DESACONSEJADO como pieza de seguridad (rango x2.4, ~60% de fallo); como apuesta de varianza media solo ACEPTABLE CON SALVEDADES, y antes hay que comprobar que el partido (10:00Z) no haya empezado.

## Resumen
| Par | Veredicto |
|---|---|
| A Birmingham +2.5 Preston + U4.5 | ACEPTABLE CON SALVEDADES |
| B Bucaramanga 1X + U4.5 | ACEPTABLE CON SALVEDADES (flojo) |
| C Bucaramanga 1X + O0.5 | ACEPTABLE CON SALVEDADES |
| D Birmingham U4.5 + 1X | DESACONSEJADO (A lo domina) |
| E Kyoto-Ratchaburi +1.5 + U3.5 | DESACONSEJADO para seguridad |

Ninguno es DEFENDIBLE: todos tienen EV descriptivo negativo o nulo contra el precio de mercado, y ninguno tiene alineaciones, bajas ni cuota real del par.

## Datos pendientes comunes
Alineaciones y bajas de los tres partidos; cuota real del par en la casa (y si el operador permite combinar ambas patas del mismo partido); separación casa/fuera; k/n de 5+ goles y de 0-0 para Bucaramanga; hora actual y estado de Kyoto y Birmingham.
