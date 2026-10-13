# MANIFIESTO — ejecución real 2026-10-13 (America/Caracas)
Generado desde los archivos persistidos. Commit del código al generarlo: `38fbd5d`. Todo lo siguiente sale de `inventory.json`, `state.json`, `coverage.json`, `sources/consultas.jsonl` y de las transcripciones de los agentes; nada está estimado.

## Partidos por estado
- Registros brutos por fuente: {'apwin': 41, 'football-data': 199} · duplicados dentro de fuente: 0
- Únicos: 240 · calendario CONFIRMADO: 240 (verificación SUFICIENTE para selección final: 0) · no confirmados: 0
- No elegibles prepartido (todas las causas): 225 · iniciados/finalizados: 8
- Requieren evaluación (confirmados y elegibles): 15 → estados: {'NO_INVESTIGADO_SIN_FUENTE_PERMITIDA': 8, 'PARCIAL_PROXY_OTRA_COMPETICION': 7}
- Universo truncado: True → UNIVERSO TRUNCADO: apwin 2026-10-12: 11 accesibles de 15 declarados; apwin 2026-10-13: 15 accesibles de 166 declarados; apwin 2026-10-14: 15 accesibles de 126 declarados — los partidos contados son una cota inferior; nunca «la jornada completa»
- Mercados: 345 (15×23) · examinados 161 (de ellos proxy de otra competición 161; misma competición 0) · NOT_CHECKED 184 · parciales 63 · NO_EVALUABLE 98
- Veredicto de la puerta de cobertura: **RANKING PROVISIONAL RESTRINGIDO** (exit 4)

## Lotes e integridad
- Lotes: 7 para 15 partidos (+ lote de discrepancias con 2). Conciliación `batches.py check`: ok=True · por agente: {'analista-cuantitativo': {'asignadas': 15, 'revisadas': 15}, 'analista-deportivo': {'asignadas': 15, 'revisadas': 15}, 'verificador-mercados': {'asignadas': 2, 'revisadas': 2}} · faltan 0 · duplicados 0 · desconocidos 0 · pendientes 0 · correcciones registradas en filas: 13

## Agentes invocados en la ejecución real (cumplimiento de la política)
| name (no sobrevive a reinicios) | agentId | tipo | respuestas | herramientas usadas |
|---|---|---|---|---|
| verif3 | acafd2dd7768ac2a8 | verificador-mercados | 5 | {'Bash': 20} |
| depor3 | af234e15264a6f797 | analista-deportivo | 6 | {'Bash': 19} |
| cuanti3 | aeefb729649942410 | analista-cuantitativo | 5 | {'Bash': 10, 'Read': 2} |
| audit4 | a98b924bde4ab8883 | auditor-adversarial | 3 | {'Bash': 35, 'Read': 4} |
- 0 llamadas WebFetch/WebSearch. Consultas de red de los agentes: `audit4` 2 (`curl -A football-picks-system/0.1` a football-data.co.uk, host condicional); `verif3`, `depor3`, `cuanti3`: 0. Ningún host excluido consultado por agentes.
- `Agent` lanzados: 4 (verif3, depor3, cuanti3 en paralelo; audit4). `SendMessage` del director ENTREGADOS: 11 (Ronda 2: 3 por nombre; Ronda 3: 4 por agentId; revisión final: 4 por agentId). FALLIDOS: 4 por nombre tras el reinicio del proceso (`No agent named … is reachable`). Mensajería entre pares: no se usó en la ejecución real.
- Rondas: R1 revisión por lotes (3 agentes) → R2 auditor + 3 objeciones → R3 re-verificación del proxy + re-auditoría → revisión final por lotes + auditoría final. Tercera comprobación excepcional: la R3 (cambio material por hallazgo del auditor).

## Consultas de red de los scripts (`sources/consultas.jsonl`, 100 líneas)
- Descargas por red: {'football-data': 12, 'apwin': 4} · servidas desde caché: {'football-data': 41, 'apwin': 21} · robots.txt: {'www.football-data.co.uk': 13, 'www.apwin.com': 9}
- Por ejecución de `inventory.py`/`level1.py` ningún proveedor superó su tope (football-data ≤20; apwin ≤3 páginas). En toda la sesión APWin sumó 4 descargas de red (1.ª ejecución previa al cambio a consulta por día: portada `/`; después `?date=` 12, 13 y 14).
- Sondeos manuales de la Fase 0 (anteriores al cliente con política; no están en `consultas.jsonl`): robots.txt y condiciones de FotMob, BetExplorer, Transfermarkt, Understat, Football-Data, APWin y otros; portadas de calendario con `curl` y UA honesto para decidir la política (incluidas APWin `?date=2026-10-13` y su página de términos). Se declaran aquí porque no hay registro automático.

## Fase previa a la política de conformidad (NO usada como evidencia)
Agentes `verif-real` (a204fd3f816df1655), `verif2` (a057533962f9c63aa), `depor2` (a0e48dc2c6da92c0b), `cuanti2` (af08ab2d7f9885c8c) consultaron FotMob (`/api/`), el AJAX de BetExplorer, SoccerStats y Transfermarkt con un User-Agent de navegador, antes de revisar `robots.txt` y condiciones. Sus resultados no se reutilizan; sus conclusiones (cuotas 1.25–1.91, k/n de C1–C4) no figuran en ninguna decisión.

## Archivos
`inventory.json`, `state.json`, `matrix.json/.csv` (570 líneas: 345 mercados + 225 filas sin evaluación para no requeridos + cabecera), `coverage.json`, `coverage_report.md`, `batches.json`, `reviews.json`, `reviews_rebatched.json`, `reviews_raw/` (revisiones originales y finales de cada agente, mapa de IDs), `previous_run_pre_fix*/` (versiones anteriores archivadas tras cada corrección), `sources/` (brutos y consultas), `cache/` (respuestas descargadas).
