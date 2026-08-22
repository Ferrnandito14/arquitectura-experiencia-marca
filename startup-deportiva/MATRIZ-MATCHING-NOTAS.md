# Notas de integración — Matriz de Matching V0.1

Última actualización: 2026-08-22. No modifica `MATRIZ-MATCHING.md`
(se guarda verbatim) — registra cómo se integra con el resto del
proyecto, por la misma regla de trazabilidad de la sección 45 del
documento base.

## Roadmap

`CONTEXTO-MAESTRO.md` sección 34 (Fase 8 — Modelo de Matching) pasa
de `[PENDIENTE]` a `[TRABAJADA — V0.1]`. Fase 7 (Modelo de
Recomendaciones) sigue `[PENDIENTE]` — es exactamente lo que esta
matriz (su sección 79) deja abierto como siguiente paso, distinguiendo
matching ("¿es compatible?") de recomendación ("¿qué debería ver
primero?").

## Consistencia contra lo ya existente

Sin contradicciones detectadas. Confirma y detalla lo que
`CONTEXTO-MAESTRO.md` secciones 31-32 ya esbozaban (motor de matching,
matching vs. recomendación) y conecta directamente con:

- **Sección 36 (regla de no asumir) de `MATRIZ-NECESIDADES.md`** ↔
  Regla 6 y sección 36 de esta matriz ("datos faltantes no deben
  convertirse en incompatibilidad" — desconocido ≠ incompatible).
- **Sección 30 (Verificación) de `MATRIZ-OPORTUNIDADES.md`** ↔ sección
  37 de esta matriz ("confianza del match ≠ compatibilidad").
- **Sección 38 (Estado) de esta matriz** ("tryout cerrado → no
  recomendar") ↔ el campo Estado ya definido en `CONTEXTO-MAESTRO.md`
  sección 15 (oportunidad) y en `MATRIZ-OPORTUNIDADES.md`.

## Regla de mayor impacto inmediato en el prototipo

**Sección 67 (Explicabilidad)**: toda recomendación debería poder
mostrar "por qué" — no solo el resultado. Esta es la pieza que faltaba
en el boceto interactivo (`prototipo/index.html`), que hasta ahora
filtraba pero no explicaba ni clasificaba resultados. Se incorpora en
esta misma entrega (ver siguiente sección).

**Sección 66 (clasificación conceptual: MUY ALTO / ALTO / MEDIO /
BAJO / NO MATCH)** y **sección 33 (pesos por tipo de oportunidad)**:
se usan como base directa para la lógica de scoring agregada al
prototipo.

## Prototipo actualizado en esta misma entrega

`prototipo/index.html` se actualiza para dejar de ser solo un filtro y
pasar a un motor de matching real en el navegador, siguiendo
únicamente las reglas ya definidas en esta matriz (sin inventar
fórmulas nuevas — sección 78 prohíbe fijar una fórmula definitiva, así
que se usa una suma simple de criterios ✓/✗ visible en el propio
código, no un algoritmo oculto):

- Cada tarjeta de oportunidad ahora se evalúa contra el perfil activo
  usando los criterios ya existentes en los datos del boceto (edad,
  categoría, distancia, precio, horario, nivel — según el tipo de
  persona).
- El resultado se clasifica en las 5 categorías de la sección 66
  (con equivalentes visuales: colores/etiquetas), nunca con un
  porcentaje falso.
- Cada tarjeta muestra una línea de explicabilidad (sección 67):
  "Te lo mostramos porque..." listando los criterios que sí cumple.
  Sigue la "regla de no asumir" (`MATRIZ-NECESIDADES.md` secciones
  36-38): es explicación de coincidencia, no una afirmación de
  necesidad no declarada.
- Datos faltantes (ej. precio no publicado) se marcan como
  "dato no disponible", nunca como incompatibilidad (regla 6 /
  sección 36 de esta matriz).
- El panel de Club, que antes tenía el CTA "Ver perfiles compatibles"
  deshabilitado a propósito ("Fase 8 todavía no está definida"), ahora
  muestra 3 perfiles de jugador ficticios evaluados con las mismas
  reglas — es el desbloqueo directo de tener ya una Matriz de Matching
  V0.1.
- No se implementa: matching bidireccional real, historial de
  aprendizaje, ni pesos numéricos definitivos — la propia matriz
  (sección 78) los deja fuera de esta fase.

## Qué no se incorpora todavía

El matching bidireccional completo (secciones 48-49, club↔jugador con
postulación activa de ambos lados) y las bandas de actor completas de
la sección 44 (ej. scout, fisioterapeuta) no están representadas como
flujo propio en el prototipo — se limita a los cuatro personas ya
existentes. Se amplía cuando exista la Matriz de Recomendaciones V0.1
(sección 79, siguiente paso que la propia matriz pide).
