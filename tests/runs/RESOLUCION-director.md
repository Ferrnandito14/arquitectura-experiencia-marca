# Resolución del director — prueba SINTÉTICA (EJEMPLO — NO REAL)
Fixtures: `tests/fixtures/ejemplo_no_real.md`. Expectativas fijadas antes: `tests/fixtures/EXPECTATIVAS.md`.
Flujo: Ronda 1 (verificador, deportivo, cuanti en paralelo) → auditor sobre E, A, B → Ronda 2 (3 `SendMessage` con objeciones) → resolución. Tercera comprobación: NO necesaria (ningún dato pendiente cambiaría el estado de A/E; la independencia de fuentes no es resoluble con el fixture y se declara como riesgo).

## Las tres preguntas
1. **Más probable (entre los estimables):** E (rango 55–72%, 15/20 frecuencia combinada) ≥ A (55–68%, 13/20). B tiene la frecuencia nominal más alta (8/10 en casa) pero queda **no estimable** tras la baja confirmada del goleador (cuanti, aceptado).
2. **Mejor relación probabilidad/cuota:** **ninguna demostrada.** Los EV de A y E cruzan 0 (cuanti recalculó E: −0.065 a +0.224 a 1.70). A es la de menor exigencia: equilibrio 55.6% (1.80) / 54.6% (1.83) frente a 58.8% (1.70) / 58.1% (1.72) de E, pero su suelo de 55% es también juicio sin base independiente (el auditor lo señaló y aplico el mismo estándar que a E).
3. **Mejor alternativa global:** **A** (localía y calidad de rival documentadas por el deportivo; 2 cotizaciones; equilibrio más bajo), con **E** como sustituto razonable.

## Clasificación
| Cand. | Mercado | Cuota (fixture) | Decisión | Fundamento / riesgo |
|---|---|---|---|---|
| A | BTTS Sí Alfa–Beta | 1.80 (odds-1) / 1.83 (odds-2, otra casa) | **SELECCIONAR** (valor económico NO demostrado) | Datos esenciales en 2 orígenes con cifras (source-a/b), 2 cuotas; localía y rivales documentados. Riesgo: n=10, 3 fuentes de independencia no acreditada, sin goles a favor/en contra |
| E | Over 2.5 Theta–Iota | 1.70 / 1.72 | **SUSTITUIR D por E** y **MANTENER COMO ALTERNATIVA** de A | 2 orígenes + 2 cuotas, pero sin localía/rivales; EV cruza 0 |
| B | Victoria Gamma | 1.55 (1 sola fuente) | **NO EVALUABLE** | Baja confirmada del goleador sin impacto cuantificable; 1 sola cotización; rivales flojos |
| C | Over 9.5 córners | 1.90 / 1.88 | **NO EVALUABLE** | corners-b defectuosa descartada (ceros vs corners-a); queda 1 origen, n=5, sin local/visitante ni liquidación |
| D | Victoria Eta | 1.40 (1 fuente) | **SUSTITUIR** (por E) | n=4/3, H2H 2019 irrelevante, sin 2ª cuota |

Criterios de desempate usados: documentación de contexto > frecuencia bruta; menor probabilidad de equilibrio requerida; no se combinan A y E (misma fuente de datos, sin ticket verificado).
Aceptado en ronda 2: verificador degrada A/E de "Verificado" a "Verificado con salvedad" (la 3.ª fuente `source-c` no aporta cifras propias: mínimo de 3 fichas con datos propios NO cumplido → "Parcial" en ese requisito; los 2 orígenes con cifras sí cumplen el criterio de SELECCIONAR de la skill).
Estado de validación (sintético): A = respaldada por datos y precio verificables en el fixture, sin valor demostrado; E = alternativa; B, C = no evaluable; D = descartado/sustituido.
