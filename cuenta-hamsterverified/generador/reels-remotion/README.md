# Reels "El hámster responde" con Remotion

Plantilla aprobada por Fernando el 2026-10-25. Un guion en JSON se convierte en un reel vertical de unos 11 a 15 segundos: el hámster lee una pregunta común con su voz, responde en una frase, da un consejo y cierra con "Palabra de hámster". Lleva música original de fondo.

## Uso

```
python hacer_reel.py guiones/d3-responde-postergar.json out/d3-responde-postergar.mp4
```

La primera vez instala las dependencias (`npm install --ignore-scripts`) y Remotion descarga un Chrome sin interfaz (unos 120 MB). Después, cada reel tarda menos de dos minutos.

## Guion

```json
{
 "id": "d3-responde-postergar",
 "pregunta": "¿Cómo dejo de postergar?",
 "titular": "Empieza dos minutos.",
 "destacar": ["dos"],
 "consejo": "Casi siempre, seguir cuesta menos que empezar."
}
```

Opcionales: `puente` ("Te lo explico en una línea."), `cierre` ("Palabra de hámster."), `sello` (por defecto ninguno; solo para datos verificables), `serie` ("El hámster responde").

Reglas del contenido (ver `../../REGLAS.md`):
- La pregunta es una duda frecuente y genérica. En pantalla dice "Pregunta común" y nunca se atribuye a una persona ni se presenta como mensaje recibido.
- Nada de consejos médicos, legales o de inversión concretos.
- Frases cortas: el titular se lee en un vistazo y el consejo cabe en tres líneas.

## Qué hace `hacer_reel.py`

1. Graba cada frase con la voz "Microsoft Pablo" de Windows (`voz/narrar.ps1`), sin servicios externos ni claves.
2. Recorta silencios, une las frases con pausas y calcula cuándo empieza cada una. Sube un poco el tono para el hámster.
3. Genera música original con código (acordes suaves, bajo, bombo y shaker a 96 pulsaciones por minuto). La tonalidad cambia según el `id`, para que no todos los reels suenen igual. Va unos 8 dB por debajo de la voz.
4. Renderiza `src/HamsterResponde.tsx` con esos tiempos: texto palabra por palabra sincronizado con la voz, globos de diálogo, la boca del hámster según el volumen y todo dentro de la zona segura de Instagram (250 px arriba, 500 px abajo).
5. Deja el MP4 (H.264 + AAC, 1080x1920, 30 fps) listo para subir.

## Voz

Por defecto usa "Microsoft Pablo" de Windows (acento de España, aprobada por Fernando).

En prueba desde el 2026-10-26: Piper, una voz sin conexión que funciona en Windows y en Linux. Si Fernando la aprueba, la sesión de la nube también podría hacer estos reels con voz.

```
pip install piper-tts==1.8.0
HAMSTER_VOZ=piper:ruta/a/es_MX-ald-medium.onnx python hacer_reel.py guiones/mi-guion.json out/mi-reel.mp4
```

- `HAMSTER_PIPER_PYTHON`: la Python que tiene `piper-tts`, si no es la misma que ejecuta el script.
- `HAMSTER_PIPER_RITMO`: velocidad (por defecto 0.85; menos es más rápido).
- Las voces (`.onnx` y `.onnx.json`) se descargan de https://huggingface.co/rhasspy/piper-voices y no se suben al repo (pesan unos 60 MB cada una). Probadas: `es_MX-ald-medium` (datos de entrenamiento Unlicense), `es_MX-claude-high` (Apache 2.0) y `es_ES-davefx-medium` (CC0).
- piper-tts tiene licencia GPL 3.0: se usa como herramienta, no se copia su código al repo.
- En la Dell, la Python de Inkscape no sirve para Piper (no hay paquetes de onnxruntime para ella). Se usó una Python 3.12 oficial portátil de python.org.
- Muestras para comparar, con el mismo texto: `../../media/prototipos/voces/` (`*-natural.mp3` sin el tono del hámster).

## Límites

- Con la voz por defecto necesita Windows.
- La sesión de la nube todavía no lo ha probado: falta comprobar que pueda instalar Remotion y Piper. Por ahora estos reels se hacen desde la Dell.
- Remotion es gratis para personas y equipos de hasta 3 personas. No se pasa clave de licencia, así que no envía datos de uso.
