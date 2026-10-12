#!/usr/bin/env bash
# Instalación PERSONAL opcional: copia agentes y skills a ~/.claude (disponibles en todos tus proyectos).
# El destino principal del sistema es el propio proyecto (.claude/ de este repo); esto es una operación distinta.
# Uso: ./install.sh [--dry-run] [--force] [--dest DIR]
set -euo pipefail
SRC="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/.claude"
DEST="${HOME}/.claude"; DRY=0; FORCE=0
while [ $# -gt 0 ]; do
  case "$1" in
    --dry-run) DRY=1 ;; --force) FORCE=1 ;;
    --dest) DEST="${2:?falta DIR}"; shift ;;
    -h|--help) sed -n '2,5p' "$0"; exit 0 ;;
    *) echo "argumento desconocido: $1" >&2; exit 2 ;;
  esac; shift
done
[ -d "$SRC/agents" ] && [ -d "$SRC/skills" ] || { echo "error: no encuentro $SRC/agents ni skills" >&2; exit 2; }
n=0; skipped=0
while IFS= read -r -d '' f; do
  rel="${f#"$SRC"/}"; dst="$DEST/$rel"
  if [ -e "$dst" ] && cmp -s "$f" "$dst"; then echo "= igual      $dst"; continue; fi
  if [ -e "$dst" ] && [ "$FORCE" -eq 0 ]; then echo "! EXISTE     $dst (usa --force para sobrescribir)"; skipped=$((skipped+1)); continue; fi
  if [ -e "$dst" ]; then act="SOBRESCRIBIR"; else act="CREAR"; fi
  echo "+ $act  $dst"; n=$((n+1))
  if [ "$DRY" -eq 0 ]; then mkdir -p "$(dirname "$dst")"; [ -e "$dst" ] && cp -p "$dst" "$dst.bak.$(date +%Y%m%d%H%M%S)"; cp -p "$f" "$dst"; fi
done < <(find "$SRC/agents" "$SRC/skills" -type f -print0 | sort -z)
[ "$DRY" -eq 1 ] && echo "(dry-run: no se modificó nada)"
echo "cambios: $n   omitidos por existir: $skipped   destino: $DEST"
[ "$skipped" -eq 0 ] || exit 1
