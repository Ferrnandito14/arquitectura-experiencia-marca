# Cómo enseñar, vender y mantener las páginas sin perder el trabajo

Borrador para Fernando. No es asesoría legal: el contrato final conviene que lo revise un abogado.

## La idea central

Lo que se vende no es el archivo HTML: es la página terminada (con sus fotos, precios y número), publicada en su dominio, y el mantenimiento mes a mes. Una página publicada en internet siempre se puede copiar; no existe una forma técnica de impedirlo del todo. La protección real es no entregar nada terminado antes de cobrar y que el valor esté en el servicio.

## 1. Antes de que paguen: enseñar sin regalar

1. Primer mensaje: solo la imagen (`vista-telefono.png`). No el archivo ni el código.
2. Si quieren probarla en el teléfono: un enlace temporal en una cuenta de alojamiento de Fernando, nunca el archivo.
   - Dirección de Fernando, no del negocio (por ejemplo `hermanos-mora.tumarca.com`).
   - Franja fija que diga "Propuesta de diseño. No es el sitio oficial".
   - Sin número de WhatsApp real, sin fotos del negocio, precios "por confirmar". Así la demo no sirve como página final aunque la copien.
   - `noindex` (no sale en buscadores) y se baja a los 7 días o si dicen que no.
3. Nunca mandar el `.html`, un `.zip` ni acceso a la cuenta de alojamiento antes del pago.

## 2. Al vender: acuerdo por escrito

Un acuerdo corto (puede ser un PDF firmado o aceptado por WhatsApp) que diga:

- Qué se entrega: la página, cuántas secciones, cuántas rondas de cambios.
- Precio y forma de pago: anticipo antes de empezar a personalizar y el resto al publicar. Los montos los define Fernando.
- Plazo de entrega.
- Plan mensual de mantenimiento: qué incluye (cambios de precios, horarios y fotos, copias de seguridad, alojamiento, revisión de que todo funcione) y qué no incluye (páginas nuevas, tienda en línea), con su precio.
- Qué pasa si cancelan el plan (ver punto 3).

## 3. Quién es dueño de qué

Las guías del sector coinciden: el dominio debe quedar a nombre del negocio. Retener el dominio para obligar a pagar se considera mala práctica y daña la reputación. Propuesta:

| Pieza | A nombre de | Por qué |
|---|---|---|
| Dominio (`barberiahermanosmora.com`) | El negocio, con Fernando como administrador | Es su marca. Si se van, se lo llevan sin pelea. |
| Alojamiento | Cuenta de Fernando | Lo incluye el plan mensual. |
| Diseño y código | Fernando, con licencia de uso para el negocio mientras pague el plan | Es el trabajo de Fernando. |
| Textos, fotos, logo | El negocio | Son suyos. |

Si el negocio cancela el plan, dos opciones fijadas desde el principio en el acuerdo:
- comprar los archivos de la página por un monto acordado de antemano y llevársela, o
- se baja la página y conservan su dominio, textos y fotos.

Así el negocio sabe desde el inicio que no queda atrapado, y Fernando no regala el trabajo.

## 4. Cómo se monta (técnico)

- Una cuenta de alojamiento estático gratuita a nombre de Fernando, con un proyecto por cliente.
- Un dominio propio de Fernando para las demos y para presentarse como servicio.
- Código en el repo de Fernando (privado). El cliente nunca recibe acceso al repo.
- Las claves de acceso no se guardan en el repo ni se envían por chat.

## Lista de entrega de una página vendida

Sale de las preguntas que más se repiten cuando alguien vende webs con IA (comentarios del reel de idanbuild, 2026-10-25). Una página vendida no se entrega sin esto:

1. Dominio a nombre del cliente y DNS configurado (Fernando como administrador).
2. Alojamiento en la cuenta de Fernando, con HTTPS.
3. Quitar `noindex` y la franja de propuesta; poner el número real de WhatsApp.
4. Datos estructurados `LocalBusiness` (nombre, dirección, horario, teléfono) para que Google entienda el negocio.
5. `sitemap.xml` y verificación en Google Search Console; confirmar que la página queda indexada.
6. Enlace desde la ficha de Google Maps del negocio a la página (lo hace el dueño o con su acceso).
7. Textos, precios y fotos aprobados por escrito por el cliente.
8. Reserva o pedido en línea conectado de verdad: en las demos el formulario no envía nada. En la página vendida se conecta a un servicio que guarde las solicitudes y avise al negocio (por ejemplo, el formulario de Netlify con aviso por correo, o una agenda en línea). Se le dice al cliente qué datos se piden (nombre y WhatsApp), para qué se usan y quién los ve.
9. Cómo pide cambios el cliente (WhatsApp) y en cuánto tiempo se hacen, según el plan.
10. Copia de seguridad del sitio.

Fuera del precio de lanzamiento: blog, tienda, formularios con base de datos y automatizaciones. Se cotizan aparte.

## 5. Mantenimiento

- Cambios pedidos por WhatsApp, con un tiempo de respuesta acordado.
- Revisión mensual: que los botones funcionen, que el horario y los precios estén al día, copia de seguridad.
- Un resumen corto cada mes al cliente con lo que se hizo.

## Precios decididos (2026-10-24)

| Concepto | Precio | Cómo se cobra |
|---|---|---|
| Página personalizada (precio de lanzamiento, primeros clientes) | $130 | $65 de anticipo para empezar a personalizar, $65 al publicar |
| Plan mensual | $20 al mes | Alojamiento, cambios de precios, horarios y fotos, revisión mensual y copia de seguridad |
| Dominio `.com` | Lo paga el negocio (unos $10 a $15 al año) | A nombre del negocio |

A cambio del precio de lanzamiento se pide por escrito: permiso para mostrar la página como ejemplo y una opinión breve del dueño al publicarla.

Referencia de mercado (agencias en Venezuela, 2026): landing de $80 a $500, mantenimiento de pymes de $25 a $75 al mes.

## Cómo se presenta

Como Fernando Romero, persona y no empresa: da más confianza mientras el servicio empieza. Las demos llevan una franja fija "Propuesta de diseño · Fernando Romero" y el aviso al pie. El nombre "Nodo Caracas" (`nodocaracas.com`) queda como opción para más adelante.
