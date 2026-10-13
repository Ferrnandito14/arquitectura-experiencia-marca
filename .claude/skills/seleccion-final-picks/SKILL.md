---
name: seleccion-final-picks
description: Orquesta el descubrimiento, la evaluación individual de TODOS los partidos confirmados de una jornada, el contraste multiagente y la decisión final de picks de fútbol (SELECCIONAR/ALTERNATIVA/SUSTITUIR/DESCARTAR/NO EVALUABLE). Usa scripts de inventario, Nivel 1 y cobertura con puerta de cobertura. Úsala cuando el usuario pida elegir, comparar, validar o sustituir picks o borradores, "analiza la jornada", "decide los mejores picks".
---

# Selección final de picks — director de decisión

Tú (la conversación principal) eres el **director de decisión**: coordinas, resuelves y decides. No hay quinto agente. Los borradores del usuario NO son picks aprobados. Ninguna apuesta es segura: son candidatos evaluados. Equipo (`.claude/agents/`): `verificador-mercados`, `analista-deportivo`, `analista-cuantitativo`, `auditor-adversarial`. Metodología: `protocolo-multifuente`, `verificacion-estadistica-futbol`, `evaluacion-probabilidad-valor` (+ `scripts/calc.py`).

## REGLA CRÍTICA
**Todo partido confirmado y elegible dentro del alcance de la jornada recibe una evaluación individual (Nivel 1) ANTES de cualquier ranking definitivo.** Descubrir cientos de partidos y profundizar en cuatro elegidos de antemano está prohibido. **No seleccionar un partido es válido; no investigarlo y afirmar que no ofrece oportunidades no lo es.** Que un partido esté *procesado* no significa que esté *evaluado suficientemente*: informa ambas cifras.

## Alcance y zona horaria
- La jornada es un **día de calendario local**; por defecto `America/Caracas` (UTC−4). Ventana = `[00:00, 24:00)` locales convertidos a UTC con `zoneinfo`. Un partido a las 00:00 UTC del 13 es del 12 local. No confundas fecha local con fecha UTC.
- Lista cerrada de 2–3 candidatos solo para comparar → no hace falta reconstruir la jornada (ve al Nivel 2 con esos candidatos), pero indícalo en el informe.
- No pidas cuotas de Triunfobet ni ligas para empezar; las que aporte el usuario se registran como "comunicadas por el usuario" (no verificadas).

## Fuentes: política de acceso (obligatoria)
`scripts/sources_policy.json` manda: **denegado por defecto**; hosts `excluida` (condiciones de uso, `robots.txt` o anti-bot) **no se consultan**; los `condicional` solo con sus límites (ritmo, nº de descargas). `common.py` lo impone en código. Identidad honesta `User-Agent: football-picks-system/0.1`; **no falsificar navegador ni evadir CAPTCHA/Cloudflare**; no guardar cabeceras sensibles. Si una fuente falla o está excluida: registrar el motivo y buscar alternativa permitida; si no hay, la limitación es parte del resultado. Revisa `docs/FUENTES-CONFORMIDAD.md`. Ampliar cobertura = obtener datos de forma legítima (API con licencia/clave, calendario aportado por el usuario con `inventory.py --manual`, autorización escrita del proveedor), no relajar la política.

## Flujo (10 pasos) con scripts
Scripts en `.claude/skills/seleccion-final-picks/scripts/` (ejecutar desde la raíz del proyecto). Todo se guarda en `runs/<fecha>/`.
1. **Descubrir** y 2. **normalizar/deduplicar/verificar**: `python3 …/inventory.py --date AAAA-MM-DD --tz America/Caracas [--manual archivo]` → `inventory.json`, `sources/` (registro bruto + `consultas.jsonl`). Estados **independientes** por partido: calendario {CONFIRMADO, NO_CONFIRMADO, DUPLICADO, FECHA_DISCREPANTE, INFORMACION_INSUFICIENTE}, encuentro {PROGRAMADO, EN_JUEGO, FINALIZADO, APLAZADO, CANCELADO, DESCONOCIDO}, elegibilidad {ELEGIBLE, NO_ELEGIBLE, PENDIENTE_DE_VERIFICAR}, análisis {PENDIENTE, EN_CURSO, COMPLETADO, NO_EVALUABLE_TRAS_INTENTOS (hubo intentos reales que fallaron o no bastaron), **NO_INVESTIGADO_SIN_FUENTE_PERMITIDA** (ninguna fuente permitida cubre el partido: no hubo consulta real)}. Se consultan los días −1/0/+1 de cada fuente y se filtra por timestamp normalizado. Nada se elimina del inventario (los no confirmados y los fuera de fecha se conservan con su disposición). **`event_status` y `discrepancies` mandan sobre `calendar_verification_status`:** CONFIRMADO se refiere a existencia/hora según las fuentes, no es un estado fiable por sí solo (la base `…con_discrepancias_abiertas` lo declara). Una sola fuente estructurada fiable basta para *entrar* al universo; una **selección final** exige `selection_calendar_verification = SUFICIENTE` (oficial o dos fuentes independientes).
3. **Revisar discrepancias** (calendario, hora, identidad) con `verificador-mercados`: **todas**, no una muestra (más una muestra de control de registros sin discrepancias).
4. **Nivel 1 universal**: `python3 …/level1.py --run runs/<fecha>` → `state.json` (cola reanudable, escritura atómica), `matrix.json/.csv`. Para cada confirmado y elegible: forma, contexto, y las familias de mercado (resultado/hándicaps; goles 1.5/2.5/3.5, BTTS, por equipo, rangos, 1.ª parte; córners; tarjetas y árbitro; tiros/a puerta/fueras de juego) con campos separados `market_availability_status`, `statistics_availability_status`, `price_verification_status`, `evaluation_status` {EVALUABLE, PARCIAL, NO_EVALUABLE, **NOT_CHECKED**}, `not_evaluable_reason`, `sources_checked`. **NOT_CHECKED ≠ NO_EVALUABLE**; no encontrar una cuota no prueba que el mercado no exista; falta de estadísticas no es cero. Un partido sin fuente permitida que lo cubra queda `NO_INVESTIGADO_SIN_FUENTE_PERMITIDA` (y uno cuyo intento real falló o no bastó, `NO_EVALUABLE_TRAS_INTENTOS`), siempre **con motivo y evidencia**, nunca omitido ni rellenado; sus mercados son `NOT_CHECKED` y `statistics_availability_status` también (`INSUFICIENTES` solo si se buscó y no bastó). «Procesado» no es «examinado»: el informe muestra «con al menos una consulta real de datos». Las frecuencias k/n y Wilson son **descriptivas, no probabilidades predictivas**; "últimos 10" no es una temporada completa. La matemática viene de `calc.py` (importada).
5. **Cobertura**: `python3 …/coverage_report.py --run runs/<fecha>` → métricas con denominadores (brutos por fuente, únicos, confirmados, no confirmados, iniciados/finalizados, evaluados, pendientes, mercados examinados, candidatos, no evaluables; % cobertura de encuentros y de mercados por separado). **Puerta de cobertura (exit≠0):** con confirmados+elegibles pendientes → **BLOQUEADO** (no hay ranking definitivo; procesa los pendientes o guarda la cola y di cuántos faltan). Con limitación sistémica (familias de mercado enteras no evaluables, o sin histórico) → etiqueta **RANKING PROVISIONAL RESTRINGIDO** y explica qué conclusiones NO se sostienen. Una nota genérica de limitaciones no desbloquea el ranking.
6. **Revisión por lotes de agentes**: `python3 …/batches.py make --run runs/<fecha>` crea lotes de tamaño calculado del volumen real, con `match_id` estables. `analista-deportivo` y `analista-cuantitativo` revisan **todas las filas** de cada lote asignado y devuelven JSON `{agent,batch_id,rows:[{match_id,review_status,corrections,note}]}`; `verificador-mercados` revisa el lote de discrepancias. Concilia con `batches.py check --results …`: ninguna fila ausente/duplicada/desconocida; fila no revisada = PENDIENTE; **un resumen por competición no es evidencia**. Si el volumen supera el contexto, divide en más lotes, nunca reduzcas el universo.
7. **Candidatos para Nivel 2** de TODA la jornada (ningún partido anterior tiene prioridad). Nivel 2 profundiza: muestras ampliadas, línea exacta, rivales comparables, localía, bajas/alineaciones, córners/tarjetas con fuentes permitidas, cuotas en ≥2 fuentes **realmente independientes** (varias casas vía un mismo agregador = una vía de datos), probabilidad *defendible* o "no estimable", riesgos, correlación.
8. **Contraste** (Ronda 2) y 9. **Resolución** del director; 10. **Informe**. Detalle abajo.
Si el trabajo se interrumpe: persistir inventario, cola y matriz; informar partidos pendientes; reanudar sin repetir consultas vigentes (caché). No declares exhaustiva la jornada ni definitivo el ranking con pendientes.

## Mecanismos de coordinación (probados en Claude Code 2.1.296; evidencia en docs/PRUEBAS-picks.md y tests/runs/)
- **Por defecto, mediada por el director (hub-and-spoke).** Lanzas especialistas con `Agent` (varias llamadas en un mismo mensaje = paralelo) y **siempre con `name`**; cada informe vuelve a ti.
- **Objeción → respuesta (verificado):** `SendMessage` con `to` = nombre del agente ya terminado lo **reanuda con su contexto** (mismo agentId) y su respuesta llega como notificación. Si el nombre no resuelve usa el agentId; si no es reanudable, relanza un `Agent` con su informe previo + la objeción.
- **Entre pares (verificado, no es el flujo base):** los agentes tienen `SendMessage` y al reanudarse ven un roster de agentes con nombre; uno escribió a otro y recibió respuesta directa. El director sigue repartiendo objeciones y decidiendo. Registra solo los mensajes y respuestas que realmente ocurrieron.
- **Agent Teams** (experimental): NO activado ni necesario; no lo actives sin explicar antes el cambio.
- Los subagentes no ven tu conversación ni tus skills: todo contexto va en el prompt (rutas de scripts, `match_id`, política de fuentes, formato de entrega). Pueden heredar un "modo plan" (solo lectura) del que los lanza: pídeles lecturas por tubería y que no escriban archivos; los scripts y tú persisten los resultados.

**Plantilla de delegación (rellena):**
```
CONTEXTO: [fecha local America/Caracas + ventana UTC; DATOS REALES o "EJEMPLO — NO REAL, solo fixture://"]
POLÍTICA DE FUENTES: sources_policy.json; UA football-picks-system/0.1; sin evadir anti-bot; excluidas = no consultar.
MATERIAL: [runs/<fecha>/batches.json lote bXX → match_ids; matrix.json] (no leas EXPECTATIVAS ni otros tests/)
TU TAREA: [rol + qué hacer con CADA fila del lote] ; CÁLCULOS: scripts/calc.py (no a mano)
ENTREGA: JSON de revisión por fila (match_id, review_status, corrections, note) + tabla de registro de fuentes (8 campos) + limitaciones.
```
**Plantilla de objeción (SendMessage):**
```
AFIRMACIÓN CUESTIONADA: … · EVIDENCIA: [cita + fuente] · PREGUNTA: … · IMPACTO SOBRE LA DECISIÓN: alto/medio/bajo
Responde ≤10 líneas: RESPUESTA | EVIDENCIA | CAMBIO EN TU ESTADO DEL CANDIDATO.
```

## Ronda 2 y resolución (decide SIEMPRE tú)
`auditor-adversarial` ataca los finalistas **y** audita la cobertura: muestra de partidos que no avanzaron, mercados poco populares, competiciones con menos cobertura, fuentes defectuosas, descartes y no evaluables materiales (la muestra no sustituye la evaluación universal). El director envía las objeciones con la plantilla; no se exige unanimidad: pesa la calidad y pertinencia de la evidencia. **Tercera comprobación** solo si un dato crítico concreto puede cambiar la decisión (una consulta dirigida, no una ronda nueva). No prolongues el debate.

Responde por separado: **(1) ¿qué selección parece más probable? (2) ¿cuál tiene mejor relación probabilidad/cuota? (3) ¿cuál es la mejor alternativa global? (4) ¿qué se sustituye o descarta? (5) ¿qué no puede evaluarse y por qué?** Una selección probable con precio desfavorable no es valor. Sin probabilidad defendible → "no estimable", sin EV. Sin precio verificado en ≥2 vías independientes → "fundamento deportivo, sin valor económico confirmado". Una combinada no tiene valoración económica completa si falta cuota confirmada de algún componente; multiplicador solo con cuotas de la misma casa (`calc.py combo`); declarar correlación (mismo partido ⇒ dependiente). No es obligatorio recomendar apuestas ni completar un número de picks.

Estados: **SELECCIONAR · MANTENER COMO ALTERNATIVA · SUSTITUIR · DESCARTAR · NO EVALUABLE** (con motivo).

## Informe final (empieza por la decisión)
A. Veredicto · B. Tabla de candidatos (mercado, cuota verificada y vía, fundamento, riesgo, decisión) · C. Evidencia decisiva · D. Contraste entre agentes (mecanismo realmente usado) · E. Fuentes realmente consultadas / no consultadas por política · F. Riesgos y alternativas · G. Estado de validación. **Más** la tabla de cobertura (denominadores y %), qué calcularon los scripts y qué revisaron los agentes, y la etiqueta **RANKING PROVISIONAL RESTRINGIDO** si corresponde. No presentes un resultado parcial como exhaustivo.

## Reglas de integridad
No simules visitas, herramientas ni conversaciones; no inventes datos, cuotas ni probabilidades; no uses memoria como dato actual. Datos obtenidos antes de la política de conformidad (p. ej. endpoints excluidos) no se reutilizan como evidencia. No toques el seguimiento patrimonial (`reto-de-90-dias-20`); respeta sus reglas de honestidad si ambas skills están activas. Sin push a GitHub sin autorización.
