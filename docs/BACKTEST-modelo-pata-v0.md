# Backtest del modelo pata por pata v0 (13-oct, 114 partidos finalizados)

Modelo: Poisson con ataque/defensa de los últimos ≤10 partidos encogidos hacia la media de la competición (k=8). Mercado: cuotas medias sin margen. Menor = mejor.

```
partidos finalizados con datos: 798 filas de mercado
mercado       n  Brier modelo Brier mercado Brier mezcla  LL modelo LL mercado LL mezcla
1x2 1       114        0.2217        0.2088       0.2116     0.6356     0.6041    0.6123
1x2 2       114        0.2279        0.2247       0.2231     0.6472     0.6443    0.6358
1x2 X       114        0.2222         0.223       0.2222     0.6352     0.6412     0.636
TODOS       798        0.2238        0.2169       0.2182     0.6387     0.6229    0.6251
btts        114        0.2455        0.2407       0.2415     0.6848     0.6748    0.6762
over 1.5    114        0.1769        0.1716       0.1728     0.5359     0.5207    0.5243
over 2.5    114        0.2505        0.2349       0.2404      0.698     0.6622    0.6747
over 3.5    114        0.2219        0.2145       0.2161     0.6343     0.6132    0.6167
```

**Lectura honesta:** con muestras de ≤10 partidos el modelo v0 NO supera al mercado (Brier 0.2238 vs 0.2169) y la mezcla 50/50 queda en medio. Sirve como segunda opinión por pata (señala discrepancias con el mercado) pero no como sustituto del precio. Para mejorarlo hace falta la muestra de liga/temporada completa (`league_sample.py`) y el ajuste por rotación. Un solo día: no concluyente.
