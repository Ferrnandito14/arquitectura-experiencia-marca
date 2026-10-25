# Startup Deportiva

Esta carpeta contiene la línea de proyecto **Startup Deportiva**: una
plataforma de descubrimiento, matching y recomendación para el
ecosistema deportivo (deportistas, familias, clubes, academias, scouts,
entrenadores, staff, organizaciones, competiciones, oportunidades).

Es una startup **separada** de la línea de Huella Digital / Arquitectura
Digital de Marca que vive en el resto de este repositorio (los agentes
`agente-*` y `auditoria-marca`). Comparten repositorio por decisión
explícita del propietario del proyecto, no por relación de producto —
no asumir que un agente de una línea aplica a la otra sin evaluarlo
primero contra la necesidad real de Startup Deportiva.

## Contenido

- **`CONTEXTO-MAESTRO.md`** — documento base y fuente de verdad del
  estado actual del proyecto: problema, visión, ecosistema, actores,
  modelo de perfil, modelo de oportunidades/necesidades, matching,
  roadmap maestro (Fases 0-22) y las instrucciones de continuidad para
  trabajar el proyecto entre distintas conversaciones/sesiones.
- **`MATRIZ-CONTEXTO.md`** — Matriz de Contexto V0.1: cómo la
  plataforma transforma el perfil en un contexto operativo (13
  contextos desarrollados).
- **`MATRIZ-CONTEXTO-NOTAS.md`** — notas de integración de la matriz
  con el resto del proyecto y con el boceto.
- **`ANALISIS-AGENTES.md`** — evalúa qué skills de la línea Huella
  Digital son reutilizables para Startup Deportiva (ninguna tal cual).
- **`INVESTIGACION-ECOSISTEMA-VE.md`** — investigación con fuentes del
  ecosistema real del fútbol venezolano (Distrito Capital).
- **`prototipo/index.html`** — boceto interactivo del producto.

## Cómo continuar el trabajo en una nueva sesión

1. Leer `CONTEXTO-MAESTRO.md` completo antes de proponer nada nuevo.
2. No inventar decisiones que no estén documentadas ahí.
3. Cualquier decisión nueva validada se incorpora actualizando este
   documento (o los que se desprendan de él), nunca reemplazando
   secciones anteriores sin dejar registro del motivo.
4. Los agentes/skills para esta línea de producto se evalúan y
   construyen aquí mismo, dentro de `startup-deportiva/`, a medida que
   se definan (ver secciones 37-38 y 46-47 del documento base). No se
   trasladan automáticamente agentes de `agente-*` (línea Huella
   Digital) sin pasar primero por: capacidad necesaria → caso de uso →
   entrada → procesamiento → salida → valor → implementación.

## Próxima etapa

**Matriz de Casos de Uso**: validar los 13 contextos de
`MATRIZ-CONTEXTO.md` contra casos reales (su propia sección 24 lo pide
antes de tratarla como regla definitiva de software), e ir ampliando el
boceto con los 9 contextos que todavía no representa — ver
`MATRIZ-CONTEXTO-NOTAS.md`.
