---
name: evaluacion-probabilidad-valor
description: Método para separar probabilidad, precio y valor en un pick de fútbol - probabilidad de equilibrio, cuota sin margen, rangos de probabilidad defendibles, EV teórico, correlación y combinadas. Incluye script de cálculo determinista. Úsala al evaluar cuotas o comparar picks/tickets.
---

# Probabilidad vs. valor

Tres preguntas separadas: (1) ¿cuál es más probable? (2) ¿cuál tiene mejor relación probabilidad/cuota? (3) ¿cuál es la mejor alternativa global tras evidencia y riesgo?

## Pasos
1. **Frecuencia observada** (k/n, con intervalo): `scripts/calc.py freq k n`.
2. **Probabilidad implícita bruta** = 1/cuota: `calc.py implied C`.
3. **Sin margen** (solo con todas las selecciones del mismo mercado de la misma casa): `calc.py novig C1 C2 [C3]`; método proporcional, declarar que es aproximación.
4. **Estimación propia**: solo si hay base (varias fuentes independientes, n suficiente, ajuste por rival/bajas). Entregar **rango** (p. ej. 55–65%) y método/supuestos. Si no es defendible: "no estimable" y no calcular EV.
5. **EV teórico** = p×cuota − 1 (`calc.py ev p C`), con el rango: calcular con extremos. Si el rango cruza EV=0, no hay ventaja demostrada.
6. **Combinadas**: `calc.py combo ...` (misma casa). Probabilidad conjunta = producto solo si independientes (`joint`); mismos partido/equipo/árbitro/condiciones → correlación, declararla y no usar el producto.
7. Sin cuota verificada → "fundamento deportivo, sin valor económico confirmado".

## Prohibido
Cuota atractiva = valor; probable = rentable; promedio = probabilidad; modelos con los mismos datos = evidencias independientes; cuota histórica como actual; precisión falsa (decimales sin base).
