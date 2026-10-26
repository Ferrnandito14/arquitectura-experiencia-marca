# Contrato de salida — verificador (versión 1)

Devuelve UN archivo JSON: {"agente": "verificador", "version_contrato": 1, "run": "<run>", "unidades": [ … ], "limitaciones": ["…"]}.
Una entrada en `unidades` por CADA unit_id del paquete (partido|grupo). Campos permitidos por unidad (cualquier otro es inválido): disponibilidad, precio, discrepancias, fuentes_consultadas, nota, excepciones, evidencia, unit_id.

- `disponibilidad`: una de ['verificada_en_fuente', 'no_encontrada', 'no_ofrecida', 'no_verificable']
- `precio`: una de ['real_verificado', 'comunicado_usuario', 'referencia_agregador', 'sin_precio']
- `discrepancias`: lista con valores de ['ninguna', 'calendario', 'hora', 'identidad_partido', 'precio_anomalo', 'linea_distinta', 'mercado_mal_etiquetado', 'paquete_desactualizado_vs_fuente']
- `fuentes_consultadas`: lista de textos cortos (fuentes realmente consultadas)
- `nota`: texto ≤ 200 caracteres (puede ir vacío)
- `excepciones`: lista de {"entry_id": <`id` de UNA LÍNEA (entrada) de la unidad, no el id de la unidad>, "disponibilidad": <valor>} cuando esa línea difiere del veredicto de la unidad
- `evidencia`: lista NO vacía de referencias que empiecen por ['paquete:', 'apif_query:', 'archivo:', 'web:', 'cache:'] (p. ej. `paquete:<unit_id>`, `apif_query:get_events match_id=…`)

Reglas de coherencia (las comprueba el validador): no afirmes un precio real, un estimador, datos suficientes ni una validación que el paquete no tenga; si dudas, usa el valor conservador.
