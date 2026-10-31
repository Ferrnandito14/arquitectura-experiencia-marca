# Reglas de liquidación de la casa de Fernando (confirmadas por él)

- **Total de goles «Más de 1.25»** (31-oct-2026): con exactamente 1 gol se devuelve lo apostado y la combinada NO se cae (la pata queda a cuota 1.00); con 2+ goles gana; con 0 goles pierde. No es el reparto asiático estándar (media pérdida con 1 gol): no aplicar `p_ah`/cuarto de línea estándar a esta casa sin confirmarlo para otras líneas (.25/.75).
- **«PA» (pago anticipado) en 1X2:** se liquida como ganado cuando el equipo llega a diferencia de 2 o más goles, aunque el partido termine distinto.
- Pendiente: comprobar si `seguimiento.py` y el comparativo liquidan las líneas .25/.75 de la casa con esta regla (hoy usan la estándar) y si el PA se refleja en los resultados registrados.
