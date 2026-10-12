# Instalación

## Destino principal: el proyecto (decidido)
Los agentes y skills viven en `.claude/` de este repo y están activos al abrir Claude Code en esta carpeta:
```
cd /ruta/a/football-picks-system && claude
```
Verifica con `claude agents --json` (4 agentes) o preguntando por las skills de proyecto. Requiere Claude Code ≥ 2.1.206 para el roster entre agentes; probado en 2.1.296. Python 3 para `calc.py`.

## Opcional: instalación personal (`~/.claude`)
Operación distinta, solo si quieres el sistema disponible en todos tus proyectos (se cargarán también en proyectos que no son de fútbol):
```
./install.sh --dry-run          # muestra exactamente qué cambiaría
./install.sh                    # crea lo que no exista; NO sobrescribe archivos distintos
./install.sh --force            # sobrescribe (deja copia .bak.<fecha>)
./install.sh --dest /otra/ruta  # otro destino
```
No se copia ningún `settings.local.json` ni configuración de otros proyectos. No duplica entre destinos automáticamente.

## Entregables de `dist/`
`football-picks-system-v2.zip` (+ `SHA256SUMS`), `v1-to-v2.patch` (aplicable con `git am` sobre el commit "Import existing football picks system v1"), `full-from-empty.patch`. Para restaurar sin git: descomprime el ZIP y copia `.claude/` a tu proyecto.
