# Proceso de diseño de una página

Paso obligatorio antes de diseñar o rediseñar una página para un negocio. Sale del reel de soyenriquerocha ("Diseña páginas web BIEN con Claude", 2026-10-25): darle a Claude un sistema de diseño real como referencia en vez de pedirle "una web bonita". La meta: que cada página sea útil y, además, se sienta propia del negocio y viva.

## 1. Identidad del negocio (ya lo hacíamos)

Fotos, reseñas y ficha de Google Maps, Instagram del local, colores y letras de su letrero. Sin esto no se empieza.

## 2. Referencias de diseño (nuevo)

Buscar entre 3 y 5 páginas de referencia antes de escribir código. Se usan para decidir la dirección, nunca para copiar una.

| Sitio | Para qué sirve |
|---|---|
| [Refero Styles](https://styles.refero.design) | Biblioteca de sistemas de diseño sacados de webs reales, cada uno con su DESIGN.md (colores, tipografía, espaciado, componentes y reglas). Es la referencia principal: el DESIGN.md se le da a Claude tal cual |
| [Godly](https://godly.website) | Webs con animación y movimiento. Para decidir cómo se mueve la página |
| [Awwwards](https://www.awwwards.com) | Webs premiadas. Buscar por sector (restaurant, barber, dental, bakery) |
| [One Page Love](https://onepagelove.com) | Páginas de una sola pantalla, el mismo formato de nuestras demos |
| [Land-book](https://land-book.com), [Lapa Ninja](https://www.lapa.ninja), [SiteInspire](https://www.siteinspire.com), [CSS Design Awards](https://www.cssdesignawards.com) | Galerías para ampliar la búsqueda por estilo o sector |

Cómo se usan:
1. Buscar por sector y por el carácter del negocio (por ejemplo "barbería clásica", "clínica cercana", "panadería de barrio con tradición").
2. Elegir una referencia dominante y como mucho dos secundarias para detalles. No promediar estilos.
3. Anotar en el encabezado de la demo, en un comentario, qué se tomó de cada referencia (tipografía, ritmo, tipo de animación).
4. Los colores y las letras salen del negocio (paso 1). De la referencia se toma la estructura, el ritmo y el movimiento.

La skill `refero-design` (`.claude/skills/refero-design`) trae la metodología completa: investigar, fijar referencias, decidir y luego construir. Su conector en vivo (Refero MCP) es de pago y no está conectado; las galerías de arriba se consultan con el navegador.

## 2b. Pasada obligatoria por las skills de diseño (antes de escribir CSS)

Fernando lo pidió el 2026-10-26, después de que Cakevana's saliera con una letra infantil elegida a ojo. Ninguna página se muestra sin esto:

1. `refero-design`: armar el "candado de referencia" (una referencia principal, 1 o 2 detalles prestados, qué se descarta) con estilos reales de [Refero Styles](https://styles.refero.design) buscados por sector.
2. `ui-ux-pro-max`: `search.py "<sector>" --design-system` y `--domain typography` para ver qué pareja de letras propone y para qué tipo de producto está pensada cada una. Si una letra aparece "para apps infantiles", no va en un negocio adulto.
3. Comparar la letra con el logo real del negocio (ampliado). La letra del titular tiene que parecerse en ancho, contraste y forma.
4. Revisar con `refero-design/references/anti-ai-slop.md`: nada de palabra suelta en otro color o cursiva dentro del titular, como mucho dos familias de letra, y sin crema y dorado por defecto si la marca no los usa.
5. Anotar en el comentario `Referencias` del `<head>` qué se tomó de cada referencia y qué se descartó.

## 3. Movimiento con carácter

Cada demo carga `reserva/vida.js` (lo aplica `reserva/aplicar_vida.py`):
- El titular entra palabra por palabra y luego el resto de la portada.
- Las secciones aparecen en cascada al bajar.
- Barra de progreso arriba con el color del botón principal.
- Botones que responden al pasar el cursor y al tocarlos.
- Transición entre los pasos de la reserva.

El ritmo cambia según el negocio (`window.VIDA = {caracter: ...}`):
- `firme`: barberías. Movimiento corto y decidido.
- `suave`: clínica y restaurante elegante. Más lento y con menos recorrido.
- `calido`: comida. Con un pequeño rebote.

Reglas (de la guía de movimiento de `refero-design`):
- Si una animación no da respuesta, continuidad o jerarquía, sobra.
- Si la persona pidió menos movimiento en su teléfono, no se anima nada.
- Nunca esconder contenido sin un respaldo que lo muestre.
- Sin librerías: la demo sigue siendo un solo archivo HTML.

Para algo más elaborado en una página vendida (texto que se arma al bajar, galerías con arrastre): GSAP ([gsap.com](https://gsap.com)) o Motion ([motion.dev](https://motion.dev)), cargados desde cdnjs con versión fija. La skill `ui-ux-pro-max` trae ejemplos listos de GSAP (`--domain gsap`).

## 4. Revisión antes de publicar

La lista del punto 11 de `modelo-de-venta.md`.
