# Transcripción de texto — auditor (a19bfbb9fb1397585) — datos sintéticos


## [mensaje recibido]
CONTEXTO: PRUEBA CON DATOS SINTÉTICOS "EJEMPLO — NO REAL". Prohibido usar web o memoria. Verifica tú mismo contra SOLO /home/user/football-picks-system/tests/fixtures/ejemplo_no_real.md (NO leas EXPECTATIVAS.md ni otros archivos de tests/). Cálculos con python3 /home/user/football-picks-system/.claude/skills/evaluacion-probabilidad-valor/scripts/calc.py.

RESUMEN DE RONDA 1 (informes de tres especialistas, que pueden contener errores; compruébalos):
- verificador: A Verificado (cuotas 1.80 odds-1, 1.83 odds-2); B Parcial (una sola cotización 1.55; baja confirmada del goleador de Gamma); C Parcial (córners con una sola fuente válida; corners-b defectuosa, descartada); D No verificable (n=4, H2H 2019, una cuota); E Verificado (3 fuentes de forma, cuotas 1.70/1.72).
- deportivo: prioridad por solidez: E, A, B (con reserva por la baja), C (sin verificar), D (descartar).
- cuanti: rangos de prob.: A 55–68% (EV de -0.010 a +0.224 a 1.80, "cruza 0"), B 58–72% (EV -0.101 a +0.116), E 60–72% (EV +0.020 a +0.224 a 1.70; "único con EV>=0 en todo el rango"), C y D no estimables. Los rangos son juicio suyo (media de frecuencias recortada), no un modelo.

TU TAREA: para E, A y B responde «¿cuál es el argumento más fuerte para NO seleccionarlo?»; verifica las afirmaciones que sostienen la decisión (cifras, k/n, cuotas, consistencia de fuentes, independencia de fuentes, calidad de rivales, bajas); señala la mejor alternativa si existe. Cada objeción con evidencia citada (fuente fixture://) o la verificación concreta pendiente, e impacto (alto/medio/bajo). No reabras lo ya resuelto sin evidencia nueva.
ENTREGA: por candidato → objeción principal (con evidencia), secundarias, qué dato la resolvería, quién debe responderla (verificador/deportivo/cuanti), veredicto sugerido (no vinculante). Conciso.

## [mensaje recibido]
<system-reminder>
Other agents active in this session, addressable via SendMessage({to: name, message}): main, cuanti, deportivo, verificador.
</system-reminder>

### [tool_use] Read {"file_path": "/home/user/football-picks-system/tests/fixtures/ejemplo_no_real.md"}

### [tool_use] Bash {"command": "python3 /home/user/football-picks-system/.claude/skills/evaluacion-probabilidad-valor/scripts/calc.py --help"}

### [tool_use] Bash {"command": "cd /home/user/football-picks-system/.claude/skills/evaluacion-probabilidad-valor/scripts; for a in \"7 10\" \"6 10\" \"8 10\" \"9 10\" \"4 5\" \"3 5\"; do echo \"freq $a\"; python3 calc.py freq $a; done; python3 calc.py novig 1.80 2.00; python3 calc.py novig 1.83 1.95; python3 calc.py novig 1.70 2.10; python3 calc.py novig 1.72 2.10; python3 calc.py novig 1.55 4.20 6.50; python3 calc.

## [respuesta]
Todo lo anterior sale de `fixture://ejemplo_no_real.md` y de `calc.py`. No usé web ni memoria. Hice solo lecturas y cálculos, porque el modo plan está activo.

## Hallazgos transversales

1. **Los rangos de cuanti no son probabilidades.** Parten de frecuencias k/n de 10 partidos. Los Wilson 95% del fixture son muy anchos: 7/10 da [0.40, 0.89], 6/10 da [0.31, 0.83] y 8/10 da [0.49, 0.94]. Impacto: alto.
2. **Las tres fuentes de forma no están declaradas independientes.** source-b dice de sí misma "independiente". source-c solo dice "consistente" y no aporta k/n propios. Para E, la fuente c sirve solo como confirmación cualitativa. Impacto: medio.
3. **Las probabilidades implícitas sin margen son un punto de referencia.** Salen del método proporcional, que es una aproximación. Impacto: bajo.

| Pick | Cuota | Prob. sin margen (proporcional) | Rango de cuanti | Margen de la casa |
|---|---|---|---|---|
| E | 1.70 | 55.3% (odds-1), 55.0% (odds-2 con 1.72) | 60–72% | 5.8–6.4% |
| A | 1.80 | 52.6% | 55–68% | 5.6–5.9% |
| B | 1.55 | 62.2% | 58–72% | 3.7% |

El suelo de cuanti para E (60%) está solo 5 puntos sobre el mercado. Ese suelo no está justificado por ningún modelo.

## E: Más de 2.5 goles, Theta–Iota (cuota 1.70)

**Objeción principal.** El "único con EV≥0 en todo el rango" depende de un suelo de 60% que sale de una media recortada de dos frecuencias. Esas frecuencias son Theta 8/10 (Wilson [0.49, 0.94]) e Iota 7/10 (Wilson [0.40, 0.89]). Con la probabilidad de equilibrio de 58.8% a 1.70, el EV es 0 y la conclusión ya cambia con un par de puntos de diferencia. Source-a no da rivales, localía ni goles a favor y en contra de ninguno de los dos equipos. Es una conclusión con muestra y contexto débiles, y no un resultado robusto.

**Secundarias:**
- **Independencia.** Source-b da lo mismo que source-a (8/10 y 7/10). Source-c solo dice "consistente". Si las tres comparten proveedor, valen como una sola evidencia. El fixture no lo acredita ni lo niega. Impacto: medio. Debe responderlo el verificador.
- **Contexto ausente.** No hay localía, calidad de rival, xG ni goles medios en ninguna ficha. La frase "sin bajas relevantes reportadas" aparece en source-a y en club-news. Es ausencia de reporte, no confirmación de plantillas. Impacto: medio.
- **Cuotas.** Hay 1.70 en odds-1 y 1.72 en odds-2, de casas distintas. No se deben mezclar casas. Si el EV se calcula a 1.70, el margen frente al suelo es mínimo. Impacto: bajo.
- **Muestra.** n=10 supera el umbral de 8, pero sigue siendo débil. Impacto: medio.

**Dato que lo resolvería:**
- Goles a favor y en contra por localía de Theta (local) e Iota (visitante).
- Calidad de los rivales de esos 10 partidos.
- Que el verificador confirme si las fuentes de forma son independientes.

**Quién responde:** deportivo (contexto) y verificador (independencia).

**Veredicto sugerido:** E es la opción más sólida de las tres, pero solo con un EV marginal y con incertidumbre alta. Mantenerlo como principal con reserva declarada. No está justificado lenguaje de "valor claro".

## A: BTTS Sí, Alfa–Beta (cuota 1.80)

**Objeción principal.** Los datos de Alfa y Beta son sólidos y consistentes en las tres fuentes, pero el 55% del suelo de cuanti está solo 2.4 puntos sobre el 52.6% del mercado sin margen. Con los k/n de 7/10 y 6/10, el EV a 1.80 es negativo en la parte baja del rango. Cuanti ya lo reconoce al decir que "cruza 0". No hay argumento a favor de A que el propio rango no desmienta.

**Secundarias:**
- **Rivales.** Alfa tuvo 6 rivales de mitad de tabla o mejores. Eso refuerza su 7/10, pero source-a no desglosa cuáles de esos 7 BTTS fueron contra esos rivales. Beta tiene "nivel similar" sin detalle. Impacto: medio.
- **Localía.** Alfa tiene 4 de 5 con BTTS en casa (Wilson amplio) y Beta 3/5 fuera. Con n=5, estos subconjuntos son muy débiles. Impacto: medio.
- **Doble cuota.** 1.80 (odds-1) y 1.83 (odds-2) son de casas distintas. La 1.80 figura como "comunicada" en el candidato. Hay que anotar cuál se usa. Impacto: bajo.
- **Bajas.** club-news solo cubre a Gamma. Para Alfa y Beta dice "sin bajas relevantes reportadas", que es ausencia de reporte. Impacto: bajo.

**Dato que lo resolvería:** goles marcados por Alfa y por Beta (partidos en que no marcaron, y contra quién), más porterías a cero. Debe responderlo el deportivo.

**Veredicto sugerido:** descartar como principal si E se mantiene. Como alternativa queda en segundo lugar. Es defendible solo con la cuota 1.83.

**Mejor alternativa:** E.

## B: Victoria local Gamma, vs Delta (cuota 1.55)

**Objeción principal.** La baja confirmada del máximo goleador de Gamma (club-news, comunicado del club, 2099-01-01 10:00) afecta justo al equipo cuyo 8-1-1 en casa sostiene el pick. Esa forma se logró con ese delantero y contra "rivales de tabla media-baja" (source-a). Además, cuanti da 58–72% frente al 62.2% sin margen del mercado. Su suelo queda 4 puntos por debajo del mercado, con un EV mínimo de -0.101 que cuanti ya reporta. El fixture no cuantifica el impacto de la baja, y no hay que inventarlo.

**Secundarias:**
- **Una sola cotización.** 1.55 solo está en odds-1. odds-2 no cubre el mercado. El mínimo operativo exige ≥2 fuentes comparables para una selección finalista. Impacto: alto.
- **Muestra y rival.** Delta como visitante hizo 3 victorias, 2 empates y 5 derrotas en 10. Eso favorece a Gamma, pero la comparación con rivales de nivel desigual no queda ajustada. Impacto: medio.
- **Fuentes.** Gamma 8-1-1 y Gamma–Delta están confirmados en source-b y source-c, aunque esas fuentes no hablan de la baja. Impacto: bajo.
- **Tamaño de la muestra.** 8/10 en casa tiene Wilson [0.49, 0.94] y no hay desglose del 8-1-1 con y sin el delantero. Impacto: medio.

**Dato que lo resolvería:**
- Segunda cotización para B.
- Rendimiento de Gamma sin su delantero (si lo hay).
- Fecha y estado de la baja respecto al partido.

**Quién responde:** verificador (cuota) y deportivo (efecto de la baja).

**Veredicto sugerido:** no seleccionar con la información actual. Es el candidato más expuesto a un dato omitido (la baja) y no cumple el mínimo de dos fuentes de cuotas.

## Orden y alternativas

El orden de menor a mayor objeción es E, luego A, luego B. Todo lo que sostiene la decisión se confirmó contra el fixture, pero ningún candidato muestra un EV positivo sin un supuesto no justificado.

- **Mejor alternativa:** no hay una superior en el fixture. C y D siguen descartados: C tiene una sola fuente válida y D tiene n=4 con un H2H de 2019.
- **Posible combinación (no recomendada):** una combinada de E y A obligaría a considerar la correlación y a no mezclar casas. Solo tendría sentido si las dos cuotas fueran de la misma casa, y el fixture no lo garantiza.

Lo único que no pude verificar es si los proveedores de las tres fuentes son realmente independientes. Quedó señalado como verificación pendiente, y el fixture no lo resuelve.