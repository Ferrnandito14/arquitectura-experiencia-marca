# Informe de cobertura

| Métrica | Valor | Denominador / nota |
|---|---|---|
| Registros brutos por fuente | {'apifootball': 748, 'apwin': 313, 'football-data': 199} | duplicados dentro de fuente: 0 |
| Partidos únicos | 1012 | tras deduplicar |
| Partidos con calendario CONFIRMADO (según fuente estructurada) | 1009 | de 1012 únicos; con verificación SUFICIENTE para selección final: 243 |
| Partidos no confirmados | 3 | calendario: {'CONFIRMADO': 1009, 'FECHA_DISCREPANTE': 3} |
| Iniciados/finalizados | 189 | no elegibles prepartido (todas las causas): 690 |
| Requieren evaluación (confirmados y elegibles) | 319 | base de la cobertura |
| Con disposición registrada (con motivo y evidencia) | 319 | de 319 = 100.0% — de ellos: 0 solo proxy parcial, 34 sin ninguna consulta de datos, 272 evaluados de verdad |
| Hora/calendario de los requeridos | 190 de 319 con UNA sola fuente; 129 con verificación suficiente para selección final | «CONFIRMADO» significa sin discrepancias entre fuentes, no hora contrastada |
| Con al menos una consulta real de datos | 285 | de 319 |
| Con histórico de la MISMA competición de los dos equipos (apifootball, sin amistosos) | 138 | de 319; ≤10 partidos recientes, mezcla casa/fuera, sin ajustar por rival |
| Con HISTORIAL PROPIO MIXTO (apifootball: copas/otras competiciones etiquetadas; al menos un equipo sin 6 partidos de la misma competición) | 147 | de 319; muestra menos comparable |
| Con histórico de la MISMA liga (Football-Data) | 0 | de 319 |
| Solo con forma doméstica PROXY (otra competición): evaluación PARCIAL | 0 | de 319; no evalúa el partido |
| NO intentados (ningún adaptador de fuente permitida los cubre; no se comprobó si otra fuente permitida lo haría) | 34 | de 319 con disposición: «con disposición» no es «examinado» |
| Pendientes | 0 | [] |
| Mercados examinados | 6555 | de 7337 = 89.3% (NOT_CHECKED: 782); con historial propio del equipo: 6555; solo proxy de OTRA competición: 0 |
| Mercados con estadística descriptiva o cuota media (PARCIAL/EVALUABLE) | 2380 | con historial propio/misma liga: 2380; el resto es proxy de otra competición |
| Mercados NO_EVALUABLE (huecos: en proxies, la fuente abierta no trae ese dato o no es comparable) | 4175 | familias sin ningún mercado evaluable con historial propio o de la misma liga: [] |

**Veredicto de la puerta de cobertura: RANKING PROVISIONAL RESTRINGIDO — limitación sistémica: 34 partidos NO investigados (sin fuente permitida), 0 solo con forma doméstica proxy (parcial) y 13 con intento insuficiente; UNIVERSO TRUNCADO: apwin 2026-10-12: 11 accesibles de 15 declarados; apwin 2026-10-13: 167 accesibles de 172 declarados — los partidos contados son una cota inferior; nunca «la jornada completa»**

**⚠ UNIVERSO TRUNCADO: apwin 2026-10-12: 11 accesibles de 15 declarados; apwin 2026-10-13: 167 accesibles de 172 declarados — los partidos contados son una cota inferior; nunca «la jornada completa».** Nada de lo que sigue puede describirse como «la jornada completa».

**Qué NO se sostiene con este resultado:**
- Hay 2380 mercados con estadística descriptiva PARCIAL (de partidos de otra competición cuando es proxy), pero ningún candidato evaluado, ninguna probabilidad, cuota ni EV para los 319 partidos requeridos.
- 782 mercados están NOT_CHECKED (no investigados): eso no prueba que el mercado no exista ni que la estadística sea 0.
- No se sostiene ninguna selección por valor ni «alta probabilidad»; cualquier orden entre partidos sería criterio cualitativo sin valor económico confirmado.
- No hay histórico de la misma competición ajustado por rival, árbitro designado, bajas ni cuotas ejecutables de una casa concreta para estos partidos; el historial propio es descriptivo y el proxy doméstico no sustituye esos datos.
- El calendario de cada partido proviene de una sola fuente: no basta para una selección final (`selection_calendar_verification`).
- Para levantar la restricción faltan, según el caso: partidos sin cobertura de la API, bajas/alineaciones, cuotas ejecutables de la casa de la persona usuaria y contraste de Nivel 2.
