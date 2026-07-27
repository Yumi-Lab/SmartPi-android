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

- Ubuntu 14.04 x86_64, Oracle JDK 1.6.0_45, make 3.81 (the trusty default). All frozen in [docker/Dockerfile](../docker/Dockerfile).
- The Allwinner pack tools are 32-bit i386 ELF binaries: the container installs i386 multiarch libraries. This rules out building on Apple Silicon Macs entirely (Rosetta does not translate i386) and on ARM hosts in general.
- trusty apt repositories only exist on `old-releases.ubuntu.com`; the Dockerfile rewrites sources.list accordingly.
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

- Sources must be fetched on the host (modern git, python3 for gdown), never inside the trusty container (git 1.9, dead CA store).
- Google Drive quota errors are frequent; prefer the `sources-archive` release of this repo once populated (see [SOURCES.md](SOURCES.md)).
- The `android/` directory must sit next to `lichee/`; the fa_tools scripts use relative paths.
