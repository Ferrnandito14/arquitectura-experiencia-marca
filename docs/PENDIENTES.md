
## Regla de la persona usuaria (21-oct-2026) — copas cortas y torneos continentales
En copas cortas y torneos continentales (Copa Venezuela, Copa Colombia, CAF Champions League, AFC Challenge League, Champions League, etc.) la evidencia de historial se saca de los enfrentamientos pasados (H2H) y de las ligas domésticas de cada equipo, no solo de la misma competición (muestra pequeña).
- Herramienta: `contexto_continental.py --run runs/<fecha>` (después de `rotation_prior.py`); es referencia descriptiva, no cambia `p_modelo` ni introduce pesos.
- Se omitió en los runs del 20-oct y del 21-oct. Está PENDIENTE correrla y relanzar solo deportivo, cuantitativo y auditor de los partidos de copa/continentales (por ejemplo Barranquilla–América de Cali, 15 de Agosto–Simba, Young Africans–CFFA, que salieron sin `p_modelo`).
- Desde ahora, incluirla en `prep.sh` de cada día. No ejecutarla sin aviso: la persona usuaria pidió ahorrar tokens y lo hará cuando lo indique.

## Formato de entregables (31-oct-2026)
Fernando pidió que, desde ahora, los entregables sean **página web** (Artifact HTML), no Excel. Generador: `build_retos_web.py` + `retos_web_plantilla.html` → `dist/retos-del-dia.html`; se publica el mismo artefacto cada día (misma URL, título «Retos del Día»). Los libros `.xlsx` de ligas quedan como histórico; no se generan nuevos salvo petición.
