#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CODEX_HOME="${CODEX_HOME:-$HOME/.codex}"
PETS_DIR="$CODEX_HOME/pets"
TARGET_DIR="$PETS_DIR/mojo-carrot"

mkdir -p "$PETS_DIR"
rm -rf "$TARGET_DIR"
cp -R "$SCRIPT_DIR/mojo-carrot" "$TARGET_DIR"

echo "Installed MOJO Carrot pet to: $TARGET_DIR"
echo
echo "To enable it, set this in $CODEX_HOME/config.toml:"
echo 'selected-avatar-id = "custom:mojo-carrot"'
echo
echo "Restart Codex Desktop if the pet does not refresh immediately."
