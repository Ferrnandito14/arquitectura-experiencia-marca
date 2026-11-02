# SUPERVISOR del ×4 / ×1,20 «estadística primero» — lunes 2-nov-2026 (hora Caracas = UTC−4)
Lo lee la sesión de la nube en CADA despertar (cada 2 min vía send_later). Estado en `runs/2026-11-02/estado.json`. Regla: hacer UN paso útil por despertar, anotar en `estado.json`, re-armar `send_later` 2 min (mensaje: «SUPERVISOR: lee runs/2026-11-02/SUPERVISOR.md y estado.json y ejecuta el siguiente paso; re-arma 2 min»).
Fernando NO está frente a la computadora: avisar por CORREO (Gmail, barcaferr14@gmail.com) cuando termine todo o ante cualquier bloqueo >15 min, desconexión de las manos >10 min, error de API repetido, o decisión que sea suya.

## Escalera (estado en estado.json → pasos[])
1 fetch  : `estadistica_primero.py fetch` (100 equipos, 8 partidos, stats) COMPLETO. Vigilar procesos: `ps aux | grep estadistica_primero`; si hay <1 proceso y faltan archivos, relanzar 3 (`--orden adelante|atras|azar`, `THESTATSAPI_KEY_FILE=/tmp/claude-0/-home-user/d56b1dd2-9e37-5240-9a83-4b470c476a77/scratchpad/probe/thestatsapi_key.txt`, `setsid nohup`). Completo = 100 `lista_*.json` y un `stats_*.json` por cada partido de esas listas (los fallos de stats quedan {ok:false}).
2 analisis: `estadistica_primero.py analisis --run runs/2026-11-02 --desde 14:00` → `pool/est_patas.json`. Revisar: ¿cuántos partidos con patas? ¿córners/tarjetas con n≥8?
3 shortlist (POR p_dep, SIN mirar cuotas): hasta 2 patas por partido con p_dep ≥ 0.62 (y las de córners/tarjetas solo si n≥8 en ambos); ≈60 patas. Guardar `pool/est_shortlist.json`.
4 precios: pedir a la sesión local (session_01YYA3bun9e9SrA838rgGhJk) leer cuotas EXACTAS de la casa (solo lectura, ambos lados cuando sea córners/tarjetas/goles equipo; «no existe» sin sustituir; hora de lectura). Guardar `pool/est_precios.json`.
5 ensamblado ×4 (3-5 patas, cuota 1.20-2.10 por pata, partidos distintos, ≤1 «Más de», producto 4.0-4.8, stake 3563.38): maximizar ∏p_dep; EV_dep = ∏p·∏cuota −1; reportar también EV de mercado solo como contraste. ×1,20 informativo (1-3 patas, producto ≥1.22, máx p_dep) y evaluar retroactivamente Reims o empate y Bragantino Más de 1,25 con el método.
6 agentes EN ABSOLUTO sobre los 3 mejores tickets: deportivo (Sonnet) y auditor (Opus), con `est/` y `pool/est_patas.json`. Puerta: ninguna pata BAJA/sin datos/descartada; si ningún ticket pasa → NO se apuesta, correo a Fernando con el motivo.
7 cupón: manos limpian cupón (ya pedido), cargan el ×4 aprobado, describen cupón y verifican: mismas patas/líneas, cuotas no bajan >0.05 por pata ni >5% el total.
8 APOSTAR (autorizado por Fernando, 2-nov, SOLO este ×4, 3563.38 Bs, antes del primer partido): la sesión local lo hace únicamente si Fernando lo confirmó en SU chat; si no lo confirmó, dejar cargado y avisar por correo. Registrar ID/monto/cuota en `plan_x4/registro_plan_x4.jsonl` y `data/`.
9 página «Retos del Día» (Artifact) + commit (trailers de atribución) + correo final con tickets, patas, estadística por pata y estado.
Hora límite dura: el primer partido del ticket final (≥14:00 Caracas = 18:00 UTC). A las 17:00 UTC (13:00 Caracas) si no hay ticket verificado → correo de alerta.

## Autosupervisión (en cada despertar)
- ¿Procesos fetch vivos? ¿archivos crecen? ¿manos conectadas (get_session connection_status) y no pegadas (updated_at >10 min sin avance con status RUNNING → interrupt_session y reenviar la tarea)?
- ¿Algún paso lleva >15 min en el mismo estado? → diagnosticar y corregir; si no se puede, correo.
- Nunca repetir un paso ya hecho; nunca avanzar un paso si su puerta no pasó.
