# Resolución del director — jornada local 2026-10-13 (America/Caracas), datos REALES

**Veredicto: no hay picks. El resultado es RANKING PROVISIONAL RESTRINGIDO (puerta de cobertura, exit 4) y no puede describirse como «la jornada completa».** No es «no hay oportunidades»: es que las fuentes que se pueden consultar de forma automatizada y conforme a sus condiciones no permiten evaluar los partidos.

## Qué se hizo y con qué alcance
- Inventario con fuentes permitidas: 240 únicos (Football-Data 199, todos anteriores a la ventana; APWin 41). 15 caen en la ventana local `[2026-10-13T04:00Z, 2026-10-14T04:00Z)`, todos de **una sola fuente** (APWin) y 0 con verificación de calendario suficiente para selección final.
- **El universo es una cota inferior**: APWin declara 166 partidos para el 13-oct y 126 para el 14-oct y su HTML permitido solo muestra la primera página (15). Prueba concreta: Millwall–Swansea (Championship, citado por la persona usuaria como partido de esa jornada) **no aparece** en el inventario permitido.
- Nivel 1 sobre los 15: 7 con forma doméstica **proxy** de otra competición (Lens–Sporting, Galatasaray–Barcelona, Atlético–Man United, Villarreal–Napoli, Inter–Club Brugge, RB Leipzig–PSV, Arsenal–Lille) y 8 **no investigados** (4 de AFC Champions League, Sabah–Slavia, Viking–Bayern, Portimonense U23–Académico Viseu U23, Lens U19–Sporting U19). 0 evaluados con histórico de la misma competición. Mercados: 345; 0 examinados de la misma competición; 161 solo proxy; 184 `NOT_CHECKED`.
- Revisión por agentes: cada fila de cada lote (15/15 deportivo, 15/15 cuantitativo, 2/2 verificador para las discrepancias) + auditor adversarial en tres rondas. Los defectos que encontraron están corregidos y regenerados (ver `docs/PRUEBAS-picks.md`).

## Las cinco preguntas
1. **¿Qué selección parece más probable?** No se puede responder: no hay probabilidades defendibles. Las frecuencias k/n del proxy (n 5–8, otra competición, casa+fuera mezclados, sin ajustar por rival) son descriptivas y no sustituyen el análisis del partido.
2. **¿Cuál tiene mejor relación probabilidad/cuota?** No se puede responder: ninguna fuente permitida aporta cuotas de ninguna casa para estos partidos; no se calcula EV.
3. **¿Cuál es la mejor alternativa global?** Ninguna es seleccionable con la evidencia actual.
4. **¿Qué se conserva, sustituye o descarta?** Nada se selecciona ni se descarta por mérito deportivo. Ningún candidato anterior (C1–C4) tiene prioridad: Bragantino–Cruzeiro (00:00Z) es del **12-oct** en Caracas y queda fuera; Galatasaray–Barcelona e Inter–Brugge solo tienen proxy; Inter–Brugge **victoria**, **Over 9.5 córners** y su **combinada** no tienen cuota (sin valoración económica de la combinada); Millwall–Swansea no fue descubierto por las fuentes permitidas.
5. **¿Qué no puede evaluarse y por qué?** Los 8 no investigados (ningún adaptador de fuente permitida los cubre; no se comprobó si las ligas extra de Football-Data cubrirían alguno), y para los 7 con proxy: resultado/hándicap (ligas distintas sin rivales comunes), cuotas, árbitro, bajas y alineaciones, y cualquier mercado de la misma competición.

## Estado de validación por candidato (todos los 15)
**NO EVALUABLE** para selección. Detalle por partido y motivo en `matrix.json`/`state.json`; no hay SELECCIONAR, MANTENER, SUSTITUIR ni DESCARTAR por mérito.

## Decisiones de conformidad que quedan para la persona usuaria
- Football-Data: su `robots.txt` bloquea por nombre a crawlers de IA y declara el uso destinado a particulares; se descargaron 12 CSV (≤20) con identidad honesta y ritmo bajo. **Aceptación del riesgo: PENDIENTE.**
- APWin: sus términos prohíben el «uso no autorizado» sin definir automatización; se leyeron 4 páginas públicas. Ampliar a paginación: **PENDIENTE de decisión** (no se hizo).
- Para cobertura exhaustiva real: API deportiva con licencia (clave de la persona usuaria), calendario/CSV aportado con `inventory.py --manual`, o permiso escrito de proveedores.
