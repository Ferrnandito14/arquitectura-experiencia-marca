Ninguna fila de b01–b04 tiene una corrección de datos en el partido, la competición, la categoría ni la hora. Lo que sí hay son dos incoherencias de estado y una salvedad sobre la razón de NO_EVALUABLE. No consulté ningún host por red: todo sale de los ficheros locales (`batches.json`, `inventory.json`, `matrix.json`, `state.json`, `coverage_report.md`, `sources_policy.json`, `docs/FUENTES-CONFORMIDAD.md`).

**Qué comprobé en las 15 filas**
- **Partido, competición y categoría:** los nombres, la competición, el país y la categoría de `inventory.json` coinciden con los del lote. Las categorías son "men" para AFC CL y UEFA CL, y "youth" para Liga Revelação U23 y UEFA Youth League.
- **Hora:** el timestamp de APWin (`original_datetime`) convertido a UTC coincide con `normalized_datetime_utc`. La hora local es UTC-4 (Caracas). Las 15 filas caen dentro de la ventana [04:00Z, 04:00Z+1d). La más temprana (m-2e91a798c280) es 03:45 local = 07:45Z. Tomo la zona UTC de APWin como declarada por el sistema (`confirmada: true`); no la verifiqué con otra fuente.
- **Estados en `inventory.json`:** las 15 filas tienen calendario CONFIRMADO, evento PROGRAMADO, elegibilidad ELEGIBLE, análisis PENDIENTE y `analysis_required` true.
- **Estados en `matrix.json` y `state.json`:** las 15 filas están en NO_EVALUABLE_TRAS_INTENTOS, con `evaluated_markets_ok` = 0, `form` vacío y 0 estadísticas. Cada fila tiene 6 intentos registrados (5 fuentes excluidas más Football-Data sin cobertura) y 23 mercados NO_EVALUABLE (345 en total) con precio null. No hay mezcla de datos de otro partido ni cifras inventadas.

**Hallazgos y correcciones propuestas**

| # | Hallazgo | Filas | Corrección propuesta |
|---|---|---|---|
| 1 | `inventory.json` marca `sports_analysis_status` y `market_analysis_status` como PENDIENTE y la disposición como "elegible para evaluación prepartido". En `state.json` y `matrix.json` ya figura NO_EVALUABLE_TRAS_INTENTOS. | Las 15 | Sincronizar el inventario con NO_EVALUABLE_TRAS_INTENTOS. `analysis_required` puede quedar true, pero el motivo debe quedar visible. |
| 2 | `calendar_verification_status` es CONFIRMADO con una sola fuente (APWin), pero `selection_calendar_verification` dice REQUIERE_VERIFICACION_ADICIONAL. Un lector podría tomar la hora como confirmada por doble fuente. | Las 15 | Mostrar en el informe "una fuente (APWin), hora sin contraste". Sin autorización del organizador (UEFA/AFC) u otro dato legítimo, no puede subir de nivel. |
| 3 | El texto "sin fuente permitida que aporte este dato para la liga" es cierto para este caso: de la política solo Football-Data es condicional y las demás fuentes están excluidas o no revisadas. Dos salvedades: (a) "sin cobertura" de Football-Data lo declara el propio sistema y yo no lo comprobé; (b) APWin es condicional pero solo con la portada `?date=`, que sirve de calendario y no de histórico. | Las 15 | Mantener NO_EVALUABLE. Añadir al motivo "fuentes no revisadas ⇒ denegadas, no 'inexistentes'". |
| 4 | Liga Revelação U23 está etiquetada "youth". Es sub-23 (cantera/reserva de clubes). | m-5e288e8a1f72 | Etiquetar como "reserva/sub-23" para no confundirla con juvenil (U19). Su cuota o estadística no es comparable con la del primer equipo. |

**Tipo de fuente legítima que haría falta, sin consultarla**

| Competición | Tipo de fuente | Estado en la política |
|---|---|---|
| AFC Champions League (4 partidos) | Sitio oficial del organizador (AFC) o API deportiva con licencia, para forma, bajas y alineaciones | NO REVISADA |
| UEFA Champions League (10 partidos) | UEFA.com oficial o API con licencia, más comunicados oficiales de los clubes para bajas | NO REVISADA |
| UEFA Youth League (1 partido) | UEFA.com oficial o datos aportados por el usuario | NO REVISADA |
| Liga Revelação U23 (1 partido) | Liga Portugal / FPF, API con licencia o datos aportados por el usuario | NO REVISADA |
| Comunes a todas | Calendario o CSV aportado por el usuario (`inventory.py --manual`) o autorización escrita del proveedor, para forma, bajas y alineaciones | No es host: es un dato aportado por el usuario |

FotMob, BetExplorer, Transfermarkt, Understat y SoccerStats están EXCLUIDAS. Flashscore, Soccerway, SofaScore, OddsPortal, Oddschecker, FootyStats, FBref, worldfootball.net y los sitios oficiales aparecen como NO REVISADA ⇒ denegada.

**Bloques por lote**

```json
{"agent":"analista-deportivo","batch_id":"b01","rows":[
{"match_id":"m-2e91a798c280","review_status":"REVISADO","corrections":["sincronizar inventory con NO_EVALUABLE_TRAS_INTENTOS","declarar calendario de una sola fuente (APWin)"],"note":"Newcastle Jets FC - Gamba Osaka, AFC CL, men, 03:45 local (07:45Z). Matriz coherente, sin estadísticas. Falta fuente oficial AFC o con licencia (NO REVISADA)."},
{"match_id":"m-2b3f5d6e6a5b","review_status":"REVISADO","corrections":["sincronizar inventory con NO_EVALUABLE_TRAS_INTENTOS","declarar calendario de una sola fuente (APWin)"],"note":"Pohang Steelers - Johor Darul Ta'zim, AFC CL, men, 06:00 local (10:00Z). Matriz coherente, sin estadísticas."},
{"match_id":"m-9e75e37d4b9d","review_status":"REVISADO","corrections":["sincronizar inventory con NO_EVALUABLE_TRAS_INTENTOS","declarar calendario de una sola fuente (APWin)"],"note":"Kyoto Sanga - Ratchaburi, AFC CL, men, 06:00 local (10:00Z). Matriz coherente, sin estadísticas."},
{"match_id":"m-ab313671331d","review_status":"REVISADO","corrections":["sincronizar inventory con NO_EVALUABLE_TRAS_INTENTOS","declarar calendario de una sola fuente (APWin)"],"note":"Shanghai SIPG - Daejeon Citizen, AFC CL, men, 06:00 local (10:00Z). Matriz coherente, sin estadísticas."}]}
```
```json
{"agent":"analista-deportivo","batch_id":"b02","rows":[
{"match_id":"m-5e288e8a1f72","review_status":"REVISADO","corrections":["sincronizar inventory con NO_EVALUABLE_TRAS_INTENTOS","declarar calendario de una sola fuente (APWin)","etiquetar categoría como reserva/sub-23, no juvenil"],"note":"Portimonense U23 - Academico Viseu U23, Liga Revelação U23, 06:00 local (10:00Z). Matriz coherente. Falta Liga Portugal/FPF o datos aportados por el usuario (NO REVISADA)."},
{"match_id":"m-7172178569c0","review_status":"REVISADO","corrections":["sincronizar inventory con NO_EVALUABLE_TRAS_INTENTOS","declarar calendario de una sola fuente (APWin)"],"note":"Lens - Sporting, UEFA CL, men, 12:45 local (16:45Z). Matriz coherente, sin estadísticas. Falta UEFA oficial o API con licencia (NO REVISADA)."},
{"match_id":"m-c237309e8e29","review_status":"REVISADO","corrections":["sincronizar inventory con NO_EVALUABLE_TRAS_INTENTOS","declarar calendario de una sola fuente (APWin)"],"note":"Sabah - Slavia Praha, UEFA CL, men, 12:45 local (16:45Z). Matriz coherente, sin estadísticas."},
{"match_id":"m-05f58afa45b9","review_status":"REVISADO","corrections":["sincronizar inventory con NO_EVALUABLE_TRAS_INTENTOS","declarar calendario de una sola fuente (APWin)"],"note":"Viking - Bayern München, UEFA CL, men, 15:00 local (19:00Z). Matriz coherente, sin estadísticas."}]}
```
```json
{"agent":"analista-deportivo","batch_id":"b03","rows":[
{"match_id":"m-0af946c9d2f0","review_status":"REVISADO","corrections":["sincronizar inventory con NO_EVALUABLE_TRAS_INTENTOS","declarar calendario de una sola fuente (APWin)"],"note":"RB Leipzig - PSV, UEFA CL, men, 15:00 local (19:00Z). Matriz coherente, sin estadísticas."},
{"match_id":"m-0f1b11fab280","review_status":"REVISADO","corrections":["sincronizar inventory con NO_EVALUABLE_TRAS_INTENTOS","declarar calendario de una sola fuente (APWin)"],"note":"Villarreal - Napoli, UEFA CL, men, 15:00 local (19:00Z). Matriz coherente, sin estadísticas."},
{"match_id":"m-11cf48aef451","review_status":"REVISADO","corrections":["sincronizar inventory con NO_EVALUABLE_TRAS_INTENTOS","declarar calendario de una sola fuente (APWin)"],"note":"Arsenal - Lille, UEFA CL, men, 15:00 local (19:00Z). Matriz coherente, sin estadísticas."},
{"match_id":"m-295297ed3e94","review_status":"REVISADO","corrections":["sincronizar inventory con NO_EVALUABLE_TRAS_INTENTOS","declarar calendario de una sola fuente (APWin)"],"note":"Galatasaray - Barcelona, UEFA CL, men, 15:00 local (19:00Z). Matriz coherente, sin estadísticas."}]}
```
```json
{"agent":"analista-deportivo","batch_id":"b04","rows":[
{"match_id":"m-d21f4803797c","review_status":"REVISADO","corrections":["sincronizar inventory con NO_EVALUABLE_TRAS_INTENTOS","declarar calendario de una sola fuente (APWin)"],"note":"Inter Milan - Club Brugge, UEFA CL, men, 15:00 local (19:00Z). Matriz coherente, sin estadísticas."},
{"match_id":"m-fd4f0f50a781","review_status":"REVISADO","corrections":["sincronizar inventory con NO_EVALUABLE_TRAS_INTENTOS","declarar calendario de una sola fuente (APWin)"],"note":"Atlético Madrid - Manchester United, UEFA CL, men, 15:00 local (19:00Z). Matriz coherente, sin estadísticas."},
{"match_id":"m-8f866f457c46","review_status":"REVISADO","corrections":["sincronizar inventory con NO_EVALUABLE_TRAS_INTENTOS","declarar calendario de una sola fuente (APWin)"],"note":"Lens U19 - Sporting U19, UEFA Youth League, youth, 07:00 local (11:00Z). Matriz coherente, sin estadísticas. Falta UEFA.com oficial o datos aportados por el usuario (NO REVISADA)."}]}
```

**Pendiente**
- **Contexto deportivo de los 15 partidos:** forma, bajas, alineaciones, motivación y H2H quedan sin evaluar. Ninguna fuente permitida los cubre y no los reconstruyo de memoria. Hace falta una de las fuentes de la tabla de arriba, previa revisión y alta en la política, o datos aportados por el usuario.
- **Hora de cada partido:** sigue con una sola fuente (APWin). Necesita contraste con un calendario oficial o aportado por el usuario.
- **Cuotas y mercados:** no hay precios ni disponibilidad en ninguna fila (todos NOT_CHECKED).
- **Football-Data:** su "sin cobertura" no lo pude comprobar de forma independiente.

**Registro de fuentes**

| Fuente | URL o ficha | Dato buscado | Información obtenida | Fecha de consulta | Estado | Discrepancias | Alternativa consultada |
|---|---|---|---|---|---|---|---|
| Ficheros locales del proyecto (archivos del sistema, no fuentes web) | `runs/2026-10-13/{batches,inventory,matrix,state}.json`, `coverage_report.md` | Partido, hora, estados, evaluación de Nivel 1 | Datos de los 15 partidos leídos; coherentes salvo los hallazgos 1–4 | 2026-10-13 | Consultada y útil | Estado PENDIENTE en `inventory.json` frente a NO_EVALUABLE en `matrix.json`/`state.json` | Ninguna |
| `sources_policy.json` y `docs/FUENTES-CONFORMIDAD.md` | `.claude/skills/seleccion-final-picks/scripts/sources_policy.json` | Qué hosts están permitidos | FotMob, BetExplorer, Transfermarkt, Understat y SoccerStats excluidas; Football-Data y APWin condicionales; el resto no revisadas, por tanto denegadas | 2026-10-13 | Consultada y útil | Ninguna | Ninguna |
| APWin | Portada con `?date=` | Hora de los 15 partidos | No consultada por mí; solo leí el dato ya almacenado en el inventario | 2026-10-13 | No consultada | Una sola fuente de calendario | Ninguna permitida |
| Football-Data | Ficheros CSV | Cobertura de AFC CL, UEFA CL, Youth League y Liga Revelação | No consultada; el "sin cobertura" figura en `state.json` | 2026-10-13 | No consultada | No verificado de forma independiente | Ninguna |
| FotMob, BetExplorer, Transfermarkt, Understat, SoccerStats | n/a | Forma, bajas, alineaciones | Excluidas por política | 2026-10-13 | No consultada | n/a | Ninguna |
| Flashscore, Soccerway, SofaScore, OddsPortal, Oddschecker, FootyStats, FBref, worldfootball.net, UEFA, AFC, Liga Portugal | n/a | Forma, bajas y calendario oficial | NO REVISADA ⇒ denegada | 2026-10-13 | No consultada | n/a | Datos aportados por el usuario o API con licencia |