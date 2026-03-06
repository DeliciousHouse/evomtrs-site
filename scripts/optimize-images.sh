#!/usr/bin/env bash
# Generate responsive WebP variants (320w, 640w, 960w, 1280w). Recompress with quality 78 (hero 75).
# Targets: hero <100KB, gallery <80KB.
set -euo pipefail
IMG_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../public/assets/images" && pwd)"
cd "$IMG_DIR"
HERO_SOURCE="Resized_1_2_3e5105d8-6291-4100-beaa-902338ab75f3_1200x.webp"
QUALITY=78
HERO_QUALITY=75

for src in *.webp; do
  [[ -f "$src" ]] || continue
  base="${src%.webp}"
  if [[ "$base" == *"-320w" ]] || [[ "$base" == *"-640w" ]] || [[ "$base" == *"-960w" ]] || [[ "$base" == *"-1280w" ]]; then
    continue
  fi
  for w in 320 640 960 1280; do
    out="${base}-${w}w.webp"
    q=$QUALITY
    [[ "$src" == "$HERO_SOURCE" ]] && q=$HERO_QUALITY
    cwebp -q "$q" -resize "$w" 0 "$src" -o "$out"
  done
done

# Hero 960w: if still >100KB, re-encode at lower quality for LCP preload
hero960="${HERO_SOURCE%.webp}-960w.webp"
if [[ -f "$hero960" ]]; then
  size=$(wc -c < "$hero960")
  if [[ $size -gt 102400 ]]; then
    cwebp -q 72 -resize 960 0 "$HERO_SOURCE" -o "$hero960"
  fi
fi

echo "Done. Variants: *-320w.webp, *-640w.webp, *-960w.webp, *-1280w.webp"
