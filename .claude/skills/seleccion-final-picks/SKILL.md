---
name: seleccion-final-picks
description: Orquesta la investigación multiagente y la decisión final de picks de fútbol - amplía el calendario, activa verificador, analistas y auditor en paralelo, organiza el contraste, resuelve discrepancias y entrega SELECCIONAR/ALTERNATIVA/SUSTITUIR/DESCARTAR/NO EVALUABLE. Úsala cuando el usuario pida elegir, comparar, validar o sustituir picks o borradores de combinadas, o diga "decide los mejores picks".
---

# Selección final de picks — director de decisión

Tú (la conversación principal) eres el **director de decisión**: coordinas, resuelves y decides. No crees un quinto agente. Eres el responsable final de conservar, sustituir o descartar. Los borradores del usuario NO son picks aprobados. Ninguna apuesta es segura; son candidatos evaluados.

Equipo (subagentes en `.claude/agents/`): `verificador-mercados`, `analista-deportivo`, `analista-cuantitativo`, `auditor-adversarial`.
Metodología: `protocolo-multifuente` (fuentes y registro), `verificacion-estadistica-futbol`, `evaluacion-probabilidad-valor` (+ `scripts/calc.py`).

## Paso 0 — Alcance
- Lista cerrada de 2–3 candidatos para comparar → no reconstruyas la jornada; ve al Paso 2.
- Borradores/universo abierto/fecha → Paso 1.
- No pidas al usuario cuotas de Triunfobet ni ligas a revisar; si las aporta, regístralas como "comunicadas por el usuario". Pregunta solo por datos personales imprescindibles.
- Franjas horarias definidas por el usuario = bloques separados, clasificados por hora de **inicio**; no mezcles.

## Paso 1 — Cobertura del calendario
Invoca la skill `cobertura-exhaustiva-picks` si existe en el entorno (inventario, auditoría de cobertura, diversificación) y aplica SIEMPRE `protocolo-multifuente` (calendarios Flashscore/Soccerway/worldfootball/BetExplorer/FotMob + oficiales; no solo SofaScore/APWin). Si `cobertura-exhaustiva-picks` no está disponible, ejecuta tú ese inventario con `verificador-mercados`. Resultado: lista maestra de partidos únicos, competiciones no examinadas y candidatos priorizados. Nuevos partidos pueden reemplazar borradores.

## Mecanismos de coordinación (probados en Claude Code 2.1.296 el 2026-10-12; evidencia en docs/PRUEBAS-picks.md y tests/runs/)
- **Por defecto: mediada por el director (hub-and-spoke).** Lanzas especialistas con `Agent` (varias llamadas en un mismo mensaje = paralelo) y **siempre con `name`**; cada informe vuelve a ti.
- **Objeción → respuesta (verificado):** `SendMessage` con `to` = nombre del agente ya terminado lo **reanuda con su contexto** (mismo agentId; el agente responde citando su ronda 1 sin que se la reenvíes) y la respuesta llega como notificación. Si el nombre no resuelve usa el agentId; si no se puede reanudar, relanza un `Agent` con su informe previo + la objeción.
- **Entre pares (verificado, pero no es el flujo base):** los agentes tienen `SendMessage` y, al reanudarse, ven un roster de agentes con nombre (`main` y los demás). Un agente pudo escribir a otro por nombre y recibir respuesta directa. Aun así, **el director sigue siendo quien reparte las objeciones y decide**; no dependas de que se coordinen solos. Informa en D qué ocurrió realmente.
- **Agent Teams** (experimental, `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1`, lista de tareas compartida): NO activado ni necesario. No lo actives sin explicar antes el cambio a la persona. Con Teams activo, un subagente lanzado con `name` pasa a ser teammate (otro modo de funcionamiento).
- Los subagentes no ven tu conversación ni tus skills cargadas: las skills metodológicas llegan por el campo `skills:` de cada agente y todo contexto va en el prompt.

## Paso 2 — Ronda 1: investigación paralela
En UN solo mensaje lanza con `Agent` (`name` fijo, `subagent_type` el del agente): `verificador-mercados` (name `verificador`), `analista-deportivo` (name `deportivo`), `analista-cuantitativo` (name `cuanti`). Los subagentes NO ven tu conversación: el prompt debe ser autocontenido.

**Plantilla de delegación** (rellena los corchetes):
```
CONTEXTO: [fecha/zona horaria; si hay datos de prueba: "EJEMPLO — NO REAL, solo fixture://, prohibido web/memoria"]
CANDIDATOS: [id | partido | mercado y línea exacta | cuota comunicada y quién la comunicó]
MATERIAL/FUENTES A USAR: [rutas de fixtures, o "catálogo del protocolo-multifuente"]
TU TAREA: [la función del agente + qué candidatos]
CÁLCULOS: usa python3 .claude/skills/evaluacion-probabilidad-valor/scripts/calc.py (no calcules a mano)
ENTREGA (formato fijo): 1) tabla de registro de fuentes (8 campos, estados permitidos); 2) por candidato: hechos con fuente/fecha/n · a favor · en contra · pendientes · estado propio (Verificado/Parcial/No verificable o rango de prob.); 3) limitaciones.
```
Después, con los resúmenes de ronda 1, lanza `auditor-adversarial` (name `auditor`) sobre los candidatos mejor valorados.

## Paso 3 — Ronda 2: objeción → respuesta
Haz la **lista de contradicciones** (dato vs dato, fuente vs fuente, tesis deportiva vs precio, objeción del auditor, cifras defectuosas). Por cada una, `SendMessage` al agente responsable con esta plantilla:
```
OBJECIÓN [n] sobre [candidato]: [qué dice quién] · EVIDENCIA: [cita literal + fuente]
PREGUNTA: ¿corriges, defiendes con evidencia nueva, o declaras no verificable? Responde en ≤10 líneas: RESPUESTA | EVIDENCIA | CAMBIO EN TU ESTADO DEL CANDIDATO.
```
Aplica lo que cada agente corrija. Quien objeta no decide: decides tú.

## Paso 4 — Resolución y cierre (decide SIEMPRE tú)
Responde por separado, para cada candidato relevante: **(1) ¿cuál es más probable? (2) ¿cuál tiene mejor relación probabilidad/cuota (valor)? (3) ¿cuál es la mejor alternativa global tras evidencia y riesgo?** Una selección probable con precio desfavorable no es valor; una cuota alta no es valor sin probabilidad defendible. Si la probabilidad no es estimable: "no estimable", sin EV.

Asigna a cada candidato: **SELECCIONAR · MANTENER COMO ALTERNATIVA · SUSTITUIR · DESCARTAR · NO EVALUABLE**:
- SELECCIONAR: fundamento sólido, datos esenciales confirmados en ≥2 orígenes y precio verificado (≥2 cotizaciones comparables) — si falta el precio, como mucho "fundamento deportivo, sin precio confirmado" (alternativa).
- SUSTITUIR: hay una alternativa mejor respaldada (indica cuál y por qué). DESCARTAR: deficiencia material concreta. NO EVALUABLE: faltan datos esenciales que no se pudieron obtener.
- Sin unanimidad: pesa calidad y pertinencia de la evidencia. Nunca devuelvas la elección ni la síntesis a la persona; si la evidencia no separa dos opciones, dilo y elige con criterio explícito (p. ej. menor riesgo/menor correlación).
- **Cierre:** 2 rondas. **Tercera comprobación** solo si un dato crítico concreto (baja decisiva, cuota mal identificada, línea/liquidación) puede cambiar el estado de un candidato: una consulta dirigida a un solo agente, no una ronda nueva. No reinicies por discrepancias menores ni repitas datos sin evidencia nueva.
- Combinadas: multiplicador solo con cuotas de la misma casa (`calc.py combo`); correlación declarada; no fuerces N tickets; no recomiendes apostar todas las alternativas; bloques horarios del usuario separados.

## Paso 5 — Respuesta (empieza por la decisión)
A. **Veredicto ejecutivo** (qué seleccionas, descartas y por qué).
B. **Clasificación**: tabla candidato | mercado | cuota verificada (fuente/fecha) | fundamento | riesgo | decisión.
C. **Evidencia decisiva** (estadística, contextual, precio).
D. **Contraste entre agentes**: desacuerdos, evidencia que los resolvió, incertidumbres vigentes; modalidad de coordinación usada.
E. **Fuentes efectivamente consultadas** (tabla de registro; estados reales; fuentes inaccesibles).
F. **Riesgos y alternativas** (qué invalidaría la selección; sustituto razonable).
G. **Estado de validación**: respaldada por datos y precio verificables · fundamento deportivo sin precio · alternativa con incertidumbre · descartado · no evaluable.

## Reglas de integridad
No simules visitas, herramientas ni conversaciones. Si las webs no son accesibles (política de red, bloqueo, JS), dilo en E, no rellenes con memoria como si fuera dato actual, y degrada los candidatos a "NO EVALUABLE" o "sin verificar" según corresponda. Esta skill no toca el seguimiento del capital (`reto-de-90-dias-20`); respeta sus reglas de honestidad si ambas están activas.
