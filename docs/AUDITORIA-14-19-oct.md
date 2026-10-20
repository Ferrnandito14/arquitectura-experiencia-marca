# Auditoría de cierre — ventana móvil 14–19 oct 2026 (PARCIAL: 6 días de estudio)

Generada el 19-oct-2026 (hora de Caracas) a petición de la persona usuaria, siguiendo la sección 16 del prompt maestro (`docs/PROMPT-MAESTRO-correccion-1.md`). Detalle completo en `dist/auditoria-14-19-oct.xlsx`.

## Resumen

- **Ventana:** 14–19 oct 2026 (6 días de estudio; marcada PARCIAL: el 7.º día es el 20-oct). El 13-oct queda como línea base fuera de esta ventana.
- **Boletos:** 33 boletos del usuario liquidados con monto: 11 ganados, 22 perdidos. Invertido 21,038.77 Bs; cobro 12,382.82 Bs; NETO −8,655.95 Bs (bonos no incluidos). Por día: 15-oct +740.23, 16-oct −336.48, 17-oct −3,323.26, 18-oct −2,055.25, 19-oct −3,681.19.
- **Dónde se pierde:** Boletos de cuota total ≤ ×1.5: 5 de 5 ganados (+1,400 Bs, n=5). De ×1.5 a ×3: 5 de 13 (−112). De ×3 a ×6: 1 de 7 (−4,222). Más de ×6: 0 de 8 (−5,723). Tres patas o más: 2 ganados de 18 boletos (−9,799 Bs).
- **Patas del usuario:** 71 aciertos en 102 patas (69.6 %), en línea con lo que implicaban las cuotas (~71 %): no hay ventaja medible, ni desventaja. Cuota 1–1.25: 94 % (n=17); ≥1.8: 50 % (n=12). El azar no se distingue de un buen precio con estos n.
- **Objetivo ×1.20:** Para crecer con ×1.20 diario hay que acertar el 83.3 % de las veces. Combinadas ×1.2 del libro: 14 de 17 (82.4 %, +2.5 % por unidad); boletos propios ≤×1.5: 5 de 5. Es compatible con el equilibrio, pero con n tan pequeño no demuestra ventaja.
- **Modelo:** Brier del modelo 0.1954 contra 0.1800 del mercado (n=13,455): el mercado es mejor los 6 días. Calibración global aceptable (±3 pp) con sobreestimación en 80–100 % (87.9 % dicho, 85.2 % real). Cuando el modelo supera al mercado en más de 15 pp, acierta 56.9 % (n=353) = el mercado (56.5 %), no el 77.2 % que decía. EV teórico ≥ +10 %: 53.3 % de acierto frente a 71.3 % esperado, ROI −9.8 % (IC −18.3 a −0.9), peor en 17–19 (−12.1 %) que en 14–16 (−7.5 %).
- **Agentes:** Aprobada 73.2 % (n=683) frente a degradada 70.2 % (n=3,347) y 72.7 % de todas: ventaja de 3.0 pp con intervalos solapados. Mitad 14–16: +4.5 pp; mitad 17–19: +2.9 pp: no hay mejora, SIN SEÑAL. Solidez deportiva BAJA 72.8 % frente a MEDIA 72.6 % (ALTA solo 4 patas): no discrimina. Las «rechazadas» aciertan 76.8 %: los rechazos son por precio o fuente, no predicen fallos. La alerta de brecha del cuantitativo sí aporta información.
- **Disciplina:** Exposición registrada: 1,350 → 1,886 → 7,070 → 4,044 → 6,688 Bs entre el 15 y el 19 oct (×4.9), con 7, 7, 9, 5 y 9 boletos por día. Es una observación, no causalidad.
- **Límites:** Faltan boletos sin liquidar o sin monto (13-oct F; 15-oct K; 16-oct N y R; 17-oct A), no hay registro de boletos del 14-oct, los 3 boletos de balance del 18-oct no se incluyen por indicación del usuario, saldo real no confirmado (último: 1,807.98 Bs el 10-oct) y los bonos no se descuentan. Precios de referencia de agregador (no ejecutables) en el catálogo; el modelo sigue sin validar: nada es «apto».

## Recomendaciones (máx. 5)

- **Cambiar ya:** 1. Tratar como ruido las patas con brecha modelo − mercado > 15 pp positiva o EV teórico ≥ +10 %: usar la probabilidad del mercado (sin margen) en esas patas o dejarlas fuera del ranking. Evidencia: n=353 y n=796; acierto 56.9 % y 53.3 %; ROI −9.8 %. Se refuta si en los próximos días esa banda deja de rendir por debajo del mercado.
- **Cambiar ya:** 2. No usar la solidez «BAJA» del analista deportivo como criterio de exclusión de combinadas: BAJA 72.8 % frente a MEDIA 72.6 % (n=4,897 y 1,520). Mantenerla informativa hasta que ALTA tenga n≥100 y acierte más. Se refuta si BAJA empieza a acertar claramente menos con n≥300 por semana.
- **Cambiar ya:** 3. Presentar el ×1.20 como objetivo principal y los ≥×3 como bloque secundario con exposición propia y sin sumarlos al reto: los ≥×3 propios fueron 1 de 15 y los combos del libro ×3–×3.8, 3 de 17. La cuantía la decide el usuario; el sistema solo informa del riesgo.
- **Seguir observando:** 4. Equilibrio del ×1.20 (83.3 %): registrar cada día la tasa del ×1.20 propio y del libro. Hoy 14/17 y 5/5. Se confirma con n≥30 y ≥83.3 %; se refuta con n≥30 y <80 %.
- **Seguir observando:** 5. El mercado supera al modelo en Brier (0.180 frente a 0.195). Hipótesis: mezclar modelo y mercado con un peso calibrado fuera de muestra (no fijado a mano). Se confirma si la mezcla baja el Brier en días no usados para calibrar.

## Datos pendientes y límites

- **Boletos sin liquidar o sin monto en el registro:** 13-oct F; 15-oct K; 16-oct N y R; 17-oct A
- **Boletos del 14-oct:** Sin registro
- **Boletos de balance del 18-oct (3):** Fuera del registro por indicación del usuario
- **Plan de Claude 18-oct (T1–T3 y ×1.2) y montos del 17-oct:** El usuario indicó que no son estrictamente necesarios; no se inventan
- **Saldo real confirmado:** Último: 1,807.98 Bs el 10-oct
- **Bonos de A y D (19-oct) y otros:** No descontados
- **Etiquetas por pata de rotación, alineaciones y correlación:** No existen en el registro: no medible
- **«Escenario de pérdida» del deportivo frente a la causa real del fallo:** Campo de enumeración genérico: se requiere codificación manual para medir
