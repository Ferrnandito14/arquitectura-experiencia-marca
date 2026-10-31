# Plan ×4 con bono 9 % (1-nov a 5-nov-2026) — MEMORIA APARTE DEL RETO ×1,20

Regla de Fernando (31-oct/1-nov): estos tickets van a una memoria separada. NO se mezclan con
`data/registro_tickets_usuario.jsonl`, `data/ledger_*.jsonl` ni el balance del ×1,20 (21.361,51 Bs al 31-oct).
Si de aquí sale algo útil para el ×1,20, se le dice a Fernando y se decide juntos antes de incluirlo.

## Reglas del plan
- Un ticket ×4 por día; se reinvierte todo el premio. Bono 9 % sobre la ganancia (cuota con bono = base × 1,09 aprox.).
- Casa exige: mínimo 2 patas y cuota ≥ 1,20 por pata. Nuestra regla: cada pata ≤ 2,10.
- Día 0: sáb 31-oct, 183,58 Bs, cuota 4,16, 5 patas (ticket completo) → premio 834,35 Bs si gana. Día 1 = dom 1-nov con ese premio (confirmado por Fernando).
- Días 2-5: lun 2, mar 3, mié 4, jue 5-nov. Hoja de referencia: Google Sheets compartida por Fernando
  (Día 0 a Día 5; premio final día 5 = 1.314.560,92 Bs si se gana todo).
- Horas siempre en Caracas.

## Archivos
- `registro_plan_x4.jsonl`: una línea por ticket/día (patas, cuotas, apostado, resultado).
- Capturas: pendientes (Fernando enviará la del día 0).

## Aritmética de riesgo (sin afirmar ventaja)
Un ×4 gana ~22-25 % de las veces; ganar 6 seguidos (días 0-5) ≈ 0,01-0,02 %. El riesgo de bolsillo es solo el día 0 (183,58 Bs).

## Decisiones de Fernando (31-oct-2026)
- **Modo completo** de agentes para el plan ×4 (verificador Haiku, deportivo Sonnet, auditor Opus sobre los finalistas); no recortar precisión por ahorrar tokens.
- Cada día se proponen 2 tickets: principal de 2 patas y alternativo de 3 patas (cuota base ≈ ×4,00; cada pata entre 1,20 y 2,10; partidos distintos). Fernando elige.
- Rutina diaria: inventario y filtro (scripts) → sentido común de datos → pool de patas → agentes sobre finalistas → alineaciones ~1 h antes del primer partido → ticket → registro y monto del día siguiente.
- Fuentes: TheStatsAPI (plan de 7 días renovado el 31-oct; aviso el jueves 5-nov), football-data para ligas grandes. apifootball recortada a 2 ligas.
- Recordatorio del 5-nov programado (trig_01JaSsMJvQQukU5FiV9Mz5aa).
