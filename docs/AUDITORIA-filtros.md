# Auditoría de los filtros del sistema

Patas liquidadas (lado favorecido por el modelo, cuota ≤ 2.10): **1158** en 2 día(s): 2026-10-14, 2026-10-15.

Exceso = frecuencia real − probabilidad media del modelo (en puntos porcentuales). Un filtro es útil si lo que CONSERVA tiene más exceso que lo que DESCARTA con IC 95 % que excluye 0.

| Filtro | Conserva (n) | Descarta (n) | Acierto conserva | Acierto descarta | Exceso conserva | Exceso descarta | Dif. [IC 95 %] | Veredicto |
|---|---|---|---|---|---|---|---|---|
| Estado de agentes: aprobada (frente al resto) | 63 | 1095 | — | — | — | — | — | muestra insuficiente |
| Agentes: no rechazada ni degradada (frente a rechazadas y degradadas) | 309 | 849 | 70.2 | 68.9 | -2.0 | -3.86 | [-5.59, 9.21] | no concluyente |
| Agentes: no degradada por el deportivo (BAJA) | 678 | 480 | 72.6 | 64.6 | -0.03 | -8.07 | [1.4, 14.01] | útil (separa) |
| Agentes: no rechazada | 789 | 369 | 66.8 | 74.5 | -5.69 | 1.62 | [-13.66, -1.37] | contraproducente (descarta patas mejores) |
| Elegible para combinadas | 277 | 881 | 71.8 | 68.4 | -1.52 | -3.94 | [-5.88, 10.9] | no concluyente |
| Precio real o de referencia con casas (frente a sin precio verificable) | 1158 | 0 | — | — | — | — | — | muestra insuficiente |

Lectura: «no concluyente» significa que con estos días no se puede afirmar que el filtro ayude ni que estorbe; el registro sigue creciendo (cada día liquidado se añade con `comparativo_resultados.py --ledger`).
