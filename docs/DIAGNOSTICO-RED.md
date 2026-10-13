# Diagnóstico de red (2026-10-12, contenedor cloud de Claude Code)

Sin tokens ni cabeceras sensibles. Método: por capa y por dominio, GET de solo lectura con límite de 10 s.

| Capa | Herramienta | Resultado observado |
|---|---|---|
| Proxy de salida (CONNECT) | `curl https://<dominio>/` (apex y `www.`) | **403 "CONNECT tunnel failed"** en los 22 dominios deportivos probados (flashscore, soccerway, worldfootball, betexplorer, fotmob, sofascore, apwin, laliga, ligaportugal, afa, ligaprofesional, cbf, soccerstats, footystats, understat, fbref, football-data.co.uk, oddalerts, refsradar, oddsportal, oddschecker, transfermarkt). El estado del proxy lista esos hosts como `connect_rejected`. |
| DNS local | `getent hosts` | Sin resolución para los 22 dominios deportivos; sí para `github.com` y `code.claude.com` (tráfico permitido). |
| Herramienta WebFetch | `WebFetch` | `getaddrinfo ENOTFOUND <dominio>` (flashscore, worldfootball, fbref, oddsportal): falla en resolución propia, capa distinta del proxy de curl. |
| Buscador | `WebSearch` | Funciona, pero solo devuelve listados de resultados (no fichas); en la prueba solo devolvió páginas antiguas de Rotowire. No sustituye la lectura de fichas. |
| Control positivo | `curl code.claude.com` | HTTP 302 (el egress funciona para dominios permitidos). `github.com` responde (301/400 según ruta). |

**Conclusión:** bloqueo deliberado por política de dominios a nivel de proxy (CONNECT 403) y de resolución, no caída general ni TLS ni respuesta del servidor. No es un fallo de los sitios.

**Qué desbloquearía (lo cambia la persona, no el agente):** en el entorno cloud, *Network access → Allowed domains* (ver https://code.claude.com/docs/en/cloud-environments#network-access), añadiendo estos dominios (y sus subdominios usados):
`flashscore.com, soccerway.com, worldfootball.net, betexplorer.com, fotmob.com, sofascore.com, apwin.com, laliga.com, ligaportugal.pt, afa.com.ar, ligaprofesional.ar, cbf.com.br, soccerstats.com, footystats.org, understat.com, fbref.com, football-data.co.uk, oddalerts.com, refsradar.com, oddsportal.com, oddschecker.com, transfermarkt.com`
(Algunos sitios pueden además bloquear bots o exigir JavaScript: eso solo se sabrá al probar.)


## Actualización 2026-10-13 (tras autorizar los dominios en el entorno)
Capa de red del entorno: **abierta** (19 de 22 dominios responden 200/301 con el User-Agent honesto `football-picks-system/0.1`). Lo que sigue bloqueado ya no es la red del contenedor sino decisiones de los propios sitios:

| Fuente | Resultado con UA honesto | Consecuencia |
|---|---|---|
| soccerstats.com | 403 con desafío Cloudflare ("Just a moment") ya en `robots.txt` | Excluida; no se evade. |
| worldfootball.net, oddschecker.com | 403 (Cloudflare) en la fase previa | No revisadas ⇒ denegadas. |
| footystats.org, fbref.com | 403 anti-bot en la fase previa | No revisadas ⇒ denegadas. |
| cbf.com.br | Error TLS (`unable to get local issuer certificate`) en la fase previa | Pendiente de revisar; no se desactiva la verificación TLS. |
| fotmob.com, betexplorer.com, transfermarkt.com, understat.com | Responden, pero sus condiciones/`robots.txt` prohíben el acceso automatizado | **Excluidas por política**, no por red (ver `docs/FUENTES-CONFORMIDAD.md`). |
| football-data.co.uk, apwin.com | 200 | Condicionales (ritmo y topes en la política). |

Lección: «la red está abierta» ≠ «se puede consultar». La autorización de dominios del entorno no sustituye la revisión de condiciones de uso de cada proveedor.
