# Conformidad de fuentes para acceso automatizado (revisión del 2026-10-12)

Alcance: qué sitios puede consultar **de forma automatizada** este sistema. Se leyeron `robots.txt` y las condiciones de uso enlazadas desde cada sitio. **No es asesoría legal**; ante duda, la fuente queda denegada. La política ejecutable es `.claude/skills/seleccion-final-picks/scripts/sources_policy.json` (denegado por defecto; `common.py` la impone).

Identidad: `User-Agent: football-picks-system/0.1`. No se falsifica un navegador y no se evaden CAPTCHA, Cloudflare ni restricciones de acceso.

| Fuente | Estado | Evidencia |
|---|---|---|
| FotMob | **EXCLUIDA** | `fotmob.com/tos.txt`: prohíbe scraping y "systematic, regular, or bulk retrieval of data" con robots/spiders; `robots.txt`: `Disallow: /api/*`. |
| BetExplorer (Livesport) | **EXCLUIDA** | `terms-of-service.php`: no "embedding, aggregating, scraping or recreating" el contenido sin consentimiento; no cargar el servidor con peticiones automatizadas; `robots.txt` desautoriza `/*?year=`, `/*?month=`. |
| Transfermarkt | **EXCLUIDA** | `intern/anb` §11.1: "not permitted to access or copy the Digital Content using bots, spiders, screen scraping or other automated processes" (aunque `robots.txt` permita `/`). |
| Understat | **EXCLUIDA** | `robots.txt`: `Disallow: /`. |
| SoccerStats | **EXCLUIDA (inaccesible por anti-bot)** | Con el UA honesto responde con un desafío Cloudflare («Just a moment») ya en `robots.txt`; no se evade. **Sus condiciones de uso no se han leído**: no es una exclusión por términos. |
| Football-Data | CONDICIONAL | CSV gratuitos "for use with spreadsheet applications"; uso destinado a particulares, no a productos comerciales o de entrenamiento con bots/scrapers/IA. Se usan solo ficheros CSV concretos (`fixtures.csv`, temporadas), ≥3 s entre descargas, tope de 20 por ejecución, análisis privado. `robots.txt` permite a `*` pero **bloquea por nombre a crawlers de IA** (GPTBot, ClaudeBot, Anthropic-AI, Claude-Web, PerplexityBot, CCBot…): riesgo medio-bajo que debe aceptar la persona usuaria (ver `risk_note`). |
| APWin | CONDICIONAL | `robots.txt` permite la portada (prohíbe `/calendar/*`, `/search/*`, `/s/*`); sus términos no contienen cláusula explícita de acceso automatizado pero reservan derechos sobre el contenido. Solo la portada con `?date=` (3 páginas por ejecución, ≥5 s), sin rastreo ni llamadas de cliente. Sus términos son los de la suscripción Premium y declaran prohibido «any unauthorized, commercial or non-commercial use»: riesgo medio que debe aceptar la persona usuaria. **El HTML solo trae la página 1 de una lista paginada** (13-oct: 15 accesibles de 166 declarados). |
| Flashscore, Soccerway, SofaScore, OddsPortal, Oddschecker, FootyStats, FBref, RefsRadar, OddAlerts, worldfootball.net, oficiales (LaLiga, Liga Portugal, AFA, CBF, UEFA, EFL, DFB…) | NO REVISADA → denegada | Algunas devuelven solo JavaScript o desafíos anti-bot; ninguna se ha revisado en términos. Activarla exige revisarla y registrarla en la política. |

## Consecuencias para la cobertura (2026-10-13, Caracas)
- Con las vías permitidas solo se obtienen **240 registros únicos** (Football-Data 199, todos anteriores a la ventana; APWin 41, de los cuales 15 caen en la ventana local; **universo truncado**: APWin declara 166 para el 13-oct y solo muestra 15). De esos 15, **7** (cruces de Champions con ambos equipos en ligas que Football-Data cubre) reciben forma doméstica como **proxy parcial de otra competición**; **8** (AFC Champions League, Liga Revelação U23, Youth League, Sabah–Slavia, Viking–Bayern) quedan `NO_INVESTIGADO_SIN_FUENTE_PERMITIDA`. El ranking es **PROVISIONAL RESTRINGIDO** y no hay picks (ver `runs/2026-10-13/coverage_report.md`).
- La cobertura exhaustiva real exige datos obtenidos legítimamente: una API deportiva con licencia/clave, un calendario/CSV aportado por la persona usuaria (`inventory.py --manual`), o autorización escrita del proveedor. Relajar esta política no es una opción de implementación.

## Datos anteriores a esta revisión
En una fase previa de pruebas, agentes del sistema consultaron FotMob (`/api/`), el endpoint AJAX de BetExplorer, SoccerStats y Transfermarkt con un User-Agent de navegador. Esa fase fue anterior a esta revisión de conformidad: sus resultados **no se reutilizan como evidencia** ni en el pipeline ni en las decisiones, y se conservan solo como registro histórico de lo ocurrido (`tests/runs/`, informes del 2026-10-12). El comportamiento descrito (p. ej. cuotas O/U obtenidas por un agente y vacías para otro en el endpoint de BetExplorer) no se reprodujo: reproducirlo implicaría volver a consultar un host excluido.


## Estado de aceptación (a 2026-10-13)
| Fuente | Estado | Decisión de la persona usuaria |
|---|---|---|
| Football-Data | condicional, **ya usada** (12 descargas CSV) | **PENDIENTE** — riesgo medio-bajo: `robots.txt` bloquea por nombre crawlers de IA; el cliente se identifica con su propio UA y descarga ficheros CSV concretos para análisis privado (valoración nuestra, no un hecho jurídico). |
| APWin | condicional, **ya usada** (4 páginas públicas en la sesión) | **PENDIENTE** — riesgo medio: términos de la suscripción Premium («any unauthorized, commercial or non-commercial use is prohibited»). Paginación no ampliada. |

Observaciones de APWin: (1) el HTML incluye además un bloque JSON-LD (`SportsEvent`) con 6 partidos destacados por día; todos los del 13-oct ya estaban en el feed, así que no amplía el universo en la ventana (sí aporta 6 partidos del 12-oct no presentes en el feed); (2) para el 12-oct declara `total:15` y muestra 11 sin que se haya podido explicar la diferencia; (3) las horas del feed y del JSON-LD coinciden, pero son de la misma fuente (no independientes).

## Football-Data: lo que NO se comprobó
Que sus «ligas extra» (p. ej. Noruega, Japón, China) cubran alguno de los 8 partidos no investigados: no se evaluó. No se afirma que «ninguna fuente permitida» los cubra, solo que **no se intentó** (ningún adaptador permitido implementado).

## Actualización 2026-10-13 (decisiones de la persona usuaria y nuevas fuentes)
- **APWin — paginación AUTORIZADA** por la persona usuaria («autorizo ampliar la paginación» siempre que amplíe el calendario y permita analizar). Vía usada: el JSON público `https://www.apwin.com/api/home/calendar?date=…&locale=en&timezone=America/New_York&country=US&page=N`, el mismo que consume la propia web; `robots.txt` no lo veta (solo `/calendar/*`, `/search/*`, `/s/*`…), no requiere sesión ni evade protección alguna, UA `football-picks-system/0.1`, ≥5 s entre peticiones, tope 48 por ejecución. Resultado 13-oct: 167 accesibles de 172 declarados (antes 15 de 166).
- **apifootball (`apiv3.apifootball.com`) — CONDICIONAL.** API con clave propia de la persona usuaria (cuenta en apifootball.com, plan gratuito en período de prueba). Autenticación `APIkey` en la query; la clave se guarda fuera del repo y `common.redact_url` la sustituye por `***` en logs, caché y `Response.url` (test `SecretRedaction`). `robots.txt` del host API: 404. Pendiente: condiciones de uso (la página de términos devolvió 404) y límite de peticiones del plan (no medido; la prueba usó ~9 peticiones sin error). Recordatorio programado para la fecha de pago indicada por el panel (2026-10-28).
- Nota técnica verificada: `get_events` exige la zona **codificada** (`timezone=America%2FCaracas`); sin codificar devolvió horas desplazadas. Con la zona correcta, 118 de los 166 partidos requeridos coinciden de forma única por hora de inicio + nombre.

## Actualización 2026-10-14 — TheStatsAPI (`api.thestatsapi.com`) como segunda fuente de cuotas — CONDICIONAL
- API de pago con clave propia de la persona usuaria (plan contratado el 14-oct-2026). Autenticación por cabecera `Authorization: Bearer`; la clave NUNCA se escribe en logs, caché ni artefactos (`tsa_fetch.py` registra solo la URL sin credenciales; prueba `Cliente`).
- Términos leídos (`https://www.thestatsapi.com/terms`, actualizados 2026-04-01): uso permitido en aplicaciones y herramientas internas propias; **prohibido** compartir la clave con terceros, revender o redistribuir datos en bloque, crear un servicio competidor y almacenar datos más allá de lo necesario. Por eso el run solo guarda las respuestas de cuotas de los partidos analizados (`<run>/thestatsapi/`) y los entregables no republican la fuente como dataset. `robots.txt` solo veta rutas del sitio web (`/api/` para rastreadores), no el uso documentado de la API con clave.
- Cobertura medida el 14-oct sobre los 34 partidos: 32 emparejados (los 2 de la Copa Uruguay con Boston River y Maldonado no figuran); cuotas de Bet365, Paddy Power, BetMGM UK, Pinnacle y Betfair Exchange; córners, tarjetas, goles por equipo, 1.ª parte, hándicap europeo y remates (ver `docs/SONDA-cuotas-api.md`). Muchas líneas las cotiza una sola casa: el libro muestra `N.º de casas`.
- La fuente no documenta cómo cuenta las «tarjetas» (¿amarilla=1, roja=2?): se rotula y no se asume la regla A=1, R=2.

