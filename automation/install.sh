#!/bin/bash
# Installs the "OCR with macocr" Finder Quick Action.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKFLOW_NAME="OCR with macocr.workflow"
SRC="$SCRIPT_DIR/$WORKFLOW_NAME"
DEST_DIR="$HOME/Library/Services"
DEST="$DEST_DIR/$WORKFLOW_NAME"

if [[ ! -d "$SRC" ]]; then
  echo "error: $SRC not found" >&2
  exit 1
fi

mkdir -p "$DEST_DIR"
rm -rf "$DEST"
cp -R "$SRC" "$DEST"

# Force Finder/Services to re-scan ~/Library/Services.
/System/Library/CoreServices/pbs -flush >/dev/null 2>&1 || true

echo "Installed: $DEST"
echo "Look for \"OCR with macocr\" under Finder > right-click > Quick Actions."
echo "If it doesn't show up immediately, log out/in or reopen Finder — the Services menu cache can lag."
