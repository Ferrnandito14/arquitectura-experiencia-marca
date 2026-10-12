# Resultados reales de pruebas (2026-10-12, contenedor cloud)

**Limitación global:** todas las webs deportivas (Flashscore, Soccerway, worldfootball, BetExplorer, FotMob, OddsPortal, FootyStats, LaLiga…) están bloqueadas por la política de red del entorno (proxy 403 en CONNECT / DNS ENOTFOUND en WebFetch). WebSearch devolvió solo páginas antiguas de Rotowire. Para habilitarlas: ajustar *Network access* del entorno en la nube (Allowed domains).

| Prueba | Estado | Detalle |
|---|---|---|
| Carga de agentes/skills | OK | `claude -p` listó los 4 agentes y las 4 skills de proyecto + `cobertura-exhaustiva-picks` y `reto-de-90-dias-20` (cuenta). |
| `calc.py` | OK | implied/novig/ev/combo/joint/freq ejecutados; `combo 1.12 1.12` = 1.2544 (coincide con el ejemplo de `reto-de-90-dias-20`). |
| Fuente inaccesible (parcial de A) | OK | `verificador-mercados` real intentó Flashscore, Soccerway, worldfootball y LaLiga: registró "Acceso fallido" con error exacto, sin inventar partidos, "fuente inaccesible" ≠ "partido no encontrado". Defecto observado: solo 1 URL por fuente y no intentó BetExplorer/FotMob/SofaScore/APWin (marcadas "No consultada"). |
| A cobertura multifuente con datos | NO EJECUTADA | Sin acceso de red a las fuentes. |
| B córners/tarjetas | NO EJECUTADA | Ídem. |
| C cuotas (2 fuentes) | NO EJECUTADA | Ídem. |
| D comparación BTTS vs victoria | NO EJECUTADA | Requiere datos y cuotas reales. |
| E desacuerdo cuanti/deportivo | NO EJECUTADA (solo aritmética) | `calc.py` cubre la parte de alta probabilidad vs precio; la resolución por el director no se probó. |
| F sustitución de borradores | NO EJECUTADA | Requiere búsqueda de alternativas con datos. |
| G cierre en 2 rondas | NO EJECUTADA | Requiere una ejecución completa. |
| Mensajería directa entre agentes | NO PROBADA | Agent Teams no habilitado; la coordinación diseñada es mediada por el director (SendMessage a agentes con nombre). |
