# Building

## Official build sequence

The BSP builds in two stages, from two sibling directories `lichee/` and `android/`:

```
cd lichee/fa_tools
./build.sh -b nanopi-m1 -p android -t all      # u-boot + kernel + modules
cd ../../android
./build.sh -b nanopi-m1                        # Android tree + final pack
```

Output image: `lichee/tools/pack/sun8iw7p1_android_nanopi-m1_uart0.img`

## Build environment constraints

- The BSP wants a 2014-era environment: Oracle JDK 1.6.0_45, make 3.81, gcc 4.x host. All frozen in [docker/Dockerfile](../docker/Dockerfile).
- The historical recommendation was Ubuntu 14.04, but Canonical purged trusty from `old-releases.ubuntu.com` (verified 2026-07-27: the dists listing stops at precise; trusty, xenial and later are gone, wayback never captured the indexes, and public mirrors followed the deletion). The container is therefore based on `debian/eol:wheezy` with `archive.debian.org`, which Debian keeps forever: same era, make 3.81 native, gcc 4.7, i386 multiarch.
- The Allwinner pack tools are 32-bit i386 ELF binaries: the container installs i386 multiarch libraries. This rules out building on Apple Silicon Macs entirely (Rosetta does not translate i386) and on ARM hosts in general.
- `tedwang/aosp-v4` (the Docker Hub AOSP-KitKat reference image) still exists but is a schema1 manifest, rejected by Docker 26+/containerd 2.1: unusable on modern hosts without a skopeo conversion.
- The JDK download from the Huawei mirror uses `--no-check-certificate` because trusty's CA store is frozen in time; integrity is enforced by a pinned sha256 instead.
- Full Android build: about 8 GB RAM, 40 GB disk, 2-4 h on 4 cores. Lichee-only (u-boot + kernel): far smaller, use it for fast iteration.

## Local build (x86_64 Linux only)

```
./scripts/fetch-sources.sh                     # clones lichee + android into sources/
docker build --platform linux/amd64 -t smartpi-android-build docker/
docker run --rm --platform linux/amd64 -v "$PWD:/work" smartpi-android-build /work/scripts/build.sh lichee    # or: android
```

## CI

`.github/workflows/build.yml`, manual dispatch with a `target` input:

- `lichee`: u-boot + kernel only. Fast feedback on toolchain and FEX changes.
- `android`: full image. Tight but expected to fit on the free public-repo runner (4 vCPU, 16 GB RAM, 6 h limit) after the disk cleanup step.

If the free runner proves too small, move to a real x86 server (Hetzner class). Do NOT use the `yumi-usa-server` self-hosted runner (IONOS): it has 425 MB RAM plus 4 GB swap, far below the 8 GB required. Workflow patterns to copy for self-hosted routing and tag releases: `Yumi-Lab/RetroMi-packages`.

## Known traps

- Sources must be fetched on the host (modern git, python3 for gdown), never inside the container (ancient git and CA store).
- Google Drive quota errors are frequent; prefer the `sources-archive` release of this repo once populated (see [SOURCES.md](SOURCES.md)).
- The `android/` directory must sit next to `lichee/`; the fa_tools scripts use relative paths.
- The lichee tree ships no cross toolchain. `brandy/build.sh -t` expects `brandy/toolchain/gcc-linaro-arm.tar.xz` and the kernel needs the soft-float `arm-linux-gnueabi-` prefix; `fetch-sources.sh` installs it.
- Host tools the BSP assumes without declaring: `fakeroot` (rootfs cpio), `gawk` (kernel scripts use `strtonum`, absent from mawk), `file` (AOSP `gcc-sdk` wrappers detect the host arch with it), `busybox unix2dos` (see below).
- `tools/pack/pack` runs `busybox unix2dos` on the FEX files, but Debian's busybox lacks that applet. Without the CRLF conversion the Allwinner `script` compiler segfaults on `sys_partition.fex`, `sunxi_mbr.fex` ends up empty and the image build dies with `Dragon execute image.cfg Failed`. The container installs `dos2unix` and shims `busybox` to forward those two applets.
- The Allwinner pack tools exit 0 even when they fail, so `scripts/build.sh` verifies that an `.img` actually exists.
- Do not trust a local container build on an Apple Silicon Mac: qemu emulation of the wheezy i386/amd64 binaries segfaults at random points (apt methods, dpkg maintainer scripts). Only the x86_64 CI result is meaningful.
