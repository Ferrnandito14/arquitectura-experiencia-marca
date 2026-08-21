# Análisis: agentes/skills de Huella Digital vs. necesidades de Startup Deportiva

Última actualización: 2026-08-21 (contra el estado del repo a esa fecha:
`agente-investigador-digital`, `agente-evaluador-iadm`,
`agente-estratega-brechas`, `agente-productor-diagnostico`,
`agente-analista-transicion`, `auditoria-marca`).

Este documento se actualiza cada vez que se agrega o modifica una skill
en este repositorio, para decidir si aplica, se adapta o no aplica a
Startup Deportiva. Regla fija (documento base, secciones 37-38):

```
CAPACIDAD  →  NECESIDAD DEL PRODUCTO  →  AGENTE
```

Una skill no se traslada por existir — se traslada solo si hay una
necesidad ya documentada en `CONTEXTO-MAESTRO.md` que la justifique.

## Estado del roadmap en el momento de este análisis

Fase 4 (Modelo de Contexto) está **pendiente**. Fases 5 a 8
(Oportunidades, Necesidades, Recomendaciones, Matching) también. Eso
importa para este análisis: todavía no existe una necesidad de producto
validada que pida un agente ejecutable — por regla del documento base
(sección 41), lo que no es necesario ahora se posterga.

## Veredicto por skill existente

| Skill (Huella Digital) | Qué hace | Capacidad subyacente | ¿Aplica a Startup Deportiva ahora? |
|---|---|---|---|
| `agente-investigador-digital` (Investigador Forense Digital) | Recolecta, sin puntuar, data cruda pública y técnica de una empresa (performance, cumplimiento legal, sentimiento, canales activos) | Recolección verificable de información pública, sin alucinar huecos | **Candidato a adaptar, no aún.** El patrón (recolectar solo lo verificable, declarar huecos explícitamente) es exactamente lo que pide la sección 30 (Confianza y Verificación) para estructurar perfiles de clubes/academias (sección 29). Pero eso es trabajo de Fase 5, todavía sin profundizar. No implementar todavía. |
| `agente-evaluador-iadm` (Evaluador IADM) | Puntúa 1-5 Presencia/Arquitectura/Experiencia con la rúbrica propietaria IADM | Scoring de madurez de marca digital | **No aplica.** El IADM es un instrumento específico de diagnóstico de marca; Startup Deportiva no tiene (ni necesita todavía) un concepto equivalente de "madurez digital" de un club. Si en el futuro se define un score de confianza/verificación de organizaciones (sección 30), sería un instrumento nuevo, no el IADM reutilizado. |
| `agente-estratega-brechas` (Estratega de Brechas) | Convierte score IADM en mapa de brechas y prioridades, recomienda el "qué" nunca el "cómo" | Priorización por causa raíz sobre un diagnóstico ya puntuado | **No aplica ahora.** Depende de un scoring previo (IADM) que no existe en este producto. |
| `agente-productor-diagnostico` (Productor de Entregables) | Ensambla el diagnóstico de 4 etapas en un documento de 7 bloques, lo entrega en Canva | Producción de entregables a partir de etapas previas | **No aplica ahora.** Startup Deportiva no produce "diagnósticos" como entregable — su unidad de valor es perfil/oportunidad/necesidad/match, no un informe. |
| `agente-analista-transicion` (Analista de Transición) | Traduce brechas/prioridades de la Fase 0 en requerimientos técnicos de diseño para la Fase 1 | Traducción de "qué" (negocio) a requerimientos formales de diseño | **No aplica directamente**, pero el patrón es reutilizable como *forma*: cuando Fase 4 (Modelo de Contexto) quede definida, va a hacer falta ese mismo puente — de la matriz conceptual a requerimientos de implementación del prototipo. Se evalúa como agente nuevo en su momento, no como traslado de este. |
| `auditoria-marca` (orquestador Fase 0) | Encadena las 4 etapas de diagnóstico de marca | Orquestación de pipeline secuencial | **No aplica.** Es el orquestador del pipeline de diagnóstico de marca completo; Startup Deportiva no tiene ese pipeline. |

## Conclusión

Ninguna skill existente se traslada tal cual. Todas nacieron para el
diagnóstico de arquitectura digital de marca (Fase 0-1 de esa línea) y
su rúbrica (IADM) no tiene equivalente aquí. Lo único con valor de
patrón reutilizable — no de código, sino de *disciplina* — es:

1. **No alucinar información**: declarar huecos de datos en vez de
   rellenarlos (patrón del Investigador Forense Digital).
2. **Separar responsabilidades por etapa**: cada agente hace una sola
   cosa y no se adelanta a la siguiente (patrón de las 4 etapas y del
   Analista de Transición).
3. **Freno de solucionismo**: recomendar el "qué" antes que el "cómo".

Cuando Fase 4 (Modelo de Contexto) esté resuelta y Fase 5/6 (Oportunidades/Necesidades) profundizadas, los primeros candidatos reales a
convertirse en agente son:

- **Intérprete de Contexto** — perfil → contexto operativo (nace de
  Fase 4).
- **Investigador de Organizaciones Deportivas** — adaptación real del
  patrón del Investigador Forense Digital, para estructurar y verificar
  datos públicos de clubes/academias (nace de Fase 5 + sección 29-30).
- **Motor de Matching** — perfil+oportunidad/necesidad → compatibilidad
  (nace de Fase 8, todavía sin fórmula definida).

Ninguno de los tres se implementa todavía: no hay necesidad de producto
validada que lo pida (regla de la sección 41). Se documentan aquí como
candidatos para no perder la trazabilidad de la decisión.

## Cómo se actualiza este documento

Cada vez que se agregue o edite una skill en este repositorio:

1. Ubicarla en la tabla de arriba (o agregar fila si es nueva).
2. Aplicar la regla capacidad → necesidad → agente contra el estado
   vigente de `CONTEXTO-MAESTRO.md` (no contra lo que "podría servir").
3. Si aplica, anotar a qué sección del documento base responde antes
   de adaptarla — nunca adaptar primero y justificar después.
4. Si no aplica todavía, dejar registrado el motivo (como en esta
   versión), no borrarlo del historial.
