# Pruebas — estado real (2026-10-12, Claude Code 2.1.296, contenedor cloud)

Las tres categorías NO se mezclan. Los resultados sintéticos no validan investigación deportiva real.

## 1. Ejecutadas con DATOS REALES
| # | Prueba | Resultado |
|---|---|---|
| 1 | Carga: 4 agentes y 4 skills detectados | **OK.** `claude -p` ejecutado desde este repo listó `analista-cuantitativo, analista-deportivo, auditor-adversarial, verificador-mercados` y las skills `evaluacion-probabilidad-valor, protocolo-multifuente, seleccion-final-picks, verificacion-estadistica-futbol`. Además aparecen las skills de cuenta `cobertura-exhaustiva-picks` y `reto-de-90-dias-20`. |
| 2 | Script `calc.py` (válidos, límites, inválidos) | **OK.** `python3 -m unittest discover -s tests -v` → 19 tests, OK. Entradas inválidas → stderr + exit 2, sin trazas (incl. `freq 11 10`, `freq 0 0`, `implied 0`, nan/inf, nº de args). |
| 3–5 | Intentos reales de acceso a fuentes deportivas (calendarios, córners/tarjetas, cuotas) | **Ejecutados; resultado: ACCESO FALLIDO en los 22 dominios del catálogo.** curl: `CONNECT tunnel failed, response 403`; WebFetch: `getaddrinfo ENOTFOUND`; `getent hosts` sin resolución. Detalle por capa en `docs/DIAGNOSTICO-RED.md`. Un `verificador-mercados` real (v1) intentó Flashscore, Soccerway, worldfootball y LaLiga oficial y registró "Acceso fallido" con el error literal, sin inventar partidos. Defecto corregido en v2: intentar ≥2 URLs por fuente y diagnosticar la capa. |
| — | `install.sh` (`--dry-run`, creación, idempotencia, argumento inválido) | **OK** sobre un directorio temporal (9 archivos; segunda ejecución 0 cambios; `--bogus` → exit 2). |
| 10 | Persistencia: ZIP, patches, checksums | Ver `dist/VERIFICACION.txt` (generado fuera del ZIP) y el informe final. |

## 2. Ejecutadas con DATOS DE PRUEBA (sintéticos — "EJEMPLO — NO REAL")
Fixture: `tests/fixtures/ejemplo_no_real.md`; expectativas fijadas antes: `tests/fixtures/EXPECTATIVAS.md`; evidencia: `tests/runs/` (MANIFIESTO, transcripciones, `RESOLUCION-director.md`). 4 agentes reales con nombre; 0 llamadas a WebFetch/WebSearch (solo Read y Bash).
| # | Prueba | Resultado |
|---|---|---|
| 6 | Comparación probable vs valor | **OK.** Cuanti separó "más probable" (B nominal) de "mejor valor"; el director resolvió las 3 preguntas por separado. Ningún candidato con valor demostrado (EV cruza 0 en A y E). |
| 7 | Desacuerdo: auditor objeta → agente responde → director resuelve | **OK.** El auditor objetó E, A, B; el director envió 3 objeciones con `SendMessage`; cuanti corrigió E (suelo 60%→55%, retiró "mejor valor") y declaró B no estimable; deportivo cambió su orden a A > E > B; verificador degradó "Verificado" a "con salvedad". Caso "alta probabilidad/precio desfavorable" (B) resuelto con la evidencia deportiva (baja confirmada). |
| 8 | Sustitución de borrador débil | **OK.** D (n=4, H2H 2019, 1 cuota) → SUSTITUIR por E (2 orígenes + 2 cuotas). |
| 9 | Cierre | **OK.** 2 rondas, 0 terceras comprobaciones (ningún dato pendiente cambiaba el estado de A/E), decisión final emitida por el director. |
| C | Fuente defectuosa | **OK.** `corners-b` (ceros incompatibles) detectada y descartada por verificador, deportivo y cuanti; C quedó NO EVALUABLE. |
| — | Mecanismos de comunicación | **Verificado:** `Agent` con `name` en paralelo; `SendMessage` a agente terminado lo reanuda con su contexto (mismo agentId; deportivo respondió citando su ronda 1 con 0 herramientas); mensajería entre pares: deportivo → cuanti entregada y respondida; roster (`main, cuanti, verificador`) visible en el contexto reanudado. En ninguna ejecución de decisión los agentes se escribieron solos: la coordinación fue mediada por el director. |
Desviaciones observadas: el verificador omitió la columna "Fecha de consulta" en su tabla (la declaró aparte); los subagentes afirmaron estar en "modo plan" y no escribieron archivos (el sistema no lo necesita, pero indica que heredan el modo de permisos de la sesión que los lanza). Los rangos de probabilidad de cuanti son juicio declarado, no modelo.

## 3. NO ejecutadas, con motivo
| Prueba | Motivo |
|---|---|
| 3 (matriz multifuente real), 4 (córners/tarjetas línea exacta real), 5 (dos cotizaciones reales) con datos | Dominios bloqueados por la política de red del entorno (ver DIAGNOSTICO-RED). Requiere autorizar los dominios en *Network access → Allowed domains* y repetir. |
| 6–9 con partidos reales | Mismo bloqueo. Lo sintético demuestra la coordinación, no la calidad de la investigación real. |
| Agent Teams | No activado deliberadamente (experimental, no necesario). |
| Cobertura/uso de `cobertura-exhaustiva-picks` | Skill de cuenta (almacén sincronizado), no modificada ni invocada en las pruebas; su integración está definida en el Paso 1 pero no probada. |
| Zonas horarias/franjas del usuario, combinadas reales | No hubo datos reales. |
