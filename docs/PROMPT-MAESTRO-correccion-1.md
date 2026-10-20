# Corrección 1 al prompt maestro (recibida de la persona usuaria, 19-oct-2026, hora de Caracas)

Estado: texto COMPLETO (la sección 16 llegó entera en un segundo mensaje).

Sustituye el encabezado y la sección 2; añade las secciones 2.1 y 16; el resto del prompt maestro queda igual.

## Encabezado (objetivo del reto)
Crecer el saldo con una apuesta diaria de cuota ≈ ×1.20 (interés compuesto, mínimo ×1.20 por día). Es una meta, no un resultado garantizado.

## 2. Uso obligatorio de las skills
Usar siempre `reto-de-90-dias-20` (principal) y `cobertura-exhaustiva-picks` (apoyo) para borradores, análisis, combinadas, revisión de resultados y auditorías. Leer sus instrucciones, consultar el historial del proyecto (registros pre-partido, resultados, balances y comparativos de cada día) y no repetir investigación vigente. Si no se puede ejecutar una skill, decirlo y no afirmar haberla usado.

## 2.1 El estudio en Claude Code
Repositorio local `football-picks-system` (sin push a remoto). Flujo: inventario del día → modelo propio de probabilidades → libro diario `ligas-XX-oct` (Excel, una hoja por liga, rankings, combinadas, cuota mínima justa) → seguimiento en vivo de tickets → auditoría. Inicio del estudio: 14 oct 2026. Horas siempre en Caracas.

Agentes (revisan unidad por unidad = partido × grupo de mercado; un validador comprueba cobertura):
- Verificador de mercados: hora, estado, existencia de mercados y precios; marca cuotas anómalas o sin fuente.
- Analista deportivo: forma, localía, rotación, contexto; solidez ALTA/MEDIA/BAJA y escenario de pérdida.
- Analista cuantitativo: P modelo frente al precio, cuota mínima, alerta si la brecha supera 15 pp.
- Auditor adversarial: mejor argumento para NO elegir el pick; puede objetar a los otros.

Veredictos resultantes: aprobada / degradada / objetada / rechazada. Los rechazados o degradados salen de las combinadas.

Reglas fijas: cada pata ≤ 2.10; las combinadas pasan por agentes y por el sistema de riesgos; las cuotas de agregador son referencia, no ejecutables; mientras el modelo no esté validado, nada se marca «apto para apostar». Cuánto se apuesta lo decide el usuario; el sistema da probabilidades, riesgos y saldo por escenario.

## 16. Auditoría de cierre (diaria al terminar los resultados; completa a los 7 días)
La auditoría de 7 días ya está programada a las 00:10 (Caracas) del 20-oct. No duplicarla: si ya existe el informe, actualizarlo solo con lo nuevo. Usar la ventana móvil de los últimos 7 días. Si hay menos (el 20 oct habrá 6: 14 al 19 oct), marcarla como PARCIAL y dar el n real.

### A. Escáner de aciertos y fallos
- Patas: acierto % frente a la probabilidad implícita y a P modelo / P usada.
- Boletos: ganados/perdidos y neto en Bs, separando los del plan de Claude, los del usuario y los del libro.
- Fallos: pata causante, mercado, liga, banda de cuota, nº de patas, rotación/alineaciones, correlación entre patas.
- Aciertos: buen precio o azar.
- Desglose por mercado, liga y banda de cuota (1–1.25, 1.25–1.4, 1.4–1.8, ≥1.8); simples frente a combinadas; ×3+ aparte.

### B. Evaluación de los 4 agentes (cada uno por separado)
- Verificador: cuotas marcadas como anómalas o sin fuente frente a lo confirmado después (¿evitó errores de precio?).
- Analista deportivo: acierto de patas con solidez ALTA frente a MEDIA y BAJA; ¿los «escenarios de pérdida» coincidieron con los fallos reales?
- Analista cuantitativo: acierto de patas con brecha >15 pp frente a ≤15 pp, y si la cuota mínima habría filtrado fallos.
- Auditor adversarial: acierto de las patas objetadas y si sus argumentos (muestra débil, fuente única, cuota no ejecutable) se confirmaron. Separar objeción deportiva de objeción por verificación.
- Veredicto final: acierto y ROI por día y acumulado; diferencia aprobada − degradada y su tendencia.
- Mejora: comparar la primera mitad de la ventana con la segunda. Dar n e intervalo; si no se distingue del azar, decir «sin señal».
- Indicar qué agente aporta información propia y cuál repite al modelo.

### C. Calibración
- Modelo frente a mercado (Brier); sobreestimación por banda de probabilidad y de cuota.
- Precio ejecutable frente a referencia y si el signo es estable.

### D. Disciplina
- Exposición real frente a la acordada (ej.: 15 oct ≈ 1.570 Bs frente a 1.200).
- Boletos fuera del plan, pérdidas perseguidas, montos no registrados, saldo real no confirmado.

### E. Recomendaciones (máx. 5)
- Cada cambio con su evidencia, el n y qué dato lo confirmaría o refutaría en los próximos días.
- Separar «cambiar ya» de «seguir observando». No cambiar criterios retrospectivamente ni declarar ventaja con muestras pequeñas.
- Lo no concluible va como hipótesis pendiente.

Formato: tabla breve + 5–8 viñetas de conclusiones, solo lo que cambió respecto al balance anterior.

### Datos pendientes del usuario (no inventarlos)
Resultados del 18 oct (T1–T3 y el ×1.2), montos de los boletos del 17 oct, y saldo real (último confirmado: 1.807,98 Bs el 10 oct).
