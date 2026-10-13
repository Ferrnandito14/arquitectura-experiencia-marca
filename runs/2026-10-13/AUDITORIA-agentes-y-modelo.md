# Auditoría de los agentes y del modelo — jornada 13-oct-2026 (hora de Caracas)

Resultado del día: **todos los tickets perdidos**. Sistema: 3 patas acertadas de 7 resueltas. Persona usuaria (ticket D): 4 de 5. Registro por pata en `seguimiento/registro_resultados.jsonl`. Cuatro auditorías independientes (auditor adversarial, cuantitativo, deportivo, verificador de datos); este documento las consolida. Todo es de **un solo día y 12 patas**: sirve para encontrar fallos de proceso, no para probar que el modelo sea bueno o malo.

## 1. ¿Mala suerte o error de método?
| Medida | Valor |
|---|---|
| Aciertos esperados del sistema (probabilidad de mercado sin margen) | 4.8 de 7; reales 3; P(≤3) = 14.8 % |
| Unders | esperados 2.65 de 4; real 1; P(≤1) = 11 % |
| Perder A, B y C a la vez | 10–14 % |
| Ticket D | esperado 3.3 de 5, real 4 |

**Perder todo era plausible por varianza.** Lo que sí fue error de método: se armaron y se jugaron tickets con EV negativo (B −33 %, C −12 a −15 %, A −6 a −11 %) rotulados como "seguridad" o "defendibles".

## 2. Qué falló, por agente
| Agente | Acertó | Falló / no vio | Corrección |
|---|---|---|---|
| Verificador | hora, cuota y mercado coinciden con el feed | contrastó el feed consigo mismo; no exigió segunda fuente de cuotas ni alineaciones | cuota en ≥2 fuentes independientes; detectar precios anómalos en la escalera |
| Deportivo | regresión a la media, marcó Brugge +1.5 como débil | "neutral, algo positivo" para casi todo: no discrimina; Watford 6/11 y aun así "algo positivo"; no usó descanso, motivación, estilo, árbitro | escenario de pérdida cuantificado; con ≥3/11 cambios rebajar el veredicto |
| Cuantitativo | Durban 37 % de fallo; EV de C −15 % | llamó "robusto" a Cardiff por estabilidad de cuota; no dio P(pérdida) por ticket | entregar P(ticket) con rango; "robusto" solo con EV ≥ 0 |
| Auditor | Durban, Bayern 1.ª mitad, Brugge +1.5 | Cardiff, Viking y Leipzig en BAJO/MEDIO fallaron (3 de 3); veredictos "aceptable" con EV negativo; casi nunca "no apostar" | riesgo por P(fallo): <10 % bajo, 10–25 % medio, >25 % alto; "aceptable" prohibido con EV ≤ −5 % |
| Director | vetó Durban; concluyó "hoy no hay ×4" | reincorporó Durban para llegar a ×4; relajó filtros contra el consenso; "seguridad" ×1.25 con EV −11 % | ver §3 |

Nota del auditor: ≈5.5/9.

## 3. Fallos de proceso (del director)
1. Una pata vetada volvió al ticket para alcanzar el multiplicador: decidió el precio, no la evidencia.
2. Se relajaron filtros con los tres agentes diciendo "débil, EV −15 %".
3. Mismas patas repetidas entre tickets (Durban, Athletic, Leipzig, San Carlos, Bucaramanga).
4. Direcciones correlacionadas: tres de cuatro unders cayeron en un día de ~4 goles por partido en Champions; el producto de probabilidades las trata como independientes.
5. Se decidió sin alineaciones (la API las traía vacías); Watford llegó con 6/11 de habituales y Bayern con 5/11.
6. "Ausente del once" se presentó como baja: no lo es (Saka jugó y marcó).
7. Ticket D (de la persona usuaria) sin evaluación previa.
8. El multiplicador objetivo guio la selección en lugar de dejar el ticket vacío.

## 4. Sesgos
- **Maldición del ganador:** con n=10 y 300 patas, escoger las 7 de mayor brecha muestra−mercado produce brecha media +0.31 por puro ruido; las brechas reales (+0.13 a +0.27) son lo esperable sin ventaja real. **Una brecha grande no es señal.**
- **"Apoyo" de Wilson (n 6–10):** ordena por ruido, techo 0.722 con n=10; incoherente (vetó Durban, dejó pasar Cardiff con +0.25).
- **Sesgo de mercados:** el sistema excluye ganador/1X2 de favorito y "12"; solo ofrece totales, hándicaps y doble oportunidad. 4 de 5 patas de la persona usuaria eran de ganador/BTTS. Con n tan chico no se distingue del azar.

## 5. Fallos de datos y pipeline
| # | Fallo | Solución | Esfuerzo |
|---|---|---|---|
| 1 | Muestra = últimos ≤10 de la misma competición (n 6–10); las ligas completas ya descargadas (Serie B 328, Sudamericana 143, Colombia 249 partidos) no alimentan el ranking | muestras de liga/temporada con ajuste por rival y localía; mostrar siempre k/n | medio |
| 2 | Córners, tarjetas y remates con cuota estimada circular | fuera de tickets salvo cuota manual de la persona usuaria | bajo |
| 3 | Cuota = media de agregador, no ejecutable; `get_odds` da 404 para Athletic–Londrina y Bucaramanga | cuota manual obligatoria; segunda fuente | medio |
| 4 | Sin snapshots a T-60/T-0 (alineaciones, bajas, cuotas) ni bloqueo si falta el once | gate: sin once confirmado no hay ticket | medio |
| 5 | Caché de 24 h en `apif_query.py` devolvía marcadores atrasados | **CORREGIDO**: TTL 60 s para eventos, alineaciones, cuotas y estadísticas | hecho |
| 6 | El registro de resultados guardó "ACERTADA 2-0" que luego se anuló | **CORREGIDO**: registro rehecho con resultados finales; las patas de goles en vivo son provisionales | hecho |
| 7 | Hándicap de cuarto de línea, prórroga/penales y gol anulado sin liquidación ni prueba | añadir liquidadores y pruebas | medio |
| 8 | Árbitro se guardaba pero nada lo usaba | usar media de tarjetas/córners del árbitro y de la liga; alerta si es null en una pata de tarjetas | bajo |
| 9 | Una sola fuente (apifootball) para casi todo | evaluar fuentes permitidas adicionales con fila en `sources_policy.json` | alto |
| 10 | No se guarda probabilidad declarada, cuota ni alineación al proponer, ni intervenciones del director | `snapshots.jsonl` por pata + calibración diaria | medio |

## 6. Qué agregar (priorizado)
**Reglas del director:** (1) una pata vetada no vuelve a un ticket para alcanzar un multiplicador; si no hay combinación, "sin ticket"; (2) prohibido "seguridad/casi seguro" si P(ticket) < 85 % o EV < 0, y mostrar siempre P(pérdida); (3) sin once confirmado no hay ticket (esperar ~1 h antes); (4) máx. 1 pata repetida entre tickets y máx. 2 unders (u overs) por ticket y por día; (5) modo **"NO APOSTAR"** cuando el EV es negativo en todos los escenarios.
**Reglas deportivas:** rotación fuerte o defensa nueva ⇒ vetar el under; dominancia clara + rival rotado ⇒ cola de goles larga, no usar "menos de 4.5" como seguridad; "gana la 1.ª mitad" solo con ventaja muy clara; reincorporar mercados de ganador del favorito con filtro de dominancia; usar el promedio de goles de la competición/ronda como prior; calendario, descanso y fase de la eliminatoria obligatorios.
**Reglas cuantitativas:** encogimiento hacia el mercado p = (n·f + m·p_mercado)/(n + m), con m≈30–50; muestras n>30 antes que n=10; descuento por correlación entre patas de la misma dirección; registro de calibración (Brier, log-loss, hit-rate y ROI por tipo de mercado, rango de cuota y dirección); no sacar conclusiones con <30 patas por tipo; congelar un tipo con ROI < −10 % y n ≥ 30.

## 7. Límites de esta auditoría
12 patas en un día; una sola fuente de datos; las cuotas de los tickets son de TriunfoBet (no verificadas independientemente); las alineaciones "habituales" son comparación con los últimos partidos, no bajas confirmadas. Los agentes auditores son del mismo sistema que se audita.
