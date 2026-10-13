# Resolución del director — jornada 2026-10-13 (America/Caracas) · v2.4
Sustituye a la resolución anterior (matriz previa a la API). Estado: **PROVISIONAL RESTRINGIDO**. Nada de lo siguiente es una probabilidad ni un valor esperado demostrado.

## Proceso
Nivel 1 por scripts (319 partidos requeridos) → revisión por lotes de agentes (319/319 por deportivo y cuantitativo; 30 discrepancias por verificador; `batches.py check` ok) → Nivel 2 sobre 21 finalistas (verificador, deportivo, cuantitativo, auditor) → regeneración con vetos → auditoría adversarial de los borradores (`reviews_raw/level2/auditor_ronda2.md`).
Las objeciones del auditor se tratan como objeciones estructuradas; el hilo `SendMessage` con los agentes del Nivel 2 se perdió con los reinicios del worker, por lo que la ronda 2 la hizo un auditor nuevo (no una continuación).

## Decisiones
| Objeción | Decisión |
|---|---|
| T1 Apoyo = promedio de dos equipos, un 10/10 tapa al flojo | **Aceptada**: piso por equipo (0.55 seguridad; 0.45 amplio, relajado y rotulado). |
| T2 Apoyo conjunto bajo el equilibrio 1/cuota en todos los borradores | **Aceptada y declarada**: ningún borrador tiene ventaja demostrable; se muestra el apoyo conjunto y la implícita de mercado. |
| T3 Patas «12» con ~8 % de empates | **Aceptada**: todas las patas «12» fuera de tickets hasta verificar marcadores a 90'. |
| T4 Kyoto +1.5 en 4 de 5 borradores | **Aceptada**: una pata aparece como máximo en 2 borradores de un perfil. Sigue siendo el único EV descriptivo positivo y se señala como posible sobreajuste. |
| T5 Tops con 3 casas, 1 fuente o sub-23 | **Aceptada**: tops y tabla de córners/tarjetas solo con patas elegibles. |
| Vetos: Pohang O1.5, Kaizer +1.5, Petrojet O1.5, Sariyer U4.5, Villarreal +1.5 | **Aceptados** (en `vetoes.json`). |
| Córners/tarjetas «inutilizables» | **Parcialmente aceptada**: se mantienen como referencia con cuota APROXIMADA rotulada y «cuota real mínima a exigir»; ninguna entra en tickets sin cuota real (`--manual-odds`). |
| Comprobar si ya empezaron los partidos de 10:00Z | **Aceptada**: la hora actual y el estado en vivo deben comprobarse antes de apostar. |

## Orden de defendibilidad (según el auditor, sobre la versión previa al piso por equipo)
Seguridad: Bucaramanga 1X > Pendikspor O1.5 > Cardiff U4.5 > Birmingham+Harju > Al Sadd «12»+Sariyer (esta última salió de los tickets). Amplio: A-D2 > A-D1 > A-D3 > A-D5 > A-D4 (D4 y D5 reemplazados por la regeneración). Ninguno es «defendible» en sentido estadístico fuerte.

## No evaluable / pendiente
34 partidos sin fuente permitida; 13 con intento insuficiente; 3 partidos de Zambia con hora sin resolver; alineaciones, bajas y árbitro no disponibles; cuotas ejecutables y cuotas reales de córners/tarjetas no disponibles.

## Qué haría falta para cerrar
1. Tus cuotas reales por pata (CSV `home,away,seleccion,cuota`) para confirmar los rangos ×1.20–1.28 y ×4.0–4.8 con `--manual-odds`.
2. Alineaciones y bajas del día; marcadores a 90' para reabrir las patas «12».
3. Comprobar la hora actual y el estado de cada partido.

## Pares del mismo partido: reevaluación por agentes (autorizada por la persona usuaria si hay respaldo estadístico y de los agentes)
Informes: `reviews_raw/level2/pares_{deportivo,cuantitativo,auditor}.md`. Regla de decisión: un par solo se propone si ningún agente lo declara DESACONSEJADO; los pares con respaldo dividido se vetan; los aceptados llevan su condición en el ticket.
| Par | Deportivo | Cuantitativo | Auditor | Decisión |
|---|---|---|---|---|
| Birmingham–Preston: +2.5 visitante + menos de 4.5 (×1.282, cons ×1.218) | Aceptable con salvedades | Aceptable con salvedades | Aceptable con salvedades | **Se mantiene** (borrador de seguridad #1) con condición: cuota real del combinado ≥1.20 y alineaciones; si paga menos, mejor la pata simple menos de 4.5 |
| Bucaramanga: 1X + menos de 4.5 | Aceptable flojo | Desaconsejado | Desaconsejado | Vetado |
| Bucaramanga: 1X + más de 0.5 | Aceptable | Desaconsejado | Desaconsejado | Vetado |
| Birmingham–Preston: menos de 4.5 + 1X | Desaconsejado | Desaconsejado | Desaconsejado | Vetado |
| Kyoto–Ratchaburi: +1.5 + menos de 3.5 (variante Champions) | Desaconsejado | Aceptable condicionado (cuota ≥2.35) | Aceptable en el límite (cuota ≥2.20) | Vetado: sin respaldo unánime |
Correcciones aceptadas del auditor: se retira la frase «las patas se refuerzan entre sí (0.722 vs 0.521)», que comparaba cosas incomparables (el 0.722 es el techo de Wilson de un 10/10 con n=10); el overround 1.153 que motivó el veto de la +1.5 de Birmingham era un artefacto de mezclar medias de casas distintas (con medianas es 1.089), aunque el veto se mantiene por las demás causas. Veto adicional: todo el partido Pohang–Johor.
Ningún agente considera defendible (valor demostrado) ningún par; el mejor es «probable pero no rentable demostrado» (EV de modelo −4 % a −9 %).
