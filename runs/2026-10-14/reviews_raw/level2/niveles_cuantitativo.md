# Niveles de riesgo: informe cuantitativo (8 borradores) - 2026-10-14

Fuente: /home/user/football-picks-system/runs/2026-10-14/tickets.json (leido 2026-10-14 ~01:20 UTC; ningun partido iniciado). Calculos con calc.py (freq, joint) y script propio en scratchpad. Solo informa riesgos y cifras; la decision es del usuario. EV de mercado no se usa como veredicto.

## Metodo y limites (leer primero)
- P(mercado) = producto de prob_implicita_sin_margen por pata (proporcional, aproximacion; cuota_media = promedio de casas, NO precio de una sola casa). Asume independencia entre partidos.
- P(central) = encogimiento tickets.py: (N*f + 40*p_mercado)/(N+40), N=20: pesa 1/3 muestra y 2/3 mercado. NO es evidencia independiente del mercado.
- Piso muestral = producto de limites inferiores Wilson 95% de k/n agrupado (n=20 por pata). Pesimista; no es probabilidad.
- RANGO de P(ticket) = [min(P mercado, piso Wilson) ; P central]. Es una banda de metodos, no un intervalo de confianza. Hipotesis no verificada: independencia entre partidos.
- Sesgo comun: en TODAS las 40 patas la frecuencia observada supera al mercado (brechas +0.07 a +0.34). Patas elegidas por brecha alta = maldicion del ganador; la muestra probablemente sobreestima. Por eso el extremo bajo (mercado) es el mas defendible; el alto (central) es optimista.
- Contexto: n=10 por equipo, ambos agrupados 20; mezcla local/visitante; sin ajuste por rival (calidad de rivales no verificada).
- apif_query.py: get_events con id interno m-... devolvio [] (no es id de apifootball); no se uso para cifras. Rotacion tomada de rotation.json (basada en cambios medios y descanso).

## Tabla resumen
| Borrador | Nivel | Patas/partidos | Cuota media | P(ticket) rango | P mercado / central / piso | P(perdida) rango | Pata mas debil (p sin margen) | Brecha max muestra-mercado | Parte del riesgo por n de patas* |
|---|---|---|---|---|---|---|---|---|---|
| seguridad 1 | estandar | 2/2 | 1.249 | 0.64-0.79 | .709 / .785 / .641 | 0.21-0.36 | St. Louis-Vancouver O1.5 (.829) | .145 | 46% |
| seguridad 2 | estandar | 2/2 | 1.238 | 0.58-0.77 | .705 / .768 / .583 | 0.23-0.42 | Strømmen-Asane O1.5 (.838) | .112 | 46% |
| seguridad 3 | riesgo explicito | 1/1 | 1.250 | 0.73-0.81 | .732 / .805 / .764 | 0.19-0.27 | Santa Fe-Jaguares Hcp vis +2.5 (.732) | .218 | 0% (pata unica) |
| x3 1 | riesgo explicito | 5/5 | 2.856 | 0.24-0.37 | .244 / .369 / .263 | 0.63-0.76 | Bryne-Raufoss U4.5 (.677) | .239 | 67% |
| x3 2 | riesgo alto | 5/4 | 3.086 | 0.24-0.38 | .237 / .381 / .315 | 0.62-0.76 | Inter Miami-NYCFC Hcp vis +1.5 (.571) | .329 | 67% |
| amplio 1 | riesgo alto | 7/7 | 4.173 | 0.11-0.24 | .149 / .242 / .106 | 0.76-0.89 | Los Angeles-Austin Hcp vis +1.5 (.564) | .336 | 72% |
| amplio 2 | riesgo alto | 7/7 | 4.163 | 0.10-0.24 | .151 / .237 / .096 | 0.76-0.90 | Los Angeles-Austin Hcp vis +1.5 (.564) | .336 | 72% |
| amplio 3 | riesgo alto | 8/8 | 4.321 | 0.07-0.21 | .127 / .205 / .067 | 0.79-0.93 | Los Angeles-Austin Hcp vis +1.5 (.564) | .336 | 74% |

*Parte del riesgo por n de patas = (P perdida ticket - P perdida de una sola pata con la media geometrica de las patas) / P perdida ticket. Mide cuanto del fallo proviene de encadenar patas y no de la calidad media (media geometrica por pata .73-.84). Numero esperado de patas falladas (suma de 1-p): seg 0.32/0.32/0.27; x3 1.21/1.21; amplio 1.62/1.62/1.77.
Referencia de equilibrio (1/cuota, informativa, no veredicto): seg 0.80/0.81/0.80; x3 0.35/0.32; amplio 0.24/0.24/0.23. P mercado cae por debajo en todos por el margen de las casas; la banda alta (central) solo lo supera en seguridad 3 (EV central +0.006), x3 y amplio 1; esos EV central dependen de la muestra optimista y cruzan 0.

## Detalle por borrador
### seguridad 1 (x1.249): Cincinnati-New England O1.5 (.855; 20/20 agrupado=1.0/1.0) + St. Louis-Vancouver O1.5 (.829; 1.0/0.9)
- Correlacion: misma direccion (2 overs), misma liga (MLS), misma noche (23:30 y 00:30 UTC). Correlacion positiva debil esperable por entorno; sin base para cuantificar; el producto puede ser algo bajo o alto, no demostrable.
- Rotacion: Cincinnati local 'medio' (4.33 cambios), resto bajo/medio.
- Debil: St. Louis (menor p). Por n de patas: 46% del riesgo.
### seguridad 2 (x1.238): Chicago-Philadelphia O1.5 (.841) + Strømmen-Asane O1.5 (.838)
- Correlacion: 2 overs; ligas distintas (MLS / Noruega), horas distintas; practicamente independientes.
- Strømmen-Asane inicia 13:00 UTC, descanso 3 dias en ambos, rotacion media: primera pata en resolverse. Piso muestral bajo (.58) por 18/20 en dos patas.
### seguridad 3 (x1.25): Santa Fe-Jaguares de Cordoba, hcp visitante +2.5 (.732; 0.9/1.0)
- Pata unica: sin riesgo por numero de patas, solo calidad. Brecha muestra-mercado .218 (frecuencia 0.95 agrupada vs .732 mercado). Jaguares: rotacion ALTA (3 dias descanso, 4.0 cambios); el proyecto veto sus patas de victoria/unders por rotacion, esta pata (hcp +2.5) no esta vetada; rotacion alta del visitante puede restar capacidad de limitar la diferencia (hipotesis no verificada, sin cifra). Solo 4 casas, 3 precios distintos.
### x3 1 (x2.856): Moss-Egersund O1.5 (.850), QPR-Derby U4.5 (.830), LA Galaxy-Portland +1.5 vis (.711), Bryne-Raufoss U4.5 (.677), Columbus-Charlotte +1.5 vis (.720)
- Correlacion: 2 hcp +1.5 visitante (MLS, 02:30 y 23:30 UTC, mismo tipo de fallo: goleada local); 2 patas Noruega primera division mismo horario 17:00 (una over, una under: se compensan en direccion de goles); 2 unders (QPR, Bryne). Todas debiles; no cuantificable.
- Debil: Bryne U4.5 (.677; apoyo_min_equipo 0.49, un equipo con 8/10). Columbus y Bryne sin datos de rotacion. QPR rotacion media provisional. 67% del riesgo viene de encadenar 5 patas.
### x3 2 (x3.086; nivel 3): Dallas-Seattle +1.5 vis (.688), Moss-Egersund O1.5 (.850), Sarmiento-River O0.5 (.875), Inter Miami-NYCFC U5.5 (.810) + Hcp vis +1.5 (.571) mismo partido
- Correlacion mismo partido (Inter Miami-NYCFC): U5.5 y +1.5 visitante fallan ambos en goleadas locales de 6+ goles; asociacion positiva leve (el producto .810x.571=.463 subestima algo la conjunta). La muestra conjunta (8/10 local, 10/10 visitante) da limite Wilson .606 conjunto, pero con una brecha de .33 vs mercado en la pata hcp (muestra .90 vs mercado .571). La cuota 1.93 de la pareja es producto de cuotas medias; que una casa acepte ambas en una combinada (restricciones de partido) y a ese precio: NO verificado.
- Debil: Inter Miami +1.5 (.571). Inter Miami rotacion media provisional. 5 patas, 4 partidos: 67% del riesgo por numero de patas.
### amplio 1 (x4.173): Toronto-Orlando O1.5 (.854), Sporting JAX-Birmingham U5.5 (.835), DC United-NYRB U5.5 (.860), Bohemians-Mlada Boleslav O1.5 (.775), Hartford-Charleston O1.5 (.774), Los Angeles-Austin +1.5 vis (.564), Hodd-Ranheim O2.5 (.719)
- Correlacion: 4 overs / 2 unders; USL Championship x2 (23:00 UTC), MLS x3 (23:30/02:30). Hodd-Ranheim: Hodd tiene rotacion ALTA (3 dias, 4.0 cambios); el proyecto veto todas sus patas under por eso, pero esta over 2.5 se incluyo; efecto de la rotacion sobre goles no verificado.
- Debil: Los Angeles-Austin +1.5 (.564 vs muestra .90: brecha .336, el mercado ve un local claramente favorito; la muestra de los equipos no refleja ese cruce). Sporting JAX, DC y Bohemians con rotacion media provisional. 72% del riesgo por 7 patas.
### amplio 2 (x4.163): Toronto O1.5, Bohemians U4.5 (.825), Hartford O1.5, Los Angeles-Austin +1.5, CF Montreal-Atlanta U4.5 (.769), Batman Petrolspor-Istanbulspor O1.5 (.769; n=9/10), Umraniyespor-Boluspor U4.5 (.828)
- Correlacion: 3 over / 3 under (algo de compensacion de direccion en total); Turquia 1 Lig x2 (11:30 y 14:00 UTC), MLS x3 (Toronto, Montreal ambos 23:30; LA-Austin 02:30). Misma debil que amplio 1. Batman Petrolspor con n=9 en un equipo. Cadena de 7 patas: 72%.
### amplio 3 (x4.321, 8 patas): Toronto O1.5, Bohemians U4.5, Waldhof-Ingolstadt U14.5 corners (.833), Wehen-Aachen U12.5 corners (.833), Al Raed-Jeddah U4.5 (.835), Los Angeles-Austin +1.5, Hodd-Ranheim O2.5, Batman O1.5
- ADVERTENCIA de datos: las 2 patas de corners (3. Liga, ambas 17:00 UTC) tienen cuota_tipo estimada_por_modelo, n_casas=0, cuota 1.11: su "probabilidad sin margen" .833 NO es de mercado observado, es salida de modelo. El P de mercado de este ticket (.127) incorpora dos valores no verificados; la cuota combinada x4.321 no existe como precio observado (usa_cuota_estimada=True). Frecuencias 18/20 en cada una, con n_recientes=8 (muestra reciente corta, discrepancia respecto a n=10). Al Raed-Jeddah con 4 casas.
- Correlacion: 4 unders (2 corners 3. Liga mismo horario, goles); Hodd rotacion alta como arriba. Debil: Los Angeles-Austin. Mayor numero de patas: 74% por encadenamiento, P(ticket) mas baja: 0.07-0.21.

## Estado de datos
| Dato | Fuente | Fecha | n | Estado |
|---|---|---|---|---|
| Prob. sin margen por pata, frec k/n | tickets.json (apifootball misma competicion + cuotas medias 4-7 casas) | 2026-10-14 | 10+10 | Una sola cadena de datos (no independiente) |
| Corners 3. Liga (2 patas, amplio 3) | cuota estimada por modelo | 2026-10-14 | 8 recientes | No verificable (sin cuota de mercado) |
| Rotacion | rotation.json | 2026-10-14 | 4 partidos previos | Una fuente; faltan 8+ partidos sin dato |
| Cuota de un solo operador | no verificada | - | - | Los multiplicadores son promedios de casas; sin valor economico confirmado |

## Hipotesis no verificadas
Independencia entre partidos; que la cuota combinada exista en una casa concreta; efecto de la rotacion sobre goles/hcp; calidad de rivales en las muestras; liquidacion de la linea .5 de hcp y cuartos asiaticos.
