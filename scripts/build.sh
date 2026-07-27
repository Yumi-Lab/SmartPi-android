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
  ls -la "$SRC"/lichee/tools/pack/*.img 2>/dev/null || echo "WARNING: no .img produced in lichee/tools/pack/"
fi
