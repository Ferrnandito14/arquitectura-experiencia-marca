# Pruebas — estado real (2026-10-12/13, Claude Code 2.1.296, contenedor cloud)

Tres categorías que NO se mezclan. **Ninguna prueba sintética valida la investigación deportiva real, y la ejecución real NO produjo picks** (ver «Resultado de la ejecución real»).

## 1. Pruebas unitarias y offline (código y reglas)
`python3 -m unittest discover -s tests -v` → **147 pruebas, OK** (sin red). Cubren: `calc.py` (válidos, límites, entradas inválidas con código 2 y sin trazas); robots.txt con comodines y especificidad; política de fuentes (denegado por defecto, excluidas, topes y ritmo por proveedor); cliente HTTP simulado (UA honesto, caché, `Retry-After`, backoff, anti-bot no evadido, sin cabeceras sensibles en el log, escritura atómica); zonas horarias (ventana de Caracas, bordes 03:59/04:00Z, BST/GMT y EDT/EST por fecha); normalización y deduplicación conservadora (femenino, juvenil, reservas, mismo nombre en otra competición); los cuatro estados independientes (calendario/encuentro/elegibilidad/análisis; confirmado+finalizado); base de confirmación y `selection_calendar_verification`; parser de APWin (con regresión del fallo real) y paginación; cola reanudable (corte y reanudación, `EN_CURSO`, errores recuperables → intervención); estados por mercado (`NOT_CHECKED` ≠ `NO_EVALUABLE`; `INSUFICIENTES` solo si se buscó); proxy doméstico (alias exactos, sin difusos, ambigüedad, solo equipos masculinos de primera plantilla, nota con n<8, nunca `COMPLETADO`); `calc.py` importado sin reimplementar (AST); informe de cobertura (denominadores, **puerta de cobertura que falla con un confirmado y elegible sin evaluar**, motivo+evidencia obligatorios, universo truncado, proxy ≠ suficiente, integridad inventario↔estado↔matriz); lotes con IDs estables (ausentes, duplicados, desconocidos, filas pendientes, «un resumen no es evidencia», re-asignación tras cambio de IDs); cláusulas obligatorias de la skill y del protocolo.
**Mutaciones comprobadas** (se rompió a propósito cada regla y las pruebas fallaron): puerta de cobertura, robots con comodines, `Disallow` ignorado, exclusión de fuentes, ventana local, `NO_EVALUABLE`→`PARCIAL`, y el parser antiguo de APWin (el test de regresión falla con él). Hallazgo: un primer test de regresión pasaba también con el parser antiguo; se reescribió.
`install.sh`: `--dry-run`, creación, idempotencia y argumento inválido OK (directorio temporal).

## 2. Pruebas sintéticas (datos ficticios «EJEMPLO — NO REAL», `tests/fixtures/`, evidencia en `tests/runs/`)
Flujo multiagente real con 4 agentes y solo `fixture://`, 0 llamadas web: verificador, deportivo y cuantitativo en paralelo → auditor → Ronda 2 con `SendMessage` (objeción → respuesta, con correcciones reales de cuanti/deportivo/verificador) → resolución del director → cierre en 2 rondas; fuente defectuosa detectada y descartada; sustitución de un borrador débil; mensajería entre pares verificada (deportivo → cuanti). Validan la coordinación y la lógica, no la calidad deportiva.

## 3. Ejecución REAL (jornada local 2026-10-13, America/Caracas) y su resultado
Datos reales, solo fuentes permitidas por la política. Registro completo en `runs/2026-10-13/` (inventario, cola, matriz, informe de cobertura, consultas, revisiones y MANIFIESTO).
| Etapa | Resultado real |
|---|---|
| Inventario | 240 únicos (Football-Data 199, todos anteriores a la ventana; APWin 41). **15** en la ventana local. **Universo truncado**: APWin declara 166 (13-oct) y 126 (14-oct) y el HTML permitido solo trae 15 por día. |
| Calendario | Los 15 con **una sola fuente** (APWin), 0 con verificación suficiente para selección final. Bragantino–Cruzeiro (00:00Z) = 12-oct 20:00 Caracas ⇒ fuera de la jornada. |
| Nivel 1 | 15 con disposición: **7** con forma doméstica PROXY de otra competición (`PARCIAL_PROXY_OTRA_COMPETICION`), **8** `NO_INVESTIGADO_SIN_FUENTE_PERMITIDA` (AFC Champions League, Liga Revelação U23, UEFA Youth League, Sabah–Slavia, Viking–Bayern). 0 evaluados con histórico de la misma competición. |
| Mercados | 345 = 15×23: 161 examinados (todos proxy de otra competición), 184 `NOT_CHECKED`. 0 de la misma competición. |
| Puerta de cobertura | **RANKING PROVISIONAL RESTRINGIDO** (exit 4). Sin picks, sin probabilidades, sin cuotas, sin EV. |
| Revisión por agentes | verificador (discrepancias + muestra de control de 12 + re-derivación de los 240), deportivo y cuantitativo (cada fila de cada lote), auditor adversarial (3 rondas). **Defectos reales encontrados por ellos y corregidos**: `sources_checked` aparentaba consultas inexistentes; `NO_EVALUABLE` donde correspondía `NOT_CHECKED`; clasificación de reservas (Serie B/Willem II/filiales); inventario regenerado sin conservar avance; `match_id` dependía de la categoría; estadísticas `INSUFICIENTES` sin intento; estado de partido «tras intentos» sin intentos; parser de APWin que perdía la competición; universo truncado no declarado; proxy contado como «suficiente». Recalculo independiente de 32 frecuencias k/n del proxy: 32/32 coinciden. |
| Mensajería | `SendMessage` por nombre reanuda con contexto; **los nombres no sobreviven a un reinicio del proceso de trabajo, los agentId sí** (verificado: los 4 agentes se reanudaron por ID tras el reinicio). |
| Cumplimiento | Se descubrió, al revisar `robots.txt` y condiciones, que FotMob/BetExplorer/Transfermarkt/Understat/SoccerStats no son usables de forma automatizada. **La fase previa de pruebas (antes de esa revisión) las había consultado con un User-Agent de navegador; esos datos no se reutilizan.** Descargas de red de esta ejecución: Football-Data 12 (tope 20), APWin 4 en toda la sesión (≤3 por ejecución de `inventory.py`; el tope por ejecución se respetó, ver MANIFIESTO). |

## 4. NO ejecutado (con motivo)
| Elemento | Motivo |
|---|---|
| Cobertura exhaustiva real de la jornada (cientos de partidos, córners/tarjetas/cuotas reales, dos cotizaciones comparables, comparación y sustitución con datos reales, selección final) | No existen fuentes permitidas que lo cubran; las que sí lo hacen están excluidas por sus condiciones. Requiere API con licencia, datos aportados por la persona usuaria o permiso del proveedor. |
| Paginación de APWin (`page=2…`) | Decisión de la persona usuaria (condiciones de APWin); no se amplía el tope. |
| Revisión de UEFA/AFC/Liga Portugal/FPF y de las demás fuentes «no revisadas» | Procedimiento en `docs/PROCEDIMIENTO-ALTA-FUENTE.md`; pendiente de decisión. |
| Cuotas actuales de cualquier casa | Ninguna fuente permitida las proporciona para estos partidos. |
| Verificación de la cita de uso de Football-Data (`data.php`, 2026-10-12) | Solo vista en una consulta; no hay copia guardada; el riesgo se eleva a la persona usuaria. |
| Agent Teams | No activado (experimental, no necesario). |
| `cobertura-exhaustiva-picks` y `reto-de-90-dias-20` (skills de cuenta) | No modificadas ni invocadas. |
