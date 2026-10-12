# football-picks-system

Sistema multiagente para investigar, contrastar y decidir picks de fútbol en Claude Code. Repositorio local independiente (sin remoto, no publicado). Separado de `insta-mcp`.

## Contenido
- `.claude/skills/seleccion-final-picks` — orquestadora: el director (la conversación principal) lanza, contrasta y **decide**.
- `.claude/skills/protocolo-multifuente` — catálogo de fuentes, mínimos de consulta, registro de 8 campos, diagnóstico de fallos de red.
- `.claude/skills/verificacion-estadistica-futbol`, `.claude/skills/evaluacion-probabilidad-valor` (+ `scripts/calc.py`).
- `.claude/agents/` — `verificador-mercados`, `analista-deportivo`, `analista-cuantitativo`, `auditor-adversarial`.
- `tests/` (unittest de `calc.py`, fixtures sintéticos, evidencia del flujo en `tests/runs/`), `docs/` (instalación, pruebas, diagnóstico de red), `install.sh` (opcional), `dist/` (entregables generados).

## Agentes, skills y coordinación
- **Skill** = procedimiento que se carga en un contexto (la orquestadora la ejecuta el director; las metodológicas se precargan en los agentes con el campo `skills:`).
- **Agente (subagente)** = trabajador con contexto propio, herramientas limitadas y un rol; no ve la conversación del director.
- **Coordinación** = quién habla con quién: por defecto el director lanza (`Agent` con `name`), reparte objeciones (`SendMessage`, que reanuda al agente con su contexto) y decide. Agent Teams (experimental) no se usa.

## Uso
En esta carpeta: `/seleccion-final-picks <borradores/candidatos, fecha, zona horaria>` o lenguaje natural ("decide los mejores picks…"). Cálculos: `python3 .claude/skills/evaluacion-probabilidad-valor/scripts/calc.py --help`. Tests: `python3 -m unittest discover -s tests -v`.

## Limitaciones conocidas (ver docs/PRUEBAS-picks.md)
La investigación con datos reales **no está validada**: en el entorno de desarrollo las webs deportivas están bloqueadas (docs/DIAGNOSTICO-RED.md). Lo probado con datos sintéticos demuestra la coordinación, no la calidad de la investigación real.
