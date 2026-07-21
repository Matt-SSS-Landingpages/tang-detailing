#!/usr/bin/env bash
#
# convert-webp.sh — batch-convert site photography to WebP.
#
# Generates a .webp sibling for every photographic .jpg/.png in
# assets/images (recursively). SVG and AVIF files are skipped — SVG is
# already vector and AVIF is already a modern compressed format.
#
# Prefers `cwebp` (libwebp) if installed; otherwise falls back to
# `sharp-cli` via npx (no global install needed).
#
#   Install cwebp (recommended, fastest):  brew install webp
#   Or just run this script — it will use `npx sharp-cli` automatically.
#
# Usage:
#   ./scripts/convert-webp.sh            # convert everything
#   ./scripts/convert-webp.sh --force    # re-encode even if .webp exists
#
set -euo pipefail

QUALITY=80
FORCE=0
[[ "${1:-}" == "--force" ]] && FORCE=1

# Resolve repo root (this script lives in <root>/scripts).
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
IMG_DIR="$SCRIPT_DIR/../assets/images"

if command -v cwebp >/dev/null 2>&1; then
  ENCODER="cwebp"
else
  ENCODER="sharp"
  echo "cwebp not found — falling back to 'npx sharp-cli'."
fi

convert_one() {
  local src="$1"
  local out="${src%.*}.webp"

  if [[ -f "$out" && "$FORCE" -eq 0 ]]; then
    echo "skip   $out (exists)"
    return
  fi

  if [[ "$ENCODER" == "cwebp" ]]; then
    cwebp -quiet -q "$QUALITY" "$src" -o "$out"
  else
    npx --yes sharp-cli@latest -i "$src" -o "$(dirname "$out")" -f webp -q "$QUALITY" >/dev/null 2>&1
  fi
  echo "wrote  $out"
}

shopt -s nullglob nocaseglob
found=0
while IFS= read -r -d '' f; do
  found=1
  convert_one "$f"
done < <(find "$IMG_DIR" -type f \( -iname '*.jpg' -o -iname '*.jpeg' -o -iname '*.png' \) -print0)

[[ "$found" -eq 0 ]] && echo "No .jpg/.png files found under $IMG_DIR"
echo "Done."
