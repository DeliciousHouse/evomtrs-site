#!/usr/bin/env bash
# Minify styles.css to styles.min.css (target <15KB). Run after editing CSS.
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SRC="$ROOT/public/assets/css/styles.css"
OUT="$ROOT/public/assets/css/styles.min.css"
if [[ ! -f "$SRC" ]]; then
  echo "Missing $SRC"
  exit 1
fi
npx --yes cssnano-cli "$SRC" "$OUT"
echo "Minified: $(wc -c < "$SRC") -> $(wc -c < "$OUT") bytes"
