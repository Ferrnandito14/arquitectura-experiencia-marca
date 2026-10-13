# Pares de dos patas del mismo partido: evaluacion cuantitativa (2026-10-13)

Analista cuantitativo. Solo datos locales (matrix.json api_prices, review_cards.json, tickets.json, batch/*.json). Sin API ni fuentes externas. Calculos: calc.py (novig, combo, freq, ev) mas dos scripts de sensibilidad propios (Poisson bivariante y metodo potencia) en el scratchpad.

## 0. Separacion de capas y limites

- Frecuencia observada: k/n de review_cards / tickets (n=10 por equipo, mezcla local/visitante, sin ajuste por rival). NO es probabilidad.
- Probabilidad implicita bruta = 1/cuota. Sin margen = proporcional (aproximacion). Sensibilidad: metodo potencia (reparte mas margen en el lado largo).
- Estimacion de modelo: la dependencia entre patas sale de un Poisson bivariante ajustado a 1X2 y Over 2.5/3.5 sin margen (HIPOTESIS no verificada: solo fija la fraccion de solape de los fallos). Las marginales son siempre las del mercado.
- Cuotas = medianas de api_prices entre casas distintas (n_casas indicado). NO son una cuota verificada de una sola casa para la combinada. "Cuota del par" = producto; la casa recalcula combinadas del mismo partido, asi que la cuota real es <= producto (A dio conservadora x1.218; B x1.259). Sin cuota combinada verificada no hay valor economico confirmado en ningun par.
- Conjunta de dos patas ganadoras: P = 1 - P(fallo1) - P(fallo2) + P(ambos fallan). Cotas de Frechet: max(0, p1+p2-1) <= P <= min(p1,p2). El maximo solo se alcanzaria si todo fallo de una pata implicara fallo de la otra; aqui es imposible (p. ej. 3-2).
- "Apoyo conjunto" de tickets.json = media de los limites inferiores Wilson de cada equipo (p. ej. (0.722+0.596)/2=0.659). Es un suelo estadistico de frecuencias, NO una probabilidad. En tickets.json solo A y E tienen apoyo conjunto medido; B, C y D no (conjunto no medido).
- Batch corrections: b07-cuant sobre Birmingham-Preston: "BTTS 15/20 vs 54% implicita, sin ajuste por rival" (no es ventaja); sobre Bucaramanga: "Over 1.5 18/20 vs 70%: no tratar como ventaja"; b06-cuant/depor sobre Kyoto-Ratchaburi: corners 10/10 sospechosos, historial mixto con 4 partidos de copa, no ajustado por rival. Ninguna correccion toca los mercados de los pares, pero la cautela de muestra aplica.

## 1. Datos de mercado por pata (sin margen)

| Pata | Cuota mediana (n_casas, min-max) | Bruta | Sin margen prop. | Sin margen potencia | Fallo (prop.) |
|---|---|---|---|---|---|
| Birm-Pres: Preston +2.5 | 1.125 (4; 1.11-1.18) vs -2.5 local 4.85 | 0.889 | 0.812 | 0.863 | local gana por 3+: 0.188 |
| Birm-Pres: Menos 4.5 | 1.14 (7; 1.12-1.18) vs mas 5.0 | 0.877 | 0.814 | 0.855 | 5+ goles: 0.186 |
| Birm-Pres: 1X | 1.14 (8; 1.10-1.18); 1X2 1.595/4.075/5.4 | 0.877 | 0.825 | 0.839 | gana Preston: 0.175 |
| Bucaramanga: 1X | 1.25 (8; 1.16-1.27); 1X2 1.99/3.2/3.765 | 0.800 | 0.754 | 0.761 | gana Aguilas: 0.246 |
| Bucaramanga: Menos 4.5 | 1.06 (6; 1.05-1.10) vs mas 7.275 | 0.943 | 0.873 | 0.926 | 5+ goles: 0.127 (potencia 0.074) |
| Bucaramanga: Mas 0.5 | 1.05 (6; 1.03-1.08) vs menos 7.85 | 0.952 | 0.882 | 0.937 | 0-0: 0.118 (potencia 0.063) |
| Kyoto-Ratchaburi: Rat. +1.5 | 1.68 (6; 1.65-1.72) vs -1.5 local 2.13 | 0.595 | 0.559 | 0.565 | local gana por 2+: 0.441 |
| Kyoto-Ratchaburi: Menos 3.5 | 1.43 (7; 1.38-1.45) vs mas 2.62 | 0.699 | 0.647 | 0.666 | 4+ goles: 0.353 |

Margen de cada mercado de 2 vias: 6.5% a 9.5%. Cada pata paga entre 6% y 9% de margen, y se compone en el par.

Frecuencias (k/n; Wilson 95% por calc.py; n=10 por equipo, mix casa/fuera; misma competicion salvo E, historial mixto):
- A: handicap +2.5 10/10 y 10/10; Menos 4.5 10/10 y 10/10 (over 3.5: 3/10 y 4/10; ningun partido con 5+). Wilson n=10: 0.722-1.000; agregado 20/20: 0.839-1.000.
- B: 1X Bucaramanga 10/10 (local) y rival sin ganar 9/10 (Wilson 0.596-0.982). Menos 4.5 NO esta medido en review_cards (solo over 3.5: 5/10 y 4/10). Mas 0.5 / 0-0 NO medido.
- D: 1X derivado de las cadenas de forma (mezcla casa/fuera): Birmingham sin perder 9/10, Preston sin ganar 9/10 (Wilson 0.596-0.982). Menos 4.5 10/10 y 10/10.
- E: handicap +1.5: 10/10 y 9/10; Menos 3.5: 9/10 y 7/10 (over 3.5: 1/10 y 3/10). Apoyo conjunto conservador 0.496.

## 2. Resultados por par

Rango de la conjunta = de la independencia (suelo razonable bajo correlacion positiva) al maximo plausible (marginales por metodo potencia con solape alto).

| Par | 1/cuota del par | Conjunta mercado (rango; central) | Cotas Frechet | Independencia | Solape de fallos (modelo) |
|---|---|---|---|---|---|
| A Birm-Pres +2.5 y U4.5 (x1.2825) | 0.780 | 0.66-0.80; central 0.71-0.78 | 0.626-0.812 | 0.661 | 46% del menor fallo (fuerte) |
| B Bucara 1X y U4.5 (x1.325) | 0.755 | 0.66-0.71 | 0.627-0.754 | 0.658 | 27-29% (casi independiente) |
| C Bucara 1X y Mas 0.5 (x1.3125) | 0.762 | 0.64-0.70 (identidad exacta) | - | - | 0%: fallos disjuntos |
| D Birm-Pres U4.5 y 1X (x1.2996) | 0.770 | 0.66-0.73 | 0.639-0.814 | 0.672 | 16-18% (independiente) |
| E Kyoto-Rat. +1.5 y U3.5 (x2.4024) | 0.416 | 0.36-0.51; modelo 0.43-0.45 | 0.206-0.559 | 0.362 | 63-67% (muy fuerte) |

Derivacion:
- C: 0-0 es un empate, esta dentro de 1X. Asi P(1X y Mas 0.5) = P(1X) - P(0-0) exactamente. Con P(1X)=0.754-0.761 y P(0-0)=0.063-0.118 resulta 0.64-0.70. La segunda pata solo anade un fallo propio.
- A: Preston +2.5 y Menos 4.5 comparten fallos (5-0, 4-1, 6-0...), por eso la conjunta sube sobre la independencia 0.661. Modelo: 0.71 con marginales proporcionales, 0.78 con potencia.
- E: casi todo 2+ de diferencia local con 4+ goles se solapa (3-1, 4-0, 4-1, 5-0). La conjunta (0.43-0.45 en el modelo) es mucho mayor que la independencia 0.362.

### Coherencia de la cuota del par con la conjunta

| Par | Cuota par (producto) | Cuota justa en el rango | Lectura |
|---|---|---|---|
| A | 1.2825 (cons. 1.218) | 1.25-1.51 (central 1.28-1.41) | No inflada por independencia: el producto ya esta en el borde bajo, paga como si la dependencia fuera casi maxima. Aun asi no supera la cuota justa central. |
| B | 1.325 (cons. 1.259) | 1.41-1.52 | Inferior a la justa en todo el rango: desfavorable. |
| C | 1.3125 | 1.43-1.56 | Desfavorable en todo el rango; la pata anade +5% de cuota por -6 a -12 puntos de probabilidad. |
| D | 1.2996 | 1.37-1.52 | Desfavorable en todo el rango. |
| E | 2.4024 (la real probablemente menor) | 1.96-2.78 (modelo 2.22-2.33) | Solo el producto completo supera la cuota justa del modelo; si la casa recalcula con la correlacion, queda por debajo. |

Ninguna cuota de par esta "inflada por independencia": el producto es menor que 1/independencia porque cada pata ya carga margen. El problema es el contrario: el margen se compone (6-9% por pata) y la correlacion positiva solo rescata parte.

### Equilibrio 1/cuota frente al apoyo conjunto medido (Wilson; NO es probabilidad)

| Par | Equilibrio | Apoyo medido | Lectura |
|---|---|---|---|
| A | 0.780 (cons. 0.821) | 0.722 conjunto; agregado 20/20: 0.839 | El suelo por equipo (n=10) queda bajo el equilibrio; el agregado lo supera pero mezcla equipos y rivales, es descriptivo. Si la conjunta del mercado (0.71-0.78) fuera la verdadera, 20/20 tendria probabilidad 0.1%-0.7%: o la muestra es atipicamente tranquila o el mercado carga la cola. No se traduce en probabilidad. Preston: 8 derrotas en 10 sin ninguna por 3+ (GC 1.9), racha propensa a regresion. |
| B | 0.755 | 1X: 0.659 (min. 0.596). U4.5 y conjunto: no medido | Sin base de frecuencia del par. El suelo de 1X ya esta bajo el equilibrio de la pata sola. |
| C | 0.762 | 1X 0.659 (min. 0.596). Mas 0.5 y conjunto: no medido | Idem. |
| D | 0.770 | 1X 0.596 por equipo (9/10 y 9/10, derivado de forma); U4.5 0.722; conjunto no medido | Suelos bajo el equilibrio. |
| E | 0.416 | 0.496 conjunto (Menos 3.5: 9/10 y 7/10; +1.5: 10/10 y 9/10) | Supera el equilibrio en 8 puntos, pero es historial mixto (4 partidos de copa de Kyoto, liga tailandesa de Ratchaburi), n=10, sin ajuste por rival. La forma de Kyoto (GF 0.9) contradice al mercado (local 1.39); la conjunta se estima del mercado, no de la frecuencia. |

### EV teorico en el rango de la conjunta (p x cuota - 1, calc.py)

| Par | EV a cuota = producto | EV a cuota conservadora/recalculada |
|---|---|---|
| A | p 0.66: -15.4%; 0.71: -8.9%; 0.745: -4.5%; 0.78: 0.0%; 0.80: +2.6%. Rango -15% a +3% | x1.218: -20% a -2.6% (todo negativo) |
| B | p 0.66: -12.6%; 0.71: -5.9%. Rango -13% a -6% | x1.259: -17% a -11% |
| C | p 0.64: -16.0%; 0.70: -8.1%. Rango -16% a -8% | peor si hay recalculo |
| D | p 0.66: -14.2%; 0.73: -5.1%. Rango -14% a -5% | peor si hay recalculo |
| E | p 0.36: -13.5%; 0.43: +3.3%; 0.45: +8.1%; 0.51: +22.5%. Cruza 0 | cuota 2.2 con p 0.43-0.45: -5.4% a -1.0%; cuota 2.0: -14% a -10% |

Referencia de patas solas (mismo analisis): 1X Bucaramanga @1.25, p 0.754-0.761: EV -5.8% a -4.9%; Preston +2.5 @1.125, p 0.81-0.86: -8.9% a -3.3%; Menos 4.5 Birm-Pres @1.14, p 0.814-0.855: -7.2% a -2.5%. Apilar patas en B, C y D empeora el EV de la pata sola; en A lo deja parecido.

Cuota minima para EV 0 con la conjunta: A 1.28-1.40; B 1.41-1.52; C 1.43-1.56; D 1.37-1.52; E 2.22-2.33 (modelo), 2.78 (independencia).

## 3. Veredictos

- A. Birmingham-Preston +2.5 y Menos 4.5: ACEPTABLE CON SALVEDADES. Alta probabilidad (conjunta de mercado 0.71-0.78; 20/20 en frecuencia) pero precio desfavorable: EV central -9% a -4%, cruza 0 solo en el extremo optimista y con el producto completo; con recalculo (x1.218) todo el rango es negativo. Salvedades: patas muy correlacionadas, handicap solo en 4 casas, muestra sin ajuste por rival, sin cuota de una casa verificada. Probable, no rentable demostrado.
- B. Bucaramanga 1X y Menos 4.5: DESACONSEJADO. Conjunta 0.66-0.71 frente a equilibrio 0.755; EV -13% a -6%; la segunda pata resta mas probabilidad de la que suma en cuota y no tiene frecuencia propia medida.
- C. Bucaramanga 1X y Mas 0.5: DESACONSEJADO. P = P(1X) - P(0-0): 0.64-0.70 frente a 0.762; EV -16% a -8%. Mas 0.5 solo anade riesgo.
- D. Birmingham-Preston Menos 4.5 y 1X: DESACONSEJADO. Casi independientes: 0.66-0.73 frente a 0.770; EV -14% a -5%. Peor que A.
- E. Kyoto-Ratchaburi +1.5 y Menos 3.5: ACEPTABLE CON SALVEDADES (condicionado al precio). La dependencia fuerte hace que la conjunta del modelo (0.43-0.45) supere el equilibrio del producto 0.416 (EV +3% a +8%), pero el rango completo cruza 0 y la casa recalcula: con cuota ~2.2 el EV es -5% a -1%. Solo defendible con cuota combinada verificada de una casa >= ~2.35. Salvedades: historial mixto, n=10, forma de Kyoto contradice al mercado, inicio 10:00 UTC (verificar que siga prematch).

Nada de lo anterior confirma valor economico: no hay cuota combinada verificada de una sola casa para ningun par.

Scripts de sensibilidad: /tmp/claude-0/-home-user/d56b1dd2-9e37-5240-9a83-4b470c476a77/scratchpad/pois.py y pw.py
