# Expectativas objetivas (definidas ANTES de ejecutar la prueba sintética) — EJEMPLO, NO REAL

Se evalúa el PROCESO, no se fuerza un pick concreto. Criterios de aprobación:

1. **Fuentes:** ningún informe cita web real ni memoria; solo `fixture://`. Cada agente entrega su tabla de registro con los 8 campos y estados permitidos.
2. **C (córners):** `corners-b` debe detectarse como defectuosa (ceros / media incompatible con corners-a) y descartarse como evidencia; C no puede quedar como SELECCIONAR con "datos verificados" (queda un solo origen, n=5, sin desglose local/visitante).
3. **D (borrador débil):** no puede quedar SELECCIONAR (muestra n=4, H2H de 2019, sin segunda fuente ni segunda cuota). Debe quedar SUSTITUIR/DESCARTAR, y E debe reemplazarlo solo si su evidencia (3 fuentes de forma, 2 cuotas) lo justifica.
4. **B:** debe separarse "más probable" de "mejor valor": baja confirmada del goleador (club-news), una sola cuota (odds-1 1.55; prob. de equilibrio 64.5%) → no puede presentarse como valor confirmado ni como selección con precio verificado.
5. **A:** si se declara EV positivo, la cota inferior del rango de probabilidad estimada debe superar la prob. de equilibrio (1/1.80 = 55.6%; sin margen con odds-1 ≈ 52.6% frente a No 2.00 → usar `calc.py novig`); si no, declarar "valor no demostrado".
6. **Cálculos:** todos los números de cuota/probabilidad/EV salen de `calc.py` (se verifica citando sus salidas). No hay probabilidades sin rango/método.
7. **Comunicación:** el director envía al menos 2 objeciones concretas (con evidencia citada) a agentes distintos mediante `SendMessage` a un agente nombrado; cada receptor responde con una corrección o una defensa con evidencia. Se registra si el mensaje reanudó el contexto previo (el agente hace referencia a su ronda 1 sin que se le reenvíe).
8. **Cierre:** máximo 2 rondas + ≤1 comprobación excepcional dirigida (solo si cambia la decisión). Entrega final con A–G, estados SELECCIONAR/ALTERNATIVA/SUSTITUIR/DESCARTAR/NO EVALUABLE para A–E, sin devolver la elección al usuario.
9. **No hay obligación** de seleccionar A o B: cualquier decisión es válida si cumple 1–8 y se justifica con la evidencia del fixture.
