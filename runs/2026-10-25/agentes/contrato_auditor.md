# Contrato de salida — auditor (versión 1)

Devuelve UN archivo JSON: {"agente": "auditor", "version_contrato": 1, "run": "<run>", "unidades": [ … ], "limitaciones": ["…"]}.
Una entrada en `unidades` por CADA unit_id del paquete (partido|grupo). Campos permitidos por unidad (cualquier otro es inválido): objecion, severidad, recomendacion, nota, excepciones, evidencia, objeciones_a_agentes, unit_id.

- `objecion`: una de ['ninguna', 'muestra_debil', 'brecha_muestra_mercado', 'rotacion_no_cuantificada', 'fuente_unica', 'dato_defectuoso', 'correlacion', 'cuota_no_ejecutable', 'estimador_sin_validar']
- `severidad`: una de ['baja', 'media', 'alta']
- `recomendacion`: una de ['mantener', 'degradar', 'descartar_de_rankings', 'verificar_manualmente']
- `nota`: texto ≤ 200 caracteres (puede ir vacío)
- `excepciones`: lista de {"entry_id": <`id` de UNA LÍNEA (entrada) de la unidad, no el id de la unidad>, "objecion": <valor>} cuando esa línea difiere del veredicto de la unidad
- `evidencia`: lista NO vacía de referencias que empiecen por ['paquete:', 'apif_query:', 'archivo:', 'web:', 'cache:'] (p. ej. `paquete:<unit_id>`, `apif_query:get_events match_id=…`)

Reglas de coherencia (las comprueba el validador): no afirmes un precio real, un estimador, datos suficientes ni una validación que el paquete no tenga; si dudas, usa el valor conservador.
- Muestra mínima del auditor: TODAS las unidades que otro agente marque con solidez BAJA, discrepancia o mercado no verificable, más al menos max(10, 20 % de las unidades restantes) con al menos una unidad de cada grupo de mercado presente (política declarada, no un hecho estadístico).
- `objeciones_a_agentes` (OPCIONAL; omítelo o déjalo vacío si no hay): lista de {"entry_id": <id de línea de la unidad o null si afecta a toda la unidad>, "agente": una de ['verificador', 'deportivo', 'cuantitativo'], "campo": <campo del contrato de ese agente>, "problema": uno de ['valor_contradice_paquete', 'valor_contradice_fuente', 'afirmacion_sin_evidencia', 'omision', 'dato_citado_incorrecto']}. Úsalo cuando el valor de otro agente contradice el paquete o la fuente; la explicación va en `nota` y la prueba en `evidencia`.
