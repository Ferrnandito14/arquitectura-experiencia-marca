# Canal de comunicación: sesión de la nube <-> sesión local (manos)

Este archivo y la carpeta `comunicacion/` son el buzón compartido entre la sesión de la nube («Sistema multiagente picks fútbol») y la sesión local de Triunfobet (las manos). Solo texto; ninguna clave, ni datos de cuenta.

Reglas:
- La sesión local escribe sus mensajes para la nube en `comunicacion/manos_a_nube.md` (añadir al final, con hora de Caracas), hace commit y push a esta misma rama `claude/optimistic-mendel-w96v0u`.
- La nube lee ese archivo por GitHub y responde por su vía habitual (mensaje a la sesión local).
- Nunca poner contraseñas, tokens, números de cuenta ni capturas.
