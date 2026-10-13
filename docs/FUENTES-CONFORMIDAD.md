# Conformidad de fuentes para acceso automatizado (revisión del 2026-10-12)

Alcance: qué sitios puede consultar **de forma automatizada** este sistema. Se leyeron `robots.txt` y las condiciones de uso enlazadas desde cada sitio. **No es asesoría legal**; ante duda, la fuente queda denegada. La política ejecutable es `.claude/skills/seleccion-final-picks/scripts/sources_policy.json` (denegado por defecto; `common.py` la impone).

Identidad: `User-Agent: football-picks-system/0.1`. No se falsifica un navegador y no se evaden CAPTCHA, Cloudflare ni restricciones de acceso.

| Fuente | Estado | Evidencia |
|---|---|---|
| FotMob | **EXCLUIDA** | `fotmob.com/tos.txt`: prohíbe scraping y "systematic, regular, or bulk retrieval of data" con robots/spiders; `robots.txt`: `Disallow: /api/*`. |
| BetExplorer (Livesport) | **EXCLUIDA** | `terms-of-service.php`: no "embedding, aggregating, scraping or recreating" el contenido sin consentimiento; no cargar el servidor con peticiones automatizadas; `robots.txt` desautoriza `/*?year=`, `/*?month=`. |
| Transfermarkt | **EXCLUIDA** | `intern/anb` §11.1: "not permitted to access or copy the Digital Content using bots, spiders, screen scraping or other automated processes" (aunque `robots.txt` permita `/`). |
| Understat | **EXCLUIDA** | `robots.txt`: `Disallow: /`. |
| SoccerStats | **EXCLUIDA** | Con el UA honesto responde con un desafío Cloudflare ("Just a moment"); no se evade. |
| Football-Data | CONDICIONAL | CSV gratuitos "for use with spreadsheet applications"; uso destinado a particulares, no a productos comerciales o de entrenamiento con bots/scrapers/IA. Se usan solo ficheros CSV concretos (`fixtures.csv`, temporadas), ≥3 s entre descargas, tope de 20 por ejecución, análisis privado. `robots.txt` permite todo. |
| APWin | CONDICIONAL | `robots.txt` permite la portada (prohíbe `/calendar/*`, `/search/*`, `/s/*`); sus términos no contienen cláusula explícita de acceso automatizado pero reservan derechos sobre el contenido. Solo la portada con `?date=` (3 páginas por ejecución, ≥5 s), sin rastreo ni llamadas de cliente. |
| Flashscore, Soccerway, SofaScore, OddsPortal, Oddschecker, FootyStats, FBref, RefsRadar, OddAlerts, worldfootball.net, oficiales (LaLiga, Liga Portugal, AFA, CBF, UEFA, EFL, DFB…) | NO REVISADA → denegada | Algunas devuelven solo JavaScript o desafíos anti-bot; ninguna se ha revisado en términos. Activarla exige revisarla y registrarla en la política. |

## Consecuencias para la cobertura (2026-10-13, Caracas)
- Con las vías permitidas solo se obtienen **240 registros únicos** (Football-Data 199, todos fuera de la jornada; APWin 41, de los cuales 15 caen en la ventana local) y **ninguna fuente permitida cubre sus estadísticas** (Champions League, AFC Champions League, ligas juveniles). Las 15 evaluaciones de Nivel 1 quedan `NO_EVALUABLE_TRAS_INTENTOS` con motivo y evidencia. El ranking es **PROVISIONAL RESTRINGIDO** (ver `runs/2026-10-13/coverage_report.md`).
- La cobertura exhaustiva real exige datos obtenidos legítimamente: una API deportiva con licencia/clave, un calendario/CSV aportado por la persona usuaria (`inventory.py --manual`), o autorización escrita del proveedor. Relajar esta política no es una opción de implementación.

## Datos anteriores a esta revisión
En una fase previa de pruebas, agentes del sistema consultaron FotMob (`/api/`), el endpoint AJAX de BetExplorer, SoccerStats y Transfermarkt con un User-Agent de navegador. Esa fase fue anterior a esta revisión de conformidad: sus resultados **no se reutilizan como evidencia** ni en el pipeline ni en las decisiones, y se conservan solo como registro histórico de lo ocurrido (`tests/runs/`, informes del 2026-10-12). El comportamiento descrito (p. ej. cuotas O/U obtenidas por un agente y vacías para otro en el endpoint de BetExplorer) no se reprodujo: reproducirlo implicaría volver a consultar un host excluido.
