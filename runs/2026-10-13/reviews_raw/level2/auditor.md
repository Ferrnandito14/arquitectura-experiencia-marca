# Nivel 2 — Auditoría adversarial (jornada 2026-10-13, America/Caracas)

Auditor: auditor-adversarial. Hora de la auditoría: 2026-10-13 ~03:50-04:10 UTC (= 23:50-00:10 del 12-oct en Caracas). Cuotas del agregador con sello `odd_date` 03:18:5x UTC.
Etiquetas: **[V]** verificado por mí con datos (archivos del run o API) · **[I]** inferido · **[NV]** no verificable con lo disponible.

Transparencia sobre la API: hice unas 32 invocaciones de `apif_query.py` (H2H x4, standings x~14, varias repetidas desde caché; las repeticiones también cuentan en el contador). Es ligeramente más que las 30 pedidas; no hice ninguna más después. No consulté lineups (no hay once prepartido a estas horas) ni lesiones: **el run entero no contiene datos de bajas** (`grep` de lesion/baja/injur/suspend = 0 aciertos en finalists.json y tickets.json) [V].

## 0. Objeciones transversales (afectan a los 10 borradores)

| # | Objeción | Evidencia / verificación | Impacto |
|---|---|---|---|
| T1 | **Bug en la «implícita sin margen» de doble oportunidad (1X/12/X2).** `tickets.py::_price` normaliza dividiendo por la suma de las 3 cuotas de `odd_1x, odd_12, odd_x2`, que son resultados solapados (suma de probabilidades ≈2). La implícita sale ≈ la mitad. | [V] `matrix.json` guarda `overround: 2.1448` para `resultado.doble_oportunidad`. Reportado vs correcto (desde 1X2 normalizado): Bucaramanga 1X 0.379 vs **0.754**; Simba 12 0.426 vs **0.840**; Harju 12 0.384 vs **0.759**; Fajr X2 0.272 vs **0.550**. En tickets.md el borrador S3 muestra «0.379» (parece enorme ventaja: 0.659 vs 0.379) y es falso. | ALTO (engaña la lectura de S3, S4, A1, A2, A5) |
| T2 | **Apoyo = media aritmética de los Wilson de los dos equipos, no el eslabón más débil**, y para hándicap/totales cada equipo se mide con sus últimos 10 en cualquier competición/sede, sin enfrentar a los dos. | [V] `tickets.py` L111: `lo = (wilson(kh)+wilson(ka))/2`. Hándicap +2.5: «el local no ganó por ≥3» y «el visitante no perdió por ≥3» son dos frecuencias ajenas al cruce. | MEDIO |
| T3 | **Techo de Wilson con n=10: 0.722.** El SKILL pide ≥0.80 por ítem en seguridad; el código lo rebajó a 0.65 (comentario en `DEFAULT_TARGETS`). Con la regla del SKILL ninguna pata de seguridad es elegible; el propio SKILL dice «si no hay combinación defendible, se dice y no se fuerza ningún ticket». | [V] `tickets.py` L30-32; SKILL «Ticket de seguridad … ≥0.80 por ítem». | ALTO (decisión de proceder) |
| T4 | **Casi nada tiene valor por la propia métrica del sistema.** De 2176 patas con cuota media, 289 tienen apoyo ≥0.55 y **solo 1** (Kyoto +1.5) tiene apoyo×cuota>1; solo 2 (Kyoto +1.5, Qatar SC +1.5) superan la implícita sin margen (sin contar 1X/12/X2, ver T1). Los 10 borradores están hechos de patas con EV descriptivo negativo (−12% a −50%). La tabla «atractivo» tiene una sola fila. Además es el máximo entre ~2000 patas (maldición del ganador). | [V] cálculo propio con `tickets.collect_legs`. | ALTO |
| T5 | **Cuota media engañosa; Marathon y 1xBet cotizan idéntico en todas las patas** (una sola vía efectiva) y en muchas patas el «≥3 casas» son 3 con 2 repetidas. El promedio lo suben bet365/Betano/Betfair. Con precios reales de una sola casa **ningún** ticket cae en su rango objetivo. | [V] cuotas por casa del `get_odds` masivo (cache) y producto por ticket: ver tabla §1. | ALTO |
| T6 | **Calendario «2 fuentes independientes» no demostrado.** apifootball y APWin coinciden al segundo en 228 de 231 partidos comunes (las 3 discrepancias son de Zambia). No se consultó ninguna fuente oficial (UEFA, EFL, Liga BetPlay, etc.). | [V] comparación de `original_datetime` en `inventory.json`. Independencia de proveedor: [NV]. | MEDIO |
| T7 | **Mezcla de competiciones/etiquetas rotas en ligas menores.** Ejemplos [V]: filas «FA Trophy – Final» el 26-sep y «FA Cup – Semi-finals» el 3-oct (rondas clasificatorias mal etiquetadas); `league_id=149` agrupa NPL Premier, Southern Central y «Southern Premier South» y **Gloucester y Taunton no aparecen en esa tabla** (90 filas, 70 equipos); Leamington figura con dos líneas distintas (P7 y P10); córners/tarjetas = None en el 100% de filas no-league. Hasta 9 de 20 filas de una muestra son copas (Leamington), 8/20 Gloucester. | dump de `matrix.json` y `get_standings league_id=149`. | ALTO para S5 y para las patas non-league |
| T8 | **Combinadas del mismo partido.** El «apoyo conjunto > independiente» solo prueba correlación positiva; justamente por eso la casa recalcula el precio por debajo del producto. Las patas «Menos de 5.5» pagan 1.03-1.10: añaden 3-10% de pago por un riesgo propio no nulo. | [I] la cuota combinada del ticket (1.45-1.59) es el producto simple, no una cuota de la casa. En CL fase de liga la media es 3.83 goles/partido (n=18 partidos, `get_standings` 3) [V], así que «Menos de 5.5» no es trivial. | ALTO para A1,A2,A3,A5 |
| T9 | **Hándicap visitante +2.5 y favorito local.** Filtrando solo las filas de local del favorito [V]: Inter ganó por ≥3 en 2/6 en casa y por ≥2 en 4/6; Arsenal 2/5 y 3/5; Essen 1/5 y 2/5; Orlando Pirates 1/5 y 4/5; Kyoto 0/5. La frecuencia agregada «0.8/1.0» mezcla filas de visitante y amistosos (Inter: 4 amistosos; Arsenal: 4). El umbral de equilibrio de Inter +2.5 es 69% y el de Arsenal +2.5 68%, frente a 4/6 y 3/5 en casa. | dump `matrix.json` filas `venue=local`. | MEDIO-ALTO para A1,A2,A3,A5 |
| T10 | **Betfair (bolsa) entra en el promedio de fijas** (p. ej. Workington +2.5: Betfair 1.65 vs resto 1.45-1.53; Harju 12: BetVictor 1.07 vs WilliamHill 1.25). Un solo precio extremo mueve el promedio. | [V] cuotas por casa. | MEDIO |

## 1. Precios por casa vs «cuota media» (producto por ticket) [V]

| Borrador | Cuota media (tickets.md) | Solo Marathon/1xBet | Mediana por pata | Mejor precio por pata | Rango objetivo |
|---|---|---|---|---|---|
| S1 | 1.217 | 1.190 | 1.190 | 1.270 | 1.20-1.28 |
| S2 | 1.241 | 1.200 | 1.250 | 1.270 | idem |
| S3 | 1.234 | 1.220 | 1.250 | 1.270 | idem |
| S4 | 1.212 | 1.155 | 1.199 | 1.288 | idem |
| S5 | 1.276 | 1.230 | 1.248 | 1.356 | idem |
| A1 | 4.009 | 3.678 | 3.729 | 5.11 | 4.0-4.8 |
| A2 | 4.051 | 3.389 | 3.463 | 4.129 | idem |
| A3 | 4.034 | 3.790 | 3.871 | 4.977 | idem |
| A4 | 4.042 | 3.252 | 3.391 | 4.277 | idem |
| A5 | 4.031 | 3.781 | 3.958 | 5.153 | idem |

(Los productos por pata ignoran que las parejas del mismo partido se repricean; y A2/A4 incluyen una pata con cuota inventada; ver abajo.) «Mejor precio» exige repartir las patas entre casas distintas, algo que la regla de no mezclar casas en un multiplicador prohíbe.

Break-even y EV (mi cálculo, implícita sin margen con DC corregido, independencia entre patas; los pares del mismo partido son positivamente correlados pero la casa los repricea) [V para los números, I para su lectura]:

| | S1 | S2 | S3 | S4 | S5 | A1 | A2 | A3 | A4 | A5 |
|---|---|---|---|---|---|---|---|---|---|---|
| Acierto necesario (1/cuota) | 82.2% | 80.6% | 81.0% | 82.5% | 78.4% | 24.9% | 24.7% | 24.8% | 24.7% | 24.8% |
| Implícita conjunta de mercado | 75.1% | 75.2% | 75.4% | 70.5% | 65.2% | 18.3% | 20.7% | 16.1% | 18.8% | 15.5% |
| EV de mercado | −8.6% | −6.6% | −7.0% | −14.6% | −16.9% | −26.5% | −16.0% | −35.2% | −24.1% | −37.5% |
| EV con Wilson conjunto (tickets.md) | −12% | −18% | −19% | −37% | −39% | −24% | −28% | −50% | −50% | −50% |

Nota honesta: comparar un límite inferior de Wilson con una probabilidad «justa» sesga siempre contra el pick; la lectura correcta es «no hay evidencia de ventaja sobre el mercado», no «EV demostrado negativo».

## 2. Borradores «seguridad» ×1.20-1.28

### S1 — Kyoto Sanga–Ratchaburi, hándicap visitante +2.5 @1.217. Riesgo principal: MEDIO
**Objeción principal:** el precio ejecutable es peor que el anunciado y fuera de rango. Solo 3 casas cotizan +2.5 (Marathon 1.19, 1xBet 1.19, bet365 1.27); Marathon y 1xBet son la misma cifra, así que la «media 1.217» la sostiene una sola casa. [V] A 1.19 el ticket queda en ×1.19 (<1.20). Equilibrio 82.2% vs implícita de mercado 75.1% y Wilson 0.722.
**Secundarias:**
1. Muestra: solo liga, n=6 y 6 (apoyo 0.61, no 0.722); Ratchaburi incluye 2 amistosos ante equipos menores (6-2, 5-0) y goleadas 6-1/6-0 en Liga Tailandesa; en la CL concedió 6 (4-6 ante Shanghai Port, 15-sep). No hay H2H (consulta `get_H2H` 5078/397 vacía). [V]
2. El mercado asigna ~25% a que Kyoto gane por ≥3 (Kyoto −2.5 a 3.55-3.74), mientras su historial dice 0/10 (0/5 en casa; solo 9 goles en 10 partidos). La discrepancia 25% vs 0% es un aviso de que el historial no captura el cruce. [V cifras, I lectura]
3. Calendario: 06:00 Caracas, ~6 h tras el sello de las cuotas; ambas fuentes de calendario coinciden al segundo (T6); sin once ni bajas. [V/NV]
**Dato que la resolvería:** precio real en la casa del usuario ≥1.20 y comprobación de once (≈1 h antes) + una fuente oficial AFC/clubes.
**Veredicto sugerido:** MANTENER solo como «menos mala» si la casa paga ≥1.20; si paga 1.19 el ticket sale del rango. **Alternativa:** misma lógica en Queen's Park +2.5 local (ver §4).

### S2 — Cardiff–Watford, menos de 4.5 goles @1.241. Riesgo principal: BAJO-MEDIO
**Objeción principal:** pagar 24% por arriesgar el 100% exige 80.6%; el mercado pone la implícita en 75.2% (casas 1.20-1.27, Marathon 1.20) y el único «fallo» del historial es una copa (Watford 1-5 Peterborough). Sin ventaja demostrable, solo es la pata mejor sustentada. [V]
**Secundarias:**
1. Solo liga: 9/9 y 9/9 (apoyo 0.701); H2H 6/6 con ≤4 goles (2,3,1,2,4,3) [V]; Championship 2.83 goles/partido en n=107 [V]. Tienden a favor: la objeción es de precio, no de muestra.
2. Equipos 20.º y 21.º con GA 14 en 9 partidos cada uno: un 3-2/4-1 es plausible; el mercado cotiza Over 4.5 a 3.7-4.0 (~25%) [V], mucho más que la tasa histórica de la muestra. 
3. Bajas/once: no consultados [NV]; partido 14:45 Caracas.
**Dato que lo resolvería:** cuota real ≥1.24 y once. **Veredicto:** MANTENER (la más defendible de seguridad junto con S3).

### S3 — Bucaramanga–Águilas Doradas, 1X @1.234. Riesgo principal: MEDIO
**Objeción principal:** la implícita mostrada (0.379) es un bug (T1); la correcta es 0.754 (equilibrio 81%): sin ventaja. [V]
**Secundarias:**
1. Doble oportunidad que depende del empate: la liga tiene 31.5% de empates (Clausura 34.1%, n=126 partidos) y Águilas ganó el último H2H (2-1, abr-2026); en los 4 H2H con Bucaramanga de local hay 2 victorias, 1 empate y 1 derrota (0-1, oct-2022). [V]
2. Bucaramanga como local en Clausura: 2V-3E-0D en 5; invicta 11 partidos. La muestra sí es 100% liga (10/10 y 9/10). Positivo, pero sin ajuste por rival. [V]
3. Cuotas 1.16 (Sbo) a 1.27: 8 casas, rango amplio; Marathon 1.22. [V]
**Veredicto:** MANTENER como alternativa; no vale más que S2. **Dato:** cuota real de la casa y bajas.

### S4 — Norrköping–Sundsvall U5.5 @1.107 + Simba–Mashujaa «12» @1.095 → ×1.212. Riesgo principal: MEDIO
**Objeción principal:** doble pata con equilibrio 82.5% y precios Marathon 1.09×1.06=**1.155** (<1.20): el rango solo se alcanza con bet365/Betfair/Betano. [V]
**Secundarias:**
1. Simba «12»: muestra de Tanzania con huecos y de dos temporadas (3 filas previas al 1-jul; hueco 30-jun→15-ago; cards/corners casi todos None); 0 empates en 20 filas pese a que la liga tiene 15.5% (9/58, `get_standings` 551). La probabilidad real de empate no es 0; la implícita correcta de «12» es 0.840 (equilibrio 91%). [V]
2. Norrköping: Superettan, 1.º vs 16.º; U5.5 en solo liga 17/17. La pata es sólida pero paga 10%: equilibrio 90%, mercado 0.839. [V] Dos amistosos entre las filas (no cuentan).
3. Simba juega a las 12:00 Caracas; Norrköping 13:00; sin bajas. [V horario / NV bajas]
**Veredicto:** SUSTITUIR la pata Simba por Queen's Park +2.5 o Sariyer U4.5 (ver §4); mantener Norrköping U5.5.

### S5 — Gloucester–Taunton O1.5 @1.093 + Hyde–Quorn O1.5 @1.167 → ×1.276. Riesgo principal: ALTO
**Objeción principal:** peor calidad de datos de todo el lote. [V] Gloucester y Taunton **no existen en la tabla** `league_id=149`; el 40% de las filas de Gloucester/Hyde son copas con etiquetas inventadas («FA Trophy Final» 26-sep); sin córners ni tarjetas; en solo liga el apoyo cae de 0.722 a 0.606 (5/5+7/7) y de 0.659 a 0.587 (Hyde). Marathon paga 1.07 y 1.15 → ×1.23.
**Secundarias:**
1. Hyde–Quorn: 3 casas (1.15, 1.15, 1.20); Betano empuja la media. [V]
2. Ambos partidos a las 18:45Z el mismo día y en divisiones no-league: correlación por condiciones (clima, calidad de campo, bajas no publicadas) y por proveedor único de datos. [I]
3. Equilibrio de Gloucester 91.5% por ganar 9%; Hyde–Quorn 85.7%. EV de mercado −17%. [V]
**Veredicto:** DESCARTAR.

## 3. Borradores «amplio» ×4.0-4.8

### A1 — Workington O2.5 + Fajr X2 + Inter U5.5 + Brugge +2.5 → ×4.009 (3 partidos). Riesgo principal: ALTO
**Objeción principal:** ningún precio ejecutable llega a 4.0 (Marathon 3.68; mediana 3.73). Betfair 1.65 en Workington O2.5 (resto 1.45-1.53) y bet365/Betano en el resto levantan el promedio. [V]
**Secundarias:**
1. Workington O2.5: solo liga 6/7 y 7/8 → apoyo 0.508; Workington/Whitby en NPL (3.31 goles/partido) pero Whitby 16.º con 17-32; la muestra incluye 5 copas mal etiquetadas. Implícita 0.609 > apoyo 0.596 > …; sin ventaja. [V]
2. Fajr X2: n=7 (<8 = muestra débil por el skill). La liga iraní tiene 39.7% de empates y 1.94 goles/partido (n=68) [V], lo cual favorece X2, pero el mercado ya cotiza Fajr local favorito (1X2 2.02/2.96/3.75) pese a ser 14.º (1V-4E-2D) frente a un Arak 5.º invicto: indicio de información no recogida (bajas/local) [I]. Calendario Irán: riesgo de aplazamiento [NV].
3. Pareja Inter: Inter ganó por ≥3 en 2/6 de sus partidos en casa y por ≥2 en 4/6 (incluido amistoso Lumezzane). Brugge +2.5 en solo liga: 4/6 + 8/8 → 0.488. La «Menos de 5.5» (1.10) añade riesgo (CL: 3.83 goles/partido en n=18) y la casa no pagará 1.589 por el par. [V/I]
**Veredicto:** SUSTITUIR (quitar «Menos de 5.5» de Inter y Workington O2.5; sin esas patas no llega a 4.0).

### A2 — Fajr X2 + Athletic-MG O1.5 + «Más de 2.5 tarjetas» + Arsenal U5.5 + Lille +2.5 → ×4.051. Riesgo principal: ALTO (bloqueante)
**Objeción principal:** una pata es una **cuota inventada**: «Más de 2.5 tarjetas (A+R)» @1.13 sale de la fórmula `1/(p_suavizada×1.08)` aplicada a la misma estadística (`cuota_tipo estimada_por_modelo`, n_casas=0). Una línea de 2.5 tarjetas totales probablemente ni existe en casas (líneas habituales 3.5-5.5) [I]; sin esa pata el ticket es ×3.585 (4.051/1.13), fuera de rango. [V aritmética]
**Secundarias:**
1. Regla de liquidación de tarjetas (¿doble amarilla = 1 o 2? ¿puntos de reserva?) sin verificar; datos de tarjetas con filas None (n=9). [V/NV]
2. Arsenal: la CL tiene 3.83 goles/partido; Arsenal en casa ganó por ≥3 en 2/5 y por ≥2 en 3/5; Lille +2.5 en solo liga 5/6+6/6 → 0.523 (<equilibrio 68%). Pareja con Under 5.5 @1.06 (equilibrio 94%). [V]
3. Fajr n=7, Athletic-MG O1.5: Londrina 8/10 (apoyo 0.606 < implícita 0.675) con 7 casas muy concordantes (1.35-1.40). [V]
**Veredicto:** DESCARTAR.

### A3 — Essen–Köln +2.5, Arsenal–Lille +2.5, Inter U5.5 + Brugge +2.5, Birmingham–Preston +1.5 → ×4.034. Riesgo principal: ALTO
**Objeción principal:** cuatro hándicaps de «el favorito no arrasa» con apoyo 0.56-0.66 inferior al equilibrio de cada pata (68-85%); en casa el favorito arrasó con frecuencia relevante (Arsenal 2/5, Inter 2/6, Essen 1/5 por ≥3). [V] EV de mercado −35%. Marathon: 3.79.
**Secundarias:**
1. Birmingham–Preston +1.5: apoyo 0.56 < implícita 0.595; Preston es 24.º (1V-1E-7D, DG −8) y Birmingham como local 0V-4E-0D (7-7); solo liga 9/9 y 7/9; H2H: 6 partidos, todos de un gol (a favor) [V]. La pata tiene sentido deportivo pero el precio es justo.
2. Essen +2.5: 3 casas (1.16, 1.16, 1.23); Essen anotó 6-2 y 5-2 en sus filas (equipo de goleada); Köln fuera 2V-1E-1D. [V]
3. Cuatro patas «underdog pierde de poco» correlacionan en un día de favoritos fuertes (UCL 19:00Z comparte hora con Birmingham 19:00Z). [I]
**Veredicto:** SUSTITUIR/DESCARTAR; si se quiere conservar algo, solo Birmingham +1.5 y Essen +2.5, sin las patas de Inter y Arsenal.

### A4 — Leamington O1.5 + Workington O2.5 + Athletic-MG O1.5 + tarjetas>2.5 + Birmingham +1.5 → ×4.042. Riesgo principal: ALTO (bloqueante)
**Objeción principal:** misma cuota inventada que A2 (1.13); sin ella ×3.577 (Marathon 3.25). [V]
**Secundarias:**
1. Tres de cinco patas son non-league o con mala calidad de datos: Leamington O1.5 en solo liga 6/6+5/5 → 0.588; 9 de 20 filas son copas; standings con dos líneas inconsistentes. [V]
2. Workington O2.5 repetida del A1/A5 (concentración: si falla, caen 3 de los 5 borradores). [V]
3. Birmingham +1.5 apoyo 0.56 < implícita 0.595. [V]
**Veredicto:** DESCARTAR.

### A5 — Harju–Nõmme «12», Workington O2.5, Arsenal U5.5 + Lille +2.5, Orlando U5.5 + Galaxy +2.5 → ×4.031 (6 patas). Riesgo principal: ALTO
**Objeción principal:** 6 patas, 2 parejas del mismo partido con precios 1.03/1.06 que no aportan pago pero sí riesgo, y la pata Orlando +2.5 en solo liga cae a 3/5 (apoyo 0.438); en casa Orlando ganó por ≥3 solo 1 de 5. EV de mercado −37.5%. [V]
**Secundarias:**
1. Orlando–Galaxy: la competición viene etiquetada «Play-offs 1/2» (league_id 297) y la tabla tiene 40.4% de empates, 2.28 goles/partido (n=57) [V]; datos de la liga principal mezclados con play-offs.
2. Harju «12»: el equipo aparece como «Harju Jalgpallikool» en la API y como «Harju JK Laagri» en la tabla (identidad de nombre a confirmar; las filas cruzadas del 29-ago coinciden, así que es el mismo club [I]); BetVictor 1.07 vs WilliamHill 1.25 (spread enorme); la tasa de empates de la liga es 12.7% (n=150), lo que sí apoya «12», con 10-0 de copa en la muestra. [V]
3. Arsenal pareja (ver A2). [V]
**Veredicto:** DESCARTAR.

## 4. Mejores alternativas no consideradas (verificadas con datos; sin garantía)

| Pata | Datos [V] | Observación |
|---|---|---|
| Queen's Park +2.5 local @1.09 (Escocia Championship) | 10/10+10/10, 2.06 goles/partido (n=47); Inverness no ganó por ≥3 en sus 10 filas y QP nunca perdió por ≥3 en sus 10 | Mejor sustituto de pata «segura»; precios 1.06-1.13, igual problema de equilibrio (91.7%). Candidato a reemplazar Simba «12» en S4 (Norrköping 1.107 × QP 1.09 = 1.207; con Marathon 1.09×1.06=1.155 <1.20) |
| Sariyer–Bodrumspor U4.5 @1.07 | 10/10+10/10; muchos 0-0/1-0 | 10:00 Caracas; equilibrio 93% |
| Harju–Nõmme «12» (por tasa base de la liga) | liga con 12.7% empates (n=150); implícita mercado 0.759 | única pata «12» con respaldo por base de liga, pero identidad y spread 1.07-1.25 |
| Kyoto +1.5 @1.683 | único con apoyo×cuota>1 y apoyo>implícita (+0.10) | mismo partido que S1 (regla: no repetir entre multiplicadores); solo liga 6/6+6/6 (0.61); señal de maldición del ganador |
| Cardiff U4.5, Bucaramanga 1X | ver S2/S3 | ya son las más sólidas |

Descartados de los top por seguridad por mi parte: Hartlepool–Newcastle U21 y Cheltenham–Tottenham U21 (juveniles, ya marcados); Nat. Bank Egypt–El Gaish y Ebbsfleet/Lehota (1 sola fuente de calendario, ya marcados).

## 5. Orden de menos a más defendible

- **Seguridad:** S5 (menos) < S4 < S1 < S3 < S2 (más). Razón: S5 datos rotos y 2 patas; S4 dos patas y precio < 1.20 con Marathon; S1 3 casas/1 vía y 06:00; S3 y S2 un solo evento con 7-8 casas.
- **Amplio:** A5 (menos) < A4 < A3 < A2 < A1 (más). A2 y A4 dependen de una cuota inventada (bloqueante); entre A1 y A3, A1 tiene todas las patas con cuota real y menor EV negativo en mi cálculo; aun así ninguno llega a 4.0 con precios de una sola casa.

## 6. Objeciones críticas que bloquearían apostar (hasta resolverse)

1. **Cuota inventada** en A2 y A4 (tarjetas >2.5 @1.13, fórmula circular). Sin cuota real, sin multiplicador. [V]
2. **Rangos no alcanzables con precios reales de una casa**: todos los amplio (3.25-3.96 con Marathon/mediana) y S1/S4 (<1.20 con Marathon). Hace falta la cuota real de la casa del usuario para cada pata, misma casa. [V]
3. **Regla del propio SKILL (≥0.80 en seguridad)**: ninguna pata la cumple (techo 0.722 con n=10); hay que declararlo en lugar de forzar tickets. [V]
4. **Bug de «implícita» en 1X/12/X2** (T1): corregir antes de citar «ventaja» en S3/S4/A1/A2/A5. [V]
5. **Parejas del mismo partido (Inter, Arsenal, Orlando, Athletic-MG)**: exigir la cuota real de «crear apuesta»; el producto es solo un tope. [I]
6. **Sin bajas/once/árbitro/regla de tarjetas**: nada de lesiones en el run; once no publicado. [V/NV]
7. **Calendario**: sin fuente oficial y con apifootball≈APWin al segundo; Irán (Fajr) y Tanzania/non-league sujetos a cambios de hora. [V/NV]
8. **Datos de ligas menores** (T7) para S5, Leamington, Hyde, Gloucester, Workington. [V]

## 7. Lo que no pude verificar
Cuotas de la casa del usuario; alineaciones/lesiones; fuentes oficiales; independencia real entre APWin y apifootball; árbitro y regla de liquidación de tarjetas; variación de cuotas desde las 03:18 UTC; existencia de la línea Over 2.5 tarjetas en alguna casa.
