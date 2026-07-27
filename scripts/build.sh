#!/bin/bash
# Build the BSP inside the Ubuntu 14.04 container.
# Usage: build.sh [lichee|android]
#   lichee  - u-boot + kernel only (fast iteration)
#   android - full image (default)
set -e

TARGET="${1:-android}"
BOARD="${BOARD:-nanopi-m1}"
SRC="${SRC:-/work/sources}"

if [ ! -d "$SRC/lichee/fa_tools" ]; then
  echo "ERROR: $SRC/lichee/fa_tools not found. Run scripts/fetch-sources.sh on the host first." >&2
  exit 1
fi

echo "=== lichee: u-boot + kernel (board $BOARD) ==="
cd "$SRC/lichee/fa_tools"
./build.sh -b "$BOARD" -p android -t all

if [ "$TARGET" = "android" ]; then
  echo "=== android: full tree + pack ==="
  cd "$SRC/android"
  ./build.sh -b "$BOARD"
  echo "=== pack output ==="
  # the Allwinner pack tools always exit 0, even when the image build fails
  # (e.g. "Dragon execute image.cfg Failed"), so check for the artifact itself
  if ! ls "$SRC"/lichee/tools/pack/*.img >/dev/null 2>&1; then
    echo "ERROR: pack produced no .img - check the pack log above for" >&2
    echo "       'Dragon execute image.cfg Failed' or an empty sunxi_mbr.fex" >&2
    exit 1
  fi
  ls -la "$SRC"/lichee/tools/pack/*.img
fi
