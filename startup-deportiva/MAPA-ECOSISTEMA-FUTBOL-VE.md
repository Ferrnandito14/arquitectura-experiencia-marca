# Mapa del ecosistema futbolístico venezolano — Investigación obligatoria V0.1

Última actualización: 2026-08-22. Investigación de campo (búsqueda web) realizada
en respuesta a la instrucción **"INVESTIGACIÓN DEPORTIVA OBLIGATORIA"** entregada
por el usuario: antes de tomar decisiones definitivas sobre arquitectura de
datos, actores, matching, recomendaciones o flujos, había que investigar el
ecosistema real más allá de las referencias ya mencionadas en el proyecto
(AFDC, Liga Canguro Diamante, Liga Pipo Rossi, Liga FUTVE Junior).

Este documento **no reemplaza** `INVESTIGACION-ECOSISTEMA-VE.md` (que queda
como investigación de detalle sobre fútbol formativo en Distrito Capital) —
lo **amplía** al resto del país y a las modalidades y estructuras que ese
primer documento no cubría, siguiendo la misma regla de trazabilidad de la
sección 45 del documento base.

## 0. Método y reglas seguidas

- Cada hallazgo se marca con un nivel de confianza: **CONFIRMADO** (fuente
  primaria u oficial clara), **PROBABLE** (fuente secundaria consistente,
  sin confirmación primaria), **NO CONFIRMADO** (una sola mención, sin
  contraste) o **INFORMACIÓN INCOMPLETA** (el dato existe pero está
  parcial).
- Cuando dos fuentes se contradicen, se registra la contradicción — no se
  elige una versión al azar.
- Cuando no se encontró información, se declara explícitamente como hueco,
  no se completa con una suposición razonable.
- **Limitación técnica de esta sesión**: el acceso directo (WebFetch) a
  `fvf.com.ve`, `es.wikipedia.org` y `ligafutve.org` estuvo bloqueado por
  el proxy de red del entorno. Toda la información de estas fuentes viene
  de los fragmentos indexados por la búsqueda web, no de las páginas
  completas — puede haber detalle adicional en esas páginas que esta
  investigación no capturó. Se anota en cada sección donde aplica.
- Ninguna oportunidad, vacante, tryout o necesidad del prototipo se basa en
  clubes reales identificados aquí — esta investigación es para el
  **catálogo de categorías/competiciones/organizaciones**, no para poblar
  datos simulados con entidades reales (misma regla que
  `INVESTIGACION-ECOSISTEMA-VE.md` sección 6).

## 1. Fútbol profesional masculino — pirámide de divisiones FVF/Liga FUTVE

| División | Nombre oficial 2026 | Equipos | Formato | Confianza |
|---|---|---|---|---|
| 1ª | Primera División de Venezuela / **Liga FUTVE** (70ª edición) | 14 (13 de la temporada anterior + 1 ascendido) | Apertura y Clausura; fase de 13 jornadas todos-contra-todos, luego 8 mejores a cuadrangulares semifinales | CONFIRMADO |
| 2ª | Segunda División / **Liga FUTVE 2** (47ª edición) | Fuentes inconsistentes: una cifra dice 16 equipos en dos grupos (Occidental/Oriental, 8+8, 14 jornadas ida-vuelta); otra dice "13 de la temporada anterior + 1 descendido" (sumaría 14, no 16) | Grupos regionales | **INFORMACIÓN INCOMPLETA / CONTRADICTORIA** — no se resolvió la cifra exacta de equipos |
| 3ª | Tercera División de Venezuela / **Liga FUTVE 3** — categoría amateur, sustituyó al "Torneo Aspirantes" desde la reestructuración 2007/2008 | No determinado en esta ronda | Tres fases: estadal → regional → nacional; dos torneos anuales (Apertura/Clausura) para ascender a 2ª | PROBABLE |
| Copa | **Copa Venezuela 2026** (reactivada tras un período de ausencia) | 20 equipos (14 de Liga FUTVE 2 + 6 de Liga FUTVE 1 que no llegaron a cuartos) | 5 grupos de 4, jun-oct 2026, hasta bracket de 16 | CONFIRMADO |

Fuentes: [Primera División de Venezuela 2026 — Wikipedia](https://es.wikipedia.org/wiki/Primera_Divisi%C3%B3n_de_Venezuela_2026) ·
[Segunda División de Venezuela 2026 — Wikipedia](https://es.wikipedia.org/wiki/Segunda_Divisi%C3%B3n_de_Venezuela_2026) ·
[FVF — vuelve la Copa Venezuela 2026](https://www.fvf.com.ve/articulos/vuelve-la-copa-venezuela-la-fvf-anuncia-el-inicio-de-la-edicion-2026) ·
[Radio Mundial — FVF reactiva la Copa Venezuela](https://radiomundial.com.ve/federacion-venezolana-de-futbol-reactiva-la-copa-venezuela-con-nuevo-formato-de-competencia/) ·
[Tercera División de Venezuela — Wikipedia](https://es.wikipedia.org/wiki/Tercera_Divisi%C3%B3n_de_Venezuela) ·
[Liga FUTVE 3 — Periodico 365](https://periodico365.com/futbol-de-tercera-division-de-venezuela/)

**Nota para el modelo de datos**: la Tercera División tiene una estructura de
fases **territorial** (estadal → regional → nacional) distinta a la de 1ª/2ª
(liga única o dos grupos). El campo "formato de competición" no puede
asumir un único patrón para todas las divisiones.

## 2. Fútbol femenino

- **Liga FUTVE Femenina** (nombre oficial de la Primera División Femenina):
  liga semiprofesional desde 2017, bajo la Comisión de Fútbol Femenino de
  la FVF. Antecesora: Liga Amateur de Fútbol Femenino (LAFF, desde 2000,
  mayormente equipos universitarios) → Primera División Femenina
  2003/04-2016 → reestructuración a Liga FUTVE Femenina en 2017. Campeón
  vigente: ADIFFEM (2025); Caracas es el club más laureado (6 títulos). La
  campeona clasifica a la Copa Libertadores de Fútbol Femenino. CONFIRMADO.
- **Plan Integral 2026-2030 para el fútbol femenino** (FVF): incluye
  masificación vía "Festivales Vinotinto" en los 24 estados,
  profesionalización completa de la Liga FUTVE Femenina, expansión a un
  mínimo de 8 equipos estables, continuidad de la **Copa Venezuela
  Femenina**, y creación de una **liga estadal femenina**. CONFIRMADO (es
  un plan anunciado, no todavía una estructura operativa completa — se
  marca la diferencia entre lo ya vigente y lo planeado).

Fuentes: [Liga FUTVE Femenina — Wikipedia (EN)](https://en.wikipedia.org/wiki/Liga_FUTVE_Femenina) ·
[Primera División Femenina (Venezuela) — Wikipedia (EN)](https://en.wikipedia.org/wiki/Primera_Divisi%C3%B3n_Femenina_(Venezuela)) ·
[FVF — Plan Integral 2026-2030 fútbol femenino](https://www.fvf.com.ve/articulos/la-fvf-presento-el-plan-integral-2026-2030-para-el-futbol-femenino-en-venezuela)

## 3. Fútbol formativo de clubes — Liga FUTVE Junior y Ligas de Desarrollo FVF

Ya documentado en detalle en `INVESTIGACION-ECOSISTEMA-VE.md` sección 1
(Sub-15 a Sub-21, dos bloques). Hallazgo nuevo de esta ronda: existe además
un programa llamado **"Ligas de Desarrollo FVF"**, presentado como base de
proyección hacia selecciones nacionales — el 91% del plantel Sub-17 que
fue al Mundial FIFA salió de la Liga FUTVE Junior. **No se pudo acceder al
artículo fuente completo** (bloqueo de red a fvf.com.ve); el dato de
detalle (categorías exactas, regiones, formato) queda como **INFORMACIÓN
INCOMPLETA** — solo se confirma que el programa existe y su función de
cantera hacia las selecciones.

Fuente: [FVF — La Liga FUTVE Junior 2025 ya tiene a sus campeones](https://www.fvf.com.ve/articulos/la-liga-futve-junior-2025-ya-tiene-a-sus-campeones) ·
[FVF — Ligas de Desarrollo FVF](https://www.fvf.com.ve/articulos/ligas-de-desarrollo-fvf-construyendo-generaciones-con-proyeccion-internacional) (título indexado, contenido no accesible)

## 4. Selecciones nacionales juveniles (masculinas)

Categorías confirmadas con actividad reciente: **Sub-15, Sub-17, Sub-20,
Sub-23**. La Sub-20 ganó medalla de oro en los Juegos Centroamericanos y
del Caribe 2026 (venciendo a México por penales); compite también en el
CONMEBOL Sub-20. La Sub-23 disputa el torneo preolímpico rumbo a los
Juegos Olímpicos. La Sub-17 disputó el Mundial FIFA Sub-17 Catar 2025.
CONFIRMADO. No se investigó si existe Sub-18 o Sub-21 como categoría de
selección (solo aparecen como categorías de club en la Liga FUTVE Junior).

Fuentes: [FVF — Vinotinto Sub-20 oro en Juegos Centroamericanos 2026](https://www.fvf.com.ve/articulos/la-vinotinto-sub-20-conquista-la-medalla-de-oro-en-los-juegos-centroamericanos-y-del-caribe-2026) ·
[FVF — Vinotinto Sub-23 preolímpico](https://www.fvf.com.ve/articulos/la-vinotinto-sub-23-esta-lista-para-su-estreno-en-el-preolimpico) ·
[Selección Sub-17 de Venezuela — Wikipedia](https://es.wikipedia.org/wiki/Selecci%C3%B3n_de_f%C3%BAtbol_sub-17_de_Venezuela)

## 5. Futsal

- **Liga FUTVE Futsal 1**: máxima categoría de futsal venezolano,
  dependiente de la FVF/Liga FUTVE. Empezó en 2003 con 6 equipos de 6
  ciudades; desde 2012 juega Apertura/Clausura bajo reglas FIFA.
- **Liga Superior de Futsal**: empezó en 2011, se profesionalizó en 2013 —
  **relación exacta con la Liga FUTVE Futsal 1 no aclarada** (¿es la misma
  competición renombrada, o una distinta?). INFORMACIÓN INCOMPLETA.
- **Ligas de desarrollo**: se identificó explícitamente una "Liga de
  Desarrollo Sub-12 Futsal femenina" — confirma que el futsal también
  tiene su propia pirámide formativa por categorías, separada de la del
  fútbol 11.
- **CONAFUTSAL**: aparece descrita de dos formas distintas en fuentes
  distintas — (a) como "Comisión Nacional de Árbitros y Anotadores de
  Futsal" (arbitraje) y (b) como "Comisión Nacional de Fútbol Sala" que
  coordina futsal y fútbol playa a nivel nacional, afiliada a la
  Federación Venezolana de Futsal. **Esta contradicción no se resolvió** —
  puede ser que el acrónimo se use para dos cuerpos distintos, o que una
  de las dos fuentes esté desactualizada. Se registra tal cual, sin
  elegir una versión.
- **FUNLINAFUTSAL** — "Liga Nacional Comunitaria de Futsal Menor": una
  organización adicional de futsal formativo/comunitario, encontrada de
  forma incidental (no investigada a fondo). Queda como hueco.

Fuentes: [Liga FUTVE Futsal 1 — Wikipedia](https://es.wikipedia.org/wiki/Liga_FUTVE_Futsal_1) ·
[Fútbol de salón en Venezuela — Wikipedia](https://es.wikipedia.org/wiki/F%C3%BAtbol_de_sal%C3%B3n_en_Venezuela) ·
[RNV — Liga Superior de Futsal](https://rnv.gob.ve/liga-superior-de-futsala-iniciara-el-14-de-julio-acordonaron-los-equipos/) ·
[FUNLINAFUTSAL](https://funlinafutsal.com/)

## 6. Fútbol playa

**Liga FUTVE Playa**: fase regional + fase nacional final (marzo 2026, en
el Centro Nacional de Alto Rendimiento — CNAR, Nueva Esparta). El campeón
representa a Venezuela en la CONMEBOL Libertadores Beach Soccer. La
selección nacional de fútbol playa compite en torneos internacionales
(Beach Soccer Cup en El Salvador, activa desde 2022; perdió 6-5 ante
Portugal en su debut 2025). CONFIRMADO.

Fuentes: [FVF — Liga FUTVE Playa fase regional](https://www.fvf.com.ve/articulos/la-liga-futve-playa-avanza-en-su-fase-regional-y-fortalece-el-proyecto-de-selecciones-nacionales) ·
[Beach Soccer Venezuela — fixture fase nacional final](https://www.beachsoccervenezuela.com/2026/02/definido-el-fixture-de-la-fase-nacional.html)

## 7. Asociaciones estadales — mapa parcial (no exhaustivo)

Venezuela tiene 24 entidades federales; esta ronda solo pudo investigar
las siguientes con algún nivel de detalle. **El resto queda como hueco
declarado**, no como "no existen".

| Estado | Asociación / liga identificada | Detalle encontrado | Confianza |
|---|---|---|---|
| Distrito Capital | AFDC (ya documentada en detalle en `INVESTIGACION-ECOSISTEMA-VE.md`) | 102 clubes, 429 equipos, ~7.900 jugadores | CONFIRMADO |
| Zulia | Asociación de Fútbol del Zulia (AFEZ) | Divisiones para entrenadores, atletas, fútbol femenino y árbitros; menciona "fútbol federado y regional menor" sin detalle de ligas por nombre | INFORMACIÓN INCOMPLETA |
| Táchira | (no se identificó el nombre de la asociación estadal directamente — solo la cantera de Deportivo Táchira) | Categorías del club: Teteritos, Compoticas, Mundialito, Preinfantil, Infantil C/B/A, Sub-12/14/16 femenino | PROBABLE (es la cantera de un club, no necesariamente el catálogo oficial de la asociación estadal) |
| Carabobo | Asociación de Fútbol de Carabobo (ACEFUC) — también rige fútbol sala y playa en el estado | Categorías mencionadas: Sub-9, Sub-11, Sub-13; Sub-16, Sub-18, Sub-19, Sub-20 en Liga FUTVE Junior; organiza "Copa Apertura" | PROBABLE |
| Miranda | Asociación de Fútbol del Estado Miranda (sitio: futbolmirandino.com, con directorio de clubes) | No se accedió al listado completo de clubes/categorías | INFORMACIÓN INCOMPLETA |
| Lara | Asociación de Fútbol del Estado Lara (AFEL) | Coordina con "Liga Internacional" y "Liga Unión" como los dos torneos menores más importantes del estado | PROBABLE |
| Bolívar | Asociación de Fútbol del Estado Bolívar (Asofutbolívar) | Organiza la "Liga Municipal", 20+ equipos registrados incl. academias | PROBABLE |
| Aragua | Asociación de Fútbol Aragua | Menciona liga juvenil Sub-17, "Liga Nacional Masculina" y torneo "Serie Oro"; participa en Juegos Nacionales | INFORMACIÓN INCOMPLETA |

Estados **no investigados en esta ronda** (huecos explícitos): Anzoátegui,
Mérida, Trujillo, Barinas, Portuguesa, Yaracuy, Falcón, Sucre, Nueva
Esparta, Cojedes, Guárico, Apure, Delta Amacuro, Amazonas, Monagas,
Vargas/La Guaira (fuera de lo ya cubierto por AFDC), Vargas. No asumir que
estos estados carecen de estructura — solo que esta investigación no llegó
a documentarla.

Fuentes: ver enlaces citados en cada fila de la tabla (búsquedas
individuales por estado, agosto 2026).

## 8. Fútbol escolar y estudiantil

- **LIDES (Liga Deportiva Estudiantil)**: descrita como "el campeonato de
  fútbol escolar más prestigioso de Venezuela" históricamente. Organizada
  por la Fundación Liga Deportiva Estudiantil. Sigue activa (torneos como
  la "Copa Luis Alfredo Mendoza Mendocita"). PROBABLE — no se encontró
  detalle actual de categorías/formato, solo su existencia y prestigio
  histórico.
- **Liga Colegial de Fútbol de Venezuela**: distinta de LIDES. Categorías
  confirmadas: **Sub-7, Sub-8, Sub-10, Sub-12, Sub-14, Sub-16, Sub-18**.
  En una edición reciente participaron ~215 instituciones y ~3.200
  jugadores en 8 meses de competencia (colegios como Los Arcos, Jefferson,
  British, San Ignacio de Loyola, La Salle, Hermandad Gallega, Instituto
  Cumbres). CONFIRMADO. Tiene reglamento propio publicado (PDF de bases de
  torneo).

**Hallazgo importante para el modelo de datos**: la Liga Colegial usa una
numeración de categorías (Sub-7, Sub-8, Sub-10, Sub-12...) que **no
coincide exactamente** con la de Liga Pipo Rossi (Compotas/Sub-06, Sub-07,
Sub-09, Sub-11...) ni con la de Liga Canguro Diamante (Sub-8, Sub-10,
Sub-12, Sub-14...). Confirma lo que ya advertía
`INVESTIGACION-ECOSISTEMA-VE.md` sección 4: **no existe una tabla nacional
única de categorías** — cada liga/asociación define su propio catálogo, a
veces con la misma edad bajo etiquetas distintas. El modelo de datos debe
tratar "categoría" como un valor **propio de cada competición**, no como
un catálogo global compartido.

Fuentes: [Liga Colegial de Fútbol de Venezuela — bases de torneo (PDF)](https://www.ligacolegialdefutbolvzla.com/uploadedDocs//27112019160233_12978.pdf) ·
[Empresas Polar — final 2023 Liga Colegial](https://empresaspolar.com/empresas-polar-y-sus-marcas-estuvieron-presentes-en-la-final-2023-de-la-liga-colegial-de-futbol-de-venezuela/) ·
[UNIMET — selección de fútbol campeona de LIDES](https://www.unimet.edu.ve/seleccion-de-futbol-de-la-unimet-se-titula-campeona-de-lides/)

## 9. Fútbol universitario

**Liga Universitaria U**: modelo de autogestión deportiva reactivado en
2016 tras un período crítico (suspensión de eventos como los "Juvines").
Integra 7 universidades de Caracas (Unimet, UCAB, UMA, USM, UCV, entre
otras) con más de 1.200 atletas activos en varias disciplinas —fútbol,
futsal, voleibol, baloncesto, pádel, ajedrez—. CONFIRMADO. No se encontró
una organización nacional separada bajo los nombres "FEVEDU" o "LUDU" que
el equipo había considerado como hipótesis de búsqueda — **esos nombres
no se confirmaron como entidades reales**; se descartan como pista, no se
inventan.

Fuente: [Venezuela Fútbol — Liga Universitaria U](https://www.venezuelafutbol.com.ve/la-liga-universitaria-u-un-modelo-de-autogestion-deportiva-que-impulsa-el-futuro-del-talento-joven-en-venezuela/)

## 10. Juegos Deportivos Nacionales / Juegos Nacionales Juveniles — estructura paralela por estados

Hallazgo estructuralmente importante: existe un sistema **completamente
distinto** al de las ligas de clubes — los **Juegos Deportivos Nacionales**
(organizados por Mindeporte, el ministerio del deporte), donde los
deportistas compiten **representando a su estado**, no a su club. Los
XXII Juegos Deportivos Nacionales Juveniles 2026 (Caracas, Miranda, La
Guaira) reúnen 48 federaciones deportivas en 71 disciplinas, con
categorías juveniles documentadas para fútbol en **Sub-13 y Sub-15** (edición
2023) y visorías de futsal masculino Sub-17 (edición 2026, en Mérida,
Táchira, Monagas, Carabobo, Aragua, Zulia y Delta Amacuro). CONFIRMADO
como estructura, INFORMACIÓN INCOMPLETA en el detalle completo de
categorías de fútbol 11 (solo se confirmaron Sub-13/Sub-15 en una edición
específica).

**Implicación para el modelo de datos**: "competición" no siempre implica
"club". Existe al menos un eje adicional — **selección estadal** — que
debe poder representarse como tipo de organización/participación distinta
de "club" y de "selección nacional". Esto es un tercer nivel que ni
`CONTEXTO-MAESTRO.md` ni las matrices anteriores habían contemplado
explícitamente.

Fuentes: [Juegos Deportivos Nacionales de Venezuela — Wikipedia](https://es.wikipedia.org/wiki/Juegos_Deportivos_Nacionales_de_Venezuela) ·
[Caracas2026.org — Juegos Nacionales Juveniles 2026](https://caracas2026.org/juegos-nacionales-juveniles-caracas-2026-fortaleceran-captacion-de-talento-deportivo/) ·
[FVF — Juegos Nacionales 2023, fases finales Sub-13 y Sub-15](https://www.fvf.com.ve/articulos/los-juegos-nacionales-2023-se-aproximan-a-las-fases-finales-en-sus-dos-categorias-sub-13-y-sub-15) ·
[FVF — visorías futsal Sub-17](https://www.fvf.com.ve/articulos/exito-en-las-visorias-del-futsal-masculino-sub17)

## 11. Academias privadas — más allá de Liga Pipo Rossi

Confirmadas, con foco en Caracas/Distrito Capital (mismo sesgo geográfico
que la investigación anterior — no se investigaron academias fuera de la
capital en esta ronda):

- **Academia Venezolana de Fútbol (AVF)** — fundada en 1980, la más
  antigua identificada. Participa en torneos de FVF y AFDC.
- **Academia Euroamericana de Fútbol (AEF)** — más de 10 años, edades 2-19
  años, sedes en Macaracuay, San Luis, Universidad Santa María y Colegio
  Internacional de Caracas.
- **Academia La Única** — edades 4-20, fútbol y futsal, avalada por FVF y
  por la Asociación de Fútbol y Futsal de Distrito Capital.
- **Academia Atlético de Madrid Venezuela (ATMVE)** — franquicia formativa
  de un club europeo operando en Caracas.
- **DLG Academia Naranja** — estructura formativa oficial de Deportivo La
  Guaira FC (club de Liga FUTVE), con sede en el este de Caracas y en
  Santa Rosa de Lima.

**Patrón confirmado**: varias de estas academias declaran doble afiliación
(FVF + asociación estadal) de forma simultánea — coincide con el hallazgo
ya registrado en `INVESTIGACION-ECOSISTEMA-VE.md` sección 3 (una misma
escuela puede competir en varias ligas a la vez). No se investigaron
academias fuera de Distrito Capital en esta ronda — hueco declarado.

Fuentes: [Academia La Única](https://academialaunica.odoo.com/) ·
[Academia Venezolana de Fútbol — perfil](https://forovinotinto.com/equipos/historia.php?id=avf) ·
[Academia Euroamericana de Fútbol](https://www.academiaeuroamericanadefutbol.com/) ·
[Atlético de Madrid Venezuela](https://atmve.com/) ·
[DLG Academia Naranja](https://www.dlgacademianaranja.com/)

## 12. Estructuras formales de scouting

No se encontró, en esta ronda ni en la anterior, una estructura de
scouting **institucional y unificada** a nivel nacional (ej. una red
oficial de ojeadores de la FVF con perfiles públicos). Lo que existe son:
scouts/ojeadores independientes o afiliados a asociaciones regionales
(patrón ya documentado en `INVESTIGACION-ECOSISTEMA-VE.md` sección 5), y
mecanismos puntuales de captación dentro de eventos específicos (ej. las
"visorías" de futsal Sub-17 mencionadas en la sección 10 de este
documento, organizadas estado por estado para los Juegos Nacionales).
**INFORMACIÓN INCOMPLETA** — no se puede afirmar que no exista una
estructura nacional de scouting, solo que esta investigación no la
encontró.

## 13. Huecos de información — resumen

- Cifra exacta de equipos y formato definitivo de la Segunda División
  (contradicción entre fuentes, sección 1).
- Relación exacta entre Liga FUTVE Futsal 1 y Liga Superior de Futsal
  (¿misma competición, renombrada, o distintas?).
- Doble definición contradictoria de "CONAFUTSAL" (arbitraje vs. comisión
  nacional).
- Detalle completo de "Ligas de Desarrollo FVF" (categorías, regiones,
  formato) — fuente bloqueada.
- 16 de 24 estados sin investigar (ver lista completa en sección 7).
- Detalle completo de LIDES actual (formato, categorías vigentes).
- Estructura y reglamento completo de Liga FUTVE 3 (Tercera División):
  cuántos equipos, cuántas fases estadales/regionales exactas.
- Nombre oficial vigente del último bloque de Liga FUTVE Junior (Sub-20 vs
  Sub-21) — hueco heredado de `INVESTIGACION-ECOSISTEMA-VE.md`, sigue sin
  resolverse.
- Academias privadas fuera de Distrito Capital.

Estos huecos quedan declarados, no rellenados — misma regla que el
documento anterior (sección 7 de `INVESTIGACION-ECOSISTEMA-VE.md`).

## 14. Qué cambia para el proyecto a partir de esta investigación

1. **El campo "categoría" nunca puede ser un catálogo único global.** Ya
   lo advertía el documento anterior para el fútbol formativo del
   Distrito Capital; esta investigación lo confirma también entre ligas
   escolares/colegiales (Sub-7/Sub-8/Sub-10... vs. Compotas/Sub-06/Sub-07...
   vs. Sub-8/Sub-10/Sub-12...). El modelo de datos debe atar la categoría
   a la competición que la define, no a una tabla maestra compartida.
2. **"Competición" tiene al menos tres ejes distintos, no uno**: liga de
   club (FVF/asociación estadal/privada), selección nacional por edad, y
   selección **estadal** en Juegos Deportivos Nacionales (representando al
   estado, no a un club). Ninguna matriz anterior había separado
   explícitamente este tercer eje.
3. **El país tiene múltiples modalidades activas y organizadas** más allá
   del fútbol 11 masculino de clubes: fútbol femenino, futsal (con su
   propia pirámide formativa), fútbol playa — cada una con selección
   nacional, liga(s) propia(s) y participación internacional. El campo
   "deporte/modalidad" del perfil (sección 20 del documento base) debe
   poder distinguir estas variantes, no asumir que "fútbol" es una sola
   cosa.
4. **La escala geográfica real es mayor de lo que el proyecto había
   trabajado hasta ahora.** Todo el trabajo de contexto/matching/boceto
   hecho hasta esta ronda usa datos de Distrito Capital exclusivamente.
   Existen al menos 7 asociaciones estadales adicionales con actividad
   confirmada (Zulia, Táchira, Carabobo, Miranda, Lara, Bolívar, Aragua) y
   16 más sin investigar todavía. El prototipo y el modelo de datos deben
   tratar "ubicación"/"región" como un catálogo por construir, no como
   Caracas + "otras ciudades" genérico.
5. **No se rediseña la arquitectura del producto en este documento.** Esta
   investigación es, como pide la instrucción del usuario, el paso previo
   — el modelado, la validación y la implementación de estos hallazgos en
   `CONTEXTO-MAESTRO.md`, las matrices o el prototipo quedan como trabajo
   posterior explícito, no implícito en esta entrega.
