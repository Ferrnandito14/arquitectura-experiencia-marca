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
