============================================================
STARTUP DEPORTIVA
FASE 08
MATRIZ DE ACTORES Y ROLES
VERSIÓN 0.1
============================================================

OBJETIVO
============================================================

Construir una MATRIZ DE ACTORES Y ROLES completa para la
plataforma deportiva.

La matriz debe identificar quién participa en el ecosistema,
qué función cumple, qué busca, qué ofrece, qué información
maneja, qué necesita y qué puede hacer dentro de la plataforma.

IMPORTANTE:

NO diseñar todavía la interfaz definitiva.

NO programar todavía funcionalidades definitivas.

NO asumir que los actores conocidos representan todo
el ecosistema.

Esta fase busca construir el MODELO DE ACTORES que posteriormente
alimentará:

- contexto;
- necesidades;
- oportunidades;
- matching;
- recomendaciones;
- permisos;
- visibilidad;
- agentes;
- navegación;
- arquitectura de datos.


============================================================
1. PRINCIPIO FUNDAMENTAL
============================================================

LA PLATAFORMA NO DEBE ORGANIZARSE ÚNICAMENTE
POR "TIPOS DE USUARIO".

Debe comprender:

ACTOR
+
CONTEXTO
+
ROL
+
OBJETIVO
+
NECESIDAD
+
RELACIONES
+
PERMISOS
+
OPORTUNIDADES


Un mismo individuo puede tener diferentes roles.

Ejemplo:

Una persona puede ser:

- entrenador;
- preparador físico;
- padre de un jugador;
- propietario de una academia.


Por lo tanto:

PERSONA ≠ NECESARIAMENTE UN ÚNICO ROL.


============================================================
2. DISTINCIÓN FUNDAMENTAL
============================================================

Separar conceptualmente:

PERSONA
ORGANIZACIÓN
EQUIPO
PERFIL
ROL
RELACIÓN
NECESIDAD
OPORTUNIDAD


Ejemplo:

PERSONA:
Juan Pérez


PERFIL:
Entrenador


ORGANIZACIÓN:
Club X


ROL:
Entrenador U17


RELACIÓN:
Pertenece a Club X


NECESIDAD:
Encontrar preparador físico


OPORTUNIDAD:
Vacante de preparador físico


No convertir todos estos conceptos
en una sola entidad.


============================================================
3. ACTORES INICIALES A INVESTIGAR
============================================================

Utilizar como punto de partida:

- jugador;
- padre/madre;
- representante familiar;
- representante/agente deportivo;
- club;
- academia;
- equipo;
- scout;
- entrenador;
- asistente técnico;
- preparador físico;
- fisioterapeuta;
- médico deportivo;
- psicólogo deportivo;
- nutricionista deportivo;
- utillero;
- asistente;
- coordinador deportivo;
- director deportivo;
- organizador de competición;
- árbitro;
- personal administrativo;
- fotógrafo/videógrafo deportivo;
- analista de rendimiento;
- especialista de rehabilitación;
- especialista en preparación;
- proveedor de servicios deportivos.


IMPORTANTE:

ESTA LISTA NO ES DEFINITIVA.


Debe ampliarse, reducirse o dividirse según:

- investigación;
- realidad del ecosistema;
- necesidades detectadas;
- relaciones existentes;
- oportunidades reales.


============================================================
4. ACTORES ORGANIZACIONALES
============================================================

No limitar el sistema a personas.

Identificar también:

- clubes;
- academias;
- escuelas deportivas;
- equipos;
- ligas;
- competiciones;
- asociaciones;
- federaciones;
- centros deportivos;
- instalaciones;
- clínicas;
- centros de rehabilitación;
- empresas;
- organizaciones;
- instituciones educativas;
- organizadores de eventos.


Determinar qué entidades pueden tener
perfil propio dentro de la plataforma.


============================================================
5. MATRIZ PRINCIPAL
============================================================

Crear una matriz con al menos:

ACTOR
TIPO
DESCRIPCIÓN
OBJETIVO PRINCIPAL
NECESIDADES
QUÉ OFRECE
QUÉ BUSCA
INFORMACIÓN QUE PROPORCIONA
INFORMACIÓN QUE NECESITA
RELACIONES
OPORTUNIDADES QUE PUEDE CREAR
OPORTUNIDADES QUE PUEDE RECIBIR
ACCIONES
PERMISOS
VISIBILIDAD
AGENTES RELEVANTES


============================================================
6. JUGADOR
============================================================

Analizar diferentes escenarios:

- jugador menor;
- jugador mayor de edad;
- jugador sin club;
- jugador perteneciente a club;
- jugador en academia;
- jugador buscando club;
- jugador buscando entrenamiento;
- jugador buscando servicios;
- jugador buscando tryout;
- jugador buscando oportunidad deportiva.


NO asumir que todos los jugadores
tienen las mismas necesidades.


============================================================
7. MENORES
============================================================

Separar:

JUGADOR MENOR


de:


ADULTO RESPONSABLE


La plataforma debe contemplar
que ciertas acciones pueden requerir
la intervención del padre/madre/tutor.


Investigar y diseñar conceptualmente:

- representación;
- consentimiento;
- privacidad;
- visibilidad;
- contacto;
- publicación de información.


No implementar todavía.


============================================================
8. CLUB
============================================================

El club debe poder tener información detallada.

Investigar qué información resulta relevante.

Como mínimo evaluar:

- nombre;
- ubicación;
- sedes;
- categorías;
- equipos;
- competiciones;
- divisiones;
- temporadas;
- entrenamientos;
- horarios;
- instalaciones;
- precios cuando corresponda;
- tryouts;
- necesidades;
- staff;
- jugadores;
- contactos;
- canales oficiales.


NO asumir que todos los clubes tienen
la misma estructura.


============================================================
9. CLUB + NECESIDADES
============================================================

Un club puede buscar:

- jugadores;
- entrenadores;
- asistentes;
- preparadores físicos;
- fisioterapeutas;
- médicos;
- analistas;
- utilleros;
- personal administrativo;
- otros perfiles.


La plataforma debe representar:

CLUB
↓
NECESIDAD
↓
REQUISITOS
↓
OPORTUNIDAD
↓
MATCHING


============================================================
10. ACADEMIA
============================================================

Analizar:

- edades;
- categorías;
- programas;
- ubicación;
- sedes;
- horarios;
- precios;
- entrenadores;
- instalaciones;
- metodología;
- competición;
- pruebas;
- disponibilidad.


Una academia puede ser:

- lugar de iniciación;
- formación;
- preparación;
- competición;
- transición hacia clubes.


============================================================
11. STAFF
============================================================

No crear necesariamente un único perfil llamado
"STAFF".

Determinar qué especialidades deben existir.

Ejemplos:

- entrenador;
- asistente;
- preparador físico;
- fisioterapeuta;
- médico;
- psicólogo;
- nutricionista;
- analista;
- utillero;
- coordinador.


Cada especialidad debe tener:

- capacidades;
- experiencia;
- certificaciones cuando correspondan;
- disponibilidad;
- ubicación;
- relaciones;
- historial.


============================================================
12. PROFESIONALES INDEPENDIENTES
============================================================

Analizar profesionales que:

- trabajan para clubes;
- trabajan para academias;
- trabajan independientemente;
- trabajan a domicilio;
- trabajan en instalaciones;
- trabajan para múltiples organizaciones.


NO asumir:

PROFESIONAL = UN SOLO CLUB.


============================================================
13. SCOUT
============================================================

Determinar qué necesita un scout:

- descubrir jugadores;
- filtrar jugadores;
- observar oportunidades;
- analizar perfiles;
- contactar;
- registrar seguimiento.


Determinar qué información puede consultar
y qué información debería estar restringida.


============================================================
14. REPRESENTANTE / AGENTE
============================================================

Analizar:

- jugadores representados;
- oportunidades;
- clubes;
- contactos;
- seguimiento;
- necesidades.


Distinguir:

AGENTE

de:

PADRE/MADRE/REPRESENTANTE FAMILIAR.


No asumir que cumplen la misma función.


============================================================
15. ORGANIZADORES
============================================================

Analizar actores que crean:

- competiciones;
- torneos;
- tryouts;
- eventos;
- campeonatos.


Deben poder crear:

OPORTUNIDADES


que después puedan ser encontradas
por los actores correspondientes.


============================================================
16. RELACIONES
============================================================

Para cada actor determinar
qué relaciones puede tener.


Ejemplo:

JUGADOR
↓
PERTENECE A
↓
CLUB


JUGADOR
↓
REPRESENTADO POR
↓
PERSONA


JUGADOR
↓
ENTRENADO POR
↓
ENTRENADOR


CLUB
↓
PARTICIPA EN
↓
COMPETICIÓN


CLUB
↓
BUSCA
↓
FISIOTERAPEUTA


ACADEMIA
↓
OFRECE
↓
ENTRENAMIENTO


La matriz debe identificar
todas las relaciones relevantes descubiertas.


============================================================
17. PERFIL + ROL
============================================================

Un usuario puede tener:

1 perfil principal

y múltiples:

ROLES


Ejemplo:


PERSONA
│
├── JUGADOR
│
├── ENTRENADOR
│
└── PADRE


El sistema debe estar preparado
para esta posibilidad.


============================================================
18. CLUB + PERSONAS
============================================================

Representar relaciones como:

CLUB
↓
STAFF


CLUB
↓
JUGADORES


CLUB
↓
ADMINISTRADORES


CLUB
↓
ENTRENADORES


CLUB
↓
PROFESIONALES EXTERNOS


No asumir que todos tienen
el mismo tipo de vínculo.


============================================================
19. CLUB ACTUAL DEL JUGADOR
============================================================

IMPORTANTE:

Cuando corresponda, el perfil del jugador
DEBE CONTENER SU CLUB ACTUAL.


Además investigar si debe existir:

- equipo actual;
- categoría;
- competición;
- división;
- temporada;
- estado de relación;
- fecha de inicio;
- historial de clubes.


Esto será relevante para:

- matching;
- scouting;
- recomendaciones;
- historial;
- contexto.


============================================================
20. HISTORIAL
============================================================

Investigar qué actores necesitan historial.

Ejemplos:

JUGADOR:

clubes;
equipos;
competiciones;
categorías.


ENTRENADOR:

clubes;
equipos;
categorías;
experiencia.


FISIOTERAPEUTA:

organizaciones;
especialidades;
experiencia.


CLUB:

competiciones;
temporadas;
categorías.


No asumir que todos tienen
el mismo historial.


============================================================
21. OPORTUNIDADES
============================================================

Determinar qué actores pueden:

CREAR
PUBLICAR
BUSCAR
RECIBIR
APLICAR
ACEPTAR
RECHAZAR
GESTIONAR

una oportunidad.


Ejemplos:

TRYOUT
VACANTE
ENTRENAMIENTO
ACADEMIA
SERVICIO PROFESIONAL
EVENTO
COMPETICIÓN
TRABAJO
COLABORACIÓN


============================================================
22. BÚSQUEDA
============================================================

La plataforma debe distinguir:

ACTOR QUE BUSCA

de:

ACTOR QUE OFRECE.


Ejemplo:

Jugador
→ busca club.


Club
→ busca jugador.


Jugador
→ busca fisioterapeuta.


Fisioterapeuta
→ busca clientes.


Club
→ busca fisioterapeuta.


Academia
→ busca jugadores.


Esta relación debe alimentar
el sistema de matching.


============================================================
23. NAVEGACIÓN CONTEXTUAL
============================================================

IMPORTANTE:

NO obligar al usuario a seleccionar
primero una categoría de búsqueda.


Después de construir el perfil,
la plataforma debe determinar
qué opciones son relevantes.


Ejemplo:


JUGADOR
11 años
sin club
sin experiencia competitiva
ubicación X


El sistema puede priorizar:


ACADEMIAS
ENTRENAMIENTOS
CLUBES DE INICIACIÓN


Mientras que:


CLUB PROFESIONAL
U17
necesidad de lateral


puede priorizar:


JUGADORES
TRYOUTS
STAFF
SCOUTING


============================================================
24. PERFIL DINÁMICO
============================================================

El perfil no debe ser estático.


Debe existir:


PERFIL
+
CONTEXTO ACTUAL
+
NECESIDADES ACTUALES
+
RELACIONES
+
HISTORIAL


El contexto puede cambiar.


Ejemplo:


Jugador:

sin club


posteriormente:


Jugador:

Club A
U17
Competición X


El sistema debe actualizar
las recomendaciones.


============================================================
25. ACTORES + UBICACIÓN
============================================================

Integrar la nueva fase de
INTELIGENCIA GEOGRÁFICA.


Cada actor debe determinar
si necesita:

- ubicación;
- radio;
- sedes;
- disponibilidad geográfica;
- movilidad;
- trabajo remoto;
- trabajo a domicilio.


No todos los actores requieren
el mismo nivel de precisión.


============================================================
26. ACTORES + PRIVACIDAD
============================================================

Determinar para cada actor:

- información pública;
- información privada;
- información restringida;
- información visible mediante relación;
- información visible mediante autorización.


Especial atención:

MENORES.


============================================================
27. ACTORES + AGENTES
============================================================

Determinar qué agentes pueden asistir
a cada actor.


Ejemplo:


JUGADOR

puede recibir asistencia de:

- Context Agent;
- Opportunity Agent;
- Matching Agent;
- Geo Agent;
- Recommendation Agent.


CLUB:

- Need Agent;
- Search Agent;
- Matching Agent;
- Scout Agent;
- Geo Agent.


No crear agentes innecesarios.


La matriz debe identificar
qué capacidad necesita cada actor.


============================================================
28. MATRIZ DE ACTORES
============================================================

Crear una tabla final como:


| Actor | Tipo | Objetivo | Necesidades | Ofrece |
|------|------|----------|-------------|--------|


Y una segunda:


| Actor | Busca | Puede crear | Puede recibir | Relaciones |
|------|------|-------------|---------------|------------|


Y una tercera:


| Actor | Datos públicos | Datos privados | Permisos | Agentes |
|------|----------------|----------------|----------|---------|


============================================================
29. MATRIZ DE PRIORIDAD
============================================================

Clasificar los actores según:

CORE
IMPORTANT
SECONDARY
FUTURE


No intentar construir todo
en la primera versión.


Determinar cuáles son indispensables
para que exista el MVP.


============================================================
30. RESULTADO ESPERADO
============================================================

Al terminar esta fase debemos poder responder:


¿QUIÉNES PARTICIPAN?


¿QUÉ PAPEL TIENE CADA UNO?


¿QUÉ BUSCA CADA UNO?


¿QUÉ OFRECE CADA UNO?


¿QUÉ RELACIONES EXISTEN?


¿QUÉ INFORMACIÓN NECESITA?


¿QUÉ INFORMACIÓN PUEDE VER?


¿QUÉ OPORTUNIDADES PUEDE CREAR?


¿QUÉ AGENTES PUEDEN AYUDARLO?


¿QUÉ PARTE DEL SISTEMA DEBE SER PRIORITARIA?


============================================================
31. REGLA DE NO SOBRECONSTRUCCIÓN
============================================================

NO convertir cada actor descubierto
en una funcionalidad independiente.


Primero determinar:

¿REALMENTE NECESITAMOS UN FLUJO DIFERENTE?


Puede existir:

UNA MISMA ARQUITECTURA

con:

DIFERENTES CONTEXTOS
+
DIFERENTES ROLES
+
DIFERENTES PERMISOS
+
DIFERENTES NECESIDADES.


============================================================
32. INVESTIGACIÓN DEL ECOSISTEMA
============================================================

Antes de cerrar esta matriz:

INVESTIGAR EXHAUSTIVAMENTE EL ECOSISTEMA
FUTBOLÍSTICO DE VENEZUELA.

No limitarse a:

- Asofútbol;
- Canguro;
- Diamante;
- Pipo;
- LIDES;
- Colegial.

Estas son únicamente referencias iniciales.


Investigar también:

- divisiones;
- categorías;
- ediciones;
- temporadas;
- competiciones;
- ligas;
- torneos;
- fútbol base;
- fútbol femenino;
- futsal;
- fútbol playa;
- competiciones escolares;
- universitarias;
- regionales;
- estatales;
- municipales cuando correspondan;
- clubes;
- academias;
- asociaciones;
- federaciones;
- organizaciones;
- estructuras de competición;
- tryouts;
- scouting;
- eventos.


NO asumir que la lista proporcionada
es completa.


============================================================
33. INVESTIGACIÓN Y VERIFICACIÓN
============================================================

Utilizar múltiples fuentes.

Priorizar:

1. fuentes oficiales;
2. federaciones;
3. organizaciones deportivas;
4. competiciones;
5. clubes;
6. academias;
7. instituciones;
8. medios especializados;
9. redes oficiales;
10. otras fuentes relevantes.


Registrar cuando sea posible:

- fuente;
- fecha;
- estado;
- nivel de confianza.


Distinguir:

CONFIRMADO
PROBABLE
NO CONFIRMADO
INFORMACIÓN INCOMPLETA


NO INVENTAR DATOS.


============================================================
34. IMPACTO DE LA INVESTIGACIÓN
============================================================

Si la investigación demuestra
que nuestra matriz de actores
es incompleta:

MODIFICARLA.


Si demuestra que algunos actores
deben dividirse:

DIVIDIRLOS.


Si demuestra que algunos actores
no son relevantes:

REDUCIRLOS.


La realidad del ecosistema
tiene prioridad sobre nuestras
suposiciones iniciales.


============================================================
35. DOCUMENTACIÓN
============================================================

Guardar los resultados de esta fase
de manera estructurada dentro del proyecto.

Crear o actualizar la documentación
correspondiente sin destruir
trabajo previo.


Antes de modificar archivos existentes:

- revisar estructura;
- entender dependencias;
- conservar información válida;
- evitar duplicados.


============================================================
36. REGLA DE IMPLEMENTACIÓN
============================================================

NO comenzar todavía
la implementación completa de estos actores.


Esta fase es de:

INVESTIGACIÓN
+
MODELADO
+
ARQUITECTURA CONCEPTUAL.


La implementación vendrá
después de cerrar las matrices
y validar el modelo.


============================================================
37. SALIDA FINAL
============================================================

Entregar:

1. Matriz completa de actores.
2. Actores core.
3. Actores importantes.
4. Actores secundarios.
5. Actores futuros.
6. Relaciones principales.
7. Roles múltiples.
8. Necesidades principales.
9. Información necesaria.
10. Permisos preliminares.
11. Agentes relevantes.
12. Impacto de la investigación
    del fútbol venezolano.
13. Dudas y supuestos pendientes.
14. Recomendaciones para la siguiente fase.


============================================================
38. INVESTIGACIÓN DEPORTIVA OBLIGATORIA
============================================================

ANTES DE TOMAR DECISIONES DEFINITIVAS SOBRE LA ARQUITECTURA
DEL PRODUCTO, LOS DATOS, LOS ACTORES, EL MATCHING,
LAS RECOMENDACIONES O LOS FLUJOS DE LA PLATAFORMA:

CLAUDE CODE DEBE REALIZAR UNA INVESTIGACIÓN EXHAUSTIVA,
DETALLADA Y ESTRUCTURADA DEL ECOSISTEMA FUTBOLÍSTICO
DE VENEZUELA.

NO LIMITARSE A LAS COMPETICIONES, LIGAS, TORNEOS,
ORGANIZACIONES O CATEGORÍAS QUE YA HAYAN SIDO MENCIONADAS
EN ESTE CONTEXTO.

LAS REFERENCIAS EXISTENTES SON SOLAMENTE PISTAS INICIALES.

INVESTIGAR TODAS LAS COMPETICIONES, DIVISIONES,
CATEGORÍAS, EDICIONES, TEMPORADAS Y ESTRUCTURAS
QUE PUEDAN SER RELEVANTES PARA EL PRODUCTO.

SI LA INFORMACIÓN NO PUEDE VERIFICARSE:

NO INVENTAR.

REGISTRARLA COMO:

"INFORMACIÓN PENDIENTE DE VERIFICACIÓN".


============================================================
FIN DE FASE 08
============================================================
