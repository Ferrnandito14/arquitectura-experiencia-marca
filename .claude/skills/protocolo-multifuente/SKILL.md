---
name: protocolo-multifuente
description: Catálogo de fuentes de fútbol con su estado de política de acceso (permitida/condicional/excluida), protocolo de consulta multifuente (calendario, forma, córners, tarjetas, cuotas, lesiones), recetas de acceso permitidas y registro auditable de fuentes. Cárgala al descubrir partidos, verificar datos, o cuando un agente deba saber qué fuentes puede consultar y cómo registrarlas. Extiende a cobertura-exhaustiva-picks.
---

# Protocolo multifuente (SofaScore y APWin NO son fuentes dominantes)

Consultar una fuente = abrir la ficha/tabla/sección concreta y extraer el dato. Una portada no cuenta. Nunca inventes el contenido de una página que no pudiste leer. Cobertura variable por liga: ninguna fuente lo cubre todo.

## 0. Política de acceso (manda sobre el catálogo)
- `scripts/sources_policy.json` (denegado por defecto) y `docs/FUENTES-CONFORMIDAD.md` registran, con evidencia, qué fuentes se pueden consultar de forma AUTOMATIZADA. Revisión del 2026-10-12: **excluidas** FotMob, BetExplorer, Transfermarkt (condiciones de uso), Understat (`robots.txt`), SoccerStats (desafío Cloudflare con UA honesto); **condicionales** Football-Data (CSV, uso privado, pocos ficheros) y APWin (solo portada/HTML público, 3 páginas); **no revisadas ⇒ denegadas**: Flashscore, Soccerway, SofaScore, OddsPortal, Oddschecker, FootyStats, FBref, RefsRadar, OddAlerts, worldfootball, fuentes oficiales y prensa. Una fuente se activa revisando antes `robots.txt` + condiciones y registrándola en la política.
- Identidad honesta `User-Agent: football-picks-system/0.1`. **No falsificar un navegador ni evadir CAPTCHA, Cloudflare u otras restricciones.** `robots.txt` se respeta (con comodines). Ritmo bajo por proveedor, caché, reintentos acotados, `Retry-After`. No guardar tokens ni cabeceras sensibles.
- Un agente que lea una página manualmente por su cuenta (WebFetch/Bash) debe respetar la misma política: no usar hosts excluidos aunque "funcionen". Las tablas de registro deben mostrar las fuentes excluidas como **No consultada — excluida por política**.

## 1. Catálogo (objetivo de cobertura; se usa lo que la política permite)
| Uso | Fuentes del catálogo |
|---|---|
| Calendario/descubrimiento | Flashscore `flashscore.com`, Soccerway `soccerway.com`, worldfootball.net, BetExplorer `betexplorer.com/football/`, FotMob `fotmob.com`, SofaScore `sofascore.com`, APWin `apwin.com` |
| Oficiales (prioridad en horario/estado) | LaLiga `laliga.com`, Liga Portugal `ligaportugal.pt`, AFA `afa.com.ar`, Liga Profesional `ligaprofesional.ar`, CBF `cbf.com.br`, UEFA/EFL/DFB y la federación u organizador de cada competición |
| Forma, resultados, H2H | Flashscore, Soccerway, BetExplorer, FotMob, SofaScore, APWin, SoccerStats `soccerstats.com`, worldfootball.net |
| Avanzadas | FootyStats `footystats.org`, Understat `understat.com`, FBref `fbref.com/en/`, Football-Data `football-data.co.uk` (histórico por liga con córners, tarjetas, tiros y árbitro; no sustituye precios actuales) |
| Córners | FootyStats, Flashscore, FotMob, Soccerway, SofaScore, APWin (+ Football-Data en ligas cubiertas) |
| Tarjetas/disciplina | FootyStats, Flashscore, Soccerway, SofaScore, APWin, OddAlerts `oddalerts.com/referees`, RefsRadar `refsradar.com` (+ Football-Data) |
| Cuotas | OddsPortal `oddsportal.com/football/`, Oddschecker `oddschecker.com/football`, BetExplorer; la casa concreta |
| Lesiones/alineaciones | Comunicados de clubes/competiciones, Transfermarkt `transfermarkt.com`, FotMob, prensa local fiable |
Es un catálogo de *búsqueda de datos*, no una obligación de llamar a todos por partido: se intenta lo que cubre la liga y el mercado **y la política permite**; lo demás se registra como no consultado con su motivo.

## 2. Mínimos operativos (requisitos de investigación, no citas decorativas)
- **Por jornada:** intentar los calendarios del catálogo que la política permita; consultar solo SofaScore/APWin nunca completa el calendario. Si la política deja una sola vía, el inventario queda con `confirmation_basis` débil y la cobertura se informa como limitada.
- **Por partido que avanza a Nivel 2:** hasta 3 fichas pertinentes de proveedores distintos con datos útiles, las estadísticas esenciales con un segundo origen, y la fuente oficial si hace falta confirmar el encuentro.
- **Por candidato a ticket final:** partido/estado/mercado verificados; estadísticas contrastadas; cuotas en ≥2 vías **independientes** (varias casas de un mismo agregador son UNA vía); bajas revisadas; fecha y fuente de cada cifra; limitaciones declaradas.
- Cifra sospechosa (ceros, medias incompatibles, muestra incompleta): contrastar o descartar. Cuota aportada por el usuario = "comunicada por el usuario". No mezclar casas en un multiplicador.

## 3. Fuente inaccesible y diagnóstico de red
1. Antes de marcar "Acceso fallido": intenta al menos **dos** URLs/secciones permitidas de esa fuente y registra el error literal.
2. Diagnostica la capa: DNS (`getaddrinfo ENOTFOUND`), proxy (`CONNECT tunnel failed, response 403`), TLS, HTTP del servidor, anti-bot (desafío Cloudflare), JS/parcial. No atribuyas el fallo a "dominios permitidos" sin evidencia por capa; si es política de red del entorno, nombra el dominio y dónde se autoriza (*Network access → Allowed domains* del entorno cloud: lo cambia la persona).
3. Un bloqueo anti-bot, un `robots.txt` que desautoriza o unas condiciones que prohíben el acceso automatizado **no son un fallo a esquivar**: se documentan y se busca una vía permitida.
4. Bloqueo general ⇒ no repetir decenas de peticiones; una por capa y pasar a alternativas. Si todas fallan: no declarar validada ninguna selección ni inventar datos en vivo.
5. No digas que la persona puede resolverlo salvo acción concreta real (autorizar un dominio, aportar un calendario/CSV, facilitar una clave de API con licencia, conceder permiso escrito del proveedor).

## 4. Registro obligatorio (tabla en cada entrega)
`Fuente | URL o ficha | Dato buscado | Información obtenida | Fecha de consulta | Estado | Discrepancias | Alternativa consultada`
Estados permitidos (solo estos): **Consultada y útil · Consultada con datos insuficientes · Acceso parcial · Acceso fallido · No consultada**. "Consultada" exige evidencia de contenido real leído en esta ejecución. En "Información obtenida" va el dato concreto o el error literal. Distinguir: partido no encontrado · no confirmado · no investigado · mercado no disponible · mercado **no buscado (NOT_CHECKED)** · fuente inaccesible. Datos de prueba: `fixture://…`, etiquetados "EJEMPLO — NO REAL", nunca cuentan como fuentes reales. Datos obtenidos por vías excluidas (p. ej. antes de la revisión de política) no se reutilizan como evidencia.

## 5. Calendario
Lista maestra de partidos **únicos** (`inventory.py`): nombres normalizados (minúsculas, sin acentos/sufijos) pero **sin fusionar por parecido de nombre**: categoría (masculino/femenino/juvenil/reserva), competición y hora intervienen; la ambigüedad mantiene registros separados con discrepancia. Convierte horas con `zoneinfo` (BST/EDT por fecha, no offsets fijos); conserva hora original, zona de origen (confirmada vs inferida) y hora normalizada. Estados: calendario / encuentro / elegibilidad / análisis, independientes (un partido puede estar CONFIRMADO y ya FINALIZADO). Sin promesa de cobertura mundial: búsqueda amplia, sistemática y auditable de las competiciones visibles en las fuentes permitidas.

## 6. Recetas de acceso verificadas (solo vías permitidas, 2026-10-12)
- **Football-Data:** `https://www.football-data.co.uk/fixtures.csv` (calendario de las próximas jornadas de ligas cubiertas; hora del Reino Unido, zona no declarada ⇒ *inferida*) y `…/mmz4281/<temporada>/<Div>.csv` (histórico con goles, córners `HC/AC`, tarjetas `HY/AY/HR/AR`, tiros, árbitro). Uso privado, pocos ficheros, ritmo ≥3 s. No cubre competiciones europeas ni ligas fuera de su lista.
- **APWin:** `https://www.apwin.com/?date=AAAA-MM-DD` embebe en el HTML un subconjunto de partidos (JSON de Next con `kickoffUnix` en época UTC). La web declara más partidos de los que carga el HTML; el resto llega por llamadas de cliente que **no** se usan. El día de APWin es EDT (UTC−4 en octubre). Es una vía de calendario *agregada*: sola no basta para una selección final.
- **Vías no usables hoy:** endpoints `/api/` de FotMob, páginas de fecha de BetExplorer (`?year=`), páginas de Transfermarkt, Understat, SoccerStats (ver `docs/FUENTES-CONFORMIDAD.md`).
