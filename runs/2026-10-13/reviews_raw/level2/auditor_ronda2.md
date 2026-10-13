# Auditor adversarial - ronda 2 (tickets regenerados 2026-10-13)
Fuentes revisadas: tickets.md/json, review_cards.json, matrix.json (api_prices), reviews_raw/batch/*.json (corrections por match_id). Sin fuentes externas ni API. No pude comprobar la hora actual: los partidos de 10:00Z (Kyoto, Pohang), 12:15Z, 14:00Z (Sariyer) y 15:00Z (Harju) pueden estar ya jugados o en juego.

## Hallazgos transversales
T1 (alto) El "apoyo" de un ticket es el PROMEDIO aritmetico de los Wilson inferiores de cada equipo (verificado: (0.722+0.49)/2=0.606; (0.722+0.596)/2=0.659; (0.397+0.722)/2=0.56). Un 10/10 (techo 0.722) tapa al equipo flojo. Con el peor equipo solo: 8/10 -> 0.49, 7/10 -> 0.397, ambos bajo el piso 0.55 del perfil amplio. Casi todas las patas 0.606 y la 0.56 de Kaizer no pasarian el piso por equipo.
T2 (alto) En TODO borrador el apoyo conjunto (0.05-0.71) queda bajo el punto de equilibrio 1/cuota (0.79 en x1.267; ~0.23 en x4.3). Solo EV descriptivo; en las patas de seguridad el apoyo (0.722) tampoco supera la implicita sin margen (0.75-0.86).
T3 (alto) Patas "12" (sin empate): 0 empates en Al Sadd/Al Hilal (20 partidos), Bury (0/10; Needham 2), Sabah (0/8; Slavia 2), Leipzig (0/10; PSV 2), Cong An/Kashima (1+1). Total 8 empates en 98 partidos (8%) frente a ~22-30% de empate en el 1X2 (cuota X: Al Sadd 4.27, Bury 3.36, Sabah 3.71, Leipzig 4.47, Cong An 4.49). Las muestras mezclan copas/eliminatorias (Emir Cup F/SF/QF, King's Cup, DFB Pokal, Qualifying) donde el empate podria estar registrado como victoria: HIPOTESIS no verificada (dato que resuelve: marcador a 90' vs resultado final por partido). Seleccion por "pocos empates" = sesgo del ganador.
T4 (medio) Concentracion: Kyoto +1.5 esta en 4 de 5 borradores amplios (D1,D2,D3,D5); RWE, Kaizer, Athletic-MG y Pohang en 2 cada uno. Un fallo de Kyoto hunde 4 de 5 opciones. Es la pata con MENOR implicita (0.559) y el unico EV positivo del ranking atractivo (+0.107): maximo sobre ~3200 patas, tipico sobreajuste. Mercado: Kyoto -1.5 paga 2.12 (~47% gana por 2+) pese a 0.9 GF del Kyoto en su historial; el mercado sabe algo (alineacion, rotacion) que no tenemos.
T5 (medio) Cuotas: mediana de 4-8 casas por un agregador; patas con solo 4 casas: Workington, Buriram, Kaizer, Villarreal, Chippenham (5 en Harju). La cabecera dice ">=3 casas"; el brief dice >=4. Los tops incluyen patas de 3 casas (Simba, Kyoto +2.5, Cheltenham), Lehota con calendario de 1 fuente y Cheltenham-Tottenham U21 (u23): contradicen las reglas de la cabecera.
T6 (medio) Muestras: "historial propio" (copas + liga + continental) en AFC/UEFA sin ajustar por rival; incluye pretemporada (Como Cup/Emirates Cup en Villarreal y Arsenal) pese a "sin amistosos" (b11 dep).
T7 (bajo) RESOLUCION-director.md (veredicto "no hay picks", exit 4) describe la matriz previa a la API; no respalda ni contradice estos tickets. No usarlo.

## Perfil SEGURIDAD (mejor a peor)
### S-D2 Bucaramanga - Aguilas Doradas, 1X @1.25 (8 casas, 1.16-1.27) -> MAS DEFENDIBLE (salvedades menores)
Principal (medio): frecuencias de equipo mezclan casa/fuera; el dato relevante (Bucaramanga como local) no esta separado. 10/10 sin derrota del local y 1 victoria en 10 del visitante (DDDDLDLLWD) cuadran con el mercado (visitante gana 3.76, ~26%).
Secundarias: min 1.16 de una casa es atipico (la mediana vale); 23:30Z sin once ni bajas. Lote: b07 cuant y dep sin correcciones relevantes (solo nota de Over 1.5, ajena a la pata). Resolveria: split local/visitante y alineaciones.
### S-D3 Pendikspor - Van BB, Mas de 1.5 @1.22 (7 casas) -> ACEPTABLE CON SALVEDADES
Principal (medio): GF 1.1 y 0.9, forma LDLWDLWDDL / LLLWDLDDLL; 19/20 en Over 1.5 contra 75% implicito (brecha ~20 pp); Over 2.5 de mercado 1.79 vs 9/20 historico. b01 dep: historial mixto (incluye Quarter-finals de 1. Lig). Un 1-0/0-0 lo pierde (~25%). Resolveria: marcadores de los 10 sin fase eliminatoria.
### S-D1 Cardiff - Watford, Menos de 4.5 @1.25 (7 casas, 1.20-1.27) -> ACEPTABLE CON SALVEDADES (peor de los simples)
Principal (alto): precio anomalo. Over 4.5 paga 3.77-3.80 (~25% de 5+ goles) frente a Birmingham 5.15, Bristol 6.2, Sariyer 6.9; la escalera (Over 2.5 1.49, Over 3.5 2.23) implica ~3.3 goles esperados, mientras los historiales dan 2.8 y 2.5 GF+GA (Over 3.5: 3/9 y 2/10). O el mercado sabe algo (bajas defensivas) o hay ruido; la pata se eligio por pagar justo 1.25 (el objetivo): seleccion adversa.
Secundarias: local n=9; sin bajas/alineaciones. Lote: b07 cuant y dep limpios (no vieron el precio atipico). Resolveria: bajas de ambos; precio en otra fuente.
### S-D5 Birmingham - Preston U4.5 @1.14 + Harju - Nomme U5.5 @1.10 -> ACEPTABLE CON SALVEDADES (flojo)
Principal (alto): apoyo conjunto 0.521 vs equilibrio ~0.80; cada pata exige 87.7% y 90.9% de acierto frente a implicitas 81.4% y 82.3%. Birmingham: favorito 1.59 contra Preston GA 1.9 (BTTS 15/20; b07 cuant: 75% vs 54% de mercado). Harju: 5 casas; visitante encaja 2.6 y Over 2.5 en 8/10; Over 3.5 de mercado ~49% vs 2/10 local (b09 cuant: sin ventaja demostrada); Over 5.5 paga 4.89 (rango 3.75-5.5). Resolveria: mas casas para el 5.5; alineaciones.
### S-D4 Al Sadd - Al Hilal "12" @1.19 + Sariyer - Bodrumspor U4.5 @1.065 -> DESACONSEJADO
Principal (alto): "12" sin empates en 20 partidos con Emir Cup y King's Cup en la muestra (T3); b06 dep: historial mixto liga/copa/continental, tarjetas visitante n=9; b06 cuant: Over 1.5/BTTS inflados por rivales menores. Segunda pata: 1.065 paga 6.5% por un riesgo de ~14% segun mercado (equilibrio 93.9% vs implicita 86.4%); b01 dep: el visitante incluye una semifinal de playoff. Alternativa: S-D2.
Orden seguridad: D2 > D3 > D1 > D5 > D4.

## Perfil AMPLIO (mejor a peor)
Ninguno es "defendible" (conjunto 0.05-0.15 contra equilibrio >=0.21); el orden es por numero y gravedad de patas problematicas.
### A-D2 x4.484 (Kyoto +1.5, FUS U3.5, Athletic-MG O1.5, Petrojet O1.5, San Carlos U3.5) -> ACEPTABLE CON SALVEDADES (el mejor)
Principal (alto): Petrojet O1.5 @1.33: b08 cuant "BTTS 9/10 y Over 2.5 8/10 vs mercado ~51%/45%, discrepancia >30 pp, no usar frecuencia como probabilidad"; b08 dep: Premier League + Relegation Group y tarjetas 1/10 vs 9/10 "verificar". Sin esa pata el ticket baja a ~x3.37, fuera de rango.
Secundarias: FUS, Athletic-MG, San Carlos con lotes b07/b10 limpios. Kyoto: T4 y b06 (Copa en historial, corners 10/10 identicos 8.5/9.5). Athletic-MG: forma LLLW../DLDL.. con 18/20 Over 1.5 vs 68% implicito. San Carlos 02:00Z.
### A-D1 x4.343 (Kyoto, Workington O1.5, Durban U2.5, RWE +1.5) -> ACEPTABLE CON SALVEDADES
Principal (alto): Durban (y Kaizer) con etiqueta "Play-offs 1/2" en TODO el historial (b10 dep pidio confirmar fase); local 0.4 GF, 18/20 Under 2.5 vs 63% implicito. Workington O1.5: 4 casas, nivel 7, b09 cuant 19/20 vs 80% implicito, ceros sospechosos. RWE +1.5: visitante n=8 (b01 dep); por equipo 0.556/0.529; cuota 1.56 (1.43-1.6).
Resolveria: fase de Durban; mas casas para Workington.
### A-D3 x4.199 (Kyoto, Bury 12, Buriram +1.5, Sabah 12, Kaizer +1.5) -> ACEPTABLE CON SALVEDADES (al borde de DESACONSEJADO)
Principal (alto): tres patas de 4 casas o n=8 y dos "12" con 0 empates (T3). Kaizer +1.5: el local gana por 2+ en 3/10 (Wilson propio 0.397, oculto en el promedio 0.56); mercado ~29% a Kaizer por 2+: la frecuencia COINCIDE con el mercado, sin apoyo. Sabah n=8 con Qualifying y pretemporada (b11). Buriram: ASEAN/FA Cup, 4 casas (b06).
### A-D5 x4.16 (Kyoto, Pohang O1.5, Villarreal +1.5, Leipzig 12, Chippenham O1.5, Cong An 12) -> DESACONSEJADO
Principal (alto): 6 patas, apoyo conjunto 0.052; Pohang vetable (abajo); Villarreal con amistosos en la muestra y 4 casas (b11 dep); dos "12" (T3); Chippenham 4 casas con tarjetas 0/4 sospechosas (b11); Cong An con 4+ partidos de copa/ASEAN (b06).
### A-D4 x4.481/4.257 (Athletic-MG O1.5, Pohang O1.5, RWE +1.5, Bristol U4.5 + Blackburn +1.5, Kaizer +1.5) -> DESACONSEJADO (peor)
Principal (alto): 3 de 6 patas con defecto verificable (Pohang, Kaizer, RWE n=8) y la justificacion "las patas se refuerzan" es erronea: 0.56 = (0.397+0.722)/2 con conjunto local 7/10 y visitante 10/10; el conjunto del local (7/10) es MENOR que cada pata sola (9/10 y 8/10), y compararlo con 0.399 (producto de dos Wilson) no es una prueba de dependencia. La casa recalcula la combinada (1.342 media) y Blackburn +1.5 tiene rango 1.20-1.36. Implicita conjunta mas baja del perfil (0.137).
Orden amplio: D2 > D1 > D3 > D5 > D4.

## Patas a vetar (motivo)
1. Pohang-Johor O1.5 (A-D4, A-D5): misma muestra inflada (Johor 5.4 GF, 10/10 Over 1.5 vs rivales de otra liga) por la que ya se veto el X2; sin Johor el equipo local da 8/10 -> 0.49 < piso 0.55 (b06 cuant+dep). Incoherente vetar una y mantener la otra.
2. Kaizer Chiefs +1.5 (A-D3, A-D4): Wilson propio 0.397; frecuencia = mercado; 4 casas; etiqueta Play-offs.
3. Petrojet O1.5 (A-D2): b08 cuant+dep (discrepancia >30 pp, Relegation Group).
4. Patas "12" con 0 empates (Al Sadd, Bury, Sabah, Leipzig, Cong An): vetar hasta verificar marcadores a 90' (T3). Prioridad: Al Sadd.
5. Sariyer U4.5 @1.065 (S-D4): sin retorno y playoff en la muestra.
6. Villarreal +1.5 (A-D5): amistosos en la muestra + 4 casas.
7. No vetar pero acotar: Kyoto +1.5 a UN borrador y comprobar que no haya empezado; Cardiff U4.5 solo tras revisar bajas.
8. Tabla corners/tarjetas: ninguna utilizable (todas "1.11 aprox" derivadas de la propia frecuencia; sin cuota, arbitro ni regla A+R). Vetar ademas por categoria prohibida: Artis Brno B-Brno B y Montana-Ludogorets II (reserve), Gillingham-Brighton U21 y Boston-Southampton U21 (u23); Petrojet (tarjetas 1/10 vs 9/10); Arsenal-Lille (amistosos en la muestra); Havelse (corners n=8). Misma logica que los vetos ya aplicados a Hartlepool U21 y Athletic-MG tarjetas.

## Estado de objeciones para cierre
- T1, T2: riesgo aceptado solo si el ticket muestra Wilson por equipo.
- T3: sin resolver (marcadores a 90' pendientes). T4: sin resolver (limitar Kyoto).
- Cardiff precio anomalo, fase de Durban/Kaizer, Petrojet: pendientes de dato (bajas; fase; marcadores).
- Motivo de descarte propuesto: S-D4, A-D4, A-D5.
