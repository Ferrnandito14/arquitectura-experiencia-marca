============================================================
STARTUP DEPORTIVA
MATRIZ DE RECOMENDACIONES
VERSIÓN 0.1
============================================================

PROPÓSITO
============================================================

Definir cómo la plataforma transforma los resultados del
MATCHING en recomendaciones concretas para cada usuario.

La plataforma NO debe convertirse en un catálogo infinito.

PRINCIPIO:

ENTENDER AL USUARIO
        ↓
DETECTAR NECESIDADES
        ↓
EVALUAR OPORTUNIDADES
        ↓
PRIORIZAR
        ↓
RECOMENDAR
        ↓
PERMITIR EXPLORAR MÁS


============================================================
1. DIFERENCIA ENTRE MATCHING Y RECOMENDACIÓN
============================================================

MATCHING:

Determina qué tan compatible es una oportunidad con el usuario.


RECOMENDACIÓN:

Determina:

- qué mostrar;
- en qué orden;
- en qué grupo;
- con qué prioridad;
- con qué explicación;
- cuándo mostrarlo;
- cuándo dejar de mostrarlo.


MATCHING
=
COMPATIBILIDAD


RECOMENDACIÓN
=
COMPATIBILIDAD + CONTEXTO + PRIORIDAD + MOMENTO


============================================================
2. PRINCIPIO DE EXPERIENCIA
============================================================

El usuario NO debe entrar y preguntarse:

"¿Qué hago ahora?"


La plataforma debe interpretar su perfil y contexto
y presentar caminos relevantes.


Ejemplo:

PERFIL:

11 años
Principiante
Fútbol
Miami


La plataforma puede mostrar:

"Opciones para comenzar a entrenar"

- Academias cercanas
- Escuelas de iniciación
- Entrenadores
- Programas para principiantes


No mostrar inicialmente:

- Tryouts profesionales
- Scouting profesional
- Vacantes de staff


============================================================
3. RECOMENDACIÓN CONTEXTUAL
============================================================

Las recomendaciones dependen de:

- tipo de usuario;
- edad;
- deporte;
- nivel;
- categoría;
- posición;
- club actual;
- historial;
- ubicación;
- disponibilidad;
- presupuesto;
- objetivo;
- necesidad;
- preferencias;
- actividad reciente;
- oportunidades disponibles.


============================================================
4. PERFIL + CONTEXTO + NECESIDAD
============================================================

La recomendación se genera mediante:


PERFIL
+
CONTEXTO ACTUAL
+
NECESIDAD
+
MATCHING
+
ESTADO DE LA OPORTUNIDAD


No utilizar solamente información estática del perfil.


============================================================
5. RECOMENDACIÓN PRINCIPAL
============================================================

Cada usuario puede tener una:

NECESIDAD / RECOMENDACIÓN PRINCIPAL.


Ejemplo:

Jugador principiante:

"Academias para comenzar"


Jugador competitivo:

"Oportunidades para competir"


Jugador buscando club:

"Clubes y tryouts compatibles"


Deportista:

"Preparadores físicos cercanos"


Fisioterapeuta:

"Clubes que buscan fisioterapia"


Club:

"Profesionales disponibles para tu necesidad"


============================================================
6. RECOMENDACIONES SECUNDARIAS
============================================================

Además de la necesidad principal pueden aparecer
necesidades relacionadas.


Ejemplo:

Jugador busca club.


PRINCIPAL:

Clubes / tryouts.


SECUNDARIAS:

- preparación física;
- entrenador;
- fisioterapia;
- scouting;
- competiciones.


No mostrar todas simultáneamente con el mismo peso.


============================================================
7. AGRUPACIÓN
============================================================

Las recomendaciones deben organizarse por grupos.


Ejemplo:

PARA TI

├── Clubes recomendados
├── Tryouts próximos
├── Academias cercanas
├── Entrenadores
└── Preparadores físicos


Esto evita presentar una lista plana.


============================================================
8. GRUPOS FUNCIONALES
============================================================

Los grupos deben depender del actor.


POSIBLES GRUPOS:

- Buscar club
- Buscar academia
- Buscar tryouts
- Buscar oportunidades
- Buscar entrenador
- Buscar preparador físico
- Buscar fisioterapeuta
- Buscar staff
- Buscar trabajo
- Buscar jugadores
- Buscar profesionales
- Buscar competición
- Buscar servicios


No todos los grupos aparecen para todos los usuarios.


============================================================
9. RECOMENDACIONES ADAPTATIVAS
============================================================

El sistema puede modificar los grupos según el perfil.


Ejemplo:

NIÑO PRINCIPIANTE:

1. Academias
2. Entrenamiento
3. Clubes formativos


JUGADOR COMPETITIVO:

1. Clubes
2. Tryouts
3. Scouting
4. Competiciones


FISIOTERAPEUTA:

1. Vacantes
2. Clubes
3. Academias
4. Colaboraciones


CLUB:

1. Jugadores
2. Staff
3. Servicios
4. Oportunidades


============================================================
10. CLUB ACTUAL DEL JUGADOR
============================================================

Cuando aplique, el club actual debe formar parte
del contexto de recomendación.


JUGADOR
+
CLUB ACTUAL
+
CATEGORÍA
+
COMPETICIÓN
+
NIVEL


pueden modificar las recomendaciones.


Ejemplo:

Jugador:

16 años
Sub-17
Lateral derecho
Club actual X


La plataforma puede identificar:

- oportunidades de continuidad;
- competiciones compatibles;
- tryouts externos;
- clubes de nivel similar o superior;
- necesidades de entrenamiento;
- servicios complementarios.


IMPORTANTE:

La existencia de un club actual NO significa que el
jugador esté buscando abandonarlo.


El sistema debe distinguir:

- pertenece a club;
- busca mejorar;
- busca oportunidades;
- busca cambiar;
- busca servicios.


============================================================
11. HISTORIAL DEL JUGADOR
============================================================

El historial puede mejorar las recomendaciones.


Ejemplo:

Club actual:
Club A


Historial:

Club B
Academia C


Esto ayuda a entender:

- trayectoria;
- experiencia;
- evolución;
- nivel.


No debe convertirse automáticamente en una recomendación
de cambio de club.


============================================================
12. RECOMENDACIÓN POR OBJETIVO
============================================================

OBJETIVO:

Comenzar.


Recomendar:

- academias;
- iniciación;
- entrenadores.


OBJETIVO:

Competir.


Recomendar:

- clubes;
- equipos;
- competiciones.


OBJETIVO:

Ser descubierto.


Recomendar:

- tryouts;
- showcases;
- scouting.


OBJETIVO:

Mejorar.


Recomendar:

- entrenadores;
- preparadores físicos;
- fisioterapia;
- programas.


OBJETIVO:

Trabajar.


Recomendar:

- vacantes;
- organizaciones;
- colaboraciones.


============================================================
13. RECOMENDACIÓN POR PROXIMIDAD
============================================================

La distancia puede afectar el orden.


Ejemplo:

Academia A
5 km


Academia B
12 km


Academia C
28 km


Si las demás variables son similares:

A > B > C


Pero:

DISTANCIA NO DEBE SER EL ÚNICO CRITERIO.


============================================================
14. RECOMENDACIÓN POR PRECIO
============================================================

Dentro del presupuesto:

Mayor prioridad.


Fuera del presupuesto:

Menor prioridad o exclusión según contexto.


La plataforma debe distinguir:

- precio conocido;
- precio desconocido;
- precio variable;
- precio bajo;
- precio alto.


NO asumir precio desconocido = gratis.


============================================================
15. RECOMENDACIÓN POR HORARIO
============================================================

Si el horario coincide:

Aumentar relevancia.


Si no coincide:

Reducir relevancia.


Si el horario es obligatorio:

Puede excluir.


============================================================
16. RECOMENDACIÓN POR NIVEL
============================================================

Una oportunidad debe ser compatible
con el nivel actual.


Ejemplo:

Principiante:

Academia iniciación
→ alta.


Academia alto rendimiento
→ baja.


Jugador competitivo:

Club competitivo
→ alta.


Entrenamiento exclusivamente recreativo
→ baja.


============================================================
17. RECOMENDACIÓN POR CATEGORÍA
============================================================

Debe considerar:

- edad;
- categoría;
- deporte;
- temporada.


Ejemplo:

Jugador Sub-15


Recomendaciones prioritarias:

Sub-15.


Posiblemente:

Sub-16 según reglas.


No:

Sub-10.


============================================================
18. RECOMENDACIÓN POR COMPETICIÓN
============================================================

Para usuarios competitivos:


Objetivo:

Competir a nivel regional.


Priorizar:

Competiciones regionales.


Objetivo:

Alto rendimiento.


Priorizar:

Competiciones de mayor nivel.


============================================================
19. RECOMENDACIÓN TEMPORAL
============================================================

Las oportunidades cercanas en el tiempo
pueden recibir prioridad.


Ejemplo:

TRYOUT


Fecha:

sábado.


Usuario compatible.


→ Alta prioridad.


Tryout:

dentro de 6 meses.


→ menor prioridad.


============================================================
20. RECOMENDACIÓN POR URGENCIA
============================================================

No toda oportunidad tiene la misma urgencia.


Ejemplo:

Vacante:

"Buscamos fisioterapeuta inmediatamente."


Puede priorizarse.


Pero:

La urgencia NO debe superar automáticamente
los criterios de compatibilidad.


============================================================
21. RECOMENDACIÓN POR DISPONIBILIDAD
============================================================

Considerar:

- cupos;
- horarios;
- fechas;
- temporada;
- disponibilidad profesional.


Una oportunidad sin capacidad disponible
no debe aparecer como opción principal.


============================================================
22. RECOMENDACIÓN POR ESTADO
============================================================

Estados posibles:


ACTIVA
→ puede recomendarse.


PRÓXIMA
→ puede recomendarse como oportunidad futura.


AGOTADA
→ no recomendar como oportunidad activa.


CERRADA
→ no recomendar.


PAUSADA
→ no recomendar temporalmente.


============================================================
23. RECOMENDACIÓN POR VERIFICACIÓN
============================================================

La plataforma debe distinguir:

VERIFICADO
NO VERIFICADO
EN REVISIÓN


La verificación puede afectar:

- confianza;
- posición;
- presentación.


IMPORTANTE:

Verificación NO equivale automáticamente
a mejor compatibilidad.


============================================================
24. RECOMENDACIÓN POR CALIDAD DE INFORMACIÓN
============================================================

Una oportunidad con información completa
puede ser más útil que una con información incompleta.


Ejemplo:

Club A:

- precio;
- horarios;
- categorías;
- ubicación;
- contacto;
- competición.


Club B:

- solo nombre.


Aunque ambos sean compatibles:


Club A
→ más útil para decisión.


============================================================
25. EXPLICACIÓN DE LA RECOMENDACIÓN
============================================================

Siempre que sea posible:


"Te recomendamos esta opción porque..."


Ejemplo:


"Está a 7 km de tu ubicación,
acepta jugadores de tu categoría,
entrena martes y jueves
y está dentro de tu presupuesto."


La explicación debe ser breve.


============================================================
26. RECOMENDACIONES NO INTRUSIVAS
============================================================

La plataforma NO debe bombardear al usuario.


Priorizar:

- pocas recomendaciones relevantes;
- grupos claros;
- posibilidad de explorar más.


No:

"50 cosas que puedes hacer."


============================================================
27. CANTIDAD DE RESULTADOS
============================================================

En la pantalla principal:

MOSTRAR UNA SELECCIÓN.


Después:

"Ver más"


El catálogo completo queda disponible
mediante búsqueda / exploración.


============================================================
28. RECOMENDACIONES + BUSCADOR
============================================================

RECOMENDACIONES:

"Creemos que esto te interesa."


BUSCADOR:

"Quiero encontrar algo específico."


FILTROS:

"Quiero restringir los resultados."


Los tres sistemas deben coexistir.


============================================================
29. RECOMENDACIONES + FILTROS
============================================================

Ejemplo:


RECOMENDACIONES:

Academia A
Academia B
Academia C


Usuario aplica:

Distancia < 10 km
Precio < $150


↓

Nuevo conjunto de resultados.


Los filtros no destruyen el perfil
ni cambian permanentemente el contexto.


============================================================
30. RECOMENDACIONES POR NECESIDAD
============================================================

Cada necesidad puede tener su propio bloque.


Ejemplo:


MI DESARROLLO

- Entrenador
- Preparador físico
- Fisioterapeuta


MI CARRERA

- Clubes
- Tryouts
- Scouting


MI ENTORNO

- Competiciones
- Academias
- Eventos


============================================================
31. RECOMENDACIONES PARA FAMILIAS
============================================================

Para perfiles gestionados por familias:


Puede priorizar:

- academias;
- clubes;
- entrenamientos;
- proximidad;
- horarios;
- precios;
- información relevante;
- oportunidades apropiadas para la edad.


IMPORTANTE:

Las recomendaciones para menores
deben respetar controles de privacidad,
seguridad y representación.


============================================================
32. RECOMENDACIONES PARA CLUBES
============================================================

CLUB


Puede recibir:


JUGADORES

"Perfiles compatibles."


STAFF

"Profesionales disponibles."


NECESIDADES

"Personas que pueden resolverlas."


OPORTUNIDADES

"Eventos / scouting / competición."


SERVICIOS

"Proveedores relevantes."


============================================================
33. RECOMENDACIONES PARA PROFESIONALES
============================================================

Ejemplo:

FISIOTERAPEUTA


Puede recibir:


"Clubes que podrían necesitar tu perfil."


"Academias cercanas."


"Vacantes compatibles."


"Deportistas que buscan tu servicio."


============================================================
34. RECOMENDACIONES PARA ENTRENADORES
============================================================

Puede recibir:


- clubes;
- academias;
- jugadores;
- equipos;
- oportunidades laborales;
- servicios.


Según:

- especialidad;
- nivel;
- deporte;
- ubicación;
- disponibilidad.


============================================================
35. RECOMENDACIONES PARA SCOUTS
============================================================

Puede recibir:


- jugadores compatibles;
- eventos;
- showcases;
- clubes;
- competiciones.


Según:

- deporte;
- edad;
- categoría;
- posición;
- región;
- nivel.


============================================================
36. RECOMENDACIONES PARA STAFF
============================================================

Puede incluir:


- vacantes;
- clubes;
- academias;
- equipos;
- servicios.


Según:

- rol;
- especialidad;
- experiencia;
- certificación;
- ubicación;
- disponibilidad.


============================================================
37. RECOMENDACIONES BIDIRECCIONALES
============================================================

Cuando ambas partes buscan:


CLUB
↓
busca jugador


JUGADOR
↓
busca club


La plataforma puede identificar:


"Existe una coincidencia entre tu perfil
y esta necesidad."


Esto debe estar sujeto a:

- permisos;
- privacidad;
- verificación;
- reglas de contacto.


============================================================
38. RECOMENDACIONES DE OPORTUNIDADES NUEVAS
============================================================

Cuando aparece una nueva oportunidad compatible:


Puede generarse una alerta.


Ejemplo:


"Nuevo tryout compatible con tu perfil."


"No debes buscar nuevamente."


La plataforma detecta la oportunidad.


============================================================
39. RECOMENDACIONES POR CAMBIO DE CONTEXTO
============================================================

Si cambia:


edad
club
categoría
ubicación
nivel
objetivo
disponibilidad


↓

actualizar recomendaciones.


============================================================
40. RECOMENDACIONES POR ACTIVIDAD
============================================================

Las acciones pueden convertirse
en señales futuras.


Ejemplos:


Guarda una academia
→ posible interés.


Contacta un club
→ intención alta.


Ignora repetidamente cierto tipo
→ posible menor relevancia.


IMPORTANTE:

No definir todavía algoritmos de aprendizaje.


============================================================
41. RECOMENDACIONES COMPLEMENTARIAS
============================================================

La plataforma puede detectar
necesidades relacionadas.


Ejemplo:


Jugador busca club.


Sistema puede sugerir:


"También puedes mejorar tu preparación física."


"Hay fisioterapeutas deportivos cerca."


"Hay tryouts próximos."


Pero deben ser:

SECUNDARIAS.


No competir con la necesidad principal.


============================================================
42. RECOMENDACIONES DE TRAYECTORIA
============================================================

La plataforma puede ayudar
a visualizar caminos.


Ejemplo:


NIÑO PRINCIPIANTE


Academia
↓
Entrenamiento
↓
Competición
↓
Club
↓
Tryout


Esto NO significa que la plataforma
decida la carrera del usuario.


Solo muestra posibilidades.


============================================================
43. RECOMENDACIÓN DE SIGUIENTE PASO
============================================================

La plataforma puede sugerir:


"Tu siguiente paso podría ser..."


Ejemplo:


Perfil:
11 años
principiante.


Siguiente paso:


"Explora academias de iniciación
a menos de 10 km."


Esto reduce fricción.


============================================================
44. RECOMENDACIONES SEGÚN MADUREZ DEL PERFIL
============================================================

PERFIL NUEVO:


Recomendaciones basadas
en información inicial.


PERFIL COMPLETO:


Mayor precisión.


PERFIL ACTIVO:


Mayor personalización.


No exigir perfil perfecto
para comenzar.


============================================================
45. INFORMACIÓN QUE FALTA
============================================================

La plataforma puede detectar:


"Para mejorar tus recomendaciones
necesitamos saber..."


Ejemplo:


Falta:

horario disponible.


Solicitarlo solamente
cuando sea relevante.


============================================================
46. RECOMENDACIÓN PROGRESIVA
============================================================

PRIMERA EXPERIENCIA:


Pocas preguntas.


↓


Primeras recomendaciones.


↓


Usuario interactúa.


↓


La plataforma aprende más contexto.


↓


Recomendaciones mejores.


============================================================
47. RECOMENDACIÓN + EXPLORACIÓN
============================================================

La plataforma debe ofrecer:


PARA TI


pero también:


EXPLORAR


para evitar crear una experiencia cerrada.


============================================================
48. ESTRUCTURA DE LA PANTALLA PRINCIPAL
============================================================

Conceptualmente:


PERFIL


"Hola, [usuario]"


↓


CONTEXTO


"Esto es lo que entendemos de ti."


↓


RECOMENDACIÓN PRINCIPAL


"Puede interesarte..."


↓


OPORTUNIDADES


3–5 resultados relevantes.


↓


RECOMENDACIONES SECUNDARIAS


Otros grupos relevantes.


↓


EXPLORAR MÁS


Acceso al universo de la plataforma.


============================================================
49. LA PLATAFORMA NO DEBE SER UN CATÁLOGO
============================================================

PRINCIPIO:


CATÁLOGO
=
toda la información.


PLATAFORMA
=
información + contexto + relación + recomendación.


La información completa existe.


La interfaz muestra
solamente lo relevante en cada momento.


============================================================
50. INFORMACIÓN DETALLADA DE CADA ENTIDAD
============================================================

Toda oportunidad recomendada
debe poder abrirse.


Ejemplo:


CLUB


Debe poder contener:


- identidad;
- historia;
- ubicación;
- deportes;
- categorías;
- equipos;
- competiciones;
- instalaciones;
- horarios;
- precios;
- entrenadores;
- staff;
- tryouts;
- requisitos;
- oportunidades;
- contacto;
- verificación;
- estado.


La recomendación es solo
la puerta de entrada.


============================================================
51. PERFIL DETALLADO DEL JUGADOR
============================================================

Debe poder contener:


- información personal;
- deporte;
- categoría;
- edad;
- posición;
- nivel;
- experiencia;
- club actual;
- equipo;
- competición;
- historial de clubes;
- estadísticas cuando aplique;
- objetivos;
- disponibilidad;
- ubicación;
- servicios buscados;
- oportunidades;
- permisos;
- visibilidad.


============================================================
52. PERFIL DETALLADO DEL PROFESIONAL
============================================================

Debe poder contener:


- identidad;
- rol;
- especialidad;
- deportes;
- certificaciones;
- experiencia;
- trayectoria;
- organizaciones;
- ubicación;
- disponibilidad;
- servicios;
- tarifas;
- modalidad;
- referencias;
- verificación;
- oportunidades buscadas.


============================================================
53. RELACIONES ENTRE ENTIDADES
============================================================

La plataforma no debe almacenar solamente
entidades independientes.


Debe entender relaciones:


JUGADOR
↓ pertenece a
CLUB
↓ participa en
COMPETICIÓN


JUGADOR
↓ busca
CLUB


CLUB
↓ busca
JUGADOR


JUGADOR
↓ busca
FISIOTERAPEUTA


FISIOTERAPEUTA
↓ ofrece
SERVICIO


CLUB
↓ necesita
STAFF


Esto será fundamental para
la arquitectura de datos posterior.


============================================================
54. ESTADO DE LAS RECOMENDACIONES
============================================================

Una recomendación puede estar:


NUEVA


VISTA


GUARDADA


DESCARTADA


CONTACTADA


APLICADA


COMPLETADA


EXPIRADA


Esto permitirá posteriormente
medir comportamiento.


============================================================
55. RECOMENDACIÓN + ACCIÓN
============================================================

Toda recomendación debe poder llevar
a una acción.


Ejemplos:


Academia
→ Ver perfil


Tryout
→ Ver detalles


Club
→ Contactar


Vacante
→ Aplicar


Fisioterapeuta
→ Solicitar servicio


Jugador
→ Ver perfil


Evento
→ Registrarse


============================================================
56. NO TODAS LAS ACCIONES SON IGUALES
============================================================

La acción depende del tipo de oportunidad.


Por eso cada entidad debe definir
sus acciones disponibles.


============================================================
57. PRIORIZACIÓN GENERAL
============================================================

La prioridad conceptual puede depender de:


1. Compatibilidad.
2. Necesidad.
3. Relevancia contextual.
4. Disponibilidad.
5. Proximidad.
6. Preferencias.
7. Temporalidad.
8. Calidad de información.
9. Verificación.
10. Actividad / señales.


Los pesos exactos se definirán
posteriormente.


============================================================
58. REGLA DE NO SOBRECARGA
============================================================

La plataforma puede tener
muchísimas capacidades.


Pero el usuario debe ver
solamente las relevantes.


PRINCIPIO:


MUCHA CAPACIDAD
+
POCA FRICCIÓN.


============================================================
59. REGLA DE DESCUBRIMIENTO
============================================================

El usuario no tiene que conocer
todas las capacidades de la plataforma.


La plataforma debe ayudarlo
a descubrirlas cuando sean relevantes.


============================================================
60. REGLA DE ADAPTACIÓN
============================================================

La interfaz conceptual debe adaptarse
al actor y al contexto.


No diseñar:

"una pantalla universal."


Diseñar:

"Sistema universal
con experiencias contextuales."


============================================================
61. REGLA DE INFORMACIÓN
============================================================

La plataforma debe almacenar
información detallada.


Pero:


INFORMACIÓN DISPONIBLE
≠
INFORMACIÓN MOSTRADA.


La interfaz decide
qué es relevante.


============================================================
62. REGLA DE TRANSPARENCIA
============================================================

Cuando una recomendación sea importante,
el usuario debe poder entender:

"¿Por qué me estás mostrando esto?"


============================================================
63. REGLA DE CONTROL DEL USUARIO
============================================================

El usuario debe poder:


- ignorar;
- guardar;
- explorar;
- filtrar;
- modificar preferencias;
- actualizar contexto.


La recomendación no debe ser una imposición.


============================================================
64. REGLA DE ACTUALIZACIÓN
============================================================

Las recomendaciones deben actualizarse
cuando cambien:


- oportunidades;
- perfil;
- contexto;
- necesidades;
- disponibilidad;
- ubicación;
- temporada.


============================================================
65. EJEMPLO FINAL
============================================================

PERFIL:


Jugador
16 años
Sub-17
Lateral derecho
Nivel competitivo
Club actual: Club A
Miami


OBJETIVO:


Buscar oportunidades competitivas.


PLATAFORMA:


MATCHING


↓


RESULTADOS:


Tryout B
MATCH MUY ALTO


Club C
MATCH ALTO


Showcase D
MATCH ALTO


Club E
MATCH MEDIO


↓


RECOMENDACIÓN:


"Encontramos 3 oportunidades
que encajan especialmente bien
con tu perfil."


↓


GRUPOS SECUNDARIOS:


Preparación física


Fisioterapia


Entrenamiento individual


↓


EXPLORAR:


Todos los clubes


Todos los tryouts


Todos los servicios


============================================================
66. EJEMPLO — PRINCIPIANTE
============================================================

PERFIL:


11 años
Fútbol
Sin experiencia
Miami


OBJETIVO:


Comenzar.


RECOMENDACIÓN PRINCIPAL:


"Opciones para comenzar a entrenar."


RESULTADOS:


Academia A
Academia B
Entrenador C


RECOMENDACIONES SECUNDARIAS:


Campamentos
Entrenamiento individual


NO PRIORIZAR:


Scouting profesional
Tryouts profesionales.


============================================================
67. EJEMPLO — CLUB
============================================================

CLUB:


Necesidad:


"Buscamos fisioterapeuta."


PLATAFORMA:


MATCHING


↓


Fisio A
Fisio B
Fisio C


RECOMENDACIÓN:


"3 profesionales compatibles."


Criterios:


- certificación;
- experiencia;
- deporte;
- disponibilidad;
- ubicación.


============================================================
68. EJEMPLO — DEPORTISTA
============================================================

DEPORTISTA:


Necesidad:


"Busco fisioterapeuta."


PLATAFORMA:


MATCHING


↓


Fisio A
Fisio B
Fisio C


Prioridad:


- especialidad;
- distancia;
- disponibilidad;
- precio;
- experiencia.


============================================================
69. OBJETIVO DE ESTA MATRIZ
============================================================

La plataforma debe pasar de:


"Tenemos miles de datos."


a:


"Sabemos qué información
es relevante para este usuario
en este momento."


============================================================
70. QUÉ NO DEFINIMOS TODAVÍA
============================================================

NO DEFINIR TODAVÍA:


- algoritmo;
- machine learning;
- fórmula matemática;
- pesos definitivos;
- IA predictiva;
- arquitectura técnica;
- base de datos;
- diseño final de interfaz.


Eso viene después.


============================================================
71. SIGUIENTE ETAPA
============================================================

ETAPA 07:


MATRIZ DE ACTORES Y ROLES.


OBJETIVO:


Definir exhaustivamente:

- quién puede utilizar la plataforma;
- quién representa a quién;
- qué tipos de perfiles existen;
- qué relaciones existen;
- qué puede hacer cada actor;
- qué información necesita cada actor;
- qué información puede ofrecer;
- qué necesidades puede tener;
- qué oportunidades puede publicar;
- qué oportunidades puede buscar.


Después:


ETAPA 08


MATRIZ DE INFORMACIÓN / DATOS.


Ahí construiremos las fichas completas de:


- jugador;
- familia;
- club;
- academia;
- equipo;
- entrenador;
- scout;
- fisioterapeuta;
- preparador físico;
- staff;
- asistencia;
- otros profesionales;
- organizaciones;
- oportunidades;
- servicios;
- competiciones;
- tryouts;
- eventos.


============================================================
FIN
============================================================
