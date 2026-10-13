# Revisión DEPORTIVA de los 3 borradores ×4.0–4.8 («amplio») · jornada 13-oct-2026 (~15:00Z)

Alcance: tickets.md / tickets.json (targets[*].tickets[*].items[*].patas), review_cards.json, inventory.json (match_id), reviews_raw/batch/*.json y, como apoyo, los informes previos de level2 (deportivo, auditor, auditor_ronda2, pares_deportivo) y la caché local de respuestas ya descargadas (`cache/*.body`, solo lectura; NO se consultó API ni fuentes externas). Alineaciones/bajas: [ND] en todos los partidos (nada en cards ni en level2; get_lineups no devolvió datos en el nivel 2). Ninguna cifra de este informe es probabilidad; son frecuencias k/n de muestras de 10 partidos por equipo, local y visitante mezclados, sin ajuste por rival.

## 0. Registro de fuentes
| Fuente | Ficha concreta | Dato buscado | Resultado | Estado | Valor | Discrepancias / alternativa |
|---|---|---|---|---|---|---|
| tickets.md / tickets.json | 3 borradores «amplio» | patas, cuotas, apoyo | 10 patas únicas en 10 partidos (varias repetidas entre borradores) | Consultada y útil | alto | cuotas = mediana de agregador, no ejecutables |
| review_cards.json | 10 match_id (m-02355e736d07, m-91fa22dc9167, m-6844e1f1eb7c, m-3700b5e38591, m-53aa260644d7, m-adc7b810d3d6, m-549c8576741f, m-6ce0c602d26f, m-6c54048fb3b7, m-3c088c296ea9) | historial, forma, GF/GA, k/n, tipo de historial | los 10 son `apifootball_misma_competicion`, n=10/10 salvo Chippenham 9/10 | Consultada y útil | medio (una sola fuente de datos: apifootball) | — |
| inventory.json | por nombre de partido | localizar match_id | los match_id vienen ya en las patas de tickets.json | Consultada y útil | bajo | — |
| reviews_raw/batch/b01,b07,b09,b10,b11 (dep. y cuant.) | filas de esos match_id | correcciones de lote | ver cada pata | Consultada y útil | medio | — |
| level2/deportivo.md, auditor.md, auditor_ronda2.md, pares_deportivo.md | secciones de los partidos | clasificación, H2H, contexto | contexto de Athletic-MG, Bucaramanga, Birmingham, Workington; Durban/Pendikspor/San Carlos/FUS/Chippenham/Blackburn solo por el auditor | Consultada y útil (segunda mano) | medio | — |
| cache/*.body (marcadores ya descargados) | equipos de las 10 fichas | reconstruir marcadores de la muestra para ver «cómo se pierde» | hay filas de Pendikspor, Durban, AmaZulu, Londrina, San Carlos, Inter San Carlos, Bucaramanga, Workington, Whitby, Chippenham, Frome, Birmingham, Preston, Bristol, Blackburn, FUS, Raja; NO hay de Athletic-MG, Van BB ni Águilas Doradas | Acceso parcial | medio-bajo (mezcla copas/U21/temporadas; solo se usó para contrastar los k/n de la ficha) | mismo origen (apifootball): no es verificación independiente |
| Lesiones/alineaciones/árbitro | — | bajas | no disponible | No investigado / no verificable | — | pendiente |

## 1. Hallazgos transversales
1. Concentración de patas: Durban U2.5 y Athletic-MG O1.5 están en los 3 borradores; Bucaramanga O1.5 en D1 y D2; San Carlos U3.5 en D1 y D3; Bristol–Blackburn +1.5 en D2 y D3. Elegir otro borrador no diversifica el riesgo de Durban ni de Athletic-MG.
2. Etiqueta «Play-offs 1/2» (Durban, AmaZulu): es el nombre de liga en la fuente, no una fase. En la caché local la misma etiqueta cubre jornadas 1–7 (ago–sep 2026, rivales distintos cada semana) y 27–30 (may 2026, de una liga de 30 jornadas), también para Orlando Pirates, Stellenbosch, etc. Conclusión (una sola fuente, apifootball): liga regular mal rotulada. El auditor_ronda2 y el lote b10 deportivo pidieron confirmarlo y sigue sin 2.ª fuente. Matiz real: ~3 de los 10 partidos de Durban son de la temporada anterior (may-2026).
3. Etiqueta «Quarter-finals» (Pendikspor): 1 de los 10 es un cuartos de final de promoción (Bodrumspor 2-0, 07-may-2026). Termina con 2 goles, así que no cambia O1.5 (sin él: 8/9), pero resta comparabilidad.
4. «Sesgo del 10/10»: en casi todas las patas la frecuencia observada (90–100 %) supera lo que da el mercado sin margen (63–81 %). Un 10/10 con n=10 es compatible con regresión a la media (lo dejó escrito el deportivo de nivel 2). El apoyo Wilson de cada pata (0.596–0.722) queda en la mayoría POR DEBAJO de la implícita: ninguna pata tiene ventaja demostrada y el apoyo conjunto (0.087 / 0.063 / 0.053) está lejos del equilibrio (0.239 / 0.240 / 0.236).
5. Caso de aviso (Sariyer–Bodrumspor, ×4 caído por 0-3 en 28'): fue una pata «menos de 4.5» con 0 de 20 en cola (card: O3.5 0/10 y 2/10) y aun así una goleada temprana la cargó (veto «Sariyer U4.5»). Un 0/n de cola no protege contra un partido que se abre pronto. Las patas expuestas son las «menos de» y el hándicap +1.5 (ver §5).

## 2. Veredicto por pata
Leyenda: k/n [local, visitante]. «Mkt» = implícita sin margen del ticket.

### P1. Pendikspor – Van BB · Más de 1.5 goles @1.22 (1. Lig, 17:00Z) · DEFENDIBLE
- Hechos: O1.5 9/10 y 10/10; forma local LDLWDLWDDL (GF/GA 1.1/1.9), visitante LLLWDLDDLL (0.9/2.2); O2.5 4/10 y 5/10; BTTS 7/10 y 6/10; 1X2 1.63/3.68/4.71; apoyo 0.659 (mín. equipo 0.596) vs Mkt 0.75. Historial misma competición con 1 cuartos de final (§1.3). Fuente: card m-02355e736d07 + batch b01 dep. (13-oct).
- A favor: Van BB encaja 2.2 y no tuvo ningún partido con menos de 2 goles en 10; Pendikspor concede 1.9; un 1-1 ya cumple. Un partido abierto (el de Sariyer) ayuda a esta pata.
- En contra: forma mala de ambos (7 y 8 no-victorias); el único fallo local fue un 1-0 (Umraniyespor, 05-sep); un 0-0 o 1-0 la pierde. El auditor_ronda2 vio un precio de Over 4.5 anómalo (~25 % de 5+ goles): o el mercado sabe algo (bajas) o es ruido.
- Invalidaría: bajas ofensivas en ambos y ritmo bajo.
- Pendiente: alineaciones, bajas, 2.ª fuente de marcadores de Van BB (sin filas en caché).

### P2. Durban City – AmaZulu · Menos de 2.5 goles @1.46 (1.44–1.5, 7 casas; 17:30Z) · DEFENDIBLE (con salvedades; la menos holgada de las «menos de»)
- Hechos: U2.5 10/10 y 8/10 (O2.5 0/10 y 2/10; O3.5 0/10 y 1/10); Durban GF/GA 0.4/0.6, forma DDLLDDWDLD (6 empates, 1 victoria); AmaZulu 1.1/0.8, DLWWDWLWWW; 1X2 2.24/2.88/3.32; BTTS 2/10 y 3/10. Apoyo 0.606 (mín. 0.49) vs Mkt 0.632: el Wilson no supera la implícita. El mercado da ~37 % a O2.5 frente a 2/20 (cuant. b10: «discrepancia moderada»).
- Contraste con marcadores (caché local, misma fuente): los partidos de liga de Durban que se reconstruyen (1-1, 0-2, 0-0, 0-2, 1-1, 0-0, 0-0, 0-0, 0-1...) terminan todos con 2 goles o menos; los dos Over 2.5 de AmaZulu son un 1-2 en Richards Bay (3 goles) y un 2-5 en Sundowns (7 goles). Los k/n de la ficha cuadran.
- A favor: perfil de bajo gol real, no solo de frecuencia: el local casi no marca (0.4 por partido) y ambos empatan muchísimo.
- En contra: línea 2.5 = margen de un solo gol (basta un 2-1 o un 3-0 temprano). AmaZulu ya encajó 5 y 3 en dos de sus 10 (tipo de cola de Sariyer). ~3 de los 10 de Durban son de la temporada anterior. Fase sin 2.ª fuente (§1.2).
- Invalidaría: gol/expulsión temprana, bajas defensivas de Durban, cambio de entrenador.
- Pendiente: alineaciones, bajas, confirmación de que «Play-offs 1/2» es liga regular.

### P3. Athletic-MG – Londrina · Más de 1.5 goles @1.36 (Serie B, 22:30Z) · DEFENDIBLE (borderline)
- Hechos: O1.5 10/10 y 8/10; O2.5 7/10 y 6/10; forma local LLLWLWDDLL (GF/GA 1.4/1.8), visitante DLDLWWLLLL (1.2/1.3); BTTS 6/10 y 5/10. Apoyo 0.606 (mín. 0.49) vs Mkt 0.679 (18/20 contra 68 %; el deportivo de nivel 2 la llamó «la más frágil de las Over»: p~3 % de un 10/10 con 2.3 goles de media). Athletic #15 (42 pts), Londrina #18 en descenso (28 pts).
- Contraste con marcadores (caché, solo Londrina): sus dos 0-0 fueron en casa (Juventude, Atlético-GO); sus 4 partidos de visitante en la ventana (Avaí 2-1, Vila Nova 2-0, São Bernardo 1-2, Ceará 2-1) tuvieron todos 2+ goles. Sin filas de Athletic-MG: su 10/10 no se contrastó.
- A favor: dos defensas permeables (1.8 y 1.3 encajados); el escenario de pérdida se limita a 0-0/1-0/0-1.
- En contra: Serie B suele ser cerrada; la motivación de descenso de Londrina puede cerrar el partido; el mercado (68 %) descuenta bastante más que la muestra; está en los 3 borradores.
- Invalidaría: Athletic-MG sin sus atacantes; Londrina jugando a no perder.
- Pendiente: alineaciones; marcadores de Athletic-MG.

### P4. San Carlos – Inter San Carlos · Menos de 3.5 goles @1.30 (Costa Rica, 14-oct 02:00Z) · DEFENDIBLE (con salvedades)
- Hechos: U3.5 10/10 y 8/10 (O3.5 0/10 y 2/10; O2.5 2/10 y 2/10); San Carlos GF/GA 1.0/0.7 (DLLWWLWWWW), Inter 1.0/1.3 (LDWWWLWDLD); 1X2 2.25/3.03/3.09; 6 casas. Apoyo 0.606 (mín. 0.49) vs Mkt 0.709. El mercado da ~29 % a 4+ goles frente a 2/20: brecha ~19 pp.
- Contraste con marcadores (caché): los dos Over 3.5 de Inter son derrotas fuera: 0-5 (Alajuelense, 20-sep) y 1-3 (Cartaginés, 25-jul). San Carlos: 0/10. El derbi de la ciudad (09-ago) fue 2-0 para Inter.
- A favor: 2 goles de media por partido en ambos; la línea exige 4+.
- En contra: el único camino de pérdida (Inter hundido ante un favorito) ya le ocurrió dos veces: es el tipo de escenario Sariyer. Parte de la muestra de San Carlos es del Clausura anterior.
- Invalidaría: San Carlos con ritmo alto de local e Inter con bajas defensivas.
- Pendiente: alineaciones (empieza a las 02:00Z del 14: hay tiempo).

### P5. Atlético Bucaramanga – Águilas Doradas · Más de 1.5 goles @1.33 (Primera A, 23:30Z) · DEFENDIBLE
- Hechos: O1.5 9/10 y 9/10; O2.5 5/10 y 4/10; BTTS 8/10 y 6/10; Bucaramanga GF/GA 1.9/1.0 (DDWDDWDWWW), Águilas 1.2/1.5 (DDDDLDLLWD). Apoyo 0.596/0.596 vs Mkt 0.70 (18/20 contra 70 %). Clausura con ~34 % de empates (n=126, auditor); Bucaramanga #4, invicta en 11, 5 empates.
- Contraste con marcadores (caché, solo Bucaramanga): en sus 5 partidos recientes en casa (1-1, 1-1, 2-2, 2-0, 3-1) siempre hubo 2+ goles; su 0-0 fue fuera (Tolima) y el 1-0 en la jornada 1.
- A favor: el local mete casi 2 por partido; los empates 1-1 o 2-2 (muy frecuentes) cumplen.
- En contra: el 0-0 o el 1-0 son la salida natural de dos equipos que empatan mucho; el visitante lleva 1 victoria en 10. El nivel 2 menciona una «fase cuadrangular»/calendario que las cards no confirman (muestran jornadas 1–13 de Clausura): motivación/rotación sin contrastar.
- Invalidaría: rotaciones, partido trabado y gol tardío.
- Pendiente: alineaciones; calendario/fase.

### P6. Birmingham City – Preston North End · Menos de 4.5 goles @1.14 (Championship, 19:00Z) · DEFENDIBLE (la más parecida a Sariyer; paga poco)
- Hechos: U4.5 10/10 y 10/10; O3.5 3/10 y 4/10; BTTS 8/10 y 7/10; O2.5 6/10 y 7/10; Birmingham GF/GA 1.4/1.2 (en casa 0V-4E-0D, 7:7, según nivel 2), Preston 0.9/1.9 (#24, 1V-1E-7D). 1X2 1.59/4.08/5.23. Apoyo 0.722 (el más alto) vs Mkt 0.814 (el mercado da ~18 % a 5+; observado 0/20). BTTS 15/20 contra 54 % de mercado (b07 cuant.).
- A favor: 5+ goles exige un partido muy abierto; no ocurrió en 20 partidos de los dos.
- En contra: perfil «local favorito contra el peor de la tabla» como Sariyer: una goleada temprana (0-3 a la media hora) deja un gol de margen; Birmingham en casa da 3.5 goles de media. Paga 1.14 por un riesgo de cola que el mercado fija en ~18 %.
- Invalidaría: Birmingham con once muy ofensivo, Preston con bajas defensivas, gol temprano.
- Pendiente: alineaciones y bajas.

### P7. Workington – Whitby Town · Más de 1.5 goles @1.135 (NPL Premier, 18:45Z) · DEFENDIBLE (cuota frágil)
- Hechos: O1.5 10/10 y 9/10; O2.5 9/10 y 7/10; Workington GF/GA 2.1/1.7 (LWWWWWWDDL), Whitby 1.5/2.9 (WLLLWLWLLD). Solo 4 casas (1.11–1.2). Apoyo 0.659 (mín. 0.596) vs Mkt 0.803. Tarjetas 0/3 y 0/1: ceros sospechosos (b09), irrelevantes para goles pero señal de cobertura pobre (nivel 7).
- Contraste con marcadores (caché, solo liga): Workington, 2+ goles totales en todos los partidos reconstruidos; Whitby, único 0-0 en Bamber Bridge (10-oct) y 29 goles encajados en 10.
- A favor: la defensa de Whitby (2.9) y el ataque de Workington dan partido abierto; la pata con menor riesgo de «partido cerrado» de las Over.
- En contra: H2H (6, 2023-26) con solo 3 O2.5 y un 0-0 en enero-2026; liga semiprofesional con alineaciones inestables; solo 4 casas (el auditor_ronda2 lo marcó). Workington cayó 0-3 el 10-oct.
- Invalidaría: ausencia de delanteros de Workington; rotación.
- Pendiente: cuota con más casas; alineaciones.

### P8. Bristol City – Blackburn Rovers · Hándicap visitante +1.5 @1.22 (1.20–1.36; Championship, 18:45Z) · DÉBIL
- Hechos: Blackburn no pierde por 2+: 10/10; Bristol no gana por 2+: 8/10 (frec [0.8, 1.0]); forma Bristol WLDWWWLLWD (1.4/1.3), Blackburn LDWLDLLWDW (1.4/1.4); 1X2 2.05/3.38/3.53; BTTS 6/10 y 8/10; O2.5 5/10 y 8/10. Apoyo 0.606 (mín. 0.49) vs Mkt 0.743. Rango de cuotas amplio (1.20–1.36). b07: sin correcciones.
- Contraste con marcadores (caché): las derrotas recientes de Blackburn en liga fueron por un gol (1-2 QPR, 1-2 Sheffield Utd, 1-2 Preston).
- A favor: equipos parejos (local apenas favorito a 2.05); Blackburn pierde de poco.
- En contra: la frecuencia solo mejora ~6–13 pp la implícita (0.8/1.0 vs 0.74); Wilson de Bristol 0.49; sin ventaja informativa (misma lógica por la que se vetaron RWE +1.5 y Kaizer +1.5). Los partidos de Blackburn son abiertos (BTTS 8/10, O2.5 8/10): sube la varianza de un 2-0/3-1 local. Es la pata más sensible a un «0-3 en la media hora»: con 1.5 de colchón cae con una goleada temprana. Está en D2 y D3.
- Invalidaría: bajas defensivas de Blackburn, ventaja ofensiva clara de Bristol, gol temprano local.
- Pendiente: alineaciones; racha local de Bristol por separado (la ficha no separa casa/fuera); cuota real de la casa.

### P9. FUS Rabat – Raja Casablanca · Menos de 3.5 goles @1.135 (Botola Pro, 20:00Z) · DEFENDIBLE
- Hechos: U3.5 10/10 y 9/10 (O3.5 0/10 y 1/10; O2.5 3/10 y 3/10); FUS GF/GA 0.7/1.2 (DWLLWDLLLD), Raja 1.4/1.0 (LDWWLDWWWD); BTTS 5/10 y 5/10; 1X2 3.16/2.92/2.25 (visitante favorito). Apoyo 0.659 (mín. 0.596) vs Mkt 0.806. b07 cuant. y dep.: sin anomalías.
- Contraste con marcadores (caché): el único Over 3.5 de Raja es un 3-4 en Zemamra (jun-2026). FUS: 0-1 y 0-0 en las dos últimas semanas.
- A favor: liga de pocos goles; ninguno supera 1.4 GF por partido.
- En contra: la muestra mezcla el final de la temporada anterior (jun-jul) con solo 3 partidos de la nueva; el mercado da ~19 % a 4+ goles frente a 1/20; el visitante favorito puede abrir el marcador pronto.
- Invalidaría: cambios de plantilla/entrenador; expulsión temprana.
- Pendiente: alineaciones; separar jornadas de la nueva temporada.

### P10. Chippenham Town – Frome Town · Más de 1.5 goles @1.185 (Southern League Premier South, 18:45Z) · DÉBIL
- Hechos: O1.5 9/9 y 8/10 (n=9 el local); O2.5 5/9 y 6/10; Chippenham GF/GA 1.0/2.0 (LDWLLWLLD), Frome 1.6/1.4 (WLLWWDLDDD); 4 casas (1.17–1.22); apoyo 0.596 (mín. 0.49) vs Mkt 0.769. Tarjetas 0/4 y 0/3: ceros sospechosos, descartados (b11 dep. y cuant.).
- Contraste con marcadores (caché, solo liga): los partidos de Chippenham reconstruidos tuvieron todos 2+ goles; los dos fallos de Frome son 1-0 (Bath y Havant).
- A favor: defensas flojas (2.0 y 1.4 encajados) y empates con goles (2-2, 3-3).
- En contra: n=9 en el local; nivel 7 con cobertura pobre y solo 4 casas (la combinación de datos más débil de los tres borradores); ataque de Chippenham de 1.0; Frome cierra 1-0 de vez en cuando. Solo en D3; el auditor_ronda2 ya la señaló (A-D5).
- Invalidaría: ausencias en ataque; cuota que cambie al contrastar con más casas.
- Pendiente: alineaciones; cuota con ≥5 casas; 2.ª fuente de marcadores.

## 3. Resumen de patas
| Pata | Veredicto | Motivo corto |
|---|---|---|
| Pendikspor O1.5 | DEFENDIBLE | defensas abiertas; fallo = 0-0/1-0 |
| Durban U2.5 | DEFENDIBLE (salvedades) | local 0.4 GF; margen de un gol; fase sin 2.ª fuente; en los 3 borradores |
| Athletic-MG O1.5 | DEFENDIBLE (borderline) | 18/20 contra 68 % de mercado; Londrina fuera siempre 2+; en los 3 borradores |
| San Carlos U3.5 | DEFENDIBLE (salvedades) | cola = Inter hundido fuera (0-5, 1-3); mercado 29 % a 4+ |
| Bucaramanga O1.5 | DEFENDIBLE | local siempre 2+ goles en casa en la ventana; fallo = 0-0/1-0 |
| Birmingham U4.5 | DEFENDIBLE (paga poco) | favorito contra el último; cola de goleada abierta |
| Workington O1.5 | DEFENDIBLE (4 casas) | Whitby encaja 2.9; precio frágil |
| Bristol–Blackburn +1.5 | DÉBIL | frecuencia ≈ mercado; cae con goleada local |
| FUS Rabat U3.5 | DEFENDIBLE | liga de pocos goles; mezcla de temporadas |
| Chippenham O1.5 | DÉBIL | n=9, nivel 7, 4 casas, ceros sospechosos |

Ninguna pata queda NO RESPALDADA: todas tienen perfil de goles coherente con la línea y misma competición. Ninguna tiene ventaja demostrada sobre el mercado.

## 4. Veredicto por borrador
| Borrador | Cuota | Patas | Apoyo conjunto / equilibrio | Veredicto |
|---|---|---|---|---|
| D1 (Pendikspor O1.5, Durban U2.5, Athletic O1.5, San Carlos U3.5, Bucaramanga O1.5) | ×4.188 | 5 | 0.087 / 0.239 | DEFENDIBLE con salvedades (el mejor: ninguna pata DÉBIL) |
| D2 (Birmingham U4.5, Workington O1.5, Durban U2.5, Athletic O1.5, Blackburn +1.5, Bucaramanga O1.5) | ×4.169 | 6 | 0.063 / 0.240 | DÉBIL (una pata DÉBIL; Workington con 4 casas) |
| D3 (FUS U3.5, Durban U2.5, Athletic O1.5, San Carlos U3.5, Blackburn +1.5, Chippenham O1.5) | ×4.236 | 6 | 0.053 / 0.236 | DÉBIL (dos patas DÉBILES; el menor apoyo conjunto) |

Sin contradicciones internas ni pares del mismo partido en ningún borrador.

## 5. Caso de aviso: ¿alguna pata con perfil Sariyer–Bodrumspor?
Sariyer U4.5 cayó con 0 de 20 en cola; un 0-3 en 28' la rompió. Lección: una pata «menos de» o un hándicap con colchón corto cae cuando el favorito local abre pronto. Patas expuestas, de más a menos:
1. Bristol–Blackburn +1.5 (cae con 2-0/3-1 local; partidos abiertos).
2. Birmingham U4.5 (favorito 1.59 en casa contra el último; 3.5 goles de media en casa).
3. Durban U2.5 (colchón de un gol; un 0-3 temprano la mata, aunque el perfil de bajo gol es real).
4. San Carlos U3.5 (Inter ya cayó 0-5 y 1-3 ante favoritos).
5. FUS U3.5.
Las Over (Pendikspor, Athletic-MG, Bucaramanga, Workington, Chippenham) no sufren por una goleada temprana: su escenario de pérdida es el opuesto, un partido cerrado 0-0/1-0.

## 6. Recomendación de vetos
1. Vetar D3 (dos patas DÉBILES, apoyo conjunto más bajo 0.053). Sin Blackburn ni Chippenham quedan 4 patas ≈×2.93, fuera del rango ×4.0–4.8.
2. Vetar la pata Bristol–Blackburn +1.5 en cualquier borrador.
3. Vetar la pata Chippenham O1.5.
4. D2 solo sería aceptable sustituyendo Blackburn +1.5; si no, descartarlo.
5. D1 es el único sostenible, con salvedades: ninguna pata con ventaja demostrada (0.087 contra 0.239), cuotas no ejecutables, alineaciones sin datos. Durban U2.5 y Athletic-MG O1.5 son puntos únicos de fallo de los tres borradores.

## 7. Datos pendientes
- Alineaciones y bajas de los 10 partidos ([ND]); sobre todo Birmingham, Bristol/Blackburn, Athletic-MG, Durban y San Carlos/Inter (02:00Z del 14).
- 2.ª fuente que confirme «Play-offs 1/2» de Durban/AmaZulu como liga regular.
- Marcadores de Athletic-MG, Van BB y Águilas Doradas (sin filas en la caché local).
- Cuota real de la casa por pata (Blackburn 1.20–1.36; Workington y Chippenham con 4 casas).
- Calendario de Bucaramanga (fase) y racha local de Bristol.
- Comprobar hora y estado en vivo antes de apostar.
