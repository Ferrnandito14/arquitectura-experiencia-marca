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

- `claude-code-mods` (hamzafer): activados context-bar, usage-meter, where-am-i, blast-radius, agent-radar, mission-control, replay-theater, next-steps, rulebook-guard, cache-clock, heatmap (cache-clock pide además `/cache-clock setup`). El resto: `/plugin install <mod>@claude-code-mods`.
- `agent-router-tools` (alexandernicholson): activado keepalive. `agent-router` queda disponible sin activar: necesita un endpoint compatible con Anthropic (`/plugin install agent-router@agent-router-tools`).
