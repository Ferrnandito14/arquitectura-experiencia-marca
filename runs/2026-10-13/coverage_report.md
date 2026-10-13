# Informe de cobertura

| Métrica | Valor | Denominador / nota |
|---|---|---|
| Registros brutos por fuente | {'apwin': 41, 'football-data': 199} | duplicados dentro de fuente: 0 |
| Partidos únicos | 240 | tras deduplicar |
| Partidos confirmados | 240 | de 240 únicos |
| Partidos no confirmados | 0 | calendario: {'CONFIRMADO': 240} |
| Iniciados/finalizados | 8 | no elegibles prepartido (todas las causas): 225 |
| Requieren evaluación (confirmados y elegibles) | 15 | base de la cobertura |
| Con disposición registrada (evaluado, no evaluable tras intentos, o no investigado por falta de fuente permitida; con motivo y evidencia) | 15 | de 15 = 100.0% |
| Hora/calendario de los requeridos | 15 de 15 con UNA sola fuente; 0 con verificación suficiente para selección final | «CONFIRMADO» significa sin discrepancias entre fuentes, no hora contrastada |
| Con al menos una consulta real de datos | 0 | de 15 |
| Evaluados suficientemente (histórico obtenido) | 0 | de 15 |
| Procesados SIN ninguna consulta real de datos (ninguna fuente permitida los cubre) | 15 | de 15 procesados: «procesado» no es «examinado» |
| Pendientes | 0 | [] |
| Mercados examinados | 0 | de 345 = 0.0% (NOT_CHECKED: 345) |
| Mercados con evaluación parcial/evaluable (candidatos) | 0 | |
| Mercados no evaluables | 0 | familias sin ningún mercado evaluable: ['resultado', 'goles', 'corners', 'tarjetas', 'otros'] |

**Veredicto de la puerta de cobertura: RANKING PROVISIONAL RESTRINGIDO — limitación sistémica: familias sin ningún mercado evaluable ['resultado', 'goles', 'corners', 'tarjetas', 'otros']; 15 partidos sin histórico suficiente**

**Qué NO se sostiene con este resultado:**
- No hay candidatos evaluados (0 mercados con datos), ni k/n, probabilidad, cuota o EV para los 15 partidos requeridos.
- 345 mercados están NOT_CHECKED (no investigados): eso no prueba que el mercado no exista ni que la estadística sea 0.
- No se sostiene ninguna selección por valor ni «alta probabilidad»; cualquier orden entre partidos sería criterio cualitativo sin valor económico confirmado.
- No hay histórico, córners, tarjetas, árbitro, bajas ni cuotas de ninguna casa para estos partidos.
- El calendario de cada partido proviene de una sola fuente: no basta para una selección final (`selection_calendar_verification`).
- Para levantar la restricción hace falta una fuente que cubra estas competiciones **obtenida de forma legítima** (API con licencia, datos aportados por el usuario, permiso del proveedor).
