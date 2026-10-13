Sigo con lecturas de solo lectura: el modo plan me impide editar o ejecutar nada que modifique el sistema.

=====

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

=====

RESPUESTA
1. C1 y C2 están bien aplicadas en las 345 celdas, pero quedan dos contradicciones nuevas.
   - **Estado de estadísticas:** `statistics_availability_status` sigue en INSUFICIENTES en las 345 celdas, aunque nadie intentó obtener esas estadísticas. Debe ser NOT_CHECKED (manual: "falta de estadísticas no es cero"). INSUFICIENTES implica que se buscó y no bastó.
   - **Estado del partido:** `sports_analysis_status` y `market_analysis_status` siguen en NO_EVALUABLE_TRAS_INTENTOS en los 15 partidos. Los 15 `attempts` son 5 "no consultada: excluida por política" y 1 "sin cobertura". El manual reserva ese estado para "motivo y evidencia de intentos", y aquí no hubo ninguna consulta real. Propongo NO_INVESTIGADO_SIN_FUENTE_PERMITIDA o NOT_CHECKED. Hay que ajustar `PROCESSED_OK` en `coverage_report.py` para que lo siga contando como procesado sin evaluar.
2. Texto para `coverage_report.py` (7 líneas): "**Qué NO se sostiene con este ranking:** no hay ningún candidato, k/n, probabilidad, cuota ni EV; los 345 mercados están NOT_CHECKED (no investigados), lo cual no prueba que el mercado no exista ni que la estadística sea 0. No se sostiene ninguna selección por valor ni 'alta probabilidad'. No hay histórico, córners, tarjetas, árbitro, bajas ni cuotas de ninguna casa. Cualquier orden entre partidos sería solo criterio deportivo cualitativo, sin valor económico confirmado. Las familias resultado, goles, corners, tarjetas y otros están sin cobertura de datos permitidos. Para levantar la restricción hace falta una fuente permitida que cubra estas competiciones."
3. Retiro el hallazgo 7. Los equipos y las competiciones no son comparables, y la liga doméstica no es evidencia del partido de Champions, AFC ni juveniles. Aunque se declarara, quedaría como contexto débil, no como base de probabilidad.

EVIDENCIA
- `matrix.json`: 15 partidos, y `set(matrix)==set(analysis_required)` en `inventory.json` es True.
- Las 345 celdas son idénticas:
  - `evaluation_status` y `market_availability_status`: NOT_CHECKED.
  - `not_evaluable_reason`: "no investigado: …no implica que el mercado no exista ni que la estadística sea 0".
  - `sources_checked`: [].
  - `sources_not_consulted`: [fotmob, betexplorer, transfermarkt, understat, soccerstats, football-data].
  - `stats` y `price` vacíos; `form` vacío en los 15 partidos.
- `coverage_report.md`: "Mercados examinados 0 de 345 (NOT_CHECKED: 345)" y "Procesados SIN ninguna consulta real: 15". El veredicto sigue en RESTRINGIDO.
- La fila "Mercados no evaluables 0" es coherente con el cambio.
- No verifiqué `state.json` ni `reviews_raw/id_map_before_fix.json`. Tampoco comprobé que el mapeo de los match_id nuevos coincida con los antiguos.

CAMBIO EN TU ESTADO
- C1 y C2 pasan a CONFIRMADAS.
- Abro C3 (estadísticas INSUFICIENTES → NOT_CHECKED) y C4 (estado de partido TRAS_INTENTOS → no investigado). Las dos quedan pendientes de aplicar.
- Hallazgo 7 retirado.
- Mis bloques JSON de lotes usan los match_id antiguos, así que quedan obsoletos. Los 15 siguen REVISADO en cuanto al contenido, y rehago los bloques con los id nuevos si me das el mapa.

=====

RESPUESTA
- La afirmación se sostiene para Inter–Club Brugge y Lens–Sporting. Recalculé desde los CSV 2627 de `cache/*.body`, con las URLs localizadas en cada `.meta.json`. Las 32 frecuencias k/n coinciden con la matriz, sin ninguna discrepancia. Los intervalos Wilson de la matriz coinciden con los de `calc.py freq`.
- Ninguna celda proxy declara EVALUABLE, cuota, EV ni probabilidad. Hay 7 partidos con `proxy_sample`=true, 0 celdas EVALUABLE y 0 celdas con `price`.
- Todas las celdas PARCIAL llevan el aviso "OTRA competición" en `not_evaluable_reason`. `sample_note` empieza con "PROXY: forma de liga DOMÉSTICA, OTRA competición… NO es evidencia del partido". Solo comprobé en detalle los dos cruces pedidos.

EVIDENCIA (mi k/n = matriz). Dentro de cada fila, la primera cifra es el equipo local y la segunda el visitante.

| Mercado | Inter (n=6) | Club Brugge (n=8) | Lens (n=6) | Sporting (n=8) |
|---|---|---|---|---|
| BTTS | 4/6 | 3/8 | 5/6 | 6/8 |
| Goles >2.5 | 5/6 | 6/8 | 5/6 | 6/8 |
| Córners >9.5 | 3/6 | 6/8 | 4/6 | 1/8 |
| Tarjetas (A+R) >4.5 | 1/6 | 3/8 | 2/6 | 3/8 |

- Ejemplos de Wilson: Inter BTTS 4/6 da [0.300, 0.903]; Brugge BTTS 3/8 da [0.137, 0.694]; Sporting córners >9.5 1/8 da [0.022, 0.471].
- Usé los últimos ≤10 partidos anteriores a 2026-10-13, y todos los disponibles caben en esa ventana. Las fechas llegan hasta el 9 o 10 de octubre.

Observaciones de método, que no son discrepancias de cifras:
1. **Muestra débil:** n=6 u 8 en todos los casos, por debajo del umbral de 8 de la skill en 3 de 4 equipos. La temporada 26/27 lleva pocas jornadas. Debe seguir como PARCIAL y no subir.
2. **Etiquetas local/visitante:** "local" y "visitante" en la matriz son el equipo local y el equipo visitante del cruce de Champions. La muestra de cada uno mezcla sus partidos en casa y fuera, no es una división por localía.
3. **Tarjetas:** cuentan amarillas más rojas sin ponderar. Esto no sirve para puntos de tarjetas, y una doble amarilla puede contar dos veces. Los CSV no permiten separar doble amarilla de roja directa.
4. **Rivales y contexto:** los rivales son domésticos, de distinto nivel, y sin ajuste por calidad. La Champions cambia el nivel del rival, la rotación y el árbitro.
5. **Origen común:** las cuatro series salen del mismo proveedor (football-data), así que no hay contraste con una segunda fuente independiente. La skill exige un segundo origen para estadísticas esenciales, y eso no se cumple.
6. **Campo `proxy_sample`:** existe a nivel de partido, no de celda. La celda se identifica solo por el texto de `not_evaluable_reason`. Lo recomendable es copiarlo también a la celda para que ningún consumidor posterior lo pierda.

CAMBIO EN TU ESTADO
- Afirmación sobre k/n: CONFIRMADA para estos dos cruces.
- Hallazgo 7: reabierto como aceptable solo en forma de proxy descriptivo, con las cuatro cautelas anteriores. Sigue sin ser evidencia del partido ni base de probabilidad: "no estimable", sin EV. Si hace falta, queda como contexto para el director, nunca como entrada de ranking por valor.
- Propongo C5: copiar `proxy_sample` a cada celda.
- C3 y C4 (de la ronda 2) siguen sin verificar en este envío.

=====

Revisé las 15 filas de los siete lotes, en solo lectura y sin red. Cuadran las 345 celdas, las cifras de `coverage_report.md` y los lotes. Quedan tres puntos menores: `otros.tiros` cuenta como PARCIAL sin serlo, y hay dos matices de estados.

**(a) Celda por celda.** Los tres patrones que aparecen suman 345 celdas.

| Patrón | Celdas | `proxy_sample` | `evaluation_status` | `statistics_availability_status` | `price_verification_status` | Contenido |
|---|---|---|---|---|---|---|
| Partidos sin proxy | 184 | false | NOT_CHECKED | NOT_CHECKED | PRECIO_NO_CONFIRMADO | `sources_checked` vacío, sin stats ni precio |
| Proxy con estadística | 63 | true | PARCIAL | PARCIALES | PRECIO_NO_CONFIRMADO | solo `football-data`, razón con "OTRA competición" |
| Proxy sin ese mercado | 98 | true | NO_EVALUABLE | INSUFICIENTES | PRECIO_NO_CONFIRMADO | solo `football-data`, razón "la fuente permitida abierta no incluye este mercado/estadística" |

- Ninguna celda es EVALUABLE ni lleva `price`, probabilidad o EV.
- Estado de partido: los 8 sin proxy están en NO_INVESTIGADO_SIN_FUENTE_PERMITIDA y los 7 con proxy en PARCIAL_PROXY_OTRA_COMPETICION. Eso aplica C4.
- Las 7 `sample_note` contienen PROXY, OTRA competición, n<8, sin árbitro, "NO las de ninguna casa" y "sin ponderar". La palabra "alias" aparece solo en las notas que la necesitan. No tengo evidencia de que el criterio de alias sea el correcto en las demás notas, solo de que el texto está presente cuando hace falta.

**(b) Cifras del informe.** Cuadran con la matriz:
- 184 NOT_CHECKED + 63 PARCIAL + 98 NO_EVALUABLE = 345.
- 63 + 98 = 161 examinados, el 46,7%.
- Hay 7 partidos con proxy y 8 sin consulta real.

**(c) C3 y C4 de la ronda 2.** Están aplicados. Los 8 partidos sin proxy tienen `statistics_availability_status` en NOT_CHECKED, y el estado de partido ya no es NO_EVALUABLE_TRAS_INTENTOS.

```json
{"agent":"analista-cuantitativo","batch_id":"b01","rows":[
{"match_id":"m-9ec6426a60e9","review_status":"REVISADO","corrections":[],"note":"Newcastle Jets-Gamba Osaka. 23/23 NOT_CHECKED, sin proxy, sin cifras, sources_checked vacío. Partido NO_INVESTIGADO_SIN_FUENTE_PERMITIDA."},
{"match_id":"m-0c15b801051b","review_status":"REVISADO","corrections":[],"note":"Kyoto Sanga-Ratchaburi. 23/23 NOT_CHECKED, sin cifras."},
{"match_id":"m-652b82fc3ca3","review_status":"REVISADO","corrections":[],"note":"Pohang Steelers-Johor Darul Ta'zim. 23/23 NOT_CHECKED, sin cifras."}]}
```
```json
{"agent":"analista-cuantitativo","batch_id":"b02","rows":[
{"match_id":"m-fef50009982d","review_status":"REVISADO","corrections":[],"note":"Shanghai SIPG-Daejeon Citizen. 23/23 NOT_CHECKED, sin cifras."},
{"match_id":"m-23a8afef592b","review_status":"REVISADO","corrections":[],"note":"Portimonense U23-Academico Viseu U23. 23/23 NOT_CHECKED, sin proxy (U23 excluido por regla de primera plantilla)."}]}
```
```json
{"agent":"analista-cuantitativo","batch_id":"b03","rows":[
{"match_id":"m-97cb0716e4dc","review_status":"REVISADO","corrections":[],"note":"Lens-Sporting. Proxy F1/P1: 9 PARCIAL y 14 NO_EVALUABLE, con proxy_sample=true. Frecuencias k/n verificadas en la ronda 3. Sin cuota, EV ni probabilidad."},
{"match_id":"m-d89de9c16489","review_status":"REVISADO","corrections":[],"note":"Sabah-Slavia Praha. 23/23 NOT_CHECKED, sin cifras."}]}
```
```json
{"agent":"analista-cuantitativo","batch_id":"b04","rows":[
{"match_id":"m-26124a15db3b","review_status":"REVISADO","corrections":["otros.tiros no debería ser PARCIAL"],"note":"Atlético Madrid-Manchester United. Proxy: 9 PARCIAL y 14 NO_EVALUABLE. Frecuencias de este cruce no recalculadas por mí (ver hallazgo 2). Sin cuota ni EV."},
{"match_id":"m-56d70359455c","review_status":"REVISADO","corrections":["otros.tiros no debería ser PARCIAL"],"note":"Villarreal-Napoli. Proxy: 9 PARCIAL y 14 NO_EVALUABLE. Frecuencias de este cruce no recalculadas por mí (ver hallazgo 2). Sin cuota ni EV."}]}
```
```json
{"agent":"analista-cuantitativo","batch_id":"b05","rows":[
{"match_id":"m-7fbfa4899ff4","review_status":"REVISADO","corrections":["otros.tiros no debería ser PARCIAL"],"note":"RB Leipzig-PSV. Proxy: 9 PARCIAL y 14 NO_EVALUABLE. Frecuencias de este cruce no recalculadas por mí (ver hallazgo 2). Sin cuota ni EV."},
{"match_id":"m-837c7443671e","review_status":"REVISADO","corrections":["otros.tiros no debería ser PARCIAL"],"note":"Inter-Club Brugge. Proxy I1/B1. Frecuencias recalculadas por mí en la ronda 3 y coincidentes. Sin cuota ni EV."}]}
```
```json
{"agent":"analista-cuantitativo","batch_id":"b06","rows":[
{"match_id":"m-c585811d2f7b","review_status":"REVISADO","corrections":["otros.tiros no debería ser PARCIAL"],"note":"Galatasaray-Barcelona. Proxy: 9 PARCIAL y 14 NO_EVALUABLE. Frecuencias de este cruce no recalculadas por mí (ver hallazgo 2). Sin cuota ni EV."},
{"match_id":"m-e58658a3f614","review_status":"REVISADO","corrections":[],"note":"Viking-Bayern München. 23/23 NOT_CHECKED, sin cifras."}]}
```
```json
{"agent":"analista-cuantitativo","batch_id":"b07","rows":[
{"match_id":"m-fa26ce1cb71b","review_status":"REVISADO","corrections":["otros.tiros no debería ser PARCIAL"],"note":"Arsenal-Lille. Proxy E0/F1, n=6 en ambos equipos. Frecuencias de este cruce no recalculadas por mí (ver hallazgo 2). Sin cuota ni EV."},
{"match_id":"m-316ec30a5d4e","review_status":"REVISADO","corrections":[],"note":"Lens U19-Sporting U19. 23/23 NOT_CHECKED, sin cifras (juvenil, sin proxy)."}]}
```

Hallazgos pendientes:
1. **`otros.tiros` como PARCIAL.** Es PARCIAL en los 7 proxies, pero su bloque en `level1.py` cuenta "dato de tiros presente", que es presencia de dato y no una frecuencia de mercado. Debería ser NO_EVALUABLE, o aportar una estadística real (por ejemplo tiros totales sobre una línea declarada). Si pasa a NO_EVALUABLE, el recuento de 63 baja a 56 y el de 98 sube a 105.
2. **Frecuencias recalculadas.** Solo recalculé Inter–Club Brugge y Lens–Sporting (ronda 3). Los otros cinco cruces proxy tienen k/n sin verificación independiente mía. Si se quiere cerrar, puedo repetir el cálculo desde los CSV de `cache/` para esos cinco.
3. **Estado de precio.** En las 184 celdas sin consulta `price_verification_status` dice PRECIO_NO_CONFIRMADO. Es válido, pero NOT_CHECKED sería más preciso, porque nadie intentó verificar cuota. Es un matiz menor, no una contradicción.
4. **Estado de mercado en los proxies.** `market_availability_status` sigue en NOT_CHECKED en las 161 celdas proxy, y es correcto: no hubo cuota. Debe mantenerse así.
5. **Universo truncado.** El informe advierte de apwin 11 de 15, 15 de 166 y 15 de 126. Cualquier conclusión es una cota inferior, y las 15 filas revisadas no son "la jornada completa".
6. **Calendario.** Los 15 partidos tienen una sola fuente de calendario y ninguno tiene verificación suficiente para selección final. No es un fallo cuantitativo, pero limita cualquier pick.

Archivos revisados (todos en `/home/user/football-picks-system/runs/2026-10-13/`):
- `matrix.json`
- `batches.json`
- `state.json`
- `inventory.json`
- `coverage_report.md`