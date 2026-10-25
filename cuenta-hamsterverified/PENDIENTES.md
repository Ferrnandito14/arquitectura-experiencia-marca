# Pendientes para la persona dueña

Aquí se anota lo que Claude no debe decidir solo (comentarios graves, mensajes directos, restricciones de la cuenta, dudas).

- 2026-10-24: la foto de perfil de hamster.2511058 es una persona, no el hámster. Cambiarla al hámster con sello azul y actualizar la bio (hoy solo dice "esencia"). Lo decide Fernando.
- 2026-10-24: Fernando pidió habilitar el navegador para publicar o interactuar y no llegó a indicar qué acciones. Mientras tanto siguen vigentes los límites de RELEVO.md.
- 2026-10-24: Chrome se usó antes por error con la cuenta personal de Fernando. Regla acordada: en el navegador usar siempre hamster.2511058 y no abrir nada de la cuenta personal.
- 2026-10-25 URGENTE (afecta a la automatización): las dos tareas programadas de la nube corren sin el repo como fuente, y el proxy de git rechaza (403) cada push. Efecto: el publicador publica pero no guarda el estado en `cola.json`, y la producción diaria pierde lo que crea (las piezas del 26/10 hechas a las 06:07 se perdieron). Arreglo definitivo, solo desde la web de claude.ai: abrir las rutinas "Producción diaria hamsterverified" y "Publicador y comentarios hamsterverified" y añadir el repo `arquitectura-experiencia-marca` como fuente con permiso de escritura. Mientras tanto: el publicador ya no duplica (comprueba en Instagram antes de publicar) y las piezas se preparan desde sesiones interactivas.
