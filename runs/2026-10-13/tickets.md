# Tickets provisionales por multiplicador objetivo

> **Cuotas = promedio de ≥3 casas vía agregador (NO ejecutables); la casa recalcula las combinadas del mismo partido (cuota real menor). Apoyo = frecuencia descriptiva conservadora (Wilson inferior), NO probabilidad predictiva ni EV.** Entre partidos distintos el producto supone independencia. Las cuotas de cada pata son la MEDIANA entre casas; «conservadora» descuenta un 5 % a cada par del mismo partido y debe seguir ≥ el mínimo del rango más un colchón. Contrastar con la cuota REAL de la casa y con el Nivel 2 (bajas, alineaciones, 2.ª fuente de calendario) antes de apostar. **Regla: un partido no puede aparecer en dos tickets** (si falla en uno, no arrastra al otro): TODOS los borradores de un perfil excluyen los partidos de TODOS los borradores de los perfiles anteriores: escojas el que escojas de cada multiplicador, no comparten partido. Dos patas del mismo partido solo entran con justificación medida (apoyo conjunto sobre los mismos partidos pasados). Las patas de los tickets exigen **calendario confirmado por dos fuentes independientes** (hora del partido) y excluyen categorías juvenil/sub-23/reserva (plantillas rotativas); los rankings top lo marcan en columnas.

> **Puertas de calidad de datos.** (1) Veracidad: 28 mercados bloqueados automáticamente por avisos graves de los agentes (cifras defectuosas/imposibles/sospechosas). (2) Representatividad: 2633 patas con historial MIXTO (otra competición, copas, pretemporada) quedan fuera de los tickets y rankings principales; las de Champions pasan a las variantes `*_champions`, rotuladas de menor respaldo.

## Ranking general — familia ×1.2–1.28 (seguridad) (de primero a último)

Criterio: mayor apoyo conjunto descriptivo; a igual apoyo, menor distancia al equilibrio 1/cuota. Un margen negativo = la frecuencia histórica no cubre lo que paga el ticket. NO es EV real.

| Puesto | Perfil | Borrador | Cuota (cons.) | Patas | Apoyo conjunto | Equilibrio 1/cuota | Margen |
|---|---|---|---|---|---|---|---|
| 1 | seguridad | 1 | ×1.282 (1.218) | 2 | 0.722 | 0.821 | -0.099 |
| 2 | seguridad | 2 | ×1.25 (1.25) | 1 | 0.712 | 0.8 | -0.088 |
| 3 | seguridad | 3 | ×1.25 (1.25) | 1 | 0.659 | 0.8 | -0.141 |
| 4 | seguridad | 4 | ×1.22 (1.22) | 1 | 0.659 | 0.82 | -0.161 |
| 5 | seguridad_champions | 1 | ×1.235 (1.235) | 1 | 0.606 | 0.81 | -0.204 |
| 6 | seguridad_champions | 2 | ×1.25 (1.25) | 1 | 0.496 | 0.8 | -0.304 |
| 7 | seguridad | 5 | ×1.265 (1.265) | 2 | 0.476 | 0.791 | -0.315 |
| 8 | seguridad_champions | 3 | ×1.265 (1.265) | 2 | 0.438 | 0.791 | -0.353 |
| 9 | seguridad_champions | 4 | ×1.229 (1.229) | 2 | 0.421 | 0.814 | -0.393 |
| 10 | seguridad_champions | 5 | ×1.264 (1.264) | 2 | 0.392 | 0.791 | -0.399 |
| 11 | usuario (cuota informada, no verificada) | — | ×1.27 | 2 | 0.265 | 0.787 | -0.522 |

## Ranking general — familia ×4.0–4.8 (amplio) (de primero a último)

Criterio: mayor apoyo conjunto descriptivo; a igual apoyo, menor distancia al equilibrio 1/cuota. Un margen negativo = la frecuencia histórica no cubre lo que paga el ticket. NO es EV real.

| Puesto | Perfil | Borrador | Cuota (cons.) | Patas | Apoyo conjunto | Equilibrio 1/cuota | Margen |
|---|---|---|---|---|---|---|---|
| 1 | amplio_champions | 1 | ×4.205 (4.205) | 4 | 0.079 | 0.238 | -0.159 |
| 2 | amplio | 1 | ×4.273 (4.273) | 5 | 0.076 | 0.234 | -0.158 |
| 3 | amplio | 2 | ×4.21 (4.21) | 6 | 0.053 | 0.238 | -0.185 |
| 4 | amplio | 3 | ×4.22 (4.22) | 6 | 0.045 | 0.237 | -0.192 |

## Perfil «seguridad»: ×1.2–1.28 (≤2 patas, apoyo mínimo por ítem 0.65, colchón 1 %) — 5 borradores

### Puesto 1 · Borrador 1: ×1.282 (conservadora ×1.218) · 2 pata(s) en 1 partido(s) · apoyo conjunto descriptivo 0.722 (implícita de mercado sin margen 0.661)

| Partido | Inicio UTC | Selección | Cuota media (mín–máx, casas) | Apoyo cons. | n |
|---|---|---|---|---|---|
| Birmingham City – Preston North End (efl championship) | 2026-10-13T19:00:00Z | Hándicap visitante +2.5 ⚑ | 1.125 (1.11–1.18, 4) | 0.722 (mín. equipo 0.722) | 10/10 |
| Birmingham City – Preston North End (efl championship) | 2026-10-13T19:00:00Z | Menos de 4.5 goles ⚑ | 1.14 (1.12–1.18, 7) | 0.722 (mín. equipo 0.722) | 10/10 |
| ⚑ *dos patas del mismo partido (cuota combinada media 1.282; la casa suele pagar menos).* Conjunto medido en los mismos partidos pasados: local 1.0 (n=10), visitante 1.0 (n=10); apoyo conservador conjunto 0.722 (límite inferior de Wilson; techo 0.722 con n=10), frente a 0.521 como producto de los apoyos individuales (0.722 × 0.722). Referencia descriptiva: no prueba dependencia ni es una probabilidad. Reevaluación de agentes: deportivo, cuantitativo y auditor: ACEPTABLE CON SALVEDADES (ninguno lo ve defendible; EV de modelo ≈ −4 % a −9 %). Condición: exigir cuota real del combinado ≥1.20 y mirar alineaciones; el +2.5 tiene solo 4 casas (1xBet y Marathon repiten precio). Si la casa paga menos de 1.20, es mejor la pata simple Menos de 4.5 (×1.14). | | | | | |

### Puesto 2 · Borrador 2: ×1.25 (conservadora ×1.25) · 1 pata(s) en 1 partido(s) · apoyo conjunto descriptivo 0.712 (implícita de mercado sin margen 0.752)

| Partido | Inicio UTC | Selección | Cuota media (mín–máx, casas) | Apoyo cons. | n |
|---|---|---|---|---|---|
| Cardiff City – Watford (efl championship) | 2026-10-13T18:45:00Z | Menos de 4.5 goles | 1.25 (1.2–1.27, 7) | 0.712 (mín. equipo 0.701) | 9/10 |

### Puesto 3 · Borrador 3: ×1.25 (conservadora ×1.25) · 1 pata(s) en 1 partido(s) · apoyo conjunto descriptivo 0.659 (implícita de mercado sin margen 0.754)

| Partido | Inicio UTC | Selección | Cuota media (mín–máx, casas) | Apoyo cons. | n |
|---|---|---|---|---|---|
| Atlético Bucaramanga – Águilas Doradas (categoria primera a) | 2026-10-13T23:30:00Z | Local o empate (1X) | 1.25 (1.16–1.27, 8) | 0.659 (mín. equipo 0.596) | 10/10 |

### Puesto 4 · Borrador 4: ×1.22 (conservadora ×1.22) · 1 pata(s) en 1 partido(s) · apoyo conjunto descriptivo 0.659 (implícita de mercado sin margen 0.75)

| Partido | Inicio UTC | Selección | Cuota media (mín–máx, casas) | Apoyo cons. | n |
|---|---|---|---|---|---|
| Pendikspor – Van BB (1 lig) | 2026-10-13T17:00:00Z | Más de 1.5 goles | 1.22 (1.21–1.27, 7) | 0.659 (mín. equipo 0.596) | 10/10 |

### Puesto 5 · Borrador 5: ×1.265 (conservadora ×1.265) · 2 pata(s) en 2 partido(s) · apoyo conjunto descriptivo 0.476 (implícita de mercado sin margen 0.666)

| Partido | Inicio UTC | Selección | Cuota media (mín–máx, casas) | Apoyo cons. | n |
|---|---|---|---|---|---|
| Harju Jalgpallikool – Nõmme United (meistriliiga) | 2026-10-13T15:00:00Z | Menos de 5.5 goles | 1.1 (1.07–1.14, 5) | 0.722 (mín. equipo 0.722) | 10/10 |
| Durban City – AmaZulu (premier soccer league) | 2026-10-13T17:30:00Z | Menos de 3.5 goles | 1.15 (1.11–1.17, 6) | 0.659 (mín. equipo 0.596) | 10/10 |

## Perfil «amplio»: ×4.0–4.8 (≤6 patas, apoyo mínimo por ítem 0.55, colchón 4 %) — 3 borradores

### Puesto 1 · Borrador 1: ×4.273 (conservadora ×4.273) · 5 pata(s) en 5 partido(s) · apoyo conjunto descriptivo 0.076 (implícita de mercado sin margen 0.156)

| Partido | Inicio UTC | Selección | Cuota media (mín–máx, casas) | Apoyo cons. | n |
|---|---|---|---|---|---|
| Athletic-MG – Londrina (serie b) | 2026-10-13T22:30:00Z | Más de 1.5 goles | 1.36 (1.35–1.4, 7) | 0.606 (mín. equipo 0.49) | 10/10 |
| San Carlos – Inter San Carlos (primera division fpd) | 2026-10-14T02:00:00Z | Menos de 3.5 goles | 1.3 (1.29–1.32, 6) | 0.606 (mín. equipo 0.49) | 10/10 |
| Sariyer – Bodrumspor (1 lig) | 2026-10-13T14:00:00Z | Menos de 3.5 goles | 1.27 (1.23–1.29, 7) | 0.606 (mín. equipo 0.49) | 10/10 |
| Bristol City – Blackburn Rovers (efl championship) | 2026-10-13T18:45:00Z | Hándicap visitante +1.5 | 1.22 (1.2–1.36, 7) | 0.606 (mín. equipo 0.49) | 10/10 |
| Rot-Weiss Essen – Fortuna Köln (3 liga) | 2026-10-13T17:00:00Z | Hándicap visitante +1.5 | 1.56 (1.43–1.6, 6) | 0.562 (mín. equipo 0.529) | 10/8 |

### Puesto 2 · Borrador 2: ×4.21 (conservadora ×4.21) · 6 pata(s) en 6 partido(s) · apoyo conjunto descriptivo 0.053 (implícita de mercado sin margen 0.142)

| Partido | Inicio UTC | Selección | Cuota media (mín–máx, casas) | Apoyo cons. | n |
|---|---|---|---|---|---|
| Workington – Whitby Town (northern premier league) | 2026-10-13T18:45:00Z | Más de 1.5 goles | 1.135 (1.11–1.2, 4) | 0.659 (mín. equipo 0.596) | 10/10 |
| FUS Rabat – Raja Casablanca (botola pro) | 2026-10-13T20:00:00Z | Menos de 3.5 goles | 1.135 (1.12–1.17, 6) | 0.659 (mín. equipo 0.596) | 10/10 |
| Athletic-MG – Londrina (serie b) | 2026-10-13T22:30:00Z | Más de 1.5 goles | 1.36 (1.35–1.4, 7) | 0.606 (mín. equipo 0.49) | 10/10 |
| San Carlos – Inter San Carlos (primera division fpd) | 2026-10-14T02:00:00Z | Menos de 3.5 goles | 1.3 (1.29–1.32, 6) | 0.606 (mín. equipo 0.49) | 10/10 |
| Chippenham Town – Frome Town (southern league premier south) | 2026-10-13T18:45:00Z | Más de 1.5 goles | 1.185 (1.17–1.22, 4) | 0.596 (mín. equipo 0.49) | 9/10 |
| Rot-Weiss Essen – Fortuna Köln (3 liga) | 2026-10-13T17:00:00Z | Hándicap visitante +1.5 | 1.56 (1.43–1.6, 6) | 0.562 (mín. equipo 0.529) | 10/8 |

### Puesto 3 · Borrador 3: ×4.22 (conservadora ×4.22) · 6 pata(s) en 6 partido(s) · apoyo conjunto descriptivo 0.045 (implícita de mercado sin margen 0.143)

| Partido | Inicio UTC | Selección | Cuota media (mín–máx, casas) | Apoyo cons. | n |
|---|---|---|---|---|---|
| Workington – Whitby Town (northern premier league) | 2026-10-13T18:45:00Z | Más de 1.5 goles | 1.135 (1.11–1.2, 4) | 0.659 (mín. equipo 0.596) | 10/10 |
| Athletic-MG – Londrina (serie b) | 2026-10-13T22:30:00Z | Más de 1.5 goles | 1.36 (1.35–1.4, 7) | 0.606 (mín. equipo 0.49) | 10/10 |
| Sariyer – Bodrumspor (1 lig) | 2026-10-13T14:00:00Z | Menos de 3.5 goles | 1.27 (1.23–1.29, 7) | 0.606 (mín. equipo 0.49) | 10/10 |
| Wrexham – West Bromwich (efl championship) | 2026-10-13T18:45:00Z | Hándicap visitante +1.5 | 1.15 (1.15–1.2, 5) | 0.596 (mín. equipo 0.596) | 10/10 |
| Rot-Weiss Essen – Fortuna Köln (3 liga) | 2026-10-13T17:00:00Z | Hándicap visitante +1.5 | 1.56 (1.43–1.6, 6) | 0.562 (mín. equipo 0.529) | 10/8 |
| Al-Saqer – Al Jabalain (first division) | 2026-10-13T15:15:00Z | Menos de 3.5 goles | 1.2 (1.18–1.22, 5) | 0.55 (mín. equipo 0.49) | 6/10 |

## Perfil «seguridad_champions»: ×1.2–1.28 (≤2 patas, apoyo mínimo por ítem 0.45, colchón 1 %) — 5 borradores

### Puesto 1 · Borrador 1: ×1.235 (conservadora ×1.235) · 1 pata(s) en 1 partido(s) · apoyo conjunto descriptivo 0.606 (implícita de mercado sin margen 0.745)

| Partido | Inicio UTC | Selección | Cuota media (mín–máx, casas) | Apoyo cons. | n |
|---|---|---|---|---|---|
| Buriram United – Beijing Guoan (afc champions league) | 2026-10-13T12:15:00Z | Hándicap visitante +1.5 | 1.235 (1.21–1.27, 4) | 0.606 (mín. equipo 0.49) | 10/10 |

### Puesto 2 · Borrador 2: ×1.25 (conservadora ×1.25) · 1 pata(s) en 1 partido(s) · apoyo conjunto descriptivo 0.496 (implícita de mercado sin margen 0.749)

| Partido | Inicio UTC | Selección | Cuota media (mín–máx, casas) | Apoyo cons. | n |
|---|---|---|---|---|---|
| Atlético Madrid – Manchester United (uefa champions league) | 2026-10-13T19:00:00Z | Menos de 4.5 goles | 1.25 (1.22–1.28, 6) | 0.496 (mín. equipo 0.397) | 10/10 |

### Puesto 3 · Borrador 3: ×1.265 (conservadora ×1.265) · 2 pata(s) en 2 partido(s) · apoyo conjunto descriptivo 0.438 (implícita de mercado sin margen 0.681)

| Partido | Inicio UTC | Selección | Cuota media (mín–máx, casas) | Apoyo cons. | n |
|---|---|---|---|---|---|
| Al Sadd – Al Hilal (afc champions league) | 2026-10-13T16:00:00Z | Más de 1.5 goles | 1.1 (1.08–1.14, 7) | 0.722 (mín. equipo 0.722) | 10/10 |
| Lens – Sporting (uefa champions league) | 2026-10-13T16:45:00Z | Más de 1.5 goles | 1.15 (1.14–1.19, 6) | 0.606 (mín. equipo 0.49) | 10/10 |

### Puesto 4 · Borrador 4: ×1.229 (conservadora ×1.229) · 2 pata(s) en 2 partido(s) · apoyo conjunto descriptivo 0.421 (implícita de mercado sin margen 0.697)

| Partido | Inicio UTC | Selección | Cuota media (mín–máx, casas) | Apoyo cons. | n |
|---|---|---|---|---|---|
| RB Leipzig – PSV (uefa champions league) | 2026-10-13T19:00:00Z | Más de 1.5 goles | 1.055 (1.04–1.11, 6) | 0.722 (mín. equipo 0.722) | 10/10 |
| Sabah – Slavia Praha (uefa champions league) | 2026-10-13T16:45:00Z | Menos de 4.5 goles | 1.165 (1.14–1.21, 6) | 0.583 (mín. equipo 0.49) | 8/10 |

### Puesto 5 · Borrador 5: ×1.264 (conservadora ×1.264) · 2 pata(s) en 2 partido(s) · apoyo conjunto descriptivo 0.392 (implícita de mercado sin margen 0.688)

| Partido | Inicio UTC | Selección | Cuota media (mín–máx, casas) | Apoyo cons. | n |
|---|---|---|---|---|---|
| Villarreal – Napoli (uefa champions league) | 2026-10-13T19:00:00Z | Menos de 5.5 goles | 1.045 (1.01–1.09, 6) | 0.722 (mín. equipo 0.722) | 10/10 |
| Arsenal – Lille (uefa champions league) | 2026-10-13T19:00:00Z | Menos de 4.5 goles | 1.21 (1.2–1.24, 6) | 0.543 (mín. equipo 0.49) | 10/10 |

## Perfil «amplio_champions»: ×4.0–4.8 (≤6 patas, apoyo mínimo por ítem 0.45, colchón 4 %) — 1 borradores

**Solo existe 1 borrador distinto con las patas disponibles** (se pidieron varios para poder escoger): ampliar patas, bajar el apoyo mínimo o aportar cuotas reales.

### Puesto 1 · Borrador 1: ×4.205 (conservadora ×4.205) · 4 pata(s) en 4 partido(s) · apoyo conjunto descriptivo 0.079 (implícita de mercado sin margen 0.183)

| Partido | Inicio UTC | Selección | Cuota media (mín–máx, casas) | Apoyo cons. | n |
|---|---|---|---|---|---|
| Kyoto Sanga – Ratchaburi (afc champions league) | 2026-10-13T10:00:00Z | Hándicap visitante +1.5 | 1.68 (1.65–1.72, 6) | 0.659 (mín. equipo 0.596) | 10/10 |
| Viking – Bayern München (uefa champions league) | 2026-10-13T19:00:00Z | Menos de 5.5 goles | 1.4 (1.37–1.44, 6) | 0.496 (mín. equipo 0.397) | 10/10 |
| Shanghai SIPG – Daejeon Citizen (afc champions league) | 2026-10-13T10:00:00Z | Más de 1.5 goles | 1.2 (1.17–1.22, 7) | 0.496 (mín. equipo 0.397) | 10/10 |
| Galatasaray – Barcelona (uefa champions league) | 2026-10-13T19:00:00Z | Más de 3.5 goles | 1.49 (1.44–1.57, 7) | 0.49 (mín. equipo 0.49) | 10/10 |

## Top de picks por SEGURIDAD (mayor apoyo conservador; una pata por partido)

| # | Partido | Categoría | Inicio UTC | Calendario | Selección | Cuota media (mín–máx, casas) | Apoyo cons. | n | Implícita s/margen | EV desc. cons. |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | Birmingham City – Preston North End (efl championship) | men | 2026-10-13T19:00:00Z | 2 fuentes | Menos de 4.5 goles | 1.14 (1.12–1.18, 7) | 0.722 | 10/10 | 0.8143 | -0.177 |
| 2 | Harju Jalgpallikool – Nõmme United (meistriliiga) | men | 2026-10-13T15:00:00Z | 2 fuentes | Menos de 5.5 goles | 1.1 (1.07–1.14, 5) | 0.722 | 10/10 | 0.8226 | -0.206 |
| 3 | Norrköping – GIF Sundsvall (superettan) | men | 2026-10-13T17:00:00Z | 2 fuentes | Menos de 5.5 goles | 1.1 (1.08–1.14, 7) | 0.722 | 10/10 | 0.841 | -0.206 |
| 4 | Simba – Mashujaa (ligi kuu bara) | men | 2026-10-13T16:00:00Z | 2 fuentes | Gana alguno, sin empate (12) | 1.095 (1.06–1.13, 4) | 0.722 | 10/10 | 0.8387 | -0.209 |
| 5 | Pendikspor – Van BB (1 lig) | men | 2026-10-13T17:00:00Z | 2 fuentes | Más de 0.5 goles | 1.04 (1.02–1.05, 5) | 0.722 | 10/10 | 0.9114 | -0.249 |
| 6 | Cartaginés – Puntarenas (primera division fpd) | men | 2026-10-14T00:00:00Z | 2 fuentes | Menos de 5.5 goles | 1.04 (1.01–1.05, 5) | 0.722 | 10/10 | 0.9099 | -0.249 |
| 7 | Orlando Pirates – TS Galaxy (premier soccer league) | men | 2026-10-13T17:30:00Z | 2 fuentes | Menos de 5.5 goles | 1.035 (1.01–1.04, 4) | 0.722 | 10/10 | 0.9206 | -0.253 |
| 8 | Bristol City – Blackburn Rovers (efl championship) | men | 2026-10-13T18:45:00Z | 2 fuentes | Menos de 5.5 goles | 1.035 (1.02–1.05, 4) | 0.722 | 10/10 | 0.9206 | -0.253 |
| 9 | Stoke City – Middlesbrough (efl championship) | men | 2026-10-13T19:00:00Z | 2 fuentes | Más de 0.5 goles | 1.03 (1.02–1.05, 4) | 0.722 | 10/10 | 0.9244 | -0.256 |
| 10 | Millonarios – Once Caldas (categoria primera a) | men | 2026-10-14T01:30:00Z | 2 fuentes | Menos de 5.5 goles | 1.03 (1.01–1.04, 4) | 0.722 | 10/10 | 0.9337 | -0.256 |
| 11 | San Carlos – Inter San Carlos (primera division fpd) | men | 2026-10-14T02:00:00Z | 2 fuentes | Más de 0.5 goles | 1.03 (1.03–1.07, 5) | 0.722 | 10/10 | 0.8806 | -0.256 |
| 12 | Cardiff City – Watford (efl championship) | men | 2026-10-13T18:45:00Z | 2 fuentes | Menos de 4.5 goles | 1.25 (1.2–1.27, 7) | 0.712 | 9/10 | 0.7525 | -0.11 |
| 13 | Queen's Park – Inverness CT (championship) | men | 2026-10-13T18:45:00Z | 2 fuentes | Menos de 4.5 goles | 1.1 (1.06–1.12, 7) | 0.712 | 10/9 | 0.8503 | -0.217 |
| 14 | Burnley – Charlton Athletic (efl championship) | men | 2026-10-13T18:45:00Z | 2 fuentes | Menos de 5.5 goles | 1.035 (1.01–1.06, 4) | 0.712 | 9/10 | 0.914 | -0.263 |
| 15 | ASO Chlef – MC Alger (ligue 1) | men | 2026-10-13T16:45:00Z | 2 fuentes | Más de 0.5 goles | 1.1 (1.08–1.12, 5) | 0.676 | 8/8 | 0.837 | -0.256 |

## Top de picks por ATRACTIVO (rentabilidad-cuota: EV descriptivo conservador = apoyo × cuota − 1, apoyo ≥ 0.55; ordenado de mayor a menor; EV negativo = la estadística conservadora no cubre el precio)

| # | Partido | Categoría | Inicio UTC | Calendario | Selección | Cuota media (mín–máx, casas) | Apoyo cons. | n | Implícita s/margen | EV desc. cons. |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | Cardiff City – Watford (efl championship) | men | 2026-10-13T18:45:00Z | 2 fuentes | Menos de 4.5 goles | 1.25 (1.2–1.27, 7) | 0.712 | 9/10 | 0.7525 | -0.11 |
| 2 | Durban City – AmaZulu (premier soccer league) | men | 2026-10-13T17:30:00Z | 2 fuentes | Menos de 2.5 goles | 1.46 (1.44–1.5, 7) | 0.606 | 10/10 | 0.6322 | -0.115 |
| 3 | Rot-Weiss Essen – Fortuna Köln (3 liga) | men | 2026-10-13T17:00:00Z | 2 fuentes | Hándicap visitante +1.5 | 1.56 (1.43–1.6, 6) | 0.562 | 10/8 | 0.5927 | -0.123 |
| 4 | Atlético Bucaramanga – Águilas Doradas (categoria primera a) | men | 2026-10-13T23:30:00Z | 2 fuentes | Local o empate (1X) | 1.25 (1.16–1.27, 8) | 0.659 | 10/10 | 0.7542 | -0.176 |
| 5 | Athletic-MG – Londrina (serie b) | men | 2026-10-13T22:30:00Z | 2 fuentes | Más de 1.5 goles | 1.36 (1.35–1.4, 7) | 0.606 | 10/10 | 0.6792 | -0.176 |
| 6 | Birmingham City – Preston North End (efl championship) | men | 2026-10-13T19:00:00Z | 2 fuentes | Menos de 4.5 goles | 1.14 (1.12–1.18, 7) | 0.722 | 10/10 | 0.8143 | -0.177 |
| 7 | Pendikspor – Van BB (1 lig) | men | 2026-10-13T17:00:00Z | 2 fuentes | Más de 1.5 goles | 1.22 (1.21–1.27, 7) | 0.659 | 10/10 | 0.75 | -0.196 |
| 8 | Harju Jalgpallikool – Nõmme United (meistriliiga) | men | 2026-10-13T15:00:00Z | 2 fuentes | Menos de 5.5 goles | 1.1 (1.07–1.14, 5) | 0.722 | 10/10 | 0.8226 | -0.206 |
| 9 | Norrköping – GIF Sundsvall (superettan) | men | 2026-10-13T17:00:00Z | 2 fuentes | Menos de 5.5 goles | 1.1 (1.08–1.14, 7) | 0.722 | 10/10 | 0.841 | -0.206 |
| 10 | Simba – Mashujaa (ligi kuu bara) | men | 2026-10-13T16:00:00Z | 2 fuentes | Gana alguno, sin empate (12) | 1.095 (1.06–1.13, 4) | 0.722 | 10/10 | 0.8387 | -0.209 |
| 11 | San Carlos – Inter San Carlos (primera division fpd) | men | 2026-10-14T02:00:00Z | 2 fuentes | Menos de 3.5 goles | 1.3 (1.29–1.32, 6) | 0.606 | 10/10 | 0.7092 | -0.212 |
| 12 | Queen's Park – Inverness CT (championship) | men | 2026-10-13T18:45:00Z | 2 fuentes | Menos de 4.5 goles | 1.1 (1.06–1.12, 7) | 0.712 | 10/9 | 0.8503 | -0.217 |
| 13 | Sariyer – Bodrumspor (1 lig) | men | 2026-10-13T14:00:00Z | 2 fuentes | Menos de 3.5 goles | 1.27 (1.23–1.29, 7) | 0.606 | 10/10 | 0.7338 | -0.23 |
| 14 | Cartaginés – Puntarenas (primera division fpd) | men | 2026-10-14T00:00:00Z | 2 fuentes | Menos de 5.5 goles | 1.04 (1.01–1.05, 5) | 0.722 | 10/10 | 0.9099 | -0.249 |
| 15 | Workington – Whitby Town (northern premier league) | men | 2026-10-13T18:45:00Z | 2 fuentes | Más de 1.5 goles | 1.135 (1.11–1.2, 4) | 0.659 | 10/10 | 0.803 | -0.252 |

*EV descriptivo conservador NO es valor esperado real: usa el límite inferior de frecuencias pasadas como «probabilidad», y al escoger lo mejor entre cientos de patas tiende a sobrestimar. Estos rankings acompañan a los tickets y no los reemplazan; pueden repetir partidos que estén en un ticket.*

## Córners y tarjetas: cuota APROXIMADA por modelo (✎ no es de ninguna casa) y cuota real mínima a exigir (ordenadas de mayor a menor apoyo)

| Partido | Selección | Cuota aprox. | Apoyo cons. | n | Cuota real mínima para tener valor |
|---|---|---|---|---|---|
| Petrojet – Wadi Degla | Menos de 5.5 tarjetas (A+R) | 1.11 ✎ | 0.606 | 10/10 | 1.65 |
| Atlético Bucaramanga – Águilas Doradas | Más de 2.5 tarjetas (A+R) | 1.11 ✎ | 0.596 | 10/10 | 1.68 |
| Bandırmaspor – Sivasspor | Más de 2.5 tarjetas (A+R) | 1.11 ✎ | 0.596 | 10/10 | 1.68 |
| Millonarios – Once Caldas | Más de 2.5 tarjetas (A+R) | 1.11 ✎ | 0.596 | 10/10 | 1.68 |
| Havelse – Würzburger Kickers | Menos de 11.5 córners | 1.13 ✎ | 0.583 | 10/8 | 1.72 |
| Birmingham City – Preston North End | Menos de 5.5 tarjetas (A+R) | 1.12 ✎ | 0.58 | 9/10 | 1.72 |
| FUS Rabat – Raja Casablanca | Más de 3.5 tarjetas (A+R) | 1.12 ✎ | 0.58 | 10/9 | 1.72 |
| Norrköping – GIF Sundsvall | Menos de 4.5 tarjetas (A+R) | 1.12 ✎ | 0.58 | 10/9 | 1.72 |
| Pendikspor – Van BB | Más de 2.5 tarjetas (A+R) | 1.12 ✎ | 0.58 | 10/9 | 1.72 |
| Rot-Weiss Essen – Fortuna Köln | Más de 2.5 tarjetas (A+R) | 1.13 ✎ | 0.566 | 10/8 | 1.77 |
| RSB Berkane – CR Khemis Zemamra | Menos de 10.5 córners | 1.13 ✎ | 0.565 | 9/9 | 1.77 |
| RSB Berkane – CR Khemis Zemamra | Menos de 5.5 tarjetas (A+R) | 1.17 ✎ | 0.56 | 10/10 | 1.79 |
| Vaprus – Nõmme Kalju | Más de 8.5 córners | 1.17 ✎ | 0.56 | 10/10 | 1.79 |
| Al-Saqer – Al Jabalain | Menos de 5.5 tarjetas (A+R) | 1.11 ✎ | 0.556 | 6/8 | 1.8 |
| Zob Ahan – Sepahan | Menos de 4.5 tarjetas (A+R) | 1.12 ✎ | 0.548 | 6/7 | 1.82 |
| Pendikspor – Van BB | Menos de 10.5 córners | 1.17 ✎ | 0.543 | 10/10 | 1.84 |
| Sariyer – Bodrumspor | Menos de 10.5 córners | 1.17 ✎ | 0.543 | 10/10 | 1.84 |
| Stoke City – Middlesbrough | Menos de 5.5 tarjetas (A+R) | 1.17 ✎ | 0.543 | 10/10 | 1.84 |
| Tapatío – Tepatitlán | Más de 4.5 tarjetas (A+R) | 1.17 ✎ | 0.543 | 10/10 | 1.84 |
| Vaprus – Nõmme Kalju | Más de 2.5 tarjetas (A+R) | 1.18 ✎ | 0.528 | 9/10 | 1.89 |

*Cuota aproximada = 1 / (frecuencia suavizada de ambos equipos × (1 + 0.08)): supone un margen típico de casa y SALE de la misma estadística, por eso no se usa para hablar de valor. Sirve para armar y ordenar borradores. Antes de apostar compárala con tu casa: solo tiene valor si paga claramente por encima de la «cuota real mínima». Si me pasas tus cuotas reales (`--manual-odds archivo.csv` con columnas home,away,seleccion,cuota) sustituyen a las aproximadas.*

## Patas VETADAS por la revisión (no entran en ningún ticket ni ranking)

| Partido | Selección | Motivo |
|---|---|---|
| Pohang Steelers – Johor Darul Ta'zim | Local gana (1) | Auditor ronda 2 / cierre de veto: la muestra de Johor está inflada (5.4 GF por partido, 10/10 over 1.5 contra rivales de otra liga) y afecta a cualquier pata de goles; se veta todo el partido |
| Pohang Steelers – Johor Darul Ta'zim | Empate (X) | Auditor ronda 2 / cierre de veto: la muestra de Johor está inflada (5.4 GF por partido, 10/10 over 1.5 contra rivales de otra liga) y afecta a cualquier pata de goles; se veta todo el partido |
| Pohang Steelers – Johor Darul Ta'zim | Visitante gana (2) | Auditor ronda 2 / cierre de veto: la muestra de Johor está inflada (5.4 GF por partido, 10/10 over 1.5 contra rivales de otra liga) y afecta a cualquier pata de goles; se veta todo el partido |
| Pohang Steelers – Johor Darul Ta'zim | Local o empate (1X) | Auditor ronda 2 / cierre de veto: la muestra de Johor está inflada (5.4 GF por partido, 10/10 over 1.5 contra rivales de otra liga) y afecta a cualquier pata de goles; se veta todo el partido |
| Pohang Steelers – Johor Darul Ta'zim | Gana alguno, sin empate (12) | Auditor ronda 2 / cierre de veto: la muestra de Johor está inflada (5.4 GF por partido, 10/10 over 1.5 contra rivales de otra liga) y afecta a cualquier pata de goles; se veta todo el partido |
| Pohang Steelers – Johor Darul Ta'zim | Empate o visitante (X2) | Revisión por lotes (cuantitativo/deportivo): el apoyo de Johor se apoya en 5.4 goles/partido y 9/10 over 2.5 contra rivales mucho más débiles de otra liga; historial mixto sin ajuste por rival |
| Pohang Steelers – Johor Darul Ta'zim | Hándicap local -2.5 | Auditor ronda 2 / cierre de veto: la muestra de Johor está inflada (5.4 GF por partido, 10/10 over 1.5 contra rivales de otra liga) y afecta a cualquier pata de goles; se veta todo el partido |
| Pohang Steelers – Johor Darul Ta'zim | Hándicap visitante +2.5 | Auditor ronda 2 / cierre de veto: la muestra de Johor está inflada (5.4 GF por partido, 10/10 over 1.5 contra rivales de otra liga) y afecta a cualquier pata de goles; se veta todo el partido |
| Pohang Steelers – Johor Darul Ta'zim | Hándicap local -1.5 | Auditor ronda 2 / cierre de veto: la muestra de Johor está inflada (5.4 GF por partido, 10/10 over 1.5 contra rivales de otra liga) y afecta a cualquier pata de goles; se veta todo el partido |
| Pohang Steelers – Johor Darul Ta'zim | Hándicap visitante +1.5 | Auditor ronda 2 / cierre de veto: la muestra de Johor está inflada (5.4 GF por partido, 10/10 over 1.5 contra rivales de otra liga) y afecta a cualquier pata de goles; se veta todo el partido |
| Pohang Steelers – Johor Darul Ta'zim | Hándicap local -0.5 | Auditor ronda 2 / cierre de veto: la muestra de Johor está inflada (5.4 GF por partido, 10/10 over 1.5 contra rivales de otra liga) y afecta a cualquier pata de goles; se veta todo el partido |
| Pohang Steelers – Johor Darul Ta'zim | Hándicap visitante +0.5 | Auditor ronda 2 / cierre de veto: la muestra de Johor está inflada (5.4 GF por partido, 10/10 over 1.5 contra rivales de otra liga) y afecta a cualquier pata de goles; se veta todo el partido |
| Pohang Steelers – Johor Darul Ta'zim | Hándicap local +0.5 | Auditor ronda 2 / cierre de veto: la muestra de Johor está inflada (5.4 GF por partido, 10/10 over 1.5 contra rivales de otra liga) y afecta a cualquier pata de goles; se veta todo el partido |
| Pohang Steelers – Johor Darul Ta'zim | Hándicap visitante -0.5 | Auditor ronda 2 / cierre de veto: la muestra de Johor está inflada (5.4 GF por partido, 10/10 over 1.5 contra rivales de otra liga) y afecta a cualquier pata de goles; se veta todo el partido |
| Pohang Steelers – Johor Darul Ta'zim | Hándicap local +1.5 | Auditor ronda 2 / cierre de veto: la muestra de Johor está inflada (5.4 GF por partido, 10/10 over 1.5 contra rivales de otra liga) y afecta a cualquier pata de goles; se veta todo el partido |
| Pohang Steelers – Johor Darul Ta'zim | Hándicap visitante -1.5 | Auditor ronda 2 / cierre de veto: la muestra de Johor está inflada (5.4 GF por partido, 10/10 over 1.5 contra rivales de otra liga) y afecta a cualquier pata de goles; se veta todo el partido |
| Pohang Steelers – Johor Darul Ta'zim | Hándicap local +2.5 | Auditor ronda 2 / cierre de veto: la muestra de Johor está inflada (5.4 GF por partido, 10/10 over 1.5 contra rivales de otra liga) y afecta a cualquier pata de goles; se veta todo el partido |
| Pohang Steelers – Johor Darul Ta'zim | Hándicap visitante -2.5 | Auditor ronda 2 / cierre de veto: la muestra de Johor está inflada (5.4 GF por partido, 10/10 over 1.5 contra rivales de otra liga) y afecta a cualquier pata de goles; se veta todo el partido |
| Pohang Steelers – Johor Darul Ta'zim | Más de 0.5 goles | Auditor ronda 2 / cierre de veto: la muestra de Johor está inflada (5.4 GF por partido, 10/10 over 1.5 contra rivales de otra liga) y afecta a cualquier pata de goles; se veta todo el partido |
| Pohang Steelers – Johor Darul Ta'zim | Menos de 0.5 goles | Auditor ronda 2 / cierre de veto: la muestra de Johor está inflada (5.4 GF por partido, 10/10 over 1.5 contra rivales de otra liga) y afecta a cualquier pata de goles; se veta todo el partido |
| Pohang Steelers – Johor Darul Ta'zim | Más de 1.5 goles | Auditor ronda 2: misma muestra inflada de Johor (5.4 GF, rivales de otra liga) por la que ya se vetó el X2; sin Johor el equipo local queda en 0.49 <0.55 |
| Pohang Steelers – Johor Darul Ta'zim | Menos de 1.5 goles | Auditor ronda 2 / cierre de veto: la muestra de Johor está inflada (5.4 GF por partido, 10/10 over 1.5 contra rivales de otra liga) y afecta a cualquier pata de goles; se veta todo el partido |
| Pohang Steelers – Johor Darul Ta'zim | Más de 2.5 goles | Auditor ronda 2 / cierre de veto: la muestra de Johor está inflada (5.4 GF por partido, 10/10 over 1.5 contra rivales de otra liga) y afecta a cualquier pata de goles; se veta todo el partido |
| Pohang Steelers – Johor Darul Ta'zim | Menos de 2.5 goles | Auditor ronda 2 / cierre de veto: la muestra de Johor está inflada (5.4 GF por partido, 10/10 over 1.5 contra rivales de otra liga) y afecta a cualquier pata de goles; se veta todo el partido |
| Pohang Steelers – Johor Darul Ta'zim | Más de 3.5 goles | Auditor ronda 2 / cierre de veto: la muestra de Johor está inflada (5.4 GF por partido, 10/10 over 1.5 contra rivales de otra liga) y afecta a cualquier pata de goles; se veta todo el partido |
| Pohang Steelers – Johor Darul Ta'zim | Menos de 3.5 goles | Auditor ronda 2 / cierre de veto: la muestra de Johor está inflada (5.4 GF por partido, 10/10 over 1.5 contra rivales de otra liga) y afecta a cualquier pata de goles; se veta todo el partido |
| Pohang Steelers – Johor Darul Ta'zim | Más de 4.5 goles | Auditor ronda 2 / cierre de veto: la muestra de Johor está inflada (5.4 GF por partido, 10/10 over 1.5 contra rivales de otra liga) y afecta a cualquier pata de goles; se veta todo el partido |
| Pohang Steelers – Johor Darul Ta'zim | Menos de 4.5 goles | Auditor ronda 2 / cierre de veto: la muestra de Johor está inflada (5.4 GF por partido, 10/10 over 1.5 contra rivales de otra liga) y afecta a cualquier pata de goles; se veta todo el partido |
| Pohang Steelers – Johor Darul Ta'zim | Más de 5.5 goles | Auditor ronda 2 / cierre de veto: la muestra de Johor está inflada (5.4 GF por partido, 10/10 over 1.5 contra rivales de otra liga) y afecta a cualquier pata de goles; se veta todo el partido |
| Pohang Steelers – Johor Darul Ta'zim | Menos de 5.5 goles | Auditor ronda 2 / cierre de veto: la muestra de Johor está inflada (5.4 GF por partido, 10/10 over 1.5 contra rivales de otra liga) y afecta a cualquier pata de goles; se veta todo el partido |
| Pohang Steelers – Johor Darul Ta'zim | Ambos anotan: sí | Auditor ronda 2 / cierre de veto: la muestra de Johor está inflada (5.4 GF por partido, 10/10 over 1.5 contra rivales de otra liga) y afecta a cualquier pata de goles; se veta todo el partido |
| Pohang Steelers – Johor Darul Ta'zim | Ambos anotan: no | Auditor ronda 2 / cierre de veto: la muestra de Johor está inflada (5.4 GF por partido, 10/10 over 1.5 contra rivales de otra liga) y afecta a cualquier pata de goles; se veta todo el partido |
| Pohang Steelers – Johor Darul Ta'zim | Más de 8.5 córners | Auditor ronda 2 / cierre de veto: la muestra de Johor está inflada (5.4 GF por partido, 10/10 over 1.5 contra rivales de otra liga) y afecta a cualquier pata de goles; se veta todo el partido |
| Pohang Steelers – Johor Darul Ta'zim | Menos de 8.5 córners | Auditor ronda 2 / cierre de veto: la muestra de Johor está inflada (5.4 GF por partido, 10/10 over 1.5 contra rivales de otra liga) y afecta a cualquier pata de goles; se veta todo el partido |
| Pohang Steelers – Johor Darul Ta'zim | Más de 9.5 córners | Auditor ronda 2 / cierre de veto: la muestra de Johor está inflada (5.4 GF por partido, 10/10 over 1.5 contra rivales de otra liga) y afecta a cualquier pata de goles; se veta todo el partido |
| Pohang Steelers – Johor Darul Ta'zim | Menos de 9.5 córners | Auditor ronda 2 / cierre de veto: la muestra de Johor está inflada (5.4 GF por partido, 10/10 over 1.5 contra rivales de otra liga) y afecta a cualquier pata de goles; se veta todo el partido |
| Pohang Steelers – Johor Darul Ta'zim | Más de 10.5 córners | Auditor ronda 2 / cierre de veto: la muestra de Johor está inflada (5.4 GF por partido, 10/10 over 1.5 contra rivales de otra liga) y afecta a cualquier pata de goles; se veta todo el partido |
| Pohang Steelers – Johor Darul Ta'zim | Menos de 10.5 córners | Auditor ronda 2 / cierre de veto: la muestra de Johor está inflada (5.4 GF por partido, 10/10 over 1.5 contra rivales de otra liga) y afecta a cualquier pata de goles; se veta todo el partido |
| Pohang Steelers – Johor Darul Ta'zim | Más de 11.5 córners | Auditor ronda 2 / cierre de veto: la muestra de Johor está inflada (5.4 GF por partido, 10/10 over 1.5 contra rivales de otra liga) y afecta a cualquier pata de goles; se veta todo el partido |
| Pohang Steelers – Johor Darul Ta'zim | Menos de 11.5 córners | Auditor ronda 2 / cierre de veto: la muestra de Johor está inflada (5.4 GF por partido, 10/10 over 1.5 contra rivales de otra liga) y afecta a cualquier pata de goles; se veta todo el partido |
| Pohang Steelers – Johor Darul Ta'zim | Más de 2.5 tarjetas (A+R) | Auditor ronda 2 / cierre de veto: la muestra de Johor está inflada (5.4 GF por partido, 10/10 over 1.5 contra rivales de otra liga) y afecta a cualquier pata de goles; se veta todo el partido |
| Pohang Steelers – Johor Darul Ta'zim | Menos de 2.5 tarjetas (A+R) | Auditor ronda 2 / cierre de veto: la muestra de Johor está inflada (5.4 GF por partido, 10/10 over 1.5 contra rivales de otra liga) y afecta a cualquier pata de goles; se veta todo el partido |
| Pohang Steelers – Johor Darul Ta'zim | Más de 3.5 tarjetas (A+R) | Auditor ronda 2 / cierre de veto: la muestra de Johor está inflada (5.4 GF por partido, 10/10 over 1.5 contra rivales de otra liga) y afecta a cualquier pata de goles; se veta todo el partido |
| Pohang Steelers – Johor Darul Ta'zim | Menos de 3.5 tarjetas (A+R) | Auditor ronda 2 / cierre de veto: la muestra de Johor está inflada (5.4 GF por partido, 10/10 over 1.5 contra rivales de otra liga) y afecta a cualquier pata de goles; se veta todo el partido |
| Pohang Steelers – Johor Darul Ta'zim | Más de 4.5 tarjetas (A+R) | Auditor ronda 2 / cierre de veto: la muestra de Johor está inflada (5.4 GF por partido, 10/10 over 1.5 contra rivales de otra liga) y afecta a cualquier pata de goles; se veta todo el partido |
| Pohang Steelers – Johor Darul Ta'zim | Menos de 4.5 tarjetas (A+R) | Auditor ronda 2 / cierre de veto: la muestra de Johor está inflada (5.4 GF por partido, 10/10 over 1.5 contra rivales de otra liga) y afecta a cualquier pata de goles; se veta todo el partido |
| Pohang Steelers – Johor Darul Ta'zim | Más de 5.5 tarjetas (A+R) | Auditor ronda 2 / cierre de veto: la muestra de Johor está inflada (5.4 GF por partido, 10/10 over 1.5 contra rivales de otra liga) y afecta a cualquier pata de goles; se veta todo el partido |
| Pohang Steelers – Johor Darul Ta'zim | Menos de 5.5 tarjetas (A+R) | Auditor ronda 2 / cierre de veto: la muestra de Johor está inflada (5.4 GF por partido, 10/10 over 1.5 contra rivales de otra liga) y afecta a cualquier pata de goles; se veta todo el partido |
| Công An Nhân Dân – Kashima Antlers | Gana alguno, sin empate (12) | Auditor ronda 2: pocos empates con copas/ASEAN en la muestra; patas '12' vetadas hasta verificar marcadores a 90' |
| Sariyer – Bodrumspor | Menos de 4.5 goles | Auditor ronda 2: paga 1.065 (6.5 %) con equilibrio 93.9 % frente a implícita 86.4 %; la muestra incluye semifinal de playoff |
| Al Sadd – Al Hilal | Gana alguno, sin empate (12) | Auditor ronda 2: 0 empates en 20 partidos con copas en la muestra; hipótesis (sin verificar) de empates registrados como victoria; sesgo del ganador |
| Sabah – Slavia Praha | Gana alguno, sin empate (12) | Auditor ronda 2: 0 empates en 8; muestra con Qualifying y pretemporada; patas '12' vetadas hasta verificar marcadores a 90' |
| Petrojet – Wadi Degla | Más de 1.5 goles | Auditor ronda 2: lote b08: discrepancia >30 pp frente al mercado, historial con Relegation Group y tarjetas 1/10 vs 9/10 por verificar |
| Orlando Pirates – TS Galaxy | Hándicap visitante +2.5 | Nivel 2 (deportivo): Pirates #2, ganó por 3+ en 3/10; cuota ya baja y riesgo no compensado |
| Kaizer Chiefs – Stellenbosch | Hándicap visitante +1.5 | Auditor ronda 2: Wilson propio 0.397; la frecuencia coincide con el mercado (sin apoyo); etiqueta Play-offs sin confirmar |
| Richards Bay – Mamelodi Sundowns | Local gana (1) | Revisión por lotes (cuantitativo): precios de doble oportunidad incoherentes con el 1X2 (medias de distinto n de casas) y BTTS observado 16/20 frente a ~37% del mercado |
| Richards Bay – Mamelodi Sundowns | Empate (X) | Revisión por lotes (cuantitativo): precios de doble oportunidad incoherentes con el 1X2 (medias de distinto n de casas) y BTTS observado 16/20 frente a ~37% del mercado |
| Richards Bay – Mamelodi Sundowns | Visitante gana (2) | Revisión por lotes (cuantitativo): precios de doble oportunidad incoherentes con el 1X2 (medias de distinto n de casas) y BTTS observado 16/20 frente a ~37% del mercado |
| Richards Bay – Mamelodi Sundowns | Local o empate (1X) | Revisión por lotes (cuantitativo): precios de doble oportunidad incoherentes con el 1X2 (medias de distinto n de casas) y BTTS observado 16/20 frente a ~37% del mercado |
| Richards Bay – Mamelodi Sundowns | Gana alguno, sin empate (12) | Revisión por lotes (cuantitativo): precios de doble oportunidad incoherentes con el 1X2 (medias de distinto n de casas) y BTTS observado 16/20 frente a ~37% del mercado |
| Richards Bay – Mamelodi Sundowns | Empate o visitante (X2) | Revisión por lotes (cuantitativo): precios de doble oportunidad incoherentes con el 1X2 (medias de distinto n de casas) y BTTS observado 16/20 frente a ~37% del mercado |
| Richards Bay – Mamelodi Sundowns | Hándicap local -2.5 | Revisión por lotes (cuantitativo): precios de doble oportunidad incoherentes con el 1X2 (medias de distinto n de casas) y BTTS observado 16/20 frente a ~37% del mercado |
| Richards Bay – Mamelodi Sundowns | Hándicap visitante +2.5 | Revisión por lotes (cuantitativo): precios de doble oportunidad incoherentes con el 1X2 (medias de distinto n de casas) y BTTS observado 16/20 frente a ~37% del mercado |
| Richards Bay – Mamelodi Sundowns | Hándicap local -1.5 | Revisión por lotes (cuantitativo): precios de doble oportunidad incoherentes con el 1X2 (medias de distinto n de casas) y BTTS observado 16/20 frente a ~37% del mercado |
| Richards Bay – Mamelodi Sundowns | Hándicap visitante +1.5 | Revisión por lotes (cuantitativo): precios de doble oportunidad incoherentes con el 1X2 (medias de distinto n de casas) y BTTS observado 16/20 frente a ~37% del mercado |
| Richards Bay – Mamelodi Sundowns | Hándicap local -0.5 | Revisión por lotes (cuantitativo): precios de doble oportunidad incoherentes con el 1X2 (medias de distinto n de casas) y BTTS observado 16/20 frente a ~37% del mercado |
| Richards Bay – Mamelodi Sundowns | Hándicap visitante +0.5 | Revisión por lotes (cuantitativo): precios de doble oportunidad incoherentes con el 1X2 (medias de distinto n de casas) y BTTS observado 16/20 frente a ~37% del mercado |
| Richards Bay – Mamelodi Sundowns | Hándicap local +0.5 | Revisión por lotes (cuantitativo): precios de doble oportunidad incoherentes con el 1X2 (medias de distinto n de casas) y BTTS observado 16/20 frente a ~37% del mercado |
| Richards Bay – Mamelodi Sundowns | Hándicap visitante -0.5 | Revisión por lotes (cuantitativo): precios de doble oportunidad incoherentes con el 1X2 (medias de distinto n de casas) y BTTS observado 16/20 frente a ~37% del mercado |
| Richards Bay – Mamelodi Sundowns | Hándicap local +1.5 | Revisión por lotes (cuantitativo): precios de doble oportunidad incoherentes con el 1X2 (medias de distinto n de casas) y BTTS observado 16/20 frente a ~37% del mercado |
| Richards Bay – Mamelodi Sundowns | Hándicap visitante -1.5 | Revisión por lotes (cuantitativo): precios de doble oportunidad incoherentes con el 1X2 (medias de distinto n de casas) y BTTS observado 16/20 frente a ~37% del mercado |
| Richards Bay – Mamelodi Sundowns | Hándicap local +2.5 | Revisión por lotes (cuantitativo): precios de doble oportunidad incoherentes con el 1X2 (medias de distinto n de casas) y BTTS observado 16/20 frente a ~37% del mercado |
| Richards Bay – Mamelodi Sundowns | Hándicap visitante -2.5 | Revisión por lotes (cuantitativo): precios de doble oportunidad incoherentes con el 1X2 (medias de distinto n de casas) y BTTS observado 16/20 frente a ~37% del mercado |
| Richards Bay – Mamelodi Sundowns | Más de 0.5 goles | Revisión por lotes (cuantitativo): precios de doble oportunidad incoherentes con el 1X2 (medias de distinto n de casas) y BTTS observado 16/20 frente a ~37% del mercado |
| Richards Bay – Mamelodi Sundowns | Menos de 0.5 goles | Revisión por lotes (cuantitativo): precios de doble oportunidad incoherentes con el 1X2 (medias de distinto n de casas) y BTTS observado 16/20 frente a ~37% del mercado |
| Richards Bay – Mamelodi Sundowns | Más de 1.5 goles | Revisión por lotes (cuantitativo): precios de doble oportunidad incoherentes con el 1X2 (medias de distinto n de casas) y BTTS observado 16/20 frente a ~37% del mercado |
| Richards Bay – Mamelodi Sundowns | Menos de 1.5 goles | Revisión por lotes (cuantitativo): precios de doble oportunidad incoherentes con el 1X2 (medias de distinto n de casas) y BTTS observado 16/20 frente a ~37% del mercado |
| Richards Bay – Mamelodi Sundowns | Más de 2.5 goles | Revisión por lotes (cuantitativo): precios de doble oportunidad incoherentes con el 1X2 (medias de distinto n de casas) y BTTS observado 16/20 frente a ~37% del mercado |
| Richards Bay – Mamelodi Sundowns | Menos de 2.5 goles | Revisión por lotes (cuantitativo): precios de doble oportunidad incoherentes con el 1X2 (medias de distinto n de casas) y BTTS observado 16/20 frente a ~37% del mercado |
| Richards Bay – Mamelodi Sundowns | Más de 3.5 goles | Revisión por lotes (cuantitativo): precios de doble oportunidad incoherentes con el 1X2 (medias de distinto n de casas) y BTTS observado 16/20 frente a ~37% del mercado |
| Richards Bay – Mamelodi Sundowns | Menos de 3.5 goles | Revisión por lotes (cuantitativo): precios de doble oportunidad incoherentes con el 1X2 (medias de distinto n de casas) y BTTS observado 16/20 frente a ~37% del mercado |
| Richards Bay – Mamelodi Sundowns | Más de 4.5 goles | Revisión por lotes (cuantitativo): precios de doble oportunidad incoherentes con el 1X2 (medias de distinto n de casas) y BTTS observado 16/20 frente a ~37% del mercado |
| Richards Bay – Mamelodi Sundowns | Menos de 4.5 goles | Revisión por lotes (cuantitativo): precios de doble oportunidad incoherentes con el 1X2 (medias de distinto n de casas) y BTTS observado 16/20 frente a ~37% del mercado |
| Richards Bay – Mamelodi Sundowns | Más de 5.5 goles | Revisión por lotes (cuantitativo): precios de doble oportunidad incoherentes con el 1X2 (medias de distinto n de casas) y BTTS observado 16/20 frente a ~37% del mercado |
| Richards Bay – Mamelodi Sundowns | Menos de 5.5 goles | Revisión por lotes (cuantitativo): precios de doble oportunidad incoherentes con el 1X2 (medias de distinto n de casas) y BTTS observado 16/20 frente a ~37% del mercado |
| Richards Bay – Mamelodi Sundowns | Ambos anotan: sí | Revisión por lotes (cuantitativo): precios de doble oportunidad incoherentes con el 1X2 (medias de distinto n de casas) y BTTS observado 16/20 frente a ~37% del mercado |
| Richards Bay – Mamelodi Sundowns | Ambos anotan: no | Revisión por lotes (cuantitativo): precios de doble oportunidad incoherentes con el 1X2 (medias de distinto n de casas) y BTTS observado 16/20 frente a ~37% del mercado |
| Richards Bay – Mamelodi Sundowns | Más de 8.5 córners | Revisión por lotes (cuantitativo): precios de doble oportunidad incoherentes con el 1X2 (medias de distinto n de casas) y BTTS observado 16/20 frente a ~37% del mercado |
| Richards Bay – Mamelodi Sundowns | Menos de 8.5 córners | Revisión por lotes (cuantitativo): precios de doble oportunidad incoherentes con el 1X2 (medias de distinto n de casas) y BTTS observado 16/20 frente a ~37% del mercado |
| Richards Bay – Mamelodi Sundowns | Más de 9.5 córners | Revisión por lotes (cuantitativo): precios de doble oportunidad incoherentes con el 1X2 (medias de distinto n de casas) y BTTS observado 16/20 frente a ~37% del mercado |
| Richards Bay – Mamelodi Sundowns | Menos de 9.5 córners | Revisión por lotes (cuantitativo): precios de doble oportunidad incoherentes con el 1X2 (medias de distinto n de casas) y BTTS observado 16/20 frente a ~37% del mercado |
| Richards Bay – Mamelodi Sundowns | Más de 10.5 córners | Revisión por lotes (cuantitativo): precios de doble oportunidad incoherentes con el 1X2 (medias de distinto n de casas) y BTTS observado 16/20 frente a ~37% del mercado |
| Richards Bay – Mamelodi Sundowns | Menos de 10.5 córners | Revisión por lotes (cuantitativo): precios de doble oportunidad incoherentes con el 1X2 (medias de distinto n de casas) y BTTS observado 16/20 frente a ~37% del mercado |
| Richards Bay – Mamelodi Sundowns | Más de 11.5 córners | Revisión por lotes (cuantitativo): precios de doble oportunidad incoherentes con el 1X2 (medias de distinto n de casas) y BTTS observado 16/20 frente a ~37% del mercado |
| Richards Bay – Mamelodi Sundowns | Menos de 11.5 córners | Revisión por lotes (cuantitativo): precios de doble oportunidad incoherentes con el 1X2 (medias de distinto n de casas) y BTTS observado 16/20 frente a ~37% del mercado |
| Richards Bay – Mamelodi Sundowns | Más de 2.5 tarjetas (A+R) | Revisión por lotes (cuantitativo): precios de doble oportunidad incoherentes con el 1X2 (medias de distinto n de casas) y BTTS observado 16/20 frente a ~37% del mercado |
| Richards Bay – Mamelodi Sundowns | Menos de 2.5 tarjetas (A+R) | Revisión por lotes (cuantitativo): precios de doble oportunidad incoherentes con el 1X2 (medias de distinto n de casas) y BTTS observado 16/20 frente a ~37% del mercado |
| Richards Bay – Mamelodi Sundowns | Más de 3.5 tarjetas (A+R) | Revisión por lotes (cuantitativo): precios de doble oportunidad incoherentes con el 1X2 (medias de distinto n de casas) y BTTS observado 16/20 frente a ~37% del mercado |
| Richards Bay – Mamelodi Sundowns | Menos de 3.5 tarjetas (A+R) | Revisión por lotes (cuantitativo): precios de doble oportunidad incoherentes con el 1X2 (medias de distinto n de casas) y BTTS observado 16/20 frente a ~37% del mercado |
| Richards Bay – Mamelodi Sundowns | Más de 4.5 tarjetas (A+R) | Revisión por lotes (cuantitativo): precios de doble oportunidad incoherentes con el 1X2 (medias de distinto n de casas) y BTTS observado 16/20 frente a ~37% del mercado |
| Richards Bay – Mamelodi Sundowns | Menos de 4.5 tarjetas (A+R) | Revisión por lotes (cuantitativo): precios de doble oportunidad incoherentes con el 1X2 (medias de distinto n de casas) y BTTS observado 16/20 frente a ~37% del mercado |
| Richards Bay – Mamelodi Sundowns | Más de 5.5 tarjetas (A+R) | Revisión por lotes (cuantitativo): precios de doble oportunidad incoherentes con el 1X2 (medias de distinto n de casas) y BTTS observado 16/20 frente a ~37% del mercado |
| Richards Bay – Mamelodi Sundowns | Menos de 5.5 tarjetas (A+R) | Revisión por lotes (cuantitativo): precios de doble oportunidad incoherentes con el 1X2 (medias de distinto n de casas) y BTTS observado 16/20 frente a ~37% del mercado |
| Hartlepool – Newcastle Utd U21 | Local gana (1) | Nivel 2 (verificador/deportivo): plantilla sub-23, una sola fuente de calendario, cuotas 1X2 sospechosas |
| Hartlepool – Newcastle Utd U21 | Empate (X) | Nivel 2 (verificador/deportivo): plantilla sub-23, una sola fuente de calendario, cuotas 1X2 sospechosas |
| Hartlepool – Newcastle Utd U21 | Visitante gana (2) | Nivel 2 (verificador/deportivo): plantilla sub-23, una sola fuente de calendario, cuotas 1X2 sospechosas |
| Hartlepool – Newcastle Utd U21 | Local o empate (1X) | Nivel 2 (verificador/deportivo): plantilla sub-23, una sola fuente de calendario, cuotas 1X2 sospechosas |
| Hartlepool – Newcastle Utd U21 | Gana alguno, sin empate (12) | Nivel 2 (verificador/deportivo): plantilla sub-23, una sola fuente de calendario, cuotas 1X2 sospechosas |
| Hartlepool – Newcastle Utd U21 | Empate o visitante (X2) | Nivel 2 (verificador/deportivo): plantilla sub-23, una sola fuente de calendario, cuotas 1X2 sospechosas |
| Hartlepool – Newcastle Utd U21 | Hándicap local -2.5 | Nivel 2 (verificador/deportivo): plantilla sub-23, una sola fuente de calendario, cuotas 1X2 sospechosas |
| Hartlepool – Newcastle Utd U21 | Hándicap visitante +2.5 | Nivel 2 (verificador/deportivo): plantilla sub-23, una sola fuente de calendario, cuotas 1X2 sospechosas |
| Hartlepool – Newcastle Utd U21 | Hándicap local -1.5 | Nivel 2 (verificador/deportivo): plantilla sub-23, una sola fuente de calendario, cuotas 1X2 sospechosas |
| Hartlepool – Newcastle Utd U21 | Hándicap visitante +1.5 | Nivel 2 (verificador/deportivo): plantilla sub-23, una sola fuente de calendario, cuotas 1X2 sospechosas |
| Hartlepool – Newcastle Utd U21 | Hándicap local -0.5 | Nivel 2 (verificador/deportivo): plantilla sub-23, una sola fuente de calendario, cuotas 1X2 sospechosas |
| Hartlepool – Newcastle Utd U21 | Hándicap visitante +0.5 | Nivel 2 (verificador/deportivo): plantilla sub-23, una sola fuente de calendario, cuotas 1X2 sospechosas |
| Hartlepool – Newcastle Utd U21 | Hándicap local +0.5 | Nivel 2 (verificador/deportivo): plantilla sub-23, una sola fuente de calendario, cuotas 1X2 sospechosas |
| Hartlepool – Newcastle Utd U21 | Hándicap visitante -0.5 | Nivel 2 (verificador/deportivo): plantilla sub-23, una sola fuente de calendario, cuotas 1X2 sospechosas |
| Hartlepool – Newcastle Utd U21 | Hándicap local +1.5 | Nivel 2 (verificador/deportivo): plantilla sub-23, una sola fuente de calendario, cuotas 1X2 sospechosas |
| Hartlepool – Newcastle Utd U21 | Hándicap visitante -1.5 | Nivel 2 (verificador/deportivo): plantilla sub-23, una sola fuente de calendario, cuotas 1X2 sospechosas |
| Hartlepool – Newcastle Utd U21 | Hándicap local +2.5 | Nivel 2 (verificador/deportivo): plantilla sub-23, una sola fuente de calendario, cuotas 1X2 sospechosas |
| Hartlepool – Newcastle Utd U21 | Hándicap visitante -2.5 | Nivel 2 (verificador/deportivo): plantilla sub-23, una sola fuente de calendario, cuotas 1X2 sospechosas |
| Hartlepool – Newcastle Utd U21 | Más de 0.5 goles | Nivel 2 (verificador/deportivo): plantilla sub-23, una sola fuente de calendario, cuotas 1X2 sospechosas |
| Hartlepool – Newcastle Utd U21 | Menos de 0.5 goles | Nivel 2 (verificador/deportivo): plantilla sub-23, una sola fuente de calendario, cuotas 1X2 sospechosas |
| Hartlepool – Newcastle Utd U21 | Más de 1.5 goles | Nivel 2 (verificador/deportivo): plantilla sub-23, una sola fuente de calendario, cuotas 1X2 sospechosas |
| Hartlepool – Newcastle Utd U21 | Menos de 1.5 goles | Nivel 2 (verificador/deportivo): plantilla sub-23, una sola fuente de calendario, cuotas 1X2 sospechosas |
| Hartlepool – Newcastle Utd U21 | Más de 2.5 goles | Nivel 2 (verificador/deportivo): plantilla sub-23, una sola fuente de calendario, cuotas 1X2 sospechosas |
| Hartlepool – Newcastle Utd U21 | Menos de 2.5 goles | Nivel 2 (verificador/deportivo): plantilla sub-23, una sola fuente de calendario, cuotas 1X2 sospechosas |
| Hartlepool – Newcastle Utd U21 | Más de 3.5 goles | Nivel 2 (verificador/deportivo): plantilla sub-23, una sola fuente de calendario, cuotas 1X2 sospechosas |
| Hartlepool – Newcastle Utd U21 | Menos de 3.5 goles | Nivel 2 (verificador/deportivo): plantilla sub-23, una sola fuente de calendario, cuotas 1X2 sospechosas |
| Hartlepool – Newcastle Utd U21 | Más de 4.5 goles | Nivel 2 (verificador/deportivo): plantilla sub-23, una sola fuente de calendario, cuotas 1X2 sospechosas |
| Hartlepool – Newcastle Utd U21 | Menos de 4.5 goles | Nivel 2 (verificador/deportivo): plantilla sub-23, una sola fuente de calendario, cuotas 1X2 sospechosas |
| Hartlepool – Newcastle Utd U21 | Más de 5.5 goles | Nivel 2 (verificador/deportivo): plantilla sub-23, una sola fuente de calendario, cuotas 1X2 sospechosas |
| Hartlepool – Newcastle Utd U21 | Menos de 5.5 goles | Nivel 2 (verificador/deportivo): plantilla sub-23, una sola fuente de calendario, cuotas 1X2 sospechosas |
| Hartlepool – Newcastle Utd U21 | Ambos anotan: sí | Nivel 2 (verificador/deportivo): plantilla sub-23, una sola fuente de calendario, cuotas 1X2 sospechosas |
| Hartlepool – Newcastle Utd U21 | Ambos anotan: no | Nivel 2 (verificador/deportivo): plantilla sub-23, una sola fuente de calendario, cuotas 1X2 sospechosas |
| Hartlepool – Newcastle Utd U21 | Más de 2.5 tarjetas (A+R) | Nivel 2 (verificador/deportivo): plantilla sub-23, una sola fuente de calendario, cuotas 1X2 sospechosas |
| Hartlepool – Newcastle Utd U21 | Menos de 2.5 tarjetas (A+R) | Nivel 2 (verificador/deportivo): plantilla sub-23, una sola fuente de calendario, cuotas 1X2 sospechosas |
| Hartlepool – Newcastle Utd U21 | Más de 3.5 tarjetas (A+R) | Nivel 2 (verificador/deportivo): plantilla sub-23, una sola fuente de calendario, cuotas 1X2 sospechosas |
| Hartlepool – Newcastle Utd U21 | Menos de 3.5 tarjetas (A+R) | Nivel 2 (verificador/deportivo): plantilla sub-23, una sola fuente de calendario, cuotas 1X2 sospechosas |
| Hartlepool – Newcastle Utd U21 | Más de 4.5 tarjetas (A+R) | Nivel 2 (verificador/deportivo): plantilla sub-23, una sola fuente de calendario, cuotas 1X2 sospechosas |
| Hartlepool – Newcastle Utd U21 | Menos de 4.5 tarjetas (A+R) | Nivel 2 (verificador/deportivo): plantilla sub-23, una sola fuente de calendario, cuotas 1X2 sospechosas |
| Hartlepool – Newcastle Utd U21 | Más de 5.5 tarjetas (A+R) | Nivel 2 (verificador/deportivo): plantilla sub-23, una sola fuente de calendario, cuotas 1X2 sospechosas |
| Hartlepool – Newcastle Utd U21 | Menos de 5.5 tarjetas (A+R) | Nivel 2 (verificador/deportivo): plantilla sub-23, una sola fuente de calendario, cuotas 1X2 sospechosas |
| Bury Town – Needham Market | Gana alguno, sin empate (12) | Auditor ronda 2: 0 empates en 10 (Needham 2): patas '12' vetadas hasta verificar marcadores a 90' |
| Birmingham City – Preston North End | Hándicap visitante +1.5 | Nivel 2 (deportivo): Preston #24 perdió por 2+ en 3/10; se prefiere la +2.5 (overround 1.153 anómalo en la +1.5 según cuantitativo) |
| Villarreal – Napoli | Hándicap visitante +1.5 | Auditor ronda 2: la muestra incluye amistosos (Como Cup/Emirates Cup) pese a 'sin amistosos'; 4 casas |
| Inter Milan – Club Brugge | Hándicap visitante +2.5 | Nivel 2 (deportivo): Inter ganó por 3+ en 2 de 4 partidos competitivos en casa; el mercado da ~35% a la goleada → riesgo alto para una pata de seguridad |
| RB Leipzig – PSV | Gana alguno, sin empate (12) | Auditor ronda 2: 0 empates en 10; patas '12' vetadas hasta verificar marcadores a 90' |
| Arsenal – Lille | Hándicap visitante +2.5 | Nivel 2 (deportivo): favorito fuerte en casa, ganó por 3+ en 2 de 4 en casa; mercado ~36–39% a la goleada |
| Athletic-MG – Londrina | Más de 2.5 tarjetas (A+R) | Nivel 2 (verificador/deportivo/cuantitativo): sin mercado de tarjetas en la API, cuota solo estimada por modelo, sin árbitro ni regla de liquidación verificada |

## PARES del mismo partido vetados tras la reevaluación por agentes

| Partido | Par | Motivo |
|---|---|---|
| Atlético Bucaramanga – Águilas Doradas | Local o empate (1X) + Menos de 4.5 goles | Deportivo: aceptable flojo; cuantitativo y auditor: DESACONSEJADO (conjunta 0.66–0.71 frente a equilibrio 0.755; la 1X simple a 1.25 lo domina; el producto 1.325 supera el rango). |
| Atlético Bucaramanga – Águilas Doradas | Local o empate (1X) + Más de 0.5 goles | Cuantitativo y auditor: DESACONSEJADO (P = P(1X) − P(0-0): 0.64–0.70 frente a 0.762; riesgos disjuntos). |
| Birmingham City – Preston North End | Menos de 4.5 goles + Local o empate (1X) | Deportivo, cuantitativo y auditor: DESACONSEJADO (conjunta 0.66–0.73 frente a 0.77; el par +2.5 visitante + menos de 4.5 lo domina). |
| Kyoto Sanga – Ratchaburi | Hándicap visitante +1.5 + Menos de 3.5 goles | Deportivo: DESACONSEJADO (×2.40 pide ~40 %, historial mixto con copas); cuantitativo y auditor: aceptable solo con cuota real del par ≥2.20–2.35. Sin respaldo unánime de los agentes: no se propone. |

---
Partidos usados en borradores de perfiles previos: 28; sin partidos repetidos entre multiplicadores: True; cuotas manuales aplicadas: 0.
Patas evaluadas: 5074 (con cuota media: 1947) en 135 partidos.
