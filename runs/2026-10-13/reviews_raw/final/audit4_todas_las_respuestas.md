# Auditoría adversarial, ejecución 2026-10-13 (Caracas)

Todo lo anterior se hizo en solo lectura. Usé dos peticiones a football-data.co.uk: un GET a `data.php` que dio 302 sin cuerpo, y un HEAD que confirmó la redirección a `football-data.co.uk/data.php`. No hice una tercera, así que no puedo confirmar qué ligas cubre ni la cláusula de uso comercial o de IA de Football-Data.

## 1. Objeciones

| # | Objeción y evidencia | Impacto | Responde |
|---|---|---|---|
| O1 | **El universo APWin es solo la página 1 de una lista paginada, y el informe no lo dice.** En `runs/2026-10-13/cache/*.body` (y `probe/apwin.html`), `?date=2026-10-13` trae `"pagination":{"page":1,"hasMore":true,"total":166}`. `?date=2026-10-14` trae `hasMore:true,total:126`. Solo hay 15 `kickoffUnix` por página, ordenados por prioridad de liga (UCL 9, AFC 4, U23 1, Youth 1) y no por hora. Las UCL son 9 de unas 18 de una jornada completa. No hay ningún partido entre 19:00Z del 13-oct y 23:30Z del 14-oct, un hueco de 28,5 h que incluye la tarde y noche americana del 13 local. Por tanto «15 en la ventana» es una cota inferior de entre 166 y 126 partidos que APWin lista. La frase «ninguno es evaluable» se refiere a una muestra truncada. | **Alto** para C-a y C-c. El informe debe decir «≥15, truncado». | verificador |
| O2 | **«Ninguna fuente permitida cubre sus estadísticas» es cierto por construcción, no por el mundo.** `level1.py` define `covers(match)` como `bool(match.extra.div)`. Solo los partidos cuyo calendario viene de Football-Data tienen `div`. Los 15 de APWin salen «sin cobertura» sin consultar nada. En `sources/consultas.jsonl` solo se descargó `fixtures.csv` (0 CSV de temporada). Pero las filas brutas de Football-Data (`raw_football-data.json`) contienen a Arsenal y Man United (E0), Barcelona, Ath Madrid y Villarreal (SP1), Napoli e Inter (I1), Lens y Lille (F1), Bayern (D1), PSV (N1), Club Brugge (B1), Galatasaray (T1) y Sp Lisbon (P1). Siete cruces UCL tienen ambos equipos en ligas domésticas de Football-Data: Lens–Sporting, Galatasaray–Barcelona, Atlético–Man U, Villarreal–Napoli, Inter–Brugge, Leipzig–PSV y Arsenal–Lille. Esos CSV traen goles, córners, tarjetas, árbitro y tiros, y la política permite hasta 20 descargas por ejecución. Sigue sin ser un pick: es forma doméstica, mezcla competiciones, no hay cuotas ni bajas y el n es pequeño en octubre. Pero sería PARCIAL, no NOT_CHECKED, y habría que declarar la mezcla de competiciones. Que Football-Data cubra ligas fuera de las principales (Japón, China, Noruega) no lo pude confirmar (ver arriba). | **Alto** para el estado «NO_INVESTIGADO». Medio para la decisión final: sigue sin haber pick. | cuantitativo y verificador |
| O3 | **«Partidos confirmados 240 de 240» sobrestima.** `inventory.json` marca los 240 como `REQUIERE_VERIFICACION_ADICIONAL`: 0 son `SUFICIENTE`, todos son de una sola fuente, y las dos fuentes no comparten ningún partido (ligas disjuntas). Football-Data tiene `tz_confirmada:false` (se asume Europe/London). `coverage.json` ya incluye `required_single_source_calendar:15`, `required_selection_calendar_sufficient:0` y `with_real_data_attempt:0`, pero `coverage_report.md` no los muestra. | Medio | verificador |
| O4 | **«Procesados 15/15 = 100,0%» como cifra principal.** Se calcula con `data_attempted:false` en los 15. El veredicto dice «15 partidos sin histórico suficiente», pero no se buscó ningún histórico. Lo correcto es «no investigados». «Mercados no evaluables 0» y «examinados 0/345» sí son coherentes (345 = 15×23). | Medio | cuantitativo |
| O5 | **La revisión de agentes está desfasada.** `reviews_raw/*.md` (00:19Z) describe el estado previo al arreglo: «NO_EVALUABLE_TRAS_INTENTOS» y «23 mercados NO_EVALUABLE». El `state.json` actual (00:23Z) tiene `NO_INVESTIGADO_SIN_FUENTE_PERMITIDA` y `NOT_CHECKED`. Las correcciones «sincronizar inventory con NO_EVALUABLE_TRAS_INTENTOS» ya son contradictorias. El conteo de IDs sí cuadra (`ok:true`, sin duplicados ni faltantes). Un revisor cuenta «UCL 10 partidos» y son 9. | Bajo-medio | deportivo |
| O6 | **Football-Data «robots permite todo» omite que bloquea a agentes de IA.** `rb_www.football-data.co.uk.txt` tiene `User-agent: * / Disallow:` (vacío), pero luego `Disallow: /` para GPTBot, ChatGPT-User, Anthropic-AI, Claude-Web, ClaudeBot, PerplexityBot, CCBot y otros. El UA honesto cae bajo `*`, así que es técnicamente permitido. El riesgo es de intención: el operador es un agente de IA y la fuente declara no querer IA. La cita del documento («particulares, no productos comerciales ni entrenamiento con IA») no está en ninguna copia guardada (`fd_home.html` es solo `notes.txt`). No pude verificarla. | Medio. La política de un host condicional se apoya en una cita que no pude verificar. | verificador |
| O7 | **APWin pesa más de lo que su ficha admite.** Sus términos (`apwin_terms.html`) son los de la suscripción Premium: «use… personal, individual and non-transferable, and any unauthorized, commercial or non-commercial use is prohibited». Es la única fuente de los 15 partidos y de los 41 de APWin. La política dice «sin cláusula explícita sobre acceso automatizado». Eso es cierto, pero la reserva de derechos es amplia. El límite de 3 páginas por ejecución además impide leer `page=2`. | Medio | verificador |
| O8 | Dos partidos de APWin están como `CONFIRMADO` pese a un estado obsoleto («upcoming» con hora ya pasada): Carrick Rangers U20–Dungannon Swifts U20 y Capiatá–Benjamin Aceval. Su base es «con_discrepancias_abiertas». El verificador ya lo señaló. Es coherente que estén fuera de la ventana. | Bajo | verificador |
| O9 | `matrix.csv` tiene 570 filas: 345 de mercado y 225 en blanco. Es correcto pero engañoso al contar. | Bajo | cuantitativo |
| O10 | Los 199 registros de Football-Data son resultados ya jugados del fin de semana del 9 al 12 de octubre. `fixtures.csv` no trajo partidos próximos. La disposición «fuera de la fecha local» es cierta, pero también son histórico útil (ver O2). | Bajo | verificador |

## 2. C-b: las citas contra las copias guardadas

Las citas son fieles.

- **FotMob.** `fm_tos.html` dice textualmente: «use of automatic services (robots, spiders, indexing, etc.), as well as other methods for systematic, regular, or bulk retrieval of data, is expressly forbidden», y «scraping… without the express written consent… strictly prohibited». `robots_www.fotmob.com.txt` tiene `Disallow: /api/*` para `*` y lo permite solo a Googlebot, Bingbot, Qwantbot y AmazonAdBot. Exclusión respaldada.
- **BetExplorer.** `be_tos.html` dice «not permitted to use our content… by embedding, aggregating, scraping or recreating it without our express consent» y «must not burden our server… with automated requests». El operador es Livesport s.r.o. El `robots` lista `/*?year=` y `/*?month=`, correcto. Exclusión respaldada.
- **Transfermarkt.** `tm_terms.html` (og:url `…/intern/anb`) §11.1 dice textualmente «not permitted to access or copy the Digital Content using bots, spiders, screen scraping or other automated processes». Además prohíbe usarlo para entrenar IA. El `robots` solo bloquea a `wget` y a Slurp con retardo, de modo que la exclusión descansa en los términos, como dice el documento. Respaldada.
- **Understat.** `robots_understat.com.txt` dice `User-agent: * / Disallow: /`. Respaldada.
- **SoccerStats.** La copia de `robots.txt` es el desafío Cloudflare («Just a moment…»). Es «bloqueada por anti-bot, no evadida», no «prohibida por condiciones». Sus términos nunca se leyeron. Conviene reetiquetarla como «inaccesible por anti-bot» y no como «excluida por sus condiciones». Impacto bajo.
- **Fuentes excluidas que deberían ser condicionales.** Ninguna con evidencia.
- **Fuentes «NO REVISADA → denegada».** Es una limitación del sistema, no un hallazgo sobre el mundo. Las copias `rb_*.txt` muestran que AFA y Liga Portugal permiten todo, salvo `/cache/` en AFA. Sus términos de uso sí se podrían leer y revisar. UEFA y AFC no tienen `robots` guardado. Esa revisión de conformidad es una vía que el sistema no ha explorado: no es evasión, sino leer los términos y registrar el resultado.

## 3. C-c: muestra de 25 de los 225

Recalculé las 240 horas a mano desde `sources/raw_*.json`, sin usar el inventario. Las horas de Football-Data las convertí con Europe/London (BST, +1 h). Resultado: **0 discrepancias en 240**, y 15 en la ventana [04:00Z 13-oct, 04:00Z 14-oct), igual que el sistema. `normalized_datetime_local` coincide en las 240 y no hay `match_id` duplicados.

Muestra de 11 de APWin, los más cercanos al borde, más 8 de Football-Data (los 5 pedidos más 3 extremos) y 6 más de APWin del 14-15 oct:

| Partido | UTC | Caracas | Disposición |
|---|---|---|---|
| Carlos Manucci–Alianza Univ. | 13-oct 01:00 | 12-oct 21:00 | fuera, correcto |
| Bragantino–Cruzeiro | 13-oct 00:00 | 12-oct 20:00 | fuera, en juego. **C-d se sostiene.** |
| Botafogo-SP–Ceará | 13-oct 00:00 | 12-oct 20:00 | fuera, en juego |
| Criciúma–América MG, Chapecoense–Athletico-PR | 12-oct 22:30 | 12-oct 18:30 | fuera, en juego |
| Capiatá–Benjamin Aceval | 12-oct 22:30 | 12-oct 18:30 | fuera, estado obsoleto (O8) |
| Nacional PAR–Recoleta | 12-oct 22:20 | 12-oct 18:20 | fuera, en juego |
| All Boys–Godoy Cruz, Novorizontino–Ponte Preta | 12-oct 22:00 | 12-oct 18:00 | fuera (en juego / finalizado) |
| HFX Wanderers–Cavalry | 12-oct 20:00 | 12-oct 16:00 | fuera, finalizado |
| Carrick U20–Dungannon U20 | 12-oct 19:00 | 12-oct 15:00 | fuera, estado obsoleto |
| FC Cincinnati–NE Revolution (+5 MLS más) | 14-oct 23:30 | 14-oct 19:30 | fuera, correcto |
| St. Louis–Vancouver (+3 MLS más) | 15-oct 00:30 | 14-oct 20:30 | fuera, correcto |
| Famalicão–Alverca, Coventry–Newcastle, Levante–Sevilla | 12-oct 19:15 / 19:00 | 12-oct 15:15 / 15:00 | fuera, ya jugados |
| Derby–Wrexham, Middlesbrough–Wolves, Preston–Millwall (EFL) | 10-oct 14:00 | 10-oct 10:00 | fuera, ya jugados |
| Braunschweig–Holstein Kiel, Heidenheim–Kaiserslautern | 9-oct 16:30 | 9-oct 12:30 | fuera, ya jugados |

Conclusión sobre C-c: los 225 conocidos están bien clasificados (tiempo, ventana y disposición). Lo que no se puede sostener es que «los demás partidos no requieren análisis» como afirmación sobre el mundo, por O1.

## 4. Lo que resiste el ataque

- C-d (Bragantino–Cruzeiro, 00:00Z, es del 12 local).
- La ventana UTC y la conversión horaria de los 240 registros.
- Las citas de FotMob, BetExplorer, Transfermarkt y Understat.
- La integridad entre `inventory.json`, `state.json` (240 = 225 + 15), `matrix.json` (15 partidos × 23 mercados = 345) y `matrix.csv` (345 + 225 en blanco). No hay IDs huérfanos (`reviews.json` sin faltantes, duplicados ni desconocidos) ni filas duplicadas.
- Los números del informe (denominadores y 0,0 %) salvo la presentación de O3 y O4. Los 345 mercados pasaron de «examinados» a `NOT_CHECKED` tras el arreglo, comparando `previous_run_pre_fix/coverage.json` con el actual.
- Cero picks: no hay ninguna cuota ni dato verificable, y no hay evidencia para seleccionar.

## 5. Vía permitida no explorada

1. Descargar los CSV de temporada de Football-Data (`mmz4281/2627/{E0,SP1,D1,I1,F1,N1,B1,T1,P1}.csv`) para la forma doméstica de 7 de los cruces UCL. Esto entra en el límite de 20 por ejecución. Hay que declarar que mezcla competiciones y que el n es pequeño.
2. Paginar APWin (`page=2…`) requiere ampliar los límites de la política y registrar la decisión, porque hoy el tope es de 3 páginas por ejecución. No lo probé.
3. Leer los términos de UEFA.com, AFC y Liga Portugal y registrar el resultado en la política, no relajarla.
4. Calendario aportado por la persona usuaria con `inventory.py --manual`.

## 6. Veredicto sugerido (no vinculante)

**Se puede afirmar**
- El sistema no tiene datos verificados para seleccionar ningún pick en esta ejecución.
- Los 225 registros conocidos están correctamente fuera de la ventana.
- Bragantino–Cruzeiro no pertenece al 13-oct local.
- FotMob, BetExplorer, Transfermarkt y Understat están excluidos con respaldo textual.

**No se puede afirmar**
- Que haya 15 partidos en la jornada: son ≥15 vistos de 166 en la lista de APWin.
- Que ningún partido sea evaluable: no se investigó ninguno, y la forma doméstica de Football-Data habría dado cobertura PARCIAL en 7 cruces UCL.
- Que «240 partidos confirmados» equivalga a calendario verificado: es una sola fuente, tz sin confirmar, 0 `SUFICIENTE`.
- Que la cobertura sea «100,0 %»: sería 100 % de procesado y 0 % de examinado.
- Que la política de Football-Data sea limpia: omite el bloqueo explícito a agentes de IA y su cita de uso comercial no la pude verificar.

Mejor alternativa: etiquetar el resultado como «NO INVESTIGADO / universo truncado» (no «no evaluable») y ejecutar la vía 1 del apartado 5 antes de cerrar la jornada.

## 7. Registro de fuentes

| Fuente | URL o ficha | Dato buscado | Información obtenida | Fecha de consulta | Estado | Discrepancias | Alternativa consultada |
|---|---|---|---|---|---|---|---|
| FotMob | `probe/fm_tos.html`, `robots_www.fotmob.com.txt` (copias locales) | Cláusula de scraping y robots | Cita textual del sistema confirmada; `Disallow: /api/*` | 13-oct-2026 (copia de 00:00–00:01Z) | Consultada y útil | Ninguna | n/a |
| BetExplorer | `probe/be_tos.html`, `robots_www.betexplorer.com.txt` | Términos y robots | Cita confirmada; operador Livesport s.r.o.; `be_terms.html` y `be_about.html` vacías | 13-oct-2026 | Consultada y útil | Ninguna en la cita | n/a |
| Transfermarkt | `probe/tm_terms.html` (`intern/anb`), `robots_www.transfermarkt.com.txt` | §11.1 y robots | Cita §11.1 confirmada; robots permite `/` | 13-oct-2026 | Consultada y útil | Ninguna | n/a |
| Understat | `robots_understat.com.txt` | `Disallow: /` | Confirmado | 13-oct-2026 | Consultada y útil | Ninguna | n/a |
| SoccerStats | `robots_www.soccerstats.com.txt` | robots | Solo desafío Cloudflare; términos no leídos | 13-oct-2026 | Acceso fallido | «Excluida por condiciones» no está respaldada, solo por anti-bot | n/a |
| Football-Data | `rb_www.football-data.co.uk.txt`, `probe/fd_home.html` (copias); `data.php` (curl) | robots y cláusula de uso | robots: `*` permitido, bloquea ClaudeBot, Anthropic-AI, Claude-Web, etc.; cláusula de uso no hallada en copias; curl a `data.php` dio 302 sin cuerpo (GET y HEAD, 2 peticiones) | 13-oct-2026 (00:24Z) | Acceso parcial | Cita del documento no verificable (O6) | Ninguna: se agotó el tope de 2 peticiones |
| APWin | `probe/apwin.html` y `runs/2026-10-13/cache/*.body` (`?date=12/13/14`), `apwin_terms.html`, `rb_www.apwin.com.txt` | Calendario, paginación, términos | `hasMore:true,total:166` (13-oct) y `126` (14-oct), solo 15 partidos visibles; términos con «commercial or non-commercial use prohibited» | 13-oct-2026 (00:21Z) | Consultada con datos insuficientes | Universo truncado (O1); términos más amplios que la ficha (O7) | Ninguna permitida sin ampliar política |
| Archivos del run | `runs/2026-10-13/{inventory,state,matrix,coverage,batches,reviews}.json`, `matrix.csv`, `coverage_report.md`, `reviews_raw/*` | Integridad y recálculo UTC→Caracas de los 240 registros | 0 discrepancias de hora/ventana; informe desfasado respecto a `coverage.json` | 13-oct-2026 | Consultada y útil | O3, O4, O5, O9 | n/a |

**Limitaciones**
- Solo revisé copias locales de las páginas legales, que pueden estar desactualizadas respecto a las originales.
- No consulté ninguna fuente externa distinta de football-data.co.uk, así que la veracidad real de los calendarios (p. ej. la UCL del 13-oct) no está contrastada.
- No es asesoría legal.

Archivos relevantes:
- `/home/user/football-picks-system/runs/2026-10-13/coverage_report.md`
- `/home/user/football-picks-system/runs/2026-10-13/coverage.json`
- `/home/user/football-picks-system/runs/2026-10-13/inventory.json`
- `/home/user/football-picks-system/runs/2026-10-13/cache/` (los `.body` de APWin con la paginación)
- `/home/user/football-picks-system/.claude/skills/seleccion-final-picks/scripts/level1.py` (`covers()`)
- `/home/user/football-picks-system/.claude/skills/seleccion-final-picks/scripts/sources_policy.json`
- `/home/user/football-picks-system/docs/FUENTES-CONFORMIDAD.md`

=====

## Ronda 3: resultado

Todo es lectura de archivos locales, sin red.

### (a) Estado de O1 a O10

| # | Estado | Evidencia |
|---|---|---|
| O1 | RESUELTA | `inventory.meta.source_completeness` registra 166 declarados y 15 cargados el 13-oct (126 y 15 el 14-oct). `coverage.json` tiene `universe_truncated:true`. El veredicto y el informe dicen «cota inferior». Nota menor: el 12-oct declara 15 y carga 11, y no se explica. |
| O2 | PARCIAL | 7 cruces UCL reciben forma doméstica de 11 CSV de `TOP_DIVS`, con `team_aliases.json` y etiqueta `proxy_sample:true`. Los 8 restantes siguen «NO_INVESTIGADO». Los 4 de la AFC (Japón y China) no se intentaron, y no confirmé que Football-Data cubra esas ligas. |
| O3 | RESUELTA | El informe tiene la fila «CONFIRMADO… con verificación SUFICIENTE para selección final: 0» y la fila «15 de 15 con UNA sola fuente». |
| O4 | PARCIAL | El informe sí distingue «con disposición» (15), «consulta real» (7) y «evaluados suficientemente» (0). Pero `state.json`, `inventory.json` y `matrix.csv` marcan los 7 proxies como `COMPLETADO` (ver N1). |
| O5 | PARCIAL | `reviews_raw/README.md` es honesto. Pero `batches.json` y `reviews.json` ya no están en `runs/2026-10-13/` (quedaron en `previous_run_pre_fix3/`). Los `.md` crudos tienen 0 IDs vigentes. La matriz con proxy, generada a las 00:30Z, no la revisó ningún agente. |
| O6 | PARCIAL | `risk_note` y `docs/FUENTES-CONFORMIDAD.md` ya mencionan el bloqueo de crawlers de IA. La cita de `data.php` (fechada 12-oct) sigue sin poder verificarla. La decisión de la persona usuaria está pendiente, pero el run ya descargó 11 CSV (00:30Z) y la política sigue en «condicional». |
| O7 | PARCIAL | `risk_note` de APWin añadido («no se amplía a paginación sin decisión expresa»). La fuente se sigue usando. |
| O8 | ABIERTA (bajo) | Carrick U20 y Capiatá siguen `CONFIRMADO` con «discrepancias_abiertas». Es aceptable si el informe lo declara. |
| O9 | ABIERTA (bajo) | `matrix.csv` tiene 571 líneas (345 mercados, 225 filas en blanco y la cabecera). |
| O10 | RESUELTA | La nota de `docs/FUENTES-CONFORMIDAD.md` ya dice que los 199 de Football-Data son «anteriores a la ventana». |

### (b) Objeciones nuevas

- **N1 (alto): `COMPLETADO` engaña.** `level1.py:285` lo asigna si hay `form.local` y `form.visitante`. Los 7 proxies figuran `COMPLETADO/COMPLETADO` en inventario, estado y matriz. El `SKILL.md` define `COMPLETADO` como análisis hecho, y el informe dice «evaluados suficientemente 0». Hace falta un estado distinto, por ejemplo `PARCIAL_PROXY`.
- **N2 (alto): «Mercados examinados 161 de 345 = 46,7 %».** Cuenta 63 PARCIAL y 98 NO_EVALUABLE obtenidos de otra competición. Se puede leer como cobertura real del partido. Debería desglosarse o presentarse como «proxy».
- **N3 (alto): tarjetas no comparables entre ligas.** `fd_home.html` (notes de Football-Data) dice que en Inglaterra y Escocia las amarillas no incluyen la primera cuando hay doble amarilla, y en Europa sí. `tarjetas.total` suma amarillas y rojas sin ajustar, y mezcla Arsenal y Man United (E0) con rivales de otras ligas.
- **N4 (medio-alto): muestras débiles.** Las 7 filas tienen n entre 5 y 8: Leipzig local 5 (n=5); Man United, Arsenal y Villarreal–Napoli 6 en un lado. La skill dice «n<8 = muestra débil». Hay 14 lados, 10 con n<8 y 4 con n=8. Las etiquetas «local últimos 8» mezclan partidos en casa y fuera; «local» es el rol del partido, no la sede.
- **N5 (medio): líneas fijas** de córners (8.5/9.5/10.5) y tarjetas (3.5/4.5/5.5), no las del mercado real. La skill exige «línea exacta», y aquí no existe línea porque no hay cuota.
- **N6 (medio): riesgo de alias.** `team_aliases.json` es explícito y no usa coincidencia difusa, lo cual es sano. Pero «sporting»→Sp Lisbon descansa en que los juveniles no lleguen al proxy (hoy `Lens U19–Sporting U19` es `proxy_sample:false`, correcto). No hay prueba automática de eso. Conviene una verificación manual de los 7 alias. Se descargaron además SC0 y G1, que no se usan.
- **N7 (medio): `familias sin ningún mercado evaluable: []`** en el informe. Es cierto solo por los 63 PARCIAL de proxy, y puede leerse como que hay mercados evaluables.
- **N8 (medio): `SKILL.md` no se actualizó.** No define `proxy`, `UNIVERSO TRUNCADO` ni el significado de `COMPLETADO` para proxy. Sigue enunciando solo `NO_INVESTIGADO`.
- **N9 (bajo): árbitro** `null` en todas las filas. No hay designación, así que ningún mercado de tarjetas es defendible.

### (c) Cobertura o validación sin respaldo

- «Revisado por agentes 15 de 15»: eso fue sobre la matriz anterior. La matriz actual (00:30Z) no tiene revisión.
- El informe dice «Con al menos una consulta real de datos: 7 de 15», pero es de otra competición. No hay validación del partido.
- La cita de `data.php` en `risk_note` no la puedo confirmar.

### (d) Veredicto sugerido (no vinculante)

**Puede afirmarse**
- No hay picks defendibles.
- El universo de APWin es una cota inferior (166 declarados el 13-oct, 15 cargados).
- Los 15 partidos tienen calendario de una sola fuente y 0 verificación SUFICIENTE.
- Hay descriptivos domésticos parciales (k/n, n 5 a 8) en 7 cruces UCL, de otra competición.
- Se registra cuándo y cómo se consultó cada fuente.
- Las exclusiones de FotMob, BetExplorer, Transfermarkt y Understat siguen respaldadas.

**No puede afirmarse**
- Que 7 partidos estén «COMPLETADOS» o «evaluados».
- Que haya mercados evaluables, probabilidades, cuotas o EV.
- Que 46,7 % de mercados examinados sea cobertura de la jornada.
- Que haya sido revisado por agentes tras el cambio.
- Que Football-Data esté libre de riesgo.

Pendientes antes de cerrar: renombrar `COMPLETADO` en los proxies, normalizar las tarjetas de E0, marcar n<8 y repetir la revisión de agentes sobre la matriz nueva. La decisión sobre Football-Data y APWin queda en manos de la persona usuaria.

=====

## Auditoría final: estado de N1–N9 y O1–O10

Todo es lectura de archivos locales, sin red.

### (a) Re-evaluación

| Objeción | Estado | Evidencia |
|---|---|---|
| N1 | RESUELTA | En `inventory.json`, `state.json` y `matrix.json` los 7 proxies están en `PARCIAL_PROXY_OTRA_COMPETICION` y los otros 8 en `NO_INVESTIGADO_SIN_FUENTE_PERMITIDA`. Ningún partido figura `COMPLETADO`. |
| N2 | RESUELTA | El informe dice «161 de ellos son solo proxy de OTRA competición y 0 de la misma», y «de la misma competición: 0». |
| N3 | PARCIAL | **Retiro la cita: no hay nada que retirar.** La línea existe en `probe/fd_home.html`, línea 45: «Note also that English and Scottish yellow cards do not include the initial yellow card when a second is shown to a player converting it into a red, but this is included as a yellow (plus red) for European games.» Si no la ven, será por las etiquetas HTML. La nota actual dice «sin verificar que la definición sea homogénea», pero esa fuente ya dice que no lo es entre E0/SC y el resto. Debería decir «NO homogénea». Afecta a Arsenal–Lille y Atlético–Man United (E0 frente a otra liga). Impacto bajo-medio. |
| N4, N5 | RESUELTA | `sample_note` incluye «MUESTRA DÉBIL n<8: Manchester United n=6» y «líneas… referencias fijas, NO las de ninguna casa». |
| N6 | RESUELTA (parcial) | `team_aliases.json` tiene `needs_review.sporting`, y el `SKILL.md` excluye juveniles, sub-23, reservas y femenino. No ejecuté el test automático que mencionan. |
| N7 | RESUELTA | El informe calcula «familias sin ningún mercado evaluable de la misma competición» con las 5 familias. |
| N8 | RESUELTA | El `SKILL.md` define «Proxy doméstico» y «Universo truncado». |
| N9 | ABIERTA (bajo) | El árbitro sigue en `null`, pero la nota lo declara. Aceptable. |
| O1, O3, O10 | RESUELTA | |
| O2 | PARCIAL | El proxy cubre 7 cruces UCL. Para los 4 de la AFC (Japón y China) no hay evidencia de que no exista fuente permitida, porque no se intentó. |
| O4 | RESUELTA | El informe distingue disposición (15), consulta real (7) y evaluados suficientemente (0). |
| O5 | PARCIAL | `batches.json` está regenerado (7 lotes, 15 filas, lote `disc` con 2 discrepancias). Las revisiones de los agentes sobre la matriz definitiva siguen en curso, y `reviews_raw/*.md` solo tiene las antiguas. Queda ABIERTA hasta que `batches.py check` confirme que no falta ninguna fila. |
| O6, O7 | PARCIAL | Los `risk_note` existen, pero la decisión de la persona usuaria no está registrada y el run ya descargó los CSV. La cita de `data.php` sigue sin verificarse por mí. |
| O8, O9 | ABIERTA (bajo) | Sin cambios. |

### (b) Afirmaciones que aún sobrestiman

- **«Procesados sin consulta real: 8 de 15 (ninguna fuente permitida los cubre)».** No se intentó ninguna fuente para Japón ni China (4 AFC), y Football-Data tiene ligas extra que no pude confirmar. Debería decir «no intentado», no «ninguna lo cubre». Impacto medio.
- **«Mercados no evaluables 98» (`NO_EVALUABLE`).** Son huecos de un proxy de otra competición, no un juicio sobre el mercado del partido. El informe lo califica solo en parte. Impacto bajo.
- **«Mercados con evaluación parcial/evaluable 63»** sigue apareciendo con la palabra «evaluable» en la métrica. La nota aclara que no hay candidatos, pero el nombre de la fila conserva el término. Impacto bajo.
- **`docs/FUENTES-CONFORMIDAD.md`, línea 19**, dice que el ranking es «PROVISIONAL RESTRINGIDO y no hay picks». Es correcto. Pero Football-Data aparece como «CONDICIONAL» con riesgo «que debe aceptar la persona usuaria», cuando ya se usó (11 CSV a las 00:30Z) sin esa aceptación registrada. Impacto medio.
- **`risk_note` de Football-Data** dice «no es un crawler». Es discutible, porque descarga CSV de forma automatizada con identidad propia. Debería presentarse como valoración, no como hecho.

### (c) Veredicto final sugerido (no vinculante)

**Puede afirmarse**
- No hay picks defendibles hoy.
- El universo de partidos es una cota inferior (15 de 166 el 13-oct).
- Los 15 partidos tienen calendario de una sola fuente, sin verificación suficiente para selección final.
- 7 cruces UCL tienen estadística descriptiva doméstica parcial (de otra competición, n entre 5 y 8, sin cuota, sin árbitro).
- La clasificación horaria de los 240 registros es correcta; Bragantino–Cruzeiro es del 12 local.
- Las exclusiones de FotMob, BetExplorer, Transfermarkt y Understat están respaldadas por el texto de sus términos o `robots`.

**No puede afirmarse**
- Que alguno de los 15 partidos esté evaluado, ni que haya mercados evaluables de la misma competición.
- Que «ninguna fuente permitida» cubra los 8 restantes.
- Que la revisión por agentes esté cerrada (en curso).
- Que Football-Data y APWin estén aceptados por la persona usuaria.
- Que el proxy sirva para ordenar picks.

Para cerrar quedan tres cosas: la conciliación de `batches.py check`, la decisión de la persona usuaria sobre Football-Data y APWin, y reformular «ninguna fuente permitida» como «no intentado» donde corresponda.