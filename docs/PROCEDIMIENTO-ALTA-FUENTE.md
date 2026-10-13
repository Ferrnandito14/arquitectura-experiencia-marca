# Procedimiento para dar de alta una fuente (de «NO REVISADA ⇒ denegada» a «condicional/permitida»)

Una fuente solo entra en `.claude/skills/seleccion-final-picks/scripts/sources_policy.json` tras estos pasos. Se hacen **leyendo** (una persona o un agente con lecturas puntuales), no con rastreo. Si falla el paso 1 o el 2, la fuente queda **excluida**. Esto no es asesoría legal: lo valida quien decide la política.

1. **robots.txt** del host (con UA `football-picks-system/0.1`): anotar `Disallow` que afecten a las rutas que se usarían (calendarios, fichas, estadísticas). Un desafío anti-bot ya en `robots.txt` ⇒ excluida; no se evade.
2. **Condiciones de uso / política de datos** enlazadas desde el sitio: buscar cláusulas sobre bots, scraping, agregación, extracción sistemática, uso comercial o de IA. Guardar la cita literal.
3. **API oficial o licencia de datos**: ¿existe?, ¿requiere clave o acuerdo escrito? Si existe, es la vía preferente (la persona usuaria aporta la clave o el permiso; el sistema nunca lo gestiona por su cuenta).
4. **Anti-bot**: si responde con CAPTCHA/Cloudflare, registrar «excluida» con la evidencia (código y título de la respuesta).
5. **Prueba mínima de ruta**: una petición por ruta concreta, con UA honesto, comprobando que devuelve contenido real (no un shell JS) y qué datos aporta realmente (forma, bajas, alineaciones, córners…), no solo el calendario.
6. **Límites**: rutas permitidas, pausa mínima entre peticiones, tope de descargas por ejecución, uso privado/no comercial si aplica.
7. **Registro**: añadir el proveedor a `sources_policy.json` (estado, hosts, motivo, evidencia, límites, `reliability`, `independence_group`) y a `docs/FUENTES-CONFORMIDAD.md`; añadir/ajustar el adaptador en `adapters.py` y sus tests offline.
8. **Independencia**: declarar de qué proveedor de datos deriva (varias webs pueden compartir feed); dos fuentes que comparten feed no cuentan como dos para confirmar.

## Pendientes de revisión (candidatas para cubrir lo que hoy falta)
| Competición / necesidad | Candidata | Estado |
|---|---|---|
| UEFA Champions League, UEFA Youth League | uefa.com (oficial) y comunicados de clubes | NO REVISADA |
| AFC Champions League Elite | the-afc.com (oficial) | NO REVISADA |
| Liga Revelação U23 | Liga Portugal / FPF (oficial) | NO REVISADA (Liga Portugal: `robots.txt` sin restricciones; términos sin revisar) |
| Calendarios generales | Flashscore, Soccerway, SofaScore, OddsPortal, worldfootball.net | NO REVISADAS (varias son solo JS o con anti-bot) |
| Estadísticas | FootyStats, FBref, RefsRadar, OddAlerts | NO REVISADAS (FootyStats/FBref respondieron con anti-bot en una fase previa) |
| Cualquier competición | API deportiva con licencia (clave de la persona usuaria) o CSV/JSON aportado con `inventory.py --manual` | Vía recomendada para cobertura exhaustiva |
