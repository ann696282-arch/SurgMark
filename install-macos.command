#!/bin/sh
set -eu
BASE=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
SOURCE="$BASE/SurgMark-ESD"
DESTINATION="${SURGMARK_INSTALL_DIR:-$HOME/Applications/SurgMark-ESD}"
if [ ! -f "$SOURCE/index.html" ]; then
  echo 'Extract the entire ZIP before installing.'
  exit 1
fi
mkdir -p "$DESTINATION"
cp -R "$SOURCE/." "$DESTINATION/"
chmod +x "$DESTINATION/Start-SurgMark.command"
printf 'Installed: %s\nOpen Start-SurgMark.command or index.html.\n' "$DESTINATION"
if [ "${SURGMARK_NO_OPEN:-0}" != 1 ]; then
  open "$DESTINATION/index.html"
fi
