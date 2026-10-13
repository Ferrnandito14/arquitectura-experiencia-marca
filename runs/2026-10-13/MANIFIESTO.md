# MANIFIESTO — ejecución real 2026-10-13 (America/Caracas) · v2.4
Todo lo siguiente sale de `inventory.json`, `state.json`, `coverage.json`, `batches.json`, `reviews_raw/` y `sources/consultas.jsonl`. La clave de apifootball nunca aparece (censurada en los registros por `common.redact_url`).

## Partidos por estado
- Registros brutos por fuente: apifootball 748 · apwin 313 · football-data 199 · duplicados dentro de fuente: 0.
- Únicos: 1012 · calendario CONFIRMADO 1009 (verificación SUFICIENTE para selección final: 243) · FECHA_DISCREPANTE 3.
- No elegibles prepartido (todas las causas): 690 · iniciados/finalizados: 189.
- **Requieren evaluación (confirmados y elegibles): 319.** De ellos: 285 con consulta real de datos (= 272 evaluados con suficiencia + 13 con intento insuficiente; por tipo de historial: misma competición 138, historial propio mixto 147) y 34 SIN fuente permitida (NO_INVESTIGADO, sin ninguna consulta de datos). 285 + 34 = 319. Con verificación de calendario suficiente: 129; con una sola fuente de calendario: 190.
- **Universo truncado:** APWin 12-oct 11 de 15 declarados; APWin 13-oct 167 de 172 declarados → los partidos contados son una cota inferior; nunca «la jornada completa».
- Mercados: 7337 posibles (319×23) · examinados 6555 (89.3 %) · NOT_CHECKED 782 · evaluables/parciales 2380 · NO_EVALUABLE 4175 (huecos de datos, p. ej. córners/tarjetas sin cobertura).
- Veredicto de la puerta de cobertura: **RANKING PROVISIONAL RESTRINGIDO** (exit 4): hay partidos sin fuente permitida y el universo está truncado.

## Lotes e integridad
- 11 lotes para 319 partidos + lote de discrepancias (30). Conciliación `batches.py check` sobre `reviews_raw/all_results.json`: **ok=True · faltan 0 · duplicados 0 · desconocidos 0 · pendientes 0** · correcciones/advertencias registradas en filas: 443.
- Cada partido revisado por analista-deportivo y analista-cuantitativo; los 30 con discrepancia, además por verificador-mercados. Resultados en `reviews_raw/batch/<lote>_<agente>.json`.
- Limitación: las fichas son compactas (~1.6 KB); los agentes de lote trabajaron solo con ellas, sin fuentes externas. 3 partidos de Zambia (NAPSA–Nkana, Green Eagles–Red Arrows, Nchanga–Trident) quedan sin hora resuelta (apifootball 14-oct 13:00Z vs APWin 14-oct 00:00Z) y no pueden ser picks.

## Agentes invocados
- Nivel 2 (sobre `finalists.json`, 21 partidos): verificador-mercados, analista-deportivo, analista-cuantitativo, auditor-adversarial → informes en `reviews_raw/level2/`.
- Revisión por lotes: 22 agentes de lote (11 lotes × deportivo y cuantitativo) + 1 verificador (discrepancias) = 23 respuestas conciliadas.
- Auditoría adversarial final sobre los borradores regenerados: `reviews_raw/level2/auditor_ronda2.md` (agente nuevo: no es continuación por SendMessage de los agentes anteriores; ese hilo se perdió en los reinicios del worker).
- Combinada de la persona usuaria (Inter–Brugge más de 1.75 + Viking–Bayern menos de 7, ×1.27): 3 agentes más (deportivo, cuantitativo, auditor adversarial) → `reviews_raw/level2/usuario_*.md`; análisis en `ANALISIS-combinada-usuario.md` y `user_tickets_eval.md` (calculado por `custom_check.py`).
- Aviso: `apif_query.py` devolvió «sin clave» en el entorno del verificador del lote de discrepancias; ese agente leyó solo los datos crudos guardados (`sources/raw_*.json`).

## Consultas de red de los scripts (`sources/consultas.jsonl`, acumulado de la sesión)
- Descargas reales: apifootball 646 · apwin 23 · football-data 12 · servidas desde caché: apifootball 3009 · apwin 90 · football-data 133.
- Topes por ejecución respetados (apifootball 700, apwin 48 páginas, football-data 20). Ningún host excluido consultado.
- Sondeos manuales previos de condiciones/robots (FotMob, BetExplorer, Transfermarkt, Understat, Football-Data, APWin y otros) y pruebas de la API con `curl` (declarados aquí porque no tienen registro automático).

## Cambios de método durante la ejecución (para trazabilidad)
- Historial por equipo: prefiere la MISMA competición si hay ≥6 partidos; excluye amistosos; etiqueta `history_kind`.
- Tickets: patas con cuota real exigen ≥4 casas (rankings ≥3); calendario con 2 fuentes; sin juveniles/sub-23/reservas; un partido no puede estar en dos multiplicadores; ≥2 borradores por multiplicador.
- Vetos del director en `vetoes.json` (18 entradas: 6 de Nivel 2, 2 de la revisión por lotes y 10 del auditor de ronda 2).
- Variante `--champions` (solo UEFA Champions League, pisos relajados: apoyo 0.45, equipo 0.35) y ranking general por familia de multiplicador; no se propone ningún ticket sin al menos una cuota real.

## Puertas de calidad aplicadas a los tickets (decisión de la persona usuaria)
- Veracidad: 28 mercados bloqueados automáticamente por avisos graves de los agentes de lote (listados en `tickets.json` → `bloqueadas_por_calidad`).
- Representatividad: 2679 patas con historial mixto fuera de los tickets y rankings principales; las de Champions van a las variantes `seguridad_champions` y `amplio_champions`.
- Amplio: diversidad relajada (solape ≤60 %, pata repetida ≤3 veces) porque con historial de la misma competición hay pocas combinaciones.
