# Informe de cobertura

| Métrica | Valor | Denominador / nota |
|---|---|---|
| Registros brutos por fuente | {'apifootball': 748, 'apwin': 313, 'football-data': 199} | duplicados dentro de fuente: 0 |
| Partidos únicos | 1017 | tras deduplicar |
| Partidos con calendario CONFIRMADO (según fuente estructurada) | 1014 | de 1017 únicos; con verificación SUFICIENTE para selección final: 238 |
| Partidos no confirmados | 3 | calendario: {'CONFIRMADO': 1014, 'FECHA_DISCREPANTE': 3} |
| Iniciados/finalizados | 189 | no elegibles prepartido (todas las causas): 693 |
| Requieren evaluación (confirmados y elegibles) | 321 | base de la cobertura |
| Con disposición registrada (con motivo y evidencia) | 321 | de 321 = 100.0% — de ellos: 0 solo proxy parcial, 36 sin ninguna consulta de datos, 281 evaluados de verdad |
| Hora/calendario de los requeridos | 194 de 321 con UNA sola fuente; 127 con verificación suficiente para selección final | «CONFIRMADO» significa sin discrepancias entre fuentes, no hora contrastada |
| Con al menos una consulta real de datos | 285 | de 321 |
| Con HISTORIAL PROPIO de los dos equipos (apifootball, todas sus competiciones, etiquetadas; NO es la misma competición) | 285 | de 321; muestra ≤10 partidos recientes, mezcla casa/fuera, sin ajustar por rival |
| Con histórico de la MISMA liga (Football-Data) | 0 | de 321 |
| Solo con forma doméstica PROXY (otra competición): evaluación PARCIAL | 0 | de 321; no evalúa el partido |
| NO intentados (ningún adaptador de fuente permitida los cubre; no se comprobó si otra fuente permitida lo haría) | 36 | de 321 con disposición: «con disposición» no es «examinado» |
| Pendientes | 0 | [] |
| Mercados examinados | 6555 | de 7383 = 88.8% (NOT_CHECKED: 828); con historial propio del equipo: 6555; solo proxy de OTRA competición: 0 |
| Mercados con estadística descriptiva o cuota media (PARCIAL/EVALUABLE) | 2486 | con historial propio/misma liga: 2486; el resto es proxy de otra competición |
| Mercados NO_EVALUABLE (huecos: en proxies, la fuente abierta no trae ese dato o no es comparable) | 4069 | familias sin ningún mercado evaluable con historial propio o de la misma liga: [] |

**Veredicto de la puerta de cobertura: RANKING PROVISIONAL RESTRINGIDO — limitación sistémica: 36 partidos NO investigados (sin fuente permitida), 0 solo con forma doméstica proxy (parcial) y 4 con intento insuficiente; UNIVERSO TRUNCADO: apwin 2026-10-12: 11 accesibles de 15 declarados; apwin 2026-10-13: 167 accesibles de 172 declarados — los partidos contados son una cota inferior; nunca «la jornada completa»**

**⚠ UNIVERSO TRUNCADO: apwin 2026-10-12: 11 accesibles de 15 declarados; apwin 2026-10-13: 167 accesibles de 172 declarados — los partidos contados son una cota inferior; nunca «la jornada completa».** Nada de lo que sigue puede describirse como «la jornada completa».

**Qué NO se sostiene con este resultado:**
- Hay 2486 mercados con estadística descriptiva PARCIAL (de partidos de otra competición cuando es proxy), pero ningún candidato evaluado, ninguna probabilidad, cuota ni EV para los 321 partidos requeridos.
- 828 mercados están NOT_CHECKED (no investigados): eso no prueba que el mercado no exista ni que la estadística sea 0.
- No se sostiene ninguna selección por valor ni «alta probabilidad»; cualquier orden entre partidos sería criterio cualitativo sin valor económico confirmado.
- No hay histórico de la misma competición ajustado por rival, árbitro designado, bajas ni cuotas ejecutables de una casa concreta para estos partidos; el historial propio es descriptivo y el proxy doméstico no sustituye esos datos.
- El calendario de cada partido proviene de una sola fuente: no basta para una selección final (`selection_calendar_verification`).
- Para levantar la restricción faltan, según el caso: partidos sin cobertura de la API, bajas/alineaciones, cuotas ejecutables de la casa de la persona usuaria y contraste de Nivel 2.
