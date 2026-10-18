# Contrato de salida — deportivo (versión 1)

Devuelve UN archivo JSON: {"agente": "deportivo", "version_contrato": 1, "run": "<run>", "unidades": [ … ], "limitaciones": ["…"]}.
Una entrada en `unidades` por CADA unit_id del paquete (partido|grupo). Campos permitidos por unidad (cualquier otro es inválido): solidez, factor_principal, direccion_favorable, escenario_perdida, nota, excepciones, evidencia, unit_id.

- `solidez`: una de ['ALTA', 'MEDIA', 'BAJA', 'NO_EVALUABLE']
- `factor_principal`: una de ['forma', 'localia', 'rotacion', 'calendario_descanso', 'bajas_alineaciones', 'arbitro', 'estilo_ritmo', 'muestra_insuficiente', 'contexto_competicion']
- `direccion_favorable`: una de ['over', 'under', 'local', 'empate', 'visitante', 'sin_sesgo']
- `escenario_perdida`: una de ['goleada_local', 'goleada_visitante', 'partido_cerrado', 'partido_abierto', 'rotacion_inesperada', 'tarjetas_atipicas', 'penal_o_expulsion', 'sin_escenario_definido']
- `nota`: texto ≤ 200 caracteres (puede ir vacío)
- `excepciones`: lista de {"entry_id": <`id` de UNA LÍNEA (entrada) de la unidad, no el id de la unidad>, "solidez": <valor>} cuando esa línea difiere del veredicto de la unidad
- `evidencia`: lista NO vacía de referencias que empiecen por ['paquete:', 'apif_query:', 'archivo:', 'web:', 'cache:'] (p. ej. `paquete:<unit_id>`, `apif_query:get_events match_id=…`)

Reglas de coherencia (las comprueba el validador): no afirmes un precio real, un estimador, datos suficientes ni una validación que el paquete no tenga; si dudas, usa el valor conservador.
