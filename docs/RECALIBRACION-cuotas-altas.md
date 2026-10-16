# Recorte de P en cuotas altas — prueba fuera de muestra

Banda de cuota 1.8–2.1, lado favorecido por el modelo (P ≥ 50 %). Runs en el registro: 2026-10-14, 2026-10-15. Ajuste con un run, evaluación en el otro (y al revés). **Análisis: no se aplica al modelo.**

## Por pliegue (se ajusta con el otro run)

| Evaluado en | n ajuste | n prueba | Frecuencia real | P media | Método | P media recortada | Brier | Log-loss |
|---|---|---|---|---|---|---|---|---|
| 2026-10-14 | 128 | 130 | 46.9% | 58.4% | sin recorte |  | 0.2772 | 0.7521 |
| 2026-10-14 | 128 | 130 | 46.9% | 58.4% | frecuencia de la banda | 50.0% | 0.25 | 0.6931 |
| 2026-10-14 | 128 | 130 | 46.9% | 58.4% | desplazamiento | 45.9% | 0.2641 | 0.7219 |
| 2026-10-14 | 128 | 130 | 46.9% | 58.4% | encogimiento a 1/cuota | 50.6% | 0.2464 | 0.686 |
| 2026-10-14 | 128 | 130 | 46.9% | 58.4% | logística (Platt) | 51.8% | 0.2478 | 0.6888 |
| 2026-10-15 | 130 | 128 | 50.0% | 62.5% | sin recorte |  | 0.2828 | 0.7819 |
| 2026-10-15 | 130 | 128 | 50.0% | 62.5% | frecuencia de la banda | 46.9% | 0.2509 | 0.695 |
| 2026-10-15 | 130 | 128 | 50.0% | 62.5% | desplazamiento | 51.0% | 0.2673 | 0.7323 |
| 2026-10-15 | 130 | 128 | 50.0% | 62.5% | encogimiento a 1/cuota | 41.5% | 0.2651 | 0.727 |
| 2026-10-15 | 130 | 128 | 50.0% | 62.5% | logística (Platt) | 41.6% | 0.2655 | 0.7313 |

## Agrupado fuera de muestra

| Método | n | P media | Frecuencia real | Brier | Δ Brier vs sin recorte | IC 95 % Δ (por partido) | Log-loss |
|---|---|---|---|---|---|---|---|
| sin recorte | 258 | 60.4% | 48.4% | 0.2799 | — | — | 0.7669 |
| frecuencia de la banda | 258 | 48.5% | 48.4% | 0.2505 | -0.0295 | [-0.0561, -0.0043] | 0.6941 |
| desplazamiento | 258 | 48.4% | 48.4% | 0.2657 | -0.0142 | [-0.032, 0.0046] | 0.727 |
| encogimiento a 1/cuota | 258 | 46.1% | 48.4% | 0.2557 | -0.0242 | [-0.0617, 0.0134] | 0.7063 |
| logística (Platt) | 258 | 46.7% | 48.4% | 0.2566 | -0.0234 | [-0.0599, 0.0125] | 0.7099 |

## Lectura

Mejoran el Brier con IC que excluye 0: frecuencia de la banda.
Δ Brier negativo = el recorte mejora. El IC remuestrea partidos completos. Con 2 runs cada pliegue se ajusta con un solo día; el resultado puede cambiar al sumar jornadas.
La pendiente de la logística en la banda es la prueba de si la P del modelo ordena patas DENTRO de la banda: pendiente ≤ 0 = no discrimina (solo sirve la tasa base de la banda). El encogimiento con w > 1 sobrepasa 1/cuota y no es defendible como regla.
El recorte solo se promovería a la recalibración vigente tras repetirse en más días; hoy es un candidato.

## Parámetros candidatos (ajustados con todo el registro; NO aplicados)

n=258, frecuencia real 48.4%, P media 60.4%.

- frecuencia de la banda: {'c': 0.4845}
- desplazamiento: {'delta': 0.1197}
- encogimiento a 1/cuota: {'w': 1.5026}
- logística (Platt): {'a': 0.1578, 'b': -0.494}
