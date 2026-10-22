# Reglas para Claude en este repo

Estas reglas reemplazan, en cualquier sesión, lo que harían los plugins `rulebook-guard` y `blast-radius` cuando no están cargados.

## Escritura

- No uses rayas largas (—) en textos. Usa coma, punto, dos puntos o paréntesis.
- Escribe en español, directo: la conclusión o la acción primero, pasos numerados cuando haya varios.
- Evita frases típicas de IA ("No es X, es Y", "Lo que nadie te cuenta", "Espero que te sirva"). Para editar o auditar textos usa la skill `no-ai-slop`.
- No inventes datos, cifras ni citas. Si falta información, pregunta.

## Git

- No uses `git commit --amend` ni reescribas historia sin preguntar antes.
- No hagas force push. Si hace falta, pregunta primero y explica por qué.
- Antes de un push, revisa que los archivos tengan el formato del resto del repo.
- No metas datos personales (teléfonos, correos, documentos de identidad, direcciones) en notas, archivos ni mensajes de commit. Si un texto los trae, avisa y pide confirmación.

## Acciones destructivas

- Antes de `rm -r`, borrar carpetas, migraciones o cualquier cosa difícil de revertir, muestra qué se va a eliminar y espera confirmación.
- Si no recibes respuesta, no ejecutes la acción.

## Skills disponibles (`.claude/skills/`)

- `i-have-adhd`: respuestas con la acción primero y pasos numerados.
- `no-ai-slop`: edita o audita textos sin perder la voz del autor.
- `book-to-skill`: convierte un libro o documento en un skill consultable (necesita Python).

Origen de cada skill y plugin: `.claude/skills/THIRD_PARTY.md`.
