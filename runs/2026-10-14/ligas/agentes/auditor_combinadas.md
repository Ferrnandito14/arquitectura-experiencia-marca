# Auditoría adversarial de combinadas — 14-oct-2026 (horas de Caracas)

Fuentes leídas por mí: hoja «Combinadas» y «Léeme» de dist/ligas-14-oct.xlsx; dataset.json; grupo_A/B/C.json; apif_query (get_events y get_lineups de 711715, 857088 y 858783, consulta 14-oct ~02:20 UTC). Estado: todas las cifras de forma son de apifootball (una sola proveedora, no independientes entre sí) y las previas de prensa no se abrieron (WebFetch falló, solo WebSearch).

## Hallazgos transversales (afectan a las 9 opciones)

1. **Alineaciones y bajas VACÍAS en todos los partidos usados** (confirmado por mí: `starting_lineups` y `missing_players` vacíos en Nashville, Fluminense y Santarém; los informes dicen lo mismo para Lincoln, Dallas y RSL). Impacto ALTO. Es riesgo desconocido, no nulo. Resolvería: once oficial ~1 h antes de cada partido.
2. **Nashville (1.23) está en las 9 opciones.** Es una pata común, así que un tropiezo de Nashville (P fallo mercado 23.5 %) hunde todas las opciones a la vez; no hay diversificación entre opciones. Impacto ALTO para quien juegue más de una.
3. **Todas las opciones superan el 35 % de P de fallo** (P de fallo según mercado: 51.3 % en ×1.5–1.8, 56.2–57.1 % en ×2–2.6, 73.2–74.6 % en ×3–3.8), así que las 9 caen en ALTO por tu criterio. La diferencia entre ellas es de pocos puntos. Las P centrales salen de 80 % mercado + 20 % modelo v0 (que no supera al mercado), así que P central y P mercado son prácticamente la misma información.
4. **«Solidez» es juicio cualitativo sobre muestras n=10 (n=8 en Libertadores) mezclando rivales y competiciones.** No se convierte en probabilidad. Las frecuencias por sede (p. ej. 10/20) tienen intervalos amplios (±22 pp).
5. **Cuota total = producto de las cuotas.** No he verificado que tu casa acepte esas combinaciones al producto (patas de partidos distintos).
6. **Dataset vs. informe, descanso de Nashville/SKC:** el dataset dice «descanso justo (4 días)», el informe C dice que ambos jugaron el 11-oct (3 días). Discrepancia menor (impacto bajo), pero el flag de rotación «bajo» se calculó con el dato de 4 días.
7. **Misma noche, mismo horario:** Nashville, Fluminense y Dallas empiezan a las 20:30 y RSL a las 21:30. No hay margen para reaccionar a una alineación tardía de una pata con otra.

## Auditoría por pata

| Pata | Cuota | P fallo mercado | Argumento más fuerte en contra | Datos faltantes | Impacto |
|---|---|---|---|---|---|
| Gana Nashville | 1.23 | 23.5 % | Líder con 63 pts y +12/+14 sobre sus perseguidores a 6 jornadas: rotación posible con la posición casi asegurada; el propio informe dice que ese riesgo «no está cuantificado». Empató 2-2 en Miami y 0-0 en NYC en septiembre. El 76.5 % ya incluye todo, y con 1.23 el margen de error es mínimo. A favor: 9G-1E-0P en casa (n=10), SKC 2G-0E-8P fuera (n=10) | Alineaciones y bajas vacías; árbitro sin muestra (n=0) | Alto |
| Gana Gil Vicente (Santarém) | 1.41 | 36.3 % | Copa vs. tercera categoría: el informe de grupo A cita novedades en el once según A Bola (12-oct, no abierta), con el portero Samuel Portugal debutando. Gil Vicente solo gana 3 de 7 en liga, marca 0.86 g/p y gana por 2+ solo 1/7. El empate (4.00) pierde la pata. Sin modelo (p_modelo = null; p central = mercado) | Once vacío; árbitro de una sola fuente; datos de Liga 3 de una sola fuente; si la liquidación incluye prórroga no lo he podido comprobar (el empate a 4.00 sugiere 90 min) | Alto |
| Gana West Ham (Lincoln) | 1.68 | 43.2 % | Empate: 3 de 4 visitas de liga empatadas (1-1 Watford, 2-2 Millwall); Lincoln en casa: 0V-2E-2D (n=4) y sin victorias locales. Hándicap -1 para West Ham: 0/4 fuera en liga. Veltman en duda en una previa. Cuota 4.33 al empate | Alineaciones vacías; bajas solo por WebSearch, no oficiales; árbitro no designado; rotación «s/d» (no es «bajo», es desconocida) | Alto |
| Más de 2.5 (Lincoln – West Ham) | 1.66 | 42.8 % | El Over depende solo de West Ham (8/10 Over) porque Lincoln marca 0.8 g/p y 4/9 porterías a cero; Lincoln gana sus 1-0 (3 veces). Los 6-0 y 4-2 de West Ham inflan su media (no se convierte media en probabilidad) | Mismos que arriba | Medio |
| Menos de 3.5 (RSL – San José) | 1.66 | 43.9 % | San José fuera 5/10 con 4+ goles; RSL concede 2.0 por partido. El 65 % de «13/20» está contra un 56.1 % implícito, pero con n=20 de dos equipos no es diferencia fiable. La brecha del modelo (+10.2 pp) viene de un modelo v0 que no supera al mercado | Alineaciones vacías; árbitro sin designar | Medio |
| Más de 1.5 (Fluminense – Palmeiras) | 1.58 | 40.7 % | Ida de semifinal sin Cano, John Kennedy (Flu) y Vitor Roque, Jefte (Pal); Abel Ferreira sancionado; Palmeiras 7 porterías a cero y 3 de sus últimos 10 en 0-0. En eliminatorias de Libertadores de la muestra solo 5/8 superó 1.5. Brecha modelo +13.3 pp (cerca del umbral de ruido). Discrepancia entre fuentes en Alisson/M. Reis/Riquelmi. Árbitro Tello: n=4, no extrapolable | Once no publicado; bajas de prensa sin abrir | Alto |
| Menos de 3.5 (Dallas – Seattle) | 1.58 | 40.9 % | Dallas 5/10 en casa con 4+ goles; Seattle viene de un 3-3 y un 3-0. Árbitro Freemon: media 4.88 pts, no relacionado con goles. Sin bajas verificables | Alineaciones vacías (confirmado en el informe C; la ficha no la consulté) | Medio |

## Correlación entre patas

- **Misma noche:** todas las opciones combinan partidos que se juegan casi a la vez (20:30–21:30). Sin correlación causal entre partidos distintos, pero sí riesgo operativo compartido: sin once confirmado de ninguna.
- **Misma liga:** las MLS (Nashville + RSL, Nashville + Dallas) comparten jornada y contexto de final de temporada (6 jornadas por jugar) pero no dependen una de otra. Correlación estadística pequeña; lo relevante es que la base MLS «Menos de 3.5» (59 %, 186/317) aporta el mismo prior a ambas patas.
- **Misma dirección:** ×3–3.8 #1 y #2 mezclan Over y Under en partidos distintos, lo que diversifica; #3 combina victoria de favorito + Over + Under.
- **Mismo partido:** ninguna de las 9 opciones combina dos patas del mismo partido (verificado en la hoja). Lo único pendiente es confirmar que tu casa acepte cada combinación al producto de cuotas; con partidos distintos es lo habitual.

## Opciones

### ×1.5–1.8 opción 1 — Nashville gana (1.23) + Gil Vicente gana (1.41) = 1.73
- P fallo mercado 51.3 % (clasificación: ALTO). P gana central 48.1 %.
- Objeción principal: la pata Gil Vicente (36.3 % de fallo por sí sola) y el empate a 90 min; once de Gil Vicente con rotación anunciada (A Bola, 12-oct, sin abrir), sin alineaciones verificadas. Segunda: Nashville con rotación no cuantificada.
- Objeciones secundarias: dos favoritos con p_modelo ausente (Gil Vicente) o por debajo del mercado (Nashville, -4.9 pp), por lo que el modelo no respalda ninguna; ambas se ven como «margen cero de error».
- Dato que lo resolvería: once de Gil Vicente (14:00) y once de Nashville (~20:30); confirmación de que tu casa liquida el 1X2 de la Taça a 90 minutos.
- Pata sustituta: no hay en el catálogo. Para quedar en ×1.5–1.8 con Nashville (1.23) la segunda pata tendría que cotizar 1.22–1.46; las únicas con esa cuota son LASK–Liverpool 1.28 y Atlético-MG–Torque 1.33, ambas vetadas por rotación. Gil Vicente es la única posible.
- Riesgo que pesa más: rotación/once de Gil Vicente (datos faltantes).

### ×2–2.6 opción 1 — Nashville (1.23) + Gana West Ham (1.68) = 2.07
- P fallo 56.6 % (ALTO).
- Objeción principal: «Gana West Ham» tiene 43.2 % de fallo y el empate es su escenario modal (3 empates en 4 visitas de liga); rotación «s/d» y alineaciones vacías.
- Secundarias: bajas de prensa no oficiales (Veltman en duda); árbitro sin designar.
- Resolvería: once de West Ham y la baja de Veltman; en el aire, no hay H2H útil.
- Sustituta: ninguna superior entre las no-BAJA/no-vetadas para ese rango (Aston Villa Más de 2.5 1.58, 60.3 %, daría 1.94 con Nashville, fuera de rango).
- Riesgo que pesa más: el empate en Lincoln – West Ham.

### ×2–2.6 opción 2 — Nashville (1.23) + RSL Menos de 3.5 (1.66) = 2.04
- P fallo 57.1 % (ALTO).
- Objeción principal: San José visitante con 5/10 de partidos de 4+ goles y RSL concede 2.0 por partido; la ventaja respecto al mercado (13/20 vs 56.1 %) está dentro del ruido.
- Secundarias: sin once ni árbitro; 21:30 para esa pata.
- Dato que lo resolvería: alineación de RSL y San José.
- Sustituta: Dallas Menos de 3.5 (1.58; P fallo 40.9 %) da 1.94, fuera de rango; Lincoln Más de 2.5 (1.66) da 2.04 pero con riesgo propio. No hay mejora clara.
- Riesgo que pesa más: partido abierto con goles de visitante.
- Nota de coherencia: es la opción cuyo prior (base MLS 59 %) coincide con el mercado.

### ×2–2.6 opción 3 — Nashville (1.23) + Lincoln–West Ham Más de 2.5 (1.66) = 2.04
- P fallo 56.2 % (ALTO).
- Objeción principal: el Over solo depende de West Ham; Lincoln aporta 0.8 g/p y gana 1-0 con frecuencia (3 veces).
- Secundarias: mismos datos faltantes del partido; si el 2.5 se queda en 2 goles (1-0 o 1-1) falla.
- Resolvería: once de West Ham (Castellanos/Piroe) y confirmación de baja de Lincoln (Darikwa, Melia).
- Sustituta: ninguna clara (misma situación que la opción 2).
- Riesgo que pesa más: gol único de West Ham.

### ×3–3.8 opción 1 — Nashville (1.23) + Fluminense Más de 1.5 (1.58) + West Ham gana (1.68) = 3.26
- P fallo 74.3 % (ALTO).
- Objeción principal: tres patas con 23–43 % de fallo cada una; ninguna con alineación confirmada. La de Fluminense depende de una ida de semifinal con ambos delanteros ausentes y de un entrenador sancionado.
- Secundarias: West Ham y Nashville ya analizadas.
- Resolvería: onces de las tres.
- Sustituta de Fluminense: Aston Villa Más de 2.5 (1.58, 60.3 %), ojo, muestra de Fenerbahce n=7 solo de previas europeas y Villa rota ~7.0 cambios por partido; no es claramente mejor. Dallas Menos de 3.5 (1.58) tiene riesgo parecido.
- Riesgo que pesa más: la pata Fluminense (0-0/1-0 en ida cautelosa).

### ×3–3.8 opción 2 — Nashville + Fluminense Más de 1.5 + Dallas Menos de 3.5 = 3.07
- P fallo 73.2 % (ALTO).
- Objeción principal: Fluminense – Palmeiras Más de 1.5 (40.7 % de fallo, 5/8 en eliminatorias de la muestra).
- Secundarias: Dallas sin alineaciones; sus 5/10 partidos con 4+ goles en casa. Tres partidos a las 20:30.
- Resolvería: once de Fluminense/Palmeiras, y bajas de Dallas/Seattle.
- Sustituta: no mejora clara. Es la combinación con menor cuota total del rango, así que paga menos por el mismo riesgo.
- Riesgo que pesa más: Fluminense.

### ×3–3.8 opción 3 — Nashville + Fluminense Más de 1.5 + RSL Menos de 3.5 = 3.23
- P fallo 74.6 % (ALTO).
- Objeción principal: Fluminense (igual que antes) más una RSL – San José abierta.
- Secundarias: ninguna adicional; es la que cierra a las 21:30.
- Sustituta: Dallas Menos de 3.5 (1.58) por RSL (1.66) baja cuota total a 3.07 (misma opción 2); la cifra de P es parecida.
- Riesgo que pesa más: Fluminense.

## Alternativas superiores no consideradas
No encuentro en el catálogo patas ≤2.10, no BAJA y no vetadas con P de mercado claramente mayor que las usadas. Quedan fuera por veto de rotación LASK–Liverpool (1.28, 73.9 %) y Atlético-MG–Torque (1.33, 70.4 %). Las siguientes (Aston Villa Más de 2.5 60.3 %, Maldonado Menos de 2.5 57.9 %, Norwich Menos de 3.5 57.2 %, San Diego Más de 2.5 56.8 %) no superan a las patas ya usadas en solidez. Maldonado – Albion es copa uruguaya sin alineaciones; Norwich – Southampton, solidez MEDIA con modelo discrepante (p=.38 vs .57 de mercado, -19 pp, se descarta el modelo en el informe).

## Resumen de veredicto (no vinculante)
- Las 9 opciones son ALTO por P de fallo (44–75 %). La cifra de fallo del mercado es una descripción del riesgo, no una recomendación; la decisión es tuya.
- Menor P de fallo: ×2–2.6 (≈56–57 %) y ×1.5–1.8 (51.3 %); ×3–3.8 supera el 73 %.
- Mayor riesgo transversal: alineaciones vacías y Nashville presente en todas.
