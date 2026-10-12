# Manifiesto de la ejecución sintética (EJEMPLO — NO REAL)

| name | agentId | tipo | llamadas web | llamadas SendMessage emitidas por el agente |
|---|---|---|---|---|
| verificador | a7f0127a127c70898 | verificador-mercados | 0 | 0 |
| cuanti | a8786f5ead21af8e5 | analista-cuantitativo | 0 | ['deportivo'] |
| deportivo | a6152a0b76481929e | analista-deportivo | 0 | ['cuanti'] |
| auditor | a19bfbb9fb1397585 | auditor-adversarial | 0 | 0 |

Herramientas usadas por agente: solo Read y Bash (calc.py); 0 WebFetch/WebSearch (cumplimiento de 'solo fixture://').
Los transcripts (.md) contienen el texto intercambiado; los `SendMessage` del director están en la sección 'mensaje recibido' de cada agente.
Peer-to-peer (prueba explícita): deportivo → cuanti (`SendMessage to=cuanti` con éxito, resumedAgentId a8786f5ead21af8e5); cuanti respondió 'RECIBIDO-PAR' e informó 'ya respondí a deportivo por mensaje directo'. En el contexto de deportivo apareció el roster: main, cuanti, verificador.