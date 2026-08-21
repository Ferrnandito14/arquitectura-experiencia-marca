# Investigación: ecosistema real del fútbol venezolano (Distrito Capital)

Última actualización: 2026-08-21. Investigación de campo (búsqueda web) para
anclar el prototipo y el futuro modelo de contexto (Fase 4) en la
estructura **real** del fútbol formativo venezolano, no en categorías
inventadas. Todo lo que sigue tiene fuente citada; lo que no se pudo
verificar se marca explícitamente como tal, siguiendo el principio de no
alucinar información (sección 30 y el freno del Investigador Forense
Digital, ver `ANALISIS-AGENTES.md`).

## 1. Categorías oficiales — FVF / Liga FUTVE Junior

La Federación Venezolana de Fútbol (FVF) organiza el fútbol formativo de
clubes de 1ª y 2ª división a través de la **Liga FUTVE Junior**, con seis
categorías divididas en dos bloques:

- **Bloque bajo**: Sub-15, Sub-16, Sub-17
- **Bloque alto**: Sub-18, Sub-19, Sub-21 (referida también como Sub-20
  en coberturas de prensa — no se pudo verificar cuál es el nombre
  oficial vigente entre Sub-20/Sub-21; queda como hueco de información)

Las selecciones nacionales juveniles ("Vinotinto") compiten en Sub-15,
Sub-17 y Sub-20.

Fuentes: [FVF — Categorías](https://www.fvf.com.ve/categorias) ·
[FVF — Liga FUTVE Junior arranca con seis categorías](https://www.fvf.com.ve/articulos/la-liga-futve-junior-arranca-el-9-de-abril-con-seis-categorias-en-accion) ·
[FVF — Vinotinto Sub-15 bronce Liga Evolución 2025](https://www.fvf.com.ve/articulos/la-vinotinto-sub-15-conquista-el-bronce-en-la-conmebol-liga-evolucion-2025)

## 2. Asociación de Fútbol del Distrito Capital (AFDC)

Órgano rector del fútbol amateur/formativo en Caracas, afiliado a la FVF
y al Instituto Nacional de Deportes (IND). Sitio oficial:
[asofutbolcaracas.com](https://asofutbolcaracas.com/).

**Escala real** (dato con fuente, útil para dimensionar el mercado):
**102 clubes, 429 equipos, ~7.900 jugadores, entre 6 y 20 años.**

**Ligas que organiza** (nombres reales — usarlos como opciones del campo
"competición" del perfil/oportunidad, no inventar nombres de liga):

- Liga Canguro Diamante — categorías Sub-8, Sub-10, Sub-12, Sub-14,
  Sub-16, Sub-18
- Liga Canguro Esmeralda
- Liga Raudix Platino
- Liga Distrital Titanio
- Liga Distrital Azabache
- Liga Distrital Futsal
- Primera Distrital
- Torneo Sub-20

**Clubes afiliados de ejemplo** (Liga Canguro Diamante — lista parcial,
no exhaustiva): AEF, Academia Metropolitana de Fútbol, Altos Mirándinos,
Atlético Venezuela, Caracas FC, Catia FC, C.S.S.A.P., Deportivo Gulima
FC, Deportivo Los Castores, Deportivo Miranda FC, Evolution FC, Football
Players Academy, Franco Proietti Academy, Futuros Vinotinto, Hermandad
Gallega, Paria Sport.

Fuentes: [AFDC — clubes Liga Canguro Diamante](https://asofutbolcaracas.com/clubes-liga-canguro-diamante/) ·
[AFDC — Nosotros](https://asofutbolcaracas.com/nosotros/) ·
[OneFootball — Memoria y Cuenta 2025 AFDC](https://onefootball.com/es/noticias/asociacion-de-futbol-de-distrito-capital-aprueba-por-unanimidad-memoria-y-cuenta-2025-42747474)

## 3. Liga Pipo Rossi

Liga formativa que opera en la zona de Altos Mirandinos / Distrito
Capital. Es, según su propia descripción, la única liga que desarrolla
**fútbol 7** en el país para las categorías más jóvenes:

- **Fútbol 7**: Compotas/Sub-06, Sub-07, Sub-09, Sub-11
- **Fútbol 11**: Sub-13, Sub-15, Sub-17, Sub-19

Academias que han participado en sus torneos (ej. Copa Navidad):
Academia Euroamericana de Fútbol, Guatire Futsal, Futuros Vinotinto,
entre otras. Una escuela de la zona de San Antonio de los Altos
("Deportivo Los Castores") se identifica públicamente como afiliada a
la vez a la Asociación de Distrito Capital y a la Liga Pipo Rossi — dato
útil: una misma escuela/academia puede competir en varias ligas/asociaciones a la vez, algo que el modelo de datos de "organización" debe
poder representar (no una liga única por club).

Fuentes: [Liga Pipo Rossi — Facebook](https://www.facebook.com/p/Liga-de-F%C3%BAtbol-PIPO-ROSSI-100063701314377/) ·
[Balonazos — Copa Navidad Liga Pipo Rossi](https://www.balonazos.com/la-liga-pipo-rossi-vivio-una-fiesta-de-futbol-con-la-i-edicion-de-la-copa-navidad/) ·
[Venezuela Fútbol — Liga Pipo Rossi innova con la Copa Navidad](https://www.venezuelafutbol.com.ve/liga-pipo-rossi-innova-con-la-copa-navidad/)

## 4. Taxonomía consolidada de categorías (para usar en el producto)

Uniendo las tres fuentes, la franja de edad formativa en Distrito Capital
cubre, de menor a mayor, con solapes reales entre ligas (no hay una
única tabla nacional):

```
Compotas/Sub-06 · Sub-07 · Sub-08 · Sub-09 · Sub-10 · Sub-11 · Sub-12
Sub-13 · Sub-14 · Sub-15 · Sub-16 · Sub-17 · Sub-18 · Sub-19 · Sub-20/21
```

Con dos formatos de juego según edad: **fútbol 7** (categorías más
jóvenes, hasta aprox. Sub-11) y **fútbol 11** (desde aprox. Sub-13).
Esto confirma y afina la sección 20 del documento base (campo
"categoría" del perfil): no es un campo libre, tiene un catálogo real
de ~14 valores, y el formato de juego (7 vs. 11) es un dato derivado de
la categoría, no independiente.

## 5. Perfiles profesionales del ecosistema — patrones observados

Se revisaron perfiles públicos de LinkedIn de entrenadores, scouts y
representantes que trabajan en el fútbol formativo venezolano/regional,
**sin incorporar personas identificadas al producto ni al prototipo** —
solo se documentan los patrones que deberían influir en el modelo de
perfil (sección 19-20 del documento base):

- **Entrenadores** no se describen con una sola categoría: listan varias
  a la vez (ej. "Infantil A, B y Pre-A") y suelen combinar afiliaciones —
  colegio + liga colegial + club de 1ª/2ª división + módulos de
  selecciones nacionales — en paralelo o a lo largo del tiempo.
  → El campo "capacidades/historial" del perfil (sección 20) necesita
  soportar **múltiples categorías y múltiples afiliaciones
  institucionales**, no una sola.
- **Scouts/ojeadores** se describen con una **cobertura geográfica**
  explícita (internacional, regional, un estado) como dato central de
  su perfil, no solo como filtro de búsqueda ajeno.
  → "Ubicación" en el perfil de un scout no es solo dónde vive: es
  también su radio/zona de cobertura — son dos datos distintos que hoy
  la sección 20 no separa.
- **Representantes de jugadores** se presentan como agencias con
  cartera de jugadores representados, más parecido a un perfil de
  "organización" que al de una persona individual.
  → Señal para más adelante (no implementar ahora): el rol
  "representante" puede necesitar un perfil híbrido persona/organización. Se deja registrado como hallazgo, no como decisión.
- **Validación de mercado real**: se encontró al menos un profesional
  (scout afiliado a una asociación regional de fútbol) construyendo por
  su cuenta una plataforma propia de scouting/análisis. Es una señal
  externa de que el problema descrito en la sección 3 del documento
  base (información fragmentada, búsqueda manual) es percibido como
  real por gente dentro del ecosistema, no solo una hipótesis interna.

No se citan nombres de estas personas aquí a propósito: el valor de esta
investigación es el patrón, no el individuo, y el producto no debe
lanzarse poblado con perfiles de personas reales que no se han registrado
ni dado consentimiento.

## 6. Cómo se usa esto en el prototipo

- Los **catálogos de categoría y competición** del boceto
  (`prototipo/index.html`) deben usar los nombres reales de este
  documento (Liga Canguro Diamante, Liga Pipo Rossi, Liga FUTVE Junior,
  catálogo de Sub-06 a Sub-21) en vez de placeholders genéricos.
- Los **clubes/academias que aparecen en tarjetas de oportunidad o
  necesidad de ejemplo siguen siendo ficticios** ("Academia Los Álamos",
  "Club Atlético Norte"): atribuirle una vacante, tryout o cupo
  inventado a un club real identificable (Caracas FC, Deportivo Miranda
  FC, etc.) sería presentar información falsa como si fuera real. Los
  nombres reales de clubes solo se muestran en paneles informativos que
  citan hechos verificados (afiliación, escala), nunca en datos de
  oportunidad/necesidad simulados.

## 7. Huecos de información pendientes

- Nombre oficial vigente del último tramo (Sub-20 vs. Sub-21) en la
  Liga FUTVE Junior.
- Tabla oficial completa de categorías de la FVF más allá de la Liga
  FUTVE Junior (no se pudo acceder a `fvf.com.ve/categorias` directamente
  por bloqueo de red del entorno; el dato de arriba viene de artículos
  de prensa de la FVF, no de la página fuente).
- Listado completo (no parcial) de los 102 clubes afiliados a la AFDC.
- Reglamento completo de la Liga Pipo Rossi (no se pudo acceder a
  `ligapiporossi.com` directamente por el mismo bloqueo de red).

Estos huecos quedan declarados, no rellenados. Si se necesita cerrarlos,
hay que reintentar el acceso a las fuentes primarias o pedir el dato
directamente a las asociaciones.
