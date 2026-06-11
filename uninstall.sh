#!/usr/bin/env bash
set -euo pipefail

CODEX_HOME="${CODEX_HOME:-$HOME/.codex}"
TARGET_DIR="$CODEX_HOME/pets/mojo-carrot"

if [[ -d "$TARGET_DIR" ]]; then
  rm -rf "$TARGET_DIR"
  echo "Removed: $TARGET_DIR"
else
  echo "Nothing to remove: $TARGET_DIR"
fi

echo "If your config still selects custom:mojo-carrot, choose another pet in Codex or edit $CODEX_HOME/config.toml."
