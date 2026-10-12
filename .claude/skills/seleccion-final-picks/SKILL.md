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

## Paso 2 — Ronda 1: investigación paralela
En UN solo mensaje lanza en paralelo (herramienta Agent, `run_in_background` según convenga) y **ponles `name`** para poder escribirles después:
- `verificador-mercados` (name `verificador`): calendario/estado, mercado exacto, estadísticas publicadas, cuotas en ≥2 fuentes, tabla de registro de fuentes.
- `analista-deportivo` (name `deportivo`): forma ajustada, bajas, contexto, por mercado.
- `analista-cuantitativo` (name `cuanti`): estadísticas del mercado exacto, rangos de probabilidad, precio, EV.
Los subagentes no ven tu conversación: en cada prompt incluye candidatos, fecha/zona horaria, mercados/líneas, lo que ya se sabe, qué entregar y la obligación de registrar fuentes (estados permitidos). Reparte por candidato/competición si hay muchos. Exige: hechos, a favor, en contra, pendientes.

Después lanza `auditor-adversarial` (name `auditor`) con los candidatos mejor valorados y los resúmenes de ronda 1.

## Paso 3 — Ronda 2: contraste real
Construye la **lista de contradicciones** (dato vs dato, fuente vs fuente, tesis deportiva vs precio, objeción del auditor). Distribúyela: a cada agente envíale, con `SendMessage` (a su `name`; reanuda con su contexto) o nuevo Agent si ya terminó y no es reanudable, las objeciones relevantes de los demás **citando su evidencia**. Cada uno debe: responder, corregir errores demostrados, indicar qué evidencia pesa más y por qué.
Honestidad sobre el mecanismo: esto es comunicación mediada por el director (hub-and-spoke). Hay mensajería directa entre agentes solo si Agent Teams está activo (`CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1`, experimental, más coste) y el agente tiene `SendMessage` y nombre; no la afirmes si no lo comprobaste en la ejecución. Reporta qué modalidad se usó.

## Paso 4 — Resolución
Decide tú. Sin unanimidad; priorizas calidad de datos y pertinencia de la evidencia. **Tercera comprobación excepcional** solo si un dato crítico (baja decisiva, cuota mal identificada, línea/liquidación) puede cambiar la decisión: una consulta dirigida, no una nueva ronda. Cierre: tras 2 rondas (+ la excepcional). No reinicies por discrepancias menores ni repitas datos sin evidencia nueva. Incertidumbre ≠ parálisis; obligación de decidir ≠ fabricar certeza.

Estados por candidato: **SELECCIONAR · MANTENER COMO ALTERNATIVA · SUSTITUIR · DESCARTAR · NO EVALUABLE**.
- Sin precio verificado (≥2 fuentes comparables) → puede conservarse como "fundamento deportivo, sin precio confirmado", nunca como valor económico confirmado.
- Cuota alta probabilidad/precio desfavorable: resuélvelo explícitamente (alta probabilidad ≠ valor).
- Combinadas: recalcula multiplicador (misma casa), evalúa correlación, identifica piernas débiles, busca sustitutos, compara tickets. No fuerces N combinadas; no recomiendes apostar todas las alternativas; separa objetivos (p. ej. ×1.20 vs ×4–4.8).

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
