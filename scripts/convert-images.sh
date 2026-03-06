#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SRC_DIR="${SRC_DIR:-/root/.openclaw/media/evomtrs}"
OUT_DIR="${OUT_DIR:-$ROOT_DIR/public/assets/images}"

mkdir -p "$OUT_DIR"

files=(
  "IMG_3768.jpeg"
  "IMG_3769.jpeg"
  "IMG_8875.jpeg"
  "Resized_FB_IMG_1726220550837.jpeg"
  "Resized_1_2_3e5105d8-6291-4100-beaa-902338ab75f3_1200x.jpeg"
  "Resized_1_3_a0d4bac3-1575-4b9f-b4a8-fa324156e645_1200x.jpeg"
  "Resized_5yso8hfp3ewa1.jpeg"
)

converter=""
if command -v magick >/dev/null 2>&1; then
  converter="magick"
elif command -v convert >/dev/null 2>&1; then
  converter="convert"
elif command -v cwebp >/dev/null 2>&1; then
  converter="cwebp"
else
  echo "No conversion tool found (need magick, convert, or cwebp)." >&2
  exit 1
fi

find "$OUT_DIR" -type f -name '*.webp' -delete

for file in "${files[@]}"; do
  input="$SRC_DIR/$file"
  output="$OUT_DIR/${file%.*}.webp"

  [[ -f "$input" ]] || { echo "Missing source: $input" >&2; continue; }

  if [[ "$converter" == "cwebp" ]]; then
    cwebp -q 82 "$input" -o "$output" >/dev/null
  else
    "$converter" "$input" -auto-orient -strip -resize "2200x2200>" -quality 82 "$output"
  fi

  echo "Generated: $output"
done

echo "Done. WebP assets in $OUT_DIR"
