# Revision deportiva por niveles (x1.2, x3, x4) - jornada 14-oct-2026 (hora Caracas, UTC-4)

Analista deportivo, Nivel 2. Informe de riesgos; la decision es del usuario.

## 0. Como leer esto
- Fuentes de los numeros: `matrix.json` (apifootball, ultimos 10 de cada equipo, n=10 salvo indicacion), `rotation.json` (heuristica del proyecto: descanso + cambios medios de los ultimos 4 partidos), `tickets.json`, y consultas nuevas a apifootball (get_events de los 26 partidos y get_standings de 10 ligas, consultadas el 14-oct-2026).
- Todo lo de "forma" viene de UN solo proveedor (apifootball): estado "Una sola fuente". Los corners ademas no tienen cuota verificada (cuota estimada por el modelo).
- Cuotas = medias de mercado de `tickets.json`, no ejecutables en una casa concreta.
- "Al borde" = partidos de la muestra cuyo total quedo justo en el limite (un gol de fallar la pata).
- Horarios (get_events, Caracas): MLS 19:30-22:30; Noruega 1.Div 09:00-13:00; Turquia 07:30/10:00; Alemania 3.Liga 13:00; Chequia 12:00; QPR 14:45; Santa Fe 19:30; Sarmiento 18:00; USL 19:00. El campo `fecha` de rotation.json esta en UTC (por eso Dallas, St. Louis, Chicago y LAG aparecen como 15-oct; en Caracas son del 14).
- Bajas/alineaciones: `missing_players` vacio en los 26 partidos y once confirmado solo en Sporting JAX-Birmingham (11 jugadores listados, origen no verificado como once oficial). Transfermarkt, FotMob, BetExplorer, Understat y SoccerStats NO se consultaron (excluidos por politica de fuentes en este run; ver matrix.json -> attempts). Dos busquedas web (calendario MLS, LAFC-Austin) devolvieron solo paginas de baja calidad o de otras temporadas: Consultada con datos insuficientes. Por tanto las bajas son un dato PENDIENTE en todas las patas.
- Fase MLS (standings apifootball, 28 PJ por equipo, tablas del 13/14-oct): corte de playoff 9.o por conferencia (9.o ~36 pts). Este: Cincinnati 9.o 36 pts; NYC 33, Toronto 32, DC 30, Columbus 29, Atlanta 27, Montreal 24. Oeste: Galaxy 9.o 36, Portland 33, Austin 31. La fecha de cierre de la fase regular NO esta verificada.
- Estadistico ruido recurrente: la muestra de 10 mezcla local y visitante y rivales de distinto nivel; varias muestras incluyen partidos de mayo (temporada anterior): QPR/Derby (2-may), Bohemians/Mlada Boleslav (2/23-may), Umraniyespor/Boluspor (1/2-may), Batman/Istanbulspor (1-may), Al Raed/Jeddah (abril-mayo), Waldhof/Ingolstadt/Wehen/Aachen (9/16-may).

## 1. Resumen de solidez
| Nivel | Pata | Solidez |
|---|---|---|
| x1.2 | Cincinnati-NE O1.5 | ALTA |
| x1.2 | St. Louis-Vancouver O1.5 | ALTA |
| x1.2 | Chicago-Philadelphia O1.5 | ALTA |
| x1.2 | Stromen-Asane O1.5 | ALTA |
| x1.2 | Santa Fe-Jaguares (Jag +2.5) | MEDIA |
| x3 | Moss-Egersund O1.5 | ALTA |
| x3 | QPR-Derby U4.5 | ALTA |
| x3 | LA Galaxy-Portland (Por +1.5) | MEDIA |
| x3 | Bryne-Raufoss U4.5 | BAJA |
| x3 | Columbus-Charlotte (Cha +1.5) | ALTA |
| x3 | Dallas-Seattle (Sea +1.5) | ALTA |
| x3 | Sarmiento-River O0.5 | ALTA |
| x3 | Inter Miami-NYC U5.5 + NYC +1.5 (mismo partido) | MEDIA (U5.5 ALTA; +1.5 MEDIA) |
| x4 | Toronto-Orlando O1.5 | ALTA |
| x4 | Sporting JAX-Birmingham U5.5 | BAJA |
| x4 | DC United-NY Red Bulls U5.5 | ALTA |
| x4 | Bohemians-Mlada Boleslav O1.5 | BAJA |
| x4 | Bohemians-Mlada Boleslav U4.5 | MEDIA |
| x4 | Hartford-Charleston O1.5 | MEDIA |
| x4 | LAFC-Austin (Aus +1.5) | BAJA |
| x4 | Hodd-Ranheim O2.5 | ALTA |
| x4 | Montreal-Atlanta U4.5 | MEDIA |
| x4 | Batman-Istanbulspor O1.5 | MEDIA |
| x4 | Umraniyespor-Boluspor U4.5 | ALTA |
| x4 | Waldhof-Ingolstadt U14.5 corners | MEDIA |
| x4 | Wehen-Aachen U12.5 corners | MEDIA |
| x4 | Al Raed-Jeddah U4.5 | MEDIA |

Contexto de tickets.json (informativo, sin juicio de apostar o no): p_perdida_mercado x1.2 = 0.29/0.295/0.268 (b1/b2/b3); x3 = 0.756/0.763; x4 = 0.851/0.849/0.873. Las patas MEDIA/BAJA son las que mas aportan a esa perdida.

## 2. x1.2 (seguridad)
Borrador 1: Cincinnati-NE O1.5 (1.10) + St. Louis-Vancouver O1.5 (1.135). Borrador 2: Chicago-Philadelphia O1.5 (1.115) + Stromen-Asane O1.5 (1.11). Borrador 3: Santa Fe-Jaguares Jag +2.5 (1.25).

**Cincinnati-NE O1.5 - ALTA.** Muestra: Cincinnati 10/10 y NE 10/10 con >=2 goles (3/20 al borde con exactamente 2). Cincinnati en casa: 4,83 goles totales por PJ (n=12, tabla); NE fuera: 3,00 (n=14). Pierde en 0-0 o 1-0/0-1: caso de dos equipos que rotan y se guardan en miercoles (Cincinnati rota 4,33 cambios con 4 dias; NE 2,0) y un partido trabado en un Cincinnati que esta 9.o (36 pts) y no puede arriesgar. Ruido: la media de 4,0 goles del local arrastran partidos de 6 goles; el dato util es la mediana, no la media. Faltan bajas.

**St. Louis-Vancouver O1.5 - ALTA.** Fallo de la muestra: 1/20 (Vancouver 0-1 en casa, 20-ago). Choque entre 2.o (50 pts) y 1.o (51 pts) del Oeste: el escenario de perdida es un 0-0/1-0 cauto de dos lideres que no quieren perder con 6 partidos por jugar, con St. Louis y Vancouver a 4 dias de descanso y Vancouver rotando 3,33. Local en casa 3,79 g/PJ (n=14); Vancouver fuera 3,23 (n=13). Ruido: el 6-2 y el 8-goles de St. Louis inflan la media.

**Chicago-Philadelphia O1.5 - ALTA.** Muestra 19/20 (fallo: Chicago 1-0 en Filadelfia). 4/20 al borde. Chicago en casa 3,07 g/PJ; Philadelphia fuera 4,43 (31-31 en 14). Ambos "bajo" en rotacion (5 dias). Perdida: 1-0 con ambos pendientes de defensa; es el menos probable porque Philadelphia en 14 salidas concede 31.

**Stromen-Asane O1.5 - ALTA.** 19/20 (Asane 0-1 el 3-oct). Asane (15.o, zona de descenso, 22 pts) fuera: 11-28 en 12 PJ (3,25 g/PJ). Descanso corto 3 dias en ambos (domingo 11-oct) y juego a las 09:00 Caracas (15:00 Noruega) (superficie y clima no verificados). Perdida: 1-0 de Stromen que se cierra con un Asane que ya no tiene nada que perder y rota (3,33 cambios). Ruido: Stromen en casa 4,3 de media sale de dos partidos de 7 y 6 goles.

**Santa Fe-Jaguares Jag +2.5 - MEDIA.** Santa Fe 3.o (57 pts, 35 PJ, clasificado a Sudamericana por tabla), Jaguares 19.o (28 pts, 31 PJ). Muestra: Santa Fe nunca gano por 3+ en casa (margenes en sus 6 partidos en casa: 2,0,1,0,1,-1), Jaguares nunca perdio por 3+ (0/10, peor derrota -2). Escenario de perdida: Santa Fe gana 3-0/3-1/4-1, con Jaguares jugando con 3 dias de descanso y rotacion alta (4,0 cambios segun rotation.json, descanso corto), y en Bogota (altitud 2.600 m, factor de conocimiento general, no verificado para esta fecha) el visitante se agota al final. El 0/10 es una muestra de equipos con rivales de nivel muy distinto, no ajustada al rival; el 19.o puesto y 55 goles en contra en 31 PJ (1,77/PJ) dicen que el visitante concede mucho. Faltan bajas.

## 3. x3

**Moss-Egersund O1.5 - ALTA.** 20/20 con >=2, 5/20 con exactamente 2. Moss en casa 3,58 g/PJ, Egersund fuera 4,17 (17-33 en 12). Perdida: 1-0 en una jornada con tres juegos noruegos a las 13:00 Caracas y Moss (11.o, 28 pts); Moss y Egersund no estan en rotation.json, asi que descanso y rotacion son dato pendiente. Ruido: el 5 y 6 goles de Moss no se repiten por sistema.

**QPR-Derby U4.5 - ALTA.** 20/20, 3/20 al borde (4 goles). Derby 23.o (6 pts, 8-15 en 9 PJ), partido de Championship a las 14:45. Los dos equipos puntuan poco (media de goles totales por partido 2,2 (QPR) y 2,6 (Derby) en la muestra). Perdida: 5+ goles, lo que exige que Derby (el peor del grupo) abra el juego con QPR rotando 4,33 cambios y con "copa en <=4 dias" (heuristica de rotation.json) y se produzca un 4-1/3-2; es un escenario de cola. Ruido: ambas muestras incluyen el 2-may (temporada anterior).

**LA Galaxy-Portland Por +1.5 - MEDIA.** Galaxy 9.o Oeste (36 pts) en el corte; Portland 10.o (33). Galaxy en casa 18-18 en 14 PJ (1,29 goles a favor), Portland fuera 20-29 en 14 (peor defensa visitante: 2,07 contra). Muestra: Galaxy no gano por 2+ en sus 4 partidos en casa; Portland perdio por 2 una vez en 5 salidas. Escenario de perdida: Galaxy gana 2-0/3-1: Portland encaja en cada salida y a Galaxy le sirve ganar para no salirse del corte, y ambos con 4 dias de descanso y viaje (rotacion media). La muestra de 1/10 es de rivales mixtos. Cuota 1.295 implica ~77% (-1.5 para Galaxy a ~3,4).

**Bryne-Raufoss U4.5 - BAJA.** Raufoss es 16.o (19 pts, 27-63 en 24 PJ); fuera 11-41 en 11 PJ = 4,73 goles por partido. En la muestra, 2 de sus 4 visitas terminaron con 9 y 10 goles (2-7, 1-9). Bryne 10/10 es de un equipo de pocos goles (2,2 de media) y no habla del rival. Perdida: Bryne (6.o, aspira a ascenso) gana 4-1/3-2/5-0 a un visitante hundido; el partido noruego a las 13:00 Caracas. El 18/20 de la muestra es ruido por mezcla local-visitante: la cifra especifica (Raufoss fuera) apunta a 4,7 de media, por encima de la linea.

**Columbus-Charlotte Cha +1.5 - ALTA.** Columbus 13.o Este (29 pts) en casa 19-16 (2,5 g/PJ), Charlotte 5.o (46 pts) fuera 21-24. Muestra: Columbus ganó por 3 una vez de 5 en casa; Charlotte nunca perdio por 2+ fuera (0/5). Perdida: Columbus gana 2-0/3-1: tendria que haber un partido de Charlotte con rotacion fuerte (rotation.json no incluye este partido: pendiente) y Columbus necesitado de puntos. Ruido: los 3 goles de margen de Columbus fueron un unico partido.

**Dallas-Seattle Sea +1.5 - ALTA.** Dallas 3.o Oeste (47 pts) pero 16.a en casa (25-20); Seattle 7.o (41) fuera 15-15 en 14 (2,14 g/PJ). Muestra: Dallas nunca gano por 2+ en 4 partidos en casa; Seattle nunca perdio por 2+ fuera (0/4 en sus salidas de la muestra). Perdida: Dallas gana 2-0/3-1 en casa en un partido de 20:30 Caracas con ambos "bajo" en rotacion. Ruido: el 0-5 que Dallas perdio en Seattle fue de visitante y de otro contexto.

**Sarmiento-River O0.5 - ALTA.** 20/20 sin 0-0; 4/20 con exactamente 1 gol. Argentina (Clausura, fecha 11): Sarmiento 4.o (19 pts) en grupo B, River 9.o (16 pts). Perdida: 0-0. River juega con 3 dias de descanso y casi sin cambios (0,33, un equipo que repite once = fatiga) y Sarmiento tiene un perfil de muchos 1-0; la liga argentina tiene un porcentaje alto de 0-0 (dato historico no consultado). La unica via de perdida es el 0-0; cuota 1.065.

**Inter Miami-NYC U5.5 + NYC +1.5 (mismo partido) - MEDIA.** Miami 2.o Este (49 pts), 4,64 goles totales por PJ en casa, NYC fuera 2,36. U5.5: 19/20, fallo = el 7-1 del 29-ago. +1.5: Miami gano por >=2 en 2 de sus 6 partidos en casa (6 y 4 goles); NYC perdio por 2+ fuera 0/6. Escenarios de perdida: (a) Miami gana 2-0/3-1/4-0 (rompe +1.5, la pata dominante); (b) goleada 6-1/7-1 (rompe ambas: se solapan solo en ese extremo). Ambos con 4 dias y rotacion 3,0. El 1,93 de la combinacion depende casi enteramente del +1.5 (1.65 en cuota = Miami -1.5 en ~2,1, o ~45% en el mercado). Bajas de Miami (jugadores clave) PENDIENTES.

## 4. x4 (amplio)

**Toronto-Orlando O1.5 - ALTA.** 19/20; Toronto 6/6 en casa. Toronto 11.o (32 pts), en casa 4,0 g/PJ; Orlando fuera 25-47 en 14 (5,14 por PJ). Perdida: 0-0/1-0 con Orlando rotando 4,33 cambios y Toronto con 3,33. Muy poco probable por la defensa visitante.

**Sporting JAX-Birmingham U5.5 - BAJA.** 19/20, pero 9 de 20 partidos terminaron en exactamente 5 goles (borde) y solo 1 paso de 5: 8 (Birmingham 4-4, 17-sep). JAX encaja 29 en 10 (2,9/PJ), Birmingham 22. Perdida: 6+ goles: un 4-2/5-1/3-3, perfectamente normal para dos defensas que reciben 3 por partido. JAX con 14 dias sin jugar y Birmingham 11 (rotation.json: descanso largo, "copa <=4 dias" en Birmingham) = ritmo irregular; el estadio de la fase "Group Stage" de USL no esta explicado en las fuentes. Ruido: el 19/20 se apoya en un truncamiento (nueve 5-goles y casi ningun 6): no es muestra fiable de la cola.

**DC United-NY Red Bulls U5.5 - ALTA.** 19/20 (fallo: DC 3-3... total 6 el 27-sep). DC en casa 3,07, NYRB fuera 2,93; 1/20 al borde. Perdida: 6+ goles, p. ej. 4-2; DC rota 5,67 cambios con 4 dias. DC 12.o y NYRB 8.o (36 pts, en el corte).

**Bohemians-Mlada Boleslav O1.5 - BAJA.** Bohemians en casa solo 4-1 en 4 PJ de tabla (1,25 goles totales por PJ); 7/20 al borde; en casa sus totales 0,1,2,2,4: 2 de 5 por debajo de 2. Perdida: 1-0/0-0/0-1 con rotacion pesada de ambos (5,67 y 5,33 cambios, 4 dias de descanso) y Bohemians 11.o cuidando la zona baja. Ruido: la muestra incluye mayo (temporada anterior). Los 10/10 de MB visitante vienen de partidos contra equipos distintos.

**Bohemians-Mlada Boleslav U4.5 - MEDIA.** 19/20 (unico fallo: MB 4-2 fuera el 27-jul, 6 goles), 5/20 al borde (exactamente 4). MB fuera: 7-11 en 5 PJ (3,6 por PJ). Perdida: 5+ goles, un 3-2/4-1 en un partido en el que ambos rotan mucho; contra, Bohemians en casa solo suma 1,25 por PJ. Mejor que el O1.5.

**Hartford-Charleston O1.5 - MEDIA.** Muestra 18/20, 7/20 al borde (2 goles). Discrepancia: Hartford marca la muestra a 3,0 goles por PJ en los ultimos 10, pero la tabla de la conferencia da 2,15 por PJ en 27 PJ y la tabla de grupo 1,65 en 17 (cifras no reconciliadas; hay dos tablas USL). Charleston fuera: 16-22 en 13 (2,92) pero en casa 36-11. Perdida: 1-0/0-1/0-0, Hartford 6.o de la conferencia con pocos goles estructuralmente. El 10/10 de Hartford es una racha, no un nivel.

**LAFC-Austin Aus +1.5 - BAJA.** Cuota 1.65: el mercado da a LAFC -1.5 alrededor de 2,1 (~45%). LAFC 6.o Oeste (42 pts); en casa 26-12 en 14 (defensa de 0,86 contra); Austin 13.o (31 pts) fuera 16-32 en 14 (2,29 contra) y perdio 1-4 en casa ante Nashville el 11-oct. Muestra LAFC (10 partidos, 1 victoria, 5 empates, 4 derrotas) contradice al mercado: la forma de LAFC es mala, la tabla local es buena. Perdida: LAFC gana 2-0/3-1 en casa a un Austin que concede 2,3 fuera. La cifra de 1/10 en la muestra es ruido (Austin no tuvo rivales fuertes). Bajas de LAFC PENDIENTES.

**Hodd-Ranheim O2.5 - ALTA.** Ranheim: 63-64 en 25 PJ = 5,08 por PJ, fuera 5,0 (n=12); Hodd en casa 3,67. En la muestra de 20, solo 2 fallos (2 goles). Perdida: 1-1/2-0/1-0. Hodd rota 4,0 cambios con 3 dias de descanso y juega a las 13:00 Caracas: un once alternativo suele conceder mas, no menos. Ruido: el 8 y el 7 de goles de Ranheim son extremos.

**Montreal-Atlanta U4.5 - MEDIA.** 18/20, 5/20 al borde. Montreal 15.o Este (24 pts) en casa 19-18 (2,64), Atlanta 14.o (27 pts) fuera 13-22 (2,5). Ambos casi sin opciones de playoff (corte ~36): sin tension competitiva, partido que puede abrirse. Perdida: 5+ goles (3-2, 4-1): Montreal perdio 1-7 fuera en agosto y Atlanta recibe 22 fuera. Ruido: el 1-7 es un unico partido.

**Batman Petrolspor-Istanbulspor O1.5 - MEDIA.** 17/19 (n=9 en Batman). Batman 5.o (16 pts) con 9-6 en casa (3,75 en 4 PJ); Istanbulspor 19.o (5 pts) fuera 3-14 en 5. Perdida: 1-0 de Batman o 0-0: Istanbulspor marca 7 en 9 PJ. Ruido: la muestra de Istanbulspor incluye 1-may (8-1, temporada anterior).

**Umraniyespor-Boluspor U4.5 - ALTA.** 18/20, solo 2 fallos (6 y 5 goles). Umraniyespor en casa 1,6 g/PJ (n=5), Boluspor 20.o con 3 goles a favor en 9 PJ. Perdida: Umraniyespor gana 5-0 como en el 0-6 que Boluspor encajo el 5-sep. Ruido: el 1-4 y el 0-6 vienen de partidos muy anteriores.

**Waldhof-Ingolstadt U14.5 corners - MEDIA.** Corners solo en apifootball, sin segunda fuente; cuota estimada (1.11), no verificada. Waldhof en casa: media 9,9, maximo 14; Ingolstadt fuera: media 11,4, con dos partidos >=15 (16 y 19; el 19 del 11-oct). Perdida: 15+ corners con Ingolstadt (17.o, zona de descenso) persiguiendo el resultado. Ruido: ese partido de 19 corners (Wehen 4-2 Ingolstadt, 11-oct) esta contado a la vez en las dos muestras corners de este ticket (Waldhof-Ingolstadt y Wehen-Aachen); no son independientes.

**Wehen-Aachen U12.5 corners - MEDIA.** Misma limitacion de fuente y cuota. Wehen en casa: media 10,7 (con 15 y 19); Aachen fuera: 8,1, maximo 12. Perdida: 13+ corners con Wehen (18.o, 8 pts) obligado a atacar. 2 de 20 ya superaron 12. El 19 es el partido compartido citado arriba.

**Al Raed-Jeddah U4.5 - MEDIA.** 18/20. La muestra mezcla abril-mayo (otra temporada) y septiembre; Al Raed en casa tiene totales 3,3,5,6 (2 de 4 fallan). Saudi First Division, solo 6 PJ de temporada (Al Raed 13.o, 7 pts, 7-10; Jeddah 10.o). Perdida: 5+ goles con el Al Raed de casa. Cifra de tabla minuscula (n=2 en casa).

## 5. Datos pendientes
- Bajas, dudas y once probable de los 26 partidos (club/oficial/Transfermarkt/prensa local): no consultados con exito.
- Rotation.json no contiene Columbus-Charlotte, Moss-Egersund, LAFC-Austin, Hartford, Wehen y otras; para esas patas el descanso es dato pendiente.
- Segunda fuente de forma y corners para todas las patas (hoy solo apifootball).
- Confirmar la fecha de cierre de la fase regular MLS y el formato de la fase de grupos USL.
- H2H: no consultado (no se considera informativo frente a la forma de 2026).

## 6. Registro de fuentes
| Fuente | URL/ficha | Dato buscado | Estado | Valor |
|---|---|---|---|---|
| apifootball | get_events x26 (match_id) | hora, arbitro, alineaciones, bajas | Consultada y util | hora/arbitro; bajas vacias |
| apifootball | get_standings league 332/362/153/319/134/176/330/120/44/277 | posicion, goles local/visitante | Consultada y util | contexto de fase |
| matrix.json (apifootball) | form local/visitante | ultimos 10 | Consultada y util (misma fuente) | Una sola fuente |
| rotation.json | rotacion/descanso | | Consultada y util | heuristica, incompleta |
| Busqueda web (MLS 14-oct; LAFC-Austin) | varias | calendario/bajas | Consultada con datos insuficientes | sin uso |
| Transfermarkt, FotMob, BetExplorer, Understat, SoccerStats | | | No consultada (politica) | |
