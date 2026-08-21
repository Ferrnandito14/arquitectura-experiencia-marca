# Arquitectura de Experiencia de Marca — Pipeline de Diagnóstico (Fase 0)

Este repositorio contiene las 4 skills de Claude que forman el pipeline de
diagnóstico de la Fase 0 (Auditoría) dentro del ecosistema de arquitectura
de experiencia de marca de la startup. Cada carpeta es una skill
independiente y empaquetable (`SKILL.md` + `references/`), pensada para
correr encadenada, en este orden:

```
1. agente-investigador-digital   → Investigador Forense Digital
2. agente-evaluador-iadm         → Evaluador IADM
3. agente-estratega-brechas      → Estratega de Brechas
4. agente-productor-diagnostico  → Productor de Entregables
```

## Qué hace cada etapa

1. **Investigador Forense Digital** (`agente-investigador-digital`) —
   recopila, sin puntuar ni recomendar, la "data cruda" pública y técnica
   de una empresa: rendimiento técnico, cumplimiento legal, sentimiento y
   reputación, y ecosistema de canales activos.
2. **Evaluador IADM** (`agente-evaluador-iadm`) — aplica el Índice de
   Arquitectura Digital de Marca (IADM) sobre la data cruda y asigna
   score 1-5 a Presencia, Arquitectura y Experiencia. Freno de
   alucinación: sin `datos_internos`, Performance queda exactamente "No
   evaluable sin acceso a analítica interna", nunca un número inventado.
3. **Estratega de Brechas** (`agente-estratega-brechas`) — convierte la
   Matriz IADM en mapa de brechas, prioridades por causa raíz (no por
   score más bajo) y recomendaciones estratégicas. Freno de
   solucionismo: recomienda el "qué", nunca el "cómo" (eso se vende en
   la Fase 1, Plano Digital de Marca).
4. **Productor de Entregables** (`agente-productor-diagnostico`) —
   investiga el contexto competitivo (consultoras venezolanas e
   internacionales), ensambla todo en un documento de 7 bloques, y lo
   entrega siempre como archivo de Canva (`verbatim: true`, para que la
   IA de Canva no altere scores ni evidencia ya verificados).

## Convenciones compartidas

- **Sin alucinación**: cada etapa trabaja solo con lo que puede
  verificar o con lo que le entrega la etapa anterior; los huecos de
  información se declaran explícitamente, nunca se rellenan.
- **Separación de responsabilidades**: investigar, puntuar, priorizar y
  ensamblar son trabajos de etapas distintas — ninguna etapa hace el
  trabajo de otra, ni se adelanta a diseñar la solución de la Fase 1.
- **Marco teórico compartido**: todas las etapas citan
  `references/marco-teorico-marketing-digital.md` (síntesis de
  *Inbound Marketing, la guía definitiva* de Cyberclick y *Elementos del
  marketing digital* de AMIPCI) para justificar sus juicios con
  criterio del sector, no a ojo.
- **Rúbrica propia**: `references/indice-arquitectura-digital-marca.md`
  es el instrumento propietario de la startup (el IADM) que puntúa y
  prioriza el diagnóstico.
- **Entrega en Canva**: todo entregable final de esta familia de skills
  se produce también como archivo de Canva (modo `verbatim`), con la
  conversión de tablas markdown a listas ya resuelta en cada skill (ese
  modo de Canva no soporta tablas, links ni bloques de código).

Cada carpeta puede empaquetarse de forma independiente en un `.skill`
instalable en Claude con el skill-creator estándar.
