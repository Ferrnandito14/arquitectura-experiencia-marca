# Recalibración con 3 días (14–16 oct 2026): validación fuera de muestra

Filas: 3215 patas (lado con P≥50 % de cada línea) de 94 partidos. Entrenar en dos días y probar en el tercero (rotación); la partición pedida es **14+15 → 16**.
No se usa ningún precio como entrada del ajuste (solo P del modelo, familia de mercado y resultado). p del registro = ya pasada por model_calibration donde 'aplicar'.

Criterio de publicación (fijado antes de mirar): Δ Brier con IC95 < 0 sobre todas las predicciones fuera de muestra, Δ log-loss ≤ 0, mejora en ≥ 2 de 3 folds y en 14+15→16.

## Agregado fuera de muestra (3 folds)

| Método | n | P media | Acierto | Brier | Log-loss | ECE | Δ Brier (IC95) | Δ log-loss (IC95) | Folds que mejoran | ¿Publicar? |
|---|---|---|---|---|---|---|---|---|---|---|
| sin_ajuste | 3215 | 0.713 | 0.7002 | 0.1977 | 0.5818 | 0.0206 | — | — | — | — |
| platt_global | 3215 | 0.7034 | 0.7002 | 0.1983 | 0.5826 | 0.0139 | 0.00061 [-0.00036, 0.00153] | 0.00078 [-0.00351, 0.00456] | 1/3 | no |
| isotonica_global | 3215 | 0.7038 | 0.7002 | 0.1989 | 0.5844 | 0.0139 | 0.00121 [0.00026, 0.00224] | 0.00262 [-0.00044, 0.00586] | 0/3 | no |
| platt_por_familia | 3215 | 0.7065 | 0.7002 | 0.1992 | 0.5857 | 0.0091 | 0.00146 [0.0003, 0.00257] | 0.00384 [-0.00027, 0.00756] | 0/3 | no |
| isotonica_por_familia | 3215 | 0.704 | 0.7002 | 0.2032 | 0.6042 | 0.0306 | 0.00545 [0.00285, 0.00826] | 0.0224 [0.01305, 0.03222] | 0/3 | no |

## Fold pedido: entrenar 14+15, probar 16

| Método | n prueba | Brier | Log-loss | ECE |
|---|---|---|---|---|
| sin_ajuste | 735 | 0.1805 | 0.5386 | 0.0382 |
| platt_global | 735 | 0.1823 | 0.5445 | 0.0532 |
| isotonica_global | 735 | 0.1824 | 0.5445 | 0.0541 |
| platt_por_familia | 735 | 0.1818 | 0.5439 | 0.0539 |
| isotonica_por_familia | 735 | 0.1862 | 0.5563 | 0.0645 |

## Otros folds (Brier)

| Fold | sin_ajuste | platt_global | isotonica_global | platt_por_familia | isotonica_por_familia |
|---|---|---|---|---|---|
| 14+15 → 16 (n=735) | 0.1805 | 0.1823 | 0.1824 | 0.1818 | 0.1862 |
| 15+16 → 14 (n=1260) | 0.2145 | 0.2143 | 0.2155 | 0.2154 | 0.2192 |
| 14+16 → 15 (n=1220) | 0.1907 | 0.1915 | 0.1917 | 0.1929 | 0.1968 |

## Bandas de P (agregado fuera de muestra): sin ajuste vs isotónica por familia

| Banda | n | P media (sin ajuste) | Acierto | P media (isot. fam.) | Acierto |
|---|---|---|---|---|---|
| 50-60 % | 792 | 0.55 | 0.557 | 0.563 | 0.554 |
| 60-70 % | 770 | 0.649 | 0.658 | 0.649 | 0.653 |
| 70-80 % | 756 | 0.751 | 0.724 | 0.747 | 0.731 |
| 80-90 % | 575 | 0.848 | 0.816 | 0.844 | 0.835 |
| 90-100 % | 322 | 0.936 | 0.891 | 0.945 | 0.854 |

**Decisión:** NINGÚN ajuste cumple el criterio fuera de muestra: la probabilidad del modelo queda sin cambios (no se publica la recalibración).

Limitaciones: 3 días, un solo régimen de goles por día, familias con pocas filas caen al ajuste global; el registro ya contiene la calibración por grupo vigente (`data/model_calibration.json`).
