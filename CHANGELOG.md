# CHANGELOG

## 2026-10-17 — Mantenimiento del generador de libros «ligas-XX-oct» y del comparativo (datos 14–16 oct)
Archivos entregados antes NO se modificaron: `ligas-14/15/16/17-oct-v2.xlsx`, `comparativo-…-resultados.xlsx` y sus copias en `dist/versiones/` quedan congelados; `dist/ligas-14-oct.xlsx` intacto (sha256 147f21d97e5bed13…). Copias de datos previas en `data/versiones_datos/…__20261017-051224UTC`.

### Nuevos archivos
`dist/ligas-14/15/16/17-oct-v3.xlsx` (el 17-oct sustituye al v2 para uso; los otros tres son retrospectivos), `dist/comparativo-ligas-14/15/16-oct-resultados-v3.xlsx` (liquidación corregida), `data/historial_patas.csv`, `data/analisis/*.json`, `docs/ANALISIS-tres-dias.md`, `docs/RECALIBRACION-modelo-3-dias.md`.

### Liquidación (comparativo)
- Córners: «sin dato» solo si ambos lados suman 0; un lado en 0 es dato válido; conflicto de bloques solo si el total es menor que el de la 1.ª parte.
- Tarjetas: si «1 amarilla + 1 roja en el mismo minuto» puede contarse como 2 o 3 puntos, la pata sale «regla no confirmada» (SIN DATO), no se asume.
- Prórroga/penales: goles de la tanda y prórroga fuera del 90'; si el marcador a 90' no es directo, los mercados dependientes quedan «regla no confirmada»; córners/remates en After ET/Pen. sin dato.
- Combinadas: PERDIDA si alguna pata pierde; SIN DATO si ninguna pierde pero alguna no tiene dato; ANULADA solo si todas se anulan. Fueras de juego: «regla no definida».
- Partidos en juego/aplazados no cuentan (banner PROVISIONAL). Hoja «Reglas de liquidación» y tabla de SIN DATO por motivo.
- 36 pruebas con casos reales (`tests/test_liquidacion_reglas.py`, fixtures de resultados reales).

### Rankings y precio
- Máximo 2 patas por partido en Ranking seguridad y atractivo-cuota; composición (filas / partidos distintos) en la hoja Cobertura.
- Precio de referencia (mediana de casas) en rankings y combinadas; la captura del usuario es una columna opcional y no cambia P ni orden. «P mercado sin margen», casas con par, P Pinnacle y «Modelo − mercado (pp)» con alerta > 10 pp (libro y hoja «Precio por casa»).
- Léeme/Leyenda: texto de versión al día, tarjetas A=1/R=2, precios por tipo, sin la frase de «requisito de casa».

### Registro
- `ledger_patas.jsonl`: campos nuevos (partido, cuota_usuario, p_mercado, p_pinnacle, n_casas, entry_id, dia_caracas). `dia` es la fecha UTC heredada; agrupar por `dia_caracas`.
- `data/historial_patas.csv` se regenera en cada comparativo (una fila por pata y día).

### Análisis fuera de muestra (`analisis_tres_dias.py`)
- Recalibración Platt/isotónica (global y por familia), 3 folds: no mejora → no se publica.
- Agentes: aprobada − degradada no distinguible de cero.
- Régimen del día: sin sesgo agregado; factor de corrección empeora fuera de muestra → no se publica.

### Herramientas y pruebas
- `auditoria_libros.py` (hallazgos B*/C* de libros y comparativos). Suite: 575 pruebas OK (1 omitida), antes 558.

## Pendiente o dudoso
1. Regla de tarjetas «1 amarilla + roja directa en el mismo minuto»: confirmar con la casa (2 vs 3 puntos).
2. Fueras de juego y remates: sin regla de liquidación confirmada.
3. El mercado agregado supera al modelo (Δ Brier +0.021, IC95 excluye 0): decidir si se acepta un modelo propio más cercano al consenso (requiere validación y su aprobación; hoy solo hay alerta).
4. El modelo sobreestima 80–100 % y cuotas ≥ 1.8: la recalibración simple no mejora fuera de muestra; hacen falta más días.
5. Etiqueta de agentes sin poder predictivo demostrado; propuestas previas pendientes de aprobación: elegibilidad por agente, separar «dato dudoso» de «riesgo deportivo», tope de exposición, evidencia más estricta en 1.ª parte, recorte de P en cuotas altas.
6. 15-oct: un partido sin resultado final (comparativo marcado PROVISIONAL); 6 partidos del 17-oct sin muestra suficiente para probabilidades (solo nota en su hoja).
7. Claves de apifootball y TheStatsAPI expuestas en el chat: regenerar. Reto: picks de los días 1–11 y 14; resultado Atalanta–Venezia.
