# Notas de integración — Matriz de Contexto V0.1

Última actualización: 2026-08-21. No modifica `MATRIZ-CONTEXTO.md` (se
guarda verbatim, tal como se recibió) — este documento solo registra
cómo se está integrando con el resto del proyecto, siguiendo la regla
de trazabilidad de la sección 45 del documento base.

## Inconsistencia detectada (sin corregir el original)

La sección 5 de la matriz lista 15 categorías con letras A-O:

```
A. INICIACIÓN         F. CAMBIO DE CLUB         K. BÚSQUEDA DE PROFESIONALES
B. FORMACIÓN           G. PROFESIONALIZACIÓN     L. OPORTUNIDAD PROFESIONAL
C. DESARROLLO          H. RECUPERACIÓN           M. NECESIDAD ORGANIZACIONAL
D. COMPETICIÓN         I. PREPARACIÓN FÍSICA      N. DESCUBRIMIENTO
E. SCOUTING            J. ENTRENAMIENTO INDIVIDUAL O. TRANSICIÓN
```

Pero las secciones 6-18, que desarrollan cada contexto, usan una letra
distinta a la de la lista (ej. "CONTEXTO E — CAMBIO DE CLUB" en la
sección 10, cuando la sección 5 le asigna la letra F). Son 13 contextos
desarrollados en detalle (secciones 6-18) para las 15 categorías
listadas — "Búsqueda de profesionales" no tiene sección propia
(parece cubierta de forma transversal por Preparación Física,
Recuperación y Entrenamiento Individual) y la lista no vuelve a usar
letras después de la sección 18. Se deja registrado como hueco de
información — no se reordena el documento original.

Para evitar arrastrar la ambigüedad, este proyecto identifica cada
contexto desarrollado por su **nombre**, no por su letra.

## Mapeo: personas ya construidas en el boceto ↔ contextos de la matriz

El boceto (`prototipo/index.html`) ya tenía 4 personas, tomadas de los
ejemplos de `CONTEXTO-MAESTRO.md` (secciones 6-9). La matriz permite
ubicarlas con precisión dentro del catálogo completo:

| Persona en el boceto | Contexto en `CONTEXTO-MAESTRO.md` | Contexto equivalente en la Matriz V0.1 |
|---|---|---|
| Niño principiante | Iniciación deportiva | **Contexto A — Iniciación** (sección 6) |
| Jugador competitivo | Desarrollo competitivo / scouting | **Contexto C — Desarrollo competitivo** (sección 8) y roza **Contexto D — Scouting** (sección 9) |
| Entrenador busca empleo | Oportunidad profesional | **Contexto J — Oportunidad profesional** (sección 15) |
| Club con necesidad | Necesidad de talento | **Contexto K — Necesidad organizacional** (sección 16) |

La matriz **afina** los filtros y grupos de estos 4 contextos frente a
lo que ya estaba en el boceto (ej. Iniciación ahora incluye "edad" y
"modalidad" como filtros, que el boceto todavía no tenía) — el boceto
se actualiza para reflejarlo.

## Contextos nuevos, todavía sin representar en el boceto

La matriz define 9 contextos más que el boceto no cubre todavía:
Formación, Cambio de club, Preparación física, Recuperación/Fisioterapia, Entrenamiento individual, Profesionalización, Descubrimiento,
Transición, y el eje completo de "búsqueda de profesionales" desde el
lado del deportista (preparador físico, fisioterapeuta, especialista).

No se agregan todavía al boceto interactivo por volumen: agregar los 9
de una vez sin verificarlos uno a uno contra casos reales rompeía el
principio de la sección 24 de la matriz ("debe validarse mediante casos
reales" antes de tratarse como regla de software). Se incorporan de
forma incremental, empezando por los que el usuario priorice o por los
que la próxima Matriz de Casos de Usuario (el siguiente paso que la
propia matriz pide en su sección 24) vaya confirmando.

## Estado del roadmap actualizado

`CONTEXTO-MAESTRO.md` sección 34 (Fase 4 — Modelo de Contexto) pasa de
`[PENDIENTE]` a `[TRABAJADA — V0.1]`, con esta matriz como su entregable — ver el historial de cambios agregado ahí mismo.

## Actualización 2026-08-21 (segunda entrega) — Matriz de Casos de Usuario

El usuario entregó `ESPECIFICACION-FUNCIONAL-V0.1.md`: un documento de
dos partes. La Parte I es una reescritura de esta misma
`MATRIZ-CONTEXTO.md` (mismas 15 categorías A-O, misma estructura de
contexto, sin contradicciones — solo redacción y numeración de
secciones distintas). La Parte II es la **Matriz de Casos de Usuario**
que la sección 24 de esta matriz (y la sección 25 de la Parte I nueva)
pedia como siguiente paso: 21 casos concretos, una matriz general de
actores, y seis principios operativos (matching, necesidad,
oportunidad, recomendación, visibilidad, evolución).

Con esto, el siguiente paso que la propia matriz reclamaba queda
cubierto. El siguiente paso que pide `ESPECIFICACION-FUNCIONAL-V0.1.md`
en su cierre es la **Matriz de Necesidades y Oportunidades** (Fase 5/6
del roadmap, profundizando lo que ya existía a nivel de esquema en
`CONTEXTO-MAESTRO.md` secciones 15-16).

Los 21 casos amplian el numero de contextos representables mas alla
de los 4 originales del boceto interactivo. Se incorporan en dos
piezas separadas — ver la sección siguiente.

## Diseño de plataforma (informativo + registro + resultado por contexto)

Además del boceto interactivo (`prototipo/index.html`, 4 personas, con
filtros funcionales), se construyó un **diseño de plataforma completo**
como canvas multi-pantalla, cubriendo lo que `prototipo/index.html`
no cubre: la página informativa y el registro/perfil mínimo, más 5
pantallas de resultado adicionales.

Mapeo contra la Matriz de Casos de Usuario (`ESPECIFICACION-FUNCIONAL-V0.1.md`, Parte II):

| Pantalla del diseño | Caso(s) de uso |
|---|---|
| `Main.dc.html` (informativa) | — (marketing/onboarding, no es un caso de uso) |
| `Login.dc.html` (registro) | Perfil mínimo (sección 22, documento base) |
| `ResultadoIniciacion` | Caso 01 (niño sin experiencia) + Caso 16 (familia gestiona el perfil del menor) |
| `ResultadoDesarrollo` | Caso 03 (desarrollo competitivo) + Caso 04 (cambio de club) + Caso 05/06 (tryout/scout) |
| `ResultadoRecuperacion` | Caso 09 (fisioterapia — con la restricción explícita de no diagnosticar) |
| `ResultadoOportunidadProfesional` | Caso 10 (un perfil, dos roles y dos contextos activos a la vez) |
| `ResultadoNecesidadOrganizacional` | Caso 13/14/15 (club con varias necesidades, cada una independiente con su propio progreso) |

Contextos de la matriz sin pantalla propia todavía: Formación,
Preparación física, Entrenamiento individual, Profesionalización,
Descubrimiento, Transición, y los casos 02, 07, 08, 12, 17, 18, 20, 21.
Quedan pendientes por volumen, no por falta de datos — se agregan
incrementalmente.

Todas las categorías y ligas mostradas en el diseño (Sub-06 a Sub-21,
Liga FUTVE Junior, Liga Canguro Diamante, Liga Pipo Rossi) son reales,
segun `INVESTIGACION-ECOSISTEMA-VE.md`. Los nombres de clubes,
academias y personas en las tarjetas de ejemplo son ficticios a
propósito, por la misma razón registrada en ese documento (sección 6):
no atribuir datos inventados a una organización real identificable.
El campo País del registro queda explícito desde el perfil mínimo para
que el modelo pueda escalar a otras federaciones más adelante — hoy
solo Venezuela tiene datos reales cargados.

Diseño publicado (privado, se comparte desde el propio enlace):
https://claude.ai/code/artifact/c8e810a1-2e6f-4514-8ae6-f38ad6fffb6d
