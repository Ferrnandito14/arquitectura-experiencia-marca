Revisé el inventario contra los datos brutos sin usar red. Las horas, ventana, competición, estado y elegibilidad cuadran en los 240 registros. Los fallos están en la clasificación de categoría y en la lógica de la discrepancia.

## 1) JSON de revisión

```json
{"agent":"verificador-mercados","batch_id":"disc","rows":[
{"match_id":"m-fdb8c16844d5","review_status":"REVISADO","corrections":["calendar_verification_status: CONFIRMADO es excesivo; debería ser PARCIAL/una sola fuente con discrepancia de estado abierta (confirmation_basis dice 'sin_discrepancias' pero hay 1)","event_status DESCONOCIDO: el bruto dice 'upcoming' con inicio 2026-10-12T19:00Z ya pasado; mantener DESCONOCIDO es correcto, pero la nota debe indicar posible dato obsoleto de APWin"],"note":"Carrick Rangers U20 - Dungannon Swifts U20, premiership development league (Irlanda del Norte). Epoch 1791831600 = 2026-10-12T19:00Z = 15:00 Caracas, coincide con inventario. Categoría youth correcta (U20). Fuera de ventana (12-oct), NO_ELEGIBLE correcto. La discrepancia es real: 'programado' con hora pasada. Una sola fuente, sin segunda fuente permitida."},
{"match_id":"m-168f0da91be1","review_status":"REVISADO","corrections":["calendar_verification_status: CONFIRMADO es excesivo (igual que arriba); confirmation_basis contradice la lista de discrepancias","event_status DESCONOCIDO correcto; marcar como dato posiblemente obsoleto"],"note":"Deportivo Capiatá - Benjamin Aceval, division intermedia (Paraguay). Epoch 1791844200 = 2026-10-12T22:30Z = 18:30 Caracas, coincide. Categoría men correcta. Fuera de ventana, NO_ELEGIBLE correcto. Misma discrepancia 'programado' con hora pasada. Sin segunda fuente."}
]}
```

## 2) Muestra de control (12 registros)

La zona de football-data está inferida (Europe/London, `tz_confirmed=false`). Las dos discrepancias del lote no entran en esta muestra.

| match_id | Re-derivado | ¿Coincide? | Error |
|---|---|---|---|
| m-2e91a798c280 Newcastle Jets-Gamba Osaka (req.) | 07:45Z, 03:45 Caracas, en ventana, men, AFC CL, programado, elegible | Sí | No |
| m-8f866f457c46 Lens U19-Sporting U19 (req.) | 11:00Z, 07:00, en ventana, youth, UEFA Youth League, elegible | Sí | No |
| m-7172178569c0 Lens-Sporting (req.) | 16:45Z, 12:45, en ventana, men, UEFA Champions League, elegible | Sí | No |
| m-05f58afa45b9 Viking-Bayern (req.) | 19:00Z, 15:00, en ventana, men, elegible | Sí | No |
| m-295297ed3e94 Galatasaray-Barcelona (req.) | 19:00Z, 15:00, en ventana, men, elegible | Sí | No |
| m-5e288e8a1f72 Portimonense U23-Académico Viseu U23 (req.) | 10:00Z, 06:00, en ventana, youth, elegible | Sí | No |
| m-78cd6ef12c4d Heidenheim-Kaiserslautern (football-data) | "2026-10-09 17:30" Londres (BST) = 16:30Z = 12:30 Caracas, fuera de ventana, men | Sí | No |
| m-1c7355172d58 Celta B-Sociedad B (football-data) | 2026-10-10 20:00 Londres = 19:00Z = 15:00, fuera de ventana | Hora sí, categoría no | Se clasifica `men`, pero son filiales (debería ser `reserve`) |
| m-cfd5c650b0b3 Utrecht-Willem II (football-data) | 2026-10-11 11:15 Londres = 10:15Z = 06:15, fuera de ventana | Hora sí, categoría no | Se clasifica `reserve`, pero es Eredivisie masculina de primer equipo (falso positivo por "II") |
| m-edb93d04d67f HFX-Cavalry (APWin, fuera de ventana) | 20:00Z, 16:00, 12-oct, finished | Sí | No |
| m-7c6832ea1f03 Novorizontino-Ponte Preta (APWin, fuera de ventana) | 22:00Z, 18:00, 12-oct, finished | Hora y estado sí, categoría no | Se clasifica `reserve`, pero "serie b" es la segunda división brasileña de primer equipo |
| m-f7906dd61f99 All Boys-Godoy Cruz (APWin, fuera de ventana) | 22:00Z, 18:00, 12-oct, live | Sí | No (`men` es correcto; "Prim B Nacional" es segunda división) |

Más allá de la muestra, recalculé UTC, hora de Caracas, pertenencia a la ventana, equipos y competición para los 240 registros. El resultado fue 0 discrepancias (incluido el desfase BST/GMT de Londres y UTC-4 de Caracas). La ventana es [2026-10-13T04:00Z, 2026-10-14T04:00Z) y todo cae donde corresponde.

## 3) Hallazgos sistemáticos

- **Recuentos:** hay 41 registros brutos de APWin (41 únicos) y 199 de football-data (199 únicos), 0 duplicados internos y 0 fusiones entre fuentes. Resultan 240 únicos, y cada partido tiene una sola fuente. No hay competición vacía y no hay duplicados por equipos.
- **Clasificación `reserve` poco fiable:** los 14 `reserve` son falsos positivos. Son 10 de Serie B italiana, 3 de Serie B brasileña y Utrecht-Willem II (probablemente por "B" o "II" en el nombre). Además, Celta B-Sociedad B es un falso negativo. Los 15 requeridos no se ven afectados. Si un partido así cayera en la ventana, quedaría mal excluido o incluido.
- **Estado de football-data:** `event_status` queda DESCONOCIDO en los 199 registros, porque su CSV no trae estado. Todos son del 9 al 12 de octubre y ninguno cae en ventana, así que no aportan candidatos hoy.
- **Estado de APWin:** de sus 41 registros hay 33 `upcoming`, 6 `live` y 2 `finished`. Los 8 iniciados o finalizados están el 12-oct, fuera de ventana.
- **Etiqueta "CONFIRMADO" demasiado fuerte:** los 240 partidos figuran como CONFIRMADO con la base `una_fuente_estructurada_fiable_sin_discrepancias`. Esa base contradice las 2 discrepancias del lote. Además, los 240 tienen `selection_calendar_verification=REQUIERE_VERIFICACION_ADICIONAL`.
- **Los 15 requeridos:** los 15 son solo de APWin, con estado PROGRAMADO, dentro de ventana y sin discrepancias. El criterio "una fuente estructurada basta para entrar al universo pero no para selección final" se aplica bien: están elegibles para evaluación, ninguno pasa a selección y `REQUIERE_VERIFICACION_ADICIONAL` sigue activo. Coincide con el veredicto del informe de cobertura: 0 candidatos y 345 mercados no evaluables.
- **Lens-Sporting:** están bien separados. m-7172178569c0 es Lens-Sporting, Champions League, men, 16:45Z. m-8f866f457c46 es Lens U19-Sporting U19, UEFA Youth League, youth, 11:00Z. Ambos tienen IDs de APWin distintos, y no hay fusión. En el inventario aparecen otros dos "Lens" (Lens-Lyon y Mechelen-St Truiden) que no tienen relación con este cruce.
- **Cobertura temporal:** APWin solo cubre las páginas de 12, 13 y 14-oct (11, 15 y 15 registros), y es HTML público parcial. Los 15 de ventana son partidos de AFC CL, Champions, Youth League y Liga Revelação. Esto es un límite de cobertura del universo, no un error.

## 4) Registro de fuentes

| Fuente | URL o ficha | Dato buscado | Información obtenida | Fecha de consulta | Estado | Discrepancias | Alternativa consultada |
|---|---|---|---|---|---|---|---|
| football-data | `runs/2026-10-13/sources/raw_football-data.json` (origen `football-data.co.uk/fixtures.csv`, HTTP 200, 56330 bytes) | Hora, competición y estado de partidos de control | 199 registros leídos del archivo guardado; hora local del Reino Unido, sin estado | Lectura local de este run (descarga 2026-10-13 00:11Z, desde caché 00:13Z) | Consultada y útil (archivo local; sin red) | Zona inferida, sin confirmar | Ninguna |
| APWin | `runs/2026-10-13/sources/raw_apwin.json` (origen `apwin.com/?date=2026-10-12`, `-13` y `-14`, HTTP 200) | Época UTC, estado y competición | 41 registros leídos; los 2 de discrepancia dicen `upcoming` con hora pasada | Lectura local de este run (descarga 2026-10-13 00:12Z) | Consultada y útil (archivo local; sin red) | Estado desfasado en m-fdb8c16844d5 y m-168f0da91be1 | Ninguna permitida |
| Inventario, cobertura y política | `inventory.json`, `batches.json`, `coverage.json`, `coverage_report.md`, `consultas.jsonl`, `sources_policy.json` | Contraste del inventario con el bruto y política de hosts | Contrastado; 0 diferencias de hora, ventana, equipos y competición; errores de categoría detallados arriba | Lectura local de este run | Consultada y útil | Ver sección 3 | — |
| `docs/FUENTES-CONFORMIDAD.md` | `/home/user/football-picks-system/docs/FUENTES-CONFORMIDAD.md` | Criterios de zona horaria, discrepancias y categoría | Mi grep de esos términos no devolvió líneas; no la leí completa | Intento 2026-10-13 | Consultada con datos insuficientes | — | `sources_policy.json` |
| FotMob | `fotmob.com` | Calendario | No consultada, excluida por política (términos y robots) | — | No consultada — excluida por política | — | — |
| BetExplorer | `betexplorer.com` | Calendario y cuotas | No consultada, excluida por política | — | No consultada — excluida por política | — | — |
| Transfermarkt | `transfermarkt.com` | Bajas | No consultada, excluida por política | — | No consultada — excluida por política | — | — |
| Understat | `understat.com` | Datos avanzados | No consultada, excluida por política | — | No consultada — excluida por política | — | — |
| SoccerStats | `soccerstats.com` | Forma | No consultada, excluida por política (desafío anti-bot) | — | No consultada — excluida por política | — | — |
| Flashscore, Soccerway, SofaScore, OddsPortal y similares | — | Segunda fuente de calendario y cuotas | No consultadas: no están revisadas en la política, por lo tanto denegadas | — | No consultada — denegada por política | — | — |

## 5) Limitaciones

- No pude contrastar contra ninguna segunda fuente de horario o estado. Los 240 partidos tienen una sola fuente, y las dos discrepancias de estado no se pueden resolver sin red. Probablemente sea desfase de caché de APWin, pero no está confirmado.
- La zona horaria de football-data (Europe/London) sigue inferida y no confirmada.
- Los 15 requeridos quedan en estado **Parcial** como calendario: una sola fuente (APWin), sin fuente oficial ni segunda fuente. Ninguno es verificable como selección final.
- No verifiqué mercados, líneas ni cuotas; no hay cuotas actuales en el inventario, solo las B365 de football-data, que son históricas y no se aplican a los 15 requeridos.
- No leí `docs/FUENTES-CONFORMIDAD.md` completo, solo busqué términos con grep, y no devolvió nada.
- No escribí ningún archivo, aunque el modo plan estaba activo. La tarea era solo de lectura y el plan no era necesario.