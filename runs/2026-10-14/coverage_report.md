# Informe de cobertura

| Métrica | Valor | Denominador / nota |
|---|---|---|
| Registros brutos por fuente | {'apifootball': 676, 'apwin': 364, 'football-data': 14} | duplicados dentro de fuente: 0 |
| Partidos únicos | 790 | tras deduplicar |
| Partidos con calendario CONFIRMADO (según fuente estructurada) | 786 | de 790 únicos; con verificación SUFICIENTE para selección final: 257 |
| Partidos no confirmados | 4 | calendario: {'CONFIRMADO': 786, 'FECHA_DISCREPANTE': 4} |
| Iniciados/finalizados | 297 | no elegibles prepartido (todas las causas): 509 |
| Requieren evaluación (confirmados y elegibles) | 277 | base de la cobertura |
| Con disposición registrada (con motivo y evidencia) | 277 | de 277 = 100.0% — de ellos: 0 solo proxy parcial, 33 sin ninguna consulta de datos, 243 evaluados de verdad |
| Hora/calendario de los requeridos | 178 de 277 con UNA sola fuente; 99 con verificación suficiente para selección final | «CONFIRMADO» significa sin discrepancias entre fuentes, no hora contrastada |
| Con al menos una consulta real de datos | 244 | de 277 |
| Con histórico de la MISMA competición de los dos equipos (apifootball, sin amistosos) | 122 | de 277; ≤10 partidos recientes, mezcla casa/fuera, sin ajustar por rival |
| Con HISTORIAL PROPIO MIXTO (apifootball: copas/otras competiciones etiquetadas; al menos un equipo sin 6 partidos de la misma competición) | 119 | de 277; muestra menos comparable |
| Con histórico de la MISMA liga (Football-Data) | 3 | de 277 |
| Solo con forma doméstica PROXY (otra competición): evaluación PARCIAL | 0 | de 277; no evalúa el partido |
| NO intentados (ningún adaptador de fuente permitida los cubre; no se comprobó si otra fuente permitida lo haría) | 33 | de 277 con disposición: «con disposición» no es «examinado» |
| Pendientes | 0 | [] |
| Mercados examinados | 5612 | de 6371 = 88.1% (NOT_CHECKED: 759); con historial propio del equipo: 5543; solo proxy de OTRA competición: 0 |
| Mercados con estadística descriptiva o cuota media (PARCIAL/EVALUABLE) | 2146 | con historial propio/misma liga: 2146; el resto es proxy de otra competición |
| Mercados NO_EVALUABLE (huecos: en proxies, la fuente abierta no trae ese dato o no es comparable) | 3466 | familias sin ningún mercado evaluable con historial propio o de la misma liga: [] |

**Veredicto de la puerta de cobertura: RANKING PROVISIONAL RESTRINGIDO — limitación sistémica: 33 partidos NO investigados (sin fuente permitida), 0 solo con forma doméstica proxy (parcial) y 1 con intento insuficiente; UNIVERSO TRUNCADO: apwin 2026-10-13: 154 accesibles de 167 declarados; apwin 2026-10-15: 75 accesibles de 76 declarados — los partidos contados son una cota inferior; nunca «la jornada completa»**

**⚠ UNIVERSO TRUNCADO: apwin 2026-10-13: 154 accesibles de 167 declarados; apwin 2026-10-15: 75 accesibles de 76 declarados — los partidos contados son una cota inferior; nunca «la jornada completa».** Nada de lo que sigue puede describirse como «la jornada completa».

**Qué NO se sostiene con este resultado:**
- Hay 2146 mercados con estadística descriptiva PARCIAL (de partidos de otra competición cuando es proxy), pero ningún candidato evaluado, ninguna probabilidad, cuota ni EV para los 277 partidos requeridos.
- 759 mercados están NOT_CHECKED (no investigados): eso no prueba que el mercado no exista ni que la estadística sea 0.
- No se sostiene ninguna selección por valor ni «alta probabilidad»; cualquier orden entre partidos sería criterio cualitativo sin valor económico confirmado.
- No hay histórico de la misma competición ajustado por rival, árbitro designado, bajas ni cuotas ejecutables de una casa concreta para estos partidos; el historial propio es descriptivo y el proxy doméstico no sustituye esos datos.
- El calendario de cada partido proviene de una sola fuente: no basta para una selección final (`selection_calendar_verification`).
- Para levantar la restricción faltan, según el caso: partidos sin cobertura de la API, bajas/alineaciones, cuotas ejecutables de la casa de la persona usuaria y contraste de Nivel 2.
