#!/usr/bin/env bash
# Fetch the FriendlyELEC H3 Android 4.4 BSP sources into sources/.
# Run on the HOST (modern git required), never inside the trusty container.
set -euo pipefail

SRC_DIR="${SRC_DIR:-$PWD/sources}"
LICHEE_GIT="${LICHEE_GIT:-https://github.com/friendlyarm/h3_lichee.git}"
LICHEE_FALLBACK="https://github.com/Yumi-Lab/h3_lichee.git"
ANDROID_GIT="${ANDROID_GIT:-https://gitlab.com/friendlyelec/h3_android-4.4.git}"

mkdir -p "$SRC_DIR"
cd "$SRC_DIR"

# fa_tools uses relative paths: android/ must sit next to lichee/
if [ ! -d lichee ]; then
  echo "Cloning lichee SDK..."
  git clone --depth 1 "$LICHEE_GIT" lichee \
    || git clone --depth 1 "$LICHEE_FALLBACK" lichee
fi

# Cross toolchain: gcc-linaro 4.6.3 arm-linux-gnueabi (i686 host binaries,
# hence the i386 multiarch in the container). brandy/build.sh -t expects the
# tarball at brandy/toolchain/gcc-linaro-arm.tar.xz and extracts it itself
# (tar auto-detects the bz2 despite the .xz name); the kernel then finds
# arm-linux-gnueabi-gcc through PATH. Mirrored on our sources-archive release.
TOOLCHAIN_URL="https://github.com/Yumi-Lab/SmartPi-android/releases/download/sources-archive/gcc-linaro.tar.bz2"
if [ ! -f lichee/brandy/toolchain/gcc-linaro-arm.tar.xz ]; then
  echo "Downloading cross toolchain..."
  curl -fL --retry 3 -o lichee/brandy/toolchain/gcc-linaro-arm.tar.xz "$TOOLCHAIN_URL"
  # the buildroot flow (linux platform) looks for the same toolchain here
  mkdir -p lichee/buildroot/dl
  cp lichee/brandy/toolchain/gcc-linaro-arm.tar.xz lichee/buildroot/dl/gcc-linaro.tar.bz2
fi

# The android tree is only needed for full image builds (FETCH_ANDROID=0 skips it)
if [ "${FETCH_ANDROID:-1}" = "1" ] && [ ! -d android ]; then
  echo "Cloning Android 4.4 tree (large)..."
  git clone --depth 1 "$ANDROID_GIT" android
fi

echo "Sources ready in $SRC_DIR"
du -sh lichee android 2>/dev/null || du -sh lichee
