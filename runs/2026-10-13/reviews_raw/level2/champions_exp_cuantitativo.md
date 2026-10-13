# Experimento Champions (filtros relajados): precio y base estadística. Analista cuantitativo, 13-oct-2026 ~15:25 UTC

Fuentes locales (sin API ni web): tickets.json (targets experimento_champions_*), matrix.json (api_prices/markets), inventory.json (ids), reviews_raw/batch/b07 y b11, y cache/ local de apifootball (get_odds, cuotas por casa con sello 2026-10-13 03:18 UTC, ~12 h de antigüedad a la hora del informe). Cálculos con calc.py (novig, joint, ev, freq, combo); el desglose por casa y la sensibilidad usan las mismas fórmulas en un script auxiliar.

Todas las cuotas de los tickets son MEDIANAS ENTRE CASAS de un agregador: referencia de mercado, no ejecutable en una sola casa y sin segunda fuente comparable. No hay valor económico confirmado en ningún caso.

## 1. Patas: separación de conceptos

| Pata | Cuota (mediana; n casas; rango) | k/n observados (Wilson 95%) | Prob. bruta 1/c | Prob. sin margen (proporcional, aprox.) | Rango sin margen entre casas | EV de pata si p = sin margen |
|---|---|---|---|---|---|---|
| A Leipzig–PSV más de 2.5 | 1.29; 7; 1.28–1.34 | local 9/10 [0.60–0.98]; visitante 8/10 [0.49–0.94]; lote b11: 17/20 | 0.775 | 0.725 (contra 3.40) | 0.708–0.725 | -0.065 |
| B Inter–Brugge hándicap visitante +1.5 | 2.155; 8; 2.10–2.24 | local 6/10 [0.31–0.83]; visitante 10/10 [0.72–1.00] | 0.464 | 0.443 (contra 1.715 del -1.5) | 0.434–0.449 | -0.045 |
| C Arsenal–Lille menos de 3.5 | 1.57; 7; 1.53–1.66 | 8/10 y 8/10 [0.49–0.94]; lote b11: O3.5 4/20 | 0.637 | 0.6025 (contra 2.38) | 0.592–0.611 | -0.054 |
| D Bucaramanga–Águilas 1X (Primera A, 23:30 UTC, no es Champions) | 1.25; 8; 1.16–1.27 | 10/10 y 9/10 [0.60–1.00] | 0.800 | 0.754 (desde el 1X2 1.99/3.20/3.765, 10 casas) | 0.749–0.760 | -0.057 |

Notas:
- Las frecuencias son historial propio mixto (liga, copa, pretemporada), sin ajuste de rival ni localía; el revisor deportivo lo corrige así en b11. No son probabilidades.
- C: el historial apunta a menos goles que el mercado (b11: O3.5 mercado 40% vs 4/20), pero está contaminado por pretemporada (Emirates Cup) y rivales de nivel distinto. No se convierte en probabilidad.
- A: b11 anota O2.5 mercado 72% vs 85% observado, mismo defecto de muestra mixta. D: b07 señala 90% vs 70% en over 1.5, "no demostrativa".
- El sin-margen proporcional es aproximación: reparte el margen por igual y puede sesgar favorito/no favorito.

## 2. Tickets: conjunta de mercado frente a equilibrio

Partidos distintos (A, B y C a las 19:00 UTC), sin equipo ni árbitro compartido: independencia razonable, correlación residual no cuantificable (se asume cero; si fuese positiva la conjunta real sería algo mayor que el producto).

| Ticket | Multiplicador | Equilibrio 1/cuota | Conjunta sin margen (producto) | Rango por casa (ticket en una sola casa) | EV central | EV por casa (min / max) |
|---|---|---|---|---|---|---|
| BORRADOR solo Champions A+B+C | x4.365 | 0.229 | 0.194 | 0.186–0.196 (7 casas) | -0.155 | -0.213 / -0.108 |
| MIXTA D+B+C | x4.229 | 0.2365 | 0.201 | 0.194–0.209 (6 casas) | -0.148 | -0.208 / -0.105 |

Lectura: el equilibrio exige 0.229 y el mercado sin margen da 0.194; la brecha es el margen acumulado de tres patas (aprox. 15% del retorno esperado). Para EV=0 haría falta que las tres patas estuvieran infravaloradas a la vez en torno a +5.8% relativo cada una (+5.5% en la mixta). Ninguna cifra de este paquete lo respalda.

Ejecución por casa (cuotas 03:18 UTC): la mediana x4.365 no existe en una sola casa. Mejores observadas: 1xBet x4.76 (EV -0.108 con su propio sin-margen), Pncl x4.567, Betano x4.523; mixta 1xBet x4.536. Incluso en la mejor casa el EV bajo "el mercado tiene razón" es claramente negativo. WilliamHill, Sbo y Dafabet no ofrecen las tres patas.

Sensibilidad (NO es estimación): si cada pata verdadera estuviera +-0.05 absoluto respecto al sin-margen, la conjunta del borrador queda 0.147–0.249 y EV -0.360 a +0.089; la mixta 0.153–0.259 y EV -0.353 a +0.095. El rango cruza EV=0: sin ventaja demostrada, y el extremo positivo exige acertar con sesgo favorable en las tres patas a la vez. No hay base para un modelo propio, por lo que no se emite probabilidad propia ni EV propio.

## 3. Pata que más riesgo aporta por unidad de cuota (sobre sin-margen)

- Probabilidad de fallo por unidad de ganancia, (1-p)/(c-1): A 0.95, B 0.48, C 0.70, D 0.98. En el borrador, A (Leipzig más de 2.5 @1.29) es la peor; en la mixta, D (1X @1.25). Pagan muy poco por cada fallo posible.
- Coste de margen por unidad de log-cuota, ln(1/p)/ln(c): A 1.26, D 1.26, C 1.12, B 1.06. Las cuotas cortas soportan el mayor impuesto relativo de margen; B el menor.
- B es la de mayor varianza absoluta (falla 55.7%) y la de base más débil (6/10 de un equipo, Wilson inferior 0.313, por debajo del piso 0.40 que se relajó a 0.30), pero su precio es el más ajustado. No es la peor por unidad de cuota; es la más incierta por tamaño.

## 4. Coherencia del hándicap de Brugge (+1.5 @2.155)

Cuotas por casa (cache apifootball, 03:18 UTC; home -1.5 / away +1.5): bet365 1.70/2.10; Marathon 1.71/2.17; Betfair 1.67/2.10; BetVictor 1.62/2.11; Pncl 1.72/2.19; Sbo 1.74/2.16; 1xBet 1.76/2.24; Betano 1.75/2.15. La mediana 1.715/2.155 se reproduce.
- Overround por casa 1.015–1.075 (1xBet la más baja, 1.015, y de ahí sale el máximo 2.24; coherente, sin arbitraje ni cruce). Sin-margen visitante por casa 0.434–0.449.
- Cruce con 1X2 (medianas 1.25/6.325/11.0; sin margen 0.763/0.151/0.087): P(Inter gana) 0.763; ganar por 2+ (según -1.5) 0.557; ganar por 1 queda en 0.206; +1.5 = 1-0.557 = 0.443. Coherente. Además el -1.5 local (mín. 1.62) es mayor que la cuota 1X2 local de cada casa (1.22–1.29) y el +1.5 visitante (máx. 2.24) es menor que el X2 que contiene (mín. 3.64).
- Escalera: -2.5 local 2.68 / +2.5 visitante 1.44, sin margen local por 3+ goles 0.350. Márgenes de victoria: 1 gol 0.206, 2 goles 0.207, 3+ 0.350; monótono y plausible para un favorito 1.25 con total esperado alto. El -2 de bet365 (2.10/1.70) cuadra con el push.
- Conclusión: NO hay casa con línea cruzada en Inter–Brugge (a diferencia de Blackburn). Sí aparece en otro partido del paquete: Bucaramanga–Águilas, Betfair ah-1.5 local 1.06 / visitante 1.22 (línea mezclada). No afecta a D (1X) pero confirma que el agregador trae líneas contaminadas.
- Reserva: coherente no equivale a probable; solo muestra que el precio no está roto. El 0.443 es del mercado, no una estimación propia.

## 5. ¿El apoyo 0.49–0.54 justifica algo frente al mercado?

El apoyo es un límite inferior conservador de frecuencias de historial propio (apoyo_min_equipo 0.49 = Wilson inferior de 8/10; 0.313 = de 6/10; la fórmula exacta de apoyo_conservador no la he podido verificar).
- A: apoyo 0.543 vs sin-margen 0.725 y equilibrio 0.775. C: 0.49 vs 0.6025 y 0.637. Un límite inferior por debajo del mercado no lo contradice ni lo apoya.
- B: apoyo 0.518 vs 0.443. Aparenta superar al mercado, pero viene de un 10/10 del visitante contra rivales de otras ligas, no comparable con enfrentar a Inter en Champions, y de un 6/10 del local. Una frecuencia sin ajuste de rival no mueve una probabilidad que ya agregan 8 casas.
- Apoyo conjunto 0.138/0.167 vs equilibrio 0.229/0.2365 y mercado 0.194/0.201: cota descriptiva, no probabilidad; queda por debajo de ambos.
- Todo procede del mismo proveedor (apifootball): no son evidencias independientes.
- Veredicto: no justifica nada frente al mercado. Es criterio de elegibilidad, no de valor.

## 6. Selección adversa tras relajar filtros (417 patas)

- Los 417 candidatos salen de solo 9 partidos de Champions de hoy (~46 patas por partido, muy dependientes entre sí): los ensayos independientes son del orden de 9 partidos, no 417.
- Se elige dentro de una ventana de cuota (4.0–4.8) con apoyo >= 0.40 y piso por equipo 0.30. Con k/10 el ruido es grande: si p verdadero fuera 0.5, P(>=8/10)=0.055; con 0.6, 0.167; con 0.7, 0.383 (binomial; ilustra ruido de muestreo, no la probabilidad de las patas). Entre decenas de patas con p intermedio, varias superan el umbral por azar: maldición del ganador.
- Bajar el piso por equipo de 0.40 a 0.30 admite justo B (0.313), la de muestra más débil.
- La ventana fija el precio, no el edge: si el mercado es eficiente el EV esperado tiende a -margen acumulado (-0.15), con o sin filtros. Más combinaciones comparadas (comparaciones múltiples) aumentan la probabilidad de que el ganador parezca bueno por casualidad.
- La versión mixta añade D (otra competición, 23:30 UTC) que cumple función de llenar ventana de cuota, no un vínculo deportivo con la selección Champions.

## 7. Veredicto (probable no es rentable)

- Probable: probabilidades de mercado por pata D 0.75, A 0.72, C 0.60, B 0.44; conjunta 0.19 (borrador) y 0.20 (mixta), aproximadamente 1 de 5.
- Rentable: no demostrado. EV central -0.15 (rango por casa -0.21 a -0.11); la sensibilidad solo cruza cero con supuestos favorables en las tres patas. Patas individuales de probabilidad alta, pero precio desfavorable; ticket sin ventaja demostrada.
- Mixta frente a borrador: conjunta 0.201 vs 0.194 y EV central -0.148 vs -0.155; la diferencia es menor que la incertidumbre.
- Cualquier ejecución exigiría cuotas reales de una casa en el momento de apostar (las de 03:18 UTC tienen 12 h) y asumir un coste esperado del orden del 15% de la apuesta.

## Registro de fuentes

| Fuente | Ficha | Dato | Estado |
|---|---|---|---|
| matrix.json | api_prices (Leipzig, Brugge, Arsenal, Bucaramanga) | medianas, n casas, minmax | Consultada y útil (agregador, no ejecutable) |
| cache apifootball get_odds | ids 853192, 853133, 766902; lote 13-oct (853232) | cuotas por casa 03:18 UTC | Consultada y útil; un solo proveedor |
| tickets.json, review_cards, batch b07/b11 | patas, k/n, correcciones | apoyo, k/n, notas | Consultada y útil |
| Fuentes externas / API | - | - | No consultadas por instrucción |

Limitaciones: sin segunda fuente de cuotas; sin ajuste de rival, alineaciones ni bajas; liquidación del hándicap por casa (90 minutos) no verificada; cuotas con 12 h de antigüedad.
