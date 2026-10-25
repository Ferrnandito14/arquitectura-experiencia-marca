# Notas de integración — Matriz de Recomendaciones V0.1

Última actualización: 2026-08-22. No modifica `MATRIZ-RECOMENDACIONES.md`
(se guarda verbatim) — registra cómo se integra con el resto del
proyecto, por la misma regla de trazabilidad de la sección 45 del
documento base.

## Roadmap

`CONTEXTO-MAESTRO.md` sección 34 (Fase 7 — Modelo de Recomendaciones)
pasa de `[PENDIENTE]` a `[TRABAJADA — V0.1]`. Con esto, **las Fases 4
a 8 quedan todas trabajadas** — el roadmap llega completo hasta el
borde de Fase 9 (Experiencia / UX).

## Inconsistencia de numeración detectada (sin corregir el original)

La sección 71 de esta matriz llama al siguiente paso "ETAPA 07 —
Matriz de Actores y Roles" y al que le sigue "ETAPA 08 — Matriz de
Información/Datos", usando la palabra **ETAPA** en vez de **FASE** y
una numeración propia (07, 08) que no coincide con la numeración de
`CONTEXTO-MAESTRO.md` sección 34 (donde Fase 7 es justo esta matriz de
Recomendaciones, y Fase 9 es Experiencia/UX). Es el mismo tipo de
hueco de trazabilidad ya registrado para `MATRIZ-CONTEXTO.md` (letras
A-O vs. contextos numerados). Se deja registrado, no se reordena el
documento original ni se renombra "Etapa" a "Fase": el siguiente paso
real que pide esta matriz — un modelo exhaustivo de actores/roles y
luego de datos — se ubica en el roadmap maestro como continuación de
Fase 9 en adelante, no como una fase nueva insertada.

## Consistencia contra lo ya existente

Sin contradicciones detectadas. Profundiza `CONTEXTO-MAESTRO.md`
sección 32 (Matching vs. Recomendación, ya esbozada ahí) con una
definición operativa: MATCHING = compatibilidad; RECOMENDACIÓN =
compatibilidad + contexto + prioridad + momento (sección 1).

Confirma explícitamente decisiones que el resto del proyecto ya
aplicaba de forma implícita:

- **Sección 26 (Regla de no sobrecarga)** ↔ ya presente en
  `CONTEXTO-MAESTRO.md` sección 41 y en el propio boceto (grupos
  dinámicos por persona, nunca un menú fijo). No requiere cambios.
- **Sección 62 (Regla de transparencia — "¿por qué me muestras
  esto?")** ↔ es la misma "explicabilidad" ya incorporada al boceto
  con `MATRIZ-MATCHING.md` sección 67. Esta matriz la extiende de
  match individual a la recomendación completa (sección 25): no
  cambia el copy ya escrito, pero confirma que el patrón era correcto.
- **Sección 44 (Recomendaciones según madurez del perfil)** ↔ conecta
  directamente con `CONTEXTO-MAESTRO.md` sección 22 (perfil mínimo +
  aprendizaje) — sin contradicción, la matriz solo la nombra "madurez
  del perfil" en vez de "aprendizaje progresivo".

## Regla nueva con impacto directo en trabajo futuro

- **Sección 54 (Estado de las recomendaciones: NUEVA, VISTA, GUARDADA,
  DESCARTADA, CONTACTADA, APLICADA, COMPLETADA, EXPIRADA)** — no
  existía antes ningún ciclo de vida para una recomendación individual
  (solo existía Estado para oportunidades: Activa/Cerrada, etc. en
  `MATRIZ-OPORTUNIDADES.md`). Queda documentado como pendiente de
  representar cuando exista una capa de interacción real (fuera del
  boceto estático actual).
- **Sección 30 (bloques "Mi desarrollo" / "Mi carrera" / "Mi entorno")**
  es una forma concreta de agrupación que el boceto todavía no usa
  (agrupa hoy por persona completa, no por sub-bloques dentro de una
  misma persona). Candidato para cuando se amplíe la cobertura de
  contextos del boceto.
- **Sección 53 (relaciones entre entidades, ej. JUGADOR → pertenece a
  → CLUB → participa en → COMPETICIÓN)** — la propia matriz aclara que
  esto "será fundamental para la arquitectura de datos posterior"
  (Fase 12), no algo a implementar ahora.

## Qué no se incorpora todavía

Esta entrega es solo el documento y las notas — no se modifica
`prototipo/index.html` en esta ronda. El boceto ya sigue el principio
central (pocas recomendaciones + explicación + "ver más" implícito en
los botones de acción), pero no representa agrupación multi-bloque
(sección 7-8) ni el ciclo de vida de una recomendación (sección 54).
Se incorpora de forma incremental, según la misma regla de no
adelantarse al diseño conceptual (sección 46 del documento base) — la
propia matriz (sección 70) también deja fuera de esta fase cualquier
algoritmo, arquitectura técnica o diseño final de interfaz.
