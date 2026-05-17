#!/bin/bash
# Squad Tools Manager - Shell wrapper
# Run: ./squad-tools-manager.sh <command>

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

python3 "$SCRIPT_DIR/main.py" "$@"
