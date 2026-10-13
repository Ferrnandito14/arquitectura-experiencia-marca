# x4 hoy (13-oct-2026) - Evaluacion cuantitativa de los 3 borradores del perfil "amplio" x4.0-4.8 + revision de la regla de tarjetas

Alcance: tickets.json `targets[0]` (amplio, 3 borradores; `targets[1]` amplio_champions = 0 borradores). Datos: `matrix.json` (api_prices: cuotas MEDIANAS por lado, minmax, n_casas), `review_cards.json`, correcciones de lote `reviews_raw/batch/b01, b07, b09, b10, b11`. Calculos con `calc.py` (novig_probs / ev_unit / joint_prob / wilson) importado como modulo. Sin API ni fuentes externas (solo cache local para la parte 2). Cuotas: agregador de 4-7 casas, ejecucion de ~15:08 UTC del 13-oct, NO ejecutables.

Separacion usada: frecuencia observada (k/n) | estimacion de modelo | prob. implicita bruta (1/cuota) | prob. sin margen (proporcional, aproximacion; las dos medianas de un mercado pueden venir de casas distintas) | hipotesis no verificadas.

## 0. Veredicto corto

- Ninguno de los 3 borradores tiene ventaja demostrada. Con la unica probabilidad defendible (mercado sin margen) el EV teorico es -33 % / -39 % / -41 % (B1/B2/B3). Rango extremo con minmax de casas: -41 a -26 % (B1), -48 a -31 % (B2), -49 a -33 % (B3): no cruza 0.
- Probable no es rentable: cada pata es probable (63-81 % segun mercado) pero la conjunta de mercado es 14-16 % frente a un equilibrio de 23.6-24.0 %. El producto de 5-6 patas con ~8 % de margen cada una es lo que destruye el valor.
- Estimacion propia de la conjunta: "no estimable" (ver 3). No se calcula EV "propio".
- Orden por precio (menos desfavorable primero): B1 (-33 %), B2 (-39 %), B3 (-41 %). Es diferencia de margen compuesto (5 vs 6 patas), no de calidad deportiva.
- Los 3 borradores NO diversifican: comparten 5 patas (Durban y Athletic-MG en los 3; San Carlos en B1+B3; Bucaramanga en B1+B2; Bristol +1.5 en B2+B3).

## 1. Probabilidad por pata (mercado) y conjunta

Sin margen = 1/cuota normalizada con la mediana del lado opuesto (`novig_probs`). Rango = lado elegido a su cuota max. y contrario a su min. (cota inferior) y viceversa (superior): envolvente muy generosa que mezcla casas. "Frec. media" = media de los dos k/n por equipo (n=10/10, salvo Chippenham 9/10), solo descriptiva.

| Borr. | Partido / seleccion | Cuota (mediana; min-max; n casas) | Impl. bruta 1/C | Sobre-redondeo (suma 1/C de ambos lados) | Prob. sin margen (rango) | Frec. media obs. (no es prob.) |
|---|---|---|---|---|---|---|
| 1 | Pendikspor-Van BB, Mas 1.5 | 1.22; 1.21-1.27; 7 | 0.820 | 1.093 | 0.750 (0.73-0.77) | 0.95 |
| 1,2,3 | Durban City-AmaZulu, Menos 2.5 | 1.46; 1.44-1.50; 7 | 0.685 | 1.083 | 0.632 (0.62-0.64) | 0.90 (10/10 y 8/10) |
| 1,2,3 | Athletic-MG-Londrina, Mas 1.5 | 1.36; 1.35-1.40; 7 | 0.735 | 1.083 | 0.679 (0.66-0.69) | 0.90 |
| 1,3 | San Carlos-Inter San Carlos, Menos 3.5 | 1.30; 1.29-1.32; 6 | 0.769 | 1.085 | 0.709 (0.69-0.73) | 0.90 |
| 1,2 | Bucaramanga-Aguilas Doradas, Mas 1.5 | 1.33; 1.31-1.35; 7 | 0.752 | 1.074 | 0.700 (0.68-0.71) | 0.90 |
| 2 | Birmingham-Preston, Menos 4.5 | 1.14; 1.12-1.18; 7 | 0.877 | 1.077 | 0.814 (0.80-0.84) | 1.00 |
| 2 | Workington-Whitby, Mas 1.5 | 1.135; 1.11-1.20; **4 casas** | 0.881 | 1.097 | 0.803 (0.77-0.82) | 0.95 |
| 2,3 | Bristol-Blackburn, Handicap visitante +1.5 (clave `handicap-1.5`, lado 2) | 1.22; 1.20-1.36; 7 (lado local 3.52, minmax 1.06-3.94) | 0.820 | 1.104 | 0.743 (0.725-0.767)* | 0.90 |
| 3 | FUS Rabat-Raja, Menos 3.5 | 1.135; 1.12-1.17; 6 | 0.881 | 1.093 | 0.806 (0.79-0.82) | 0.95 |
| 3 | Chippenham-Frome, Mas 1.5 | 1.185; 1.17-1.22; **4 casas** | 0.844 | 1.097 | 0.769 (0.75-0.78) | 0.90 (n 9/10) |

*Bristol: el minimo 1.06 del lado local en `handicap-1.5` es incompatible con la mediana 3.52 (media 3.29): cifra defectuosa; la descarto y uso la media (0.725) como cota inferior (con 1.06 saldria 0.44). Coherencia con el 1x2 (2.05 / 3.425 / 3.535).

Conjunta bajo independencia (partidos distintos; `joint_prob`):

| Borrador | Cuota ticket (prod. medianas) | Cuota con cada pata a su min / max | Equilibrio 1/cuota | Conjunta mercado sin margen | Rango conjunto (envolvente) | Brecha vs equilibrio | EV con p de mercado | EV rango (cotas) |
|---|---|---|---|---|---|---|---|---|
| 1 (5 patas) | 4.188 | 3.975 / 4.753 | 0.239 | 0.160 | 0.141-0.177 | -0.079 (-33 % rel.) | -0.331 | -0.41 a -0.26 |
| 2 (6 patas) | 4.169 | 3.799 / 5.460 | 0.240 | 0.146 | 0.125-0.165 | -0.094 (-39 %) | -0.392 | -0.48 a -0.31 |
| 3 (6 patas) | 4.236 | 3.943 / 5.381 | 0.236 | 0.140 | 0.121-0.158 | -0.096 (-41 %) | -0.406 | -0.49 a -0.33 |

Lectura:
- EV con p de mercado = producto(1/sobre-redondeo) - 1: es el coste del margen compuesto, no una ventaja/desventaja de modelo. Coincide con la "implicita de mercado sin margen" de tickets.md (0.16 / 0.146 / 0.14).
- La cuota ejecutable sera <= el producto de medianas (mezcla de casas; en una casa unica la combinada puede ser menor). Con cada pata a su cuota minima, EV con p de mercado = -36 % / -45 % / -45 %. Sin cuota verificada de casa: fundamento deportivo, sin valor economico confirmado.
- El "apoyo conjunto" de tickets.md (0.087 / 0.063 / 0.053) es el producto de limites inferiores de Wilson: NO es probabilidad (subestima la conjunta) y su "margen" (-0.15 a -0.18) no es EV; solo ordena.

## 2. Sensibilidad (hipotesis, no estimacion)

Para EV=0 la conjunta debe subir de 0.160/0.146/0.140 a 0.239/0.240/0.236, es decir:
- +5.8 / +6.2 / +6.5 pp ADITIVOS uniformes por pata sobre el mercado, o
- dar a la frecuencia muestral media un peso w de 27 % / 31 % / 35 % (resto mercado), con p_i = p_mercado + w*(f_i - p_mercado).
Con w=0.25: EV -2 % / -9 % / -13 %; con w=0.5: +39 % / +32 % / +24 % (ilustrativos, sin respaldo). Todo depende de un w sin base. Motivos para creer w bajo: (1) las frecuencias superan al mercado en +15 a +27 pp en TODAS las patas, patron tipico de seleccion por "mayor apoyo" entre cientos de patas (maldicion del ganador); (2) n=10 por equipo, local y visitante mezclados, sin ajuste por rival ni localia; (3) el mercado ya incorpora bajas y calidad. Conclusion: EV probablemente <0; solo cruzaria 0 con una confianza en la muestra no demostrable: sin ventaja demostrada.

## 3. Estimacion propia: "no estimable"
No hay segunda fuente independiente de frecuencias (todo API-Football misma competicion), no hay ajuste por rival y la seleccion sesgada impide leer k/n como p. Las correcciones de lote solo senalan brechas.

Banderas de lote relevantes (estado: revision por agentes, una sola fuente):
- Pendikspor (b01 deportivo): historial local mezcla eliminatorias (Quarter-finals) con liga regular.
- Durban (b10 cuant.): over 2.5 0/10 local y 2/10 visitante vs ~37 % de mercado (discrepancia moderada); (b10 deportivo): etiqueta "Play-offs 1/2" en el historial. El local anota 0.4 GF/partido: el 10/10 es de un equipo atipico y el mercado (63 %) discrepa ~28 pp. Pata mas debil y presente en los 3 borradores.
- Workington (b09 cuant.): "discrepancia fuerte frecuencia vs implicita en over 1.5/2.5" (10/10 y 9/10 vs 80 % y 61 %); nivel 7 ingles (b09 deportivo); solo 4 casas.
- Chippenham (b11): nivel 7, n 9/10, 4 casas (flags de tarjetas irrelevantes aqui).
- Bucaramanga (b07): over 1.5 18/20 (90 %) vs 70 % de mercado, "no tratar como ventaja". Birmingham (b07): aviso BTTS, no afecta a Under 4.5.
- Athletic-MG, San Carlos, FUS Rabat, Bristol: sin correcciones.

## 4. Que pata aporta mas riesgo por unidad de cuota

Dos lecturas:
a) Riesgo de fallo absoluto (prob. de fallar sin margen): Durban U2.5 36.8 %, Athletic O1.5 32.1 %, Bucaramanga 30.0 %, San Carlos 29.1 %. Fallo por unidad de ganancia neta (1-p)/(C-1): peor Workington 1.46, FUS Rabat 1.43, Birmingham 1.33, Chippenham 1.25, Bristol 1.17, Pendikspor 1.14; mejor Durban 0.80.
b) Coste de margen por unidad de pago ln(sobre-redondeo)/ln(cuota): Workington 0.73, FUS 0.70, Birmingham 0.57, Chippenham 0.55, Bristol 0.50, Pendikspor 0.45, San Carlos 0.31, Athletic 0.26, Bucaramanga 0.25, Durban 0.21. Las patas de cuota ~1.13-1.14 gastan casi tres cuartas partes de su pago en margen. Quitar cualquier pata mejora el EV (menos margen compuesto) pero saca la cuota del rango 4.0-4.8.
Resumen: mayor riesgo de fallo y peor evidencia = Durban; peor precio por unidad de cuota = Workington (B2), FUS Rabat (B3), Birmingham (B2); dato de precio defectuoso = Bristol +1.5. Alta probabilidad pero precio desfavorable: Workington/FUS/Birmingham (80-81 %).

## 5. Patas compartidas y correlacion de fallo

Compartidas: Durban U2.5 (B1,B2,B3), Athletic-MG O1.5 (B1,B2,B3), San Carlos U3.5 (B1,B3), Bucaramanga O1.5 (B1,B2), Bristol +1.5 (B2,B3). Unicas: Pendikspor (B1); Birmingham, Workington (B2); FUS Rabat, Chippenham (B3). Total 10 partidos distintos. Enumeracion exacta con p de mercado:
- P(gana) B1 16.0 %, B2 14.6 %, B3 14.0 %.
- Correlacion entre resultados de tickets: B1-B2 0.42, B1-B3 0.40, B2-B3 0.36.
- P(ganan los 3) 4.8 % (0.33 % si fueran independientes); P(pierden los 3) 72.1 % (61.7 % indep.); P(al menos uno gana) 27.9 % (38.3 % indep.).
- P(otro falla | uno falla) = 91-92 % (frente a 85-86 % sin condicionar).
- Durban U2.5 y Athletic O1.5 estan en los 3: P(falla alguno) = 1 - 0.632*0.679 = 57.1 %; ese evento tumba los 3 a la vez (~79 % de la probabilidad de perder los 3).
- 1 u en cada uno: EV total -1.13 sobre 3 u (-37.6 %); desviacion tipica 3.46 u frente a 2.59 u si fueran independientes (+34 %). La correlacion no cambia el EV, concentra la varianza: tener tres opciones no es diversificar.
- Dentro de cada ticket: partidos distintos, independencia razonable pero no verificada.
Apostar un unico borrador: B1 es el menos desfavorable en precio (incluye Pendikspor con historial parcialmente mixto y Durban).

## 6. SEGUNDA PARTE - Regla de tarjetas

Archivos: `/home/user/football-picks-system/.claude/skills/seleccion-final-picks/scripts/adapters.py` (`_card_points` L341-376; respaldo L389-390) y `tickets.py` (`_cards_tuple` L85-97, `STAT_MARKETS` L126-131, cuota estimada L236-253, `unpriced` L536-560). Verificacion con la cache local (3942 partidos con lista de tarjetas, 15 270 eventos), sin API.

### 6.1 Logica de puntos (correcta)
`p = 3 si (y>=2 y r==0) si no min(3, y+2r)` por (lado, nombre de jugador): 1A=1 OK; roja directa=2 OK; 1A+roja=3 OK; 2A+roja=min(3,4)=3 OK; 2A sin roja registrada=3 OK (regla de la casa). Excluye eventos sin nombre (cuerpo tecnico) y prorroga (`score_info_time`="Extra Time" o minuto numerico >90); "90+3" y "45+2" cuentan (no son isdigit). En la cache: minutos numericos >90 son 82/82 "Extra Time"; las prorrogas "105+2" llevan Extra Time. Patrones por jugador (y,r): (1,0)=13 263; (0,1)=603 (roja directa, 2 pts); (2,1)=215 y (1,1)=122 (3); (2,0)=16 (roja no registrada, 3). La API registra la doble amarilla como 2 amarillas + roja, por lo que (0,1) es roja directa: correcto.

### 6.2 Hallazgos
1. MEDIO - "evento sin nombre = cuerpo tecnico" no esta verificado: 483 eventos (3.2 %: 354 amarillas, 129 rojas) con `info`=home/away y sin nombre ni id. Apoyo parcial: en 11/12 filas-lado la estadistica agregada "Yellow Cards" coincide con las amarillas nombradas (no los incluye), pero n=12 y mismo proveedor. Si fueran jugadores con nombre perdido, se infravaloran puntos (rojas valen 2). Estado: hipotesis plausible no confirmada.
2. MEDIO - descarte de partidos con 0-0 puntos (`_card_points` -> None si pts==[0,0]; `_cards_tuple` si t0+t1==0). Justificado en lo principal: 3559 de 6857 partidos finalizados de la cache tienen lista vacia y casi todos sin estadistica (solo 2 con "Yellow Cards"=0 explicito): lista vacia = dato ausente, no 0. Pero un 0 real tambien se pierde y un partido con solo tarjetas de banquillo/tecnico queda "ausente". Efecto: sesgo ligero a mas tarjetas, que favorece "mas de" (p. ej. "Blackburn mas de 0.5", "Petrojet mas de 0.5", "Durban City mas de 0.5", "Al-Saqer mas de 0.5") y perjudica "menos de". En lineas de equipo solo se pierde el partido si AMBOS tienen 0.
3. MEDIO (latente) - respaldo `amarillas + 2*rojas` (sin lista de eventos pero con estadisticas agregadas): sin tope de 3, sin regla de doble amarilla (si el proveedor cuenta 2A+1R da 4 en vez de 3; patron (2,1) = 215 jugadores), admite cuerpo tecnico (documentado) y mezcla definiciones distintas dentro de una misma muestra. Impacto actual bajo (2 partidos de la cache entran por esta via) pero la mezcla no esta senalada en la ficha.
4. BAJO - la API no distingue titular/suplente (documentado): tarjetas a suplentes con nombre cuentan; la casa solo dice "sin cuerpo tecnico".
5. BAJO - variantes de nombre ("J. Smith"/"John Smith") se tratan como dos jugadores: 2A pasan a 2 pts en vez de 3; 2A+R pueden dar 4 hasta tope 3 (aqui el tope por jugador no lo evita al ser dos claves). Nombres iguales de dos jugadores del mismo equipo se fusionan (excepcional).
6. BAJO - (2,0) (16 jugadores): si el proveedor clasifico mal y no hubo expulsion, se sobrestima en 1. Irrelevante en volumen.
7. Sin errores de signo o de reparto local/visitante en `_val`/`atoms` (own/opp, hándicap visitante +1.5, totales).
8. Aviso de mercado: la liquidacion real de una casa puede usar otra metrica (n.o de tarjetas, puntos 10/25...). La regla A=1, R=2 (tope 3) solo vale si esa casa ofrece esa linea; hoy ninguna fuente publica estas cuotas.

### 6.3 Sesgos de la cuota estimada y de la "linea mas ajustada"
- Circularidad: cuota = 1/(p_est*1.08) con p_est calculada de la misma muestra que el apoyo; p_est*cuota = 1/1.08 siempre, de modo que el EV descriptivo es -7.4 % por construccion en todas las filas. No indica valor ni diferencia candidatos. La "cuota REAL minima a exigir" (1/apoyo, 1.65-1.77) frente a la aproximada (1.11-1.13) compara dos funciones de la misma muestra.
- Filtro `1.10 <= est <= 2.6` descarta (no recorta) las lineas con p_est > ~0.842. Resultado: casi todas las filas salen con 1.11-1.13 (p_est ~0.83-0.84, el borde del filtro); las lineas mas seguras no aparecen y la cuota mostrada es un artefacto del umbral. En lineas muy probables (equipo mas de 2.5 corners, Menos de 14.5 corners) un mercado real podria pagar 1.03-1.09, de modo que la cuota estimada sobrestima el pago; si el margen real de corners/tarjetas es mayor que 8 % (supuesto, sin fuente) la sobrestima aun mas.
- Suavizado (k+2)/(n+4) sobre la suma de ambos equipos: con n~20 casi no encoge, mezcla local/visitante y rivales; no corrige seleccion ni heterogeneidad.
- "Linea mas ajustada que aun pasa" (`unpriced`): por (partido, mercado, alcance, sentido) elige la linea con MAYOR cuota estimada entre las de apoyo >= 0.5, es decir, el maximo sobre una escalera de lineas correlacionadas, justo donde el ruido muestral cruza el umbral. Es maldicion del ganador: la frecuencia en la linea elegida esta inflada, y despues se ordena por apoyo (segunda seleccion). Los candidatos (apoyo Wilson 0.57-0.61, 9/10-10/10) no equivalen a probabilidad del 80-100 %.
- Con cuota real (--manual-odds) se sustituye `cuota_media` pero no la linea elegida (sigue siendo la "mas ajustada" segun la estimada).
- Recomendaciones: (1) mostrar la escalera completa (el CSV ya la tiene) y no solo el maximo; (2) no calcular EV sobre una cuota derivada de la propia frecuencia; (3) presentar estas filas como "candidatas sin precio: exigir X en la casa"; (4) marcar "linea trivial" en vez de descartar por el suelo 1.10; (5) exigir mayor apoyo a la linea elegida entre N lineas o validar fuera de muestra; (6) aislar el respaldo de estadisticas agregadas con marca de definicion distinta.

## 7. Limitaciones
- Cuotas = medianas de agregador, sin casa verificada; el lado opuesto puede ser de otras casas (novig aproximado).
- El EV con p de mercado asume mercado calibrado: es referencia, no estimacion propia.
- Independencia entre partidos y correlacion entre tickets calculadas bajo ese supuesto.
- Alineaciones/bajas no verificadas aqui (analisis deportivo). No se consulto API ni fuentes externas.
