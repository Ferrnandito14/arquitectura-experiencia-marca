/* Animaciones de las demos: entrada del titular palabra por palabra, secciones que aparecen al bajar,
   barra de progreso con el color de la marca, botones con respuesta al toque y pasos de la reserva con transición.
   Sin dependencias. Si la persona pide menos movimiento en su sistema, no anima nada.
   Opcional antes de cargar: window.VIDA = {caracter: 'firme' | 'suave' | 'calido'}. */
(function () {
  if (!window.matchMedia || matchMedia('(prefers-reduced-motion: reduce)').matches) return;
  if (!('IntersectionObserver' in window)) return;

  // Cada marca se mueve distinto: barberías con decisión, la clínica con calma, comida con algo de rebote.
  var CARACTER = {
    firme: { dur: 620, dist: 28, curva: 'cubic-bezier(.2,.8,.2,1)', paso: 70 },
    suave: { dur: 820, dist: 16, curva: 'cubic-bezier(.25,.6,.3,1)', paso: 90 },
    calido: { dur: 700, dist: 22, curva: 'cubic-bezier(.34,1.4,.64,1)', paso: 80 }
  };
  var c = CARACTER[(window.VIDA || {}).caracter] || CARACTER.firme;
  var raiz = document.documentElement;
  raiz.classList.add('vida');

  var css = '' +
    '.vida [data-v]{opacity:0;translate:0 ' + c.dist + 'px;transition:opacity ' + c.dur + 'ms ' + c.curva + ',translate ' + c.dur + 'ms ' + c.curva + ';transition-delay:var(--v-d,0ms)}' +
    '.vida [data-v].v-on{opacity:1;translate:0 0}' +
    '.vida h1 .v-pal{color:inherit;display:inline-block;opacity:0;translate:0 .45em;animation:v-sube ' + c.dur + 'ms ' + c.curva + ' forwards;animation-delay:var(--v-d,0ms)}' +
    '@keyframes v-sube{to{opacity:1;translate:0 0}}' +
    '.vida .btn{transition:transform 120ms ease-out,box-shadow 200ms ease-out,filter 200ms ease-out}' +
    '.vida .btn:hover{transform:translateY(-2px);filter:brightness(1.06)}' +
    '.vida .btn:active{transform:scale(.97)}' +
    '#v-barra{position:fixed;top:0;left:0;height:3px;width:100%;transform-origin:0 50%;scale:0 1;z-index:60;pointer-events:none}' +
    '#reserva-web .r-caja>*{animation:v-paso 360ms ' + c.curva + ' both}' +
    '#reserva-web .r-caja>*:nth-child(2){animation-delay:40ms}#reserva-web .r-caja>*:nth-child(3){animation-delay:80ms}#reserva-web .r-caja>*:nth-child(n+4){animation-delay:120ms}' +
    '@keyframes v-paso{from{opacity:0;translate:14px 0}to{opacity:1;translate:0 0}}';
  var st = document.createElement('style'); st.textContent = css; document.head.appendChild(st);

  // 1. Titular: cada palabra entra por separado (el texto sigue siendo el mismo para lectores de pantalla)
  var h1 = document.querySelector('h1');
  var t = 0;
  if (h1) {
    h1.setAttribute('aria-label', h1.textContent.replace(/\s+/g, ' ').trim());
    (function partir(nodo) {
      Array.prototype.slice.call(nodo.childNodes).forEach(function (n) {
        if (n.nodeType === 3) {
          var frag = document.createDocumentFragment();
          n.textContent.split(/(\s+)/).forEach(function (trozo) {
            if (!trozo) return;
            if (/^\s+$/.test(trozo)) { frag.appendChild(document.createTextNode(trozo)); return; }
            var s = document.createElement('span');
            s.className = 'v-pal'; s.setAttribute('aria-hidden', 'true'); s.textContent = trozo;
            s.style.setProperty('--v-d', (t++ * c.paso) + 'ms');
            frag.appendChild(s);
          });
          n.parentNode.replaceChild(frag, n);
        } else if (n.nodeType === 1) { partir(n); }
      });
    })(h1);
    // Lo que sigue al titular en la portada entra después de la última palabra
    var sig = h1.nextElementSibling, k = 0;
    while (sig) { sig.setAttribute('data-v', ''); sig.style.setProperty('--v-d', (t * c.paso + 120 + k++ * 110) + 'ms'); sig = sig.nextElementSibling; }
  }

  // 2. Secciones: título, entradilla y cada tarjeta o fila, en cascada
  var vistos = [];
  document.querySelectorAll('main section .wrap > *, footer .wrap > *').forEach(function (el) {
    if (el.id === 'reserva-web') return;
    var hijos = el.children;
    var esGrupo = hijos.length >= 2 && /grid|flex/.test(getComputedStyle(el).display) && !/^H\d$/.test(el.tagName);
    if (esGrupo) {
      Array.prototype.forEach.call(hijos, function (h, i) { h.setAttribute('data-v', ''); h.style.setProperty('--v-d', Math.min(i, 6) * c.paso + 'ms'); vistos.push(h); });
    } else { el.setAttribute('data-v', ''); vistos.push(el); }
  });
  var obs = new IntersectionObserver(function (entradas) {
    entradas.forEach(function (e) { if (e.isIntersecting) { e.target.classList.add('v-on'); obs.unobserve(e.target); } });
  }, { rootMargin: '0px 0px -8% 0px', threshold: 0.12 });
  vistos.forEach(function (el) { obs.observe(el); });
  // Respaldo: si el navegador no avisa (pestaña en segundo plano, saltos con enlaces), se revisa a mano
  // para que ningún contenido quede escondido.
  var espera = null;
  function revisar() {
    espera = null;
    vistos.forEach(function (el) {
      if (!el.classList.contains('v-on') && el.getBoundingClientRect().top < innerHeight * 0.95) { el.classList.add('v-on'); obs.unobserve(el); }
    });
  }
  addEventListener('scroll', function () { if (!espera) espera = setTimeout(revisar, 150); }, { passive: true });
  addEventListener('hashchange', function () { setTimeout(revisar, 300); });
  setTimeout(revisar, 400);
  // Portada: visible desde el inicio
  setTimeout(function () {
    document.querySelectorAll('header [data-v]').forEach(function (el) { el.classList.add('v-on'); });
  }, 30);

  // 3. Barra de progreso con el color del botón principal
  var btn = document.querySelector('.btn');
  var barra = document.createElement('div');
  barra.id = 'v-barra';
  barra.style.background = btn ? getComputedStyle(btn).backgroundColor : 'currentColor';
  document.body.appendChild(barra);
  var pendiente = false;
  addEventListener('scroll', function () {
    if (pendiente) return; pendiente = true;
    requestAnimationFrame(function () {
      var max = raiz.scrollHeight - innerHeight;
      barra.style.scale = (max > 0 ? Math.min(1, scrollY / max) : 0) + ' 1';
      pendiente = false;
    });
  }, { passive: true });
})();
