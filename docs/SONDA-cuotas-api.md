# Sonda de la API de cuotas (apifootball `get_odds`) — 14-oct-2026

**Método (sin consultas nuevas):** se analizaron TODAS las respuestas crudas de `get_odds` que quedaron en la caché de `runs/2026-10-14/cache/` (la consulta por día `from=2026-10-14&to=2026-10-15` y 26 consultas por `match_id`; el registro de cada consulta está en `sources/consultas.jsonl`).

**Resultado:** 2 213 filas (casa × partido), 249+ partidos, 68 campos distintos. Los campos publicados son: `odd_1/odd_x/odd_2` (1X2), `odd_1x/odd_12/odd_x2` (doble oportunidad), `ah-4.5 … ah+4.5` (hándicap asiático, `_1` local / `_2` visitante; con líneas enteras y de media línea), `o+0.5 … o+5.5` y `u+0.5 … u+5.5` (totales de goles, con líneas enteras), `bts_yes/bts_no` (ambos anotan).
**Ningún campo** contiene córners, tarjetas, goles por equipo ni 1.ª parte (búsqueda por `corner`, `card`, `tarj`, `team`, `1h`, `ht`, `half`, `home_total`, `away_total`: 0 coincidencias).
Algunas líneas no aparecen en ninguna fila (p. ej. `ah-0.5_1`/`ah+0.5_2`); el adaptador las busca igualmente y, si faltan, la combinación queda «consultado_no_encontrado».

**Consecuencia:** los precios de córners, tarjetas, goles por equipo y 1.ª parte NO existen en esta fuente. Vías legítimas: la plantilla CSV (`market_coverage.py --price-template`) para que la persona usuaria pegue los precios reales de SU casa, o una fuente adicional que los publique (Fase posterior, con fila en `sources_policy.json`).

## Verificación en vivo del 14-oct (a pedido del usuario: ¿no lo ofrece la fuente o no lo pedía el extractor?)
- Consulta real `get_odds match_id=711710`: 6 filas (casas), 43 campos con dato: solo `odd_1/x/2`, `odd_1x/12/x2`, `ah±…_1/_2`, `o+/u+ 0.5…5.5` y `bts_yes/no` (+ `match_id`, `odd_bookmakers`, `odd_date`). Las 8 864 filas de todas las respuestas guardadas comparten el mismo esquema de 68 campos; **todo campo con dato ya está mapeado** por el extractor (los únicos sin mapear con dato son metadatos). Los campos de totales enteros `o+1…o+5` / `u+1…u+5` existen en el esquema pero NUNCA traen dato.
- `get_live_odds` → `400: Invalid action!`; `get_odds` por liga/día para la liga 332 → `404: No odd found (please check your plan)`.
- Por mercado: **no ofrecido por la fuente** (no es omisión del extractor): córners, tarjetas, goles por equipo, 1.ª parte (resultado y goles), hándicap europeo, remates, remates a puerta, fueras de juego y totales enteros. **Ofrecido y mapeado:** 1X2, doble oportunidad, hándicap asiático (medias líneas y enteras), goles O/U (medias líneas), ambos anotan y empate no válido (= `ah0`). «El extractor no lo pedía»: ningún caso con dato (el empate no válido sí estaba sin mapear y se corrigió en la Fase 7).
- Otras fuentes de cuotas: las únicas permitidas por la política (`docs/FUENTES-CONFORMIDAD.md`) son apifootball y Football-Data (solo 1X2, totales 2.5 y hándicap de Bet365 en fixtures); OddsPortal/Oddschecker/BetExplorer/SofaScore y similares están excluidas o sin revisar (denegadas) y no se evaden. Por eso esos mercados quedan «sin cuota en fuente» hasta que se pegue la cuota de la casa.

