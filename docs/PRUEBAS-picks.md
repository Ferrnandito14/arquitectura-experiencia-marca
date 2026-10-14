# Pruebas — estado real (v2.4, jornada 2026-10-13 America/Caracas)

Tres categorías que NO se mezclan. **Ninguna prueba sintética valida la investigación deportiva real. La ejecución real produjo borradores PROVISIONALES, no un ranking definitivo ni picks con valor demostrado.**

## 1. Pruebas técnicas y offline (código y reglas)
`python3 -m unittest discover -s tests` → **227 pruebas, OK (1 omitida)**, sin red. Cubren: `calc.py`; robots.txt; política de fuentes (denegado por defecto, topes, ritmo); cliente HTTP (reintentos, caché, UA honesto); **redacción de la clave** (`common.redact_url`); inventario (ventana local Caracas, deduplicación conservadora, paginación APWin con 2–3 páginas fixture, alineación apifootball↔APWin sin fusiones ambiguas, normalización de nombres); `level1` (cola reanudable, poda de huérfanos, `ProviderLimit`, historial de la misma competición vs mixto); adaptador apifootball (llamada, estados, historial, cuotas medias/medianas) con fixtures; `coverage_report` (puerta de cobertura); `batches` (integridad: ausente/duplicado/desconocido/pendiente); **`tickets.py`** (patas, búsqueda por rango, pares del mismo partido de familias distintas con justificación, partidos sin repetir entre perfiles, diversidad, calendario de 2 fuentes, exclusión de juveniles/sub-23/reservas, top por seguridad y atractivo, cuotas manuales, vetos, **≥4 casas por pata, exclusión de patas «12», piso de apoyo por equipo, puerta automática de veracidad y separación por tipo de historial**).
Limitación: estas pruebas verifican reglas y matemática, no que las estadísticas de fútbol sean correctas.

## 2. Pruebas sintéticas (datos ficticios «EJEMPLO — NO REAL», `tests/fixtures/`, evidencia en `tests/runs/`)
Flujo multiagente de la fase anterior con 4 agentes y solo `fixture://` (0 llamadas web). Demuestra el mecanismo (objeción → respuesta → resolución) y no aporta ningún dato deportivo real.

## 3. Ejecución REAL (jornada 2026-10-13, America/Caracas)
Fuentes permitidas: APWin (paginación autorizada por la persona usuaria), apifootball (clave propia, plan de prueba), Football-Data. Registro en `runs/2026-10-13/` (ver `MANIFIESTO.md`).
| Etapa | Resultado real |
|---|---|
| Inventario | 1012 partidos únicos (apifootball 748, APWin 313, Football-Data 199 brutos). 1009 CONFIRMADOS, 3 FECHA_DISCREPANTE; 690 no elegibles prepartido (189 iniciados/finalizados). **319 requieren evaluación.** Universo truncado: APWin 167 de 172 declarados (13-oct) y 11 de 15 (12-oct). |
| Calendario | 129 de los 319 con verificación suficiente (2 fuentes) para selección final; 190 con una sola fuente. Independencia de proveedores no verificada. |
| Nivel 1 | 285 con historial propio por equipo (138 misma competición, 147 mixto), 272 evaluados con suficiencia, 13 con intento insuficiente; **34 sin fuente permitida** (NO_INVESTIGADO). |
| Mercados | 7337 posibles: 6555 examinados (89.3 %), 782 NOT_CHECKED, 2380 evaluables/parciales, 4175 NO_EVALUABLE (sobre todo córners/tarjetas sin cobertura). |
| Cuotas | Medianas de ≥3 casas vía UN agregador (no ejecutables). Córners/tarjetas: cuota APROXIMADA por modelo, rotulada. |
| Puerta de cobertura | **RANKING PROVISIONAL RESTRINGIDO** (exit 4). |
| Revisión por lotes | 11 lotes × (deportivo, cuantitativo) + 30 discrepancias (verificador): **319/319 revisados por ambos, 0 faltantes/duplicados/pendientes, 443 correcciones o advertencias**. Fichas compactas, sin fuentes externas. |
| Nivel 2 y auditoría | 4 agentes sobre 21 finalistas + auditor adversarial sobre los borradores regenerados. Hallazgos aplicados: DC mal calculada, vetos (18 entradas), ≥4 casas por pata, piso por equipo, exclusión de patas «12», tope de reutilización de patas. |
| Combinada de la persona usuaria | `custom_check.py` + 3 agentes: apoyo conjunto 0.265 frente a equilibrio 0.787; DÉBIL / sin valor demostrado / DESACONSEJADO tal como está (`ANALISIS-combinada-usuario.md`). |
| Pares del mismo partido | 3 agentes (deportivo, cuantitativo, auditor) sobre 5 pares candidatos: 1 se mantiene con condiciones (Birmingham–Preston +2.5 + menos de 4.5), 4 vetados (`pair_rules.json`). |
| Mercados nuevos y ×4 de hoy | Córners/tarjetas/remates integrados (escalera completa, regla de tarjetas de la casa); 3 agentes sobre los borradores: Durban, Blackburn +1.5 y Chippenham vetadas; resultado: 0 ×4 con todos los filtros (`RESOLUCION-director.md`). |
| Experimento Champions | Filtros relajados solo para la UEFA CL (a petición): 1 combinada y 1 borrador ×4, con 3 agentes: ninguno defendible (EV ≈ −15 %), experimento con stake simbólico. Fallo corregido: tope de candidatas por tipo de precio y `--exclude-match` solo para tickets. |
| Resultado | Seguridad: 5 borradores; amplio: 2 borradores (piso por equipo relajado a 0.45); variante Champions: 4 de seguridad y 0 de amplio. Ninguno tiene ventaja demostrable (EV descriptivo ≈ negativo salvo una pata) ni alcanza el punto de equilibrio de la probabilidad conjunta. |

## 4. NO ejecutado / NO verificado (con motivo)
| Elemento | Motivo |
|---|---|
| Alineaciones, bajas, árbitro, motivación | Ninguna fuente usada las entrega antes del partido. |
| Cuotas ejecutables de una casa concreta; cuotas reales de córners/tarjetas | Solo promedio de agregador; córners/tarjetas sin mercado en la API. Pásalas con `--manual-odds`. |
| Marcadores a 90' de los historiales con copas (patas «12») | Hipótesis de empates registrados como victoria sin comprobar; las patas «12» quedan fuera de tickets. |
| Hora de 3 partidos de Zambia | apifootball y APWin discrepan 13 h; falta tercera fuente. |
| Términos de uso de apifootball | Página de términos devolvió 404; el límite real del plan no está medido (≈650 descargas reales sin alcanzarlo). |
| Revisión de las demás fuentes «no revisadas» (UEFA/AFC/…) | `docs/PROCEDIMIENTO-ALTA-FUENTE.md`; pendiente de decisión. |
| Agent Teams | No activado. |

## Reglas de integridad
No simules visitas, herramientas ni conversaciones; no inventes datos, cuotas ni probabilidades; no uses memoria como dato actual. El apoyo (límite inferior de Wilson de una frecuencia descriptiva; techo 0.722 con n=10) NO es probabilidad predictiva y el «EV descriptivo» NO es EV real.

## v2.5 — correcciones de la auditoría del 13-oct (258 pruebas OK, 1 omitida)
Pruebas nuevas (datos FICTICIOS, EJEMPLO — NO REAL): dirección correlacionada (máx. 2 unders/overs por ticket), rótulo honesto («seguridad» solo con P≥85 % y EV≥0), P(pérdida) y EV por ticket, aviso de riesgo (sin «no apostar»), encogimiento hacia el mercado y descarte por brecha ≥15 pp, rankings por P central, snapshots.jsonl (se añaden, no se sobrescriben), muestras de liga completa (`league_sample.py`: media de liga, equipo y árbitro; tarjetas ausentes ≠ 0), riesgo de rotación (`rotation_risk.py`), calibración (`calibracion.py`: Brier, log-loss, ROI, regla n≥30 y congelación con ROI<−10 %), liquidación de hándicap de cuarto de línea y marcador a 90', registro de resultados solo con partido finalizado, tarjetas (2.ª amarilla = 2 puntos; suplentes que no jugaron no cuentan; titular luego sustituido sí cuenta). `lineup_check.py` y `apif_query.py` (TTL 60 s del día) se probaron en vivo contra apifootball el 13-oct, no con fixtures.
**No cubierto por pruebas automáticas:** integración de la penalización por rotación a priori dentro de `tickets.py` (por ahora es una herramienta aparte que se aplica a mano en la revisión), reincorporación de mercados de ganador del favorito al ranking, y las reglas de texto de los agentes (se validan en uso).

## v2.6 — rotación y favoritos integrados en `tickets.py` (265 pruebas OK, 1 omitida)
Pruebas nuevas (fixtures, EJEMPLO — NO REAL): veto de unders y de patas de ganador del equipo con rotación alta (solo ese equipo), rebaja y rótulo con rotación media, sin `rotation.json` no cambia nada, favoritos que pasan todos los filtros y los que no (rotación, dominancia, dato faltante, brecha grande, probabilidad baja), `dif_goles` por equipo en `league_sample.summarize`. **Comprobado en vivo (13-oct, apifootball):** `rotation_prior.py` dio Bayern alto (descanso corto, ≈4.7 cambios por partido), Watford alto, Cardiff medio, Arsenal alto (≈7 cambios; ganó igual: el riesgo de rotación es una señal, no una predicción). **No cubierto:** prior de liga y de árbitro dentro de `p_central`; la tabla de favoritos no se probó con `league_samples` reales (solo fixtures).

