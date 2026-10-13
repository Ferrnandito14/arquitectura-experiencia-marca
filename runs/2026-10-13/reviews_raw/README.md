# reviews_raw — revisiones tal como las entregaron los agentes (ronda 1)
- `verif3.md`, `depor3.md`, `cuanti3.md`: texto final de cada agente, SIN editar.
- `rows_original_ids.json`: sus filas JSON con los `match_id` **anteriores** a la corrección de IDs.
- `id_map_before_fix.json`: mapa id antiguo → (equipos, fecha local, categoría).
Estas revisiones se hicieron sobre la matriz previa a las correcciones: sus hallazgos (sources_checked engañoso, NO_EVALUABLE vs NOT_CHECKED, categorías, sincronía inventario/estado, estadísticas INSUFICIENTES vs NOT_CHECKED, estado de análisis sin intentos reales) ya están aplicados en el código y regenerados (`previous_run_pre_fix*/` conserva las versiones anteriores). Las filas se re-asignaron a los IDs/lotes vigentes con `batches.py rebatch`; sus textos «NO_EVALUABLE_TRAS_INTENTOS»/«23 mercados NO_EVALUABLE» describen el estado anterior.
