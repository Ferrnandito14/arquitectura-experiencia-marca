# Rutina automática del ×1,20 (pedida por Fernando el 4-nov-2026)

Hora SIEMPRE de Caracas (`TZ=America/Caracas date`). Sin preguntar salvo bloqueos reales.

## Disparador (NO es una hora fija)
La rutina arranca **justo después de que termina el partido del ticket apostado** (y esté liquidado en el historial de la casa):
1. Al cargar el cupón del día, agendar con `send_later` un **chequeo 30 min antes del inicio** del partido de la pata: preguntar a las manos si el ticket está ABIERTO (ID, monto). Si NO está apostado → avisar a Fernando (el proceso está parado) y reintentar cada 20 min hasta el inicio.
2. Cuando el ticket está abierto: agendar con `send_later` el **arranque = hora de inicio del partido + 2 h 15 min** (+ prórroga si hay: copas/eliminatorias). A esa hora pedir a las manos el estado del ticket; si no está liquidado, reintentar cada 15 min.
3. Si el ticket llega **GANADO/devuelto**: arrancar el ciclo siguiente con **TODO el saldo disponible** (monto = saldo que reporten las manos).
4. Si llega **PERDIDO**: avisar a Fernando UNA vez (chat + PushNotification) — «cayó el día» — y arrancar igualmente el ciclo siguiente con el saldo que quede (sin pedir permiso), salvo que Fernando indique parar.

## Ciclo (lo que se hace tras el disparador)
1. Manos (`session_01YYA3bun9e9SrA838rgGhJk`, solo lectura): estado/pago del ticket, saldo disponible (solo el número, no guardarlo en capturas), lista de partidos aún no empezados.
2. Registrar el resultado en `data/tickets_x12_balance.jsonl` (sin saldos de capturas). *Excepción pedida por Fernando el 4-nov: el ticket 5612767363 (São Paulo–Corinthians Más de 1,25, 0-0) NO se registra como perdido.*
3. Pipeline del día siguiente/del día: `memoria_equipos.py actualizar`; `scratchpad/run_nov5.sh` con la fecha nueva (pool + estadística); lista ANCHA (p_suav≥0,65, cuota 1,20–2,10, ≥2 casas); deportivo en lotes; contexto de las aprobadas; auditor final con **cuotas reales leídas por las manos** (solo patas con cuota ≥1,22 en Triunfobet, fecha y hora confirmadas).
4. Reglas: estadística primero (el mercado solo mide precio); torneos cortos con datos internacionales + domésticos; una pata (a lo sumo dos de partidos distintos); ranking por p_propia y pago esperado; **sin líneas .25/.75** (Más de 1,25 con 1 gol = medio perdido); partido con inicio ≥90 min después de la carga; revisar dudas de fecha/hora.
5. Manos: cargar el cupón SIN monto (confirmado por las manos el 4-nov: su regla fija les prohíbe escribir cualquier monto y pulsar «Realizar apuesta», incluso con permiso de Fernando; no se les vuelve a pedir). Esta sesión entrega a Fernando el monto exacto calculado (= saldo disponible leído por las manos) y la pata; Fernando solo teclea el monto y pulsa. Si pasa el inicio del partido sin ticket abierto, avisar: proceso parado.
6. Registrar el ticket (ID, monto, cuota, patas) en `data/tickets_x12_balance.jsonl`, commit con trailers de atribución y `git push respaldo HEAD:refs/heads/respaldo-football-picks-system`.
7. Volver al paso «Disparador».

## Notificaciones (actualizado 5-nov por Fernando)
- Fernando mantiene la computadora encendida hasta el **31-dic-2026 (nueva fecha de cierre del reto)**.
- **Aviso por CORREO** (barcaferr14@gmail.com, `mcp__Gmail__send_message`) cuando: un ticket se GANA, se PIERDE, o hay un PROBLEMA en la escalera de trabajo/proceso parado (clave, contenedor, pipeline, ticket sin apostar al inicio del partido, error de datos). Mensaje corto: ticket ID, pata, resultado/pago (sin saldos de cuenta), y qué sigue. Además PushNotification si es un problema.
- En el chat no avisar por iniciativa. Si Fernando pregunta el estado: verificar con las manos.

## Límites conocidos
- La clave de TheStatsAPI vive solo en el scratchpad de esta sesión (`.../probe/thestatsapi_key.txt`); si el contenedor se recicla, hay que volver a pedírsela (proceso parado).
- Si `/home/user/football-picks-system` no existe: restaurar la rama `respaldo-football-picks-system` de `Ferrnandito14/arquitectura-experiencia-marca` (add_repo con push).
- Plan TheStatsAPI se renueva el jueves 5-nov; claves expuestas pendientes de regenerar.
