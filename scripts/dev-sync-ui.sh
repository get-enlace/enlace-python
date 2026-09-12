#!/usr/bin/env bash
# Builds @get-enlace/ui locally and copies its dist/ output into a given
# package's src/<import_pkg>/ui_embedded/, so you can sanity-check the real
# embedded-package-data path before a release without going through the npm
# registry. Generalized over packages/* (unlike enlace-dotnet/enlace-java,
# which are single-package repos and hardcode one destination) since this
# repo adds a new adapter package per framework (enlace-fastapi today,
# enlace-flask etc. later) that all need the identical embedding step.
#
# Usage: scripts/dev-sync-ui.sh <package-dir> [path-to-enlace-ui-checkout]
#   package-dir is a directory name under packages/, e.g. enlace-fastapi.

set -euo pipefail

PACKAGE_DIR="${1:?usage: dev-sync-ui.sh <package-dir> [path-to-enlace-ui-checkout]}"
UI_DIR="${2:-../enlace-ui}"
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PKG_ROOT="$REPO_ROOT/packages/$PACKAGE_DIR"

if [[ ! -d "$PKG_ROOT" ]]; then
  echo "error: no such package 'packages/$PACKAGE_DIR'" >&2
  exit 1
fi

# enlace-ui is an npm workspace (root package.json: "workspaces": ["packages/*"]) —
# @get-enlace/ui actually builds to packages/ui/dist, not <checkout>/dist.
UI_PACKAGE_DIR="$UI_DIR/packages/ui"

# The import package name is whatever single directory lives under src/ —
# e.g. packages/enlace-fastapi/src/enlace_fastapi.
import_pkg="$(find "$PKG_ROOT/src" -mindepth 1 -maxdepth 1 -type d -exec basename {} \;)"
if [[ "$(echo "$import_pkg" | wc -l)" -ne 1 ]]; then
  echo "error: expected exactly one package under '$PKG_ROOT/src', found: $import_pkg" >&2
  exit 1
fi
DEST_DIR="$PKG_ROOT/src/$import_pkg/ui_embedded"

if [[ ! -d "$UI_DIR" ]]; then
  echo "error: enlace-ui checkout not found at '$UI_DIR'" >&2
  echo "usage: $0 <package-dir> [path-to-enlace-ui-checkout]" >&2
  exit 1
fi

echo "Building enlace-ui in $UI_DIR..."
(cd "$UI_DIR" && npm install && npm run build)

if [[ ! -d "$UI_PACKAGE_DIR/dist" ]]; then
  echo "error: '$UI_PACKAGE_DIR/dist' not found after build" >&2
  exit 1
fi

echo "Syncing $UI_PACKAGE_DIR/dist -> $DEST_DIR"
rm -rf "${DEST_DIR:?}"/*
cp -R "$UI_PACKAGE_DIR/dist/." "$DEST_DIR/"

echo "Done. Reinstall $PACKAGE_DIR (uv sync) to pick up the refreshed bundle."
