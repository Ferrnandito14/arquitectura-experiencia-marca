# Nivel 2 — Revisión cuantitativa de borradores (jornada 2026-10-13)

Etiquetas: [CALC] calculado con calc.py por CLI sobre datos del repo/API · [EST] estimado/hipótesis (no verificada) · [NV] no verificable con las fuentes permitidas.
Consultas API usadas: 6 de 15 (get_odds de Orlando Pirates, Inter, Arsenal, Athletic-MG, Kyoto, Fajr; cuotas por casa, 2026-10-13). Sin clave expuesta. Scripts de trabajo en el scratchpad (no en el repo).

## 0. Hallazgos principales (resumen)

1. [CALC] Las 10 cuotas combinadas del documento se reproducen con calc.py (diferencia ≤0.002, redondeo). Las 10 están dentro del rango objetivo NOMINALMENTE; los 5 «amplio» están a 0.2–1.3% del límite inferior 4.0 (no hay margen).
2. [CALC] Error en «implícita sin margen» de las patas de doble oportunidad (1X, 12, X2): el script aplica novig a las 3 cuotas de doble oportunidad (overround 2.14, no es un mercado de resultados excluyentes). Valores del doc 0.379 / 0.426 / 0.272 / 0.384 son incorrectos; vía 1X2 (calc novig sobre 1X2 y suma de probabilidades) salen 0.754 / 0.840 / 0.550 / 0.759. Afecta el campo «implícita conjunta» de seguridad B3, B4 y amplio B1, B2, B5 (y el top de seguridad: Simba, Hartlepool). Es una cifra informativa, no cambia las cuotas ni los multiplicadores.
3. [CALC] Kyoto Sanga (seguridad B1) y Fajr Sepasi (amplio B1/B2): la «media de 3 casas» esconde que 2 casas (Marathon y 1xBet) dan exactamente la misma cuota (misma fuente de precios; no son 2 evidencias independientes) y una tercera es un valor atípico alto. Kyoto +2.5: Marathon 1.19, 1xBet 1.19, bet365 1.27 (media 1.217; el precio modal 1.19 está FUERA de 1.20–1.28). Fajr X2: Marathon 1.62, 1xBet 1.62, Betano 1.78 (media 1.673; precio modal 1.62).
4. [CALC] Pares del mismo partido: producto de medias ≈ producto misma casa (Inter 1.512–1.740; Arsenal 1.484–1.657; Pirates 1.421–1.508), pero una casa que acepte la combinada la recalcula; con correlación positiva (hándicap +2.5 y «menos de 5.5» comparten el escenario «no hay goleada») la cuota real es plausiblemente menor. La pata «menos de 5.5» (1.03–1.10) aporta casi nada de pago y puede ser casi redundante.
5. [CALC/EST] Todos los «amplio» caen por debajo de 4.0 con cualquier ajuste adverso pequeño (pago real de la casa 2–5% menor, Fajr a 1.62, o combinada con descuento). Ninguno es robusto.
6. [CALC] Cuota estimada de tarjetas (1.13): engañosa (sección 5). Dos borradores amplio (B2, B4) dependen de ella; sin esa pata quedan en ≈3.58.

## 1. Recálculo de cuotas combinadas (calc.py combo)

| Borrador | Doc | Recalc (por ítem) | Recalc (por pata) | Rango objetivo | Estado |
|---|---|---|---|---|---|
| Seg B1 | 1.217 | 1.2170 | 1.2170 | 1.20–1.28 | en rango (+1.4% sobre 1.20) |
| Seg B2 | 1.241 | 1.2410 | 1.2410 | idem | en rango |
| Seg B3 | 1.234 | 1.2340 | 1.2340 | idem | en rango |
| Seg B4 | 1.212 | 1.2122 | 1.2122 | idem | en rango (+1.0%) |
| Seg B5 | 1.276 | 1.2755 | 1.2755 | idem | en rango (0.4% bajo 1.28) |
| Amp B1 | 4.009 | 4.0099 | 4.0099 | 4.0–4.8 | en rango (+0.2%) |
| Amp B2 | 4.051 | 4.0503 | 4.0502 | idem | en rango (+1.3%) |
| Amp B3 | 4.034 | 4.0354 | 4.0355 | idem | en rango (+0.9%) |
| Amp B4 | 4.042 | 4.0411 | 4.0412 | idem | en rango (+1.0%) |
| Amp B5 | 4.031 | 4.0331 | 4.0330 | idem | en rango (+0.8%) |

Diferencias: ninguna material. Pares (doc → calc): Inter 1.589 → 1.5894; Athletic-MG 1.553 → 1.5526; Arsenal 1.559 → 1.5593; Pirates 1.452 → 1.4523. Nota: la cuota combinada es el producto de medias de casas distintas, no el precio de una casa (calc.py lo advierte): «ticket real solo si todas las cuotas son de la misma casa».

## 2. Patas: dispersión, nº de casas, implícita sin margen vs apoyo

Dispersión = (máx−mín)/media. Todas las cifras de cuota son de agregador (una sola vía de datos) salvo las comprobaciones por casa de la API hechas aquí.

| Pata | Cuota media (mín–máx, casas) | Disp. | Apoyo (k/n) | Sin margen [CALC] | Lectura |
|---|---|---|---|---|---|
| Kyoto +2.5 vis. (Seg B1) | 1.217 (1.19–1.27, 3) | 6.6% | 0.722 (10/10, 10/10) | 0.751 | 3 casas, 2 idénticas; mercado > apoyo |
| Cardiff u4.5 (Seg B2) | 1.241 (1.20–1.27, 7) | 5.6% | 0.659 (10/10, 9/10) | 0.752 | mercado > apoyo; 7 casas, estable |
| Bucaramanga 1X (Seg B3) | 1.234 (1.16–1.27, 8) | 8.9% | 0.659 (10, 9 de 10) | 0.754 (doc 0.379 ERROR) | dispersión media-alta |
| Norrköping u5.5 (Seg B4) | 1.107 (1.08–1.14, 7) | 5.4% | 0.722 | 0.839 | mercado ≫ apoyo (+0.12) |
| Simba 12 (Seg B4) | 1.095 (1.06–1.13, 4) | 6.4% | 0.722 | 0.840 (doc 0.426 ERROR; 1X2 solo 6 casas) | pocas casas |
| Gloucester o1.5 (Seg B5) | 1.093 (1.07–1.13, 4) | 5.5% | 0.722 | 0.836 | mercado ≫ apoyo |
| Hyde o1.5 (Seg B5) | 1.167 (1.15–1.20, 3) | 4.3% | 0.659 | 0.780 | 3 casas (mínimo) |
| Workington o2.5 (Amp B1,B4,B5) | 1.508 (1.45–1.65, 6) | 13.3% | 0.596 (9/10, 9/10) | 0.609 | DISPERSIÓN ALTA; aparece en 3 borradores |
| Fajr X2 (Amp B1,B2) | 1.673 (1.62–1.78, 3) | 9.6% | 0.566 (6/7, 7/7) | 0.550 (doc 0.272 ERROR) | media inflada por Betano; n=7 |
| Inter u5.5 / +2.5 (par) | 1.103 (1.08–1.16, 6) / 1.441 (1.40–1.50, 7) | 7.3% / 6.9% | 0.659 / 0.606 | 0.844 / 0.649 | par |
| Arsenal u5.5 / +2.5 (par) | 1.060 (1.04–1.09, 6) / 1.471 (1.40–1.52, 7) | 4.7% / 8.2% | 0.659 / 0.606 | 0.878 / 0.636 | par |
| Athletic-MG o1.5 | 1.374 (1.35–1.40, 7) | 3.6% | 0.606 (10/10, 8/10) | 0.675 | estable |
| Athletic-MG o2.5 tarjetas | 1.13 EST (sin casa) | – | 0.565 (8/9, 8/9) | no calculable (sin mercado) | ver sección 5 |
| Rot-Weiss Essen +2.5 (Amp B3) | 1.183 (1.16–1.23, 3) | 5.9% | 0.659 | 0.776 | 3 casas |
| Birmingham +1.5 vis. (Amp B3,B4) | 1.459 (1.41–1.53, 7) | 8.2% | 0.560 (10/10, 7/10) | 0.595 | overround de la línea 1.153 (anómalo, lo normal 1.05–1.10 en las demás): posible mezcla de líneas; precio dudoso |
| Leamington o1.5 (Amp B4) | 1.183 (1.17–1.21, 3) | 3.4% | 0.659 | 0.768 | 3 casas |
| Harju 12 (Amp B5) | 1.181 (1.07–1.25, 7) | 15.2% | 0.659 | 0.759 (doc 0.384 ERROR) | DISPERSIÓN ALTA (1.07 vs 1.25) |
| Orlando Pirates u5.5 (Amp B5) | 1.030 (1.01–1.04, 4) | 2.9% | 0.722 | 0.920 | paga ~nada; mercado ≫ apoyo (+0.20) |
| Orlando Pirates +2.5 (Amp B5) | 1.410 (1.38–1.45, 4) | 5.0% | 0.560 (7/10, 10/10) | 0.653 | 4 casas, Marathon=1xBet idénticas |

Patas donde el mercado paga claramente menos que el apoyo (precio ya incorporado, EV descriptivo muy negativo): todas las de «menos de 5.5/4.5» y «más de 1.5» de seguridad y amplio (Orlando u5.5 0.920 vs 0.722; Arsenal u5.5 0.878 vs 0.659; Inter u5.5 0.844 vs 0.659; Norrköping 0.839 vs 0.722; Gloucester 0.836 vs 0.722; Cardiff 0.752 vs 0.659). Ejemplo calc ev: Kyoto +2.5 EV descriptivo = −0.121; Fajr X2 −0.053; Inter +2.5 −0.127. Único caso con apoyo > sin margen: Fajr X2 (0.566 vs 0.550, dentro del ruido; n=7). El «top atractivo» (Kyoto +1.5: EV desc. +0.109 = 0.659×1.683−1) es el único positivo entre 8344 patas: efecto de seleccionar el máximo (maldición del ganador); además la frecuencia 10/10 + 9/10 con n=10 y sin ajuste de rival no demuestra ventaja. No hay probabilidad predictiva defendible: NO se calcula EV real.

### Limitación del apoyo repetido (0.659 / 0.722 / 0.606 / 0.596 / 0.56)
- [CALC] Wilson 95% inferior (calc freq): 10/10 = 0.722; 9/10 = 0.596; 8/10 = 0.490; 7/10 = 0.397; 7/7 = 0.646; 6/7 = 0.487; 8/9 = 0.565.
- El «apoyo» del script es la media de los límites inferiores de los dos equipos: 10/10+10/10 → 0.722; 10/10+9/10 → 0.659; 9/10+9/10 → 0.596; 10/10+8/10 → 0.606; 10/10+7/10 → 0.560. Es una escalera discreta: con n=10 el techo es 0.722 sin importar si la probabilidad real es 0.80 o 0.97. Por eso aparece 0.722 en las 15 filas de la lista «seguridad», y el ordenamiento «por apoyo» es, en la práctica, un ordenamiento por k (más una elección de mayor cuota a igual apoyo). No distingue «muy seguro» de «bastante seguro».
- Es la media de dos intervalos, no una probabilidad conjunta ni predictiva; muestra = últimos ≤10 partidos en 180 días de TODAS las competiciones (incluye copas, rivales de muy distinto nivel, casa y fuera mezclados, sin ajuste por rival ni categoría; verificado en la nota de la matriz y en las filas de forma, p. ej. Emperor Cup + J1 League para Kyoto). Los 10/10 de hándicap +2.5 de un visitante pueden deberse a que sus rivales recientes eran débiles o a que jugó en casa.
- El producto entre partidos supone independencia (no verificable; en la práctica la correlación entre partidos distintos del mismo día es baja pero no nula: arbitraje, misma liga).

## 3. Pares del mismo partido (misma casa, API del 2026-10-13)

Producto de la cuota «u5.5» × «hándicap visitante +2.5» por casa (calc combo). Marathon y 1xBet repiten precios exactos (una sola vía efectiva).

| Partido | Producto medias (doc) | Producto por casa (calc) | Cota inf. por correlación [EST] |
|---|---|---|---|
| Inter–Brugge | 1.589 | bet365 1.653 · Marathon/1xBet 1.555 · Betfair 1.512 · BetVictor 1.523 · Betano 1.740 | ≈1.44 (la pata hándicap sola) si u5.5 es casi redundante |
| Arsenal–Lille | 1.559 | bet365 1.620 · Marathon/1xBet 1.550 · Betfair 1.484 · BetVictor 1.502 · Betano 1.657 | ≈1.47 (hándicap solo) |
| Orlando–TS Galaxy | 1.452 | bet365 1.508 · 1xBet 1.421 (solo 2 casas con ambas patas; Betano/Betfair sin la otra) | ≈1.38–1.41 |
| Athletic-MG o1.5 + tarjetas | 1.553 | no verificable (tarjetas no existe en ninguna casa consultada: mercado/línea sin cuota) | – |

- [CALC] Fréchet con probabilidades sin margen (hándicap/u5.5): Inter conjunta ∈ [0.493, 0.649] → cuota justa entre 1.54 y 2.03 (independiente: 1.83); Arsenal [0.514, 0.636] → 1.57–1.95 (indep. 1.79); Pirates [0.573, 0.653] → 1.53–1.75 (indep. 1.66). Esto acota la cuota JUSTA, no la que ofrece la casa.
- [EST, hipótesis no verificada] Las dos patas están correlacionadas positivamente (la goleada local rompe a la vez ambas). Una casa que acepte la combinada (constructor de apuestas) suele pagar por debajo del producto; descuento supuesto 5–10% sobre el par (no hay dato en las fuentes permitidas). Rango plausible de cuota real del par: Inter ≈1.40–1.65, Arsenal ≈1.40–1.62, Pirates ≈1.28–1.45. Mercado «hándicap +2.5 + u5.5 del mismo partido» podría ni siquiera aceptarse como combinación en la casa (no verificable).
- Escenarios [CALC] sobre los borradores con descuento de 5% / 10% al par: Amp B1 3.809 / 3.609; B2 3.655 / 3.281; B3 3.834 / 3.632; B4 3.839 / 3.637; B5 3.640 / 3.267. Con precios de una sola casa (sin descuento): Amp B3 con Marathon/1xBet 3.949 (con Inter Marathon 1.5552) o con Betfair 3.839; Amp B1 con Marathon+Fajr 1.62: 3.799; Amp B5 con precios Marathon/1xBet: 3.923. Conclusión: ningún borrador «amplio» con pares seguiría en rango bajo el supuesto razonable de que la casa paga algo menos; seguirían en rango solo si la casa paga el producto íntegro y sus precios están por encima de la media (bet365/Betano).

## 4. Robustez ±3% por pata (calc combo con cada cuota ×0.97 y ×1.03; piso 1.01)

| Borr. | Nominal | ±3% por pata | Mín–máx de casas (todas las patas) | Margen a inferior: uniforme necesario | ¿Sale fácil? |
|---|---|---|---|---|---|
| Seg B1 | 1.217 | 1.180–1.254 | 1.190–1.270 | 1.4% | SÍ (2 de 3 casas pagan 1.19 → 1.19 < 1.20) |
| Seg B2 | 1.241 | 1.204–1.278 | 1.200–1.270 | 3.3% / 3.1% | NO (el más robusto; 7 casas) |
| Seg B3 | 1.234 | 1.197–1.271 | 1.160–1.270 | 2.8% | Algo (casa baja 1.16 sale; −3% roza 1.20) |
| Seg B4 | 1.212 | 1.141–1.286 | 1.145–1.288 | 0.5% por pata | SÍ (dos patas ~1.10; margen 1.0%) |
| Seg B5 | 1.276 | 1.200–1.353 | 1.230–1.356 | 3.0% por pata (inf.); supera 1.28 con +0.2% | Sale por arriba (inocuo para el pago); inferior solo roza 1.200 en −3% |
| Amp B1 | 4.009 | 3.550–4.513 | 3.552–5.110 | 0.06% por pata | SÍ |
| Amp B2 | 4.051 | 3.478–4.695 | 3.598–4.665 | 0.25% | SÍ |
| Amp B3 | 4.034 | 3.465–4.678 | 3.462–4.977 | 0.18% | SÍ |
| Amp B4 | 4.042 | 3.470–4.685 | 3.649–4.832 | 0.20% | SÍ |
| Amp B5 | 4.031 | 3.396–4.816 | 3.149–5.153 | 0.14% | SÍ |

Lectura: un ajuste uniforme de solo 0.06%–0.25% por pata a la baja saca a cada borrador «amplio» de 4.0. La selección del script prioriza mayor apoyo dentro del rango y termina todas las combinaciones pegadas al límite inferior; no deja colchón. El «rango plausible» aquí NO es una probabilidad: es un intervalo de sensibilidad. Salir por arriba (más de 4.8 o 1.28) no es un riesgo de pérdida, solo cambia el objetivo.

## 5. Cuota estimada de córners/tarjetas: método y advertencias

Método (tickets.py): p_est = (k1+k2+2)/(n1+n2+4) (frecuencia suavizada de ambos equipos), cuota = 1/(p_est·1.08), solo se conserva si 1.10 ≤ cuota ≤ 2.6.
- Es circular: la cuota sale de la misma frecuencia que el apoyo, así que NO es información de mercado. Decir «cuota aprox. 1.13» no indica que alguna casa pague 1.13.
- Inconsistente con el apoyo: usa la frecuencia suavizada (Athletic tarjetas 0.818) para fijar la cuota, pero el apoyo en la tabla es 0.565 (Wilson inferior). Si una casa pagara 1.13 de verdad, el EV descriptivo con el apoyo sería 0.565×1.13−1 = −0.36. La «cuota real mínima 1.77» (1/0.565) es la que haría falta, 57% más que la estimada.
- Supone margen 8% y línea fija 2.5/5.5 tarjetas A+R, que quizá no existe en la casa (los mercados suelen ser de tarjetas totales con otra línea, o puntos de reserva 10/25/40). La regla de liquidación (¿roja = 1 tarjeta?, ¿doble amarilla?) no está verificada. La muestra es n=9 por equipo, todas las competiciones, sin ajuste por árbitro ni rival.
- Efecto en los borradores: aporta 1.13 al multiplicador sin respaldo. Amp B2 y B4 sin la tarjeta: ≈3.58 (4.0503/1.13 y 4.0411/1.13, división) → fuera de rango. Además la pata de tarjetas reduce el apoyo conjunto del par (0.565 vs 0.606 de la pata de goles sola).
- Veredicto: [CALC] la cuota es un artificio de ordenación; el borrador que la use no tiene precio verificable. Sin cuota real, «sin valor económico confirmado» (regla del skill). No se calcula EV.

## 6. Tabla por borrador

| Borrador | Cuota recalc. | Rango plausible (sensibilidad) | Patas frágiles | Observación |
|---|---|---|---|---|
| Seg B1 Kyoto +2.5 | 1.217 | 1.18–1.25 (±3%); casas 1.19–1.27 | Kyoto (3 casas, 2 idénticas; precio modal 1.19 < 1.20) | Fuera de rango en Marathon/1xBet. Apoyo 0.722 vs sin margen 0.751 |
| Seg B2 Cardiff u4.5 | 1.241 | 1.204–1.278 | ninguna | Más robusto; 7 casas; apoyo 0.659 vs 0.752 |
| Seg B3 Bucaramanga 1X | 1.234 | 1.197–1.271; casas 1.16–1.27 | disp. 8.9% | En rango en casi todos; sin margen EV positivo; sin margen DC correcto 0.754 |
| Seg B4 Norrköping u5.5 + Simba 12 | 1.212 | 1.141–1.286 | ambas (cuotas bajas ~1.10; Simba 4 casas, 1X2 de 6) | Margen inf. 1.0%; dos patas para ganar ~21% |
| Seg B5 Gloucester o1.5 + Hyde o1.5 | 1.276 | 1.200–1.353 | Hyde (3 casas) | Margen inf. 6.3%; superior justo; ligas semiprofesionales, riesgo de calendario/datos |
| Amp B1 | 4.009 | 3.55–4.51; con descuento par y Fajr 1.62: ≈3.80–3.88 | Fajr (outlier), Workington (disp. 13%), par Inter | Margen 0.2% |
| Amp B2 | 4.051 | 3.48–4.70; sin tarjeta ≈3.58 | tarjeta EST, Fajr, 2 pares | Descartar |
| Amp B3 | 4.034 | 3.47–4.68; casa única 3.84–3.95; par −5% 3.83 | Birmingham (overround 1.153), par Inter, Arsenal +2.5, RW Essen (3 casas) | Sin cuota estimada; 5 patas/4 partidos |
| Amp B4 | 4.042 | 3.47–4.69; sin tarjeta ≈3.58 | tarjeta EST, Workington, Birmingham | Descartar |
| Amp B5 | 4.031 | 3.40–4.82; casa única ≈3.92 | Harju (disp. 15%), Workington (13%), 2 pares, Orlando u5.5 a 1.03 | 6 patas con dos pares casi sin pago: frágil |

Repeticiones de partido dentro del perfil «amplio» (un fallo hunde varios): Workington en B1, B4, B5; Arsenal en B2, B3, B5; Inter en B1, B3; Fajr en B1, B2; Athletic-MG en B2, B4; Birmingham en B3, B4.

## 7. Recomendación

Distinguir: lo calculado (cuotas, sensibilidad, sin margen) es fiable; lo estimado (descuento del par, rango de cuota real) es hipótesis; lo no verificable (si la casa acepta las combinadas, cuota real de córners/tarjetas, bajas) no se afirma.

Seguridad ×1.20–1.28 (de más a menos robusta numéricamente):
1. B2 Cardiff u4.5 (1.241): 7 casas, ±3% dentro de rango, una sola pata (sin correlación ni independencia que suponer). Apoyo 0.659 vs 0.752 de mercado: el precio ya recoge la seguridad; sin ventaja demostrada (alta probabilidad aparente, precio ajustado).
2. B5 (1.276): margen inferior 6.3% (aguanta ~3% por pata); riesgo adicional de dos ligas menores con 3–4 casas y apoyo conjunto 0.476 (independencia).
3. B3 Bucaramanga 1X (1.234): casi siempre en rango, pero el mínimo de casas 1.16 queda fuera.
4. B4 (1.212): dos patas cuotas ~1.10 con 1.0% de colchón.
5. B1 Kyoto +2.5 (1.217): descartar o exigir cuota ≥1.20 en la casa; 2 de las 3 casas pagan 1.19.

Amplio ×4.0–4.8 (todos al borde inferior; ninguno robusto; si hay que elegir):
1. B3 (4.034): sin cuota estimada, una sola casa 3.84–3.95 → casi seguro bajo 4.0 si hay descuento por pares; patas razonablemente repartidas (5 patas/4 partidos). Cuota de Birmingham (+1.5) a vigilar (overround 15%).
2. B1 (4.009): colchón 0.2% y depende de Fajr (precio modal 1.62 → ≈3.88 con pares) y Workington.
3. B5 (4.031): 6 patas, dos pares, patas a 1.03/1.06 de pago nulo; con precio de casa única ≈3.92.
4. Descartar por fragilidad numérica: B2 y B4 (cuota estimada de tarjetas no verificable; sin esa pata ≈3.58, fuera de 4.0).
Recomendación de fondo: si se desea un ×4.0–4.8 realista, reconstruir los borradores con un objetivo nominal de ~4.3–4.5 para que el rango se mantenga con −5%, en lugar de pegado a 4.0 (decisión del director; no se recalcula aquí).

## 8. Limitaciones y objeciones
- No hay probabilidad predictiva defendible (muestra ≤10, sin ajuste de rival, ligas mezcladas): «no estimable» → no se calcula EV real. Las comparaciones apoyo vs sin margen son descriptivas.
- Las cuotas son de un agregador (una sola vía): el nº de casas incluye duplicados (Marathon = 1xBet en las cuotas vistas) y no son ejecutables.
- El producto entre partidos asume independencia; por pares se usó el apoyo conjunto medido en los mismos partidos pasados (que da un conjunto mayor que el producto, pero con n=10).
- El descuento por combinada correlacionada (5–10%) es una hipótesis no verificada; no hay datos del constructor de apuestas.
- Sin verificar: bajas/alineaciones (Nivel 2 deportivo), hora de partido, disponibilidad real de cada mercado en la casa.
