# Diseño de plataforma — informativo, registro y resultado por contexto

Boceto visual de alta fidelidad de la plataforma (7 pantallas), construido
con el editor de Claude Design y publicado como canvas interactivo:

**https://claude.ai/code/artifact/c8e810a1-2e6f-4514-8ae6-f38ad6fffb6d**

Estos `.dc.html` son el código fuente de ese canvas — se guardan aquí para
que el diseño quede versionado junto con el resto del proyecto (sección 46
del documento base), no solo en el enlace publicado.

## Pantallas

- `Main.dc.html` — página informativa (landing): propuesta de valor, cómo
  funciona, ejemplos por contexto, y el panel de "ecosistema real"
  (cifras de la AFDC/FVF, con fuente).
- `Login.dc.html` — registro / perfil mínimo: selección de rol, deporte,
  categoría (catálogo real Sub-06 a Sub-21), país (pensado para escalar
  a otras federaciones más adelante).
- `ResultadoIniciacion.dc.html` — Caso 01 + 16 de
  `../ESPECIFICACION-FUNCIONAL-V0.1.md`.
- `ResultadoDesarrollo.dc.html` — Caso 03/04/05/06.
- `ResultadoRecuperacion.dc.html` — Caso 09, con la restricción explícita
  de no diagnosticar.
- `ResultadoOportunidadProfesional.dc.html` — Caso 10 (un perfil, dos
  roles y dos contextos activos a la vez).
- `ResultadoNecesidadOrganizacional.dc.html` — Caso 13/14/15 (necesidades
  independientes con su propio progreso).

El mapeo completo contra la Matriz de Casos de Usuario, y qué contextos
todavía no tienen pantalla propia, está en
`../MATRIZ-CONTEXTO-NOTAS.md`.

## Datos reales vs. ilustrativos

Categorías y ligas (Sub-06 a Sub-21, Liga FUTVE Junior, Liga Canguro
Diamante, Liga Pipo Rossi, Liga Distrital Titanio) son reales, según
`../INVESTIGACION-ECOSISTEMA-VE.md`. Nombres de clubes, academias y
personas en las tarjetas de ejemplo son ficticios a propósito — nunca se
le atribuye un dato inventado (vacante, tryout, cupo) a una organización
real identificable.

## Limitaciones de esta vista previa

Este canvas corre sobre una vista previa temprana del editor de Claude
Design empaquetada dentro de un Artifact. No tiene paridad con
claude.ai/design y el editor incrustado no se actualiza después de
publicarse. Sirve para explorar y refinar visualmente el diseño — no es
código de producción ni define la arquitectura técnica (eso sigue
pendiente de las fases 10-14 del roadmap).
