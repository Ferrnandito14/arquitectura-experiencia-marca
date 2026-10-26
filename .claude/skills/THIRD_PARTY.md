# Skills de terceros

Copiadas tal cual (MIT, ver licencias) desde repos públicos. Para actualizar, volver a copiar desde el origen.

| Skill | Origen |
|---|---|
| i-have-adhd | https://github.com/ayghri/i-have-adhd (skills/i-have-adhd) |
| no-ai-slop | https://github.com/petergyang/no-ai-slop (skills/no-ai-slop) |
| book-to-skill | https://github.com/virgiliojr94/book-to-skill (raíz: SKILL.md, scripts/, book_to_skill/) |

No se instalaron los hooks de i-have-adhd (always-on) ni scripts de evaluación.

## Plugins (declarados en `.claude/settings.json`)

Se instalan al abrir el repo y aceptar la confianza de la carpeta (requiere Claude Code 2.1.289+ y Node 22+).

- `claude-code-mods` (hamzafer): activados context-bar, usage-meter, where-am-i, blast-radius, agent-radar, mission-control, replay-theater, next-steps, rulebook-guard, cache-clock, heatmap, review-watch, browser-lanes, prayer-times, reels, snake (cache-clock pide además `/cache-clock setup`). El resto: `/plugin install <mod>@claude-code-mods`.
- `agent-router-tools` (alexandernicholson): activado keepalive. `agent-router` queda disponible sin activar: necesita un endpoint compatible con Anthropic (`/plugin install agent-router@agent-router-tools`).

## Skills de CV y búsqueda de empleo

- Copiadas de https://github.com/Paramchoudhary/ResumeSkills (licencia en `_licenses/`): resume-ats-optimizer, resume-tailor, resume-bullet-writer, resume-quantifier, linkedin-profile-optimizer, cover-letter-generator, job-description-analyzer, interview-prep-generator, cold-email-writer, resume-section-builder, career-changer-translator. Quedaron fuera las demás del repo (ejecutivo, académico, portafolio, ofertas, etc.).
- Plugin `resume-optimizer` (https://github.com/KivancSerefoglu/resume-optimizer), declarado en `settings.json`: puntúa una oferta contra tu trayectoria, adapta el CV y escribe la carta sin inventar datos. Usa Chrome o Edge para generar el PDF y `pdftotext` o `pypdf` para revisar el ATS. Solo carga en la terminal de Claude Code.

## Skills de diseño (para las piezas de la cuenta de Instagram)

- `ui-ux-pro-max`: copiada de https://github.com/nextlevelbuilder/ui-ux-pro-max-skill (commit d14efff, MIT, licencia en `_licenses/`). Solo la carpeta de la skill, sin los tests. Revisada el 2026-10-24: los scripts son locales (sin red, sin subprocess, sin escritura de archivos fuera de lo que se les pide) y los datos son tablas de estilos, paletas y tipografías. No se instalaron las otras skills del repo (design, ui-styling, brand, slides, banner-design): algunas llaman a APIs externas con claves o a shadcn.
- `frontend-design`: copiada de https://github.com/anthropics/skills (commit dbd4588, Apache 2.0, licencia en `_licenses/`). Es solo un SKILL.md con guía de diseño, sin scripts.
- `framer-motion`: copiada de https://github.com/Schoepplake/framer-motion-skill (commit 1d984d5, MIT según su README; el repo no trae archivo de licencia). Solo un SKILL.md con patrones de animación para React y Next.js, sin scripts ni llamadas de red. Revisada el 2026-10-24. Es la skill de movimiento del trío de diseño web que mencionan los reels (junto a `frontend-design` y `ui-ux-pro-max`). No se instaló 21st.dev: pide una clave de API y solo sirve para componentes web.
- `refero-design`: copiada de https://github.com/referodesign/refero_skill (commit 2382e51, MIT, licencia en la carpeta). Solo SKILL.md y `references/` (guías de tipografía, color, movimiento, iconos, textos y anti-slop), sin scripts. Se quitó la carpeta `agents/` (configuración para OpenAI). Revisada el 2026-10-25. Su conector Refero MCP es de pago y no se conectó.

## Instalado fuera de `.claude/skills/`

- `remotion-best-practices` en `~/.claude/skills/`: copiada de https://github.com/remotion-dev/skills (commit 6c67adc, sin archivo de licencia, por eso no se sube al repo). Guías de Remotion (animación, audio, subtítulos, render, mapas) y dos scripts opcionales de mapas que solo leen y escriben archivos locales. Revisada el 2026-10-25. La documentación cita una clave pública de búsqueda de Algolia de la web de Remotion, que no es secreta.
- Conector oficial de Netlify (`@netlify/mcp`, versión fija 1.18.0 del 2026-10-07) en `.mcp.json`. Revisado el 2026-10-25: lee el token de la variable `NETLIFY_AUTH_TOKEN` (pasada como `NETLIFY_PERSONAL_ACCESS_TOKEN`), habla con `api.netlify.com`, descarga guías de `netlify.com/context-files` y, solo para extensiones, `api.netlifysdk.com`. Si no hay token intenta `netlify login`, que abre el navegador. Sin scripts al instalar. Su herramienta de despliegue sugiere `npx @netlify/mcp@latest`; se usa con la versión fija.

