# Notas de integración — Matriz de Oportunidades V0.1

Última actualización: 2026-08-22. No modifica `MATRIZ-OPORTUNIDADES.md`
(se guarda verbatim) — registra cómo se integra con el resto del
proyecto, por la misma regla de trazabilidad de la sección 45 del
documento base.

## Completa el par que `MATRIZ-NECESIDADES-NOTAS.md` dejó pendiente

Esta es la **Matriz de Oportunidades V0.1** que el cierre de
`MATRIZ-NECESIDADES.md` pedía como siguiente paso — no combinada con
Necesidades, tal como ya se había corregido la expectativa. Con esto,
`CONTEXTO-MAESTRO.md` tiene ahora sus dos mitades (secciones 15 y 16,
Oportunidades y Necesidades) profundizadas en matrices dedicadas.

## Roadmap

`CONTEXTO-MAESTRO.md` sección 34 (Fase 5 — Modelo de Oportunidades)
pasa de `[PENDIENTE DE PROFUNDIZAR]` a `[TRABAJADA — V0.1]`. Con Fases
4, 5 y 6 ya trabajadas, el roadmap llega completo hasta el borde de
Fase 7 (Modelo de Recomendaciones) y Fase 8 (Modelo de Matching) — y la
propia matriz (sección 54) pide exactamente eso a continuación: una
**Matriz de Matching V0.1**.

## Consistencia contra lo ya existente

Sin contradicciones detectadas. Confirma y detalla lo que
`CONTEXTO-MAESTRO.md` sección 15 ya esbozaba (oportunidad como entidad
estructurada, no una publicación) — pasa de 1 ejemplo (tryout) a 22
tipos con datos, estados y audiencia propios. También formaliza una
distinción que el resto del proyecto ya aplicaba de forma implícita
(sección 40): **persona, organización, servicio, evento y vacante son
objetos distintos** — no todo es "un perfil". El boceto y el diseño de
plataforma ya evitaban ese error (p. ej. la necesidad organizacional
del club nunca se mostró como un "perfil de necesidad"), así que no
requirió cambios.

## Reglas nuevas con impacto directo en trabajo futuro

- **Sección 30 (Verificación)**: NO VERIFICADA / VERIFICADA / VERIFICADA
  PARCIALMENTE aplica a clubes, academias, profesionales, eventos y
  oportunidades — esto es exactamente el hueco que
  `ANALISIS-AGENTES.md` dejaba abierto para el candidato "Investigador
  de Organizaciones Deportivas": cuando ese agente se evalúe, debe
  producir uno de estos tres estados, no un dato inventado.
- **Sección 46 (Información contextual)**: la misma oportunidad debe
  mostrar información distinta según quién la ve (padre vs. club vs.
  fisioterapeuta) — esto va más allá de lo que el diseño de plataforma
  implementa hoy (cada pantalla ya es contextual por persona, pero no
  hay todavía un caso de "la misma oportunidad vista por dos roles
  distintos"). Candidato a validar cuando se construya la Matriz de
  Casos de Usuario extendida o el propio MVP.
- **Sección 19 (Staff como categoría, no profesión)**: confirma una
  decisión que ya estaba implícita en `MATRIZ-NECESIDADES.md` y en el
  boceto (los grupos "Buscar staff" agrupan varios roles) — no requiere
  cambios, solo queda documentada explícitamente.

## Qué no se incorpora todavía

Los 22 tipos de oportunidad no se representan uno por uno en el boceto
ni en el diseño de plataforma — igual que con la Matriz de
Necesidades, se amplía la cobertura de forma incremental una vez
exista la Matriz de Matching V0.1 (sección 54), siguiendo la regla de
no adelantarse al diseño conceptual (sección 46 del documento base).
