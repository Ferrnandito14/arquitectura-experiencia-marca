# Manual maestro — sistema de picks (estado al 14-oct-2026, hora de Caracas)

Resumen de cómo funciona hoy el sistema, qué se puede y qué no se puede afirmar con él, y la visión actualizada tras la Fase 7 y la incorporación de TheStatsAPI. El detalle operativo vive en `.claude/skills/seleccion-final-picks/SKILL.md`; las pruebas y cifras, en `docs/PRUEBAS-picks.md`.

## 1. Reglas fijas (no se negocian)
1. **Solo hora de Caracas (UTC−4)** en todo lo que se muestra.
2. **Nunca se dice «no apostar»**: se informan riesgos (P de pérdida, brechas, alertas) y **la decisión es de la persona usuaria**. El EV de mercado no es el veredicto.
3. **Una lista de partidos define solo el universo de partidos, nunca los mercados.** Por cada partido se investiga TODO el catálogo (326 entradas por partido: 1X2, doble oportunidad, empate no válido, hándicaps asiático/europeo, goles totales y por equipo, ambos anotan, 1.ª parte, córners, tarjetas A=1/R=2, remates, fueras de juego).
4. **Cada pata ≤ 2.10.** Las combinadas pasan por los agentes y por el sistema de riesgos.
5. **Independiente de cualquier casa:** los precios son fuentes opcionales; un precio de agregador es **referencia, nunca ejecutable**.
6. **Sin pesos arbitrarios:** el modelo propio no se mezcla con el mercado salvo con un peso validado por backtest; un modelo no validado **nunca** habilita «apto para apostar».
7. **Honestidad de rótulos:** certificación de la investigación ≠ aprobación para apostar; «seguro» solo con P(ticket) ≥ 85 % y EV ≥ 0.
8. Se respeta la política de fuentes (`sources_policy.json`, `docs/FUENTES-CONFORMIDAD.md`); la clave de cada API nunca se imprime ni se guarda en el repo.

## 2. Arquitectura (cuatro capas independientes)
| Capa | Qué hace | Scripts |
|---|---|---|
| Datos deportivos | historial, forma, muestras de liga y árbitro, rotación | `inventory.py`, `level1.py`, `adapters.py`, `league_sample.py`, `rotation_prior.py` |
| Catálogo de mercados | lista declarativa de mercados, líneas y selecciones | `market_catalog.py` |
| Precios (opcionales) | cuotas de varias fuentes con tipo y procedencia | `price_sources.py` (apifootball, TheStatsAPI, Football-Data, capturas del usuario, CSV), `tsa_fetch.py` |
| Modelo y análisis | probabilidades propias, backtest, rankings, combinadas, libro | `leg_model.py`, `count_model.py`, `backtest_modelo.py`, `catalog_rankings.py`, `build_xlsx_catalog.py` |

## 3. Flujo de una jornada
1. **Universo:** capturas o lista del usuario → `partidos_usuario.json` + `ids.json` (partido → `match_id`).
2. **Datos:** inventario y Nivel 1 por partido; `league_sample.py` por liga; `rotation_prior.py`.
3. **Precios:** `apif_query.py` (apifootball) y `tsa_fetch.py --run … --ids …` (TheStatsAPI). Cuotas guardadas con fuente, hora y número de casas.
4. **Cobertura:** `market_coverage.py` ejecuta los controles A (investigación), B (analítica) y C (precios) y la preparación para apostar.
5. **Revisión de agentes** (contrato cerrado, 4 roles): `agent_review.py packages` → `digest --batch k/N` → agentes por lote → `merge` → `validate` → `gate` (COMPLETA / INCOMPLETA).
6. **Resultados:** `catalog_rankings.py` (rankings y combinadas) y `build_xlsx_catalog.py` (libro `ligas-<fecha>-v2.xlsx`).
7. **Seguimiento:** `seguimiento.py` registra resultados por pata para calibrar (sin alertas en vivo si no se piden).

## 4. Los tres controles y la preparación para apostar
- **A. Investigación:** cada combinación partido × entrada × canal tiene resultado y evidencia (`encontrado`, `consultado_no_encontrado`, `fuente_no_ofrece`, `no_verificable`, `pendiente`). `INVESTIGACION_COMPLETA` = nada pendiente. No depende del modelo ni del precio.
- **B. Analítica:** datos suficientes, estimador disponible, nivel de validación (hoy «insuficiente» en todas las familias).
- **C. Precios:** fuente identificada, tipo (real / referencia), límite 2.10.
- **Preparación para apostar (independiente):** exige a la vez investigación resuelta, precio real verificado, cuota ≤ 2.10, datos suficientes, estimador propio, **modelo validado** y revisión de agentes completa. Hoy 0 filas cumplen: el modelo no está validado.

## 5. Precios y fuentes
- **Real:** tus capturas (casa del usuario). **Referencia:** mediana de casas de un agregador, con `N.º de casas` (una sola casa = el precio de esa casa).
- **apifootball:** 1X2, doble oportunidad, hándicap asiático, goles totales, ambos anotan, empate no válido (`ah0`). No trae córners, tarjetas, goles por equipo ni 1.ª parte.
- **TheStatsAPI:** además córners (totales y por equipo), tarjetas totales, goles por equipo, 1.ª parte, hándicap europeo, totales y hándicaps enteros, remates. Mediana de Bet365, Paddy Power, BetMGM UK, Pinnacle y Betfair Exchange; se descartan casas con pares de precios incoherentes. 32 de los 34 partidos emparejados.
- **Sin cuota en fuente:** fueras de juego, tarjetas por equipo, la mayoría de remates y las líneas que ninguna casa cotiza. No se inventan ni interpolan cuotas.
- **Tarjetas:** la fuente no documenta cómo las cuenta; la regla A=1, R=2 no está confirmada.

## 6. Modelo propio
Poisson ataque/defensa con encogimiento (goles, 1X2, DC, DNB, hándicaps, ambos anotan, 1.ª parte) y binomial negativa para córners y tarjetas. **Backtest walk-forward: todas las familias «insuficiente»** (≈ 800 partidos vs tasa base, 100 vs mercado; sin cuotas históricas de córners/tarjetas). Mientras no se valide, sus probabilidades son una **segunda opinión**, no un veredicto.

## 7. Revisión de agentes (contrato JSON cerrado)
Verificador (disponibilidad y precio), deportivo (solidez y escenario de pérdida), cuantitativo (consistencia con el mercado) y auditor (objeciones, muestra mínima, `objeciones_a_agentes`). Una pata **rechazada** sale de rankings y combinadas; **degradada** (solidez BAJA/NO_EVALUABLE) sale solo de combinadas; **objetada** o con **precio nuevo sin revisar** no cuenta como aprobada.

## 8. Rankings y combinadas
Una pata por partido; ≤ 2 overs/unders, ≤ 2 de la misma liga, ≤ 3 en la misma ventana de 2 h; una pata en ≤ 2 combinadas y un partido en ≤ 3; |brecha modelo − 1/cuota| < 15 pp; cuota entre 1.10 y 2.10 en rankings. Cada combinada muestra multiplicador (producto de cuotas), aporte de cada pata, **P gana si fueran independientes**, P(pérdida), nota de correlación, estado de agentes y requisitos que faltan.

## 9. Cómo leer el libro `ligas-14-oct-v2.xlsx`
Léeme → Leyenda → una hoja por liga (todos los mercados con estimador) → Ranking seguridad → Ranking atractivo-cuota → Top por liga → Combinadas → Mercados extra → Resumen por partido → Cobertura → Catálogo completo (11 084 filas) → Sin precio (para pegar la cuota de tu casa) → Agentes.

## 10. Estado real al 14-oct
34 partidos, 8 competiciones; investigación **certificada**; revisión de agentes **COMPLETA** (544 unidades × 4 roles); 4 433 filas con probabilidad del modelo; 3 476 de 10 506 filas de mercados extra con cuota; 316 filas elegibles; 9 combinadas, todas **NO_APTA**. Hallazgos recurrentes: precios absurdos de una sola casa en hándicap, ceros de córners en el feed, y brechas de 20–40 pp entre el modelo y el mercado en varios 1X2.

## 11. Visión actualizada (qué cambia con la información nueva)
1. **El cuello de botella ya no son los datos, es la validación.** Con TheStatsAPI hay cuotas para casi todos los mercados extra; lo que falta es saber si el modelo aporta algo. Hoy no está demostrado.
2. **Dónde discrepa del mercado, lo más probable es que falle el modelo.** El backtest anterior mostró que el mercado predice mejor en 1X2; por eso un EV teórico alto (+10 % a +40 %) debe leerse como «el modelo discrepa», no como ventaja. Las alertas del libro lo marcan.
3. **Uso recomendable hoy:** el sistema es un **filtro estructural y un contador de riesgo** (cuota ≤ 2.10, correlación, exposición, P de pérdida, revisión de agentes), no un predictor. La probabilidad implícita del mercado es la referencia; el modelo, un aviso.
4. **Riesgo real de las combinadas:** P(pérdida) ≈ 10–15 % en las ×1.2, ≈ 54–63 % en las ×3 y ≈ 70–74 % en las ×4 según el propio modelo (sin validar). El resultado del 13-oct (3/7 patas del sistema; 4/5 del ticket propio) es coherente con esa dureza y no demuestra ventaja en ningún sentido.
5. **Qué lo cambiaría de verdad:** validar con **cuotas de cierre históricas**. TheStatsAPI declara 204 competiciones con histórico de cuotas (incluye MLS, Champions, Libertadores, Sudamericana, Championship y Liga Profesional argentina). Falta comprobar qué mercados guarda el histórico (córners y tarjetas incluidos) y cuántos partidos tienen cierre.

## 12. Hoja de ruta
1. **Backtest con cuotas de cierre de TheStatsAPI** (walk-forward, Brier/log-loss vs mercado, por familia y liga; peso de mezcla calculado con datos). Único camino a «APTA».
2. Relanzar verificador y auditor sobre los precios nuevos de mercados extra (hoy quedan «sin aprobar»).
3. Confirmar la definición de tarjetas de la fuente y de tu casa (A=1, R=2).
4. Cuotas reales de tu casa en «Sin precio» / «Mercados extra» para convertir referencias en precios reales.
5. Registrar resultados por pata (calibración) y retirar familias con ROI claramente negativo.

## 13. Pendientes de la persona usuaria
Regenerar las claves de apifootball y TheStatsAPI (ambas se mostraron en el chat); aportar los picks de los días 1–11 y 14 del reto y el resultado de Atalanta–Venezia; confirmar que la cuenta de TheStatsAPI es propia (la clave es personal según sus términos).
