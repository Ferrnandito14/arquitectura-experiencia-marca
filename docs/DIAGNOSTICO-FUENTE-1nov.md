# Diagnóstico del 31-oct/1-nov-2026: ¿problema del modelo o de las fuentes?

**Conclusión: de las fuentes y de cómo se leyeron; no del modelo** (en estos archivos el modelo propio no se usa: precios y probabilidades salen del mercado).

1. **Partidos femeninos con nombre de club masculino.** El listado `/football/matches` de TheStatsAPI no trae el género. «Arsenal – Aston Villa» (1-nov) era el partido femenino (entrenadoras Slegers y Sørensen). Con el género de cada equipo (`/football/teams/{id}`, campo `is_mens_team`) se hallaron 18 partidos femeninos en el pool de 265 (Inter–Lazio, Roma–Napoli, Como–Milan, Brighton–Crystal Palace, Liverpool…). Corrección: `pool_mercado.py validar` descarga la ficha de cada equipo y el pool excluye los no masculinos.
2. **Marcadores invertidos en el análisis deportivo.** El agente leía marcadores en bruto de partidos de visita (local–visitante del partido) y los atribuía al equipo al revés (victorias del Lazio 3-0 y 6-2 leídas como derrotas). Ocurrió también antes con la orientación de `matrix.json`. Corrección: `dossier_equipo.py` orienta cada partido desde el punto de vista del equipo en código; el agente solo interpreta.
3. **Coherencia de la fuente.** `dossier_equipo.py` comprueba que el partido sea el próximo partido programado de AMBOS equipos; sin coincidencia emite `alertas_fuente`.
4. **Lo que no se puede comprobar desde aquí:** qué partidos y mercados ofrece la casa de Fernando. Cualquier calendario externo es solo contraste.
5. **Fuente única (decisión de Fernando, 31-oct):** TheStatsAPI. Ya no se usan apifootball (plan recortado a 2 ligas), football-data ni fixturedownload.
