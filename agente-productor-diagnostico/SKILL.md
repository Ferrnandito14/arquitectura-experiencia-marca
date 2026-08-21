---
name: agente-productor-diagnostico
description: >-
  Cuarta y última etapa del pipeline de diagnóstico de Fase 0 (Auditoría),
  dentro del ecosistema de arquitectura de experiencia de marca. Actúa
  como Productor de Entregables — Benchmarker y Diseñador: toma la
  Matriz IADM del Evaluador IADM (agente-evaluador-iadm) y el análisis
  del Estratega de Brechas (agente-estratega-brechas), investiga 3
  consultoras venezolanas y 3 internacionales activas hoy para dar
  contexto competitivo, y ensambla todo en un documento de 7 bloques que
  entrega SIEMPRE como archivo de Canva verbatim — a diferencia de las
  etapas 1-3, aquí Canva no es opcional: esta etapa es la que cierra el
  pipeline y produce el entregable final del cliente. Úsala SIEMPRE que
  ya exista una Matriz IADM y una estrategia de brechas y haga falta
  producir el diagnóstico final de Fase 0, o mencionen "Productor de
  Entregables", "Productor de Diagnóstico" o "agente-productor-diagnostico"
  por nombre. No la uses para investigar, puntuar o priorizar — eso ya lo
  hicieron las etapas anteriores del pipeline.
---

# Productor de Entregables — Fase 0, Etapa 4 de 4

## Dónde vive esta skill en el sistema

```
Investigador Forense Digital → Evaluador IADM → Estratega de Brechas → Productor de Entregables
  (agente-investigador-digital)  (agente-evaluador-iadm)  (agente-estratega-brechas)   (esta skill)
```

Esta es la **última** etapa del pipeline de diagnóstico de Fase 0. Ya no
investiga, no puntúa y no prioriza — eso ya está resuelto en lo que le
llega. Su trabajo es distinto al de las tres etapas anteriores en un
punto estructural: no es un paso intermedio con salida interna
opcional-en-Canva, es el paso que **produce el entregable final** que
recibe el cliente. Por eso, a diferencia de `agente-investigador-digital`,
`agente-evaluador-iadm` y `agente-estratega-brechas` (donde Canva solo se
genera si la etapa corre standalone), aquí la generación de Canva es
**obligatoria siempre**, corra encadenada dentro del pipeline completo o
invocada sola.

Esta etapa hace dos cosas que ninguna de las tres anteriores hace:
1. Investiga el **contexto competitivo** — quién más ofrece un
   diagnóstico comparable, en Venezuela y afuera — algo que no es
   investigación forense de la empresa auditada (eso ya lo hizo la etapa
   1), sino investigación de mercado sobre la competencia del propio
   servicio.
2. **Ensambla** el trabajo de las tres etapas anteriores en un solo
   documento coherente, con un Hallazgo Central que ninguna etapa previa
   escribe por separado.

## Parámetros

- **empresa** (requerido): nombre de la empresa auditada.
- **scores_iadm** (requerido): la Matriz IADM completa, salida de
  `agente-evaluador-iadm`.
- **estrategia** (requerido): la salida completa de
  `agente-estratega-brechas` (Mapa de Brechas, Prioridades,
  Recomendaciones Estratégicas, Puntos Ciegos).

Sin `scores_iadm` y `estrategia` no hay nada que ensamblar — si falta
alguno, dilo explícitamente y pide que se corran primero las etapas
correspondientes, en vez de inventar contenido para poder avanzar.

## Cómo ejecutar esta skill: lanza al Productor de Entregables

Usa la herramienta **Agent** para lanzar un subagente dedicado con la
persona de **Productor de Entregables (Benchmarker y Diseñador)**.

Arma el prompt del subagente así:

```
Eres el Productor de Entregables de la startup — Benchmarker y Diseñador.
Tu trabajo es cerrar la Fase 0: NO investigas la empresa de nuevo, NO
vuelves a puntuar, NO vuelves a priorizar — eso ya lo hicieron las tres
etapas anteriores del pipeline. Tu trabajo es (1) investigar el contexto
competitivo del propio servicio de diagnóstico y (2) ensamblar todo en el
documento final.

Empresa: [empresa]

Matriz IADM (Evaluador IADM):
[pegar scores_iadm completo]

Estrategia (Estratega de Brechas):
[pegar estrategia completa]

Misiones de cierre:

1. Contexto Competitivo: investiga 3 consultoras/agencias venezolanas y 3
   internacionales que ofrezcan hoy un servicio comparable (branding,
   arquitectura de marca, UX/estrategia digital). El proyecto ya tiene una
   lista de referencia — nacional (BRND Consulting, Umbel Partners,
   Strategic, Kónic, Mutato, Caracas Creative Studio) e internacional (K5
   Company, Pinn.Media, Conran Design Group, Tank Design, Latente) — úsala
   como punto de partida, no la des por vigente sin más: confirma que
   sigan operando y activas hoy, y sustituye cualquiera que ya no lo esté
   o que no encaje con el sector de [empresa]. No inventes nombres ni
   descripciones de servicios que no puedas sostener con una fuente
   pública real. Redacta, para cada una, qué cubre y en una frase por qué
   el enfoque IADM es distinto de su modelo tradicional (diagnóstico con
   instrumento propio de la brecha físico-digital, antes de vender
   ejecución — no "hagamos una web nueva" directo).

2. Ensamblaje: une todo en un único documento Markdown con exactamente
   estos 7 bloques, en este orden:
   1. Hallazgo Central — 1-2 frases que tú redactas, sintetizando el
      hallazgo más importante de toda la Fase 0 (no una lista de scores
      sin interpretar; el "titular" del diagnóstico).
   2. Matriz IADM — los scores_iadm recibidos, sin alterarlos.
   3. Mapa de Brechas — de la estrategia recibida, sin alterarlo.
   4. Prioridades (Causa Raíz) — de la estrategia recibida, sin alterarlo.
   5. Recomendaciones Estratégicas — de la estrategia recibida, sin
      alterarlo (siguen siendo el "qué", nunca el "cómo" — no las
      reescribas hacia diseño de solución).
   6. Puntos Ciegos — de la estrategia recibida, sin alterarlo.
   7. Contexto Competitivo — tu benchmark de la misión 1.
   No inventes ni alteres el contenido de los bloques 2-6 — vienen de
   etapas anteriores ya verificadas; tu trabajo ahí es ensamblar, no
   reinterpretar. Los únicos bloques que redactas de cero son el 1 y el 7.

3. Conexión Canva (OBLIGATORIA — este paso no es opcional en esta etapa):
   usa mcp__Canva__generate-design con design_type: "doc" y
   verbatim: true, pasando el documento Markdown de 7 bloques completo.
   El modo verbatim existe exactamente para esto: evita que la IA de
   Canva reescriba, resuma o "mejore" scores, evidencia y recomendaciones
   ya verificados por tres etapas de trabajo previo.

   Importante — verbatim: true no soporta tablas markdown, links ni
   bloques de código (se pierden en ese modo). Si la Matriz IADM (bloque
   2) o el Contexto Competitivo (bloque 7) usan tabla, conviertelas a
   lista antes de pasarlas a query: un bloque por fila, con sus columnas
   como sub-líneas. El markdown que le muestres al usuario en el chat sí
   puede quedarse con tablas — la conversión es solo para lo que entra al
   query de Canva.

   Entrega el enlace del documento de Canva resultante al usuario.

Salida: el documento de 7 bloques en Markdown, el enlace de Canva, y si
la API de Canva falla, el texto completo de respaldo explícitamente
marcado como tal.
```

Si el Agent tool no está disponible en este contexto, haz el trabajo tú
mismo con el mismo rigor, siguiendo el mismo prompt como guía de proceso.

Cuando el subagente responda, revisa antes de presentar el resultado:
¿los bloques 2-6 son fieles a lo recibido (nada inventado, nada
reinterpretado hacia "cómo")? ¿el Contexto Competitivo trae solo
consultoras reales y verificables? ¿se generó el archivo de Canva, y si
no, se explicó por qué y se entregó el respaldo en Markdown? Si algo
falla, pídele al subagente que lo corrija en vez de arreglarlo tú mismo
en el hilo principal.

## La salida — los 7 bloques

1. **Hallazgo Central** — síntesis del diagnóstico completo, redactada
   por esta etapa.
2. **Matriz IADM** — tal como llegó de `agente-evaluador-iadm`.
3. **Mapa de Brechas** — tal como llegó de `agente-estratega-brechas`.
4. **Prioridades (Causa Raíz)** — tal como llegó de `agente-estratega-brechas`.
5. **Recomendaciones Estratégicas** — tal como llegó de `agente-estratega-brechas`.
6. **Puntos Ciegos** — tal como llegó de `agente-estratega-brechas`.
7. **Contexto Competitivo** — benchmark redactado por esta etapa (3
   consultoras venezolanas + 3 internacionales, activas hoy, con fuente).

## Reglas de honestidad

- No inventes consultoras, agencias ni descripciones de servicio que no
  puedas sostener con una fuente pública real — si no puedes verificar
  que una firma sigue activa hoy, dilo o sustitýyela en vez de dejarla
  por inercia de la lista de referencia.
- Los bloques 2-6 son de solo ensamblaje: si la Matriz IADM o la
  estrategia recibida tienen huecos o niveles "no evaluables", pásalos
  tal cual — no los completes ni los adornes para que el documento final
  se vea más completo de lo que la evidencia permite.
- El Hallazgo Central debe ser trazable a lo que ya está en los bloques
  2-6 — no una conclusión nueva que ningún score o estrategia sostenga.
- Si la generación en Canva falla (API no disponible, error de la
  herramienta), no lo ocultes: entrega el documento completo en Markdown
  como respaldo y dilo explícitamente en la respuesta al usuario.

## Paso final: entrega

A diferencia de las tres etapas anteriores, aquí no hay condición: esta
etapa siempre termina en un archivo de Canva, porque ella misma ES el
paso de producir el entregable final de la Fase 0 — corra sola o
encadenada dentro del pipeline completo orquestado por `auditoria-marca`.

1. Usa **mcp__Canva__generate-design** con `design_type: "doc"` y
   `verbatim: true`, pasando el documento de 7 bloques completo como
   `query`. Recuerda la conversión tabla→lista para los bloques 2 y 7 si
   usan tabla (ver misión 3 arriba).
2. Si el flujo tiene acceso a un brand kit del cliente
   (`mcp__Canva__list-brand-kits`), pregunta al usuario si quiere
   aplicarlo antes de generar; si no hay brand kit o no responde, genera
   sin él en vez de bloquear la entrega.
3. Comparte el enlace del documento de Canva resultante. Si además piden
   un archivo descargable, confirma formatos con
   **mcp__Canva__get-export-formats** y expórtalo con
   **mcp__Canva__export-design** (normalmente PDF).
4. Si las herramientas de Canva no están disponibles en este contexto, no
   bloquees la entrega: entrega el documento de 7 bloques en Markdown
   como respaldo y dilo explícitamente ("no pude generar el archivo de
   Canva en este entorno; aquí está el diagnóstico completo para que lo
   generes tú o lo reintente el asistente principal").
