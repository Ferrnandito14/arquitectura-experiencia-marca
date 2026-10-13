Revisé las 15 filas de b01 a b04 a partir de los ficheros locales. No hice consultas de red. Las 15 están cerradas como REVISADO, pero con una corrección de estados propuesta (hallazgos 2 y 3). Con el modo plan activo no apliqué ningún cambio.

## (2) Hallazgos

1. **Estructura (a): coherente, con los estados separados.**
   - Cada uno de los 15 partidos tiene 23 mercados, es decir 345 en total. Cuadra con el denominador del informe de cobertura.
   - En los 345 mercados los campos son idénticos:
     - `market_availability_status`: NOT_CHECKED
     - `statistics_availability_status`: INSUFICIENTES
     - `price_verification_status`: PRECIO_NO_CONFIRMADO
     - `evaluation_status`: NO_EVALUABLE
     - `not_evaluable_reason`: "sin fuente permitida que aporte este dato para la liga"
   - Las cuatro dimensiones están en campos distintos, como pide el manual.

2. **Defecto en `sources_checked`.** Lista fotmob, betexplorer, transfermarkt, understat, soccerstats y football-data, pero las cinco primeras figuran en `attempts` como "no consultada: excluida por política".
   - football-data figura como "sin cobertura de esta liga/competición".
   - `covers()` solo comprueba `extra.div`, que es None en los 15 partidos. No se abrió ningún CSV para estos partidos.
   - Por tanto `sources_checked` aparenta una investigación que no ocurrió.
   - Corrección en `level1.py`, línea 198: `sources_checked` debe contener solo los proveedores con `resultado` que empiece por "consultada". Los demás van en un campo aparte, `sources_excluded_or_not_covering`.

3. **¿NO_EVALUABLE o NOT_CHECKED? (b).** El manual dice (SKILL de `seleccion-final-picks`, paso 4): "NOT_CHECKED ≠ NO_EVALUABLE; no encontrar una cuota no prueba que el mercado no exista; falta de estadísticas no es cero".
   - Ese mismo texto reserva "NO_EVALUABLE_TRAS_INTENTOS con motivo y evidencia de intentos" para el partido.
   - En estos 345 mercados no hubo ningún intento sobre el mercado: no se abrió ninguna ficha ni ningún feed.
   - `level1.py` ya reconoce esto en `market_availability_status` (NOT_CHECKED), pero a la vez marca `evaluation_status` = NO_EVALUABLE. Es contradictorio dentro del mismo registro.
   - Mi conclusión es que el uso actual es incorrecto en el nivel de mercado. Es correcto en el nivel de partido, donde sí hay motivo y evidencia de intentos.
   - Corrección propuesta, en `level1.py` líneas 189 a 192, rama `else`:
     - Si `provider is None or not provider.covers(match)`, poner `ev = "NOT_CHECKED"` y `reason = "no investigado: ninguna fuente permitida cubre esta competición (sin ficha ni feed abierto); no implica que el mercado no exista ni que la estadística sea 0"`.
     - Dejar NO_EVALUABLE solo cuando la fuente cubre el partido y no trae el mercado, o cuando se abrió y no sirvió.
   - **Efecto en `coverage_report.py`.** Las líneas 58 a 60 excluyen NOT_CHECKED de `examined`, así que cambiaría esto:
     - "Mercados examinados" pasaría de 345 (100%) a 0 (0%).
     - NOT_CHECKED pasaría de 0 a 345.
     - Esto corrige una cobertura de mercados hoy sobreestimada: el 100% actual cuenta como "examinados" mercados que nadie examinó.
     - El veredicto no cambia, porque `fam_ok` sigue vacío.

4. **Cifras inventadas (c): no hay.** Los 15 partidos tienen `form` vacío, `stats` y `price` vacíos, `odds` en None y `sample_note` en None. Ninguna frecuencia, cuota o probabilidad aparece en las filas.

5. **Cálculos con calc.py (d): no aplica.** No hay k/n, cuotas, probabilidades ni EV que verificar. `calc.py freq 0 0` devuelve error de uso (código 2, "N debe ser > 0").

6. **Puerta de cobertura (e).** Los datos de `coverage.json` son:
   - `exit_code`: 4
   - `pending`: 0
   - `evaluated_sufficiently`: 0
   - `systemic_families_without_any_evaluable`: resultado, goles, corners, tarjetas, otros
   - El veredicto RANKING PROVISIONAL RESTRINGIDO es correcto, porque no hay partidos pendientes (no procede BLOQUEADO) y sí hay limitación sistémica.
   - Es **necesario pero no suficiente** por sí solo. Para que sea honesto falta:
     - Declarar los 345 mercados como NOT_CHECKED (hallazgo 3).
     - Explicar qué conclusiones NO se sostienen: ningún candidato, EV ni probabilidad; ninguna selección por valor; sin cuota verificada no hay valor confirmado.
   - El informe actual solo lista las familias.
   - Resultado práctico: no se puede emitir ningún pick con base cuantitativa. Cualquier ranking sería solo sportivo y sin valor económico confirmado.

7. **Mejora opcional, no aplicada.** Football-Data tiene CSV de ligas domésticas (por ejemplo E0, D1, I1, SP1) que podrían dar forma de algunos equipos de la Champions.
   - Mezclaría competiciones y no cubre la AFC, las ligas U23 ni la Youth League.
   - Sería una muestra débil, declarada como "otra competición", y no corrige el hallazgo 3.
   - No la ejecuté. Requiere cambiar `covers()` o el `div` en el inventario.

## (1) Bloques JSON

Las 15 filas llevan la misma corrección (C1: hallazgo 2; C2: hallazgo 3).

```json
{"agent":"analista-cuantitativo","batch_id":"b01","rows":[
{"match_id":"m-2e91a798c280","review_status":"REVISADO","corrections":["C1 sources_checked incluye proveedores no consultados","C2 evaluation_status NO_EVALUABLE -> NOT_CHECKED en los 23 mercados"],"note":"Newcastle Jets-Gamba Osaka (AFC CL). 23 mercados con estados coherentes. Sin form, stats, price ni odds. Sin cifras inventadas. calc.py no aplica."},
{"match_id":"m-2b3f5d6e6a5b","review_status":"REVISADO","corrections":["C1","C2"],"note":"Pohang Steelers-Johor Darul Ta'zim (AFC CL). Igual que arriba. Sin cifras. No estimable."},
{"match_id":"m-9e75e37d4b9d","review_status":"REVISADO","corrections":["C1","C2"],"note":"Kyoto Sanga-Ratchaburi (AFC CL). Igual. Sin cifras. No estimable."},
{"match_id":"m-ab313671331d","review_status":"REVISADO","corrections":["C1","C2"],"note":"Shanghai SIPG-Daejeon Citizen (AFC CL). Igual. Sin cifras. No estimable."}]}
```
```json
{"agent":"analista-cuantitativo","batch_id":"b02","rows":[
{"match_id":"m-5e288e8a1f72","review_status":"REVISADO","corrections":["C1","C2"],"note":"Portimonense U23-Academico Viseu U23 (Liga Revelação U23). Sin cobertura football-data (no es P1). Sin cifras. No estimable."},
{"match_id":"m-7172178569c0","review_status":"REVISADO","corrections":["C1","C2"],"note":"Lens-Sporting (UCL). Sin form, stats ni cuotas. No estimable."},
{"match_id":"m-c237309e8e29","review_status":"REVISADO","corrections":["C1","C2"],"note":"Sabah-Slavia Praha (UCL). Sin cifras. No estimable."},
{"match_id":"m-05f58afa45b9","review_status":"REVISADO","corrections":["C1","C2"],"note":"Viking-Bayern München (UCL). Sin cifras. No estimable."}]}
```
```json
{"agent":"analista-cuantitativo","batch_id":"b03","rows":[
{"match_id":"m-0af946c9d2f0","review_status":"REVISADO","corrections":["C1","C2"],"note":"RB Leipzig-PSV (UCL). Sin cifras. No estimable."},
{"match_id":"m-0f1b11fab280","review_status":"REVISADO","corrections":["C1","C2"],"note":"Villarreal-Napoli (UCL). Sin cifras. No estimable."},
{"match_id":"m-11cf48aef451","review_status":"REVISADO","corrections":["C1","C2"],"note":"Arsenal-Lille (UCL). Sin cifras. No estimable."},
{"match_id":"m-295297ed3e94","review_status":"REVISADO","corrections":["C1","C2"],"note":"Galatasaray-Barcelona (UCL). Sin cifras. No estimable."}]}
```
```json
{"agent":"analista-cuantitativo","batch_id":"b04","rows":[
{"match_id":"m-d21f4803797c","review_status":"REVISADO","corrections":["C1","C2"],"note":"Inter Milan-Club Brugge (UCL). Sin cifras. No estimable."},
{"match_id":"m-fd4f0f50a781","review_status":"REVISADO","corrections":["C1","C2"],"note":"Atlético Madrid-Manchester United (UCL). Sin cifras. No estimable."},
{"match_id":"m-8f866f457c46","review_status":"REVISADO","corrections":["C1","C2"],"note":"Lens U19-Sporting U19 (UEFA Youth League). Sin cifras. No estimable."}]}
```

## (3) PENDIENTE y motivo

- No hay filas pendientes de revisión: las 15 están REVISADO.
- Pendiente de decisión del director: aplicar C1 y C2 en `level1.py`, lo que cambia `matrix.json`, `coverage_report.md` y las pruebas.
  - Probablemente fallen `tests/test_level1.py` y `tests/test_coverage.py`, que mencionan NOT_CHECKED y NO_EVALUABLE. No los ejecuté porque estoy en modo plan.
- Pendiente de datos, no resoluble con fuentes permitidas:
  - histórico por equipo
  - córners y tarjetas
  - árbitros
  - cuotas de al menos dos casas
  - alineaciones y bajas
- Mientras falten, todo queda "no estimable" y no se calcula ningún EV.

## (4) Registro de fuentes

| Fuente | URL o ficha | Dato buscado | Información obtenida | Fecha de consulta | Estado | Discrepancias | Alternativa consultada |
|---|---|---|---|---|---|---|---|
| Ficheros locales del run | `runs/2026-10-13/{matrix,inventory,state,batches}.json`, `coverage_report.md`, `coverage.json`, `sources/consultas.jsonl` | Estados por mercado, cifras, cobertura, intentos | 345 mercados NOT_CHECKED/INSUFICIENTES/NO_EVALUABLE, sin stats ni cuotas; `consultas.jsonl` solo registra football-data (`fixtures.csv`) y apwin (portada), sin fichas de estos partidos | 2026-10-13 | Consultada y útil (lectura local, no es fuente externa) | `sources_checked` incluye proveedores excluidos o sin cobertura | n/a |
| Código y política | `level1.py`, `coverage_report.py`, `sources_policy.json`, `calc.py`, `seleccion-final-picks/SKILL.md`, `docs/FUENTES-CONFORMIDAD.md` | Definición de estados y puerta de cobertura | NOT_CHECKED ≠ NO_EVALUABLE; veredicto RESTRINGIDO coherente con el código | 2026-10-13 | Consultada y útil (lectura local) | Contradicción en `level1.py` entre `market_availability_status` NOT_CHECKED y `evaluation_status` NO_EVALUABLE | n/a |
| FotMob, BetExplorer, Transfermarkt, Understat, SoccerStats | No consultadas | Estadísticas, cuotas, bajas | Excluidas por `sources_policy.json` | 2026-10-13 | No consultada | n/a | Ninguna permitida cubre estas competiciones |
| Resto de hosts (Flashscore, OddsPortal, FootyStats, etc.) | No consultados | Estadísticas, cuotas | No revisados en la política, por tanto denegados | 2026-10-13 | No consultada | n/a | n/a |
| Football-Data | Sin ficha | Histórico de los equipos | `extra.div` en None en los 15 partidos; no se abrió ningún CSV | 2026-10-13 | No consultada | n/a | Ver hallazgo 7 |