# Traspaso del notificador de partidos por correo (20-oct-2026, hora de Caracas)

Qué es: NO es un servicio. Son tres piezas que se ejecutan dentro de un chat de Claude Code:
1. `vivo.py` (consulta apifootball cada 90 s y guarda `runs/<fecha>/seguimiento/vivo_estado.json`).
2. `estado_tickets.py` (probabilidad por pata y por ticket con el marcador en vivo; usa el libro `dist/ligas-<día>-oct-v3.xlsx` y `seguimiento/tickets_abiertos.json`).
3. Un monitor (patrón de `mon19.py`, que se rearma cada 30 min) que corre `estado_tickets.py` y avisa cuando cambia un marcador, el estado de una pata o una P se mueve ≥10 pp, más un recordatorio cada 20 min. El correo lo envía Claude con el conector Gmail a barcaferr14@gmail.com.
`seguimiento.py` liquida patas terminadas y escribe `registro_resultados.jsonl`.

Qué necesita el chat nuevo
- Este código (zip adjunto, sin claves). Carpeta de trabajo: `football-picks-system/`.
- Clave de apifootball en un archivo y la variable `APIFOOTBALL_KEY_FILE` apuntando a él. Regenerar la clave antigua (se expuso en el chat) y guardar la nueva solo en ese archivo, nunca en el repo ni impresa.
- Conector Gmail activo en el chat nuevo.
- `runs/<fecha>/seguimiento/tickets_abiertos.json` del día (patas, cuotas, montos). Hoy 20-oct aún no existe: se crea con los boletos que Fernando juegue (formato del 19-oct en `runs/2026-10-19/seguimiento/`).

Pasos
1. `export APIFOOTBALL_KEY_FILE=<ruta>` y `python3 .claude/skills/seleccion-final-picks/scripts/vivo.py --run runs/2026-10-20 --every 90` en segundo plano (ver `runs/2026-10-19/seguimiento/run_vivo19.sh`: reintenta si cae).
2. Monitor: copiar `mon19.py`, cambiar `--run`, `--book` y `START` a la fecha; correr con Monitor y volver a armarlo cada 30 min.
3. Al cierre: `seguimiento.py --run runs/<fecha>` y `registrar_tickets.py` solo con boletos que Fernando indique.

Reglas que se mantienen
- Horas siempre en Caracas. Nunca decir «no apostar» ni llamar seguro a un pick. Cuotas de API = referencia.
- Los tres boletos de balance del 18-oct NO se registran en el historial.
- Si un marcador de la API cambia y revierte, verificar con la API antes de afirmar un gol anulado.
- No imprimir ni guardar claves. Correos solo a barcaferr14@gmail.com.
