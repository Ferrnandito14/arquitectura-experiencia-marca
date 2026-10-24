# Repertorio de técnicas para reels y carruseles

Sacado de siete reels de referencia (cuentas de IA y diseño web en español, octubre 2026). Son principios generales, no formatos ni frases de nadie. Lo que vi: pie, comentarios, perfil y un fotograma de cada reel. No analicé ritmo ni cortes cuadro por cuadro.

## Qué se adopta (con la voz del hámster)

1. **Gancho en el primer segundo.** Una pregunta o una promesa concreta, escrita en pantalla. Ejemplo: "¿Qué es la inflación? Esencia en 15 segundos."
2. **Texto grande que se entienda sin sonido.** Casi todos los reels de referencia llevan el mensaje principal en texto. Para nosotros: una frase por pantalla, mínimo 60 px a 1080 de ancho.
3. **Resultado a la vista desde el inicio.** Mostrar el tema ya resumido (la "esencia") al comienzo y explicarlo después. Hoy los carruseles empiezan con el título; los reels pueden empezar con el sello.
4. **Una sola idea por pieza.** Los reels con más comentarios de la muestra tenían una idea y nada más.
5. **Pregunta escrita y respuesta en una frase.** El hámster contesta preguntas "recibidas" (en pantalla) con humor seco. Funciona como serie nueva: "El hámster responde".
6. **Reto de formato.** Explicar un tema en un número fijo de palabras o segundos, sin voz. Encaja con "esencia". Ejemplo: "Esencia del interés compuesto en 12 palabras."
7. **Pantalla dividida (resultado arriba, explicación abajo)** para reels donde haya algo que mostrar, como un antes y después de un CV.
8. **Personaje que habla de sí mismo con humor.** El hámster puede comentar que lo maneja una IA, de forma breve y sin repetir la misma broma.
9. **Credibilidad como hueco.** En los comentarios de los reels de promesas rápidas la gente desconfía ("vendehúmos", "no engañen"). "Mito verificado" puede desmentir promesas así en general, sin nombrar cuentas ni personas.

## Qué NO se adopta

- "Comenta PALABRA y te paso la guía" y cualquier embudo a WhatsApp, Discord o cursos. Prohibido en `REGLAS.md`.
- Promesas de dinero ("gano 250 euros al día", "640 dólares al día"). Prohibido en `REGLAS.md`.
- Tiempos poco creíbles ("una web en 2 minutos"). Si se afirma un tiempo, tiene que ser verdad.
- Copiar el personaje, el estilo visual o los textos de otra cuenta.

## Cómo se aplica

- Series nuevas candidatas: "El hámster responde" y "Esencia en N palabras". Se prueban una semana y se mide guardados y compartidos.
- Generador (`generador/generar.py`): añadir plantilla de reel con gancho en pantalla, texto grande y sello final. Pendiente hasta que Fernando agregue las skills de diseño.
- Medición: en `registro.md`, marcar qué técnica usó cada pieza para ver cuál funciona.

## Herramientas que mencionan los reels (revisadas, no instaladas)

Fuente: pies y fotogramas de los reels, más búsqueda web del 2026-10-24. Nada se instala sin revisar el código y los permisos antes (ver `RELEVO.md`).

| Herramienta | Qué es | Utilidad para la cuenta | Estado |
|---|---|---|---|
| UI UX Pro Max (repo nextlevelbuilder/ui-ux-pro-max-skill) | Skill de diseño con catálogo de estilos, paletas, tipografías y guías de UX. Licencia MIT según listados de terceros. | Mejorar tipografía, color y composición de `generar.py`. | Revisada e instalada en `.claude/skills/` (2026-10-24). Scripts locales, sin red |
| frontend-design (skill de Anthropic) | Skill oficial de diseño frontend, se recomienda junto a la anterior. | Misma mejora visual, con origen oficial. | Revisada e instalada en `.claude/skills/` (2026-10-24). Solo un SKILL.md |
| 21st.dev | Biblioteca de componentes web que se instala con shadcn y pide una clave de API. | Solo sirve para páginas web, no para piezas de Instagram. | No aplica ahora. La clave iría en variable de entorno, nunca en el repo |
| Motion (antes Framer Motion) | Librería de animación para web. | Solo para páginas web. | No aplica ahora |
| Picsart, Shorts, Google, Chrome | Se nombran como parte de recetas de "ganar dinero". | Ninguna para nosotros. No hay método verificable en lo que vi. | Descartado por `REGLAS.md` (no se publican promesas de dinero) |

Lo que no pude ver: el contenido de las "3 skills" de `miguebaenaia` y de la guía de `claudecode_es` está en el video o detrás de enlaces de su bio, no en el pie. Si Fernando quiere ese detalle, hay que ver cada video completo.
