# Informe de cobertura

| Métrica | Valor | Denominador / nota |
|---|---|---|
| Registros brutos por fuente | {'apwin': 313, 'football-data': 199} | duplicados dentro de fuente: 0 |
| Partidos únicos | 512 | tras deduplicar |
| Partidos con calendario CONFIRMADO (según fuente estructurada) | 512 | de 512 únicos; con verificación SUFICIENTE para selección final: 0 |
| Partidos no confirmados | 0 | calendario: {'CONFIRMADO': 512} |
| Iniciados/finalizados | 12 | no elegibles prepartido (todas las causas): 346 |
| Requieren evaluación (confirmados y elegibles) | 166 | base de la cobertura |
| Con disposición registrada (con motivo y evidencia) | 166 | de 166 = 100.0% — de ellos: 7 solo proxy parcial, 159 sin ninguna consulta de datos, 0 evaluados de verdad |
| Hora/calendario de los requeridos | 166 de 166 con UNA sola fuente; 0 con verificación suficiente para selección final | «CONFIRMADO» significa sin discrepancias entre fuentes, no hora contrastada |
| Con al menos una consulta real de datos | 7 | de 166 |
| Evaluados suficientemente (histórico de la MISMA competición) | 0 | de 166 |
| Solo con forma doméstica PROXY (otra competición): evaluación PARCIAL | 7 | de 166; no evalúa el partido |
| NO intentados (ningún adaptador de fuente permitida los cubre; no se comprobó si otra fuente permitida lo haría) | 159 | de 166 con disposición: «con disposición» no es «examinado» |
| Pendientes | 0 | [] |
| Mercados examinados | 161 | de 3818 = 4.2% (NOT_CHECKED: 3657); **de la MISMA competición: 0 (0 %)**; los otros 161 son solo proxy de OTRA competición |
| Mercados con estadística descriptiva PARCIAL (EVALUABLES de la misma competición: 0) | 63 | el resto es proxy descriptivo de otra competición, no candidatos |
| Mercados NO_EVALUABLE (huecos: en proxies, la fuente abierta no trae ese dato o no es comparable) | 98 | familias sin ningún mercado evaluable **de la misma competición**: ['resultado', 'goles', 'corners', 'tarjetas', 'otros'] |

**Veredicto de la puerta de cobertura: RANKING PROVISIONAL RESTRINGIDO — limitación sistémica: familias sin ningún mercado evaluable ['resultado', 'goles', 'corners', 'tarjetas', 'otros']; 159 partidos NO investigados (sin fuente permitida), 7 solo con forma doméstica proxy (parcial) y 0 con intento insuficiente; UNIVERSO TRUNCADO: apwin 2026-10-12: 11 accesibles de 15 declarados; apwin 2026-10-13: 167 accesibles de 172 declarados — los partidos contados son una cota inferior; nunca «la jornada completa»**

**⚠ UNIVERSO TRUNCADO: apwin 2026-10-12: 11 accesibles de 15 declarados; apwin 2026-10-13: 167 accesibles de 172 declarados — los partidos contados son una cota inferior; nunca «la jornada completa».** Nada de lo que sigue puede describirse como «la jornada completa».

**Qué NO se sostiene con este resultado:**
- Hay 63 mercados con estadística descriptiva PARCIAL (de partidos de otra competición cuando es proxy), pero ningún candidato evaluado, ninguna probabilidad, cuota ni EV para los 166 partidos requeridos.
- 3657 mercados están NOT_CHECKED (no investigados): eso no prueba que el mercado no exista ni que la estadística sea 0.
- No se sostiene ninguna selección por valor ni «alta probabilidad»; cualquier orden entre partidos sería criterio cualitativo sin valor económico confirmado.
- No hay histórico de la misma competición, árbitro designado, bajas ni cuotas de ninguna casa para estos partidos; el proxy doméstico no sustituye esos datos.
- El calendario de cada partido proviene de una sola fuente: no basta para una selección final (`selection_calendar_verification`).
- Para levantar la restricción hace falta una fuente que cubra estas competiciones **obtenida de forma legítima** (API con licencia, datos aportados por el usuario, permiso del proveedor).
