#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SRC_DIR="${1:-$ROOT_DIR/public}"
OUT_DIR="${2:-$ROOT_DIR/dist}"

python3 "$ROOT_DIR/scripts/render_site.py" "$SRC_DIR" "$OUT_DIR"
