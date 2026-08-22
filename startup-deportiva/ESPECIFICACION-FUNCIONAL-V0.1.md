============================================================
STARTUP DEPORTIVA
ESPECIFICACIÓN FUNCIONAL
MATRIZ DE CONTEXTO + MATRIZ DE CASOS DE USUARIO
VERSIÓN 0.1
============================================================

INSTRUCCIÓN PARA CLAUDE CODE
============================================================

Este documento define parte del comportamiento conceptual y
funcional de la startup deportiva.

NO convertir automáticamente estas matrices en una arquitectura
técnica definitiva.

Utilizarlas como:

- contexto de producto;
- reglas conceptuales;
- referencia para agentes;
- referencia para UX;
- referencia para modelado de datos;
- referencia para futuras decisiones de arquitectura.

Las decisiones técnicas definitivas deben tomarse después de
validar el producto.

PRINCIPIO FUNDAMENTAL:

PERFIL
+
CONTEXTO
+
NECESIDAD
+
OBJETIVO
↓
RECOMENDACIÓN
↓
ACCIÓN
↓
RESULTADO
↓
NUEVO CONTEXTO


============================================================
PARTE I
MATRIZ DE CONTEXTO
============================================================


1. PROPÓSITO
============================================================

La Matriz de Contexto define cómo la plataforma transforma la
información de una persona u organización en un CONTEXTO
OPERATIVO.

El contexto operativo determina:

- qué grupos son relevantes;
- qué actores son relevantes;
- qué oportunidades mostrar;
- qué necesidades mostrar;
- qué filtros activar;
- qué recomendaciones priorizar;
- qué acciones sugerir.

La plataforma NO debe depender únicamente de un "tipo de usuario".

Debe interpretar:

PERFIL
+
ROL
+
OBJETIVO
+
SITUACIÓN
+
NECESIDAD
+
UBICACIÓN
+
CARACTERÍSTICAS
+
COMPORTAMIENTO
+
HISTORIAL

para determinar:

CONTEXTO ACTUAL.


============================================================
2. PRINCIPIO FUNDAMENTAL
============================================================

ROL != CONTEXTO

El rol identifica QUIÉN ES EL USUARIO.

El contexto identifica:

- qué está viviendo;
- qué necesita;
- qué quiere conseguir;
- qué debería ser relevante para él AHORA.


Ejemplo:

Un jugador puede ser:

- jugador buscando academia;
- jugador buscando club;
- jugador buscando tryout;
- jugador buscando scout;
- jugador buscando entrenador;
- jugador buscando preparador físico;
- jugador buscando fisioterapeuta.

Por lo tanto:

UN MISMO PERFIL
puede tener
MÚLTIPLES CONTEXTOS.


============================================================
3. ESTRUCTURA DEL CONTEXTO
============================================================

CONTEXTO =

ROL
+
OBJETIVO
+
SITUACIÓN
+
NECESIDAD
+
NIVEL
+
ETAPA
+
UBICACIÓN
+
RESTRICCIONES
+
TEMPORALIDAD


============================================================
4. CONTEXTO DINÁMICO
============================================================

El contexto NO es permanente.

Puede cambiar por:

- edad;
- experiencia;
- objetivos;
- club actual;
- lesión;
- recuperación;
- cambio de ciudad;
- cambio de categoría;
- cambio de nivel;
- disponibilidad;
- resultados;
- nuevas necesidades;
- finalización de una oportunidad;
- comportamiento dentro de la plataforma;
- cambios de temporada;
- transición profesional.

Ejemplo:

Jugador de 16 años

↓
BUSCAR ACADEMIA

↓
Encuentra academia

↓
FORMACIÓN

↓
Quiere mejorar rendimiento

↓
PREPARACIÓN FÍSICA

↓
Tiene una lesión

↓
RECUPERACIÓN

↓
Se recupera

↓
COMPETICIÓN

↓
Busca oportunidad

↓
SCOUTING / TRYOUT


============================================================
5. CATEGORÍAS PRINCIPALES DE CONTEXTO
============================================================

A. INICIACIÓN
B. FORMACIÓN
C. DESARROLLO
D. COMPETICIÓN
E. SCOUTING
F. CAMBIO DE CLUB
G. PROFESIONALIZACIÓN
H. RECUPERACIÓN
I. PREPARACIÓN FÍSICA
J. ENTRENAMIENTO INDIVIDUAL
K. BÚSQUEDA DE PROFESIONALES
L. OPORTUNIDAD PROFESIONAL
M. NECESIDAD ORGANIZACIONAL
N. DESCUBRIMIENTO
O. TRANSICIÓN


============================================================
6. CONTEXTO A — INICIACIÓN
============================================================

PERFIL:

Niño / joven
+
poca o ninguna experiencia

OBJETIVO:

Comenzar a practicar un deporte.

NECESIDADES:

- academia;
- escuela;
- club formativo;
- entrenador;
- entrenamiento.

GRUPOS PRIORITARIOS:

- Academias;
- Escuelas;
- Clubes formativos;
- Entrenadores.

FILTROS:

- edad;
- ubicación;
- distancia;
- precio;
- horarios;
- nivel;
- modalidad.

RECOMENDACIÓN:

Priorizar opciones adecuadas para comenzar.


============================================================
7. CONTEXTO B — FORMACIÓN
============================================================

PERFIL:

Deportista joven
+
experiencia básica/intermedia.

OBJETIVO:

Mejorar habilidades.

NECESIDADES:

- academia;
- entrenador;
- entrenamiento;
- preparación física;
- recursos de formación.

GRUPOS:

- Academias;
- Entrenadores;
- Preparadores físicos;
- Clubes.

FILTROS:

- especialidad;
- nivel;
- distancia;
- precio;
- horarios;
- categoría.


============================================================
8. CONTEXTO C — DESARROLLO COMPETITIVO
============================================================

PERFIL:

Deportista
+
nivel competitivo.

OBJETIVO:

Mejorar rendimiento y competir.

NECESIDADES:

- club;
- entrenador;
- preparador físico;
- entrenamiento individual;
- competición;
- scouting.

GRUPOS:

- Clubes;
- Entrenadores;
- Preparadores físicos;
- Scouts;
- Competiciones.

FILTROS:

- categoría;
- posición;
- nivel;
- competición;
- distancia;
- experiencia;
- disponibilidad.


============================================================
9. CONTEXTO D — SCOUTING
============================================================

PERFIL:

Deportista competitivo.

OBJETIVO:

Ser descubierto / encontrar oportunidades.

NECESIDADES:

- club;
- tryout;
- scout;
- representante;
- competición.

GRUPOS:

- Clubes;
- Scouts;
- Representantes;
- Competiciones.

FILTROS:

- deporte;
- posición;
- categoría;
- nivel;
- ubicación;
- edad;
- competición;
- requisitos.


============================================================
10. CONTEXTO E — CAMBIO DE CLUB
============================================================

PERFIL:

Deportista con experiencia.

SITUACIÓN:

Ya pertenece o pertenecó a un club.

OBJETIVO:

Encontrar una nueva organización.

NECESIDADES:

- club;
- tryout;
- scouting;
- entrenador;
- oportunidades.

GRUPOS:

- Clubes;
- Scouts;
- Tryouts;
- Representantes.

FILTROS:

- ubicación;
- categoría;
- nivel;
- competición;
- posición;
- requisitos.


============================================================
11. CONTEXTO F — PREPARACIÓN FÍSICA
============================================================

PERFIL:

Deportista.

OBJETIVO:

Mejorar rendimiento físico.

NECESIDADES:

- preparador físico;
- entrenador personal;
- programa de entrenamiento;
- centro de entrenamiento.

GRUPOS:

- Preparadores físicos;
- Entrenadores personales;
- Centros deportivos.

FILTROS:

- especialidad;
- ubicación;
- distancia;
- precio;
- modalidad;
- disponibilidad;
- experiencia;
- certificaciones.


============================================================
12. CONTEXTO G — FISIOTERAPIA / RECUPERACIÓN
============================================================

PERFIL:

Deportista.

SITUACIÓN:

Necesidad de recuperación o prevención.

OBJETIVO:

Recuperarse / prevenir / mejorar condición física.

NECESIDADES:

- fisioterapeuta;
- especialista deportivo;
- centro de rehabilitación;
- profesional específico.

GRUPOS:

- Fisioterapeutas;
- Especialistas;
- Centros.

FILTROS:

- especialidad;
- ubicación;
- distancia;
- disponibilidad;
- precio;
- certificaciones;
- experiencia.

RESTRICCIÓN:

La plataforma NO debe diagnosticar médicamente al usuario.

La plataforma puede ayudar a encontrar profesionales.

La evaluación clínica pertenece al profesional.


============================================================
13. CONTEXTO H — ENTRENAMIENTO INDIVIDUAL
============================================================

PERFIL:

Deportista.

OBJETIVO:

Mejorar una capacidad específica.

EJEMPLOS:

- técnica;
- velocidad;
- fuerza;
- resistencia;
- habilidades específicas;
- posicionamiento.

NECESIDADES:

- entrenador;
- entrenador personal;
- preparador físico;
- especialista.

GRUPOS:

- Entrenadores;
- Preparadores físicos;
- Especialistas.

FILTROS:

- especialidad;
- nivel;
- ubicación;
- precio;
- disponibilidad;
- modalidad.


============================================================
14. CONTEXTO I — PROFESIONALIZACIÓN
============================================================

PERFIL:

Deportista avanzado.

OBJETIVO:

Dar el siguiente salto competitivo/profesional.

NECESIDADES:

- club;
- scout;
- representante;
- entrenador;
- preparador físico;
- fisioterapeuta;
- oportunidades.

GRUPOS:

- Clubes;
- Scouts;
- Representantes;
- Profesionales deportivos.

El sistema puede crear una experiencia mucho más especializada.


============================================================
15. CONTEXTO J — OPORTUNIDAD PROFESIONAL
============================================================

PERFIL:

Profesional deportivo.

EJEMPLOS:

- entrenador;
- fisioterapeuta;
- preparador físico;
- analista;
- asistente;
- utillero;
- staff.

OBJETIVO:

Encontrar trabajo / colaboración.

NECESIDADES:

- club;
- academia;
- equipo;
- organización.

GRUPOS:

- Clubes;
- Academias;
- Equipos;
- Organizaciones.

FILTROS:

- puesto;
- categoría;
- deporte;
- nivel;
- ubicación;
- disponibilidad;
- certificaciones;
- experiencia.


============================================================
16. CONTEXTO K — NECESIDAD ORGANIZACIONAL
============================================================

PERFIL:

- club;
- academia;
- equipo;
- organización.

OBJETIVO:

Resolver una necesidad.

TIPOS DE NECESIDAD:

- jugador;
- entrenador;
- fisioterapeuta;
- preparador físico;
- analista;
- scout;
- staff;
- asistente;
- utillero;
- otros.

FLUJO:

ORGANIZACIÓN
↓
CREA NECESIDAD
↓
DEFINE CRITERIOS
↓
PLATAFORMA BUSCA
↓
MATCHING
↓
PERFILES COMPATIBLES


============================================================
17. CONTEXTO L — DESCUBRIMIENTO
============================================================

PERFIL:

Cualquier actor.

SITUACIÓN:

No tiene una necesidad perfectamente definida.

La plataforma debe poder recomendar:

"Según tu perfil y contexto, estas son algunas cosas
que pueden interesarte."

Ejemplo:

Jugador de 15 años:

- clubes cercanos;
- entrenamientos;
- tryouts;
- preparadores físicos;
- competiciones.

La plataforma funciona también como:

MOTOR DE DESCUBRIMIENTO.


============================================================
18. CONTEXTO M — TRANSICIÓN
============================================================

El usuario cambia de situación.

Ejemplos:

- cambio de categoría;
- cambio de ciudad;
- cambio de deporte;
- cambio de club;
- finalización de temporada;
- incorporación a equipo;
- lesión;
- recuperación;
- profesionalización.

El contexto debe actualizarse.


============================================================
19. CONTEXTO → GRUPOS
============================================================

INICIACIÓN
→ Academias / Escuelas / Clubes formativos

FORMACIÓN
→ Academias / Entrenadores / Clubes

DESARROLLO
→ Clubes / Entrenadores / Preparadores físicos

COMPETICIÓN
→ Clubes / Competiciones / Entrenadores

SCOUTING
→ Scouts / Clubes / Tryouts / Representantes

CAMBIO DE CLUB
→ Clubes / Tryouts / Scouts

PREPARACIÓN FÍSICA
→ Preparadores físicos / Entrenadores personales

RECUPERACIÓN
→ Fisioterapeutas / Especialistas / Centros

ENTRENAMIENTO INDIVIDUAL
→ Entrenadores / Preparadores / Especialistas

PROFESIONALIZACIÓN
→ Clubes / Scouts / Representantes / Profesionales

OPORTUNIDAD PROFESIONAL
→ Clubes / Academias / Equipos

NECESIDAD ORGANIZACIONAL
→ Personas compatibles

DESCUBRIMIENTO
→ Recomendaciones contextuales

TRANSICIÓN
→ Nuevas oportunidades relevantes


============================================================
20. NUEVO PRINCIPIO DE LA PLATAFORMA
============================================================

La plataforma NO conecta únicamente:

DEPORTISTA ↔ CLUB

También puede conectar:

DEPORTISTA ↔ ACADEMIA
DEPORTISTA ↔ ENTRENADOR
DEPORTISTA ↔ PREPARADOR FÍSICO
DEPORTISTA ↔ FISIOTERAPEUTA
DEPORTISTA ↔ ESPECIALISTA
DEPORTISTA ↔ COMPETICIÓN
DEPORTISTA ↔ SCOUT
DEPORTISTA ↔ TRYOUT

PROFESIONAL ↔ CLUB
PROFESIONAL ↔ ACADEMIA
PROFESIONAL ↔ EQUIPO

CLUB ↔ JUGADOR
CLUB ↔ STAFF
CLUB ↔ ENTRENADOR
CLUB ↔ FISIOTERAPEUTA
CLUB ↔ PREPARADOR FÍSICO
CLUB ↔ OTROS PROFESIONALES


============================================================
21. PRINCIPIO DE DESCUBRIMIENTO
============================================================

El usuario no necesita conocer todas las posibilidades
de la plataforma.

La plataforma debe descubrir necesidades potenciales
a partir del contexto.

Ejemplo:

Jugador competitivo

↓
La plataforma detecta que pueden ser relevantes:

- club;
- preparación física;
- entrenador;
- scouting;
- tryouts.

Pero:

NO mostrar todo simultáneamente.

PRIORIDAD
↓
RELEVANCIA
↓
MOMENTO


============================================================
22. PRIORIDAD DE RECOMENDACIONES
============================================================

RECOMENDACIÓN =

RELEVANCIA
+
OBJETIVO
+
CONTEXTO
+
PROXIMIDAD
+
DISPONIBILIDAD
+
COMPATIBILIDAD

La fórmula definitiva todavía NO está definida.


============================================================
23. PRINCIPIO DE NO SOBRECARGA
============================================================

La plataforma puede contener:

- clubes;
- academias;
- scouting;
- tryouts;
- entrenadores;
- preparadores físicos;
- fisioterapeutas;
- staff;
- oportunidades;
- necesidades;
- competiciones;
- etc.

Pero el usuario no debe percibir todo simultáneamente.

Diferenciar:

CAPACIDADES INTERNAS

de:

EXPERIENCIA VISIBLE.


============================================================
24. PRINCIPIO DE EVOLUCIÓN
============================================================

El mismo usuario puede atravesar múltiples contextos.

Ejemplo:

Jugador 11 años
↓
Iniciación
↓
Formación
↓
Competición
↓
Scouting
↓
Club
↓
Profesionalización


============================================================
25. ESTADO
============================================================

MATRIZ DE CONTEXTO:

V0.1

ESTADO:

Conceptual.

Debe validarse mediante casos reales.

============================================================
FIN MATRIZ DE CONTEXTO
============================================================



============================================================
PARTE II
MATRIZ DE CASOS DE USUARIO
============================================================


OBJETIVO
============================================================

Validar que el sistema pueda interpretar diferentes perfiles,
situaciones y necesidades sin obligarlos a navegar por un
catálogo gigante de funcionalidades.

PRINCIPIO:

PERFIL
+
ROL
+
SITUACIÓN
+
OBJETIVO
+
NECESIDAD
+
CONTEXTO
↓
RECOMENDACIÓN
↓
ACCIÓN


============================================================
CASO 01 — NIÑO DE 11 AÑOS SIN EXPERIENCIA
============================================================

PERFIL:
- 11 años
- fútbol
- sin experiencia

ROL:
- deportista

SITUACIÓN:
- quiere comenzar

OBJETIVO:
- aprender

CONTEXTO:
- iniciación

PRIORIDAD:
1. Academias
2. Escuelas
3. Clubes formativos

SECUNDARIO:
- entrenadores
- entrenamiento individual

FILTROS:
- edad
- ubicación
- distancia
- precio
- horarios
- nivel

NO PRIORITARIO:
- scouting profesional
- representantes
- tryouts profesionales

ACCIÓN:
→ encontrar opción para comenzar


============================================================
CASO 02 — JUGADOR JOVEN BUSCA ACADEMIA
============================================================

PERFIL:
- 12 años
- experiencia básica

ROL:
- deportista

OBJETIVO:
- entrenar regularmente

CONTEXTO:
- formación

PRIORIDAD:
- academias
- escuelas
- clubes formativos

FILTROS:
- edad
- ubicación
- distancia
- precio
- horarios
- nivel competitivo

ACCIÓN:
→ comparar academias


============================================================
CASO 03 — JUGADOR JUVENIL COMPETITIVO
============================================================

PERFIL:
- 16 años
- Sub-17
- experiencia competitiva

OBJETIVO:
- mejorar nivel

CONTEXTO:
- desarrollo competitivo

PRIORIDAD:
- clubes
- competiciones
- entrenadores
- preparadores físicos

SECUNDARIO:
- scouting
- tryouts

FILTROS:
- categoría
- nivel
- competición
- ubicación
- posición
- disponibilidad

ACCIÓN:
→ explorar oportunidades de desarrollo


============================================================
CASO 04 — JUGADOR BUSCA CLUB
============================================================

PERFIL:
- 17 años
- competitivo

SITUACIÓN:
- quiere cambiar de club

OBJETIVO:
- encontrar nuevo equipo

CONTEXTO:
- cambio de club

PRIORIDAD:
- clubes
- tryouts
- scouts

SECUNDARIO:
- representantes

FILTROS:
- categoría
- posición
- competición
- nivel
- ubicación
- distancia
- requisitos

ACCIÓN:
→ encontrar clubes compatibles


============================================================
CASO 05 — JUGADOR BUSCA TRYOUT
============================================================

PERFIL:
- 16 años
- competitivo

OBJETIVO:
- conseguir una prueba

CONTEXTO:
- scouting / oportunidad

PRIORIDAD:
- tryouts

SECUNDARIO:
- clubes
- scouts

FILTROS:
- edad
- categoría
- posición
- fecha
- ubicación
- nivel
- requisitos

ACCIÓN:
→ solicitar / inscribirse


============================================================
CASO 06 — JUGADOR BUSCA SCOUT
============================================================

PERFIL:
- jugador competitivo

OBJETIVO:
- aumentar exposición

CONTEXTO:
- scouting

PRIORIDAD:
- scouts
- clubes
- oportunidades

SECUNDARIO:
- representantes

FILTROS:
- deporte
- posición
- categoría
- nivel
- ubicación
- experiencia

ACCIÓN:
→ encontrar oportunidades


============================================================
CASO 07 — JUGADOR BUSCA ENTRENADOR
============================================================

PERFIL:
- jugador

OBJETIVO:
- mejorar técnica

CONTEXTO:
- entrenamiento individual

PRIORIDAD:
- entrenadores

SECUNDARIO:
- especialistas
- preparadores físicos

FILTROS:
- especialidad
- deporte
- nivel
- ubicación
- distancia
- precio
- horarios
- modalidad

ACCIÓN:
→ encontrar entrenador


============================================================
CASO 08 — JUGADOR BUSCA PREPARADOR FÍSICO
============================================================

PERFIL:
- jugador competitivo

OBJETIVO:
- mejorar rendimiento físico

CONTEXTO:
- preparación física

PRIORIDAD:
- preparadores físicos
- entrenadores personales

SECUNDARIO:
- centros deportivos

FILTROS:
- especialidad
- deporte
- nivel
- ubicación
- precio
- disponibilidad
- modalidad
- certificaciones

ACCIÓN:
→ encontrar profesional


============================================================
CASO 09 — JUGADOR NECESITA FISIOTERAPEUTA
============================================================

PERFIL:
- deportista

SITUACIÓN:
- necesita recuperación / prevención

OBJETIVO:
- recibir atención profesional

CONTEXTO:
- recuperación

PRIORIDAD:
- fisioterapeutas
- especialistas deportivos
- centros

FILTROS:
- especialidad
- ubicación
- distancia
- precio
- disponibilidad
- certificaciones

RESTRICCIÓN:
- no diagnosticar
- no prescribir tratamiento automáticamente

ACCIÓN:
→ encontrar profesional


============================================================
CASO 10 — JUGADOR + ENTRENADOR
============================================================

PERFIL:
- jugador
- entrenador

ROLES:
- deportista
- profesional deportivo

SITUACIÓN:
- busca club como jugador
- busca trabajo como entrenador

CONTEXTO ACTIVO:
- cambio de club

CONTEXTO SECUNDARIO:
- oportunidad profesional

PRIORIDAD:
- clubes / tryouts

SECUNDARIO:
- vacantes de entrenador

REGLA:

NO crear dos cuentas.

Un perfil puede contener múltiples roles.

ACCIÓN:
→ resolver primero el contexto activo


============================================================
CASO 11 — ENTRENADOR BUSCA CLUB
============================================================

PERFIL:
- entrenador

OBJETIVO:
- encontrar trabajo

CONTEXTO:
- oportunidad profesional

PRIORIDAD:
- clubes
- academias
- equipos

FILTROS:
- deporte
- categoría
- nivel
- ubicación
- experiencia
- certificaciones
- disponibilidad

ACCIÓN:
→ encontrar oportunidades laborales


============================================================
CASO 12 — FISIOTERAPEUTA BUSCA EQUIPO
============================================================

PERFIL:
- fisioterapeuta deportivo

OBJETIVO:
- trabajar con equipo / club

CONTEXTO:
- oportunidad profesional

PRIORIDAD:
- clubes
- academias
- equipos

FILTROS:
- especialidad
- deporte
- categoría
- nivel
- ubicación
- disponibilidad
- certificaciones
- experiencia

ACCIÓN:
→ encontrar organizaciones compatibles


============================================================
CASO 13 — CLUB BUSCA JUGADOR
============================================================

PERFIL:
- club

SITUACIÓN:
- tiene una vacante

OBJETIVO:
- encontrar jugador

NECESIDAD:
- lateral derecho Sub-17

CONTEXTO:
- necesidad organizacional

PRIORIDAD:
- jugadores compatibles
- scouts
- oportunidades

FILTROS:
- posición
- edad
- categoría
- nivel
- ubicación
- experiencia
- características requeridas

ACCIÓN:
→ encontrar candidatos compatibles


============================================================
CASO 14 — CLUB BUSCA STAFF
============================================================

PERFIL:
- club

NECESIDAD:
- fisioterapeuta

CONTEXTO:
- necesidad organizacional

PRIORIDAD:
- fisioterapeutas

SECUNDARIO:
- profesionales deportivos

FILTROS:
- certificación
- experiencia
- especialidad
- disponibilidad
- ubicación

ACCIÓN:
→ publicar necesidad / encontrar profesionales


============================================================
CASO 15 — CLUB CON MÚLTIPLES NECESIDADES
============================================================

PERFIL:
- club

NECESIDADES:

1. Jugador Sub-17
2. Fisioterapeuta
3. Preparador físico
4. Entrenador

CONTEXTO:
- necesidad organizacional

REGLA:

NO convertir las necesidades en una búsqueda gigante.

Separar:

NECESIDAD 01
→ jugador

NECESIDAD 02
→ fisioterapeuta

NECESIDAD 03
→ preparador físico

NECESIDAD 04
→ entrenador

Cada necesidad tiene:

- criterios;
- prioridad;
- estado;
- candidatos;
- progreso.


============================================================
CASO 16 — PADRE / FAMILIA BUSCA OPCIÓN
============================================================

PERFIL:
- padre / representante familiar

USUARIO FINAL:
- niño

SITUACIÓN:
- quiere comenzar fútbol

OBJETIVO:
- encontrar opción adecuada

CONTEXTO:
- iniciación

PRIORIDAD:
- academias
- escuelas
- clubes

FILTROS:
- edad del hijo
- ubicación
- distancia
- precio
- horarios
- nivel

IMPORTANTE:

Distinguir:

QUIÉN USA LA PLATAFORMA

de:

QUIÉN ES EL DEPORTISTA.


============================================================
CASO 17 — SCOUT BUSCA JUGADORES
============================================================

PERFIL:
- scout

OBJETIVO:
- encontrar talento

CONTEXTO:
- scouting

NECESIDAD:

Ejemplo:
- laterales derechos
- Sub-17
- determinada región

PRIORIDAD:
- perfiles compatibles

FILTROS:
- edad
- posición
- categoría
- ubicación
- nivel
- características

ACCIÓN:
→ descubrir candidatos


============================================================
CASO 18 — ACADEMIA BUSCA ENTRENADOR
============================================================

PERFIL:
- academia

NECESIDAD:
- entrenador Sub-13

CONTEXTO:
- necesidad organizacional

PRIORIDAD:
- entrenadores compatibles

FILTROS:
- categoría
- certificación
- experiencia
- ubicación
- disponibilidad

ACCIÓN:
→ encontrar candidatos


============================================================
CASO 19 — EQUIPO BUSCA STAFF COMPLETO
============================================================

PERFIL:
- equipo

NECESIDADES:

- entrenador
- fisioterapeuta
- preparador físico
- asistente
- utillero

CONTEXTO:
- necesidad organizacional

MODELO:

EQUIPO
│
├── necesidad → entrenador
├── necesidad → fisioterapeuta
├── necesidad → preparador físico
├── necesidad → asistente
└── necesidad → utillero

Cada necesidad funciona como unidad independiente.


============================================================
CASO 20 — USUARIO SIN NECESIDAD DEFINIDA
============================================================

PERFIL:
- cualquier actor

SITUACIÓN:
- no sabe qué buscar

OBJETIVO:
- explorar

CONTEXTO:
- descubrimiento

La plataforma utiliza:

- perfil;
- historial;
- contexto;
- ubicación;
- actividad;

para sugerir:

- oportunidades;
- recursos;
- profesionales;
- clubes;
- academias;
- necesidades.

ACCIÓN:
→ descubrir.


============================================================
CASO 21 — USUARIO EN TRANSICIÓN
============================================================

EJEMPLO:

Jugador termina temporada.

SITUACIÓN:
- finaliza relación con club.

CONTEXTO ANTERIOR:
- competición

NUEVO CONTEXTO:
- cambio de club

La plataforma adapta recomendaciones.

PRIORIDAD:

- nuevos clubes;
- tryouts;
- scouts.


============================================================
MATRIZ GENERAL DE ACTORES
============================================================

ACTOR
│
├── DEPORTISTA
│   ├── buscar club
│   ├── buscar academia
│   ├── buscar entrenador
│   ├── buscar preparador físico
│   ├── buscar fisioterapeuta
│   ├── buscar scout
│   ├── buscar tryout
│   └── buscar oportunidades
│
├── FAMILIA
│   ├── buscar academia
│   ├── buscar club
│   └── buscar formación
│
├── ENTRENADOR
│   ├── buscar club
│   ├── buscar academia
│   └── ofrecer servicios
│
├── PREPARADOR FÍSICO
│   ├── buscar club
│   ├── buscar deportistas
│   └── ofrecer servicios
│
├── FISIOTERAPEUTA
│   ├── buscar club
│   ├── buscar deportistas
│   └── ofrecer servicios
│
├── SCOUT
│   └── buscar talento
│
├── CLUB
│   ├── buscar jugadores
│   ├── buscar staff
│   ├── crear tryouts
│   ├── crear necesidades
│   └── publicar oportunidades
│
├── ACADEMIA
│   ├── buscar entrenadores
│   ├── buscar jugadores
│   └── publicar oportunidades
│
└── EQUIPO
    ├── buscar jugadores
    ├── buscar staff
    └── publicar necesidades


============================================================
PRINCIPIO DE MATCHING
============================================================

El matching puede producirse entre:

PERSONA ↔ ORGANIZACIÓN

PERSONA ↔ PERSONA

PERSONA ↔ OPORTUNIDAD

ORGANIZACIÓN ↔ PERSONA

ORGANIZACIÓN ↔ ORGANIZACIÓN

ORGANIZACIÓN ↔ NECESIDAD


NO limitar el sistema a:

JUGADOR ↔ CLUB.


============================================================
PRINCIPIO DE NECESIDAD
============================================================

Toda búsqueda importante debe poder expresarse como:

QUIERO ENCONTRAR
+
CRITERIOS
+
CONTEXTO


Ejemplo:

CLUB

Necesito:
Lateral derecho

Categoría:
Sub-17

Ubicación:
New Jersey

Nivel:
Competitivo

↓

PLATAFORMA

Busca perfiles compatibles.


============================================================
PRINCIPIO DE OPORTUNIDAD
============================================================

Toda oportunidad debería contener conceptualmente:

QUIÉN
+
QUÉ
+
PARA QUIÉN
+
DÓNDE
+
CUÁNDO
+
REQUISITOS
+
CONDICIONES
+
ESTADO


Ejemplo:

TRYOUT

Club:
X

Categoría:
Sub-17

Posición:
Defensa

Fecha:
X

Ubicación:
X

Requisitos:
X

Estado:
Abierto


============================================================
PRINCIPIO DE RECOMENDACIÓN
============================================================

La plataforma no debe limitarse a decir:

"Esto existe."

Debe poder determinar:

"Esto probablemente te interesa."

Basándose en:

- perfil;
- contexto;
- objetivo;
- ubicación;
- disponibilidad;
- compatibilidad;
- historial;
- prioridad.


============================================================
PRINCIPIO DE VISIBILIDAD
============================================================

NO TODO LO DISPONIBLE
=
NO TODO LO VISIBLE.

Ejemplo:

Jugador de 11 años sin experiencia:

MOSTRAR:

1. Academias
2. Escuelas
3. Entrenamiento

NO PRIORIZAR:

- representantes;
- scouting profesional;
- tryouts profesionales.


============================================================
PRINCIPIO DE EVOLUCIÓN
============================================================

El mismo usuario puede atravesar múltiples contextos:

Jugador 11 años
↓
Iniciación
↓
Formación
↓
Competición
↓
Scouting
↓
Club
↓
Profesionalización


============================================================
CONCLUSIÓN FUNCIONAL
============================================================

La plataforma NO debe estructurarse principalmente como:

"¿Qué tipo de usuario eres?"

Debe estructurarse como:

"¿Quién eres + qué está pasando contigo + qué necesitas?"

El perfil define las posibilidades.

El contexto define la prioridad.

La necesidad define la búsqueda.

La oportunidad define lo disponible.

El matching define las coincidencias.

La recomendación define qué aparece primero.

La acción define qué ocurre después.

El resultado puede modificar el contexto.


============================================================
SIGUIENTE ETAPA DE PRODUCTO
============================================================

A partir de estas matrices, la siguiente pieza que debe diseñarse
NO es todavía la arquitectura técnica definitiva.

El siguiente paso funcional es construir:

MATRIZ DE NECESIDADES Y OPORTUNIDADES

Esta matriz debe definir:

1. Qué puede necesitar cada actor.
2. Qué puede ofrecer cada actor.
3. Cómo se estructura una necesidad.
4. Cómo se estructura una oportunidad.
5. Qué criterios puede utilizar el matching.
6. Qué información necesita cada búsqueda.
7. Qué información necesita cada perfil.
8. Qué estados puede tener una necesidad.
9. Qué estados puede tener una oportunidad.
10. Cómo una necesidad genera recomendaciones.

Después de validar esa matriz:

MATRIZ DE MATCHING
↓
MATRIZ DE RECOMENDACIONES
↓
UX / NAVEGACIÓN
↓
MVP
↓
ARQUITECTURA TÉCNICA
↓
IMPLEMENTACIÓN

============================================================
FIN DEL DOCUMENTO
============================================================
