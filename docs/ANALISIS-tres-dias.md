# Análisis fuera de muestra, 14–16 oct 2026 (precio, agentes, régimen del día)

Fuente: `data/ledger_patas.jsonl` (6 716 patas liquidadas ganada/perdida, 94 partidos; `data/historial_patas.csv` es la misma tabla). Código: `scripts/analisis_tres_dias.py` (`recalib|precio|agentes|regimen|todo`); resultados crudos en `data/analisis/*.json`. Todos los IC remuestrean PARTIDOS completos. Con 3 días es descriptivo: no valida ni descarta el modelo.

## 1. Lado favorecido (P ≥ 50 % y cuota ≤ 2.10), liquidación corregida
n = 2 960 patas · acierto 73.7 % · P modelo 72.3 % · Brier 0.1878 · ECE 0.034. Por día: 14-oct 70.1 % (P 72.1), 15-oct 76.8 % (P 73.1), 16-oct 74.8 % (P 71.6).
Por banda de P: 50-60 → 55.3 vs 62.5 real; 60-70 → 65.0 vs 68.4; 70-80 → 75.1 vs 74.9; 80-90 → 84.8 vs 82.2; 90-100 → 93.6 vs 89.1. La sobreestimación de las bandas altas se mantiene (≈ 3 y 4.5 pp), la de las bajas va al revés (subestima).
Por cuota (referencia): 1.0-1.4 → real 83.4 % (implícita 86.1); 1.4-1.8 → 62.1 (64.0); 1.8-2.1 → 49.4 (52.3) con P modelo 59.9: ahí el modelo sobreestima ≈ 10 pp.
Nota: las cifras difieren algo de las del encargo (73.8 / 72.4) porque la liquidación se corrigió (córners con un lado en 0, tarjetas ambiguas, prórroga/penales, Atlante–Pumas y Tijuana–Puebla ya finales) y `dia` se agrupa por día de Caracas.

## 2. Precio: tres tipos, informados por separado
| Tipo | n patas | Qué es |
|---|---|---|
| Referencia (mediana de casas del agregador) | 3 215 (lado P≥50 %) | precio base de rankings y combinadas |
| P de mercado sin margen (par over/under, mediana entre casas) | 2 969 con par | comparación con el modelo; nunca entra en la P final |
| Pinnacle sin margen (TheStatsAPI) | 118 | comparación; muestra pequeña |
| Captura de la persona usuaria | 127 | capa opcional de validación; media cuota captura − referencia = −0.027 |

Modelo vs mercado (misma muestra, 2 969 patas): Brier modelo 0.1973 vs mercado 0.1761; Δ = +0.0212 (IC95 +0.0122 a +0.0308) → **el mercado agregado predice mejor que el modelo y la diferencia es distinguible de cero**. Log-loss 0.5807 vs 0.5249. Contra Pinnacle (118 patas): Δ Brier +0.0205 (IC95 −0.0035 a +0.0447): no distinguible de cero.
Discrepancias > 10 pp (977 de 2 969): cuando el modelo está por ENCIMA del mercado (656 patas, P modelo 70.0 %, mercado 50.6 %) acertó 48.2 % (el mercado tenía razón); cuando está por DEBAJO (321 patas, modelo 64.0 %, mercado 80.3 %) acertó 86.3 %. Esto sustenta la columna «Modelo − mercado (pp)» y la alerta >10 pp del libro. No se usa para cambiar la P del modelo (principio de independencia): es un aviso. Si se quisiera un ajuste hacia el consenso habría que decidirlo con validación aparte.
ROI a cuota de referencia, lado P≥50 %: −5.4 % (captura: −8.4 %, n pequeña).

## 3. Recalibración (isotónica / Platt por banda y familia) — NO se publica
Ver `docs/RECALIBRACION-modelo-3-dias.md`. Entrenando 14+15 y probando 16 (y la rotación completa) ningún método mejora el Brier ni el log-loss: Platt global 0.1983 vs 0.1977 sin ajuste (IC95 del Δ −0.0004 a +0.0015, 1/3 folds), isotónica por familia 0.2032 (peor, IC95 excluye 0 hacia peor). Mejora el ECE (0.021 → 0.009–0.014) pero sin mejorar Brier/log-loss; por criterio fijado antes de mirar, la probabilidad queda sin cambios.

## 4. Agentes (lado favorecido, IC95 por partido)
| Etiqueta | n | Acierto | P modelo | Residuo |
|---|---|---|---|---|
| aprobada | 238 (32 partidos) | 76.1 % [68.8–82.5] | 71.7 | +4.3 pp |
| degradada | 1 635 | 71.6 % [68.7–74.6] | 71.9 | −0.3 |
| rechazada | 800 | 77.7 % [74.3–81.6] | 73.5 | +4.3 |
| objetada | 31 | 61.3 % [45–87.5] | 74.3 | −13 |
| sin revisión | 222 | 72.1 % [64.0–81.9] | 70.1 | +1.9 |

Aprobada − degradada = +4.4 pp (IC95 −2.8 a +11.5): **no distinguible de cero**. Aprobada − rechazada = −1.7 pp (−9.5 a +5.3): tampoco. Por día aprobada vs degradada: 76.7 vs 66.2 (14), 84.0 vs 74.4 (15), 69.1 vs 73.3 (16): cambia de signo el 16. Conclusión: la etiqueta de agentes no tiene poder predictivo demostrado con estos datos; no se usa como filtro duro (sigue como aviso/orden de presentación).

## 5. Régimen del día (goles esperados vs reales, 92 partidos con λ del modelo)
| Día | Partidos | Esperado | Real | Real/esperado |
|---|---|---|---|---|
| 14-oct | 31 | 3.21 | 3.90 | 1.22 |
| 15-oct | 38 | 2.92 | 3.08 | 1.06 |
| 16-oct | 23 | 3.06 | 2.17 | 0.71 |
| total | 92 | 3.05 | 3.13 | 1.03 |

No hay sesgo sistemático: en los tres días juntos el modelo acierta el nivel (3.05 vs 3.13); el error es de régimen diario con signos opuestos (infraestima el 14, sobreestima el 16). Factor de corrección k = Σreal/Σesperado entrenado en los otros dos días (0.92, 1.01, 1.13) y probado en las patas de goles totales del día no visto: Brier +0.0104 (14), −0.0001 (15), +0.0239 (16) → empeora en 2 de 3 días y en conjunto (Δ +0.0094, IC95 +0.0047 a +0.0143). **No se publica ningún factor**: el régimen de un día no se predice con los otros.

## 6. Correlación en rankings
Tope de 2 patas por partido en Ranking seguridad y atractivo-cuota (`MAX_RANK_POR_PARTIDO`), con filas y partidos distintos en la hoja Cobertura («F. Composición»). Antes (v2) → después (v3), seguridad / atractivo: 14-oct 15→17 / 16→16 partidos distintos (máx. 4→2); 15-oct 9→10 / 7→10 (máx. 8→2; las filas bajan de 25 a 18 porque pocas patas elegibles quedan tras el tope); 16-oct 12→13 / 11→13 (máx. 4→2); 17-oct 24→23 / 20→21 (máx. 3→2). Los IC por partido del comparativo (`Resumen de acierto`, columna «Partidos distintos») usan clusters por partido.
Nota: v3 de los días 14–16 es retrospectivo (solo auditoría); no se compara su acierto con el de v2 para no ajustar criterios con el día ya conocido.
