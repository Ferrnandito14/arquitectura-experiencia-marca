# Notas de integración — Mapa del Ecosistema Futbolístico Venezolano V0.1

Última actualización: 2026-08-22. No modifica `MAPA-ECOSISTEMA-FUTBOL-VE.md`
(se guarda tal como se investigó) — registra cómo se integra con el resto
del proyecto, por la misma regla de trazabilidad de la sección 45 del
documento base.

## Por qué existe este documento

El usuario entregó una instrucción explícita — **"INVESTIGACIÓN DEPORTIVA
OBLIGATORIA"** — exigiendo investigación real (no basada solo en las
referencias ya mencionadas: AFDC, Canguro, Diamante, Pipo, LIDES,
Colegial) antes de tomar más decisiones de arquitectura. Esta
investigación se hizo con búsqueda web real (`WebSearch`/`WebFetch`),
citando fuentes y marcando nivel de confianza en cada hallazgo, siguiendo
exactamente las reglas que el propio documento del usuario pedía
(secciones "VERIFICACIÓN", "REGLA CONTRA DATOS INVENTADOS").

## Relación con `INVESTIGACION-ECOSISTEMA-VE.md`

No se reemplaza — se amplía. El documento anterior cubre en detalle el
fútbol formativo de Distrito Capital (FVF/Liga FUTVE Junior, AFDC, Liga
Pipo Rossi) y patrones de perfiles profesionales en LinkedIn. Este
documento nuevo cubre lo que el anterior no tocaba: pirámide profesional
completa (1ª-3ª división + Copa Venezuela), fútbol femenino, futsal,
fútbol playa, selecciones juveniles, 7 asociaciones estadales adicionales,
fútbol escolar/colegial/universitario, Juegos Deportivos Nacionales, y
más academias privadas.

## Hallazgos con impacto directo en decisiones ya tomadas

- **Confirma** la regla ya establecida (`INVESTIGACION-ECOSISTEMA-VE.md`
  sección 4) de que no existe un catálogo nacional único de categorías —
  ahora con un tercer ejemplo (Liga Colegial: Sub-7/Sub-8/Sub-10...) que
  no coincide ni con Pipo Rossi ni con Canguro Diamante.
- **Nuevo hallazgo estructural**: existe un tercer eje de competición
  —selección estadal en Juegos Deportivos Nacionales— distinto de "club"
  y de "selección nacional". Ninguna matriz anterior (`MATRIZ-CONTEXTO.md`,
  `MATRIZ-OPORTUNIDADES.md`) lo contempla. Se registra como pendiente de
  modelar, no se fuerza su inclusión retroactiva en esas matrices.
- **Nuevo hallazgo**: el ecosistema tiene modalidades activas más allá del
  fútbol 11 masculino (femenino, futsal, playa), cada una con selección,
  liga(s) y participación internacional propias. El campo "deporte" del
  perfil (documento base, sección 20) necesita eventualmente distinguir
  modalidad, no solo "fútbol" como valor único — no se cambia el
  prototipo todavía (ver "Qué no se incorpora").
- **Confirma** el patrón de doble afiliación de escuelas/academias, ahora
  con 5 ejemplos adicionales (AVF, AEF, La Única, ATMVE, Academia Naranja).

## Contradicciones e incertidumbres registradas (no resueltas a la fuerza)

Ver sección 13 del documento — se listan explícitamente en vez de elegir
una versión: cifra de equipos de la Segunda División, relación exacta
Liga FUTVE Futsal 1 / Liga Superior de Futsal, doble definición de
"CONAFUTSAL". Quedan como huecos declarados.

## Limitación técnica de esta ronda

El proxy de red del entorno bloqueó el acceso directo (`WebFetch`) a
`fvf.com.ve`, `es.wikipedia.org` y `ligafutve.org` — toda la información
de esas fuentes viene de fragmentos indexados por búsqueda, no de las
páginas completas. Se anota en la sección 0 del documento; si se necesita
cerrar algún hueco de los listados en la sección 13, hay que reintentar
el acceso directo o buscar espejos/fuentes secundarias de esas páginas.

## Qué no se incorpora todavía

Esta investigación es, por instrucción explícita del propio documento del
usuario, un paso **previo** a modelar/validar/implementar — no cambia
`CONTEXTO-MAESTRO.md`, las matrices anteriores ni `prototipo/index.html`
en esta misma entrega. Su primer uso es como insumo directo de la
`MATRIZ-ACTORES-ROLES.md` que se construye en esta misma ronda (el
usuario pidió ambas cosas seguidas). Los cambios de fondo (nuevo eje de
competición estadal, distinción de modalidad deportiva, ampliación
geográfica más allá de Distrito Capital) quedan como trabajo futuro
explícito — ver sección 14 del documento y las recomendaciones de
`MATRIZ-ACTORES-ROLES-NOTAS.md`.
