# Backtest de los modelos propios (v1)

Generado: 2026-10-14T04:11:45Z · **Validación global: insuficiente** · política: "decisión de política (no un hecho estadístico): se puede endurecer; con menos partidos el resultado es «no_concluyente»"

## A. Walk-forward contra la tasa base de la liga (sin cuotas)

| Familia | Partidos | Brier modelo | Brier base | Skill [IC 95 %] | Frente a la tasa base |
|---|---|---|---|---|---|
| 1x2 | 819 | 0.2152 | 0.2186 | 0.0158 [-0.0025, 0.0361] | no_concluyente |
| btts | 819 | 0.2394 | 0.2387 | -0.0028 [-0.0277, 0.0211] | no_concluyente |
| cards_total | 784 | 0.2305 | 0.2287 | -0.0076 [-0.0334, 0.0186] | no_concluyente |
| corners_total | 804 | 0.2471 | 0.2414 | -0.0236 [-0.0497, 0.0006] | no_concluyente |
| dc | 819 | 0.2225 | 0.2264 | 0.017 [-0.0092, 0.0441] | no_concluyente |
| goals_total | 819 | 0.2035 | 0.2047 | 0.0061 [-0.0177, 0.0288] | no_concluyente |
| team_goals | 819 | 0.2051 | 0.2079 | 0.0136 [-0.0019, 0.0298] | no_concluyente |

## B. Frente al mercado (solo cuotas previas al inicio)

| Familia | Partidos | Brier modelo | Brier mercado | Dif. [IC 95 %] | ROI selecciones con ventaja (n) | Frente al mercado |
|---|---|---|---|---|---|---|
| 1x2 | 103 | 0.2229 | 0.2157 | [0.0072, -0.0046, 0.019] | -0.1772 (149) | no_concluyente |
| btts | 99 | 0.246 | 0.2427 | [0.0032, -0.012, 0.0182] | 0.0578 (49) | no_concluyente |
| dc | 103 | 0.224 | 0.2131 | [0.0109, -0.0057, 0.0275] | -0.0738 (90) | no_concluyente |
| goals_total | 103 | 0.2126 | 0.2065 | [0.006, -0.0082, 0.0207] | 0.0238 (145) | no_concluyente |

Exclusiones: {"partidos_usados": 105, "excluidos": {"sin_resultado_final": 769, "sin_historial": 113, "consulta_de_cuotas_posterior_al_inicio": 4, "sin_filas_de_casa_previas_al_inicio": 21, "sin_consulta_de_cuotas": 0}}

## C. Decisión de validación

- **1x2**: insuficiente (base: no_concluyente; mercado: no_concluyente)
- **btts**: insuficiente (base: no_concluyente; mercado: no_concluyente)
- **cards_total**: insuficiente (base: no_concluyente; mercado: no_evaluable_sin_cuotas_historicas)
- **corners_total**: insuficiente (base: no_concluyente; mercado: no_evaluable_sin_cuotas_historicas)
- **dc**: insuficiente (base: no_concluyente; mercado: no_concluyente)
- **goals_total**: insuficiente (base: no_concluyente; mercado: no_concluyente)
- **team_goals**: insuficiente (base: no_concluyente; mercado: no_evaluable_sin_cuotas_historicas)

Una muestra pequeña no demuestra rentabilidad; los intervalos se muestran siempre y «no_concluyente» es un resultado válido.
