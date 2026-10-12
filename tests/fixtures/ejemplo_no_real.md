# EJEMPLO — NO REAL
Todos los equipos, partidos, cifras, cuotas y "fuentes" de este archivo son INVENTADOS para probar el flujo de agentes.
Las únicas fuentes permitidas son los identificadores `fixture://`. Está PROHIBIDO usar web o memoria para este caso.
Fecha ficticia de consulta de todas las fuentes: 2099-01-01 12:00 UTC. Todos los partidos: 2099-01-02.
Convención: un bloque `fixture://X` es "la ficha abierta" de esa fuente; lo que no aparece en un bloque, esa fuente NO lo tiene.

## Candidatos
- A: BTTS "Sí" — Alfa FC vs Beta FC — cuota comunicada 1.80
- B: Victoria local — Gamma FC vs Delta FC — cuota 1.55
- C: Más de 9.5 córners — Épsilon FC vs Zeta FC — cuota 1.90
- D (borrador débil): Victoria local — Eta FC vs Kappa FC — cuota 1.40
- E (alternativa descubierta en la búsqueda): Más de 2.5 goles — Theta FC vs Iota FC — cuota 1.70

## fixture://calendario-1  (estado/hora)
Alfa-Beta 2099-01-02 20:00 UTC confirmado · Gamma-Delta 2099-01-02 18:00 UTC confirmado · Épsilon-Zeta 2099-01-02 19:00 UTC confirmado · Eta-Kappa 2099-01-02 15:00 UTC confirmado · Theta-Iota 2099-01-02 17:00 UTC confirmado.
## fixture://calendario-2
Mismos cinco partidos, mismas horas. (Sin discrepancias.)

## fixture://source-a  (forma y goles)
- Alfa (últimos 10, liga única): BTTS 7/10; 4 en casa de 5 con BTTS. Rivales: 6 de mitad de tabla o mejores.
- Beta (últimos 10): BTTS 6/10; fuera 3/5. Rivales: nivel similar.
- Gamma (local, últimos 10 en casa): 8 victorias, 1 empate, 1 derrota; rivales de tabla media-baja. Delta (visitante, últimos 10): 3 victorias, 2 empates, 5 derrotas.
- Eta (últimos 4 partidos solamente, ficha nueva): 4 victorias vs rivales de la parte baja. Kappa: 2 victorias en 4. Historial directo: Eta ganó 2-0 en 2019 (entrenadores y plantillas distintas).
- Theta (últimos 10): Over 2.5 en 8/10. Iota (últimos 10): Over 2.5 en 7/10. Sin bajas relevantes reportadas.
## fixture://source-b  (segunda fuente de forma, independiente)
- Alfa BTTS 7/10; Beta BTTS 6/10 (coincide con source-a). Gamma 8-1-1 en casa (coincide). Theta Over 2.5 8/10, Iota 7/10 (coincide).
- Eta: no hay ficha con muestra suficiente (3 partidos listados).
## fixture://source-c  (tercera fuente de forma)
- Alfa y Beta: consistentes con las anteriores. Theta/Iota: consistentes. Gamma-Delta: consistente.

## fixture://corners-a  (córners)
- Épsilon (últimos 5): córners totales por partido: 12, 11, 9, 13, 11 (media 11.2). Línea 9.5: superó 4/5. Local/visitante no desglosado en esta ficha. Rivales no indicados.
- Zeta (últimos 5): 10, 8, 12, 9, 10 (media 9.8). Línea 9.5: superó 3/5.
## fixture://corners-b  (DEFECTUOSA a propósito)
- Épsilon (últimos 5): córners totales 0, 0, 0, 0, 0 con "media de la liga 6.1"; la ficha lista 5 partidos pero las fechas coinciden con partidos que en corners-a tienen 12, 11, 9, 13, 11. Zeta: sin datos.

## fixture://club-news  (lesiones)
- Gamma FC: su delantero titular (máximo goleador del equipo) es BAJA CONFIRMADA por lesión muscular (comunicado del club, 2099-01-01 10:00). Sin otros datos de impacto.
- Resto de equipos: sin bajas relevantes reportadas.

## fixture://odds-1  (cuotas decimales, misma casa para todo el mercado listado)
- A BTTS Sí 1.80 / No 2.00 · B Gamma gana 1.55 (empate 4.20, Delta 6.50) · C Over 9.5 córners 1.90 · D Eta gana 1.40 · E Over 2.5 goles 1.70 / Under 2.5 2.10
## fixture://odds-2  (segunda fuente de cuotas, otra casa)
- A BTTS Sí 1.83 / No 1.95 · E Over 2.5 goles 1.72 / Under 2.10 · C Over 9.5 córners 1.88
- B y D: esta fuente NO cubre esos mercados. (No hay segunda cotización.)
