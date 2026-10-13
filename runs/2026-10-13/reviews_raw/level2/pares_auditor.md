# Auditoría adversarial de pares del mismo partido (2026-10-13)

Fuentes abiertas por mí (sin API ni web): tickets.md, tickets.json (cabecera), review_cards.json, matrix.json (api_prices de m-adc7b810d3d6 Birmingham, m-53aa260644d7 Bucaramanga, m-0c15b801051b Kyoto), inventory.json (solo calendario; sin precios por casa), reviews_raw/batch b06 y b07 (deportivo y cuantitativo), level2/deportivo.md, cuantitativo.md, auditor.md, auditor_ronda2.md, vetoes.json.
Hora del sistema al auditar: 2026-10-13 05:33Z. Kyoto (10:00Z), Birmingham (19:00Z) y Bucaramanga (23:30Z) aún no han empezado. No hay alineaciones de ningún partido (deportivo, 04:00Z: get_lineups vacío).

## Método de mi contraste (declarado como [I], no es una fuente)
1. Probabilidad "justa" de cada pata = cuotas MEDIANAS de api_prices normalizadas por su par de cuotas (o por las 3 de la doble oportunidad, dividiendo por suma/2).
2. Probabilidad conjunta: Poisson independiente (lh, la) calibrado a 1X2 y a una línea de goles de cada partido. Modelo tosco (sin Dixon-Coles ni sobredispersión); reproduce los marginales del mercado (Birmingham: +2.5 0.825 vs 0.812; U4.5 0.821 vs 0.814; 1X 0.813 vs 0.817) pero las colas conjuntas son indicativas.
3. Cota sin modelo (Fréchet): para que un par pague, P(perder alguna pata) debe ser ≤ 1 − 1/(producto de cuotas).

| Par | Producto | Equilibrio 1/producto | P(conjunta) modelo | EV al precio-producto | Cota sin modelo |
|---|---|---|---|---|---|
| A Birm +2.5 vis + U4.5 | 1.2825 | 0.780 | 0.724 | −7% | haría falta que ≥82% de los partidos con 5+ goles fueran goleadas locales de 3+: implausible |
| B Buc 1X + U4.5 | 1.325 | 0.755 | 0.661 | −12% | pérdida máxima tolerable 0.245 < P(falla la 1X sola) ≈0.25: no paga con NINGUNA correlación |
| C Buc 1X + O0.5 | 1.3125 | 0.762 | 0.655 | −14% | pérdidas disjuntas (0-0 es 1X ganada; victoria visitante implica ≥1 gol): pérdida ≥ 0.25 + P(0-0) |
| D Birm U4.5 + 1X | 1.2996 | 0.769 | 0.665 | −14% | haría falta que ≥75% de las victorias visitantes tuvieran 5+ goles: implausible |
| E Kyoto/Rat +1.5 vis + U3.5 | 2.402 | 0.416 | 0.452 | +9% al precio-producto; ≈ −5% a −9% a un precio de casa realista | ver E |

Cuotas medianas usadas: Birmingham +2.5 vis 1.125 (home −2.5 a 4.85; overround de la línea 1.095; 4 casas, 3 precios distintos), U4.5 1.14 (7 casas), 1X 1.14 (8). Bucaramanga 1X 1.25 (8), U4.5 1.06 (6; rango 1.05–1.10; overround de línea ≈1.08), O0.5 1.05 (6; par 7.85; overround ≈1.08). Kyoto +1.5 vis 1.68 (6), U3.5 1.43 (7).

---

## (A) Birmingham – Preston: +2.5 visitante @1.125 + U4.5 @1.14 (×1.282 / cons. ×1.218)

Objeción principal (ALTO): el "apoyo conjunto 0.722" es el techo de Wilson de un 10/10 con n=10, no evidencia: cualquier 10/10 da 0.722 y no distingue una pata del 75% de una del 95%. El equilibrio es 0.780 y el mercado (sin margen) da ≈0.68 si fueran independientes y ≈0.72 con la correlación real. El par no tiene ventaja demostrada: es precio justo menos margen (≈ −7%).

Secundarias:
1. (ALTO, comprobable) tickets.md dice "0.722 frente a 0.521 si fueran independientes: las patas se refuerzan entre sí". Compara un Wilson de 10/10 con el producto de dos Wilson (0.722²); con n=10 el 10/10 conjunto da 0.722 por construcción. Mi modelo sí sugiere asociación positiva (0.724 vs 0.825×0.821=0.677) pero de ~+5 pp, no +20 pp. Debe retirarse la frase.
2. (MEDIO) Muestras contradictorias: la ficha (solo Championship) da Preston +2.5 = 10/10; level2/deportivo.md cita un 0-4 ante Everton (Copa) y "9/10 y 10/10", "solo cayó por 3+ en 1/10". Depende de excluir ese partido. Con 0/10 o 1/10 frente a un 17-19% justo de goleada local, 0/10 ocurre con p≈0.12-0.15: no contradice al mercado.
3. (MEDIO) La +2.5 tiene 4 casas (1xBet, Betfair, Marathon, bet365) y 3 precios distintos; cuantitativo ya anotó que 1xBet y Marathon repiten precio (misma fuente de precios) -> ~3 independientes. Rango 1.11–1.18: 1.125 es la mediana, no un precio garantizado.
4. (MEDIO) El veto de la +1.5 ("overround 1.153 anómalo") sale de dividir MEDIAS de casas distintas, con un 1.01 en el lado local de −1.5 (minmax [1.01, 2.74]); con medianas el overround es 1.089 (normal). La +2.5 no tiene esa anomalía (1.095), pero el precedente indica precios mal alineados en el agregador; la mediana de 4 casas es frágil.
5. (MEDIO) Escenario de pérdida conjunta: partido abierto (BTTS 8/10 y 7/10; Preston GA 1.9). Un 4-1 o 5-1 cae en ambas; un 3-0 solo en la +2.5; un 3-3 o 2-3 solo en la U4.5. Birmingham 0V-4E-0D en casa (7:7) ayuda a la +2.5 y resta credibilidad al "favorito 1.59".
6. (MEDIO) Alineaciones [ND]; Preston #24 puede rotar o cambiar de entrenador.
7. (MEDIO) La casa recalcula combinadas del mismo partido y no está comprobado que +2.5 y totales se puedan combinar. El producto 1.2825 queda justo sobre el tope del rango (1.28); la cifra a esperar es la conservadora 1.218.
8. (BAJO) Selección adversa: el par se eligió por caer en el rango; márgenes de línea 9.5% (+2.5) y 7.7% (U4.5).

Qué lo resolvería: cuota real del combinado en la casa (≥1.20 mínimo; para EV≥0 según el modelo haría falta ≈1.38, no ocurrirá); alineaciones de las 18:00Z; marcadores de los 10 de Preston con y sin el 0-4 de Copa.
Veredicto sugerido: ACEPTABLE CON SALVEDADES (el más defendible de los cinco en términos relativos; no es una apuesta con ventaja). Veto: NO, con condiciones: cuota real del combinado ≥1.20 y retirar el texto del "refuerzo".
Mejor alternativa: dos patas de partidos distintos (sin recálculo ni correlación). Bucaramanga 1X simple @1.25 (EV de modelo ≈ −5%) es algo mejor que A (−7%).

---

## (B) Bucaramanga – Águilas Doradas: 1X @1.25 + U4.5 @1.06 (×1.325 / cons. ×1.259)

Objeción principal (ALTO): la U4.5 a 1.06 es un impuesto, no un seguro. Paga 6% por un riesgo de 5+ goles justo de ≈11-13% (equilibrio 94.3% vs justo ≈87-89%; overround de línea 1.08). Y la pérdida máxima tolerable del par (0.245) es menor que la probabilidad de que la 1X falle sola (≈0.25): con los precios del propio mercado el par no puede ser ≥0 con ninguna correlación.

Secundarias:
1. (ALTO) Dominado por la simple: 1X @1.25 ya está en el rango ×1.20–1.28; el par sube a 1.325 (fuera del tope) y solo la rebaja del 5% lo devuelve a 1.259.
2. (MEDIO) La 1X depende del empate: Clausura 31.5% empates (auditor, n=126), Águilas ganó el último H2H (2-1, abr-2026). Mínimo de casa 1.16 (atípico). Apoyo 0.659 = media de 0.722 y 0.596 (visitante 9/10).
3. (MEDIO) La U4.5 no tiene k/n en la ficha (solo Over 3.5: 5/10 y 4/10, que no es la línea); sin base muestral.
4. (BAJO) Cuadrangular: posible rotación; alineaciones [ND].

Qué lo resolvería: solo una cuota real del combinado ≥1.30 (improbable).
Veredicto sugerido: DESACONSEJADO. Veto: SÍ para el par (dominado por la 1X simple; la U4.5 es recargo). Mantener la 1X simple.
Mejor alternativa: Bucaramanga 1X simple @1.25.

---

## (C) Bucaramanga – Águilas Doradas: 1X @1.25 + Más de 0.5 @1.05 (×1.312)

Objeción principal (ALTO): las pérdidas son disjuntas. El 0-0 es un empate (1X ganada) pero pierde el O0.5; que gane el visitante implica ≥1 gol. Los riesgos se suman: ≈0.25 (visitante) + ≈0.08-0.12 (0-0; par Under 0.5 a 7.85, overround 1.08) -> conjunta 0.63-0.67 frente a equilibrio 0.762: EV −12% a −17%.

Secundarias:
1. (ALTO) Dominado por la simple y fuera del tope (1.312 > 1.28); cons. ≈1.246 solo por la rebaja del 5%.
2. (MEDIO) 18/20 en Over 1.5 de la muestra no es la línea 0.5 y es mezcla casa/fuera sin ajuste por rival (b07 cuant: "no tratar como ventaja").
3. (BAJO) Mismas limitaciones que B (empates, alineaciones [ND]).

Qué lo resolvería: nada razonable.
Veredicto sugerido: DESACONSEJADO. Veto: SÍ (riesgos disjuntos sumados por 5% de recompensa; dominado por la 1X simple).
Mejor alternativa: Bucaramanga 1X simple.

---

## (D) Birmingham – Preston: U4.5 @1.14 + 1X @1.14 (×1.30)

Objeción principal (ALTO): suma de riesgos casi disjuntos por poca recompensa. Pierde si gana Preston (≈18%, aunque es 1V-1E-7D) o si hay 5+ goles (≈18%); el solape (victoria visitante con 5+ goles) es pequeño. Modelo: conjunta 0.665 vs equilibrio 0.769 (−14%). Para ser neutral, ≥75% de las victorias visitantes tendrían 5+ goles.

Secundarias:
1. (ALTO) Dominado por A: mismo partido y misma U4.5, pero A usa la +2.5 (EV −7% vs −14%); la +2.5 pierde solo en goleada local de 3+, la 1X en cualquier victoria visitante. Producto 1.2996 fuera del tope.
2. (MEDIO) La 1X de Birmingham no tiene apoyo propio: 0V-4E-0D en casa; su valor viene de que Preston sea el peor, ya cotizado (1.14).
3. (MEDIO) Alineaciones [ND].

Qué lo resolvería: cuota real del combinado ≥1.38 (inalcanzable).
Veredicto sugerido: DESACONSEJADO. Veto: SÍ (dominado por A).
Mejor alternativa: el par A.

---

## (E) VARIANTE Champions: Kyoto – Ratchaburi +1.5 visitante @1.68 + U3.5 @1.43 (parte de amplio_champions #1)

Objeción principal (ALTO): el producto 1.68×1.43 = 2.402 no es un precio obtenible. Las patas están positivamente asociadas (modelo: conjunta 0.452 vs 0.569×0.649=0.369), así que la casa baja la combinada: precio justo ≈2.21 y con margen ≈2.0-2.1, que a 0.452 da ≈ −5% a −9%. Solo el precio-producto (que no existirá) da +9%. Además es la pata máxima entre ~3200 (maldición del ganador; auditor T4: único EV descriptivo positivo del sistema).

Secundarias:
1. (ALTO) Muestra mixta: Kyoto con 4 partidos de Copa (Emperador, J-League Cup), 0 goles en 4 y 9 GF en 10; Ratchaburi de Thai League + ASEAN, con 2 amistosos citados por deportivo (6-2, 5-0) pese a "sin amistosos"; rivales más débiles. Solo liga/competición: 6/6 y 6/6 (n pequeña). b06 (cuant): corners 10/10 idénticos en 8.5 y 9.5 "sospechoso"; b06 (dep): tarjetas local n=8.
2. (ALTO) Escenario de pérdida conjunta plausible: Kyoto 3-1 o 4-0 (mercado: ~44% gana por 2+, Kyoto −1.5 a 2.12) cae en ambas; un partido abierto de Ratchaburi (4-6 vs Shanghai Port; GF 2.3, GA 1.3) cae en la U3.5 aunque cubra el hándicap.
3. (MEDIO) Nivel 2 revisó los hándicaps de este partido, no la U3.5; 1.68 con 6 casas, 1.43 con 7; 1xBet y Marathon repiten precios.
4. (MEDIO) Ratchaburi jugó 7-oct y 9-oct y viaja a Japón: rotación/cansancio [I]; alineaciones [ND].
5. (MEDIO) Concentración: Kyoto +1.5 limitado a 1 borrador (T4 aceptada); a las 05:33Z aún no ha empezado, pero hay que comprobarlo antes de apostar.

Qué lo resolvería: cuota real del combinado ≥2.20 y alineaciones.
Veredicto sugerido: ACEPTABLE CON SALVEDADES (límite): solo si la casa da el par a ≥2.20 y se acepta la muestra mixta; si paga ≤2.10, DESACONSEJADO. Veto: NO absoluto, pero condicionado (excluir si cuota real <2.20, si ya empezó o si hay rotaciones).
Mejor alternativa: Kyoto +1.5 simple (deportivo: MANTENER, 1.683) sin la U3.5, o la U3.5 emparejada con otro partido.

---

## Vetos propuestos
- B (Bucaramanga 1X + U4.5): vetar el par; dominado por la 1X simple y no paga con ninguna correlación.
- C (Bucaramanga 1X + O0.5): vetar el par; pérdidas disjuntas (0-0 y victoria visitante).
- D (Birmingham U4.5 + 1X): vetar el par; dominado por A.
- A: no vetar, con condiciones (cuota real ≥1.20; retirar el texto del "refuerzo").
- E: no vetar; condicionado a cuota real del par ≥2.20.

Limitaciones: sin cuotas reales de casa, sin alineaciones, sin verificar el 0-4 de Copa de Preston; el modelo Poisson es calibración propia [I]; n=10 en todas las muestras.
