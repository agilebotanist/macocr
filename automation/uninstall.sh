#!/bin/bash
# Removes the "OCR with macocr" Finder Quick Action.
set -euo pipefail

WORKFLOW_NAME="OCR with macocr.workflow"
DEST="$HOME/Library/Services/$WORKFLOW_NAME"

if [[ -d "$DEST" ]]; then
  rm -rf "$DEST"
  echo "Removed: $DEST"
else
  echo "Not installed: $DEST"
fi

/System/Library/CoreServices/pbs -flush >/dev/null 2>&1 || true
