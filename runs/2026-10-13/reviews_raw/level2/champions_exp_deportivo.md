# Experimento único Champions (13-oct-2026) - revisión deportiva

Análisis hecho a las ~15:25Z solo con archivos locales del run (sin fuentes externas, sin API). Ninguna alineación ni baja está disponible: todo lo de abajo es historial propio mixto (apifootball, últimos 10 por equipo) más cuotas promedio de agregador, que no son ejecutables.

## Registro de fuentes
| Fuente | Ficha | Dato buscado | Resultado | Estado |
|---|---|---|---|---|
| review_cards.json | m-837c7443671e (Inter), m-7fbfa4899ff4 (Leipzig), m-fa26ce1cb71b (Arsenal), m-53aa260644d7 (Bucaramanga) | forma, GF/GA, k/n | leído | Consultada y útil (origen apifootball, mezcla de competiciones) |
| matrix.json | form[local/visitante] y api_prices de los 4 ids | partido a partido, rival, sede, cuotas | leído; resultado.handicap sin estadísticas (NO_EVALUABLE), pero hay cuota en api_prices (-1.5: 1.709/2.152, 8 casas) | Consultada y útil, handicap solo precio |
| inventory.json | los 4 ids | ubicar partido, estado | los 4 PROGRAMADO, calendario con 2 fuentes | Consultada y útil |
| reviews_raw/batch b07, b11 (dep y cuant) | correcciones por id | avisos previos | historial mixto; cuant: Arsenal O3.5 mercado 40% vs 4/20 observado | Consultada y útil |
| vetoes.json | -- | vetos de estos partidos | solo +2.5 de Inter y Arsenal vetadas; ninguna de las patas del experimento | Consultada y útil |
| level2/deportivo.md, pares_deportivo.md, auditor_ronda2.md | -- | análisis previos | Arsenal-Lille señalado por auditor (amistosos en muestra); ver discrepancia abajo | Consultada y útil |
| Alineaciones/bajas (club, Transfermarkt, FotMob, prensa) | -- | once, bajas | no consultada: la instrucción prohíbe fuentes externas | No consultada |

Advertencia general: apoyo de tickets.md es Wilson inferior descriptivo, no probabilidad. Cuotas = promedio de agregador, no ejecutables, y la casa recalcula combinadas entre partidos... en este caso son partidos distintos, así que el producto es razonable.

## Pata 1. RB Leipzig - PSV, más de 2.5 goles @1.29 (19:00Z)
Hechos (matrix.json, n=10 por equipo, mezcla de competiciones):
- Totales de goles de Leipzig en sus 10: 5,3,5,6,3,4,5,5,2,6 -> 9/10 con 3+ (único fallo: 0-2 en Leverkusen el 20-sep). Local en Bundesliga: 2-1, 3-0, 5-0, 6-0 = 4/4.
- PSV: 4,4,3,6,7,4,2,5,5,2 -> 8/10; los 2 fallos son 1-1 con Shakhtar (única Champions) y 2-0 en Heerenveen. De visitante: 2-1, 6-1, 3-1, 2-3 = 4/4.
- Champions: Leipzig 1-4 en Como (5 goles); PSV 1-1 en casa con Shakhtar (2 goles). Cada uno tiene un solo partido de Champions.
- Mercado (agregador, 7 casas): Over 2.5 1.304/3.35 -> 72% sin margen; Over 3.5 a 1.82 (~52%). 1X2 Leipzig 1.75, X 4.47, PSV 3.93. El mercado espera un partido abierto.
A favor: frecuencias de ambos (9/10 y 8/10) por encima del 72% del mercado; Leipzig concede (1.8 por partido en la muestra: 4-1 Leverkusen, 4-1 Freiburg, 3-1 Bremen, 4-1 Como) y PSV marca; visitante PSV anota en todos sus partidos fuera. Línea baja con 3 goles marcando casi cualquier ritmo.
En contra:
- Muestra de rivales mixta: los 5-0 y 6-0 de Leipzig (Hamburgo, Frankfurt, Trier de Copa) y los 5-1, 6-1 de PSV son contra rivales de nivel inferior al de Champions; el batch deportivo b11 ya lo avisa. El partido de Champions de PSV fue cerrado.
- Escenarios de pérdida: 0-0, 1-0 / 0-1, 1-1, 2-0 / 0-2. La Champions, con más cautela táctica, tiende a esos marcadores; el único partido de Champions de PSV (1-1) es uno de ellos. En la muestra de Leipzig, el 0-2 en Leverkusen es el patrón de partido contra un rival fuerte.
- Cuota 1.29 deja poco margen: 77% bruto, 72% sin margen.
Invalida el pick: once de Leipzig con rotación fuerte o baja de su delantero/mediapunta principal; PSV sin sus atacantes titulares; datos pendientes: alineaciones (~18:00Z), bajas, viaje.
VEREDICTO: DEFENDIBLE (con reservas por el nivel de los rivales de la muestra).

## Pata 2. Inter - Club Brugge, hándicap visitante +1.5 (Brugge +1.5) @2.155 (19:00Z)
Hechos:
- Pierde si Inter gana por 2 o más. Márgenes de Inter en sus 10 (matrix.json): +2 (final Coppa Italia vs Lazio, sede marcada visitante/neutral), 0, 0, +3, +1, +1, -1 (Real Madrid), +2, 0, +3. Ganó por 2+ en 4/10 (Lazio, Monza, Udinese, Parma).
- En casa (n=5): Verona 1-1, Monza 4-1, Napoli 3-2, Udinese 5-3, Parma 3-0 -> ganó por 2+ en 3/5, por 3+ en 2/5, rival siempre de nivel inferior salvo Napoli (ganó por 1). Es el escenario de pérdida principal.
- Brugge: 0/10 con derrota de 2+ (derrotas: 1-2 con Union, 1-2 en Gent, 2-3 con Aston Villa en Champions). Pero 9 de 10 son Primera belga o Supercopa; solo un rival de calidad Champions (Villa, perdió por 1 en casa). GF 2.2, GA 0.9.
- Mercado (matrix.json api_prices, 8 casas): +1.5 a 2.152 / -1.5 a 1.709 -> Brugge +1.5 ~44% sin margen. 1X2: Inter 1.252, X 6.2, Brugge 11 (Inter 76% sin margen). Over 3.5 a 2.04 / under 1.79. Es decir, el mercado da ~56% a que Inter gane por 2+.
- El apoyo conservador (0.518 conjunto, mínimo por equipo 0.313) viene de una muestra con rivales muy desiguales.
A favor: Brugge nunca perdió por 2+ en 10; Inter ganó por solo 1 o empató en 6/10, incluido Napoli en casa; Brugge marca (2.2 GF) y hace partidos abiertos que pueden terminar 3-2/2-1; Brugge perdió por 1 contra el único rival de Champions que enfrentó. El mercado puede estar cargando algo de goleada por reputación.
En contra:
- Es una apuesta contra un favorito muy fuerte; 2.155 paga exactamente lo que el mercado ya cree (44%). No hay evidencia independiente de ventaja: la tasa observada de no ganar por 2+ de Inter (6/10, 2/5 en casa) es comparable o inferior al 44% hacia abajo en casa, y el 10/10 de Brugge es contra ligas inferiores.
- Los partidos de Inter en casa tienden a goleadas amplias (4-1, 5-3, 3-0); el ataque (2.5 GF) y la defensa floja de Inter (1.4 GA) dan marcadores altos con diferencias de 2+.
- Inter ya fue vetado en +2.5 por riesgo de goleada (vetoes.json); +1.5 queda más expuesto aún.
- Brugge perdió 1-2 con Union, Gent: puede perder por 1 con facilidad, pero Inter-Real fue 1-2, es decir, Inter tampoco domina a los fuertes.
Escenarios de pérdida concretos: 2-0, 3-0, 3-1, 4-1, 4-2 (cualquier victoria local por 2+). Pierde también si Inter rota poco y Brugge se desfonda.
Invalida el pick: once titular de Inter completo con Brugge con bajas defensivas; línea que se mueva a +2 ya desde 18:00Z; pendientes: alineaciones, bajas, rotación (Inter jugó el 10-oct, 3 días de descanso, igual que Brugge).
VEREDICTO: DÉBIL (el sesgo observado favorece +1.5, pero la muestra de Brugge es de otro nivel y el precio es pura línea de mercado sin ventaja demostrable).

## Pata 3. Arsenal - Lille, menos de 3.5 goles @1.57 (19:00Z)
Hechos:
- Totales de Arsenal (10): 5 (Emirates Cup, amistoso), 3 (Community Shield vs City), 3, 1, 3, 1, 2, 6 (Ipswich, League Cup), 3, 3 -> 2/10 con 4+; solo 1/9 si se excluye el amistoso. En casa: 5,3,3,3,3: cuatro de cinco con exactamente 3 goles, es decir a un gol de perder.
- Lille (10, todo Ligue 1/Champions): 2,1,2,2,4,1,5,2,3,1 -> 2/10 con 4+: ambos contra los rivales más fuertes (2-2 PSG, 2-3 Betis en Champions). De visitante en liga: 1-0, 2-0, 1-0, 1-2 (todos ≤3).
- Mercado (7 casas): Under 3.5 1.581 / over 2.374 -> 60% sin margen; Arsenal 1.213 (78.5% sin margen), X 6.6, Lille 13.6. Corrección cuantitativa b11: mercado over 3.5 40% vs 4/20 observado (mercado más alto que las frecuencias).
- Discrepancia: level2/deportivo.md y auditor_ronda2 dicen que la muestra de Lille tiene 3 amistosos; en matrix.json el historial de Lille son solo Ligue 1 y Champions (sin amistosos). Los amistosos sí están en Arsenal (Emirates Cup). Se usa el matrix.json como dato primario.
A favor: frecuencia 8/10 en cada equipo ≥ mercado 60%; Lille defiende bien fuera; Arsenal gana por la mínima o 3-0 (promedio de ~2.1 GF/1.0 GA es contenido); Champions suele cerrarse.
En contra:
- Arsenal es favorito muy fuerte (1.21): cualquier 3-1, 4-0, 3-2 o 2-2 con un gol extra de Lille rompe la pata. Con 4/5 locales en exactamente 3 goles, no hay colchón.
- Los dos únicos partidos con 4+ de Lille fueron ante los rivales más fuertes y Betis les marcó 3 en Champions; la muestra de liga francesa no representa a Arsenal.
- Arsenal marcó 4-2 en Ipswich y 5 en el amistoso; Lille concedió 3 en casa en Champions (Betis).
- Rivales de la muestra de Arsenal incluyen equipos modestos (Coventry, Sunderland, Leeds) y amistosos.
Escenarios de pérdida: 4-0, 3-1, 3-2, 2-2, 4-1.
Invalida el pick: Arsenal en su onceno ofensivo completo con Lille con defensa debilitada; la línea de goles subiendo en vivo antes del cierre; pendientes: alineaciones, bajas, árbitro.
VEREDICTO: DÉBIL (8/10 es respaldo real pero con muestra mixta, favorito muy fuerte y Arsenal en casa con tendencia a 3 goles exactos).

## Pata 4 (solo ticket mixto). Atlético Bucaramanga - Águilas Doradas, local o empate (1X) @1.25 (23:30Z, Primera A)
Hechos (matrix.json, misma competición, Clausura, n=10 por equipo):
- Bucaramanga: DDWDDWDWWW, 0 derrotas en 10 (5V-5E). En casa (n=5): 1-1, 1-1, 2-2, 2-0, 3-1, sin derrota.
- Águilas: DDDDLDLLWD, 1 victoria en 10. Fuera (n=5): 2-2, 0-2, 0-1, 0-2, 2-2: ninguna victoria; 3 derrotas.
- Mercado: 1X2 1.979/3.202/3.756; 1X sin margen ~75% (el 0.379 de finalists.json es un error ya señalado). 1X a 1.25 equivale a 80% bruto, es decir por debajo del precio "justo" (~1.33), el mercado no regala valor.
- Auditor y pares: H2H (Águilas ganó el último, 2-1 en abr-2026) sin mucho peso; Clausura ~34% empates (n=126) según level2.
A favor: es la pata mejor respaldada por tipo de muestra (mismo torneo, local invicto, visitante sin victorias fuera); 1X solo pierde si gana Águilas, 1/10 en su historial.
En contra: 3.76 del visitante ~26% implica un riesgo real; Águilas gana pocas veces pero empata mucho y Bucaramanga ha concedido en 5/5 casa (BTTS 8/10), así que su ventaja no es sólida; no hay estudio casa/fuera con n≥8; hora 23:30Z impide ver la alineación antes de decidir los otros tramos.
Invalida: bajas importantes de Bucaramanga o Águilas con delanteros nuevos; pendientes: alineaciones, lesionados.
VEREDICTO: DEFENDIBLE.

## Veredicto por ticket
Cálculo (cuotas de agregador): producto de cuotas vs probabilidades sin margen multiplicadas.
- BORRADOR solo_real x4.365: Leipzig O2.5 (72%) x Brugge +1.5 (44%) x Arsenal U3.5 (60%) = 0.19 de probabilidad de mercado, cuota justa ~5.2 contra 4.365 pagado (colchón de margen negativo). El apoyo descriptivo conjunto 0.138 es un límite inferior, no una probabilidad. Patas: DEFENDIBLE, DÉBIL, DÉBIL. Ticket: DÉBIL.
- COMBINADA mixto_real x4.229: Bucaramanga 1X (75%) x Brugge +1.5 (44%) x Arsenal U3.5 (60%) = 0.20, cuota justa ~5.0 contra 4.229. Patas: DEFENDIBLE, DÉBIL, DÉBIL. Ticket: DÉBIL (algo mejor que el borrador solo Champions: la pata distinta tiene muestra de la misma competición y local invicto).
- Las dos comparten las dos patas débiles y la dependencia de que Inter no gane por 2+ y Arsenal-Lille no pase de 3 goles, ambos partidos con favorito muy fuerte. Ninguna de las dos es una apuesta de valor.

## Recomendación sobre jugar como experimento único
- Como "pick de seguridad", no. Como experimento único de relajación de filtros, aceptable solo con stake simbólico, preferentemente la COMBINADA mixto_real (pata 1X mejor respaldada) y solo si las alineaciones (~18:00Z) no muestran rotaciones en Inter ni Arsenal. Si las alineaciones no se pueden comprobar antes del cierre, no jugarla.
- Si se acepta recortar: quitar la pata de Inter +1.5 (la más expuesta) mejora más el ticket que cambiar cualquier otra.
- Antes de jugar: comprobar que la casa permite combinar partidos con inicios distintos (19:00Z y 23:30Z en el mixto) y la cuota real recalculada, y que las cuotas medias del agregador (2.155, 1.57, 1.29, 1.25) existen en una sola casa.

## Datos pendientes
Alineaciones y bajas de los cuatro partidos (no consultado, fuentes externas fuera de alcance), rotaciones por descanso (todos jugaron 9-10 oct), árbitros, línea en una casa concreta y su cuota real de combinada, separación casa/fuera con n≥8 para Bucaramanga, marcadores a 90' en las copas del historial.
