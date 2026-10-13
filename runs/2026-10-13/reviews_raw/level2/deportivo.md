# NIVEL 2 – Análisis deportivo (jornada 2026-10-13, America/Caracas)
Analista deportivo. Consulta hecha el 2026-10-13 ~03:50-04:00 UTC. 21 partidos / 41 entradas de pata = 26 patas únicas (las 41 repiten las mismas patas en distintas listas).

## 0. Alcance, fuentes y límites (leer primero)
| Fuente | Ficha concreta | Dato buscado | Estado | Valor | Discrepancias / alternativa |
|---|---|---|---|---|---|
| apifootball vía apif_query.py | get_standings, 16 ligas (ids 10,153,120,305,551,149,195,3,75,176,156,297,282,141,319,8129) | clasificación, objetivos, local/visitante | Consultada y útil (15 de 16); liga 8129 (National League Cup) devolvió 0 filas | alto salvo 8129 | liga 149 (non-league inglesa): sin filas de Gloucester ni Taunton; Leamington/Redditch aparecen duplicados con dos juegos de datos distintos (7 vs 10 partidos jugados) |
| apifootball | get_H2H en 14 pares (Harju-Nõmme, Simba-Mashujaa, Fajr-Arak, QPark-Inverness, Workington-Whitby, Birmingham-Preston, Cardiff-Watford, Essen-Köln, Gloucester-Taunton, Leamington-Redditch, Hyde-Quorn, Norrköping-Sundsvall) | H2H reciente | Consultada y útil (Hyde-Quorn: 0 filas; Essen-Köln y Fajr-Arak: 1 sola fila) | medio/bajo | H2H antiguo en varias (QPark 2022-24, Cardiff 2022-25, Leamington 2023-24) -> bajo peso |
| apifootball | get_lineups match_id=848527 (Kyoto-Ratchaburi, el más temprano, 10:00Z) | once/bajas | Consultada con datos insuficientes: sin alineaciones ni missing_players (solo entrenadores Popovic y Srimaka) | nulo | a las 04:00Z no hay alineaciones de ningún partido; no pedí el resto para no gastar cupo. NO se inventan bajas |
| matrix.json (campo form) | 10 últimos por equipo | k/n por pata | Consultada y útil | alto (recalculado) | MISMO proveedor (apifootball) que standings/H2H: no son evidencias independientes |
| Flashscore, Soccerway, FotMob, FootyStats, Transfermarkt, prensa local, etc. | – | 2.ª/3.ª fuente, bajas, árbitros | No consultadas (la instrucción fija apif_query como única vía externa) | – | El mínimo del protocolo multifuente (>=3 proveedores por partido) NO se cumple; todo lo de abajo es "una sola fuente (apifootball)" |

Consultas propias: ~30 (el contador global marca 83 por consumo de otros agentes).
Etiquetas: [V] verificado en apifootball (standings/H2H/form recalculado), [I] inferido por mí, [ND] no disponible.

### Hallazgos transversales
1. Recalculo k/n de las 26 patas desde matrix.form: TODAS coinciden con finalists.json (frec y n). No hay desvinculación partido/mercado. [V]
2. El historial es el de cada equipo en TODAS sus competiciones, no ajustado por rival ni localía. Para los hándicaps y 1X/X2 calculé también k/n solo en la sede relevante (local en casa, visitante fuera): ver tablas.
3. Las frecuencias muestrales (casi todas 1.0-0.9) superan sistemáticamente a lo que el mercado asigna (p. ej. Cardiff-Watford Under 4.5: 19/20 vs 0.75 de mercado; Athletic-Londrina Over 1.5: 18/20 vs 0.675; Kyoto +2.5: 20/20 vs 0.75). 10 partidos sin ningún "fallo" son compatibles con regresión a la media. [I]
4. Etiquetas de competición erróneas en apifootball: varios equipos non-league inglesas (Gloucester, Hyde, Quorn, Leamington, Workington, Whitby...) tienen "FA Trophy - Final", "FA Cup - Semi-finals" el mismo mes; los equipos sudafricanos tienen "Play-offs 1/2" para liga regular; Simba "CAF CL Semi-final" en sept. Son rondas previas mal rotuladas: la muestra mezcla ligas con eliminatorias contra equipos de nivel muy inferior. [V]
5. En finalists.json el campo prob_implicita_sin_margen de las patas de doble oportunidad es incoherente: 1X Bucaramanga 0.3786 (con cuotas 1X2 1.979/3.202/3.756 la 1X sale ~0.75), "12" Simba 0.4261, "12" Harju 0.3837, X2 Fajr 0.2724 (esperable ~0.55-0.60). Parece tomar la probabilidad de un único resultado. Las cuotas de DC sí son coherentes con la 1X2 (comprobado: 1/(1/h+1/a) cuadra). Corregir el campo antes de calcular EV. [V]
6. Las prob. "sin margen" de hándicap tienen margen de 10-15% al emparejar promedios de casas distintas (p. ej. Birmingham +1.5: 1/1.459 + 1/2.139 = 1.15). Poco fiables. [I]
7. Cuota de la pata de tarjetas Athletic-MG: ESTIMADA por modelo (n_casas=0). [V]
8. Hartlepool-Newcastle U21: las cuotas 1X2 (local 5.36 / visitante 1.40) parecen invertidas o mal vinculadas (U21 perdió sus 3 partidos de National League Cup contra clubes senior; es el visitante). [I]

## 1. Tabla por partido (veredicto por pata)
Formato k/n = local/visitante (sede relevante entre paréntesis). Confianza: A alta, M media, B baja.

### 1. Kyoto Sanga - Ratchaburi (AFC Champions League Elite, 10:00Z; calendario 2 fuentes)
| Pata | Cuota | frec recalc. | Veredicto |
|---|---|---|---|
| Hándicap visitante +2.5 | 1.217 | Kyoto no gana por 3+: 10/10 (5/5 casa); Ratchaburi no pierde por 3+: 10/10 (8/8 sin amistosos) | MANTENER (M-A) |
| Hándicap visitante +1.5 | 1.683 | Kyoto no gana por 2+: 10/10 (5/5); Ratchaburi no pierde por 2+: 9/10 (7/8 competitivos; la derrota 4-6 vs Shanghai Port) | MANTENER (M); redundante con +2.5 (+2.5 la contiene) |
Justificación:
- [V] Kyoto marcó 9 goles en sus últimos 10 (0 goles en 4: 0-2 FC Tokyo, 0-1 Daejeon, 0-1 Machida x2) y no ganó por 2+ ninguno. Su defensa (11 GA/10) tampoco ayuda a una goleada. Mercado 1X2: 1.38/4.63/7.05 -> es favorito, pero su rendimiento ofensivo no soporta un 3+.
- [V] ACL Elite jornada 2: Kyoto #12 (0-1 en Daejeon), Ratchaburi #13 (perdió 4-6 en casa vs Shanghai Port). Contra: Ratchaburi encajó 6 en ese partido y su muestra es de Thai League/amistosos (2 amistosos 6-2 y 5-0) -> rival más débil que el de Kyoto (J1); jugó 7-oct, 9-oct y viaja a Japón (cansancio, rotación [I]). Alineaciones: [ND].
- Invalidaría: once rotado de Ratchaburi, o Kyoto con delantero/penal temprano y expulsión visitante. H2H: [ND] (no consultado; sin cruce relevante esperado).

### 2. Cardiff City - Watford (Championship, 18:45Z)
| Pata | Cuota | frec recalc. | Veredicto |
|---|---|---|---|
| Menos de 4.5 goles | 1.241 | 10/10 y 9/10 (19/20; el fallo: Watford 1-5 Peterborough, League Cup) | MANTENER (M) |
Justificación:
- [V] Clasificación: Cardiff #21 (1-4-4, 11:14), Watford #20 (2-2-5, 7:14), defensas flojas en ambos: totales en liga Championship del par <=4 en 19/20. H2H 6 duelos 2022-25 todos <=4 goles (viejo, poco peso).
- [V] El mercado asigna ~25% a 5+ goles (Over 4.5 a 3.77) mucho más que la muestra; ambas defensas encajan 1.5-1.6 por partido. Estimación mía: el riesgo real de 5+ es de 10-15% [I].
- Invalidaría: Cardiff vino de perder 0-4 en casa vs Burnley (10-oct): si hay cambios masivos o expulsión temprana. Alineaciones: [ND].

### 3. Atlético Bucaramanga - Águilas Doradas (Primera A, 23:30Z)
| Pata | Cuota | frec recalc. | Veredicto |
|---|---|---|---|
| Local o empate (1X) | 1.234 | Buc no pierde: 10/10 (5/5 casa); Águilas gana solo 1/10 (9/10; 5/5 fuera) | MANTENER (M-A) |
Justificación:
- [V] Clausura: Buc #4, 6-5-0 en 11 (invicto), en casa 2-3-0 (9:5), fase cuadrangular; Águilas #11, fuera 1-2-3 (6:10). Buc no perdió en los últimos 5 en casa (1-1, 1-1, 2-2, 2-0, 3-1).
- [V] Mercado: 1.98/3.20/3.76 -> 1X real ~0.75 (el campo prob_implicita 0.3786 está mal). Contra: Buc empata mucho (5 de 11) y en Apertura perdió 1 de 9 en casa; el empate cuenta en 1X, así que solo la derrota local es el riesgo.
- Invalidaría: lesión clave o rotación por calendario del cuadrangular. Alineaciones: [ND].

### 4. Norrköping - GIF Sundsvall (Superettan, 17:00Z)
| Pata | Cuota | frec | Veredicto |
|---|---|---|---|
| Menos de 5.5 goles | 1.107 | 10/10 y 10/10 (9/9 y 9/9 sin amistosos/competitivos) | MANTENER (M) |
Justificación:
- [V] Norrköping #1 (17-4-4, 48:16), Sundsvall #16 (6-1-18, 19:53, fuera 5:25). Goles esperados del cruce ~3.5 [I]; el mercado pone Over 5.5 a 5.76 (~16%). H2H: mayo-2026 Sundsvall 1-3 (4 goles).
- Contra: el 20/20 sobrestima la seguridad (la goleada 5+ por parte del líder es el riesgo real, ~10-15%). Muestras con 1-2 amistosos/copa. Pata de valor mínimo (1.107). Alineaciones: [ND].

### 5. Simba - Mashujaa (Ligi Kuu, 16:00Z)
| Pata | Cuota | frec | Veredicto |
|---|---|---|---|
| Gana alguno, sin empate (12) | 1.095 | 10/10 y 10/10 (cero empates) | MANTENER (M-A) |
Justificación:
- [V] Tres señales independientes de la misma fuente: Simba #1 con 7-0-0 (13:3), Mashujaa #4 4-0-3: 0 empates entre ambos en 14 partidos-equipo de temporada; H2H 6/6 decididos (2024-26, Simba siempre gana, último 3-0 en mayo-2026).
- Contra: la liga tiene normalmente empates (mercado da el empate a 5.6, ~16%); Simba jugó el derbi el 10-oct (2-1 a Young Africans) y puede rotar [I]. Datos de córners/tarjetas ausentes en esta liga (calidad de datos baja), sin impacto en esta pata. Alineaciones: [ND].

### 6. Gloucester City - Taunton Town (Southern League Premier South, 18:45Z)
| Pata | Cuota | frec | Veredicto |
|---|---|---|---|
| Más de 1.5 goles | 1.093 | 10/10 y 10/10 | MANTENER (M) |
Justificación:
- [V] H2H 4/4 con >=2 goles (0-2, 2-1, 2-2, 3-3). Taunton: totales 3-9 en todos sus 10 (más de 2.5 en 10/10); Gloucester: 4 de 10 con exactamente 2 goles (margen estrecho).
- Contra: muestras con 5 y 3 eliminatorias (mal rotuladas) contra equipos de escalones inferiores; sin clasificación (Gloucester/Taunton no salen en la liga 149) [ND]; datos non-league sin córners/tarjetas. Calidad de datos baja. Alineaciones: [ND].

### 7. Hyde United - Quorn (Northern Premier League, 18:45Z)
| Pata | Cuota | frec | Veredicto |
|---|---|---|---|
| Más de 1.5 goles | 1.167 | 9/10 (Hyde; 4/4 en casa) y 10/10 | MANTENER (M) |
Justificación:
- [V] Hyde #13 (13:23 en 13), Quorn #15 (21:27 en 12; fuera 10:11 en 6). Hyde en casa 6:6 en 6.
- Contra: Hyde no marcó en 3 de sus 10 (0-4, 0-1, 0-2 los dos últimos fuera); H2H: [ND] (0 filas). Muestra con copas y rivales de distinto escalón; alineaciones [ND].

### 8. Workington - Whitby Town (Northern Premier League, 18:45Z)
| Pata | Cuota | frec | Veredicto |
|---|---|---|---|
| Más de 2.5 goles | 1.508 | 9/10 (4/5 casa) y 9/10 (4/4 fuera) | MANTENER (M) |
Justificación:
- [V] Workington #6 (23:22 en 13; casa 12:9), Whitby #16 (17:32 en 12; fuera 11:13 en 5 = 4.8 goles/partido). Ambos con defensas abiertas.
- En contra [V]: el H2H (6, 2023-26) solo da >2.5 en 3/6 (0-0 en enero-2026). Peso: forma reciente > H2H por muestra pequeña, pero obliga a confianza media (apoyo 0.596, el más bajo de las Over). Muestra con copas contra rivales más débiles. Alineaciones [ND].

### 9. Fajr Sepasi - Aluminium Arak (Persian Gulf Pro League, 13:30Z)
| Pata | Cuota | frec | Veredicto |
|---|---|---|---|
| Empate o visitante (X2) | 1.673 | Fajr no gana: 6/7 (3/3 casa); Arak no pierde: 7/7 (3/3 fuera) | MANTENER (M-B) |
Justificación:
- [V] Arak #5, invicto (3-4-0, 9:4), fuera 3-0-0 (6:1); Fajr #14 (1-4-2, 4:9), en casa 0-3-0 (1:1). H2H: 1 sola fila (1-1, nov-2025).
- Contra: n=7 (<8, muestra débil; hay una pausa del 7-sep al 8-oct), liga de baja calidad de datos (sin córners/tarjetas casi siempre), y el mercado (4 casas) coloca a Fajr como favorito (2.02 vs 3.75): hay una información que no vemos (sede, viaje, bajas) [I]. Alineaciones: [ND]. Comprobar cuota en la casa real.

### 10. Inter - Club Brugge (UEFA Champions League, 19:00Z)
| Pata | Cuota | frec | Veredicto |
|---|---|---|---|
| Menos de 5.5 goles | 1.103 | 9/10 y 10/10 (sin amistosos: 6/7 y 9/9) | MANTENER (M) |
| Hándicap visitante +2.5 | 1.441 | Inter no gana por 3+: 8/10 (4/6 casa; sin amistosos 5/7 y 2/4 casa); Brugge no pierde por 3+: 10/10 | SUSTITUIR -> quitar la +2.5 y dejar el Under 5.5 (B) |
Justificación:
- [V] En sus 4 partidos competitivos en casa Inter ganó por 3+ en 2 (4-1 Monza, 3-0 Parma) y marcó 5 al Udinese; Brugge sacó 5 partidos con 3+ goles propios. Muestra de Inter incluye 3 amistosos; la de Brugge es en su mayoría liga belga (rival muy inferior al de Inter).
- [V] Mercado: Inter 1.25, hándicap -2.5 a 2.66 (~35-37% de goleada 3+). Apoyo 0.606 ≈ mercado: no es pata de "seguridad". UCL: Inter perdió 1-2 en Madrid, Brugge 2-3 en casa vs Villa (jornada 2 de liga).
- Under 5.5: riesgo real de un 5-1/4-2 ~10-14% [I]. Alineaciones: [ND].

### 11. Athletic-MG - Londrina (Serie B, 22:30Z)
| Pata | Cuota | frec | Veredicto |
|---|---|---|---|
| Más de 1.5 goles | 1.374 | 10/10 y 8/10 | MANTENER (B-M) |
| Más de 2.5 tarjetas (A+R) | 1.13 ESTIMADA | 8/9 y 8/9 | SUSTITUIR / quitar salvo cuota real (B) |
Justificación:
- [V] Athletic #15 (42 pts, 38:37), Londrina #18 en descenso (28 pts, 40:47) -> motivación alta para Londrina. Over 1.5: 18/20, pero el mercado da 0.675: Athletic no tuvo ni un partido con <=1 gol en 10 (con 2.3 goles/partido de media, un 10/10 así es poco probable, p~3% [I]) -> hay regresión; Londrina tuvo dos 0-0 en sus últimos 10.
- Tarjetas: [V] k/n 16/18 con la línea muy baja (2.5; la línea habitual de A+R en Serie B suele ser mayor [I]). La cuota es del modelo (0 casas), no hay árbitro designado ([ND]) ni regla de liquidación de la casa verificada. No hay forma de comprobar el precio.
- Alineaciones: [ND].

### 12. Arsenal - Lille (UEFA Champions League, 19:00Z)
| Pata | Cuota | frec | Veredicto |
|---|---|---|---|
| Menos de 5.5 goles | 1.06 | 9/10 y 10/10 (8/9 y 7/7 sin amistosos) | MANTENER (M-A) |
| Hándicap visitante +2.5 | 1.471 | Arsenal no gana por 3+: 8/10 (3/5 en casa; sin amistosos 7/9 y 2/4 casa); Lille no pierde por 3+: 10/10 | SUSTITUIR -> quitar la +2.5 (B) |
Justificación:
- [V] Arsenal ganó por 3+ dos de sus 4 partidos competitivos en casa (3-0 Man City en Community Shield, 3-0 Coventry); mercado: Arsenal -2.5 a 2.57 (~36-39%). Lille 10/10 sin 3+ de derrota, pero con rivales de menor nivel (Ligue 1 media) y 3 amistosos en su muestra.
- UCL jornada 2: Arsenal #15 (1-0 en Nápoles), Lille #22 (2-3 en casa vs Betis). Arsenal perdió 0-3 en Brighton el 19-sep. Under 5.5: máximo en 10 de Arsenal fue 6 (4-2 en Ipswich, League Cup) -> 8/9 es consistente. Alineaciones [ND].

### 13. Rot-Weiss Essen - Fortuna Köln (3. Liga, 17:00Z)
| Pata | Cuota | frec | Veredicto |
|---|---|---|---|
| Hándicap visitante +2.5 | 1.183 | Essen no gana por 3+: 9/10 (4/5 casa); Köln no pierde por 3+: 10/10 (5/5 fuera) | MANTENER (M) |
Justificación:
- [V] Essen #3 (4-3-1, 16:12; casa 3-1-0, 9:3), Köln #12 (2-4-2, 8:8; fuera 2-1-1, 7:5). Essen ganó por 3+ solo 1/10 (6-2 Würzburg); Köln nunca perdió por 3+ (incluye 2 amistosos; competitivos 8/8). H2H: solo amistoso (5-0, jul-2025), sin valor.
- Contra: Essen en casa es el 3.º con ataque que puede desmandarse; la muestra de Köln es de sus rivales de 3. Liga (nivel similar), bien. Alineaciones [ND].

### 14. Birmingham City - Preston North End (Championship, 19:00Z)
| Pata | Cuota | frec | Veredicto |
|---|---|---|---|
| Hándicap visitante +1.5 | 1.459 | Birmingham no gana por 2+: 10/10 (5/5 casa); Preston no pierde por 2+: 7/10 (4/4 fuera) | SUSTITUIR por Preston +2.5 (9/10 y 10/10; cuota 1.135 en el agregador) (B-M) |
Justificación:
- [V] Birmingham #7 (3-5-1) en casa 0-4-0 (7:7: cuatro empates), Preston #24 (1-1-7, 8:16). A favor de +1.5: Birmingham no ganó por 2+ en 10 partidos; el H2H (6, 2022-26) siempre se decidió por 1 gol o menos de diferencia.
- En contra: Preston perdió por 2+ 3 veces de 10 (Wolves 1-3, Bristol 1-3, Everton 0-4 en Copa), es el peor equipo de la tabla; apoyo conservador 0.56 es el más bajo del lote. La +2.5 resuelve la mayor parte del riesgo (Preston solo cayó por 3+ en 1/10).
- Alineaciones [ND].

### 15. Leamington - Redditch United (Southern League Premier Central, 18:45Z)
| Pata | Cuota | frec | Veredicto |
|---|---|---|---|
| Más de 1.5 goles | 1.183 | 10/10 y 9/10 | MANTENER (M) |
Justificación:
- [V] Leamington #16 (13:16 en 10), Redditch #10 (15:14 en 10) -> ~1.5 goles/equipo/partido; discrepancia: la misma liga devuelve otra fila con 7 partidos para ambos. H2H 2023-24: 3-0, 3-0, 2-1 (antiguo).
- Contra: 4-5 de los 10 partidos de cada equipo son eliminatorias (FA Cup/Trophy mal rotuladas) vs rivales de nivel muy distinto; 4 de 10 de Leamington con exactamente 2 goles; el mercado da solo ~0.77. Alineaciones [ND].

### 16. Harju JK Laagri - Nõmme United (Meistriliiga, 15:00Z)
| Pata | Cuota | frec | Veredicto |
|---|---|---|---|
| Gana alguno, sin empate (12) | 1.181 | 9/10 y 10/10 | MANTENER (M-A) |
Justificación:
- [V] Clasificación: Harju #6 (12-2-16, 41:47), Nõmme #9 (9-1-20, 47:72) = 3 empates en 60 partidos-equipo de liga; H2H: los 3 de 2026 decididos (2-1, 1-3, 2-1) y 8 de 8 sin empate en las 8 filas más recientes del H2H (hasta 2022).
- Contra: el mercado da el empate a 3.73 (~25%) bien por encima de este patrón; muestra con 10-0 de copa. Alineaciones [ND]. Cuota ~1.18: rentabilidad baja.

### 17. Orlando Pirates - TS Galaxy (Premier Soccer League, 17:30Z)
| Pata | Cuota | frec | Veredicto |
|---|---|---|---|
| Menos de 5.5 goles | 1.03 | 10/10 y 10/10 | MANTENER (M-A; valor nulo, cuota 1.03) |
| Hándicap visitante +2.5 | 1.41 | Pirates no gana por 3+: 7/10 (4/5 casa); Galaxy no pierde por 3+: 10/10 | SUSTITUIR -> quitar (B) |
Justificación:
- [V] Pirates #2 (6-1-0, 16:1; casa 3-0-0, 6:0), Galaxy #12 (1-3-3, 7:9). Pirates ganó por 3+ en 3 de 10 (3-0, 3-0, 4-0) contra rivales de nivel medio-bajo. Mercado: Pirates 1.16, -2.5 a 2.65 (~35% de goleada).
- Contexto: perdió la final de Copa 0-2 con Sundowns el 10-oct (tercer partido en 10 días) [V]; su impacto es incierto [I]. Etiquetas "Play-offs 1/2" en la muestra son liga regular mal rotulada. Alineaciones [ND].

### 18. Hartlepool - Newcastle Utd U21 (National League Cup - Group Stage, 18:00Z; calendario: 1 fuente)
| Pata | Cuota | frec | Veredicto |
|---|---|---|---|
| Gana alguno, sin empate (12) | 1.101 | 10/10 y 10/10 | DESCARTAR (A) |
Justificación:
- Categoría u23 (excluida por las reglas del sistema), calendario con 1 sola fuente (REQUIERE_VERIFICACION_ADICIONAL), liga 8129 sin clasificación [ND].
- [V] Muestra del U21: mezcla PL2, EFL Trophy, National League Cup y Premier League Cup contra clubes senior, sub-21 y filiales; alineaciones rotativas. Hartlepool: 10 partidos sin empate en National League (poco probable de forma estable). Cuotas 1X2 sospechosas (ver §0). El "12" estimado por el mercado (1.10) concuerda con ~0.82-0.90, pero no hay confianza en el partido.

### 19. Queen's Park - Inverness CT (Scottish Championship, 18:45Z)
| Pata | Cuota | frec | Veredicto |
|---|---|---|---|
| Hándicap local +2.5 | 1.09 | QP no pierde por 3+: 10/10 (5/5 casa); Inverness no gana por 3+: 10/10 (5/5 fuera) | MANTENER (M) |
Justificación:
- [V] Queen's Park #10 (1-1-7, 4:15), Inverness #5 (3-4-2, 11:9). QP perdió por 2 tres veces en casa (0-2) pero nunca por 3+; Inverness nunca ganó por 3+ en 10 (ataque 11 goles en 9).
- Contra: H2H es de 2022-24 (sin peso). QP es el peor ataque (4 goles en 9) y defensa mala: un 0-3 es posible (~10-14% [I]). Alineaciones [ND]. Cuota 1.09.

### 20. National Bank of Egypt - El Gaish (Premier League Egipto, 14:00Z; calendario: 1 fuente)
| Pata | Cuota | frec | Veredicto |
|---|---|---|---|
| Más de 0.5 goles | 1.079 | 10/10 y 10/10 | MANTENER condicionado a segunda fuente de hora (M-B) |
Justificación:
- [V] Clasificación tras 5 jornadas: El Gaish #11 (5:5), NBE #14 (4:7): ataques bajos; 9 de 20 partidos con exactamente 1 gol; el mercado da ~7% al 0-0. Muestra incluye 4-5 partidos de mayo del grupo de descenso del curso anterior (stale).
- Calendario con 1 sola fuente: el sistema exige 2; liga con horarios cambiantes [I]. Cuota 1.079, margen de error muy pequeño. Alineaciones [ND].

### 21. Sariyer - Bodrumspor (TFF 1. Lig, 14:00Z)
| Pata | Cuota | frec | Veredicto |
|---|---|---|---|
| Menos de 4.5 goles | 1.07 | 10/10 y 10/10 | MANTENER (M-A) |
Justificación:
- [V] Sariyer #8 (12:10 en 9), Bodrumspor #15 (7:8 en 9; 5 empates): total máximo 4 en 20 partidos (4-0 Batman); mercado: Over 4.5 a 6.93.
- Contra: las muestras incluyen un partido de mayo-2026 cada uno; liga con datos de calidad media. Alineaciones [ND].

## 2. Ranking de patas más sólidas (de mayor a menor confianza deportiva)
1. Sariyer-Bodrumspor Under 4.5 (M-A): bajo gol de ambos + mercado Over 4.5 a 6.9.
2. Arsenal-Lille Under 5.5 (M-A, cuota 1.06).
3. Simba-Mashujaa "12" (M-A): standings + H2H 6/6 + forma.
4. Harju-Nõmme "12" (M-A): 3 empates en 60 partidos-equipo de liga.
5. Kyoto-Ratchaburi Ratchaburi +2.5 (M-A): Kyoto no marca ni gana por 2+.
6. Bucaramanga 1X (M-A): invicto en Clausura, 5 en casa sin perder.
7. Queen's Park +2.5 (M), Essen-Köln Köln +2.5 (M).
8. Norrköping Under 5.5 (M), Cardiff-Watford Under 4.5 (M), Orlando Pirates Under 5.5 (M-A pero cuota 1.03 sin valor), Gloucester Over 1.5 (M; H2H 4/4).
9. Kyoto +1.5 (M).

## 3. Patas que quitaría / sustituiría
| Pata | Acción | Motivo concreto |
|---|---|---|
| Hartlepool-Newcastle U21 "12" | DESCARTAR (A) | sub-23, calendario 1 fuente, muestra mixta, cuotas 1X2 sospechosas |
| Inter-Brugge +2.5, Arsenal-Lille +2.5, Orlando Pirates +2.5 | SUSTITUIR -> dejar solo Under 5.5 (B) | favoritos en casa ganaron por 3+ en 2 de 4 (Inter y Arsenal en competición) y 3/10 (Pirates); mercado les da 35-39% de goleada; apoyo 0.56-0.61 |
| Birmingham-Preston Preston +1.5 | SUSTITUIR por Preston +2.5 (B-M) | Preston pierde por 2+ en 3/10; la +2.5 sube la seguridad a 19/20 (cuota 1.135) |
| Athletic-MG Over 2.5 tarjetas | SUSTITUIR / quitar (B) | cuota estimada por modelo, sin árbitro, sin regla de liquidación; la línea baja no es verificable |
| Athletic-MG Over 1.5 | MANTENER baja | 18/20 contra mercado 0.675; es la más frágil de las Over |
| NBE-El Gaish Over 0.5 | MANTENER solo con 2.ª fuente de hora | calendario 1 fuente; cuota 1.079 sin margen |
| Fajr-Arak X2 | MANTENER con cuidado | n=7, el mercado favorece a Fajr; confirmar cuota/alineaciones |

## 4. Pendientes / no disponible
- Alineaciones y bajas de TODOS los partidos: [ND] a las 04:00Z (get_lineups vacío; ninguna baja inventada). Revisar 1-2 h antes del inicio, empezando por Kyoto (10:00Z), Fajr y NBE-El Gaish.
- Segunda y tercera fuente (Flashscore, Soccerway, FotMob, etc.): no consultadas -> sin contraste independiente de ningún dato.
- Clasificación de Gloucester/Taunton y de la National League Cup (liga 8129): [ND]. Árbitros: [ND]. Cuotas reales de la casa (sobre todo tarjetas y las DC): pendientes.
- H2H de Kyoto-Ratchaburi, Inter-Brugge, Arsenal-Lille, Pirates-Galaxy, Bucaramanga-Águilas, Sariyer-Bodrumspor, Athletic-Londrina, NBE-El Gaish: no consultados.
