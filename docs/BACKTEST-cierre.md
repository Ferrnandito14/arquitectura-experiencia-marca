# Backtest del modelo propio contra cuotas de cierre (TheStatsAPI)

Generado: 2026-10-15T17:19:06Z · partidos con cuotas: 1362 · predicciones emparejadas: 18409 · corte de la recalibración: 2026-07-26

Cierre aproximado = último precio visto; probabilidad del mercado sin margen, mediana entre casas. Cada partido se predice solo con partidos anteriores de su liga. Diferencias = modelo − mercado (negativo = el modelo predice mejor).

| Familia | Partidos | Brier modelo | Brier recalibrado | Brier mercado | Dif. modelo [IC 95 %] | Dif. recalibrado [IC 95 %] | Frente al mercado |
|---|---|---|---|---|---|---|---|
| 1x2 | 1362 | 0.2087 | 0.2084 | 0.1987 | +0.0100 [+0.0069, +0.0133] | [+0.0066, +0.0129] | peor |
| btts | 1297 | 0.2445 | 0.2396 | 0.2392 | +0.0053 [+0.0012, +0.0091] | [-0.0025, +0.0036] | peor |
| corners_total | 1181 | 0.2466 | 0.2451 | 0.2419 | +0.0048 [-0.0003, +0.0098] | [-0.0002, +0.0067] | no_concluyente |
| dc | 1362 | 0.2162 | 0.216 | 0.2024 | +0.0138 [+0.0093, +0.0182] | [+0.0091, +0.0180] | peor |
| goals_total | 1297 | 0.2107 | 0.2097 | 0.2022 | +0.0084 [+0.0051, +0.0117] | [+0.0044, +0.0105] | peor |
| team_goals | 1228 | 0.2045 | 0.204 | 0.1966 | +0.0078 [+0.0051, +0.0107] | [+0.0048, +0.0102] | peor |

## Mezcla modelo/mercado (peso elegido en la 1.ª mitad, medido en la 2.ª)

| Familia | Peso del modelo | Brier mezcla | Brier mercado | Brier modelo recal. |
|---|---|---|---|---|
| 1x2 | 0.0 | 0.1942 | 0.1942 | 0.2047 |
| btts | 0.0 | 0.2412 | 0.2412 | 0.2387 |
| corners_total | 0.1 | 0.2423 | 0.2424 | 0.2453 |
| dc | 0.0 | 0.1973 | 0.1973 | 0.2116 |
| goals_total | 0.0 | 0.2033 | 0.2033 | 0.2093 |
| team_goals | 0.1 | 0.1953 | 0.1952 | 0.2029 |

## ROI de las selecciones donde el modelo (recalibrado) ve ventaja sobre el mercado (cuota mediana de cierre, 1 u por selección)

| Familia | Ventaja | n | ROI | IC 95 % |
|---|---|---|---|---|
| 1x2 | ventaja>=3pp | 1395 | -0.113 | [-0.2024, -0.0204] |
| 1x2 | ventaja>=5pp | 1057 | -0.0865 | [-0.1949, 0.0198] |
| btts | ventaja>=3pp | 571 | 0.0415 | [-0.0351, 0.1144] |
| btts | ventaja>=5pp | 400 | 0.0397 | [-0.0489, 0.132] |
| corners_total | ventaja>=3pp | 421 | -0.0319 | [-0.1511, 0.0865] |
| corners_total | ventaja>=5pp | 255 | -0.0209 | [-0.1689, 0.1405] |
| goals_total | ventaja>=3pp | 1278 | -0.0658 | [-0.1448, 0.0197] |
| goals_total | ventaja>=5pp | 963 | -0.0686 | [-0.1591, 0.0335] |
| team_goals | ventaja>=3pp | 1870 | -0.0279 | [-0.0819, 0.0261] |
| team_goals | ventaja>=5pp | 1466 | -0.011 | [-0.0736, 0.0498] |

## Lectura

Familias donde el modelo no es peor que el mercado: ninguna. Familias donde es peor con IC que excluye 0: 1x2, btts, dc, goals_total, team_goals. Con la recalibración (parámetros ajustados antes del corte) la diferencia con el mercado ya no se distingue de cero en: btts, corners_total (no es lo mismo que superarlo: la mezcla óptima da casi todo el peso al mercado). El mercado incorpora información (alineaciones, lesiones, dinero) que el modelo no ve; una mezcla solo se aplicaría con el peso medido aquí y el sistema no depende de ninguna casa, así que los pesos se guardan como evidencia y no se usan en producción.

Limitaciones: es un cierre aproximado (último precio visto, no siempre el cierre real); la muestra de partidos con cuotas es un subconjunto del periodo y de las ligas; las tarjetas no se contrastan porque la definición de la fuente no está confirmada.
