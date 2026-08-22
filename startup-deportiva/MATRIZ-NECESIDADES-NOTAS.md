# Notas de integración — Matriz de Necesidades V0.1

Última actualización: 2026-08-22. No modifica `MATRIZ-NECESIDADES.md`
(se guarda verbatim) — registra cómo se integra con el resto del
proyecto, por la misma regla de trazabilidad de la sección 45 del
documento base.

## Corrección de expectativa

`MATRIZ-CONTEXTO-NOTAS.md` (actualización del 21-08-2026) anotaba que
el siguiente paso pendiente era una única "Matriz de Necesidades y
Oportunidades". La entrega real la dividió en dos: esta matriz cubre
solo **Necesidades** (27 tipos concretos, sección 4-30) y su propio
cierre (sección "Siguiente etapa") pide por separado una **Matriz de
Oportunidades V0.1** y luego una **Matriz de Matching V0.1** — no una
matriz combinada. Se corrige aquí para no arrastrar la expectativa
equivocada.

## Roadmap

`CONTEXTO-MAESTRO.md` sección 34 (Fase 6 — Modelo de Necesidades) pasa
de `[PENDIENTE DE PROFUNDIZAR]` a `[TRABAJADA — V0.1]`. Fase 5 (Modelo
de Oportunidades) sigue `[PENDIENTE DE PROFUNDIZAR]` — es exactamente
lo que esta matriz deja pendiente para la próxima entrega.

## Consistencia contra lo ya existente

Sin contradicciones detectadas. Esta matriz profundiza (no reemplaza)
la sección 16 de `CONTEXTO-MAESTRO.md` ("Necesidades") — pasa de un
único ejemplo genérico a 27 necesidades concretas con actor, problema,
objetivo, criterios y resultado, más los ejes transversales de estado,
prioridad y temporalidad (secciones 33-35) que `CONTEXTO-MAESTRO.md`
no tenía.

## Regla nueva con impacto directo en el boceto y el diseño de plataforma

Secciones 36-38 (necesidad explícita vs. implícita, y la "regla de no
asumir") son una restricción de producto que **no estaba** explícita
antes de esta matriz: una recomendación basada en una necesidad
*inferida* (no declarada por el usuario) debe presentarse como
sugerencia ("también podrían interesarte...") y nunca como afirmación
("necesitas..."). Se revisó el copy ya publicado:

- `prototipo/index.html` y el diseño de plataforma (`diseno-plataforma/`) ya usan lenguaje de sugerencia en sus CTA ("Ver academias
  cercanas", "Postular al tryout", "Ver perfiles compatibles") —
  ninguno afirma una necesidad no declarada por el usuario. No requirió
  cambios.
- Queda como criterio de revisión obligatorio para cualquier copy
  futuro que muestre contenido no solicitado explícitamente (p. ej. el
  contexto "Descubrimiento", todavía sin construir).

## Qué no se incorpora todavía

Los 27 tipos de necesidad no se representan uno por uno en el boceto
ni en el diseño de plataforma — ya existían ejemplos parciales
(inscripción, tryout, empleo, necesidad de jugador/fisio/preparador
físico/entrenador) cubriendo un subconjunto. Ampliar la cobertura
completa se pospone hasta que exista la Matriz de Oportunidades V0.1,
siguiendo la misma regla de no adelantarse al diseño conceptual
(sección 46 del documento base).
