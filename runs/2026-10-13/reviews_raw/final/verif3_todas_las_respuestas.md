Plan mode está activo. Mi tarea es solo lectura, así que sigo con análisis de solo lectura sin escribir archivos.

=====

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

=====

RESPUESTA
1. Acepto la corrección de categoría. La nueva muestra de 12 coincide en todo, salvo que solo hay un filial y un "Willem II", así que esos dos son repeticiones de la ronda 1 (ver EVIDENCIA).
2. El recuento ahora es men 236, youth 2, u23 1, reserve 1, total 240. Ningún Serie B ni Willem II queda como reserve. Los 14 equipos de Serie B/Willem II que listé salen todos `men`. El único reserve es Celta B–Sociedad B.
3. Sobre mi hallazgo "CONFIRMADO excesivo", acepto tu objeción sin cambiar el vocabulario de estados. CONFIRMADO se refiere a la hora de la fuente estructurada, que sí cuadra con el bruto. La discrepancia de estado queda aislada por tres señales: la base `…con_discrepancias_abiertas` (2 de 240), `event_status=DESCONOCIDO` y `NO_ELEGIBLE`. Los 2 casos tienen las tres señales y todos los demás tienen 0. Mantengo una condición: ningún consumidor aguas abajo debe leer CONFIRMADO como estado fiable. La regla debe ser que `event_status` o `discrepancies` mandan sobre `calendar_verification_status`.

EVIDENCIA
- Rederivé desde `raw_*.json` los 240 registros (APWin por época UTC, football-data por Europe/London, Caracas UTC-4). Hay 0 diferencias en hora UTC, hora local y pertenencia a ventana.
- Los 15 requeridos son los mismos partidos, con IDs nuevos, todos dentro de ventana, PROGRAMADO y elegibles.
- La muestra de 12 (Serie B marcado con ★):

| match_id | Partido | UTC / Caracas | Categoría | Disposición |
|---|---|---|---|---|
| m-d6485f2a1ef5 | Padova–Carrarese ★ | 10-11 15:15Z / 11:15 | men | NO_ELEGIBLE |
| m-4d9ba653d889 | Modena–Verona ★ | 10-11 17:30Z / 13:30 | men | NO_ELEGIBLE |
| m-b3d313d29378 | Criciúma–América Mineiro (Serie B Brasil) ★ | 10-12 22:30Z / 18:30 | men | NO_ELEGIBLE |
| m-651d68643a19 | Botafogo-SP–Ceará (Serie B Brasil) ★ | 10-13 00:00Z / 20:00 | men | NO_ELEGIBLE |
| m-335ca18cbb61 | Celta B–Sociedad B (filial) | 10-10 19:00Z / 15:00 | reserve | NO_ELEGIBLE |
| m-c8a85965e9b5 | Utrecht–Willem II ("II") | 10-11 10:15Z / 06:15 | men | NO_ELEGIBLE |
| m-8341c193f7a4 | Carrick Rangers U20–Dungannon Swifts U20 | 10-12 19:00Z / 15:00 | youth | NO_ELEGIBLE |
| m-35e4ea1f40c1 | Arsenal–Leeds | 10-10 11:30Z / 07:30 | men | NO_ELEGIBLE |
| m-652b82fc3ca3 | Pohang Steelers–Johor Darul Ta'zim (requerido) | 10-13 10:00Z / 06:00 | men | elegible |
| m-23a8afef592b | Portimonense U23–Académico Viseu U23 (requerido) | 10-13 10:00Z / 06:00 | u23 | elegible |
| m-d89de9c16489 | Sabah–Slavia Praha (requerido) | 10-13 16:45Z / 12:45 | men | elegible |
| m-26124a15db3b | Atlético Madrid–Manchester United (requerido) | 10-13 19:00Z / 15:00 | men | elegible |

- Arsenal–Lille (m-fa26ce1cb71b) también es requerido y coincide: 10-13 19:00Z, 15:00, men, elegible.
- El `confirmation_basis` ya termina en `_con_discrepancias_abiertas` en los 2 casos (los mismos Carrick Rangers U20 y Deportivo Capiatá, con IDs nuevos).

CAMBIO EN MI ESTADO
- Las filas del lote `disc` pasan a REVISADO sin correcciones pendientes en categoría, base ni vocabulario de estados.
- Limitación abierta: solo hay una fuente por partido, y los 15 requeridos siguen en "Parcial" como calendario.
- El estado 'programado' con hora pasada de los 2 casos sigue sin resolver, porque no hay segunda fuente permitida.

=====

RESPUESTA
1. **Cumplimiento: hay un posible exceso en APWin.** Football-data cumple. APWin hizo 4 descargas por red frente a un tope de 3 páginas, según cómo se cuente.
2. **Robots:** todas las URLs descargadas están permitidas.
3. **Cifras del informe:** todas las cifras que me pediste coinciden con los datos.
4. **Paginación:** ahora aparece en `coverage_report.md` y en `inventory.json meta.source_completeness`, y el veredicto es coherente. Un punto del recuento del 12-oct queda sin explicar.

EVIDENCIA
- **Cumplimiento (`consultas.jsonl`, 46 líneas, 13 de robots):**
  - football-data: 17 descargas, 12 por red (`fixtures.csv` + 11 `mmz4281/2627/*.csv`), 5 desde caché. Tope: 12 ≤ 20. Los intervalos de red son 3,0 s en las 10 transiciones consecutivas, tras un primer hueco de 1123 s. Cumple el mínimo de 3 s.
  - APWin: 16 descargas, 4 por red (`/`, `?date=` 12, 13 y 14 de octubre), 12 desde caché. Los intervalos de red son 48, 5 y 6 s, así que cumplen el mínimo de 5 s.
  - El tope es `max_pages_per_run=3`. Hubo 4 páginas por red, de las cuales 3 son `?date=` y 1 es la portada `/`. Si la portada cuenta, el tope se excede en 1. Es una decisión de política; no puedo resolverla sin red.
- **Robots (copias locales):**
  - football-data: el grupo `*` tiene `Disallow:` vacío, así que permite todo. Las 17 URLs dan permitido.
  - APWin: las reglas son solo Disallow específicos (`/search/*`, `/calendar/*`, etc.). `/` y `/?date=…` dan permitido en las 16 descargas.
  - Con `UA = "football-picks-system/0.1"`, `parse_robots` aplica el grupo `*`.
- **Cifras del informe:**
  - 240 únicos en `inventory.json`, `state.json` y matrix (15 en matrix).
  - 15 requeridos.
  - 7 con datos reales y proxy (COMPLETADO).
  - 8 NO_INVESTIGADO_SIN_FUENTE_PERMITIDA.
  - 345 mercados: 184 NOT_CHECKED + 98 NO_EVALUABLE + 63 PARCIAL. Por tanto 161 examinados.
  - Todos coinciden con el informe.
- **Paginación en los `.body` de APWin:**
  - 12-oct: `page 1, hasMore false, total 15`; cargados 11.
  - 13-oct: `hasMore true, total 166`; cargados 15.
  - 14-oct: `hasMore true, total 126`; cargados 15.
  - `meta.source_completeness` repite esos valores. `coverage.json` trae `universe_truncated=true`, y el informe lo muestra en el veredicto y en una línea de aviso.
  - La portada `/` tiene la misma paginación que la página del 12-oct (total 15, `hasMore false`).
- **Veredicto:** es coherente con la truncación. Dice "cota inferior" y "nunca la jornada completa", y los puntos "Qué NO se sostiene" no sostienen ninguna selección.
- **Punto abierto:** el 12-oct tiene `hasMore false` y `total 15`, pero se cargaron 11. Además `totalFinished` es 107, lo que sugiere que `total` cuenta algo distinto de "todos los partidos del día". El informe lo trata como "11 de 15 declarados", lo cual es correcto, pero no sé por qué faltan 4.

CAMBIO EN MI ESTADO
- La objeción del director sobre la paginación queda resuelta.
- Mantengo los 15 requeridos en "Parcial". El calendario sigue siendo de una sola fuente (APWin), y `selection_calendar_verification` sigue en `REQUIERE_VERIFICACION_ADICIONAL`.
- Nuevo pendiente: aclarar si la portada `/` cuenta para el tope de 3 páginas de APWin. Si cuenta, la ejecución excedió el tope en una página.
- Sigo sin red y sin escribir archivos; todo lo anterior es lectura local.

=====

Nada del lote nuevo `disc` queda sin revisar. Según `consultas.jsonl`, ninguna ejecución superó su tope. En la regeneración final no hubo descargas nuevas por red. Del 12-oct de APWin no encuentro la causa de los 4 partidos que faltan.

**RESPUESTA**

1. **Lote `disc` nuevo:** tiene 2 IDs, m-8341c193f7a4 (Carrick Rangers U20) y m-2411399dc132 (Deportivo Capiatá). Los dos están revisados y no requieren correcciones. El JSON va al final.
2. **Descargas por ejecución:** `consultas.jsonl` tiene ahora 82 líneas. Separé los bloques por `ts` (robots seguido de descargas). Ningún bloque supera su tope.

| Bloque (ts) | football-data (red) | APWin (red) |
|---|---|---|
| 00:11:27 | 1 (`fixtures.csv`) | 1 (portada `/`) |
| 00:12:18 | 0 | 3 (`?date=` 12, 13 y 14) |
| 00:30:10 | 11 (E0, SP1, D1, I1, F1, N1, B1, T1, P1, SC0, G1) | 0 |
| Los otros 8 bloques (00:13:35 a 00:35:30) | 0 | 0 |

   - APWin tuvo como máximo 3 páginas por bloque, y el tope es 3. Eso es coherente con tu explicación.
   - La sesión suma 4 descargas de red de APWin y 12 de football-data (tope de 20).
   - Los intervalos son correctos: 3 s entre ficheros de football-data, y 48 s (portada a 12-oct), 5 s y 6 s en APWin.
   - Puedo declarar únicamente lo que registra el log. Los sondeos manuales anteriores a la política no aparecen en `consultas.jsonl`, así que no puedo verificarlos.
3. **Regeneración final:** no hay líneas con ts en 00:5x. El último registro es 2026-10-13T00:35:32Z, y `inventory.json` se generó a las 00:35:29Z. Todos los registros posteriores a 00:30:43Z son `from_cache` (cuenta de los que no lo son: 0). Es decir, no hubo descargas nuevas de red tras las de football-data de las 00:30.
4. **APWin 12-oct (11 cargados vs 15 declarados):** el feed contiene exactamente 11 partidos en 8 arrays `matches`, y tu parser los lee todos. Esa cifra no me explica los 4 que faltan. Lo que sí veo en el HTML:
   - Hay un bloque JSON-LD (`SportsEvent`) con 6 partidos únicos del 12-oct. Ninguno está en el feed de 11: Coventry–Newcastle, Levante–Sevilla, Atalanta–Venezia, Torino–Udinese, Valladolid–Albacete y FK Bashkimi Kumanovo–Struga.
   - Cinco de ellos ya están en el inventario porque los trae football-data. FK Bashkimi Kumanovo–Struga (First Football League, 12-oct 14:00 +01:00) no está en el inventario.
   - Como 11 + 6 = 17, el total declarado de 15 no es esa suma. No he podido determinar qué cuenta `total`. El bloque `pagination` de la página trae también `totalLive` 6 y `totalFinished` 107, que sugieren que el contador no es "partidos del día".
   - Mi conclusión es que el universo de APWin es una cota inferior, incluso en el día que figura como completo (`hasMore=false`). Este partido no entra en ninguno de los 15 requeridos, que son del 13-oct.

**EVIDENCIA:** `/home/user/football-picks-system/runs/2026-10-13/sources/consultas.jsonl`, `cache/*.body` (páginas `?date=2026-10-12` y `/`, idénticas en el feed y en el JSON-LD), `inventory.json` y `batches.json`.

**CAMBIO EN MI ESTADO**
- El pendiente sobre el tope de APWin queda resuelto: ninguna ejecución individual lo excede.
- Queda abierta la causa de los 4 partidos que faltan el 12-oct. Recomiendo que el informe no diga "completo" para ningún día de APWin, y que mencione el partido FK Bashkimi Kumanovo–Struga como ejemplo de lo que queda fuera.
- Los 15 requeridos siguen en "Parcial" (una sola fuente, `selection_calendar_verification` pendiente de verificación adicional).

```json
{"agent":"verificador-mercados","batch_id":"disc","rows":[
{"match_id":"m-8341c193f7a4","review_status":"REVISADO","corrections":[],"note":"Carrick Rangers U20 - Dungannon Swifts U20, premiership development league. Epoca 1791831600 = 2026-10-12T19:00Z = 15:00 Caracas; coincide con el inventario. Categoria youth correcta (U20). Fuera de ventana, NO_ELEGIBLE correcto. Discrepancia de estado real: APWin dice upcoming con hora pasada; event_status DESCONOCIDO y confirmation_basis termina en con_discrepancias_abiertas, como corresponde. Una sola fuente; sin segunda fuente permitida para resolverla."},
{"match_id":"m-2411399dc132","review_status":"REVISADO","corrections":[],"note":"Deportivo Capiata - Benjamin Aceval, division intermedia. Epoca 1791844200 = 2026-10-12T22:30Z = 18:30 Caracas; coincide. Categoria men correcta. Fuera de ventana, NO_ELEGIBLE correcto. Misma discrepancia de estado (upcoming con hora pasada), correctamente marcada con DESCONOCIDO y con_discrepancias_abiertas. Una sola fuente."}
]}
```