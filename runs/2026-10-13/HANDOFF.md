# Traspaso de sesión (2026-10-13) — leer antes de continuar

## Reglas de la persona usuaria (Fernando) que deben persistir
- Dos multiplicadores objetivo: **×1.20–1.28 (seguridad)** y **×4.0–4.8 (amplio)**. Para el ×4 evaluar TODOS los mercados (1X2, doble oportunidad, hándicap, goles over/under, BTTS, córners, tarjetas); no limitarse a ejemplos. El ×1.2 admite 2 patas del mismo partido (ej. «Atalanta 1X + menos de 5.5 goles»); el ×4 también si está justificado (apoyo conjunto medido).
- **Un partido NO puede aparecer en dos tickets** (si cae en uno no cae en el otro). Dar **más de un borrador por multiplicador** (yo decido cuántos; hoy 5).
- **Córners y tarjetas deben llevar cuota**, aunque aproximada: se rotula «estimada por modelo ✎» (no es de ninguna casa); aceptar `--manual-odds` con cuotas reales. Entregable final: tickets + **top por seguridad y top por atractivo (rentabilidad-cuota)** + resto de la información (no lo reemplaza).
- Restricciones: sin push a GitHub, no tocar `insta-mcp`, UA honesto `football-picks-system/0.1`, sin evadir anti-bot, clave de apifootball fuera del repo (usa `APIFOOTBALL_KEY_FILE` o secreto; la clave se pegó en el chat: pedir regenerarla al terminar). Recordatorio programado `trig_01Ta32gFygrV1tt1moSw9Y1s` (26-oct 14:00Z) sobre el plan de apifootball que vence el 28-oct. No hablar del plan antes.
- Entregar ZIP + parches + checksums + VERIFICACION con SendUserFile (parches con `git format-patch --binary`, aplicar con `git am --keep-cr`).

## Estado técnico (repo local /home/user/football-picks-system, sin remoto)
- Calendario: APWin paginado (`/api/home/calendar`) + apifootball `get_events`; 1012 únicos, 319 requeridos (285 con historial de apifootball, 34 sin cobertura). Cobertura = `RANKING PROVISIONAL RESTRINGIDO`.
- Scripts: `inventory.py`, `level1.py` (--reset ESTADOS, historial propio apifootball; **pendiente aplicar**: preferir partidos de la MISMA competición y excluir amistosos — código ya escrito, falta regenerar), `coverage_report.py`, `batches.py make` (fichas compactas `review_cards.json`, 12 lotes), `tickets.py` (perfiles, pares mismo partido de familias distintas, `vetoes.json`, mediana de casas, colchón, descuento 5 % a pares, ≤1 cuota estimada por ticket), `apif_query.py` (consulta segura para agentes, tope 120).
- Pruebas: 201 OK (1 skip). Último commit `2e0c08b`; hay cambios posteriores SIN commit (common.norm_name ı/ø, prefijo de tokens en inventory, init_state poda huérfanos, same-competition en level1, vetos en tickets, tests).

## Hallazgos del Nivel 2 (informes en runs/2026-10-13/reviews_raw/level2/)
- Bug corregido: prob. implícita de doble oportunidad (1X/12/X2) estaba mal (normalizaba 3 cuotas solapadas).
- Marathon y 1xBet repiten precios: con una sola casa ningún borrador ×4 llega a 4.0 (3.25–3.96) y S1/S4 <1.20. Hay que pedir cuota real de la casa de la persona usuaria pata por pata.
- Techo de Wilson con n=10 = 0.722: umbral original 0.80 inalcanzable (bajado a 0.65: declararlo).
- Casi ninguna pata tiene ventaja vs su propia estadística (solo Kyoto +1.5; riesgo de maldición del ganador).
- Cuota inventada de «más de 2.5 tarjetas» (Athletic-MG) en A2/A4: vetar. Vetos propuestos (aún NO escritos en vetoes.json): Inter–Brugge +2.5 visit., Arsenal–Lille +2.5 visit., Orlando–TS Galaxy +2.5 visit., Athletic-MG tarjetas >2.5, Preston +1.5 (preferir +2.5), Hartlepool–Newcastle U21 (todo el partido).
- Duplicados por grafía (Bandırmaspor, Pendikspor/Van BB) corregidos con norm_name y prefijos; ligas menores (non-league inglesa) con etiquetas de ronda rotas y córners/tarjetas None.
- Revisión por lotes de agentes: hecho SOLO b01 (viejo; los lotes cambian al regenerar) → rehacer los 12 lotes × (analista-deportivo, analista-cuantitativo) + lote de discrepancias (verificador-mercados) con `batches.py check`.

## Pasos pendientes (en orden)
1. Commit de lo pendiente; escribir `vetoes.json` con los vetos de arriba.
2. `export APIFOOTBALL_KEY_FILE=/tmp/claude-0/-home-user/d56b1dd2-9e37-5240-9a83-4b470c476a77/scratchpad/probe/key.txt` (si no existe, pedir la clave como secreto/variable); `level1.py --reset COMPLETADO,NO_EVALUABLE_TRAS_INTENTOS,NO_INVESTIGADO_SIN_FUENTE_PERMITIDA`; `coverage_report.py`; `batches.py make`; `tickets.py`.
3. Lanzar revisión por lotes (12×2 + verificador) en tandas; `batches.py check` (exit 0 = todo conciliado).
4. Ronda 2 (objeciones por SendMessage) y `RESOLUCION-director.md`; actualizar MANIFIESTO, docs/PRUEBAS-picks.md, FUENTES-CONFORMIDAD.
5. Rebuild `dist/football-picks-system-v2.4.zip` + parches + SHA256SUMS + VERIFICACION y entregar; informe final con denominadores, advertencias (cuotas medias/estimadas, apoyo≠probabilidad) y pedir cuotas reales de la casa para confirmar rangos.

## SEGUIMIENTO EN VIVO (13-oct, tarde) — leer primero tras compactar
- Tickets reales de Fernando en `runs/2026-10-13/seguimiento/tickets_abiertos.json`: A ×1.25 Cardiff–Watford U4.5; B ×4.40 (Pendikspor O1.5, Durban U2.5, Athletic-MG O1.5, San Carlos U3.5, Bucaramanga O1.5); C ×4.62 Champions V1 (Brugge +2.5, Arsenal–Lille U3.5, Leipzig O2.5, Viking–Bayern U5.5); D ×5.73 propio (Arsenal gana, Barcelona gana, Bayern gana 1.ª mitad, Villarreal–Napoli BTTS, Atlético–ManU tarjetas >2.5 + Atlético o empate).
- Scripts: `seguimiento.py` (estado puntual → `estado.md/json`, `registro_resultados.jsonl`) y `seguimiento_watch.py` (vigilante en segundo plano, log en el scratchpad `vigilancia.log`, emite 1 línea por cambio). Clave: `APIFOOTBALL_KEY_FILE=<scratchpad>/probe/key.txt` (fuera del repo; la clave se pegó en el chat → pedir REGENERARLA al terminar el día).
- Canal de avisos: Monitor con `tail -F vigilancia.log`, expira cada 30 min → re-armar. Respaldo: send_later 19:10, 19:30, 20:05, 20:45, 21:15 UTC; tras 21:15 programar 00:40, 01:40, 04:10 (Athletic 22:30Z, Bucaramanga 23:30Z, San Carlos 02:00Z del 14).
- Fernando dio permiso explícito de seguimiento en vivo. Avisar solo cambios (gol, pata decidida, roja, ticket perdido/ganado), con efecto por ticket (C y D comparten Arsenal–Lille y Viking–Bayern).
- Pendiente: lectura de alineaciones Champions (~18:00Z), informe de cierre (por pata, tasa de éxito, calibración mercado vs resultado), actualizar MANIFIESTO/RESOLUCION/paquete dist, recordatorio 26-oct, él quiere añadir cosas a agentes/modelos (no especificado).

## ESTADO AL CIERRE DEL 13-oct (noche) — leer primero tras compactar
- Todos los tickets del 13-oct se perdieron (sistema 3/7 patas; ticket propio de la persona usuaria 4/5). Auditoría completa: `runs/2026-10-13/AUDITORIA-agentes-y-modelo.md`; registro final por pata: `seguimiento/registro_resultados.jsonl`.
- La persona usuaria aprobó TODAS las correcciones salvo «sin once no hay ticket»: arma los picks HORAS antes; se usa riesgo de rotación a priori y revisión a T-60 (`lineup_check.py`).
- Implementado y probado (258 pruebas): reglas nuevas en los 4 agentes y en SKILL.md; `tickets.py` (dirección, rótulo, P(pérdida), EV, NO APOSTAR, P central, snapshots); `league_sample.py`, `rotation_risk.py`, `lineup_check.py`, `calibracion.py`; seguimiento (cuarto de línea, marcador a 90', registro solo finalizado); tarjetas (2.ª amarilla = 2; suplentes que no jugaron no cuentan). TTL 60 s de `apif_query.py`; tope de consultas de agentes 250 (autorizado).
- Pendiente: integrar rotación a priori en `tickets.py`; mercados de ganador del favorito con filtro de dominancia; ejecutar `league_sample.py` por liga antes de cada jornada; la persona usuaria quería añadir cosas a agentes/modelos (sin especificar). Preferencias: hora de CARACAS siempre; respuestas simples cuando lo pide; tablas; alegría al dar buenas noticias y claridad en las malas; ya NO quiere avisos de pulso salvo que los pida.
- Clave de apifootball: se pegó en el chat; guardada fuera del repo en el scratchpad (`probe/key.txt`). PEDIR que la regenere al terminar y no usarla después. Recordatorio 26-oct (trig_01Ta32gFygrV1tt1moSw9Y1s): no hablar del plan de apifootball antes.

