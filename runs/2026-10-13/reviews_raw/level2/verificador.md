# Verificador de mercados, Nivel 2, jornada 2026-10-13 (America/Caracas)

Consulta: 2026-10-13. Vía única de datos externos: `apif_query.py` (apifootball). Consultas propias: 35 de 35 (14 get_events + 21 get_odds), ninguna falló. No se ha tocado el repo `insta-mcp` ni hecho push.

## 1. Registro de fuentes
| Fuente | Ficha | Dato buscado | Resultado | Estado | Discrepancias | Alternativa |
|---|---|---|---|---|---|---|
| apifootball (apif_query.py) | get_events match_id=848527,839350,835226,734585,740633,822550,849390,766902,802933,796954,808966,814169,812209,853192 (timezone=UTC) | equipos, competición, hora UTC, estado | 14 fichas leídas; hora UTC idéntica a `inicio_utc` en las 14; `match_status` vacío en las 14 | Consultada y útil | estado no confirmable (campo vacío) | n/a |
| apifootball | get_odds de los 21 match_id | casas, cuota por pata, existencia de mercado | 21 respuestas leídas; 3–10 casas por partido; `odd_date` 2026-10-13 03:18:46–03:18:59 (zona no declarada) | Consultada y útil | ver sección 3 | n/a |
| apifootball | get_events de 821996, 718968, 815117, 815121, 853133, 812206, 813708 | idem | NO consultados (tope de 35) | No consultada | n/a | solo datos del pipeline (finalists.json) |
| APWin | n/a | segunda fuente de calendario | no se consultó (el encargo fija la herramienta única) | No consultada | n/a | solo lo declarado en finalists.json |
| FotMob, BetExplorer, Transfermarkt, Understat, SoccerStats | n/a | n/a | excluidas por política | No consultada, excluida por política | n/a | n/a |
| OddsPortal, Oddschecker, Flashscore, Soccerway, SofaScore, FootyStats, oficiales | n/a | cuotas independientes, horario oficial | no revisadas en la política, denegadas | No consultada | n/a | n/a |

Limitación estructural: las cuotas de las ~10 casas vienen de UN solo agregador (apifootball) y de UN solo snapshot (03:18). Según el protocolo son UNA vía, no dos independientes. Ninguna pata cumple "cuotas en ≥2 vías independientes". Además Marathon y 1xBet suelen repetir la misma cuota (Kyoto +2.5 1.19/1.19; Fajr X2 1.62/1.62), así que el número efectivo de casas es menor que n_casas.

## 2. Tabla por partido
Convención del feed: `ah-X_2` = visitante +X; `ah+X_1` = local +X; `o+N`/`u+N` = más/menos de N goles; `odd_1x`/`odd_12`/`odd_x2` = doble oportunidad. Comprobado con 1X2: Kyoto local 1.38, `ah-2.5_1` 3.68 y `ah-2.5_2` 1.22; Queen's Park local 4.26 con `ah+2.5_1` 1.09.

| # | Partido (match_id API) | Hora/estado (get_events) | Cuota API (casas, min–max, media) vs finalists | Veredicto |
|---|---|---|---|---|
| 1 | Kyoto – Ratchaburi (848527), ACL Elite fase liga, ronda 2 | 10:00 UTC = igual; estado vacío | AH vis +2.5: 3 casas 1.19–1.27, media 1.217 = igual. AH vis +1.5: 6 casas 1.65–1.72, 1.683 = igual | OK. Patas duplicadas en finalists (misma pata listada 2 veces por aparecer en 2 listas). Solo 3 casas, 2 de ellas idénticas (1.19) |
| 2 | Cardiff – Watford (812209), Championship | 18:45 = igual; estado vacío | u4.5: 7 casas 1.20–1.27, 1.241 = igual | OK |
| 3 | Bucaramanga – Águilas (766902), Primera A Clausura | 23:30 = igual; estado vacío | 1X: 8 casas 1.16–1.27, 1.234 = igual (Sbo 1.16 con overround 1X2 1.168) | OK en cuota. DISCREPANCIA en `prob_implicita_sin_margen` (ver 3.1) |
| 4 | Norrköping – Sundsvall (718968), Superettan | no consultado | u5.5: 7 casas 1.08–1.14, 1.107 = igual | Parcial (horario no verificado por mí) |
| 5 | Simba – Mashujaa (821996), Ligi Kuu Bara | get_events no consultado; `status_raw` 'Not Started' viene del pipeline | 12: API da 5 casas 1.06–1.13, media 1.088; finalists dice 4 casas, media 1.095 | DISCREPANCIA menor (ver 3.2) + implícita errónea (3.1). Feed con 6 casas, Dafabet sin precio |
| 6 | Gloucester – Taunton (814169), Southern Premier South | 18:45 = igual; estado vacío | o1.5: 4 casas 1.07–1.13, 1.093 = igual | OK, pocas casas (Marathon/1xBet duplicadas) |
| 7 | Hyde – Quorn (815117), Northern Premier | no consultado | o1.5: 3 casas 1.15–1.20, 1.167 = igual | Parcial. Solo Marathon/1xBet/Betano (1.15/1.15/1.20) |
| 8 | Workington – Whitby (815121), Northern Premier | no consultado | o2.5: 6 casas 1.45–1.65, 1.508 = igual (Betfair 1.65 es el atípico) | Parcial (horario no verificado) |
| 9 | Fajr Sepasi – Aluminium Arak (849390), Persian Gulf Pro League | 13:30 = igual; estado vacío | X2: 3 casas 1.62–1.78, 1.673 = igual. Feed con solo 4 casas (Marathon, 1xBet, Betano, Dafabet sin precio) | OK en cuota, pero débil. Implícita errónea (3.1). Historial n=7 |
| 10 | Inter – Club Brugge (853192), UCL fase liga | 19:00 = igual; estado vacío | u5.5: 6 casas 1.08–1.16, 1.103 = igual. AH vis +2.5: 7 casas 1.40–1.50, 1.441 = igual | OK |
| 11 | Athletic-MG – Londrina (740633), Serie B ronda 33 | 22:30 = igual; la API llama al local "Athletic Club" (sin sufijo MG) | o1.5: 7 casas 1.35–1.40, 1.374 = igual. Tarjetas A+R 2.5: SIN mercado en get_odds | DISCREPANCIA en la pata de tarjetas (ver 5). Pata de goles OK |
| 12 | Arsenal – Lille (853133), UCL | no consultado | u5.5: 6 casas 1.04–1.09, 1.06 = igual. AH vis +2.5: 7 casas 1.40–1.52, 1.471 = igual | Parcial (horario no verificado) |
| 13 | RW Essen – Fortuna Köln (808966), 3. Liga | 17:00 = igual; estado vacío | AH vis +2.5: 3 casas 1.16–1.23, 1.183 = igual | OK, 3 casas (2 idénticas) |
| 14 | Birmingham – Preston (812206), Championship | no consultado | AH vis +1.5: 7 casas 1.41–1.53, 1.459 = igual | Parcial |
| 15 | Leamington – Redditch (813708), Southern Premier Central | no consultado | o1.5: 3 casas 1.17–1.21, 1.183 = igual | Parcial, 3 casas |
| 16 | Harju – Nõmme United (734585), Meistriliiga | 15:00 = igual; la API nombra "Harju JK Laagri" y finalists "Harju Jalgpallikool" | 12: 7 casas 1.07–1.25, 1.181 = igual. BetVictor 1.07 es atípica (overround 1X2 1.198) | DISCREPANCIA de nombre (probable mismo club, no confirmado por 2.ª fuente). Implícita errónea (3.1) |
| 17 | Orlando Pirates – TS Galaxy (822550), liga API "Play-offs 1/2" | 17:30 = igual; estado vacío | u5.5: 4 casas 1.01–1.04, 1.03 = igual. AH vis +2.5: 4 casas 1.38–1.45, 1.41 = igual | DISCREPANCIA de formato: la API dice "Play-offs 1/2", finalists "premier soccer league". No verifiqué si es eliminatoria ni si hay prórroga (ver 4) |
| 18 | Hartlepool – Newcastle Utd U21 (839350), National League Cup | 18:00 = igual; equipo "U21" | 12: 7 casas 1.04–1.17, 1.101 = igual. Visitante U21 favorito (1.40) | DISCREPANCIA de categoría: sub-23, `calendario` solo apifootball |
| 19 | Queen's Park – Inverness (802933), Scottish Championship | 18:45 = igual; árbitro D. Nicolson | AH local +2.5: 4 casas 1.06–1.13, 1.09 = igual | OK (esta pata solo está en el top, no en borradores) |
| 20 | National Bank Egypt – El Gaish (835226), Premier League egipcia | 14:00 = igual | o0.5: 7 casas 1.05–1.11, 1.079 = igual | OK en cuota. `calendario` REQUIERE_VERIFICACION_ADICIONAL (una sola fuente) |
| 21 | Sariyer – Bodrumspor (796954), 1. Lig | 14:00 = igual | u4.5: 6 casas 1.05–1.10, 1.07 = igual | OK (solo top) |

Hora: 14 de 14 consultados coinciden en UTC con `inicio_utc` (diferencia 0 min). Ningún estado distinto de programado, pero `match_status` está vacío (no "Not Started") en los 14, así que el estado programado NO está confirmado explícitamente. Ninguna categoría juvenil/reserva/femenina salvo Hartlepool–Newcastle U21 (ya excluida de borradores). Ningún emparejamiento tipo "Arsenal U19 vs Arsenal Tivat" detectado en los 14 consultados. Las medias de finalists.json coinciden con el feed en 26 de 27 patas únicas; la excepción es Simba (3.2) y la pata de tarjetas (sin cuota en feed).

## 3. Discrepancias
### 3.1 `prob_implicita_sin_margen` errónea en las 5 patas de doble oportunidad (hallazgo principal)
| Pata | Valor en finalists/tickets | Orden de magnitud correcto (de 1X2 de las casas, normalizado) |
|---|---|---|
| Bucaramanga 1X | 0.379 | ~0.75 |
| Simba 12 | 0.426 | ~0.84 |
| Fajr X2 | 0.272 | ~0.55 |
| Harju 12 | 0.384 | ~0.76 |
| Hartlepool 12 | 0.418 | ~0.82 |

Cálculo: 1/cuota ya da 0.81, 0.91, 0.60 y 0.85 antes de quitar margen, y la normalización de 1X2 (get_odds, odd_1/odd_x/odd_2) da lo anterior. Los valores del pipeline parecen normalizar las tres líneas de doble oportunidad entre sí (suma ≈1), lo que divide la probabilidad por ~2. Efecto: `implícita conjunta` de seguridad B3 (0.379), B4 (0.357) y amplio B1/B2/B5 está infravalorada, y cualquier "EV/indicador descriptivo" basado en ello es inválido. Las cuotas medias no están afectadas. Es un error del pipeline, no del feed.

### 3.2 Simba 12
Finalists: 4 casas, 1.06–1.13, media 1.095. Feed: bet365 1.10, Marathon 1.06, Betfair 1.13, 1xBet 1.06, Betano 1.09 (5 precios, media 1.088). Quitando 1xBet se reproduce 1.095. En Kyoto +2.5 el pipeline sí conserva Marathon y 1xBet idénticas, así que el criterio de deduplicación no es uniforme. Impacto mínimo (0.007).

### 3.3 Otros
- Finalists duplica patas: 41 entradas son 27 patas únicas (una entrada por aparición en cada borrador/top).
- Odds snapshot 03:18 (zona no declarada), horas antes de los partidos de tarde/noche. Cuotas no ejecutables.
- Sanidad del feed: Harju `ah-2.5_1` 2.65 con local 1.94 en 1X2 (incoherente); Hyde `ah-2.5_2` media 1.00 y Leamington 1.01. Estas líneas no se usan en patas, pero indican calidad baja en el hándicap de ligas menores.

### 4. Reglas de liquidación (confirmadas por convención estándar; no he leído reglas de ninguna casa concreta)
| Selección | Significado | Ambigüedad |
|---|---|---|
| Hándicap visitante +2.5 | visitante gana, empata o pierde por ≤2 goles (pierde si cae por ≥3); media línea, sin push | Ninguna. Tiempo reglamentario + descuento |
| Hándicap visitante +1.5 | visitante no pierde por ≥2 | Ninguna |
| Hándicap local +2.5 (Queen's Park) | local no pierde por ≥3 | Ninguna |
| Más de 1.5 / 2.5 / 0.5; Menos de 4.5 / 5.5 goles | ≥2 / ≥3 / ≥1 goles; ≤4 / ≤5 goles, 90 min + descuento, sin prórroga ni penaltis | Orlando Pirates–TS Galaxy: la API lo llama "Play-offs 1/2"; si es eliminatoria con prórroga, hay que confirmar con la casa que liquida a 90 min. UCL y ACL fase liga no tienen prórroga |
| Local o empate (1X), Empate o visitante (X2), Gana alguno sin empate (12) | doble oportunidad a 90 min; 12 pierde si hay empate | Ninguna. Nota: "12" no es "empate no apuesta" (el empate no devuelve la apuesta) |
| Más de 2.5 tarjetas (A+R) | no verificable | Atención: puede ser nº de tarjetas o puntos (amarilla=1, roja=2/3 según casa); doble amarilla; técnicos y banquillo. Sin mercado en feed |

Existencia del mercado en el feed (get_odds): todas las líneas de goles, hándicap de media línea y doble oportunidad aparecen con precio en ≥3 casas. Tarjetas y córners NO existen en get_odds.

### Item 4 (solapes entre borradores)
- Seguridad (7 partidos) vs amplio (10 partidos): intersección vacía. VERIFICADO leyendo tickets.json (cada match_id de los 5 borradores de cada perfil). Coincide con `sin_partidos_repetidos_entre_perfiles: true`.
- Dentro de "amplio" sí hay partidos repetidos entre borradores alternativos: Workington en B1/B4/B5; Arsenal–Lille en B2/B3/B5; Inter–Brugge en B1/B3; Athletic-MG en B2/B4; Fajr en B1/B2; Birmingham en B3/B4. Dentro de "seguridad" no hay solapes. El flag `sin_partidos_repetidos_entre_principales: true` es engañoso si se interpreta como sin repetición entre los 5 amplios. Elegir un borrador de cada perfil es seguro; elegir dos amplios no.
- Productos de cuota recomputados = cuota_combinada_media (±0.001). Amplio B2 y B4 incluyen la pata de tarjetas con cuota estimada.

## 5. Patas a REVISAR / ELIMINAR
ELIMINAR
1. Athletic-MG–Londrina "Más de 2.5 tarjetas (A+R)" (amplio B2 y B4): `cuota_tipo` estimada_por_modelo, n_casas 0; get_odds 740633 no trae mercado de tarjetas en ninguna de las 10 casas. Cuota 1.13 inventada por el modelo, regla A+R vs puntos ambigua, historial n=9. Sin la pata, B2 baja a ×3.58 y B4 a ×3.58 (hay que recomponer; no dentro de ×4–4.8).
2. Hartlepool–Newcastle U21 "12" (top_seguridad-3): categoría sub-23 (get_events 839350: "Newcastle Utd U21"), plantilla rotativa, una sola fuente de calendario. Además `prob_implicita` errónea (3.1).

REVISAR
3. Todas las patas de doble oportunidad (Bucaramanga 1X seguridad B3; Simba 12 seguridad B4; Fajr X2 amplio B1/B2; Harju 12 amplio B5): la `prob_implicita_sin_margen` del pipeline está mal por factor ~2 (3.1); recalcular antes de usarlas como argumento. Cuota correcta.
4. Fajr Sepasi X2: feed con 4 casas y solo 3 con precio (Marathon 1.62 = 1xBet 1.62, Betano 1.78); historial n=7 (muestra débil, <8). Dos borradores amplios dependen de esta pata.
5. Orlando Pirates–TS Galaxy (amplio B5, 2 patas): la API etiqueta la competición como "Play-offs 1/2"; confirmar formato (eliminatoria o liga) y regla de prórroga con la casa. Cuotas muy bajas (u5.5 1.03, de 4 casas).
6. Harju – Nõmme (amplio B5): nombre local difiere ("Harju JK Laagri" en API); confirmar que es el mismo club. BetVictor 1.07 vs resto 1.17–1.25.
7. Kyoto +2.5 (seguridad B1), RW Essen +2.5, Hyde o1.5, Leamington o1.5, Gloucester o1.5: solo 3–4 casas, con Marathon y 1xBet repetidas, es decir 2–3 precios independientes.
8. Partidos NO verificados con get_events por tope de 35 consultas: Norrköping (seguridad B4), Simba (B4), Hyde (B5), Workington, Arsenal–Lille, Birmingham, Leamington (amplios). Su horario/estado solo se apoya en el pipeline.
9. Patas con 2 mercados del mismo partido (Inter y Arsenal: u5.5 + AH +2.5; Athletic; Orlando): la casa recalculará la combinada (cuota menor que el producto). Las cuotas del ticket no son ejecutables.
10. Estado "programado" no confirmado explícitamente: `match_status` vacío en los 14 eventos leídos.

Sin cambios: Cardiff u4.5 (seguridad B2), Norrköping u5.5, Gloucester o1.5, Inter u5.5/+2.5, Arsenal u5.5/+2.5, Birmingham +1.5, Workington o2.5, Queen's Park local +2.5, National Bank Egypt o0.5 (calendario de una sola fuente), Sariyer u4.5: cuota y mercado coinciden con el feed.

## 6. Estado por candidato
- Verificado (hora UTC, equipos y cuota/mercado en feed; la cuota sigue siendo de una sola vía): Kyoto +2.5/+1.5, Cardiff u4.5, Bucaramanga 1X (cuota), Gloucester o1.5, Inter u5.5 y +2.5, RW Essen +2.5, Queen's Park +2.5, Sariyer u4.5, National Bank Egypt o0.5 (hora sí; calendario una sola fuente), Fajr X2 (cuota; débil).
- Parcial (cuota verificada, horario/estado no verificado por mí o con salvedad): Norrköping, Simba, Hyde, Workington, Arsenal–Lille, Birmingham, Leamington, Harju (nombre), Orlando Pirates (formato).
- No verificable: Athletic-MG Más de 2.5 tarjetas (A+R). Las patas de goles de Athletic-MG sí están verificadas.
- Eliminar por categoría: Hartlepool–Newcastle U21.
