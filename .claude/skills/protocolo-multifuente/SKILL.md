---
name: protocolo-multifuente
description: Catálogo de fuentes de fútbol y protocolo obligatorio de consulta multifuente (calendario, forma, córners, tarjetas, cuotas, lesiones) con registro auditable de fuentes. Cárgala al descubrir partidos, verificar datos o cuando una skill/agente de picks necesite saber qué fuentes consultar y cómo registrarlas. Extiende a cobertura-exhaustiva-picks.
---

# Protocolo multifuente (SofaScore y APWin NO son fuentes dominantes)

Principio: consultar una fuente = abrir la ficha/tabla/sección concreta y extraer el dato. Una portada no cuenta. Nunca inventar el contenido de una página que no se pudo leer. Cobertura variable por liga: ninguna fuente lo cubre todo.

## 1. Catálogo

| Uso | Fuentes |
|---|---|
| Calendario/descubrimiento (todas, por jornada) | Flashscore `flashscore.com`, Soccerway `soccerway.com`, worldfootball.net, BetExplorer `betexplorer.com/football/`, FotMob `fotmob.com`; además SofaScore `sofascore.com` y APWin `apwin.com` si aportan |
| Oficiales (prioridad en horario/estado) | LaLiga `laliga.com`, Liga Portugal `ligaportugal.pt`, AFA `afa.com.ar`, Liga Profesional `ligaprofesional.ar`, CBF `cbf.com.br`; para otras ligas, buscar organizador/federación y web del club |
| Forma, resultados, H2H | Flashscore, Soccerway, BetExplorer, FotMob, SofaScore, APWin, SoccerStats `soccerstats.com`, worldfootball.net |
| Avanzadas | FootyStats `footystats.org` (goles/córners/tarjetas), Understat `understat.com` y FBref `fbref.com/en/` (solo ligas cubiertas), Football-Data `football-data.co.uk` (histórico, no precios actuales) |
| Córners | FootyStats, Flashscore, FotMob, Soccerway, SofaScore, APWin; si no bastan, otros proveedores o datos oficiales |
| Tarjetas/disciplina | FootyStats, Flashscore, Soccerway, SofaScore, APWin, OddAlerts `oddalerts.com/referees`, RefsRadar `refsradar.com` (cobertura limitada) |
| Cuotas | OddsPortal `oddsportal.com/football/`, Oddschecker `oddschecker.com/football`, BetExplorer; casa que ofrece el precio objetivo |
| Lesiones/sanciones/alineaciones | Comunicados oficiales de clubes/competición, Transfermarkt `transfermarkt.com`, FotMob, prensa local fiable |

## 2. Mínimos operativos (requisitos de investigación, no citas decorativas)

- **Por jornada:** intentar los calendarios de Flashscore, Soccerway, worldfootball.net, BetExplorer y FotMob (+ SofaScore/APWin + fuentes oficiales). Consultar solo SofaScore/APWin no completa el calendario.
- **Por partido que avanza a evaluación:** ≥3 fichas pertinentes de proveedores distintos con datos útiles (+ oficial si hace falta confirmar el encuentro). Estadísticas esenciales verificadas con un segundo origen.
- **Por selección candidata a ticket final:** partido/estado/mercado verificados; estadísticas clave contrastadas; cuotas en ≥2 fuentes comparables (registrar sustituciones); bajas importantes revisadas; fecha y fuente de cada cifra; limitaciones declaradas.
- Cifra sospechosa (ceros, medias incompatibles, muestra incompleta): contrastar con otro origen; si no se confirma, no usarla como evidencia.
- Cuota aportada por el usuario (p. ej. Triunfobet): registrar como "comunicada por el usuario", sin afirmar verificación independiente. No pedirla para empezar.
- No mezclar cuotas de casas distintas en un multiplicador como si existiera en una sola.

## 3. Fuente inaccesible

1) Registrar URL/ficha intentada y dato buscado; 2) qué se pudo y no se pudo leer; 3) buscar alternativa; 4) mantener visible la limitación. No declarar inaccesible sin intentar la sección pertinente. No decir que "el usuario puede resolverlo" salvo acción concreta real (p. ej. pegar una captura).

## 4. Registro obligatorio (tabla en cada entrega)

`Fuente | URL/ficha concreta | Dato buscado | Resultado | Estado | Valor de los datos | Discrepancias | Alternativa usada`

Estados permitidos: **Consultada y útil · Consultada con datos insuficientes · Acceso parcial · Acceso fallido · No consultada**. Solo se marca "Consultada" si hay evidencia de que se abrió y leyó contenido real en esta ejecución.

Distinguir siempre: partido no encontrado · no confirmado · no investigado · mercado no disponible · fuente inaccesible.

## 5. Calendario

Lista maestra de partidos únicos; contrastar fuentes; detectar duplicados/discrepancias; confirmar hora y zona horaria (si hay franjas definidas por el usuario, clasificar por hora de **inicio**); listar competiciones aún no examinadas; priorizar partidos con datos suficientes para mercados concretos. Sin promesa de cobertura mundial: búsqueda amplia, sistemática y auditable. Si el usuario da 2–3 candidatos cerrados solo para comparar, no reconstruir toda la jornada.
