# Contrato de salida — cuantitativo (versión 1)

Devuelve UN archivo JSON: {"agente": "cuantitativo", "version_contrato": 1, "run": "<run>", "unidades": [ … ], "limitaciones": ["…"]}.
Una entrada en `unidades` por CADA unit_id del paquete (partido|grupo). Campos permitidos por unidad (cualquier otro es inválido): consistencia_modelo, riesgo_correlacion, validacion_aplicable, nota, excepciones, evidencia, unit_id.

- `consistencia_modelo`: una de ['coherente', 'discrepa_del_mercado', 'datos_insuficientes', 'sin_precio_para_contrastar', 'defecto_del_modelo', 'sin_estimador']
- `riesgo_correlacion`: una de ['ninguno', 'misma_direccion', 'mismo_partido', 'mismo_equipo_en_otras_patas']
- `validacion_aplicable`: una de ['no_validado', 'parcial', 'validado']
- `nota`: texto ≤ 200 caracteres (puede ir vacío)
- `excepciones`: lista de {"entry_id": <`id` de UNA LÍNEA (entrada) de la unidad, no el id de la unidad>, "consistencia_modelo": <valor>} cuando esa línea difiere del veredicto de la unidad
- `evidencia`: lista NO vacía de referencias que empiecen por ['paquete:', 'apif_query:', 'archivo:', 'web:', 'cache:'] (p. ej. `paquete:<unit_id>`, `apif_query:get_events match_id=…`)

Reglas de coherencia (las comprueba el validador): no afirmes un precio real, un estimador, datos suficientes ni una validación que el paquete no tenga; si dudas, usa el valor conservador.
