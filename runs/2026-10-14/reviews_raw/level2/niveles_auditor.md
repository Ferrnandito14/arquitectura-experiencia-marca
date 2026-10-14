# Auditoría adversarial de borradores por niveles (14-oct-2026)

Alcance: 8 borradores de `tickets.json` (seguridad ×1.2: T1-T3; x3: T1-T2; amplio ×4: T1-T3). Consulta: 2026-10-14 ~01:20-01:40 UTC (antes de cualquier inicio). Regla: informo riesgos; no emito «no apostar» ni uso EV de mercado como veredicto. El usuario decide.

Aviso de insumos: `runs/2026-10-14/reviews_raw/` no existía (no hay informes previos que leer); solo `tickets.json`, `inventory.json`, `rotation.json`, `candidatos_estadisticos.csv`, `tickets.py` y apif_query.py.

## 0. Hallazgos transversales

| # | Hallazgo | Evidencia / verificación | Impacto |
|---|---|---|---|
| A | Todas las cuotas son «promedio_de_mercado» de apifootball (4-7 casas). Ninguna es de una sola casa. El mejor precio individual difiere según la casa (p. ej. Betano/Pinnacle arriba, Marathon abajo); un ticket de 2-5 patas no existe a la cuota media en una sola casa. | Recalculé por casa con `get_odds` (26 patas). Ej.: Cincinnati o1.5 media 1.097 (máx 1.12 Pncl, mín 1.06 Marathon); Dallas AH+1.5 media 1.350 (1.30-1.39); Miami AH+1.5 media 1.641 (1.60-1.70). Las medias reproducen `tickets.json`. | Medio |
| B | Muestras e insumos de una sola procedencia (apifootball), `n`=10 por equipo, mezcla casa+fuera, últimos 10 de la misma competición. Calendario sí con 2 fuentes (apifootball+apwin), pero cuotas/estadísticas no se contrastaron con un segundo proveedor (protocolo pide ≥2 fuentes de cuotas y ≥3 fichas). | Reconstruí k/n con `get_events team_id=` (mismo proveedor, no independiente): reproduce `frec` en las 13 patas revisadas (sección 3). | Medio |
| C | Brecha ≥15 pp: el filtro estándar es 0.15, pero x3/x4 admiten patas con brecha 0.18-0.34 por nivel «explícito/alto». `top_picks` marca como `sospechosa_por_brecha` varias patas AH que aparecen en los tickets. Con n=10, `p_central` encoge con m=40: p_central ≈ 85-90 % mercado, así que EV central>0 es un artefacto de la mezcla, no evidencia. | `tickets.py`: `SHRINK_M=40`, `MAX_GAP=0.15`. Brechas por pata: LA-Austin +0.336, Miami AH +0.329, Dallas +0.312, LA Galaxy +0.239, Bryne +0.223, Santa Fe +0.218. | Alto en x3/x4 |
| D | Bajas y alineaciones sin dato: `missing_players` vacío y once vacío en 25/26 patas (solo Sporting JAX tiene once 11/11). Vacío = sin información, no «sin bajas». `rotation.json` es nulo para Moss, Bryne, Columbus, Hartford, LA-Austin, Montréal, Batman, Umraniyespor, Waldhof, Wehen y Al Raed. | `get_events`/`get_lineups` apifootball; `rotation.json`. | Medio |
| E | Fechas / Caracas: las 26 patas coinciden en hora UTC con apifootball (y con el epoch de apwin en las de 2 fuentes). Ningún partido de los tickets está mal fechado. Con zona Caracas (UTC-4), los de 00:30Z y 02:30Z (St. Louis, Chicago, Dallas, LA Galaxy, LA-Austin) caen el 14-oct 20:30/22:30, no el 15; la ventana del run (04:00Z-04:00Z) los incluye. Riesgo solo si alguien filtra por fecha UTC (rotation.json los rotula «2026-10-15»). Aragua-Caracas (Copa Venezuela, 20:00Z) es el único partido con «Caracas» y no está en ningún ticket. Tool: en mi tanda las llamadas `timezone=America/Caracas` de ~15 partidos devolvieron la hora UTC sin convertir; al repetirlas sueltas (Cincinnati, Santa Fe, Dallas) sí convirtieron; el resto no lo reconfirmé. Usé `normalized_datetime_local` (-04:00) del inventario. | Bajo | 
| F | Strømmen-Asane: único noruego a 13:00Z (el resto a 17:00Z), y apifootball le asigna árbitro «A. Al Fahad» (nombre saudí) en una liga noruega. Posible dato contaminado de ficha; hora sí confirmada con apwin. No cambia la hora, pero resta confianza a la ficha. | `inventory.json` m-eaa3b08148fa. | Bajo |
| G | Rotación vetada de forma asimétrica: en Santa Fe-Jaguares se vetó «Visitante gana» y los Under, pero no «Hándicap visitante +2.5»; Jaguares tiene rotación ALTO (3 días de descanso, ≈4.0 cambios). En Hodd-Ranheim (local ALTO) se vetaron Under/1X, no «Más de 2.5». | `tickets.json: patas_vetadas_por_rotacion`; `rotation.json`. | Medio-alto (Santa Fe) |
| H | Clasificación por P(fallo, mercado sin margen): BAJO ≤15 %, MEDIO 15-35 %, ALTO >35 %. Ningún borrador es BAJO. | Ver tabla 1. | - |

Tabla 1. Riesgo por borrador

| Borrador | Cuota | P fallo mercado | P fallo central (encogida) | Nivel |
|---|---|---|---|---|
| seguridad T1 Cincinnati o1.5 + St. Louis o1.5 | 1.249 | 29.1 % | 21.5 % | MEDIO |
| seguridad T2 Chicago o1.5 + Strømmen o1.5 | 1.238 | 29.5 % | 23.2 % | MEDIO |
| seguridad T3 Santa Fe-Jaguares AH vis. +2.5 | 1.25 | 26.8 % | 19.5 % | MEDIO (con salvedades) |
| x3 T1 (5 patas, nivel 2) | 2.856 | 75.6 % | 63.1 % | ALTO |
| x3 T2 (5 patas, nivel 3) | 3.086 (cons. 2.933) | 76.3 % | 61.9 % | ALTO |
| amplio T1 (7 patas) | 4.173 | 85.1 % | 75.8 % | ALTO |
| amplio T2 (7 patas) | 4.163 | 84.9 % | 76.3 % | ALTO |
| amplio T3 (7 patas, 2 con cuota estimada) | 4.321 | 87.3 % | 79.5 % | ALTO |

## 1. Seguridad ×1.2

### T1: Cincinnati-NE o1.5 (1.10) + St. Louis-Vancouver o1.5 (1.135)
- Objeción principal: no es «seguridad»; cada pata paga ~10-13 % con ~15-17 % de fallo de mercado (0.855 y 0.829). Cincinnati tiene brecha 0.145, a 0.5 pp del descarte (0.15): el 20/20 empuja la pata al límite del filtro. Impacto alto sobre la lectura «segura», medio sobre la decisión.
- Secundarias: (a) local Cincinnati rota ≈4.3 cambios con 4 días de descanso (nivel medio) y Vancouver ≈3.3; (b) k/n verificado: Cincinnati 10/10 y NE 10/10; St. Louis 10/10, Vancouver 9/10 (fallo 0-1 vs Houston, 20-ago); (c) Cincinnati max-casa 1.12 vs mín 1.06, el ticket a medias de casas no existe en una sola; (d) sin once ni bajas (D).
- Dato que la resolvería: once confirmado ~1 h antes (23:30Z / 00:30Z) y cuota de la casa objetivo.
- Veredicto sugerido (no vinculante): riesgo MEDIO aceptable si se acepta ~29 % de fallo; no debe presentarse como «seguridad».
- Alternativa: sustituir Cincinnati por Moss-Egersund o1.5 (1.10; 20/20, sin rotación medida, brecha 0.150 en el borde) no mejora; mejor Hartford-Charleston o1.5 (1.20; P fallo 22.6 %) como pata única en rango 1.2.

### T2: Chicago-Philadelphia o1.5 (1.115) + Strømmen-Asane o1.5 (1.11)
- Objeción principal: Strømmen-Asane es la ficha más dudosa (árbitro saudí, único noruego a 13:00Z); además descanso corto (3 días) en ambos con Asane ≈3.3 cambios (nivel medio). Impacto medio.
- Secundarias: k/n verificado: Chicago 9/10 (fallo 0-1 vs Charlotte, 26-sep), Philadelphia 10/10, Strømmen 10/10, Asane 9/10 (fallo 1-0 vs Stromsgodset). Es el partido que primero empieza (13:00Z), así que el ticket se liquida con horas de separación y no se puede ajustar con once de la otra pata.
- Dato: hora oficial (federación noruega) y once.
- Veredicto: MEDIO, ligeramente peor que T1 por ficha dudosa.
- Alternativa: Strømmen -> Toronto-Orlando o1.5 (1.105; 19/20; Orlando rota ≈4.3, nivel medio); multiplicador 1.232 en rango.

### T3: Santa Fe-Jaguares AH visitante +2.5 (1.25)
- Objeción principal: es una pata única que depende de Jaguares, con rotación ALTO (3 días de descanso, ≈4.0 cambios). El proyecto vetó «Visitante gana» y los Under por esa causa, pero no este hándicap (G): criterio inconsistente. Impacto alto.
- Secundarias: (a) brecha 0.218 (>15 pp): muestra 19/20 vs mercado 73.2 %; (b) cuotas más viejas: apifootball marca 2026-10-13 21:19 para este partido frente a 2026-10-14 03:19 en el resto (≈6 h de antigüedad relativa), y solo 4 casas (media 1.248; 1.22-1.27); (c) k/n: Santa Fe 9/10 (fallo: ganó 4-1 a Alianza fuera, 19-sep), Jaguares 10/10; (d) sin árbitro, sin once; (e) HA +2.5 pierde si Santa Fe gana por 3+, escenario que el mercado pone en ~27 %.
- Dato: once de Jaguares (si rota, el riesgo sube) y cuotas actualizadas en ≥2 casas.
- Veredicto: MEDIO por cifras, pero el factor rotación empuja hacia MEDIO-ALTO. Sin alternativa en rango dentro de `reemplazos` (lista vacía).
- Alternativa del pool (cuota única en 1.20-1.28 sin rotación ALTO): Hartford-Charleston o1.5 1.20 (P fallo 22.6 %, 18/20, brecha 0.126, rotación sin dato) o Batman-Istanbulspor o1.5 1.20 (P fallo 23.1 %, 17/19). Es sustitución propuesta, no recomendación de apostar.

## 2. x3

### T1 (nivel 2): Moss o1.5 1.10 + QPR u4.5 1.13 + LA Galaxy AH+1.5 1.295 + Bryne u4.5 1.37 + Columbus AH+1.5 1.295
- Objeción principal: Bryne-Raufoss u4.5 (1.37): mercado 67.7 % (P fallo 32 %). Raufoss 8/10; sus dos fallos son 7-2 (Haugesund, 9-ago) y 9-1 (Kongsvinger, 5-sep): cola de goles que la media 18/20 oculta. Brecha 0.223 por una pata que paga más porque el mercado ve riesgo. Impacto alto.
- Secundarias: (a) tres patas con brecha ≥ 0.17 (QPR 0.170, Columbus 0.180, Bryne, LA Galaxy 0.239): n=10 con 100 % no es evidencia de que el mercado se equivoque; (b) QPR rotación medio PROVISIONAL, con partido a 18:45Z entre dos que ya han jugado hace 4 días; (c) AH de LA Galaxy y Columbus solo en 4 casas; Columbus 8/10 (3-0 vs Colorado, 0-2 vs Montréal); (d) 5 patas ≈ 5 eventos independientes: P éxito 24.4 % (mercado); (e) Moss y QPR, Bryne sin dato de rotación (D).
- Dato: segundo proveedor de cuotas de Bryne u4.5 y alineación.
- Veredicto: ALTO.
- Alternativa: Bryne u4.5 -> Montréal-Atlanta u4.5 1.22 (18/20; P fallo 23.1 %; brecha 0.131), multiplicador baja a ≈2.54 (fuera de rango 2.8-3.3). Dentro de rango la única sustitución del pool es Dallas AH+1.5 (1.365; 20/20), con P fallo 31 % y brecha 0.312: cambia una cola por otra.

### T2 (nivel 3): Dallas AH+1.5 1.365 + Moss o1.5 1.10 + Sarmiento-River o0.5 1.065 + Miami-NYC u5.5 1.17 + Miami-NYC AH+1.5 1.65 (1.93 combinado)
- Objeción principal: la pata doble de Inter Miami-NYC se cotiza como producto (1.17×1.65=1.93) pero u5.5 y AH+1.5 visitante están correlacionados positivamente (ambas fallan en una goleada local, p. ej. Miami 7-1 vs Montréal, 29-ago). Una casa que ofrezca combinada del mismo partido cotizará por debajo de 1.93, o la rechazará; el ticket real queda por debajo de 3.086 y puede salir de 2.8-3.3. Además AH Miami tiene brecha 0.329 y Miami 8/10 (7-1 y 4-0 vs DC el 10-oct). Impacto alto.
- Secundarias: (a) Dallas AH brecha 0.312 con n=20 de 100 %: Seattle 10/10 verificado (sin derrotas por 2+ en sus últimos 10 de MLS), Dallas 10/10 (sin victorias por 2+, pero encaja 5-0 vs Vancouver el 23-ago); (b) Moss repite con T1 del mismo perfil (si ambos se juegan, un solo resultado hunde a los dos); (c) Sarmiento o0.5 a 1.065 paga 6.5 % con 12.5 % de fallo de mercado: la pata de peor relación; (d) rotación medio PROVISIONAL en Miami; (e) justificación de `tickets.json` reconoce que el apoyo conjunto 0.606 (Wilson) se contrasta con 0.369 de producto: no es probabilidad.
- Dato: ¿la casa acepta Under 5.5 + AH+1.5 del mismo partido y a qué cuota final?
- Veredicto: ALTO; la cuota 3.086 es la menos ejecutable del lote.
- Alternativa: Sarmiento o0.5 -> Comunicaciones-Aurora o0.5 (1.035; 4 casas 1.03-1.06; 0 empates 0-0 en los últimos 10 de cada equipo; verificado en apifootball) deja el ticket en 2.85 (en rango) y baja el fallo de esa pata de 12.5 % a ~3-9 %. Quitar la pata doble de Miami exigiría reponer ≈1.9 de multiplicador; sin alternativa en rango con baja brecha.

## 3. Verificación de muestras (k/n reproducidos, mismo proveedor)

| Pata | k/n local | k/n visitante | Notas |
|---|---|---|---|
| Cincinnati o1.5 | 10/10 (casa 4/4) | 10/10 | ok |
| St. Louis o1.5 | 10/10 | 9/10 | fallo 0-1 |
| Chicago o1.5 | 9/10 | 10/10 | fallo 0-1 |
| Strømmen o1.5 | 10/10 | 9/10 | fallo 1-0 |
| Santa Fe AH vis.+2.5 | 9/10 | 10/10 | Santa Fe ganó 4-1 fuera |
| Moss o1.5 | 10/10 | 10/10 | ok |
| QPR u4.5 | 10/10 | 10/10 | ok |
| LA Galaxy AH+1.5 | 10/10 | 9/10 | fallo SJ 3-1 Portland |
| Bryne u4.5 | 10/10 | 8/10 | 7-2 y 9-1 |
| Columbus AH+1.5 | 8/10 | 10/10 | 3-0, 0-2 |
| Dallas AH+1.5 | 10/10 | 10/10 | - |
| Miami u5.5 | 9/10 | 10/10 | 7-1 |
| Miami AH+1.5 | 8/10 | 10/10 | 7-1, 4-0 |

## 4. Amplio ×4 (patas comunes)
Riesgos comunes: 6-7 patas, P éxito 12.7-15.1 % (mercado); Toronto o1.5 (nivel medio, Orlando ≈4.3 cambios) y LA-Austin AH+1.5 (brecha 0.336, `sospechosa_por_brecha`, 9/10 y 9/10 contra mercado 56.4 %) están en los tres. LA-Austin: sin dato de rotación y solo precio 1.65 con 6 casas; el desacuerdo muestra-mercado de 34 pp indica que el mercado valora algo que las últimas 10 jornadas no capturan (forma o plantilla); sin alternativa en `reemplazos`.

### T1: Toronto o1.5, JAX u5.5, DC u5.5, Bohemians o1.5, Hartford o1.5, LA-Austin AH, Hodd o2.5
- Objeción principal: tres Under 5.5 / over 1.5 con rotación PROVISIONAL medio (JAX, DC con local ≈5.7 cambios, Bohemians ≈5.3-5.7 cambios) más Hodd-Ranheim, cuyo local tiene rotación ALTO (3 días, ≈4.0 cambios) y cuyos Under/1X se vetaron pero «Más de 2.5» sigue dentro (G). Impacto alto.
- Secundarias: Bohemians o1.5 y Hartford o1.5 con 18/20 (min equipo 0.49); Hodd o2.5 18/20 con brecha 0.181 y cuota 1.29; nivel 3 ya rotulado.
- Dato: once de Hodd y Bohemians; cuotas Hodd en segunda fuente.
- Veredicto: ALTO. Alternativa: `reemplazos` solo ofrece para Hodd córners de Stabaek con precio estimado (no ejecutable); con precio real, Comunicaciones-Aurora o0.5 (1.035) sustituye a Hodd (1.29) y deja el ticket en ≈3.35 (fuera de rango 4.0-4.8), con P fallo de esa pata de ~28 % a ~3-9 %.

### T2: Toronto, Bohemians u4.5, Hartford, LA-Austin, Montréal u4.5, Batman o1.5, Umraniyespor u4.5
- Objeción principal: 7 patas, P fallo 84.9 %; Batman-Istanbulspor tiene n=[9,10] (una muestra con partido faltante) y el resto 18/20; Batman empieza a las 11:30Z, así que sus resultados llegan casi 12 h antes del resto y no hay margen para reaccionar a cambios. Impacto medio.
- Secundarias: dos turcos (Batman, Umraniye) sin dato de rotación ni once; Bohemians u4.5 rotación PROVISIONAL medio.
- Veredicto: ALTO. Alternativa (de `reemplazos`): Montréal u4.5 -> Antalyaspor-Kayserispor o0.5 (1.04, apoyo 0.701) o Stabaek-Sandnes o1.5 (1.06, apoyo 0.659); el multiplicador baja a ≈3.5, fuera de rango.

### T3: Toronto, Bohemians u4.5, Waldhof u14.5 córners, Wehen u12.5 córners, Al Raed u4.5, LA-Austin, Hodd + Batman
- Objeción principal: dos patas de córners con cuota ESTIMADA POR MODELO (1.11, n_casas=0, minmax [1.11,1.11], prob 0.8333): no existen en ninguna casa verificada, y la «brecha» es circular (precio derivado del propio modelo). El ticket de 4.321 no es ejecutable tal cual. Impacto alto (descarte de la pata, no del ticket entero).
- Secundarias: n_recientes=8 en ambas; la línea .5 sí (14.5 / 12.5) pero no se verificó si el mercado es partido completo; Al Raed-Jeddah sin árbitro/rotación y solo 4 casas; Waldhof/Wehen empiezan a la vez (17:00Z), correlación temporal sin efecto estadístico.
- Dato: precio real en una casa de las líneas de córners; si no existe, la pata no se puede liquidar.
- Veredicto: ALTO, el más débil del lote por ejecutabilidad.
- Alternativa del pool con precio real: Waldhof/Wehen -> Comunicaciones-Aurora o0.5 (1.035) y Mezőkövesd-Ajka o0.5 (1.03, 5 casas, 0 empates 0-0 en los últimos 10 de cada equipo; `reemplazos` de T3); el multiplicador cae a ≈3.7, fuera de rango. Umraniyespor/Montréal u4.5 ya están en T2 (repetiría partidos entre tickets).

## 5. Registro de fuentes

| Fuente | URL/ficha | Dato buscado | Resultado | Estado | Valor | Discrepancias | Alternativa |
|---|---|---|---|---|---|---|---|
| apifootball (apif_query get_events) | match_id de 26 patas, tz UTC y Caracas | hora, estado, árbitro, bajas | horas coinciden con tickets.json; árbitros solo en parte; sin bajas/once salvo JAX | Consultada y útil | Alto para fecha | Caracas: conversión inconsistente en tanda (ver E) | inventario `normalized_datetime_local` |
| apifootball (get_odds) | 26 patas | precio por casa | medias reproducen `cuota_media`; máx/mín por casa | Consultada y útil | Alto | Santa Fe 2026-10-13 21:19 vs resto 2026-10-14 03:19 | - |
| apifootball (get_events team_id) | 13 patas | k/n de la muestra | reproducido (no independiente) | Consultada y útil | Medio | - | - |
| apwin | `inventory.json` epoch | hora | coincide en 2 fuentes | Consultada (vía inventario) | Medio | - | - |
| OddsPortal, Oddschecker, Flashscore, Transfermarkt, prensa/club | - | cuotas independientes, bajas, once | No consultadas (sin tiempo/acceso en esta pasada) | No consultada | - | - | pendiente |

## 6. Objeciones pendientes para ronda 2 (propongo estado)
- Fechas/Caracas (E): resuelta, sin error de fecha en los tickets.
- Rotación Santa Fe/Jaguares (G): motivo de reevaluar T3 (riesgo aceptado solo si hay once).
- Cuota combinada Miami (x3 T2): riesgo no resuelto hasta ver precio de la casa.
- Córners estimados (amplio T3): motivo de sustituir las 2 patas.
- Cuotas medias vs una casa (A): riesgo aceptado, a verificar en la casa objetivo.
- Bajas/once (D): riesgo aceptado hasta ~1 h antes de cada inicio.
