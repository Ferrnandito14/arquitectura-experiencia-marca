# Sistema multiagente de selección de picks de fútbol

Ubicación: `.claude/skills/*` y `.claude/agents/*` (proyecto). Relocalizable copiando ambas carpetas a `~/.claude/` o a otro repo.

## Uso
- `/seleccion-final-picks <borradores o candidatos, fecha, zona horaria>` o lenguaje natural ("decide los mejores picks de mañana", "compara A vs B").
- Agentes: `verificador-mercados`, `analista-deportivo`, `analista-cuantitativo`, `auditor-adversarial` (también invocables a mano).
- Cálculos: `python3 .claude/skills/evaluacion-probabilidad-valor/scripts/calc.py {implied|novig|ev|combo|joint|freq} ...`
- Opcional: Agent Teams (`CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1`) para mensajería directa; por defecto la coordinación pasa por el director.

## Integración con `cobertura-exhaustiva-picks`
Esa skill vive en las skills sincronizadas de la cuenta (`~/.claude/skills/synced/...`), no en un repo, y no se modificó. La integración es: `seleccion-final-picks` la invoca en el Paso 1 y `protocolo-multifuente` (en este proyecto) añade el catálogo y los mínimos. Para que también aplique cuando se invoque sola, añade a su `SKILL.md` en claude.ai la línea: «Aplica además `protocolo-multifuente` (calendarios de ≥5 proveedores, no solo SofaScore/APWin, y tabla de registro de fuentes).»
