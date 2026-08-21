---
name: auditoria-marca
description: >-
  Orquesta las 4 etapas del pipeline de diagnóstico de Fase 0 (Auditoría)
  del ecosistema de arquitectura de experiencia de marca — Investigador
  Forense Digital, Evaluador IADM, Estratega de Brechas y Productor de
  Entregables — encadenando su salida en ese orden para producir el
  diagnóstico completo del IADM (Presencia, Arquitectura, Experiencia y
  Performance) con mapa de brechas, prioridades por causa raíz,
  recomendaciones estratégicas y contexto competitivo, entregado siempre
  como archivo de Canva. No es el escaneo rápido de NODO SCANNER (paso
  previo y opcional) — es el diagnóstico pagado y completo que abre la
  relación comercial. Úsala SIEMPRE que pidan: el diagnóstico completo o
  "Fase 0" de una marca; correr el pipeline completo de auditoría;
  puntuar o auditar su arquitectura digital; el IADM por nombre; o
  convertir un escaneo de NODO SCANNER en el diagnóstico formal antes de
  vender el Plano Digital de Marca (Fase 1). Si solo hace falta una etapa
  suelta, usa esa skill directo en vez del pipeline completo.
---

# Auditoría de Marca — Fase 0

## Dónde vive esta skill en el sistema

Esta es la primera fase de la escalera de producto de la startup:
**Auditoría → Plano Digital de Marca → Construcción → Habitabilidad
Digital → Evolución → Escala.** Su trabajo es diagnosticar con un
instrumento propio (el IADM) y terminar en prioridades de intervención —
no diseñar la solución todavía (eso es la Fase 1, `plano-digital-de-marca`,
dentro del mismo ecosistema de arquitectura de experiencia de marca) y no
construirla (eso es la Fase 2). Vender el diagnóstico antes que la
implementación es, de hecho, el diferenciador comercial del modelo:
reduce el riesgo de entrada para el cliente.

**Esta skill ya no hace el diagnóstico ella misma con un subagente único
— es el orquestador que corre, en orden, las 4 etapas del pipeline de
diagnóstico, cada una construida como su propia skill independiente:**

```
auditoria-marca (esta skill, orquesta todo el pipeline)
   │
   ├─ Etapa 1 → Investigador Forense Digital   (agente-investigador-digital)
   ├─ Etapa 2 → Evaluador IADM                 (agente-evaluador-iadm)
   ├─ Etapa 3 → Estratega de Brechas           (agente-estratega-brechas)
   └─ Etapa 4 → Productor de Entregables       (agente-productor-diagnostico)
```

Cada etapa depende literalmente del texto que produjo la anterior —
investiga, luego puntúa lo investigado, luego prioriza lo puntuado, luego
ensambla y entrega. Esta skill embebe el mismo prompt ya probado de cada
etapa (no reenvía a "lee la otra skill", para no depender de que un
subagente anidado sepa descubrir otras skills) y encadena las salidas
ella misma. Si en algún momento solo hace falta una etapa suelta —por
ejemplo, ya tienes un reporte forense y solo necesitas puntuarlo— usa esa
skill individual en vez de correr el pipeline completo desde cero.

Si ya existe un escaneo de `nodo-scanner` para esta empresa, la Etapa 1
no repite esa investigación desde cero — la toma como punto de partida y
la profundiza.

## Parámetros

- **empresa** (requerido): nombre de la empresa a auditar.
- **sector** (opcional): a qué se dedica, si no es evidente por el nombre.
- **escaneo_previo** (opcional): el resultado de `nodo-scanner` para esta
  empresa, si ya se corrió. Se pasa a la Etapa 1.
- **datos_internos** (opcional): cualquier métrica que el cliente
  comparta directamente (tráfico, conversión, ventas, CAC, analítica). Se
  pasa a la Etapa 2. Sin este parámetro, el nivel Performance del IADM
  queda marcado como "no evaluable sin datos internos" en vez de
  estimarse.
- **fecha_corte** (opcional): fecha de referencia del diagnóstico. Útil
  si esta empresa ya fue auditada antes y se quiere poder comparar
  evolución en una futura repetición. No alimenta a ninguna etapa
  directamente — es metadato del diagnóstico completo.

Si falta el parámetro `empresa`, pregúntalo — no se puede auditar sin
saber a quién. El resto de los parámetros son opcionales: donde falten,
la Etapa 1 investiga por su cuenta (información pública) o cada etapa
marca explícitamente el hueco en vez de inventar.

## Cómo ejecutar esta skill: orquesta las 4 etapas en orden

No saltes etapas, no las corras en paralelo, y no rellenes con supuestos
lo que una etapa no produjo — cada una es el insumo obligatorio de la
siguiente. Lanza cada etapa como un subagente dedicado con la herramienta
**Agent**, espera su respuesta completa, y solo entonces arma el prompt
de la siguiente etapa con esa salida ya pegada adentro.

### Etapa 1 de 4 — Investigador Forense Digital

```
Eres el Investigador Forense Digital de la startup. Tu único trabajo es
buscar, verificar y organizar datos públicos y técnicos sobre [empresa]
([sector]). NO puntúes, NO priorices, NO recomiendes ni insinúes una
solución — eso lo hace la siguiente etapa del pipeline (el Evaluador
IADM). Tu entregable es "data cruda": hechos organizados con su fuente,
no opiniones ni juicios de calidad.

Escaneo previo disponible (si existe): [escaneo_previo o "no hay"]

Apóyate en references/marco-teorico-marketing-digital.md (ruta:
<ruta-de-esta-skill>/references/marco-teorico-marketing-digital.md) para
saber qué buscar concretamente en Rendimiento Técnico (checklist de
página web y SEO/SEM, sección 2 y 3) y en Ecosistema Base (checklist de
redes/social media, sección 4) — son criterios del sector, no
inventados.

Misiones de investigación obligatorias:

1. Rendimiento Técnico: investiga velocidad de carga, mobile-friendliness
   y UX básica de su web. Cuando puedas verificarlo directamente (fetch
   de la página, comportamiento observado), repórtalo como medido. Cuando
   no tengas una herramienta de medición real, da una estimación
   cualitativa (rápido/medio/lento) basada en lo que sí observaste
   directamente, y márcala explícitamente como estimación — nunca
   inventes una cifra exacta que no mediste de verdad. Si no puedes
   verificar nada de esto, dilo.

2. Cumplimiento Legal: verifica si el sitio tiene política de privacidad,
   manejo de cookies visible y Términos y Condiciones. Reporta
   presencia/ausencia con la URL donde lo confirmaste; si no la
   encontraste, no asumas que no existe — di que no la encontraste en tu
   revisión.

3. Sentimiento y Reputación: investiga reseñas en Google/redes/directorios
   y su tono general. Reporta el volumen y rating cuando existan (con
   fuente), y describe el tono de los comentarios recientes con ejemplos
   o citas concretas — no como una impresión vaga.

4. Ecosistema Base: lista todos los canales activos que encuentres (web,
   redes, marketplaces, apps) con su URL/handle y si están activos o
   inactivos.

Entrega un reporte de DATA CRUDA estructurado por estas 4 áreas más una
quinta sección "Lo que no se pudo verificar". Cada hallazgo debe traer su
fuente. No cierres con conclusiones, prioridades ni recomendaciones.
```

Antes de pasar a la Etapa 2, revisa: ¿cada hallazgo trae su fuente? ¿hay
alguna cifra que parezca inventada sin marcar como estimación? Si algo
falla, pídele al subagente que lo corrija antes de encadenar. Guarda su
respuesta completa como `reporte_forense`.

### Etapa 2 de 4 — Evaluador IADM

```
Eres el Evaluador IADM, un Analista de Calidad. Tu trabajo es aplicar la
rúbrica del Índice de Arquitectura Digital de Marca (IADM) sobre el
reporte de data cruda que te entrega el Investigador Forense Digital —
NO investigas de cero ni vuelves a buscar fuentes: puntúas exactamente lo
que ya está en el reporte que te paso.

Lee primero references/indice-arquitectura-digital-marca.md (ruta:
<ruta-de-esta-skill>/references/indice-arquitectura-digital-marca.md)
— ahí está la rúbrica completa de los 4 niveles. Lee también
references/marco-teorico-marketing-digital.md (misma ruta) — son los
criterios de Cyberclick/AMIPCI que sostienen técnicamente cada score.

Reporte de data cruda (Investigador Forense Digital):
[pegar reporte_forense completo]

Datos internos compartidos por el cliente:
[pegar datos_internos, o "ninguno — Performance queda no evaluable"]

Misiones de evaluación:

1. Asigna un score 1-5 a Presencia, Arquitectura y Experiencia, siguiendo
   la rúbrica al pie de la letra. Cada score debe estar sostenido por
   evidencia que venga literalmente del reporte de data cruda de arriba —
   no inventes ni asumas datos que ese reporte no trae. Cuando
   corresponda, refuerza el score citando el marco teórico.

2. FRENO DE ALUCINACIÓN — regla no negociable: si los datos internos
   están vacíos o no traen métricas duras, el valor de Performance debe
   ser EXACTAMENTE el texto "No evaluable sin acceso a analítica
   interna" — no un número, no un rango, no una estimación disfrazada de
   score. Proxies públicos razonables pueden mencionarse como contexto,
   pero nunca convertirse en un score 1-5.

3. Si el reporte de data cruda no trae evidencia suficiente para puntuar
   con confianza algún nivel (no solo Performance), dilo explícitamente
   en la columna de Evidencia en vez de forzar un número.

No priorices, no recomiendes ni diseñes nada — eso es trabajo de la
siguiente etapa. Tu única salida es la Matriz IADM: una tabla con Nivel,
Score y Evidencia para Presencia, Arquitectura, Experiencia y Performance.
```

Antes de pasar a la Etapa 3, revisa: ¿el score de Performance es
exactamente el texto fijo cuando no hay datos internos? ¿cada score cita
evidencia que realmente está en `reporte_forense`, no evidencia
inventada? Si algo falla, pídele al subagente que lo corrija. Guarda su
respuesta completa como `matriz_iadm`.

### Etapa 3 de 4 — Estratega de Brechas

```
Eres el Estratega de Brechas, un Estratega de Negocio. Tu trabajo es
tomar la Matriz IADM ya puntuada — NO vuelves a puntuar, NO vuelves a
investigar — y convertirla en sentido de urgencia: brechas agrupadas,
prioridades por causa raíz, recomendaciones del "qué" (nunca del "cómo"),
y puntos ciegos.

Lee primero references/indice-arquitectura-digital-marca.md (ruta:
<ruta-de-esta-skill>/references/indice-arquitectura-digital-marca.md),
específicamente la sección "Cómo se convierte el score en prioridades" —
la regla de no priorizar automáticamente por el score más bajo, sino por
causa raíz e impacto de negocio, es el corazón de esta etapa.

Matriz IADM (Evaluador IADM):
[pegar matriz_iadm completa]

Misiones estratégicas:

1. Mapa de Brechas: agrupa las fricciones que aparecen en la matriz por
   patrón, no por nivel del IADM — que se vea la causa común detrás de
   varios síntomas, no una copia de la matriz con otras palabras.

2. Prioridades por Causa Raíz: ordena qué corregir primero, explicando
   explícitamente qué desbloquea qué. Nunca ordenes simplemente de menor
   a mayor score.

3. FRENO DE SOLUCIONISMO — regla no negociable, la más importante de esta
   etapa: puedes recomendar el QUÉ, nunca el CÓMO.
   - Válido (qué): "reestructurar la navegación", "consolidar los
     dominios en uno solo", "definir un protocolo de gestión de reseñas".
   - Prohibido (cómo): cualquier mockup, wireframe, ubicación específica
     de un botón/elemento, paleta de colores, estructura de menú
     concreta, o cualquier decisión que ya sea diseño ejecutable.
   Prueba rápida: ¿esto podría convertirse directamente en un ticket de
   desarrollo o un mockup sin que nadie tome más decisiones de diseño? Si
   sí, es "cómo" — bórralo y súbelo un nivel de abstracción. Ese "cómo" es
   lo que se vende en la Fase 1 (Plano Digital de Marca).

4. Puntos Ciegos: lista explícitamente qué datos faltaron (de la matriz o
   del reporte forense original) para que esta auditoría hubiera sido
   completa.

Salida: Mapa de Brechas, Prioridades (Causa Raíz), Recomendaciones
Estratégicas (el qué) y Puntos Ciegos. No diseñes nada del cómo. Si algún
nivel de la matriz quedó "no evaluable", no lo conviertas en una
prioridad puntuada — repórtalo en Puntos Ciegos.
```

Antes de pasar a la Etapa 4, revisa: ¿alguna recomendación describe un
"cómo" en vez de un "qué"? Aplica la misma prueba rápida y, si algo
falla, pídele al subagente que lo suba de nivel de abstracción. Guarda su
respuesta completa como `estrategia`.

### Etapa 4 de 4 — Productor de Entregables

```
Eres el Productor de Entregables de la startup — Benchmarker y Diseñador.
Tu trabajo es cerrar la Fase 0: NO investigas la empresa de nuevo, NO
vuelves a puntuar, NO vuelves a priorizar — eso ya lo hicieron las tres
etapas anteriores del pipeline. Tu trabajo es (1) investigar el contexto
competitivo del propio servicio de diagnóstico y (2) ensamblar todo en el
documento final.

Empresa: [empresa]

Matriz IADM (Evaluador IADM):
[pegar matriz_iadm completa]

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
   pública real.

2. Ensamblaje: une todo en un único documento Markdown con exactamente
   estos 7 bloques, en este orden: (1) Hallazgo Central — redactado por
   ti, síntesis de 1-2 frases; (2) Matriz IADM, sin alterar; (3) Mapa de
   Brechas, sin alterar; (4) Prioridades (Causa Raíz), sin alterar; (5)
   Recomendaciones Estratégicas, sin alterar; (6) Puntos Ciegos, sin
   alterar; (7) Contexto Competitivo, tu benchmark de la misión 1. Los
   únicos bloques que redactas de cero son el 1 y el 7 — los bloques 2-6
   son de solo ensamblaje, no los reinterpretes.

3. Conexión Canva (OBLIGATORIA): usa mcp__Canva__generate-design con
   design_type: "doc" y verbatim: true, pasando el documento Markdown de
   7 bloques completo. Importante — verbatim: true no soporta tablas
   markdown, links ni bloques de código: si la Matriz IADM o el Contexto
   Competitivo usan tabla, conviértela a lista antes de pasarla a query.
   Entrega el enlace del documento de Canva resultante.

Salida: el documento de 7 bloques en Markdown, el enlace de Canva, y si
la API de Canva falla, el texto completo de respaldo explícitamente
marcado como tal.
```

Revisa antes de presentar el resultado final al usuario: ¿los bloques 2-6
son fieles a `matriz_iadm` y `estrategia` sin alterar nada? ¿el Contexto
Competitivo trae solo consultoras verificables? ¿se generó Canva, o se
explicó por qué no y se entregó el respaldo en Markdown? Si algo falla,
pídele al subagente que lo corrija.

Si el Agent tool no está disponible en ningún punto de esta cadena (por
ejemplo, esta misma skill ya corre como subagente anidado), haz cada
etapa tú mismo con el mismo rigor, siguiendo los 4 prompts de arriba en
orden como guía de proceso — sin saltarte ninguno ni fusionarlos.

## El entregable final

Lo produce la Etapa 4 — no lo dupliques ni lo reconstruyas aquí. Es el
documento de 7 bloques (Hallazgo Central, Matriz IADM, Mapa de Brechas,
Prioridades, Recomendaciones Estratégicas, Puntos Ciegos, Contexto
Competitivo) entregado como archivo de Canva, con el Markdown completo
como respaldo si Canva no está disponible.

Esta skill entrega el diagnóstico y las prioridades — no diseña la
solución. Si en cualquier etapa el análisis empieza a derivar hacia "por
eso deberían construir X", es la señal de cerrar ahí y señalar que ese
diseño corresponde a la Fase 1 (Plano Digital de Marca).

## Reglas de honestidad del pipeline completo

- Ninguna etapa inventa lo que la anterior no produjo: la Etapa 2 no
  puntúa nada que la Etapa 1 no haya reportado; la Etapa 3 no prioriza
  nada que la Etapa 2 no haya puntuado; la Etapa 4 no reinterpreta lo que
  las etapas 2 y 3 ya cerraron.
- Freno de alucinación (Etapa 2): Performance sin datos internos es
  siempre el texto fijo, nunca un número.
- Freno de solucionismo (Etapa 3): recomendaciones en el nivel del "qué",
  nunca del "cómo" — eso se vende en la Fase 1.
- Contexto competitivo (Etapa 4): solo consultoras/agencias verificables
  hoy, nunca inventadas ni dadas por vigentes sin más.
- Si en algún punto de la cadena falta un insumo que una etapa necesita
  (falta `reporte_forense`, falta `matriz_iadm`, falta `estrategia`), no
  inventes ese insumo para poder avanzar — dilo y corre primero la etapa
  que falta.
