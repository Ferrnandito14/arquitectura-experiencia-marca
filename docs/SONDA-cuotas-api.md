# Sonda de la API de cuotas (apifootball `get_odds`) — 14-oct-2026

**Método (sin consultas nuevas):** se analizaron TODAS las respuestas crudas de `get_odds` que quedaron en la caché de `runs/2026-10-14/cache/` (la consulta por día `from=2026-10-14&to=2026-10-15` y 26 consultas por `match_id`; el registro de cada consulta está en `sources/consultas.jsonl`).

**Resultado:** 2 213 filas (casa × partido), 249+ partidos, 68 campos distintos. Los campos publicados son: `odd_1/odd_x/odd_2` (1X2), `odd_1x/odd_12/odd_x2` (doble oportunidad), `ah-4.5 … ah+4.5` (hándicap asiático, `_1` local / `_2` visitante; con líneas enteras y de media línea), `o+0.5 … o+5.5` y `u+0.5 … u+5.5` (totales de goles, con líneas enteras), `bts_yes/bts_no` (ambos anotan).
**Ningún campo** contiene córners, tarjetas, goles por equipo ni 1.ª parte (búsqueda por `corner`, `card`, `tarj`, `team`, `1h`, `ht`, `half`, `home_total`, `away_total`: 0 coincidencias).
Algunas líneas no aparecen en ninguna fila (p. ej. `ah-0.5_1`/`ah+0.5_2`); el adaptador las busca igualmente y, si faltan, la combinación queda «consultado_no_encontrado».

**Consecuencia:** los precios de córners, tarjetas, goles por equipo y 1.ª parte NO existen en esta fuente. Vías legítimas: la plantilla CSV (`market_coverage.py --price-template`) para que la persona usuaria pegue los precios reales de SU casa, o una fuente adicional que los publique (Fase posterior, con fila en `sources_policy.json`).
