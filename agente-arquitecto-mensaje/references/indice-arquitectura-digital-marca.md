# Índice de Arquitectura Digital de Marca (IADM)

Herramienta propietaria de la startup. Es el instrumento de puntuación de
la Fase 0 (Auditoría) — el diagnóstico siempre mide los 4 niveles
completos, sin excepción, aunque un nivel termine sin evidencia
suficiente para puntuar con confianza.

Los 4 niveles son acumulativos en el sentido de que cada uno depende de
que el anterior tenga una base mínima: es difícil que la Experiencia
funcione bien si la Arquitectura está desordenada, y es difícil evaluar
Performance con confianza si la Presencia es tan débil que no genera
tráfico que medir. Por eso el orden de la puntuación importa, no solo el
resultado.

## Nivel 1 — Presencia: ¿qué existe?

Pregunta central: de todo lo que la empresa podría tener (espacios
físicos, productos, sitio web, redes activas, e-commerce, presencia en
distribuidores/marketplaces), ¿cuánto existe realmente y está vivo?

Evidencia a buscar: canales activos vs. abandonados/caídos, cobertura de
producto/catálogo, presencia en los canales que su categoría de negocio
esperaría (un negocio B2B necesita presencia distinta a un negocio de
consumo masivo).

| Score | Criterio |
|---|---|
| 1 | Casi nada existe, o lo que existe está roto/abandonado |
| 2 | Existe lo mínimo (un canal, incompleto) |
| 3 | Existen varios canales pero con huecos notorios (uno caído, otro sin actualizar) |
| 4 | Cobertura completa de los canales esperables para su categoría, todos vivos |
| 5 | Cobertura completa y además presencia en canales que superan lo esperable para su categoría/tamaño |

## Nivel 2 — Arquitectura: ¿cómo está organizado?

Pregunta central: lo que existe, ¿está organizado con una lógica clara
—jerarquía de marca/portafolio, navegación, identidad consistente entre
piezas, información encontrable— o es una colección de piezas sueltas
que no se hablan entre sí?

Evidencia a buscar: coherencia de marca entre canales (mismo tono, mismo
nombre, sin fragmentación de dominios/cuentas compitiendo por representar
"lo oficial"), si la información está organizada por la lógica del
negocio o por la lógica del usuario, si hay una arquitectura de portafolio
explicable cuando existen varias marcas/líneas.

| Score | Criterio |
|---|---|
| 1 | Fragmentación seria: dominios/cuentas duplicados o contradictorios, sin forma de saber cuál es oficial |
| 2 | Organización inconsistente, mezcla lógica del negocio con lógica del usuario sin resolver cuál manda |
| 3 | Organización coherente pero con al menos una pieza claramente desconectada del resto |
| 4 | Arquitectura clara y consistente en todos los canales revisados |
| 5 | Arquitectura clara, consistente, y explícitamente pensada desde la decisión del usuario (no solo desde la estructura interna de la empresa) |

## Nivel 3 — Experiencia: ¿cómo funciona?

Pregunta central: alguien que llega con una necesidad real, ¿puede
descubrir, entender, confiar y decidir sin fricción innecesaria? Este
nivel es el más cercano al método de recorrido físico-digital de
`arquitectura-experiencia-marca` — si esa skill ya se usó para mapear el
recorrido de esta empresa, apóyate en ese análisis en vez de repetirlo
desde cero.

Evidencia a buscar: qué tan rápido resuelve el canal digital las
preguntas que resolvería un buen vendedor/asesor en persona, dónde
hay pasos redundantes o información repetida, si hay señales de
confianza (precio visible, disponibilidad, ficha técnica, reseñas
gestionadas).

| Score | Criterio |
|---|---|
| 1 | El usuario se pierde o abandona antes de poder decidir nada |
| 2 | El usuario puede avanzar pero con fricción alta (vocabulario técnico sin traducir, pasos redundantes, info repartida) |
| 3 | El recorrido funciona pero requiere esfuerzo o paciencia del usuario |
| 4 | El recorrido es fluido para el caso más común |
| 5 | El recorrido es fluido incluso para casos menos comunes (usuarios distintos, necesidades atípicas) |

## Nivel 4 — Performance: ¿funciona de verdad?

Pregunta central: más allá de cómo se ve o cómo está organizado, ¿está
generando resultados medibles (tráfico, conversión, leads, ventas,
retención, costo de adquisición)?

**Restricción importante:** este nivel casi nunca es evaluable desde
información pública — depende de datos internos (analítica, CRM, ventas)
que solo la empresa tiene. Si el parámetro `datos_internos` no fue
proporcionado, no inventes ni estimes una cifra como si fuera dato duro.
En su lugar:
- Usa proxies públicos donde existan y sean razonables (ej. volumen de
  reseñas y su fecha más reciente como proxy de actividad; presencia en
  marketplaces con historial de ventas visible; señales indirectas como
  inversión publicitaria detectable).
- Marca explícitamente el score de este nivel como *"no evaluable sin
  datos internos"** en vez`îf forzar un número, y explica qué dato
  específico se necesitaría pedirle al cliente para poder puntuarlo.

| Score | Criterio (solo si hay datos internos o proxies razonablemente confiables) |
|---|---|
| 1 | Sin evidencia de que los canales generen resultado de negocio |
| 2 | Resultados esporádicos o muy por debajo de lo esperable para su tamaño |
| 3 | Resultados presentes pero sin evidencia de optimización activa |
| 4 | Resultados sólidos con señales de medición y ajuste activo |
| 5 | Resultados sólidos, medidos, y con ciclo de optimización visible/documentado |

## Cómo se convierte el score en prioridades

El resultado del IADM **no es solo un score — termina en Prioridades de
intervención**. Este es el paso que más valor aporta y el que más fácil
es hacer mal:

**No prioces automáticamente por el nivel más bajo.** Una empresa puede
tener Performance = 1 pero el problema real y más urgente es de
Arquitectura ("nadie sabe dónde comprar" — la gente que sí llega no
encuentra el camino, así que no hay forma de que Performance mejore hasta
resolver eso primero). Prioriza por **causa raíz e impacto de negocio**,
no por cuál número es más bajo en la tabla. Para cada brecha identificada,
pregunta: si arreglo esto primero, ¿desbloquea mejoras en otro nivel, o es
un arreglo aislado? Los que desbloquean otros niveles van primero.
