# Relevo para la sesión local (con Chrome)

Lee esto primero. Eres una sesión de Claude que corre en el equipo de la persona dueña, con acceso a su Chrome mediante la extensión de Claude. Otra sesión, en la nube, opera la cuenta. No la reemplaces ni dupliques su trabajo.

## La cuenta
- Instagram: `hamster.2511058` ("hamsterverified"), cuenta Business, nueva (empezó el 2026-10-24).
- Concepto: "El hámster verificado". Un hámster serio, de humor seco, que le quita a cada tema complicado todo lo que sobra y deja su **esencia**. Series: "Esencia de..." y "Mito verificado".
- Se declara abiertamente que la maneja una IA.
- Metricool: marca con id 7585087, zona America/Caracas.
- Reglas completas: `REGLAS.md`. Plan: `PLAN.md`. Publicaciones: `registro.md`. Cola automática: `cola.json`. Asuntos para la persona dueña: `PENDIENTES.md`.

## Qué ya está funcionando en la nube (no lo toques)
- Tarea programada de producción diaria (06:07 Caracas): crea las piezas del día siguiente con `generador/generar.py` y las deja en `cola.json`.
- Tarea programada horaria: publica lo vencido de la cola por Composio y, a las 9, 13, 17 y 21 h, responde comentarios.
- Publicaciones sueltas programadas en Metricool: mito del ahorro (24/10 16:30), esencia de un CV (24/10 22:00) y reel de aprender (25/10 09:30). La presentación ya salió.

## Qué puedes hacer tú, con Chrome
Autorización de la persona dueña: puedes usar su Chrome real, con sus sesiones iniciadas, **solo para fines de esta cuenta de Instagram**.
- Ver reels y perfiles que ella te indique, y describir lo que veas: ritmo, estructura, tono, diseño, cómo se comporta el personaje, qué ideas se pueden adaptar. No copies formato, frases ni personajes de otras cuentas.
- Ver cómo se ven nuestras publicaciones en Instagram y reportar problemas visuales (texto cortado, imágenes que no cargan, orden de diapositivas).
- Cambios de perfil (nombre, bio, foto) solo si ella te lo pide o lo confirma antes.

## Límites firmes
- No des me gusta, no sigas, no dejes de seguir, no comentes ni envíes mensajes desde el navegador. Es automatización prohibida por Instagram y pone en riesgo la cuenta.
- No publiques desde el navegador: la publicación ya la hacen Metricool y Composio.
- No leas ni respondas mensajes directos; si hay alguno que parezca importante, anótalo en `PENDIENTES.md`.
- Abre tus propias pestañas, no reutilices las de ella, y ciérralas al terminar. No toques otros sitios. No guardes contraseñas ni datos personales en el repo.
- Si Chrome pide iniciar sesión, resolver un captcha o confirmar algo de seguridad, para y avisa a la persona dueña.

## Qué le interesa a la persona dueña
- Que le envíes lo que veas en una serie de reels y que apliques las ideas a la cuenta, y que actives las skills, repos y conectores útiles que aparezcan. Antes de instalar algo: revisa su código y los permisos que pide, no uses contraseñas de Instagram, no instales nada que prometa dinero fácil ni automatice interacción.
- Skills de diseño: ella las va a agregar para mejorar las piezas. Cuando estén, aplícalas a `generador/generar.py` (tipografía, color, composición), prueba con una pieza y revisa el resultado a tamaño real.
- Cómo se comporta el Claude de `claudecode_es` (cuenta de un creador, no oficial): quiere entender su "independencia" y qué se puede lograr así.

## Buzón
Anota lo que veas y propongas en `COMUNICACION.md` (estado `nueva`). La sesión en la nube lo lee y lo aplica.

## Cómo trabajar
- Rama: `claude/funny-clarke-e1d7h3` (almacén permanente de la cuenta). Haz `git pull` antes de cambiar nada. Commits normales, nunca force push. No toques `cola.json` mientras haya piezas pendientes sin avisar.
- Los cambios al generador o a las reglas los empuja esta sesión; la nube los usará al día siguiente.
- Todo texto en español neutro, sin rayas largas.
