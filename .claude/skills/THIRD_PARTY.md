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
