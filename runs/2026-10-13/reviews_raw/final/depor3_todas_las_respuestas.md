Sigo en modo solo lectura. Extraigo las filas de los 15 partidos y la política de fuentes.

=====

Imprimo de forma compacta y reviso la matriz.

=====

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

=====

**(1) Coherencia de los 15 partidos: RESPUESTA** Sí. Las 15 filas son coherentes entre sí y Portimonense U23 – Académico Viseu U23 ahora es `u23`. Estas son las conclusiones:
- Los 15 IDs de `batches.json` (los nuevos) existen en los tres ficheros.
- En `inventory.json`, `state.json` y `matrix.json` las 15 filas tienen `sports_analysis_status` y `market_analysis_status` en NO_EVALUABLE_TRAS_INTENTOS.
- La disposición es "elegible para evaluación prepartido" y `analysis_required` es true en todas.
- Los 15 partidos no cambiaron: nombres y horas locales siguen iguales (03:45, 06:00, 07:00, 12:45 y 15:00).
- Las categorías son 13 `men`, 1 `u23` (m-23a8afef592b) y 1 `youth` (Lens U19).

**(1) EVIDENCIA** Cruce directo de los tres JSON nuevos; `coverage_report.md` muestra Pendientes 0 y 15 de 15 procesados.
**(1) CAMBIO EN MI ESTADO** Los hallazgos 1 y 4 quedan cerrados. Los IDs de mis bloques JSON anteriores quedan obsoletos, así que los reemito con el mapa nuevo: m-9ec6426a60e9, m-0c15b801051b, m-652b82fc3ca3, m-fef50009982d, m-23a8afef592b, m-97cb0716e4dc, m-d89de9c16489, m-26124a15db3b, m-56d70359455c, m-7fbfa4899ff4, m-837c7443671e, m-c585811d2f7b, m-e58658a3f614, m-fa26ce1cb71b, m-316ec30a5d4e.

**(2) Pasos para revisar y dar de alta una fuente (UEFA, AFC, Liga Portugal/FPF): RESPUESTA** Habría que hacer lo siguiente, sin consultar nada por red ahora:
1. Leer `robots.txt` del host y anotar las rutas que prohíbe (`Disallow`), como se hizo con FotMob y Understat.
2. Leer los términos de uso y la política de datos, y buscar cláusulas contra bots, scraping o agregación.
3. Buscar si existe una API oficial o licencia de datos, y si requiere clave o acuerdo escrito.
4. Si hay desafío anti-bot (Cloudflare o CAPTCHA), registrar la fuente como excluida sin evadirlo.
5. Comprobar con el User-Agent honesto (`football-picks-system/0.1`) que la ruta concreta, por ejemplo calendarios o alineaciones, responde con contenido real.
6. Definir límites: rutas permitidas, pausa entre peticiones y tope por ejecución.
7. Registrar en `sources_policy.json` el estado, los hosts, el motivo y las URLs de evidencia, y actualizar `docs/FUENTES-CONFORMIDAD.md`.
8. Verificar que lo que cada fuente aporta cubre realmente lo que falta, que son forma, bajas y alineaciones, y no solo el calendario.

Si no se pasa el paso 1 o el 2, la fuente queda excluida. Esto lo debe validar quien decide la política, porque no es asesoría legal.
**(2) EVIDENCIA** `docs/FUENTES-CONFORMIDAD.md` lista "oficiales (… UEFA …)" como NO REVISADA ⇒ denegada y dice que activarla exige revisarla y registrarla. AFC y Liga Portugal/FPF no figuran por nombre: entran en "oficiales" solo por analogía, y conviene añadirlos explícitamente.
**(2) CAMBIO EN MI ESTADO** Ninguno.

**(3) Objeción sobre la fuente única: RESPUESTA** El `coverage_report.md` actual no lo comunica con claridad. Solo lo hace `selection_calendar_verification` = REQUIERE_VERIFICACION_ADICIONAL en `inventory.json`, y ese campo no sale en el informe.
**(3) EVIDENCIA** Tres datos del informe:
- Dice "Partidos confirmados 240 de 240" y "calendario: {'CONFIRMADO': 240}".
- Muestra los registros brutos por fuente (apwin 41, football-data 199).
- No dice cuántos de los 15 partidos a evaluar dependen solo de APWin.

El `grep` de "una sola", "contraste" y "REQUIERE" no encontró nada en el informe.
**Línea propuesta**, bajo "Requieren evaluación":
`| Hora/calendario de los 15 evaluables | 15 de 15 con UNA sola fuente (APWin, zona UTC declarada) y selection_calendar_verification = REQUIERE_VERIFICACION_ADICIONAL; "CONFIRMADO" significa sin discrepancias entre fuentes, no hora contrastada |`
**(3) CAMBIO EN MI ESTADO** Mantengo el hallazgo 2 como pendiente de corrección en `coverage_report.py`.

=====

**RESPUESTA**
- **(1) Resoluciones de nombre:** las 7 resoluciones son correctas, con una reserva sobre Sporting. El mapeo es exacto o por alias y no hay coincidencias difusas. Resultados: Lens→Lens (F1), Sporting→Sp Lisbon (P1, alias), Galatasaray→T1, Barcelona→SP1, Atlético Madrid→Ath Madrid (alias), Manchester United→Man United (E0, alias), Villarreal→SP1, Napoli→I1, Inter Milan→Inter (alias), Club Brugge→B1, RB Leipzig→D1, PSV→PSV Eindhoven (N1, alias), Arsenal→E0 y Lille→F1.
- **Reserva sobre Sporting:** el alias "sporting"→"Sp Lisbon" se decide solo por el nombre, sin comprobar que sea Sporting CP en ese contexto. Es plausible porque en este mismo inventario Lens U19–Sporting U19 y la Liga Revelação son portugueses. Pero eso es contexto, no evidencia independiente, y el alias es global: si otro cruce trajera "Sporting" de otro país, se equivocaría.
- **(2) Forma:** las fechas están ordenadas, todas son anteriores a 2026-10-13 (la última es 10-10, salvo 10-09 en algunos casos), y `fd_team` y la competición son coherentes en cada lado.
- **Venue:** es relativo al equipo en su partido doméstico, como dices. El cruce Atlético–Villarreal del 23/08 sale como local para uno y visitante para el otro, y ambos con 2-2. Solo verifiqué ese cruce, no todos.
- **n por equipo:** coincide con las filas del CSV de Football-Data (`2627/*.csv`): RB Leipzig 5, Bayern 5, Man United 6, Arsenal 6, Lille 6, Sp Lisbon 8 y Galatasaray 7. Leipzig n=5 cuadra porque la Bundesliga empezó el 28-29/08. Con n<8 la muestra es débil (Leipzig 5, Inter 6, Lens 6, Man United 6, Arsenal 6, Lille 6, Napoli 6, Atlético 8).
- **(3) Los 8 restantes:**
  - Los 4 de AFC Champions League: Asia, sin liga en Football-Data (cuyo CSV cubre solo ligas europeas y TOP_DIVS).
  - Sabah–Slavia Praha: Azerbaiyán y Chequia no están en TOP_DIVS.
  - Viking–Bayern: Bayern sí resuelve (alias "bayern munchen"→"Bayern Munich", visto en D1.csv), pero Viking (Noruega) no está en las ligas cubiertas, y la cobertura exige que se resuelvan los dos equipos.
  - Portimonense U23 y Lens U19 son categorías sub-23/juvenil, que Football-Data no cubre.
- **No parece un alias faltante:** ninguno de los 8 falla por alias. Viking tampoco debería resolverse por alias, porque nunca estaría en Football-Data. Verifica que Bayern–Viking quede NO_INVESTIGADO con el motivo "un equipo sin cobertura".
- **Texto proxy:** el aviso dice "OTRA competición", "NO es evidencia del partido" y "≤10 partidos". Es honesto, pero no avisa de n<8 ni de que el calendario doméstico incluye rivales de nivel muy distinto.

**EVIDENCIA** Lectura de `inventory.json` (`extra.proxy_resolution`), `matrix.json` (`form`), `team_aliases.json` y los CSV de `runs/2026-10-13/cache` y `level1.py`, solo lectura y sin red.

**CAMBIO EN MI ESTADO** Acepto la afirmación del director con dos reservas: el alias "sporting" y el aviso de n<8. Propongo que la nota del proxy muestre n por equipo y marque "n<8 = muestra débil".

```json
{"agent":"analista-deportivo","batch_id":"ronda3","rows":[
{"match_id":"m-9ec6426a60e9","review_status":"REVISADO","corrections":[],"note":"Newcastle Jets - Gamba Osaka, AFC CL. NO_INVESTIGADO: sin fuente permitida para Asia; Football-Data no cubre ligas asiáticas."},
{"match_id":"m-652b82fc3ca3","review_status":"REVISADO","corrections":[],"note":"Pohang - Johor DT, AFC CL. NO_INVESTIGADO por falta de cobertura (Asia)."},
{"match_id":"m-fef50009982d","review_status":"REVISADO","corrections":[],"note":"Shanghai SIPG - Daejeon, AFC CL. NO_INVESTIGADO por falta de cobertura (Asia)."},
{"match_id":"m-0c15b801051b","review_status":"REVISADO","corrections":[],"note":"Kyoto Sanga - Ratchaburi, AFC CL. NO_INVESTIGADO por falta de cobertura (Asia)."},
{"match_id":"m-23a8afef592b","review_status":"REVISADO","corrections":[],"note":"Portimonense U23 - Academico Viseu U23, categoría u23. NO_INVESTIGADO: Football-Data no cubre sub-23 portugués."},
{"match_id":"m-316ec30a5d4e","review_status":"REVISADO","corrections":[],"note":"Lens U19 - Sporting U19, Youth League. NO_INVESTIGADO: la forma de los primeros equipos no es proxy de juveniles."},
{"match_id":"m-97cb0716e4dc","review_status":"REVISADO","corrections":["marcar n<8 y reserva del alias global 'sporting'"],"note":"Lens (F1, n=6) - Sporting (Sp Lisbon, P1 alias, n=8). Proxy doméstico etiquetado, fechas anteriores a 10-13; resolución de Sporting solo por nombre."},
{"match_id":"m-d89de9c16489","review_status":"REVISADO","corrections":[],"note":"Sabah - Slavia Praha, UEFA CL. NO_INVESTIGADO: Azerbaiyán y Chequia fuera de las ligas cubiertas por Football-Data."},
{"match_id":"m-c585811d2f7b","review_status":"REVISADO","corrections":["marcar n<8 en la nota del proxy"],"note":"Galatasaray (T1, n=7) - Barcelona (SP1, n=8). Resolución exacta, venue y fechas coherentes; proxy de otra competición."},
{"match_id":"m-26124a15db3b","review_status":"REVISADO","corrections":["marcar n<8 en la nota del proxy"],"note":"Atlético (Ath Madrid, SP1, alias, n=8) - Man United (E0, alias, n=6). Alias correcto; cruce Atlético-Villarreal verificado como consistente."},
{"match_id":"m-56d70359455c","review_status":"REVISADO","corrections":["marcar n<8 en la nota del proxy"],"note":"Villarreal (SP1, n=8) - Napoli (I1, n=6). Resolución exacta; proxy de otra competición."},
{"match_id":"m-7fbfa4899ff4","review_status":"REVISADO","corrections":["marcar n<8 en la nota del proxy"],"note":"RB Leipzig (D1, n=5, cuadra con las jornadas disputadas) - PSV (PSV Eindhoven, N1, alias, n=8)."},
{"match_id":"m-837c7443671e","review_status":"REVISADO","corrections":["marcar n<8 en la nota del proxy"],"note":"Inter (alias, n=6) - Club Brugge (B1, n=8). Proxy etiquetado; muestra débil en Inter."},
{"match_id":"m-e58658a3f614","review_status":"REVISADO","corrections":[],"note":"Viking - Bayern München. Bayern resuelve por alias, Viking (Noruega) no está en las ligas cubiertas; el partido queda NO_INVESTIGADO por ese motivo."},
{"match_id":"m-fa26ce1cb71b","review_status":"REVISADO","corrections":["marcar n<8 en la nota del proxy"],"note":"Arsenal (E0, n=6) - Lille (F1, n=6). Resolución exacta; proxy de otra competición."}]}
```

=====

Las 15 filas de b01–b07 son coherentes entre `inventory.json`, `state.json` y `matrix.json`. Los 15 IDs de `batches.json` coinciden con los `analysis_required=true` del inventario, y los IDs no cambiaron. Una de las dos observaciones sobre el informe afecta a la lectura de los datos proxy.

**Coherencia comprobada**
- **Los 8 sin proxy:** están en NO_INVESTIGADO_SIN_FUENTE_PERMITIDA en los tres ficheros. `proxy_sample` es false y los 23 mercados de cada partido están NOT_CHECKED, con `evaluated_markets_ok` en 0.
- **Los 7 proxy:** están en PARCIAL_PROXY_OTRA_COMPETICION en los tres ficheros. Cada uno tiene 9 mercados PARCIAL y 14 NO_EVALUABLE, y todos conservan la disposición "elegible para evaluación prepartido". Esto da 63 parciales y 98 no evaluables, y 161 + 184 = 345.
- **Sin precios:** ningún mercado tiene precio y todos están en PRECIO_NO_CONFIRMADO.
- **Notas del proxy:** incluyen las advertencias previstas. Faltan `ALIAS SUJETO A REVISIÓN` en Sporting (aparece en b03) y `MUESTRA DÉBIL` en los equipos con n<8. Atlético (n=8), PSV (n=8), Villarreal (n=8) y Barcelona (n=8) no se marcan, y es correcto.

**Textos que aún pueden hacer leer un proxy como evidencia del partido**
1. Dos filas del `coverage_report.md` pueden leerse como avance de cobertura real.
   - Dice "Mercados examinados | 161 de 345 = 46.7%". Propongo añadir "(0% de la misma competición)" en la propia celda.
   - Dice "Con disposición registrada | 15 de 15 = 100%". Propongo "(7 solo proxy, 8 sin datos)".
2. Las etiquetas de `stats` dicen "local últimos 5" y "visitante últimos 8". Se refieren al equipo designado local o visitante en este partido, pero su muestra mezcla partidos en casa y fuera de su liga, y el término "local" sugiere stats de campo. Propongo "equipo local (muestra doméstica, casa+fuera)".
3. `resultado.1x2` PARCIAL pone "local gana 3/5" junto a "visitante gana 6/8", que vienen de ligas distintas. Sigue marcado como `estadistica_descriptiva_no_probabilidad`, pero lo más seguro es dejar 1X2 como NO_EVALUABLE en los proxies, porque compara equipos que no se han enfrentado a rivales comunes.
4. `otros.tiros` solo indica "dato de tiros presente en 5 partidos", que es disponibilidad y no estadística. Conviene no contarlo como mercado PARCIAL.

```json
{"agent":"analista-deportivo","batch_id":"b01","rows":[
{"match_id":"m-9ec6426a60e9","review_status":"REVISADO","corrections":[],"note":"Newcastle Jets - Gamba Osaka, AFC CL, men, 03:45 local. NO_INVESTIGADO_SIN_FUENTE_PERMITIDA coherente en los tres ficheros. 23 mercados NOT_CHECKED."},
{"match_id":"m-0c15b801051b","review_status":"REVISADO","corrections":[],"note":"Kyoto Sanga - Ratchaburi, AFC CL, men, 06:00 local. Estados coherentes; sin datos."},
{"match_id":"m-652b82fc3ca3","review_status":"REVISADO","corrections":[],"note":"Pohang - Johor Darul Ta'zim, AFC CL, men, 06:00 local. Estados coherentes; sin datos."}]}
```
```json
{"agent":"analista-deportivo","batch_id":"b02","rows":[
{"match_id":"m-fef50009982d","review_status":"REVISADO","corrections":[],"note":"Shanghai SIPG - Daejeon Citizen, AFC CL, men, 06:00 local. Estados coherentes; sin datos."},
{"match_id":"m-23a8afef592b","review_status":"REVISADO","corrections":[],"note":"Portimonense U23 - Academico Viseu U23, categoría u23, 06:00 local. Estados coherentes; el proxy no aplica a sub-23."}]}
```
```json
{"agent":"analista-deportivo","batch_id":"b03","rows":[
{"match_id":"m-97cb0716e4dc","review_status":"REVISADO","corrections":["renombrar etiquetas 'local/visitante últimos n' como muestra doméstica casa+fuera","1X2 proxy a NO_EVALUABLE"],"note":"Lens (F1, n=6) - Sporting (Sp Lisbon, P1, alias, n=8). PARCIAL_PROXY coherente, con MUESTRA DÉBIL (Lens n=6) y ALIAS SUJETO A REVISIÓN (sporting) en la nota."},
{"match_id":"m-d89de9c16489","review_status":"REVISADO","corrections":[],"note":"Sabah - Slavia Praha, UEFA CL, men, 12:45 local. NO_INVESTIGADO coherente; Azerbaiyán y Chequia sin cobertura de Football-Data."}]}
```
```json
{"agent":"analista-deportivo","batch_id":"b04","rows":[
{"match_id":"m-26124a15db3b","review_status":"REVISADO","corrections":["renombrar etiquetas 'local/visitante últimos n'","1X2 proxy a NO_EVALUABLE"],"note":"Atlético (Ath Madrid, alias, n=8) - Man United (E0, alias, n=6). PARCIAL_PROXY coherente; nota con MUESTRA DÉBIL (Man United n=6) y sin árbitro designado."},
{"match_id":"m-56d70359455c","review_status":"REVISADO","corrections":["renombrar etiquetas 'local/visitante últimos n'","1X2 proxy a NO_EVALUABLE"],"note":"Villarreal (SP1, n=8) - Napoli (I1, n=6). PARCIAL_PROXY coherente; MUESTRA DÉBIL (Napoli n=6)."}]}
```
```json
{"agent":"analista-deportivo","batch_id":"b05","rows":[
{"match_id":"m-7fbfa4899ff4","review_status":"REVISADO","corrections":["renombrar etiquetas 'local/visitante últimos n'","1X2 proxy a NO_EVALUABLE","no contar otros.tiros como mercado PARCIAL (solo indica disponibilidad)"],"note":"RB Leipzig (D1, n=5) - PSV (N1, alias, n=8). PARCIAL_PROXY coherente; MUESTRA DÉBIL (Leipzig n=5)."},
{"match_id":"m-837c7443671e","review_status":"REVISADO","corrections":["renombrar etiquetas 'local/visitante últimos n'","1X2 proxy a NO_EVALUABLE"],"note":"Inter (I1, alias, n=6) - Club Brugge (B1, n=8). PARCIAL_PROXY coherente; MUESTRA DÉBIL (Inter n=6)."}]}
```
```json
{"agent":"analista-deportivo","batch_id":"b06","rows":[
{"match_id":"m-c585811d2f7b","review_status":"REVISADO","corrections":["renombrar etiquetas 'local/visitante últimos n'","1X2 proxy a NO_EVALUABLE"],"note":"Galatasaray (T1, n=7) - Barcelona (SP1, n=8). PARCIAL_PROXY coherente; MUESTRA DÉBIL (Galatasaray n=7)."},
{"match_id":"m-e58658a3f614","review_status":"REVISADO","corrections":[],"note":"Viking - Bayern München, UEFA CL, men, 15:00 local. NO_INVESTIGADO coherente: Viking (Noruega) no está en las ligas de Football-Data aunque Bayern sí resuelva."}]}
```
```json
{"agent":"analista-deportivo","batch_id":"b07","rows":[
{"match_id":"m-fa26ce1cb71b","review_status":"REVISADO","corrections":["renombrar etiquetas 'local/visitante últimos n'","1X2 proxy a NO_EVALUABLE"],"note":"Arsenal (E0, n=6) - Lille (F1, n=6). PARCIAL_PROXY coherente; MUESTRA DÉBIL (ambos n=6)."},
{"match_id":"m-316ec30a5d4e","review_status":"REVISADO","corrections":[],"note":"Lens U19 - Sporting U19, UEFA Youth League, youth, 07:00 local. NO_INVESTIGADO coherente; el proxy no aplica a juveniles."}]}
```

**Hallazgos pendientes**
- Las dos filas del informe de cobertura que pueden leerse como avance real (puntos 1 anterior).
- Etiquetas "local/visitante últimos n" (punto 2), 1X2 y `otros.tiros` como mercados PARCIAL (puntos 3–4).
- Los 15 partidos tienen el calendario de una sola fuente. El informe lo dice y lo cuantifica, "0 con verificación suficiente para selección final".
- El universo está truncado: "apwin 2026-10-13: 15 accesibles de 166 declarados". El informe ya lo advierte, así que no se puede hablar de la jornada completa.
- Sigue pendiente todo el contexto deportivo (bajas, alineaciones, árbitro, cuotas). Ninguna fuente permitida lo cubre, y no lo reconstruyo de memoria.
- El alias "sporting" sigue sujeto a revisión y es global, no contextual.