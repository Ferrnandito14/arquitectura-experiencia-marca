# Prototipo de reels con Remotion (no conectado a la producción)

Prueba del 2026-10-25. Reel animado del hámster con voz y música.

- `src/HamsterReel.tsx`: el reel. Texto palabra por palabra sincronizado con cada frase, sello que cae, globos de diálogo y la boca del hámster que se abre según el volumen de la voz.
- `voz/narrar.ps1`: graba la narración con la voz "Microsoft Pablo" de Windows (sin servicios externos ni claves). Luego se recorta, se sube un poco el tono para el hámster y se calculan los tiempos de cada frase (`src/tiempos.json`).
- Música: original, generada con código (progresión suave a 96 pulsaciones por minuto), sin derechos de terceros. Va a 0,16 de volumen, unos 8 dB por debajo de la voz.
- Render: `npm install --ignore-scripts` y luego `npx remotion render src/index.ts HamsterReel out/reel.mp4`. La primera vez descarga un Chrome sin interfaz (unos 120 MB). No se pasa clave de licencia, así que no envía datos de uso.

Pendiente antes de usarlo en la producción diaria:
1. La voz "Pablo" tiene acento de España. Las reglas piden español neutro: decidir si se acepta o se busca otra voz.
2. Que la sesión de la nube pueda instalar paquetes de npm y descargar el navegador.
3. Convertirlo en plantilla: que reciba el guion y genere voz, tiempos y video solo.
